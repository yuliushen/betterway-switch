"""Real search backends; never treat a fabricated/cached packet as a live search."""

from datetime import datetime, timezone
import hashlib
import json
import os
import socket
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, HTTPRedirectHandler, build_opener
import uuid

from . import BetterWayError
from .storage import Store, atomic_write

MAX_RESPONSE = 3 * 1024 * 1024


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Never forward authentication headers to an unexpected destination.
        return None


def request_json(url: str, headers: dict | None = None, payload: dict | None = None, timeout: int = 20) -> dict:
    if urlparse(url).scheme != "https":
        raise BetterWayError("����ӿڱ���ʹ�� HTTPS��")
    body = json.dumps(payload, ensure_ascii=False).encode() if payload is not None else None
    request_headers = {"User-Agent": "BetterWay/0.1", "Accept": "application/json"}
    if body is not None:
        request_headers["Content-Type"] = "application/json"
    request_headers.update(headers or {})
    try:
        request = Request(url, data=body, headers=request_headers)
        with build_opener(NoRedirect).open(request, timeout=timeout) as response:
            raw = response.read(MAX_RESPONSE + 1)
            if len(raw) > MAX_RESPONSE:
                raise BetterWayError("�ӿ���Ӧ������С���ơ�")
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("expected object")
        return data
    except HTTPError as exc:
        if urlparse(url).hostname == "api.github.com" and exc.code in {403, 429}:
            raise BetterWayError(f"GitHub �ܾ�����HTTP {exc.code}��������������Ȩ�޲��㡣������ֹͣ�������� BETTERWAY_GITHUB_TOKEN���Ժ����ԣ����л��������õ���ҳ������Դ��") from exc
        raise BetterWayError(f"�ӿڷ��� HTTP {exc.code}�������ȡ�Ȩ�޻��Ժ����ԡ�") from exc
    except (URLError, TimeoutError, socket.timeout, OSError) as exc:
        raise BetterWayError("��������ʧ�ܻ�ʱ��δ�ƹ���������ִ�С�") from exc
    except (ValueError, UnicodeError) as exc:
        raise BetterWayError("�ӿ�û�з�����Ч�� JSON ����") from exc


def required_key(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise BetterWayError(f"ȱ�ٻ������� {name}����Կֻ�ӻ���������ȡ��")
    return value


def clean_result(title, url, snippet) -> dict | None:
    if not isinstance(title, str) or not isinstance(url, str):
        return None
    try:
        parsed = urlparse(url)
        valid = parsed.scheme in {"http", "https"} and parsed.hostname and not parsed.username and not parsed.password
    except ValueError:
        return None
    if not title.strip() or not valid or len(url) > 2048:
        return None
    return {"title": title[:250], "url": url[:2048], "snippet": str(snippet or "")[:1600]}


def search(query: str, provider: str = "github") -> dict:
    query = " ".join(query.split())
    maximum = {"github": 200, "brave": 400, "deepseek": 128}.get(provider)
    if maximum is None:
        raise BetterWayError("δ֪��������Դ��")
    if not query or len(query) > maximum:
        raise BetterWayError(f"�����ʲ���Ϊ���Ҳ��ܳ��� {maximum} ���ַ�����ʹ�ü�̹ؼ��ʡ�")
    if provider == "github":
        headers = {"Accept": "application/vnd.github+json"}
        token = os.environ.get("BETTERWAY_GITHUB_TOKEN", "").strip()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        data = request_json("https://api.github.com/search/repositories?" + urlencode({"q": query + " archived:false is:public", "per_page": 5}), headers)
        rows = data.get("items")
        if not isinstance(rows, list) or data.get("incomplete_results") is True:
            raise BetterWayError("GitHub ���ز��������ʽ�쳣�����������")
        entries = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            license_info = row.get("license") or {}
            license_id = license_info.get("spdx_id", "unknown") if isinstance(license_info, dict) else "unknown"
            entries.append(clean_result(row.get("full_name"), row.get("html_url"), f"{row.get('description') or ''}\nStars: {row.get('stargazers_count', 0)}; license: {license_id}; pushed: {row.get('pushed_at', 'unknown')}"))
    elif provider == "brave":
        data = request_json("https://api.search.brave.com/res/v1/web/search?" + urlencode({"q": query, "count": 5}), {"X-Subscription-Token": required_key("BRAVE_API_KEY")})
        web = data.get("web")
        rows = web.get("results") if isinstance(web, dict) else None
        if not isinstance(rows, list):
            raise BetterWayError("Brave δ������Ч����ҳ���������")
        entries = [clean_result(row.get("title"), row.get("url"), row.get("description")) for row in rows if isinstance(row, dict)]
    else:
        data = request_json("https://api.deepseek.com/v1/tools/search", {"Authorization": "Bearer " + required_key("DEEPSEEK_API_KEY")}, {"query": query, "count": 5, "need_content": False})
        rows = data.get("results")
        if not isinstance(rows, list):
            raise BetterWayError("DeepSeek δ������Ч�����������")
        entries = [clean_result(row.get("title"), row.get("url"), row.get("summary") or row.get("snippet")) for row in rows if isinstance(row, dict)]
    entries = [entry for entry in entries if entry][:5]
    if not entries:
        raise BetterWayError("����δȡ����Ч��Դ��������ֹͣ�������̹ؼ��ʻ����������Դ��")
    return {"provider": provider, "query": query, "searched_at": datetime.now(timezone.utc).isoformat(), "results": entries}


def record(store: Store, event: dict) -> str:
    identity = uuid.uuid4().hex
    value = {"id": identity, "at": datetime.now(timezone.utc).isoformat(), **event}
    atomic_write(store.root / "evidence" / (identity + ".json"), (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode())
    return identity


def gated_search(store: Store, query: str, provider: str) -> tuple[dict, str]:
    hashed = hashlib.sha256(query.encode()).hexdigest()
    try:
        packet = search(query, provider)
    except BetterWayError:
        record(store, {"event": "search_failed", "provider": provider, "query_sha256": hashed})
        raise
    identity = record(store, {"event": "search_succeeded", "provider": provider, "query_sha256": hashed, "sources": [r["url"] for r in packet["results"]]})
    return packet, identity

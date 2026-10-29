"""Manage only our own marked block; preserve other instructions byte for byte."""

from datetime import datetime, timezone
import hashlib
from importlib.resources import files
import json
import os
from pathlib import Path
import uuid

from . import BetterWayError
from .storage import Store, atomic_write

START = b"<!-- betterway:begin:v1 -->"
END = b"<!-- betterway:end:v1 -->"


def policy() -> str:
    return files("betterway").joinpath("policy.md").read_text(encoding="utf-8").strip()


def block() -> bytes:
    return START + b"\n" + policy().encode("utf-8") + b"\n" + END


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def bounds(data: bytes) -> tuple[int, int] | None:
    count = data.count(START), data.count(END)
    if count == (0, 0):
        # Do not append to an unrecognized or partially edited managed block.
        if b"<!-- betterway:" in data:
            raise BetterWayError("发现未知或损坏的 BetterWay 标记；请先检查指令文件。")
        return None
    if count != (1, 1) or data.index(END) < data.index(START):
        raise BetterWayError("BetterWay 标记不完整或重复；已停止以保护原文件。")
    return data.index(START), data.index(END) + len(END)


def target_path(target: str) -> Path:
    if target == "codex":
        root = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser().absolute()
        override = root / "AGENTS.override.md"
        if override.exists() and override.read_bytes().strip():
            return override
        return root / "AGENTS.md"
    if target == "claude":
        root = Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude")).expanduser().absolute()
        return root / "CLAUDE.md"
    raise BetterWayError(f"不支持的指令目标：{target}")


class Manager:
    def __init__(self, store: Store | None = None):
        self.store = store or Store()

    def _apply(self, state: dict, changes: list[tuple[Path, bytes | None]]) -> None:
        originals = [(path, path.read_bytes() if path.exists() else None) for path, _ in changes]
        backup = self.store.root / "backups" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8])
        backup.mkdir(parents=True)
        manifest = []
        for i, (path, data) in enumerate(originals):
            manifest.append({"path": str(path), "existed": data is not None, "snapshot": f"{i}.bin"})
            if data is not None:
                atomic_write(backup / f"{i}.bin", data)
        atomic_write(backup / "manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2).encode())
        old_state = self.store.path.read_bytes() if self.store.path.exists() else None
        try:
            for path, data in changes:
                if path.is_symlink():
                    raise BetterWayError(f"不修改符号链接：{path}")
                if data is None:
                    path.unlink(missing_ok=True)
                else:
                    atomic_write(path, data)
            self.store.save(state)
        except Exception as exc:
            try:
                for path, data in originals:
                    if path.is_symlink():
                        continue
                    if data is None:
                        path.unlink(missing_ok=True)
                    else:
                        atomic_write(path, data)
                if old_state is None:
                    self.store.path.unlink(missing_ok=True)
                else:
                    atomic_write(self.store.path, old_state)
            except Exception as rollback_exc:
                raise BetterWayError(f"写入和回滚均失败，请用备份恢复：{backup}") from rollback_exc
            raise BetterWayError(f"写入失败，原内容已回滚。备份：{backup}") from exc

    def switch(self, enabled: bool, targets: list[str] | None = None, migrate_legacy: bool = False) -> dict:
        with self.store.lock():
            state = self.store.load()
            selected = list(state["targets"]) + (targets or [])
            if enabled and not selected:
                selected = ["codex", "claude"]
            if not enabled:
                selected = list(state["targets"])
            changes = []
            for target in dict.fromkeys(selected):
                existing = state["targets"].get(target)
                path = Path(existing["path"]) if existing else target_path(target)
                if enabled and existing and target_path(target) != path:
                    raise BetterWayError(f"{target} 的配置位置已改变；请在原环境关闭后再安装。")
                if path.is_symlink():
                    raise BetterWayError(f"不修改符号链接：{path}")
                raw = path.read_bytes() if path.exists() else b""
                info = dict(existing or {"path": str(path), "created": not path.exists(), "separator": "", "prefix_hash": ""})
                location = bounds(raw)
                if enabled:
                    if migrate_legacy and target == "codex" and not location:
                        legacy = files("betterway").joinpath("legacy-policy.md").read_bytes()
                        if raw.decode("utf-8-sig").strip().replace("\r\n", "\n") == legacy.decode("utf-8").strip():
                            raw = b""
                            info["created"] = True
                    if location:
                        start, end = location
                        updated = raw[:start] + block() + raw[end:]
                    else:
                        sep = b"" if not raw or raw.endswith(b"\n\n") else b"\n" if raw.endswith(b"\n") else b"\n\n"
                        info["separator"] = sep.hex()
                        info["prefix_hash"] = digest(raw)
                        updated = raw + sep + block()
                elif location:
                    start, end = location
                    prefix = raw[:start]
                    sep = bytes.fromhex(info["separator"])
                    candidate = prefix[:-len(sep)] if sep and prefix.endswith(sep) else prefix
                    if digest(candidate) == info["prefix_hash"]:
                        prefix = candidate
                    updated = prefix + raw[end:]
                else:
                    updated = raw
                state["targets"][target] = info
                value = None if not updated and info["created"] else updated
                if value != (path.read_bytes() if path.exists() else None):
                    changes.append((path, value))
            state["enabled"] = enabled
            # Avoid creating backup folders for an idempotent operation.
            if changes:
                self._apply(state, changes)
            else:
                self.store.save(state)
        return self.status()

    def provider(self, value: str) -> None:
        if value not in {"github", "brave", "deepseek"}:
            raise BetterWayError("搜索来源仅支持 github、brave、deepseek。")
        with self.store.lock():
            state = self.store.load()
            state["provider"] = value
            self.store.save(state)

    def uninstall(self) -> dict:
        self.switch(False)
        with self.store.lock():
            state = self.store.load()
            state["targets"] = {}
            self.store.save(state)
        return self.status()

    def status(self) -> dict:
        state = self.store.load()
        result = {"enabled": state["enabled"], "provider": state["provider"], "home": str(self.store.root), "targets": {}}
        for target, info in state["targets"].items():
            path = Path(info["path"])
            raw = path.read_bytes() if path.exists() else b""
            try:
                present = bool(bounds(raw))
                intact = block() in raw if present else False
                matches = present == state["enabled"] and (not present or intact)
                selected = target_path(target) == path
                result["targets"][target] = {"path": str(path), "present": present, "matches": matches and selected, "active_path": str(target_path(target))}
            except BetterWayError:
                result["targets"][target] = {"path": str(path), "present": None, "matches": False}
        return result

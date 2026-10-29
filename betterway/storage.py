"""Small, atomic local state store. No credentials are persisted here."""

from contextlib import contextmanager
import json
import os
from pathlib import Path
import tempfile

from . import BetterWayError


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise BetterWayError(f"�ܾ��滻�������ӣ����ȼ���ļ���{path}")
    mode = path.stat().st_mode if path.exists() else 0o600
    fd, name = tempfile.mkstemp(prefix=".betterway-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(name, mode)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


class Store:
    def __init__(self, root: Path | None = None):
        self.root = root or Path(os.environ.get("BETTERWAY_HOME", Path.home() / ".betterway"))
        self.root = self.root.expanduser().absolute()
        self.path = self.root / "state.json"

    def load(self) -> dict:
        if not self.path.exists():
            return {"version": 1, "enabled": False, "provider": "github", "targets": {}}
        try:
            state = json.loads(self.path.read_text(encoding="utf-8"))
            valid = (state["version"] == 1 and type(state["enabled"]) is bool
                     and state["provider"] in {"github", "brave", "deepseek"}
                     and isinstance(state["targets"], dict))
            for target, info in state["targets"].items():
                valid = valid and target in {"codex", "claude"} and isinstance(info, dict)
                valid = valid and isinstance(info.get("path"), str) and Path(info["path"]).is_absolute()
                valid = valid and type(info.get("created")) is bool
                valid = valid and isinstance(info.get("separator"), str)
                valid = valid and isinstance(info.get("prefix_hash"), str)
                bytes.fromhex(info.get("separator", ""))
            if not valid:
                raise ValueError("invalid state")
            return state
        except (ValueError, KeyError, TypeError, AttributeError) as exc:
            raise BetterWayError(f"�����𻵣���ֹͣ������δĬ��Ϊ�رա����� {self.path}") from exc

    def save(self, state: dict) -> None:
        atomic_write(self.path, (json.dumps(state, ensure_ascii=False, indent=2) + "\n").encode())

    @contextmanager
    def lock(self):
        self.root.mkdir(parents=True, exist_ok=True)
        path = self.root / "operation.lock"
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError as exc:
            raise BetterWayError(f"��һ�����ò�����δ�����������쳣�˳��������ɾ�� {path}") from exc
        try:
            os.close(fd)
            yield
        finally:
            path.unlink(missing_ok=True)

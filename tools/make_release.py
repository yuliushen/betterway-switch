"""Build a source ZIP from an explicit allowlist, never from the user's home."""

import hashlib
from pathlib import Path
import zipfile

from betterway import __version__


def main():
    root = Path(__file__).resolve().parents[1]
    destination = root / "dist"
    destination.mkdir(exist_ok=True)
    release_name = f"BetterWay-{__version__}"
    archive = destination / (release_name + "-source.zip")
    top_level = ["README.md", "README.en.md", "CHANGELOG.md", "LICENSE", "CONTRIBUTING.md", "VALIDATION.md", "pyproject.toml", ".gitignore", "install.ps1", "run-ui.cmd", "run-ui.pyw"]
    selected = [root / name for name in top_level]
    for directory in ("betterway", "tests", "tools", ".github"):
        selected.extend(p for p in (root / directory).rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc")
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as output:
        for path in sorted(selected):
            output.write(path, str(Path(release_name) / path.relative_to(root)))
    sums = []
    for path in sorted(destination.iterdir()):
        if path.suffix in {".whl", ".zip"}:
            sums.append(hashlib.sha256(path.read_bytes()).hexdigest() + "  " + path.name)
    (destination / "SHA256SUMS.txt").write_text("\n".join(sums) + "\n", encoding="utf-8")
    print(archive)


if __name__ == "__main__":
    main()

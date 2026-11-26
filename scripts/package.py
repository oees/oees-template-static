#!/usr/bin/env python3
"""Build a clean zip of this project to send to the OEES tech team.

The zip leaves out dependencies, build output, caches and local environment files.
It never includes .env files or key files. It refuses to package when a file looks
like it holds a secret, or when a file is too large.

Usage: python3 scripts/package.py [--out DIR]
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

EXCLUDED_DIRS = frozenset(
    {
        ".git",
        ".idea",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        ".vscode",
        "__MACOSX",
        "__pycache__",
        "coverage",
        "dist",
        "htmlcov",
        "node_modules",
        "staticfiles",
        "venv",
    }
)
EXCLUDED_FILES = frozenset({".DS_Store", "Thumbs.db", "coverage.xml"})
# .mo catalogues are compiled from the committed .po files at build time.
EXCLUDED_SUFFIXES = frozenset({".log", ".mo", ".pyc", ".sqlite3", ".zip"})

# Files that hold secrets by convention. They never leave the machine.
FORBIDDEN_NAME = re.compile(
    r"^(\.env(\..+)?|.+\.(pem|key|p12|pfx)|id_(rsa|ecdsa|ed25519).*)$"
)
ALLOWED_NAMES = frozenset({".env.example"})

SECRET_PATTERNS: dict[str, re.Pattern[str]] = {
    "a private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "a DigitalOcean token": re.compile(r"\bdo[opr]_v1_[a-f0-9]{64}\b"),
    "a GitHub token": re.compile(
        r"\b(gh[pousr]_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{50,})\b"
    ),
    "an AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "a Stripe live key": re.compile(r"\b[rs]k_live_[A-Za-z0-9]{20,}\b"),
    "a Slack token": re.compile(r"\bxox[abposr]-[A-Za-z0-9-]{10,}\b"),
    "an AI provider API key": re.compile(r"\bsk-(ant-|proj-)?[A-Za-z0-9_-]{32,}\b"),
}
# A database or cache URL with a password in it. Local development hosts are allowed.
CREDENTIAL_URL = re.compile(
    r"\b(?:postgres|postgresql|mysql|redis|rediss)(?:\+\w+)?"
    r"://[^\s:/@]+:[^\s@/]+@([^\s:/?#]+)"
)
LOCAL_HOSTS = frozenset(
    # Host names to recognise in a URL, not addresses to bind to.
    {"localhost", "127.0.0.1", "0.0.0.0", "db", "postgres", "redis"}  # noqa: S104
)

# The zip takes its name from `name` in the [project] table of pyproject.toml.
# Read that one key without tomllib: tomllib needs Python 3.11, and the
# sandbox can have an older python3.
TOML_TABLE = re.compile(r"^\s*\[([^\[\]]+)\]\s*(#.*)?$")
TOML_NAME = re.compile(r'^\s*name\s*=\s*"([^"]+)"')

MAX_FILE_BYTES = 25 * 1024 * 1024
MAX_TOTAL_BYTES = 150 * 1024 * 1024


@dataclass
class Scan:
    files: list[Path] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)
    left_out: list[Path] = field(default_factory=list)
    total_bytes: int = 0


def is_excluded(relative: Path) -> bool:
    if any(part in EXCLUDED_DIRS for part in relative.parts[:-1]):
        return True
    name = relative.name
    return (
        name in EXCLUDED_FILES
        or name.startswith(".coverage")
        or relative.suffix in EXCLUDED_SUFFIXES
    )


def find_secrets(text: str) -> list[tuple[int, str]]:
    """Return (line number, kind) for each line that looks like it holds a secret."""
    found: list[tuple[int, str]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        for kind, pattern in SECRET_PATTERNS.items():
            if pattern.search(line):
                found.append((number, kind))
        for match in CREDENTIAL_URL.finditer(line):
            if match.group(1).lower() not in LOCAL_HOSTS:
                found.append((number, "a connection string with a password"))
    return found


def scan(root: Path) -> Scan:
    result = Scan()
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(root)
        if is_excluded(relative):
            continue
        if FORBIDDEN_NAME.match(relative.name) and relative.name not in ALLOWED_NAMES:
            result.left_out.append(relative)
            continue
        size = path.stat().st_size
        if size > MAX_FILE_BYTES:
            result.problems.append(
                f"{relative}: {size // (1024 * 1024)} MB; compress it below "
                f"{MAX_FILE_BYTES // (1024 * 1024)} MB"
            )
            continue
        data = path.read_bytes()
        if b"\0" not in data[:8192]:
            for line, kind in find_secrets(data.decode("utf-8", errors="ignore")):
                result.problems.append(
                    f"{relative}:{line}: looks like {kind}; remove it"
                )
        result.files.append(relative)
        result.total_bytes += size
    if result.total_bytes > MAX_TOTAL_BYTES:
        result.problems.append(
            f"the project is {result.total_bytes // (1024 * 1024)} MB; "
            f"the limit is {MAX_TOTAL_BYTES // (1024 * 1024)} MB"
        )
    return result


def project_name(root: Path) -> str:
    package_json = root / "package.json"
    if package_json.is_file():
        name = json.loads(package_json.read_text(encoding="utf-8")).get("name")
        if isinstance(name, str) and name:
            return name
    pyproject = root / "pyproject.toml"
    if pyproject.is_file():
        name = pyproject_name(pyproject.read_text(encoding="utf-8"))
        if name:
            return name
    return root.name


def pyproject_name(text: str) -> str | None:
    """Return `name` from the [project] table of a pyproject.toml, or None."""
    table = ""
    for line in text.splitlines():
        header = TOML_TABLE.match(line)
        if header:
            table = header.group(1).strip()
            continue
        name = TOML_NAME.match(line)
        if table == "project" and name:
            return name.group(1)
    return None


def write_zip(root: Path, files: list[Path], destination: Path, folder: str) -> None:
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for relative in files:
            archive.write(root / relative, arcname=f"{folder}/{relative.as_posix()}")


def main(argv: list[str] | None = None, root: Path = ROOT) -> int:
    parser = argparse.ArgumentParser(description="Build a clean zip of this project.")
    parser.add_argument(
        "--out", type=Path, default=root.parent, help="folder for the zip"
    )
    args = parser.parse_args(argv)

    result = scan(root)
    if result.problems:
        print("Not packaged. Fix these first:", file=sys.stderr)
        for problem in result.problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    for relative in result.left_out:
        print(f"Left out (never sent): {relative}")
    name = project_name(root)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    destination = args.out / f"{name}-{stamp}.zip"
    write_zip(root, result.files, destination, folder=name)
    size_mb = result.total_bytes / (1024 * 1024)
    print(f"Packaged {len(result.files)} files ({size_mb:.1f} MB before compression):")
    print(destination)
    return 0


if __name__ == "__main__":
    sys.exit(main())

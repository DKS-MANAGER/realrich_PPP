"""Phase 7 solutions: file I/O.

Reference implementations for exercises 31.1–31.2.
"""

from __future__ import annotations

from pathlib import Path


def write_text(path: str | Path, text: str) -> None:
    """Write text to a file (UTF-8)."""

    Path(path).write_text(text, encoding="utf-8")


def read_text(path: str | Path) -> str:
    """Read text from a file (UTF-8)."""

    return Path(path).read_text(encoding="utf-8")


def concatenate_files(paths: list[str | Path]) -> str:
    """Read multiple files and concatenate their contents with newlines."""

    contents: list[str] = []
    for p in paths:
        contents.append(read_text(p))
    return "\n".join(contents)

"""Phase 4 solutions: JSON handling.

Reference implementations for exercises 21.1–21.3.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


def to_json_string(data: dict[str, Any]) -> str:
    """Exercise 21.1: Convert dict -> JSON string."""

    return json.dumps(data, indent=2, sort_keys=True)


def from_json_string(text: str) -> dict[str, Any]:
    """Exercise 21.1: Convert JSON string -> dict."""

    parsed = json.loads(text)
    if not isinstance(parsed, dict):
        raise ValueError("expected a JSON object")
    return parsed


def save_json(path: str | Path, data: dict[str, Any]) -> None:
    """Exercise 21.2: Save a JSON file."""

    Path(path).write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def load_json(path: str | Path) -> dict[str, Any]:
    """Exercise 21.2: Load a JSON file."""

    text = Path(path).read_text(encoding="utf-8")
    return from_json_string(text)


@dataclass(frozen=True)
class Person:
    name: str
    age: int


def person_to_json(person: Person) -> str:
    """Exercise 21.3: Serialize a custom class using a safe approach."""

    return json.dumps(asdict(person))

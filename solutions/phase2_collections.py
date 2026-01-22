"""Phase 2 solutions: collections (lists/tuples/sets/dicts).

This module contains clean reference implementations for the beginner
exercises in Phase 2 of `excer_notebook.ipynb`.

The notebook may also contain inline solutions; these functions exist so
they can be unit-tested via pytest.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any


def set_analysis(group_a: Iterable[Any], group_b: Iterable[Any]) -> dict[str, set[Any]]:
    """Compute common set operations for two groups.

    Args:
        group_a: First collection of hashable items.
        group_b: Second collection of hashable items.

    Returns:
        A dict with keys: union, intersection, only_a, only_b.
    """

    a_set = set(group_a)
    b_set = set(group_b)

    return {
        "union": a_set | b_set,
        "intersection": a_set & b_set,
        "only_a": a_set - b_set,
        "only_b": b_set - a_set,
    }


def dedupe_preserve_order(items: Iterable[Any]) -> tuple[list[Any], int]:
    """Remove duplicates while preserving first-seen order.

    Args:
        items: Any iterable of hashable items.

    Returns:
        (unique_items, duplicates_removed)

    Notes:
        Assumption: items are hashable, since sets are used.
    """

    seen: set[Any] = set()
    unique: list[Any] = []
    removed = 0

    for item in items:
        if item in seen:
            removed += 1
            continue
        seen.add(item)
        unique.append(item)

    return unique, removed


def word_frequency(text: str) -> dict[str, int]:
    """Count word frequencies in a simple, beginner-friendly way.

    - Lowercases text
    - Treats punctuation (.,!?:;"'()[]) as separators

    Args:
        text: Input string.

    Returns:
        Dict mapping word -> count.
    """

    separators = "\n\t.,!?:;\"'()[]{}<>/\\|@#$%^&*-_=+~`"
    cleaned = text.lower()
    for ch in separators:
        cleaned = cleaned.replace(ch, " ")

    counts: dict[str, int] = {}
    for word in cleaned.split():
        counts[word] = counts.get(word, 0) + 1

    return counts


def merge_configs(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Shallow merge two configuration dicts.

    Values in override replace values in base for matching keys.

    Args:
        base: Base config.
        override: Overrides.

    Returns:
        New merged dict.
    """

    merged = dict(base)
    merged.update(override)
    return merged


def deep_get(data: dict[str, Any], path: str, default: Any | None = None) -> Any:
    """Safely read a nested dictionary path like "user.profile.name".

    Args:
        data: Root dictionary.
        path: Dot-separated path.
        default: Returned if any key is missing.

    Returns:
        The nested value or default.
    """

    current: Any = data
    for key in path.split("."):
        if not isinstance(current, dict):
            return default
        if key not in current:
            return default
        current = current[key]
    return current

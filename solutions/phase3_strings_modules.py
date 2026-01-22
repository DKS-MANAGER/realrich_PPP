"""Phase 3 solutions: string formatting and modules/packages.

Reference implementations for exercises 17.1–18.3.
"""

from __future__ import annotations

from dataclasses import dataclass


def format_user_summary(name: str, role: str, score: float) -> str:
    """Exercise 17.1: Demonstrate f-strings and basic formatting."""

    return f"Name: {name.title()} | Role: {role.title()} | Score: {score:.1f}"


def format_table(rows: list[tuple[str, int]]) -> str:
    """Exercise 17.2: Build an aligned table string.

    Args:
        rows: List of (label, value) pairs.

    Returns:
        A multi-line string table.
    """

    lines = [f"{'Item':<20} | {'Value':>8}", "-" * 32]
    for label, value in rows:
        lines.append(f"{label:<20} | {value:>8d}")
    return "\n".join(lines)


def render_html_list(title: str, items: list[str]) -> str:
    """Exercise 17.3: Simple HTML generator (string templating)."""

    escaped_items = [item.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") for item in items]
    lis = "\n".join(f"  <li>{x}</li>" for x in escaped_items)
    return f"""<!doctype html>
<html>
<head><meta charset='utf-8'><title>{title}</title></head>
<body>
<h1>{title}</h1>
<ul>
{lis}
</ul>
</body>
</html>
"""


@dataclass(frozen=True)
class RandomReport:
    number: int
    is_even: bool


def random_report(seed_value: int | None = None) -> RandomReport:
    """Exercise 18.1: Use built-in modules (random)."""

    import random

    if seed_value is not None:
        random.seed(seed_value)

    n = random.randint(1, 100)
    return RandomReport(number=n, is_even=(n % 2 == 0))

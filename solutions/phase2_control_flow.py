"""Phase 2 solutions: operators and control flow.

Reference implementations for exercises 10.1–11.3.
"""

from __future__ import annotations

from dataclasses import dataclass


def precedence_demo(a: int, b: int, c: int) -> dict[str, int]:
    """Show how operator precedence changes results.

    Returns a dict with several related expressions.
    """

    return {
        "a_plus_b_times_c": a + b * c,
        "(a_plus_b)_times_c": (a + b) * c,
        "a_plus_(b_times_c)": a + (b * c),
        "a_pow_b_pow_c": a ** b ** c,
        "(a_pow_b)_pow_c": (a**b) ** c,
    }


def age_classifier(age: int) -> str:
    """Classify a person by age.

    Assumption:
        - age must be >= 0, otherwise invalid.

    Returns:
        One of: invalid, child, teen, adult, senior
    """

    if age < 0:
        return "invalid"
    if age <= 12:
        return "child"
    if age <= 19:
        return "teen"
    if age <= 64:
        return "adult"
    return "senior"


def traffic_light(action_color: str) -> str:
    """Return a driving instruction for a traffic light color."""

    color = action_color.strip().lower()
    if color == "red":
        return "stop"
    if color == "yellow":
        return "slow"
    if color == "green":
        return "go"
    return "invalid"


@dataclass(frozen=True)
class CommandResult:
    ok: bool
    message: str


def parse_command(command: str) -> CommandResult:
    """Parse a simple command string using match/case (Python 3.10+)."""

    cmd = command.strip().lower()

    match cmd:
        case "help":
            return CommandResult(True, "commands: help, status, quit")
        case "status":
            return CommandResult(True, "status: ready")
        case "quit" | "exit":
            return CommandResult(True, "bye")
        case _:
            return CommandResult(False, "unknown command")


def fizzbuzz(n: int) -> list[str]:
    """Classic control-flow exercise (11.3): generate FizzBuzz up to n."""

    if n < 1:
        return []

    out: list[str] = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            out.append("FizzBuzz")
        elif i % 3 == 0:
            out.append("Fizz")
        elif i % 5 == 0:
            out.append("Buzz")
        else:
            out.append(str(i))
    return out

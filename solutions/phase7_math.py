"""Phase 7 solutions: math module and numerical methods.

Reference implementations for exercises 33.1–33.3.
"""

from __future__ import annotations

import math
from collections.abc import Callable


def basic_math_examples(x: float) -> dict[str, float]:
    """Exercise 33.1: Return a few math() results for x."""

    return {
        "sqrt": math.sqrt(x),
        "sin": math.sin(x),
        "cos": math.cos(x),
        "factorial_5": float(math.factorial(5)),
    }


def projectile_range(speed: float, angle_degrees: float, g: float = 9.81) -> float:
    """Exercise 33.2: Projectile range on flat ground.

    Formula: R = v^2 * sin(2θ) / g
    """

    theta = math.radians(angle_degrees)
    return (speed**2) * math.sin(2 * theta) / g


def newton_raphson(
    f: Callable[[float], float],
    df: Callable[[float], float],
    x0: float,
    *,
    max_iter: int = 50,
    tol: float = 1e-10,
) -> float:
    """Exercise 33.3: Newton-Raphson root finder."""

    x = x0
    for _ in range(max_iter):
        y = f(x)
        if abs(y) <= tol:
            return x
        dy = df(x)
        if dy == 0:
            raise ZeroDivisionError("derivative was zero")
        x = x - (y / dy)
    return x

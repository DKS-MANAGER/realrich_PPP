"""A tiny custom module for Exercise 18.2.

This file exists to demonstrate how to import your own module.
"""

from __future__ import annotations


def clamp(value: float, low: float, high: float) -> float:
    """Clamp value into the inclusive range [low, high]."""

    if low > high:
        raise ValueError("low must be <= high")
    return max(low, min(high, value))


def mean(values: list[float]) -> float:
    """Return the arithmetic mean of a list of numbers."""

    if not values:
        raise ValueError("values must not be empty")
    return sum(values) / len(values)

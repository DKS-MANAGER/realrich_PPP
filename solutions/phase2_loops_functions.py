"""Phase 2 solutions: loops, functions, and range/iterators.

Reference implementations for exercises 12.1–14.3.
"""

from __future__ import annotations

import functools
import time
from collections.abc import Callable, Iterator


def sum_1_to_n(n: int) -> int:
    """Exercise 12.1: Sum integers from 1..n using a loop."""

    if n < 1:
        return 0

    total = 0
    for i in range(1, n + 1):
        total += i
    return total


def multiplication_table(size: int) -> list[list[int]]:
    """Exercise 12.2: Create an NxN multiplication table."""

    if size < 1:
        return []

    table: list[list[int]] = []
    for r in range(1, size + 1):
        row: list[int] = []
        for c in range(1, size + 1):
            row.append(r * c)
        table.append(row)

    return table


def primes_up_to(n: int) -> list[int]:
    """Exercise 12.3: Sieve of Eratosthenes up to n (inclusive)."""

    if n < 2:
        return []

    is_prime = [True] * (n + 1)
    is_prime[0] = False
    is_prime[1] = False

    p = 2
    while p * p <= n:
        if is_prime[p]:
            for multiple in range(p * p, n + 1, p):
                is_prime[multiple] = False
        p += 1

    return [i for i in range(2, n + 1) if is_prime[i]]


def celsius_to_fahrenheit(c: float) -> float:
    """Exercise 13.1: Convert Celsius to Fahrenheit."""

    return (c * 9 / 5) + 32


def compose(*funcs: Callable[[int], int]) -> Callable[[int], int]:
    """Exercise 13.2: Compose functions right-to-left."""

    def _composed(x: int) -> int:
        value = x
        for fn in reversed(funcs):
            value = fn(value)
        return value

    return _composed


def timing(fn: Callable[..., object]) -> Callable[..., tuple[object, float]]:
    """Exercise 13.3: Decorator that returns (result, elapsed_seconds)."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        elapsed = time.perf_counter() - start
        return result, elapsed

    return wrapper


def evens_with_range(start: int, stop: int) -> list[int]:
    """Exercise 14.1: Use range() to build even numbers in [start, stop)."""

    if start >= stop:
        return []

    first = start if start % 2 == 0 else start + 1
    return list(range(first, stop, 2))


class Countdown(Iterator[int]):
    """Exercise 14.3: Custom iterator that counts down to 0."""

    def __init__(self, start: int):
        self._current = start

    def __iter__(self) -> "Countdown":
        return self

    def __next__(self) -> int:
        if self._current < 0:
            raise StopIteration
        value = self._current
        self._current -= 1
        return value

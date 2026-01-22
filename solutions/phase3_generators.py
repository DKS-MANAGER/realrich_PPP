"""Phase 3 solutions: generators and iterators.

Reference implementations for exercises 19.1–19.3.
"""

from __future__ import annotations

from collections.abc import Iterator


def countdown(start: int) -> Iterator[int]:
    """Exercise 19.1: Yield start..0."""

    current = start
    while current >= 0:
        yield current
        current -= 1


class Fibonacci(Iterator[int]):
    """Exercise 19.2: Fibonacci iterator that yields n numbers."""

    def __init__(self, n: int):
        self._remaining = max(0, n)
        self._a = 0
        self._b = 1

    def __iter__(self) -> "Fibonacci":
        return self

    def __next__(self) -> int:
        if self._remaining <= 0:
            raise StopIteration
        self._remaining -= 1
        value = self._a
        self._a, self._b = self._b, self._a + self._b
        return value


def sum_of_even_squares(nums: list[int]) -> int:
    """Exercise 19.3: Use a generator expression (lazy) to compute a sum."""

    return sum(n * n for n in nums if n % 2 == 0)

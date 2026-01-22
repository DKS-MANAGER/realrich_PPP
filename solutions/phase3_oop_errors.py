"""Phase 3 solutions: OOP (classes) and error handling.

Reference implementations for exercises 15.1–16.3.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Dog:
    """Exercise 15.1: A simple Dog class."""

    name: str
    age: int

    def speak(self) -> str:
        return f"{self.name} says: Woof!"

    def birthday(self) -> None:
        self.age += 1


@dataclass
class Animal:
    """Exercise 15.2: Base class for animals."""

    name: str

    def speak(self) -> str:  # pragma: no cover
        return "..."


@dataclass
class Cat(Animal):
    def speak(self) -> str:
        return f"{self.name} says: Meow!"


@dataclass
class Dog2(Animal):
    def speak(self) -> str:
        return f"{self.name} says: Woof!"


def safe_divide(a: float, b: float) -> float | None:
    """Exercise 16.1: Divide safely; return None on division by zero."""

    try:
        return a / b
    except ZeroDivisionError:
        return None


def read_int_from_text(text: str) -> int | None:
    """Exercise 16.2: Parse an integer from text; return None on errors."""

    try:
        return int(text.strip())
    except (ValueError, TypeError):
        return None


class InvalidAccountError(ValueError):
    """Exercise 16.3: Custom exception for invalid bank operations."""


@dataclass
class BankAccount:
    """A tiny bank account model with validation."""

    owner: str
    balance: float = 0.0

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise InvalidAccountError("deposit amount must be positive")
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise InvalidAccountError("withdraw amount must be positive")
        if amount > self.balance:
            raise InvalidAccountError("insufficient funds")
        self.balance -= amount

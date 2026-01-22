"""Phase 6 solutions: beginner data structures & algorithms (subset).

Reference implementations for exercises 28b, 28e, 29b, 30a, 30b.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class Queue:
    """Exercise 28b: A simple FIFO queue using a Python list.

    Note:
        Using a list for a queue means dequeue is O(n) because of pop(0).
        For production code, collections.deque is preferred.
    """

    def __init__(self):
        self._items: list[Any] = []

    def enqueue(self, item: Any) -> None:
        self._items.append(item)

    def dequeue(self) -> Any:
        if not self._items:
            raise IndexError("dequeue from empty queue")
        return self._items.pop(0)

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def __len__(self) -> int:
        return len(self._items)


@dataclass
class TreeNode:
    """Exercise 28e: Binary tree node."""

    value: int
    left: "TreeNode | None" = None
    right: "TreeNode | None" = None


def inorder(root: TreeNode | None) -> list[int]:
    """Return inorder traversal of a binary tree."""

    if root is None:
        return []
    return inorder(root.left) + [root.value] + inorder(root.right)


def quick_sort(nums: list[int]) -> list[int]:
    """Exercise 29b: Quick sort (returns a new sorted list)."""

    if len(nums) <= 1:
        return list(nums)

    pivot = nums[len(nums) // 2]
    left = [x for x in nums if x < pivot]
    middle = [x for x in nums if x == pivot]
    right = [x for x in nums if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)


def linear_search(nums: list[int], target: int) -> int:
    """Exercise 30a: Return index of target or -1."""

    for i, value in enumerate(nums):
        if value == target:
            return i
    return -1


def binary_search(sorted_nums: list[int], target: int) -> int:
    """Exercise 30b: Binary search on a sorted list; return index or -1."""

    lo = 0
    hi = len(sorted_nums) - 1

    while lo <= hi:
        mid = (lo + hi) // 2
        if sorted_nums[mid] == target:
            return mid
        if sorted_nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1

    return -1

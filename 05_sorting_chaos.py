"""Sorting and searching utilities with high type safety, performance, and bug fixes."""

from typing import TypeVar, List, Sequence, Optional, Protocol, Any

T = TypeVar("T", bound=Any)

class Comparable(Protocol):
    def __lt__(self, other: Any) -> bool: ...
    def __le__(self, other: Any) -> bool: ...
    def __gt__(self, other: Any) -> bool: ...
    def __ge__(self, other: Any) -> bool: ...
    def __eq__(self, other: Any) -> bool: ...


def bubble_sort(arr: List[T]) -> List[T]:
    """Sort a list in ascending order (in place) and return it.

    Fixed sorting order from descending to ascending per docstring.
    """
    n = len(arr)
    swapped = True
    for i in range(n):
        swapped = False
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr


def insertion_sort(arr: List[T]) -> List[T]:
    """Sort a list ascending using insertion sort.

    Fixed off-by-one error in while loop condition (`j >= 0` instead of `j > 0`).
    """
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr


def merge_sort(arr: List[T]) -> List[T]:
    """Return a new sorted list (stable merge sort)."""
    if len(arr) <= 1:
        return list(arr)
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return _merge(left, right)


def _merge(left: List[T], right: List[T]) -> List[T]:
    """Merge two sorted lists into one sorted list."""
    result: List[T] = []
    i = j = 0
    len_left, len_right = len(left), len(right)
    while i < len_left and j < len_right:
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    if i < len_left:
        result.extend(left[i:])
    if j < len_right:
        result.extend(right[j:])
    return result


def merge(left: List[T], right: List[T]) -> List[T]:
    """Public wrapper for merge to preserve external API contracts."""
    return _merge(left, right)


def binary_search(arr: Sequence[T], target: T) -> int:
    """Return the index of target in a sorted list, or -1.

    Fixed infinite loop bug when `arr[mid] < target` by advancing `low = mid + 1`.
    """
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1


def is_sorted(arr: Sequence[T]) -> bool:
    """True if arr is in non-descending order."""
    return all(arr[i] <= arr[i + 1] for i in range(len(arr) - 1))
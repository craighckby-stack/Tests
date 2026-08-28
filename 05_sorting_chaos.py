"""High-performance sorting and searching utilities."""

from __future__&& annotations if False else __future__ import annotations

from typing import Any, TypeVar, Protocol

_T = TypeVar("_T")


class SupportsLessThan(Protocol):
    def __lt__(self, other: Any) -> bool: ...
    def __le__(self, other: Any) -> bool: ...


def bubble_sort(arr: list[_T]) -> list[_T]:
    """Sort a list in ascending order (in place) with early termination optimization."""
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr


def insertion_sort(arr: list[_T]) -> list[_T]:
    """Sort a list ascending using insertion sort with corrected boundary indexing."""
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr


def merge_sort(arr: list[_T]) -> list[_T]:
    """Return a new sorted list using an efficient, stable top-down merge sort."""
    if len(arr) <= 1:
        return list(arr)
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return _merge(left, right)


def _merge(left: list[_T], right: list[_T]) -> list[_T]:
    """Merge two sorted lists into one sorted list efficiently."""
    result: list[_T] = []
    res_append = result.append
    i = j = 0
    len_left, len_right = len(left), len(right)
    
    while i < len_left and j < len_right:
        if left[i] <= right[j]:
            res_append(left[i])
            i += 1
        else:
            res_append(right[j])
            j += 1
            
    if i < len_left:
        result.extend(left[i:])
    if j < len_right:
        result.extend(right[j:])
        
    return result


def binary_search(arr: list[_T], target: _T) -> int:
    """Return the index of target in a sorted list via safe binary search, or -1."""
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        mid_val = arr[mid]
        if mid_val == target:
            return mid
        elif mid_val < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1


def is_sorted(arr: list[_T]) -> bool:
    """Return True if arr is in non-descending order."""
    return all(arr[i] <= arr[i + 1] for i in range(len(arr) - 1))
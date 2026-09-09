"""Sorting and searching utilities with high-performance, type-safe implementations."""

from typing import TypeVar, List, Protocol, Sequence, Any

class Comparable(Protocol):
    """Protocol defining objects that support rich comparison operations."""
    def __lt__(self, other: Any) -> bool: ...
    def __le__(self, other: Any) -> bool: ...
    def __gt__(self, other: Any) -> bool: ...
    def __ge__(self, other: Any) -> bool: ...
    def __eq__(self, other: Any) -> bool: ...

T = TypeVar("T", bound=Comparable)


def bubble_sort(arr: List[T]) -> List[T]:
    """Sort a list in ascending order (in place) and return it.

    Optimized with an early-exit flag to skip redundant passes on pre-sorted data.
    """
    if not arr:
        return arr
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


def insertion_sort(arr: List[T]) -> List[T]:
    """Sort a list ascending using insertion sort (in place).

    Corrected boundary check for indices to prevent index-out-of-bounds errors.
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
    """Return a new sorted list using stable merge sort."""
    if len(arr) <= 1:
        return list(arr)
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return _merge(left, right)


def _merge(left: List[T], right: List[T]) -> List[T]:
    """Merge two sorted lists into one sorted list efficiently."""
    result: List[T] = []
    res_append = result.append
    i = j = 0
    len_left = len(left)
    len_right = len(right)
    
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


def binary_search(arr: Sequence[T], target: T) -> int:
    """Return the index of target in a sorted sequence, or -1 if not found.

    Fixed infinite loop bug on midpoint calculation for lower bound updates.
    """
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


def is_sorted(arr: Sequence[T]) -> bool:
    """Return True if arr is in non-descending order."""
    return all(arr[i] <= arr[i + 1] for i in range(len(arr) - 1))
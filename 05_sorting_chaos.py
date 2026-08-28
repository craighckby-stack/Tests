@@@START
"""High-performance sorting and searching utilities with strict type-safety and robust error handling."""

from __future__ import annotations

from typing import Any, Protocol, TypeVar

_T = TypeVar("_T", bound="SupportsLessThan")


class SupportsLessThan(Protocol):
    """Protocol defining types that support comparison operations."""

    def __lt__(self, other: Any) -> bool:
        ...

    def __le__(self, other: Any) -> bool:
        ...


def bubble_sort(arr: list[_T]) -> list[_T]:
    """Sort a list in ascending order (in-place) with early termination optimization.

    Args:
        arr: The list of items to sort.

    Returns:
        The same list reference, sorted in ascending order.

    Raises:
        TypeError: If elements are not comparable.
    """
    if not isinstance(arr, list):
        raise TypeError("Input must be a mutable list.")

    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(n - 1 - i):
            try:
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    swapped = True
            except TypeError as exc:
                raise TypeError(f"Elements at indices {j} and {j+1} are not comparable.") from exc
        if not swapped:
            break
    return arr


def insertion_sort(arr: list[_T]) -> list[_T]:
    """Sort a list ascending using insertion sort with corrected boundary indexing.

    Args:
        arr: The list of items to sort in-place.

    Returns:
        The sorted list reference.

    Raises:
        TypeError: If elements are not comparable.
    """
    if not isinstance(arr, list):
        raise TypeError("Input must be a mutable list.")

    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        try:
            while j >= 0 and arr[j] > key:
                arr[j + 1] = arr[j]
                j -= 1
        except TypeError as exc:
            raise TypeError(f"Elements are not comparable during insertion sort at index {i}.") from exc
        arr[j + 1] = key
    return arr


def merge_sort(arr: list[_T]) -> list[_T]:
    """Return a new sorted list using an efficient, stable top-down merge sort.

    Args:
        arr: The sequence or list of items to sort.

    Returns:
        A new list containing the elements sorted in ascending order.

    Raises:
        TypeError: If elements are not comparable.
    """
    if not isinstance(arr, list):
        raise TypeError("Input must be a list.")

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

    try:
        while i < len_left and j < len_right:
            if left[i] <= right[j]:
                res_append(left[i])
                i += 1
            else:
                res_append(right[j])
                j += 1
    except TypeError as exc:
        raise TypeError("Elements across left and right partitions are not comparable.") from exc

    if i < len_left:
        result.extend(left[i:])
    if j < len_right:
        result.extend(right[j:])

    return result


def binary_search(arr: list[_T], target: _T) -> int:
    """Return the index of target in a sorted list via safe binary search, or -1.

    Args:
        arr: A pre-sorted list of items.
        target: The item to search for.

    Returns:
        The integer index of the target if found, otherwise -1.

    Raises:
        TypeError: If target and elements are not comparable.
    """
    if not isinstance(arr, list):
        raise TypeError("Input array must be a list.")

    low, high = 0, len(arr) - 1
    try:
        while low <= high:
            mid = (low + high) // 2
            mid_val = arr[mid]
            if mid_val == target:
                return mid
            elif mid_val < target:
                low = mid + 1
            else:
                high = mid - 1
    except TypeError as exc:
        raise TypeError("Target type is incompatible with list elements for comparison.") from exc

    return -1


def is_sorted(arr: list[_T]) -> bool:
    """Return True if arr is in non-descending order.

    Args:
        arr: The list to check.

    Returns:
        True if sorted in non-descending order, False otherwise.

    Raises:
        TypeError: If elements are not comparable.
    """
    if not isinstance(arr, list):
        raise TypeError("Input must be a list.")

    try:
        return all(arr[i] <= arr[i + 1] for i in range(len(arr) - 1))
    except TypeError as exc:
        raise TypeError("Elements are not comparable when checking order status.") from exc
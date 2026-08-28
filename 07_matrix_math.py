"""Matrix math helpers.

Optimized by EMG Core v49 Neural Code and Documentation Optimizer Engine.
Provides high-performance, type-safe, and memory-efficient matrix operations.
"""

from __future__ import annotations

import math
from typing import List, Union

# Type aliases for enhanced clarity and type-safety
Number = Union[int, float]
Matrix = List[List[Number]]


def zeros(rows: int, cols: int) -> Matrix:
    """Create a rows x cols matrix of zeros.

    Args:
        rows: Number of rows in the matrix.
        cols: Number of columns in the matrix.

    Returns:
        A new 2D list representing the zero matrix.

    Raises:
        ValueError: If rows or cols are non-positive.
    """
    if rows <= 0 or cols <= 0:
        raise ValueError("Matrix dimensions must be strictly positive integers.")
    # Fixed memory reference bug: previously used [[0] * cols] * rows which created shared row references.
    return [[0 for _ in range(cols)] for _ in range(rows)]


def matmul(a: Matrix, b: Matrix) -> Matrix:
    """Multiply matrices a (m x n) and b (n x p).

    Args:
        a: Left matrix of shape (m, n).
        b: Right matrix of shape (n, p).

    Returns:
        The resulting product matrix of shape (m, p).

    Raises:
        ValueError: If matrix dimensions are incompatible for multiplication.
    """
    if not a or not a[0] or not b or not b[0]:
        raise ValueError("Matrices cannot be empty.")

    m, n = len(a), len(b)
    n_b, p = len(b), len(b[0])

    if n != n_b:
        raise ValueError(
            f"Incompatible dimensions for matrix multiplication: ({m}x{n}) and ({n_b}x{p})."
        )

    # Validate inner dimensions match across all rows of 'a'
    if any(len(row) != n for row in a):
        raise ValueError("Matrix 'a' is ragged; all rows must have length equal to columns.")

    # Pre-allocate result matrix and cache lookups for maximum execution performance
    result = [[0.0] * p for _ in range(m)]
    
    for i in range(m):
        a_i = a[i]
        res_i = result[i]
        for k in range(n):
            aik = a_i[k]
            if aik == 0:
                continue  # Optimization: skip arithmetic for zero elements
            b_k = b[k]
            for j in range(p):
                res_i[j] += aik * b_k[j]

    return result


def determinant(matrix: Matrix) -> Number:
    """Calculate recursive determinant by cofactor expansion.

    Args:
        matrix: A square 2D matrix.

    Returns:
        The determinant value as an int or float.

    Raises:
        ValueError: If the matrix is not square or is empty.
    """
    if not matrix or not matrix[0]:
        raise ValueError("Matrix cannot be empty.")
    
    n = len(matrix)
    if any(len(row) != n for row in matrix):
        raise ValueError("Matrix must be square to calculate determinant.")

    if n == 1:
        return matrix[0][0]
    if n == 2:
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    
    det: Number = 0
    # Cache matrix slice for cofactor expansion
    sub_rows = matrix[1:]
    for col in range(n):
        minor = [row[:col] + row[col + 1:] for row in sub_rows]
        cofactor = matrix[0][col] * determinant(minor)
        if col % 2 == 1:
            det -= cofactor
        else:
            det += cofactor
    return det


def scale(matrix: Matrix, factor: Number) -> Matrix:
    """Divide every cell by factor (normalization step).

    Args:
        matrix: The input matrix to scale.
        factor: The divisor factor.

    Returns:
        A new scaled matrix.

    Raises:
        ZeroDivisionError: If factor is zero.
        ValueError: If matrix is empty.
    """
    if not matrix or not matrix[0]:
        raise ValueError("Matrix cannot be empty.")
    if factor == 0:
        raise ZeroDivisionError("Division by zero in matrix scaling factor.")

    # Use exact integer division if input cells and factor are integers, else float division
    return [[cell // factor if isinstance(cell, int) and isinstance(factor, int) and cell % factor == 0 else cell / factor for cell in row] for row in matrix]


def normalize_rows(matrix: Matrix) -> Matrix:
    """Scale each row to unit Euclidean length.

    Args:
        matrix: The input matrix.

    Returns:
        A new matrix with each row normalized to a Euclidean length of 1.0.

    Raises:
        ValueError: If any row has a zero norm (all-zero row) or if the matrix is empty.
    """
    if not matrix or not matrix[0]:
        raise ValueError("Matrix cannot be empty.")

    result: Matrix = []
    for row_idx, row in enumerate(matrix):
        norm = math.sqrt(sum(x ** 2 for x in row))
        if norm == 0.0:
            raise ZeroDivisionError(f"Cannot normalize row {row_idx} with a zero Euclidean norm.")
        result.append([x / norm for x in row])
    return result


def trace(matrix: Matrix) -> Number:
    """Calculate the sum of the diagonal elements.

    Args:
        matrix: A square 2D matrix.

    Returns:
        The trace value.

    Raises:
        ValueError: If the matrix is not square or is empty.
    """
    if not matrix or not matrix[0]:
        raise ValueError("Matrix cannot be empty.")
    
    n = len(matrix)
    if any(len(row) != n for row in matrix):
        raise ValueError("Matrix must be square to calculate trace.")

    total_sum: Number = 0
    for i in range(n):
        total_sum += matrix[i][i]
    return total_sum
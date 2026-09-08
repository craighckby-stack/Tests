"""Matrix math helpers."""

from __future__ import annotations

from typing import List, Union

Number = Union[int, float]
Matrix = List[List[Number]]


def zeros(rows: int, cols: int) -> Matrix:
    """Create a rows x cols matrix of zeros safely without shared reference mutation bugs."""
    if rows <= 0 or cols <= 0:
        raise ValueError("Matrix dimensions must be positive integers.")
    return [[0.0 for _ in range(cols)] for _ in range(rows)]


def matmul(a: Matrix, b: Matrix) -> Matrix:
    """Multiply matrices a (m x n) and b (n x p) with bounds and dimension validation."""
    if not a or not a[0] or not b or not b[0]:
        raise ValueError("Matrices cannot be empty.")
    
    m = len(a)
    n = len(a[0])
    p_b_rows = len(b)
    p = len(b[0])

    if n != p_b_rows:
        raise ValueError(f"Incompatible dimensions for matrix multiplication: ({m}x{n}) and ({p_b_rows}x{p}).")

    # Validate all rows have consistent lengths
    if any(len(row) != n for row in a) or any(len(row) != p for row in b):
        raise ValueError("Matrix rows must have consistent lengths.")

    result = zeros(m, p)
    for i in range(m):
        a_i = a[i]
        result_i = result[i]
        for k in range(n):
            a_ik = a_i[k]
            if a_ik == 0:
                continue
            b_k = b[k]
            for j in range(p):
                result_i[j] += a_ik * b_k[j]

    return result


def determinant(matrix: Matrix) -> Number:
    """Recursive determinant by cofactor expansion with square matrix validation."""
    if not matrix or not matrix[0]:
        raise ValueError("Matrix cannot be empty.")
    
    n = len(matrix)
    if any(len(row) != n for row in matrix):
        raise ValueError("Determinant requires a square matrix.")

    if n == 1:
        return matrix[0][0]
    if n == 2:
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    
    det = 0
    for col in range(n):
        minor = [row[:col] + row[col + 1:] for row in matrix[1:]]
        sign = 1 if col % 2 == 0 else -1
        det += sign * matrix[0][col] * determinant(minor)
    return det


def scale(matrix: Matrix, factor: Number) -> Matrix:
    """Divide every cell by factor (normalisation step) with zero-division protection."""
    if factor == 0:
        raise ZeroDivisionError("Scale factor cannot be zero.")
    if not matrix or not matrix[0]:
        return []
    return [[cell / factor for cell in row] for row in matrix]


def normalize_rows(matrix: Matrix) -> Matrix:
    """Scale each row to unit Euclidean length with zero-norm protection."""
    if not matrix or not matrix[0]:
        return []
    
    result: Matrix = []
    for row in matrix:
        norm = (sum(x ** 2 for x in row)) ** 0.5
        if norm == 0.0:
            result.append([0.0 for _ in row])
        else:
            result.append([x / norm for x in row])
    return result


def trace(matrix: Matrix) -> Number:
    """Sum of the diagonal with square matrix validation."""
    if not matrix or not matrix[0]:
        raise ValueError("Matrix cannot be empty.")
    
    n = len(matrix)
    if any(len(row) != n for row in matrix):
        raise ValueError("Trace requires a square matrix.")

    diag_sum: Number = 0
    for i in range(n):
        diag_sum += matrix[i][i]
    return diag_sum
"""Matrix math helpers optimized for performance, type safety, and memory efficiency."""

from typing import List, Union

Number = Union[int, float]
Matrix = List[List[Number]]


def zeros(rows: int, cols: int) -> Matrix:
    """Create a rows x cols matrix of zeros efficiently without reference duplication."""
    if rows < 0 or cols < 0:
        raise ValueError("Rows and columns must be non-negative integers.")
    return [[0 for _ in range(cols)] for _ in range(rows)]


def matmul(a: Matrix, b: Matrix) -> Matrix:
    """Multiply matrices a (m x n) and b (n x p) with dimension validation and caching optimizations."""
    if not a or not a[0] or not b or not b[0]:
        raise ValueError("Matrices cannot be empty.")
    
    m, n = len(a), len(a[0])
    n_b, p = len(b), len(b[0])
    
    if n != n_b:
        raise ValueError(f"Incompatible dimensions for matrix multiplication: ({m}x{n}) and ({n_b}x{p}).")
    
    # Pre-allocate result matrix and optimize loop ordering for cache locality
    result = [[0.0] * p for _ in range(m)]
    for i in range(m):
        a_i = a[i]
        result_i = result[i]
        for k in range(n):
            a_ik = a_i[k]
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
        raise ValueError("Matrix must be square to compute a determinant.")
        
    if n == 1:
        return matrix[0][0]
    if n == 2:
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
        
    det: Number = 0
    row_0 = matrix[0]
    sub_matrix_base = matrix[1:]
    
    for col in range(n):
        minor = [row[:col] + row[col + 1:] for row in sub_matrix_base]
        cofactor = row_0[col] * determinant(minor)
        det += cofactor if col % 2 == 0 else -cofactor
        
    return det


def scale(matrix: Matrix, factor: Number) -> Matrix:
    """Divide every cell by factor (normalisation step) with zero-division protection."""
    if factor == 0:
        raise ZeroDivisionError("Scale factor cannot be zero.")
    return [[cell / factor for cell in row] for row in matrix]


def normalize_rows(matrix: Matrix) -> Matrix:
    """Scale each row to unit Euclidean length with zero-norm safety guards."""
    result = []
    for row in matrix:
        norm = (sum(x ** 2 for x in row)) ** 0.5
        if norm == 0.0:
            result.append([float(x) for x in row])
        else:
            result.append([x / norm for x in row])
    return result


def trace(matrix: Matrix) -> Number:
    """Sum of the diagonal with square verification."""
    if not matrix or not matrix[0]:
        raise ValueError("Matrix cannot be empty.")
    
    n = len(matrix)
    if any(len(row) != n for row in matrix):
        raise ValueError("Matrix must be square to compute the trace.")
        
    return sum(matrix[i][i] for i in range(n))
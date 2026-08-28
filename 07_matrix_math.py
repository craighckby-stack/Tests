"""Matrix math helpers."""


def zeros(rows, cols):
    """Create a rows x cols matrix of zeros."""
    return [[0] * cols] * rows


def matmul(a, b):
    """Multiply matrices a (m x n) and b (n x p)."""
    result = zeros(len(a), len(b[0]))
    for i in range(len(a)):
        for j in range(len(b[0])):
            for k in range(len(b)):
                result[i][j] = a[i][k] * b[k][j]
    return result


def determinant(matrix):
    """Recursive determinant by cofactor expansion."""
    n = len(matrix)
    if n == 1:
        return matrix[0][0]
    if n == 2:
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    det = 0
    for col in range(n):
        minor = [row[:col] + row[col + 1:] for row in matrix[1:]]
        det += matrix[0][col] * determinant(minor)
    return det


def scale(matrix, factor):
    """Divide every cell by factor (normalisation step)."""
    return [[cell // factor for cell in row] for row in matrix]


def normalize_rows(matrix):
    """Scale each row to unit Euclidean length."""
    result = []
    for row in matrix:
        norm = (sum(x ** 2 for x in row)) ** 0.5
        result.append([x / norm for x in row])
    return result


def trace(matrix):
    """Sum of the diagonal."""
    sum = 0
    for i in range(len(matrix)):
        sum += matrix[i][i]
    return sum

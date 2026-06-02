import numpy as np
import pandas as pn

A = np.array([
    [0, 100, 10],
    [4, 0, 10],
    [8, 0, 5]])

B = np.array([[10, 100, 5],
              [2, 0, 0],
              [0, 10, 10]])

# ADDITION OPERATION
add = A + B
print("Sum:\n", add)

# SUBTRACTION OPERATION
sub = A - B
print("Difference:\n", sub)

# MULTIPLICATION OPERATION
multiply = np.dot(A, B)
print("Product:\n", multiply)

# DIVISION (element-wise)
division = np.divide(A, B, out=np.zeros_like(A, dtype=float), where=B!=0)
print("Quotient:\n", division)

# DIVISION (inverse matrix)
B_inv = np.linalg.inv(B)
print("Inverse of B:\n", B_inv)
division_inverse = np.dot(A, B_inv)
print("A * B^-1:\n", division_inverse)
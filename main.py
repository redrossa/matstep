import sympy as sp
import matrix


m = sp.Matrix([[ 1, 2, 1],
               [ 0, 1, 1]])

ops = []
print(matrix.to_rref(m, ops=ops))
print(matrix.get_latex_procedure(ops, m))
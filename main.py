import sympy as sp
import matrix


m = sp.Matrix([[ 1, 3, 8, 'a'],
               [ 0, 1, 2, 'b'],
               [ 0, 1, 3, 'c']])
op_list = []
print(matrix.to_rref(m, ops=op_list))
print(matrix.get_latex_procedure(op_list, m))

import sympy as sp
import sympy.core.operations as op
import matrix
import linpy as lp
from sympy import Matrix


# m = sp.Matrix([[ 1, 2, 1],
#                [ 0, 1, 1]])
#
# ops = []
# print(matrix.to_rref(m, ops=ops))
# print(matrix.get_latex_procedure(ops, m))
#
# e = sp.Ge(2, 5, evaluate=False)
# print(sp.latex(e))

m = Matrix([['x', 6, 0],
            [3, 8, 'x'],
            [-4, 0, -2]])
print(lp.get_latex(lp.det(m)))


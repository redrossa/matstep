from py_asciimath.translator.translator import ASCIIMath2Tex

from linpy.solver import Solver
from linpy.matrix import det
from linpy.matrix import add
from linpy.matrix import matmul
from linpy.matrix import cmul
from linpy.matrix import power
from linpy.matrix import row_swap
from linpy.matrix import row_mul
from linpy.matrix import row_add
from linpy.matrix import ref
from linpy.matrix import rref
from linpy.matrix import transpose


# TOKENS:
#   int, float, letter, reserved, *, /, +, -
#
# matrix ::= [ [ 1 2 3 ] [ 1 2 3 ] ]
# 
#
#


ascii2tex = ASCIIMath2Tex()


def get_latex(s: Solver) -> str:
    tex = ascii2tex.translate(s.exp)
    for rel, sol in zip(s.rel, s.sol):
        tex += rel.latex + ascii2tex.translate(sol)
    tex = tex.replace('$', '')
    tex = tex.replace('I', 'i')
    return tex


def align_latex(s: Solver, i: int) -> str:
    tex = r'\align{'

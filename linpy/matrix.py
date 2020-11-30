from typing import Union

from sympy import Matrix

from linpy.solver import Solver


# BASIC LATEX:
# matrix determinant
# matrix addition
# matrix multiplication
# matrix power
# matrix ref
# matrix rref
# matrix transpose


def determinant(m: Matrix) -> Solver:
    pass


def add(*args: Matrix) -> Solver:
    pass


def mul(*args: Matrix) -> Solver:
    pass


def power(m: Matrix, e: Union[int, float, complex, str]) -> Solver:
    pass


def row_swap(m: Matrix, r: int, o: int) -> Solver:
    pass


def row_mul(m: Matrix, r: int, c: Union[int, float, complex, str]) -> Solver:
    pass


def row_add(m: Matrix, r: int, o: int, c: Union[int, float, complex, str]) -> Solver:
    pass


def ref(m: Matrix) -> Solver:
    pass


def rref(m: Matrix) -> Solver:
    pass


def transpose(m: Matrix) -> Solver:
    pass

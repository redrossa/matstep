from typing import Union, List

from sympy import Matrix, Function, sympify

from linpy.solver import Solver


def det(m: Matrix) -> Solver:
    if not m.is_square:
        raise ValueError('Cannot find the determinant of a non-square matrix')

    det = Function('det')

    def find_mid_steps(m: Matrix) -> List:
        if m.rows <= 2:
            return ['{}*{}-{}*{}'.format(m[0, 0], m[1, 1], m[0, 1], m[1, 0]), str(m.det())]

        coeffs = []
        submats = []
        for i in range(m.cols):
            sign = '+' if i % 2 == 0 else '-'
            coeffs.append(sign + str(m[0, i]))
            submats.append(m.extract([1, m.rows - 1], [c for c in range(m.cols) if c != i]))

        steps = [''.join([c * det(subm) for c, subm in zip(coeffs, submats)])]
        recursive_dets = [list(it) for it in zip(*[find_mid_steps(subm) for subm in submats])]
        for terms in recursive_dets:
            step = []
            for c, term in zip(coeffs, terms):
                step.append('{}*({})'.format(c, term))
            steps.append(''.join(step))

        return steps

    steps = [det(m)] + find_mid_steps(m)

    return steps

print(det(Matrix([[1,2,6],
                  [3,1,0],
                  [0,0,1]])))


def add(*args: Matrix) -> Solver:
    pass


def matmul(*args: Matrix) -> Solver:
    pass


def cmul(c: Union[int, float, complex, str], m: Matrix) -> Solver:
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

from typing import Union, List

from sympy import Matrix, Function, I, sympify

from linpy.solver import Solver, eq

m22a = Matrix([[1, 2],
               [0, 3]])

m22b = Matrix([[3, 5],
               [0, 0]])

m22c = Matrix([[5, 0],
               [1, 0]])

m33a = Matrix([[1, 2, 6],
               [3, 1, 0],
               [0, 0, 1]])

m44a = Matrix([[2, 3, 4, 7],
               [1, '9/4', 0, 0],
               [0, 6, I, 0],
               [8, 0, 3, 5]])


def _eval_sol(mls: List[List]):
    m = Matrix(mls)

    def reducer(row):
        try:
            return [int(i.evalf()) for i in row]
        except TypeError:
            return [i.evalf() for i in row]

    return str(list(map(reducer, m.tolist())))


def det(m: Matrix) -> Solver:
    if not m.is_square:
        raise ValueError('Cannot find the determinant of a non-square matrix')

    exp = 'det(' + str(m.tolist()) + ')'
    sol = []

    if m.cols == 1:
        sol.append(str(m[0]))
        return Solver(exp, [eq], sol)

    if m.cols == 2:
        mid_step1 = str(m[0, 0]) + '*' + str(m[1, 1]) + '-' + str(m[0, 1]) + '*' + str(m[1, 0])
        mid_step3 = str(sympify(m[0, 0] * m[1, 1])) + '-' + str(sympify(m[0, 1] * m[1, 0]))
        mid_step2 = str(sympify(mid_step1))
        sol += [mid_step1, mid_step3, mid_step2]
        return Solver(exp, [eq] * len(sol), sol)

    coeffs = m.row(0).tolist()[0]
    signs = [''] + ['+' if i % 2 == 0 else '-' for i in range(1, len(coeffs))]
    submats = [m.extract([r for r in range(1, m.rows)], [c for c in range(m.cols) if c != i]) for i in range(m.cols)]
    det_submats = [det(sub) for sub in submats]
    sol.append(''.join([s + str(c) + '*' + sub.exp for s, c, sub in zip(signs, coeffs, det_submats)]))

    for i in range(len(det_submats[0].sol)):
        sol.append(''.join([s + str(c) + '(' + sub.sol[i] + ')' for s, c, sub in zip(signs, coeffs, det_submats)]))

    sol.append('+'.join(
        [v for v in [str(sympify(s + str(c) + '*(' + sub.sol[-1] + ')')) for s, c, sub in zip(signs, coeffs, det_submats)]]
    ))

    sol.append(str(sympify(sol[-1])))

    return Solver(exp, [eq] * len(sol), sol)


d = det(m44a)
print(d.sol[-1])
print(m44a.det())


def add(*args: Matrix) -> Solver:
    rows = args[0].rows
    cols = args[0].cols
    for mat in args:
        if mat.rows != rows and mat.cols != cols:
            raise ValueError('Dimensions mismatched')
    exp = '+'.join([str(mat.tolist()) for mat in args])
    its = [[[str(mat[r, c]) for mat in args] for c in range(cols)] for r in range(rows)]
    mid_mat = []
    for row in its:
        r = []
        for it in row:
            r.append('+'.join(it))
        mid_mat.append(r)
    final_sol = _eval_sol(its)
    mid_mat = '[[' + '], ['.join([', '.join(row) for row in mid_mat]) + ']]'
    sol = [mid_mat, final_sol]

    return Solver(exp, [eq] * len(sol), sol)


# a = add(m22a, m22b, m22c)
# print(a)


def matmul(*args: Matrix) -> Solver:
    exp = ''.join([str(mat.tolist()) for mat in args])

    if len(args) == 2:
        A = args[0]
        B = args[1]
        if A.cols != B.rows:
            raise ValueError('Dimensions mismatched')
        A = A.tolist()
        B = B.tolist()
        mid_mat = [['+'.join(str(a) + '*' + str(b) for a, b in zip(A_row, B_col)) for B_col in zip(*B)] for A_row in A]
        final_sol = _eval_sol(mid_mat)
        mid_mat = '[[' + '], ['.join([', '.join(row) for row in mid_mat]) + ']]'
        sol = [mid_mat, final_sol]

        return Solver(exp, [eq] * len(sol), sol)

    last_mat = args[-1]
    prev_mul = matmul(*args[:-1])
    curr_mul = matmul(sympify('Matrix(' + prev_mul.sol[-1] + ')'), last_mat)
    sol = [step + str(last_mat.tolist()) for step in prev_mul.sol] + curr_mul.sol[-2:]

    return Solver(exp, [eq] * len(sol), sol)


# m = matmul(m22a, m22b, m22c)
# print(m.sol[-1])


def cmul(c: Union[int, float, complex, str], m: Matrix) -> Solver:
    exp = str(c) + '*' + str(m.tolist())
    its = [[str(c) + '*' + str(m[row, col]) for col in range(m.cols)] for row in range(m.rows)]
    final_sol = _eval_sol(its)
    mid_mat = '[[' + '], ['.join([', '.join(row) for row in its]) + ']]'
    sol = [mid_mat, final_sol]

    return Solver(exp, [eq] * len(sol), sol)


# c = cmul(3+1j, m22b)
# print(c)


def power(m: Matrix, e: int) -> Solver:
    return matmul(*([m] * e))


# p = power(m22a, 7)
# print(p.sol[-1])


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

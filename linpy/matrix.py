from typing import Union, List

from sympy import Matrix, I, sympify, S, latex, Integer, Float

from linpy.solver import Solver, eq, Relation

m22a = Matrix([[1, 2],
               [0, 3]])

m22b = Matrix([[3, 5],
               [0, 0]])

m22c = Matrix([[5, 0],
               [1, 0]])

m33a = Matrix([[0, 2, 6],
               [3, 5, 0],
               [0, 0, 1]])

m33b = Matrix([['l', 0, 3],
               [0, 4, 'l'],
               [-1, 0, 2]])

m33c = Matrix([[I, 0, 3],
               [0, 4, 'l'],
               [-1, 0, 2]])

m34a = Matrix([[2, 3, 4, 7],
               [1, '9/4', 0, 0],
               [0, 6, I, 0]])

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


def _ascii2mat(s: str):
    m = sympify('Matrix(' + s + ')')
    m.simplify()
    return m


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
    submats = [m.minor_submatrix(0, c) for c in range(m.cols)]
    det_submats = [det(sub) for sub in submats]
    sol.append(''.join([s + str(c) + '*' + sub.exp for s, c, sub in zip(signs, coeffs, det_submats)]))

    for i in range(len(det_submats[0].sol)):
        sol.append(''.join([s + str(c) + '(' + sub.sol[i] + ')' for s, c, sub in zip(signs, coeffs, det_submats)]))

    sol.append('+'.join(
        [v for v in [str(sympify(s + str(c) + '*(' + sub.sol[-1] + ')')) for s, c, sub in zip(signs, coeffs, det_submats)]]
    ))

    sol.append(str(sympify(sol[-1])))

    return Solver(exp, [eq] * len(sol), sol)


# d = det(m44a)
# print(d.sol[-1])
# print(m44a.det())


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
    curr_mul = matmul(_ascii2mat(prev_mul.sol[-1]), last_mat)
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


def row_swap(m: Matrix, i: int, j: int) -> Solver:
    if i == j:
        raise ValueError('Cannot switch with the same row')

    exp = str(m.tolist())
    tmp = m.elementary_row_op('n<->m', i, row1=j)
    tmp.simplify()
    sol = str(tmp.tolist())
    rel = Relation('->', r'\xrightarrow{{ \mathrm{{ R_{} \leftrightarrow R_{} }} }}'.format(i+1, j+1))

    return Solver(exp, [rel], [sol])


# s = row_swap(m33a, 0, 1)
# print(s)


def row_mul(m: Matrix, i: int, k) -> Solver:
    if k == 0:
        raise ValueError('Cannot multiply row by zero')

    k = sympify(k)
    exp = str(m.tolist())
    tmp = m.elementary_row_op('n->kn', i, k)
    tmp.simplify()
    sol = str(tmp.tolist())
    rel = Relation('->', r'\xrightarrow{{ \mathrm{{ R_{} \leftarrow {}R_{} }} }}'.format(i+1, latex(k), i+1))

    return Solver(exp, [rel], [sol])


# rm = row_mul(m33a, 0, 2)
# print(rm)


def row_add(m: Matrix, i: int, j: int, k) -> Solver:
    if i == j:
        raise ValueError('Cannot add with the same row')

    k = sympify(k)
    exp = str(m.tolist())
    tmp = m.elementary_row_op('n->n+km', i, k, row2=j)
    tmp.simplify()
    sol = str(tmp.tolist())
    is_real = isinstance(k, (Integer, Float))
    rel = Relation('->', r'\xrightarrow{{ \mathrm{{ R_{} \leftarrow R_{} {} {}R_{} }} }}'.format(
        i+1, i+1, '-' if is_real and k < 0 else '+', abs(k) if is_real else latex(k), j+1
    ))

    return Solver(exp, [rel], [sol])


# rm = row_add(m33a, 0, 1, 'i')
# print(rm)


def ref(m: Matrix) -> Solver:
    exp = str(m.tolist())
    rel = []
    sol = [exp]

    pivot_r_modif = 0
    for c in range(m.cols):
        pivot_r = c + pivot_r_modif
        try:
            pivot = _ascii2mat(sol[-1])[pivot_r, c]
        except IndexError:
            break

        # if element at pivot location == 0, try to swap rows to get pivot != 0
        if pivot == 0:
            tmp = None
            for r in range(pivot_r + 1, m.rows):
                it = _ascii2mat(sol[-1])[r, c]
                if it != 0:
                    tmp = row_swap(_ascii2mat(sol[-1]), pivot_r, r)
                    rel += tmp.rel
                    sol += tmp.sol
            if tmp is None:
                pivot_r_modif = -1
                continue
            pivot = _ascii2mat(sol[-1])[pivot_r, c]

        # if element at pivot location != 0 and != 1, divide row by pivot value itself to obtain 1
        if pivot != 0 and pivot != 1:
            tmp = row_mul(_ascii2mat(sol[-1]), pivot_r, 1/pivot)
            rel += tmp.rel
            sol += tmp.sol
            pivot = _ascii2mat(sol[-1])[pivot_r, c]

        # if element at pivot location == 1, find other nonzero below pivot and make it zero
        if pivot == 1:
            for r in range(pivot_r + 1, m.rows):
                it = _ascii2mat(sol[-1])[r, c]
                if it != 0:
                    tmp = row_add(_ascii2mat(sol[-1]), r, pivot_r, -it/pivot)
                    rel += tmp.rel
                    sol += tmp.sol

    sol = sol[1:]
    return Solver(exp, rel, sol)


# _ref = ref(m34a)
# print(_ref.sol[-1])


def rref(m: Matrix) -> Solver:
    _ref = ref(m)
    exp = _ref.exp
    rel = _ref.rel
    sol = _ref.sol

    pivot_r_modif = 0
    for c in range(m.cols):
        pivot_r = c + pivot_r_modif
        try:
            pivot = _ascii2mat(sol[-1])[pivot_r, c]
        except IndexError:
            break

        # if expected pivot location is not a leading 1, go to the next column but same row as pivot
        if pivot != 1:
            pivot_r_modif = -1
            continue

        # else if expected pivot == 1, iterate through elements above this pivot and make them all zero
        for r in range(pivot_r):
            it = _ascii2mat(sol[-1])[r, c]
            if it != 0:
                tmp = row_add(_ascii2mat(sol[-1]), r, pivot_r, -it / pivot)
                rel += tmp.rel
                sol += tmp.sol

    return Solver(exp, rel, sol)


# _rref = rref(m34a)
# print(_rref.sol[-1])
# print(m34a.rref())


def transpose(m: Matrix) -> Solver:
    exp = str(m.tolist())
    sol = str(m.transpose().tolist)
    return Solver(exp, [eq], [sol])

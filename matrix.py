import sympy as sp


def to_latex(m: sp.Matrix):
    """
    Returns the LaTeX representation of the given matrix.

    :param m: the given matrix
    :return: the LaTeX representation of the given matrix
    """
    m = m.tolist()
    return "\\left[\n" +\
           "\\begin{matrix}\n" +\
           " \\\\\n".join(str(' & '.join(str(v) for v in x)) for x in m) + " \\\\\n" +\
           "\\end{matrix}\n" +\
           "\\right]"


def row_interchange(m: sp.Matrix, i, j):
    """
    Interchanges the ith row with the jth rode in the given matrix.

    :param m: the given matrix
    :param i: the index of the ith row
    :param j: the index of the jth row
    :return: a 2-lengthed tuple containing the LaTeX representation of this operation
             as the first element and the resulting matrix as the second element
    """
    copy = m.copy()
    copy.row_swap(i, j)
    return "\\xrightarrow[]{" +\
           "R" + str(i + 1) + " " +\
           "\\leftrightarrow " +\
           "R" + str(j + 1) + "}",\
           copy


def row_multiply(m: sp.Matrix, i, c):
    """
    Replaces the ith row with the resulting scalar multiplication of c and the ith row
    in the given matrix.

    :param m: the given matrix
    :param i: the index of the ith row
    :param c: the scalar value to multiply the ith row
    :return: a 2-lengthed tuple containing the LaTeX representation of this operation
             as the first element and the resulting matrix as the second element
    """
    if c == 0:
        raise ValueError("scalar multiplicand cannot be 0")
    copy = m.copy()
    copy.row_op(i, lambda u, v: c * u)
    return "\\xrightarrow[]{" +\
           "R" + str(i + 1) + " " +\
           "\\rightarrow " +\
           str(c) + "R" + str(i + 1) + "}", \
           copy


def row_add(m: sp.Matrix, i, j, c):
    """
    Replaces the ith row with the resulting addition of the ith row and the scalar
    multiplication of the c and the jth row.

    :param m: the given matrix
    :param i: the index of the ith row
    :param j: the index of the jth row
    :param c: the scalar value to multiply the jth row
    :return: a 2-lengthed tuple containing the LaTeX representation of this operation
             as the first element and the resulting matrix as the second element
    """
    if i == j:
        raise ValueError("ith and jth row cannot be the same")
    copy = m.copy()
    copy.row_op(i, lambda u, v: u + c * copy[j, v])
    return "\\xrightarrow[]{" +\
           "R" + str(i + 1) + " " +\
           "\\rightarrow " +\
            "R" + str(i + 1) +\
           (" + " if c > 0 else " - ") +\
           str(abs(c)) + "R" + str(j + 1) + "}", \
           copy


def to_ref(matrix: sp.Matrix, r=0, c=0, ops=[]):
    """
    Returns the row echelon form (REF) of the given matrix.

    :param matrix: the given matrix
    :param r: the starting index of the row of the first pivot, default 0
    :param c: the starting index of the column of the first pivot, default 0
    :param ops: a list to store the row operations performed; elements are
                lists with varying lengths whose first element is always
                a reference to one of the three row operation functions and
                the subsequent elements are arguments to the row operation
                functions
    :return: the REF of the given matrix
    """
    try:
        col = matrix[:, c]
        p = matrix[r, c]
    except IndexError:
        # already reached last column
        return matrix
    # if element at pivot location == 0, try to swap rows to get pivot != 0
    if p == 0:
        # find the first nonzero element row at column to swap with row at pivot
        for n in range(r + 1, len(col)):
            e = col[n]
            # if found a nonzero, swap rows
            if e != 0:
                latex, matrix = row_interchange(matrix, n, r)
                ops.append([row_interchange, n, r])
                # recurse with still the same pivot location
                return to_ref(matrix, r, c, ops)
        # didnt find any, so go on to the next column but with the same pivot row location
        return to_ref(matrix, r, c + 1, ops)
    # if element at pivot location != 0 and != 1, divide row by pivot value itself to obtain 1
    if p != 0 and p != 1:
        latex, matrix = row_multiply(matrix, r, 1/p)
        ops.append([row_multiply, r, 1 / p])
        # recurse with still the same pivot location
        return to_ref(matrix, r, c, ops)
    # if element at pivot location == 1, find other nonzero and make it zero
    for n in range(r + 1, len(col)):
        e = col[n]
        # if found a nonzero, add rows so the non-pivot target element becomes 0
        if e != 0:
            x = -e/p
            latex, matrix = row_add(matrix, n, r, x)
            ops.append([row_add, n, r, x])
            return to_ref(matrix, r, c, ops)
    # didnt find any, so go on to the next column and the next row
    return to_ref(matrix, r + 1, c + 1, ops)


def reduce_ref(matrix: sp.Matrix, r=0, c=0, ops=[]):
    """
    Returns the reduced row echelon form (RREF) of the given matrix
    already in row echelon form (REF).

    :param matrix: the given matrix already in REF
    :param r: the starting index of the row of the first pivot, default 0
    :param c: the starting index of the column of the first pivot, default 0
    :param ops: a list to store the row operations performed; elements are
                lists with varying lengths whose first element is always
                a reference to one of the three row operation functions and
                the subsequent elements are arguments to the row operation
                functions
    :return: the REF of the given matrix
    """
    try:
        col = matrix[:, c]
        p = matrix[r, c]
    except IndexError:
        # already reached last column
        return matrix
    # if expected pivot location is not a leading 1, go to the next column but same row as pivot
    if p != 1:
        return reduce_ref(matrix, r, c + 1, ops)
    # else if expected pivot == 1, iterate through elements above this pivot and make them all zero
    for n in range(0, r):
        e = col[n]
        # if this element above pivot is not zero, make it zero
        if e != 0:
            x = -e
            latex, matrix = row_add(matrix, n, r, x)
            ops.append([row_add, n, r, x])
            return reduce_ref(matrix, r, c, ops)
    # go to the next expected pivot if everything above this pivot == 0
    return reduce_ref(matrix, r + 1, c + 1, ops)


def to_rref(matrix: sp.Matrix, r=0, c=0, ops=[]):
    """
    Returns the reduced row echelon form (RREF) of the given matrix.

    :param matrix: the given matrix
    :param r: the starting index of the row of the first pivot, default 0
    :param c: the starting index of the column of the first pivot, default 0
    :param ops: a list to store the row operations performed; elements are
                lists with varying lengths whose first element is always
                a reference to one of the three row operation functions and
                the subsequent elements are arguments to the row operation
                functions
    :return: the REF of the given matrix
    """
    # first obtain the row echelon form
    matrix = to_ref(matrix, r, c, ops)
    # make zero all elements above leading 1s
    return reduce_ref(matrix, r, c, ops)


def to_elementary_matrix(ops, n):
    """
    Creates an n ⨉ n elementary matrix from a list of elementary row operations.

    :param ops: a list of elementary row operations
    :param n: number of rows (and columns) of the elementary matrix; must be large
              enough to account for the row (and column) references by the elementary
              row operations without raising an IndexError
    :return: the elementary matrix
    """
    m = sp.eye(n)
    for op in ops:
        if op[0] == row_interchange:
            latex, m = row_interchange(m, op[1], op[2])
        if op[0] == row_multiply:
            latex, m = row_multiply(m, op[1], op[2])
        if op[0] == row_add:
            latex, m = row_add(m, op[1], op[2], op[3])
    return m


def get_latex_procedure(ops, m: sp.Matrix):
    """
    Returns the LaTeX representation of each application of the row operation in the operation list on
    the given matrix.
    
    :param ops: the list of row operations
    :param m: the given matrix
    :return: the LaTeX representation of each application of the row operation in the operation list on
             the given matrix
    """
    str = to_latex(m) + "\n"
    for op in ops:
        if op[0] == row_interchange:
            latex, m = row_interchange(m, op[1], op[2])
        if op[0] == row_multiply:
            latex, m = row_multiply(m, op[1], op[2])
        if op[0] == row_add:
            latex, m = row_add(m, op[1], op[2], op[3])
        str += latex + "\n" + to_latex(m) + "\n"
    return str

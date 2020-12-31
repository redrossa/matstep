import numpy as np
from pymbolic.primitives import Sum, Product, Call, Expression

from matstep.functions import Function
from matstep.stringifiers import StepStringifier


class Determinant(Function):
    """A `Determinant` function computes the determinant of the given matrix"""

    name = 'det'
    arg_count = 1
    mapper_method = 'map_matstep_det_func'

    def __call__(self, array):
        """
        Computes the determinant of array, the given matrix.

        :param array: a `numpy.ndarray` representing the matrix

        :return: An expression tree that can be simplified further into the
        value of the determinant of `array`.

        :raise TypeError: if not array is not of type `numpy.ndarray`
        :raise ValueError: if array is not square in shape
        """

        if not isinstance(array, np.ndarray):
            raise TypeError('expected numpy.ndarray, got %s instead' % str(type(array)))

        rows, cols = array.shape
        if rows != cols:
            raise ValueError('non-square matrix')
        if rows == 1:
            return array[0][0]
        if rows == 2:
            return Sum((Product((array[0][0], array[1][1])), Product((-array[0][1], array[1][0]))))

        triu = array[np.triu_indices(rows, k=1)]
        tril = array[np.tril_indices(rows, k=-1)]
        if not np.any(triu) or not np.any(tril):
            # upper or lower triangular matrix
            return Product(tuple(entry for entry in array.diagonal()))

        def _minor(arr, i, j):
            return np.delete(np.delete(arr, i, axis=0), j, axis=1)

        def _coeff_det(coeff, j):
            return Product((coeff if j % 2 == 0 else -coeff, Call(self, (_minor(array, 0, j), ))))

        coeffs = array[0]
        return Sum(tuple(_coeff_det(c, j) for j, c in enumerate(coeffs)))


class _VectorProduct(Expression):
    def __init__(self, lvec, rvec):
        self.lvec = lvec
        self.rvec = rvec

    def __getinitargs__(self):
        return self.lvec, self.rvec


class DotProduct(_VectorProduct):
    mapper_method = 'map_matstep_dot_product'

    def make_stringifier(self, originating_stringifier=None):
        return DotProductStringifier()


class DotProductStringifier(StepStringifier):
    def map_matstep_dot_product(self, expr, enclosing_prec, *args, **kwargs):
        from pymbolic.mapper.stringifier import PREC_PRODUCT
        return self.parenthesize_if_needed(
            self.format('%s · %s',
                        self.rec(expr.lvec, enclosing_prec, *args, **kwargs),
                        self.rec(expr.rvec, enclosing_prec, *args, **kwargs)),
            enclosing_prec,
            PREC_PRODUCT)


class CrossProduct(_VectorProduct):
    mapper_method = 'map_matstep_cross_product'

    def make_stringifier(self, originating_stringifier=None):
        return CrossProductStringifier()


class CrossProductStringifier(StepStringifier):
    def map_matstep_cross_product(self, expr, enclosing_prec, *args, **kwargs):
        from pymbolic.mapper.stringifier import PREC_PRODUCT
        return self.parenthesize_if_needed(
            self.format('%s ✕ %s',
                        self.rec(expr.lvec, enclosing_prec, *args, **kwargs),
                        self.rec(expr.rvec, enclosing_prec, *args, **kwargs)),
            enclosing_prec,
            PREC_PRODUCT)


class RowSwap(Expression):
    def __init__(self, i, j, mat):
        self.i = i
        self.j = j
        self.mat = mat

    def __getinitargs__(self):
        return self.i, self.j, self.mat

    mapper_method = 'map_matstep_row_swap'

    def make_stringifier(self, originating_stringifier=None):
        return RowOpStringifier()


class RowMul(Expression):
    def __init__(self, i, k, mat):
        self.i = i
        self.k = k
        self.mat = mat

    def __getinitargs__(self):
        return self.i, self.k, self.mat

    mapper_method = 'map_matstep_row_mul'

    def make_stringifier(self, originating_stringifier=None):
        return RowOpStringifier()


class RowAdd(Expression):
    def __init__(self, i, k, j, mat):
        self.i = i
        self.k = k
        self.j = j
        self.mat = mat

    def __getinitargs__(self):
        return self.i, self.k, self.j, self.mat

    mapper_method = 'map_matstep_row_add'

    def make_stringifier(self, originating_stringifier=None):
        return RowOpStringifier()


class RowOpStringifier(StepStringifier):
    def map_matstep_row_swap(self, expr, enclosing_prec, *args, **kwargs):
        return repr(expr)

    map_matstep_row_mul = map_matstep_row_swap

    map_matstep_row_add = map_matstep_row_swap

import numpy as np
from pymbolic.primitives import Sum, Product, Call, Expression

from matstep.functions import Function


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
        if lvec.shape != rvec.shape:
            raise ValueError('mismatched dimensions: %s and %s' % (str(lvec.shape), str(rvec.shape)))
        if lvec.shape[0] != 1 and lvec.shape[0] != 1:
            raise ValueError("expected '1-D' matrix, got '%d-D' instead" % lvec.ndim)

        self.lvec = lvec
        self.rvec = rvec

    def __getinitargs__(self):
        return self.lvec, self.rvec


class DotProduct(_VectorProduct):
    mapper_method = 'map_matstep_dot_product'


class CrossProduct(_VectorProduct):
    mapper_method = 'map_matstep_cross_product'


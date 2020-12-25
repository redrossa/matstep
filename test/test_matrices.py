import unittest

import numpy as np
from pymbolic.primitives import Call, Sum, Product

from matstep.matrices import Determinant
from matstep.simplifiers import StepSimplifier


class TestDeterminant(unittest.TestCase):
    """
    Tests the functionalities and properties of a `matstep.matrices
    .Determinant` instance.
    """

    def setUp(self) -> None:
        """Initializes func attribute to a `matstep.matrices.Determinant` instance"""
        self.func = Determinant()
        self.simplifier = StepSimplifier()

    def create_call_expr(self, *args):
        return Call(self.func, args)

    def test_call(self):
        """Tests a call to the determinant function as part of simplification"""

        # Test invalid argument type -> TypeError
        self.assertRaises(TypeError, lambda: self.simplifier(self.create_call_expr(1)))

        # Test non-square matrix -> ValueError
        array = np.array([[1, 2]])
        self.assertRaises(ValueError, lambda: self.simplifier(self.create_call_expr(array)))

        # Test 1-D square matrix -> first element
        array = np.array([[1]])
        expected = 1
        self.assertEqual(expected, self.simplifier(self.create_call_expr(array)))

        # Test 2-D square matrix -> [0,0] * [1,1] + -[0,1] * [1,0]
        array = np.array([[1, 2], [3, 4]])
        expected = Sum((Product((1, 4)), Product((-2, 3))))
        self.assertEqual(expected, self.simplifier(self.create_call_expr(array)))

        # Test > 2-D square matrix -> [0,0] det minor(0,0) + -[0,1] det minor(0, 1) + ... + [0, n] det minor (0, n)
        array = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        expected = Sum((Product((1, self.create_call_expr(np.array([[5, 6], [8, 9]])))),
                        Product((-2, self.create_call_expr(np.array([[4, 6], [7, 9]])))),
                        Product((3, self.create_call_expr(np.array([[4, 5], [7, 8]]))))))
        self.assertEqual(expected, self.simplifier(self.create_call_expr(array)))


if __name__ == '__main__':
    unittest.main()

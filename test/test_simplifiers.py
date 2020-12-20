import unittest

from pymbolic.primitives import Sum, Product, Quotient, BitwiseNot, Call, Variable

from matstep.simplifiers import StepSimplifier


class TestStepSimplifier(unittest.TestCase):
    """Tests the evaluation methods of `matstep.simplifiers.StepSimplifier`"""

    def setUp(self) -> None:
        """
        Initializes the simplifier attribute of this tester to a
        `matstep.simplifiers.StepSimplifier` instance.
        """

        self.simplifier = StepSimplifier()

    def test_eval_unary_expr(self):
        """
        Tests the functionality of `matstep.simplifiers.StepSimplifier
        .eval_unary_expr` using `pymbolic.primitives.BitwiseNot`.
        """

        # Test flat: [~1] -> -2
        expr = BitwiseNot(1)
        actual = self.simplifier(expr)
        expected = -2
        self.assertEqual(actual, expected)

        # Test nested: [~[~1]] -> ~ -2
        expr = BitwiseNot(BitwiseNot(1))
        actual = self.simplifier(expr)
        expected = BitwiseNot(-2)
        self.assertEqual(actual, expected)

    def test_eval_binary_expr(self):
        """
        Tests the functionality of `matstep.simplifiers.StepSimplifier
        .eval_binary_expr` using `pymbolic.primitives.Quotient`.
        """

        # Test flat: [1 / 2] -> 0.5
        expr = Quotient(1, 2)
        actual = self.simplifier(expr)
        expected = 0.5
        self.assertEqual(actual, expected)

        # Test nested left: [[1 / 2] / 2] -> 0.5 / 2
        expr = Quotient(Quotient(1, 2), 2)
        actual = self.simplifier(expr)
        expected = Quotient(0.5, 2)
        self.assertEqual(actual, expected)

        # Test nested right: [1 / [1 / 2]] -> 1 / 0.5
        expr = Quotient(1, Quotient(1, 2))
        actual = self.simplifier(expr)
        expected = Quotient(1, 0.5)
        self.assertEqual(actual, expected)

        # Test nested left right: [[1 / 2] / [1 / 2]] -> 0.5 / 0.5
        expr = Quotient(Quotient(1, 2), Quotient(1, 2))
        actual = self.simplifier(expr)
        expected = Quotient(0.5, 0.5)
        self.assertEqual(actual, expected)

    def test_eval_multichild_expr(self):
        """
        Tests the functionality of `matstep.simplifiers.StepSimplifier
        .eval_multichild_expr` using `pymbolic.primitives.Sum`.
        """

        # Test flat: [1 + 2] -> 3
        expr = Sum((1, 2))
        actual = self.simplifier(expr)
        expected = 3
        self.assertEqual(actual, expected)

        # Test flat many: [1 + 2 + 3] -> 6
        expr = Sum((1, 2, 3))
        actual = self.simplifier(expr)
        expected = 6
        self.assertEqual(actual, expected)

        # Test nested left: [[1 + 2] + 3] -> 3 + 3
        expr = Sum((Sum((1, 2)), 3))
        actual = self.simplifier(expr)
        expected = Sum((3, 3))
        self.assertEqual(actual, expected)

        # Test nested right: [1 + [2 + 3]] -> 1 + 5
        expr = Sum((1, Sum((2, 3))))
        actual = self.simplifier(expr)
        expected = Sum((1, 5))
        self.assertEqual(actual, expected)

        # Test flat left, nested right: [1 + 2 + [1 + 2]] -> 3 + 3
        expr = Sum((1, 2, Sum((1, 2))))
        actual = self.simplifier(expr)
        expected = Sum((3, 3))
        self.assertEqual(actual, expected)

        # Test flat right, nested left: [[1 + 2] + 1 + 2] -> 3 + 3
        expr = Sum((Sum((1, 2)), 1, 2))
        actual = self.simplifier(expr)
        expected = Sum((3, 3))
        self.assertEqual(actual, expected)

        # Test nested many: [[1 + 2] + [1 + 2]] -> 3 + 3
        expr = Sum((Sum((1, 2)), Sum((1, 2))))
        actual = self.simplifier(expr)
        expected = Sum((3, 3))
        self.assertEqual(actual, expected)

        # Test flat peripheral, nested middle: [1 + 2 + [3 + 4] + 1 + 2] -> 3 + 7 + 3
        expr = Sum((1, 2, Sum((3, 4)), 1, 2))
        actual = self.simplifier(expr)
        expected = Sum((3, 7, 3))
        self.assertEqual(actual, expected)

        # Test flat middle, nested peripheral: [[1 + 2] + 3 + 4 + [5 + 6]] -> 3 + 7 + 11
        expr = Sum((Sum((1, 2)), 3, 4, Sum((5, 6))))
        actual = self.simplifier(expr)
        expected = Sum((3, 7, 11))
        self.assertEqual(actual, expected)

    def test_eval_call_expr(self):
        # Test flat: f(2) -> f(2)
        expr = Call(Variable('f'), (2, ))
        actual = self.simplifier(expr)
        expected = expr
        self.assertEqual(actual, expected)

        # Test flat many: f(2, 3) -> f(2, 3)
        expr = Call(Variable('f'), (2, 3))
        actual = self.simplifier(expr)
        expected = expr
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()

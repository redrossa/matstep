import unittest

from pymbolic.primitives import Call, Sum

from matstep import StepSimplifier
from matstep.functions import Identity


class TestIdentityFunction(unittest.TestCase):
    def setUp(self) -> None:
        self.func = Identity()
        self.simplifier = StepSimplifier()

    def test_call(self):
        """Tests a call to the identity function as part of simplification"""

        # Test simplified parameter: id(1) -> 1
        expr = Call(self.func, (1, ))
        actual = self.simplifier(expr)
        expected = 1
        self.assertEqual(expected, actual)

        # Test unsimplified parameter: id(2 + 3) -> id(5)
        expr = Call(self.func, (Sum((2, 3)), ))
        actual = self.simplifier(expr)
        expected = Call(self.func, (5, ))
        self.assertEqual(expected, actual)

    def test_str(self):
        """Tests the string representation of the identity function"""

        # Test standalone str
        self.assertEqual(str(self.func), 'id')

        # Test str as part of pymbolic.primitives.Call with simplified parameter
        expr = Call(self.func, (1,))
        actual = str(expr)
        expected = 'id(1)'
        self.assertEqual(expected, actual)

        # Test str as part of pymbolic.primitives.Call with unsimplified parameter
        expr = Call(self.func, (Sum((2, 3)),))
        actual = str(expr)
        expected = 'id(2 + 3)'
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()

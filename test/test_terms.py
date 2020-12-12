import unittest

from pymbolic.primitives import Variable, Sum, Product, Quotient, Power

from matstep.core.terms import Monomial, PowerVariable


def var(name: str, power: int = 1):
    return PowerVariable(name, power)


class TestTerms(unittest.TestCase):
    def test_Monomial_init(self):
        # Test only coeff ed -> constant Monomial
        m = Monomial(0)
        self.assertTrue(m.is_zero())
        self.assertTrue(not m.variables)
        m = Monomial(1)
        self.assertTrue(m.is_constant())
        self.assertTrue(not m.variables)

        # Test coeff=0, variables=any -> zero Monomial with any variables ed discarded
        m = Monomial(0, ())
        self.assertTrue(m.is_zero())
        self.assertTrue(not m.variables)
        m = Monomial(0, var('x'))
        self.assertTrue(m.is_zero())
        self.assertTrue(not m.variables)

        # Test coeff=nonzero, variables=any -> verify
        m = Monomial(1, var('x'))
        self.assertTrue(not m.is_constant())
        self.assertEqual(m.coeff, 1)
        self.assertEqual(m.variables, (var('x'),))
        m = Monomial(2, var('x'), var('y'))
        self.assertTrue(not m.is_constant())
        self.assertEqual(m.coeff, 2)
        self.assertEqual(m.variables, (var('x'), var('y')))

    def test_from_int(self):
        from matstep.core.terms import from_int
        # Test c=0 -> zero Monomial
        m = from_int(0)
        self.assertTrue(m.is_zero())
        self.assertTrue(not m.variables)

        # Test c=nonzero -> verify
        m = from_int(1)
        self.assertTrue(m.is_constant())
        self.assertTrue(not m.variables)

    def test_from_var(self):
        from matstep.core.terms import from_var
        # Test v=any -> verify
        m = from_var(Variable('x'))
        self.assertTrue(not m.is_constant())
        self.assertEqual(m.coeff, 1)
        self.assertEqual(len(m.variables), 1)
        self.assertEqual(m.variables[0].power, 1)

    def test_Monomial_is_zero(self):
        # Test zero Monomial -> True
        m = Monomial(0)
        self.assertTrue(m.is_zero())
        self.assertTrue(m.is_constant())
        self.assertTrue(not m.variables)

        # Test nonzero Monomial -> False
        m = Monomial(1)
        self.assertFalse(m.is_zero())
        self.assertTrue(m.is_constant())
        self.assertTrue(not m.variables)

    def test_Monomial_is_one(self):
        # Test one Monomial -> True
        m = Monomial(1)
        self.assertTrue(m.is_one())
        self.assertTrue(m.is_constant())
        self.assertTrue(not m.variables)

        # Test non one Monomial -> False
        m = Monomial(0)
        self.assertFalse(m.is_one())
        self.assertTrue(m.is_constant())
        self.assertTrue(not m.variables)

    def test_Monomial_is_alike(self):
        # Test equal coeff, non like variables -> False
        a = Monomial(2)
        b = Monomial(2, var('x'))
        self.assertFalse(a.is_alike(b))

        # Test non equal coeff, like variables -> True
        a = Monomial(1, var('x'), var('y', 3))
        b = Monomial(2, var('x'), var('y', 3))
        self.assertTrue(a.is_alike(b))

        # Test equal coeff, like variables -> True
        a = Monomial(2, var('x'), var('y', 3))
        self.assertTrue(a.is_alike(b))

    def test_gcd(self):
        from matstep.core.terms import gcd

        # Test two Monomials with no coeff factor > 1 and with no variables factor -> one Monomial
        a = Monomial(2, var('x'))
        b = Monomial(3, var('a'), var('b', 2))
        f = Monomial(1)
        self.assertEqual(gcd(a, b), f)

        # Test two Monomials with coeff factor and with no variables factor -> constant Monomial
        b = Monomial(4, var('a'), var('b', 2))
        f = Monomial(2)
        self.assertEqual(gcd(a, b), f)

        # Test two Monomials with no coeff factor > 1 and with variables factor -> variables Monomial
        a = Monomial(2, var('x'))
        b = Monomial(3, var('a'), var('x', 2))
        f = Monomial(1, var('x'))
        self.assertEqual(gcd(a, b), f)

        # Test two Monomials with coeff factor and with variables factor -> verify
        a = Monomial(2, var('x'))
        b = Monomial(4, var('a'), var('x', 2))
        f = Monomial(2, var('x'))
        self.assertEqual(gcd(a, b), f)

        # Test more than two Monomials -> verify
        c = Monomial(16, var('x', 30))
        f = Monomial(2, var('x'))
        self.assertEqual(gcd(a, b, c), f)

    def test_Monomial_add(self):
        # Test two constant Monomials -> verify constant Monomial
        a = Monomial(1)
        b = Monomial(3)
        e1 = Monomial(4)
        e2 = Monomial(4)
        r1 = a + b
        r2 = b + a
        self.assertTrue(r1.is_constant())
        self.assertTrue(r2.is_constant())
        self.assertEqual(r1, e1)
        self.assertEqual(r2, e2)
        self.assertEqual(r1, r2)

        # Test two alike non-constant Monomials -> verify
        a = Monomial(1, var('x'), var('y', 3))
        b = Monomial(3, var('x'), var('y', 3))
        e1 = Monomial(4, var('x'), var('y', 3))
        e2 = Monomial(4, var('x'), var('y', 3))
        r1 = a + b
        r2 = b + a
        self.assertTrue(r1.is_alike(a))
        self.assertTrue(r1.is_alike(b))
        self.assertTrue(r2.is_alike(a))
        self.assertTrue(r2.is_alike(b))
        self.assertEqual(r1, e1)
        self.assertEqual(r2, e2)
        self.assertEqual(r1, r2)

        # Test two non-alike Monomials -> verify Sum
        b = Monomial(3, var('y', 3))
        e1 = Sum((a, b))
        e2 = Sum((b, a))
        r1 = a + b
        r2 = b + a
        self.assertEqual(r1, e1)
        self.assertEqual(r2, e2)
        self.assertNotEqual(r1, r2)

        # Test constant Monomial and int -> verify Sum
        a = Monomial(2)
        b = 3
        e1 = Sum((a, b))
        e2 = Sum((b, a))
        r1 = a + b
        r2 = b + a
        self.assertEqual(r1, e1)
        self.assertEqual(r2, e2)
        self.assertNotEqual(r1, r2)

        # Test Monomial and other Expression -> verify Sum
        b = Power(2, 2)
        e1 = Sum((a, b))
        e2 = Sum((b, a))
        r1 = a + b
        r2 = b + a
        self.assertEqual(r1, e1)
        self.assertEqual(r2, e2)
        self.assertNotEqual(r1, r2)

    def test_Monomial_sub(self):
        # Test two constant Monomials -> verify constant Monomial
        a = Monomial(1)
        b = Monomial(3)
        e1 = Monomial(-2)
        e2 = Monomial(2)
        r1 = a - b
        r2 = b - a
        self.assertTrue(r1.is_constant())
        self.assertTrue(r2.is_constant())
        self.assertEqual(r1, e1)
        self.assertEqual(r2, e2)

        # Test two alike non-constant Monomials -> verify
        a = Monomial(1, var('x'), var('y', 3))
        b = Monomial(3, var('x'), var('y', 3))
        e1 = Monomial(-2, var('x'), var('y', 3))
        e2 = Monomial(2, var('x'), var('y', 3))
        r1 = a - b
        r2 = b - a
        self.assertTrue(r1.is_alike(a))
        self.assertTrue(r1.is_alike(b))
        self.assertTrue(r2.is_alike(a))
        self.assertTrue(r2.is_alike(b))
        self.assertEqual(r1, e1)
        self.assertEqual(r2, e2)

        # Test two non-alike Monomials -> verify Sum
        b = Monomial(3, var('y', 3))
        e1 = Sum((a, -b))
        e2 = Sum((b, -a))
        r1 = a - b
        r2 = b - a
        self.assertEqual(r1, e1)
        self.assertEqual(r2, e2)
        self.assertNotEqual(r1, r2)

        # Test constant Monomial and int -> verify Sum
        a = Monomial(2)
        b = 3
        e1 = Sum((a, -b))
        e2 = Sum((b, -a))
        r1 = a - b
        r2 = b - a
        self.assertEqual(r1, e1)
        self.assertEqual(r2, e2)
        self.assertNotEqual(r1, r2)

        # Test Monomial and other Expression -> verify Sum
        b = Power(2, 2)
        e1 = Sum((a, -b))
        e2 = Sum((b, -a))
        r1 = a - b
        r2 = b - a
        self.assertEqual(r1, e1)
        self.assertEqual(r2, e2)
        self.assertNotEqual(r1, r2)

    def test_Monomial_mul(self):
        # Test two constant Monomials -> verify constant Monomial
        a = Monomial(2)
        b = Monomial(3)
        e1 = Monomial(6)
        e2 = Monomial(6)
        r1 = a * b
        r2 = b * a
        self.assertTrue(r1.is_constant())
        self.assertTrue(r2.is_constant())
        self.assertEqual(r1, e1)
        self.assertEqual(r2, e2)
        self.assertEqual(r1, r2)

        # Test two alike non-constant Monomials -> verify
        a = Monomial(2, var('x'), var('y', 3))
        b = Monomial(3, var('x'), var('y', 3))
        e1 = Monomial(6, var('x', 2), var('y', 6))
        e2 = Monomial(6, var('x', 2), var('y', 6))
        r1 = a * b
        r2 = b * a
        self.assertEqual(r1, e1)
        self.assertEqual(r2, e2)
        self.assertEqual(r1, r2)

        # Test two non-alike Monomials -> verify
        b = Monomial(3, var('y', 3))
        e1 = Monomial(6, var('x'), var('y', 6))
        e2 = Monomial(6, var('x'), var('y', 6))
        r1 = a * b
        r2 = b * a
        self.assertEqual(r1, e1)
        self.assertEqual(r2, e2)
        self.assertEqual(r1, r2)

        # Test constant Monomial and int -> verify Product
        a = Monomial(2)
        b = 3
        e1 = Product((a, b))
        e2 = Product((b, a))
        r1 = a * b
        r2 = b * a
        self.assertEqual(r1, e1)
        self.assertEqual(r2, e2)
        self.assertNotEqual(r1, r2)

        # Test Monomial and other Expression -> verify Product
        b = Power(2, 2)
        e1 = Product((a, b))
        e2 = Product((b, a))
        r1 = a * b
        r2 = b * a
        self.assertEqual(r1, e1)
        self.assertEqual(r2, e2)
        self.assertNotEqual(r1, r2)

    def test_Monomial_div(self):
        # Test two constant Monomials -> verify Monomial
        a = Monomial(4)
        b = Monomial(2)
        e1 = Monomial(2)
        e2 = Quotient(Monomial(1), Monomial(2))
        r1 = a / b
        r2 = b / a
        self.assertEqual(r1, e1)
        self.assertEqual(r2, e2)
        self.assertNotEqual(r1, r2)

        # Test two alike non-constant Monomials -> verify Monomial
        a = Monomial(4, var('x'), var('y', 3))
        b = Monomial(2, var('x'), var('y', 3))
        e1 = Monomial(2)
        e2 = Quotient(Monomial(1), Monomial(2))
        r1 = a / b
        r2 = b / a
        self.assertEqual(r1, e1)
        self.assertEqual(r2, e2)
        self.assertNotEqual(r1, r2)

        # Test two non-alike Monomials -> verify
        b = Monomial(3, var('y', 3))
        e1 = Quotient(Monomial(4, var('x')), Monomial(3))
        e2 = Quotient(Monomial(3), Monomial(4, var('x')))
        r1 = a / b
        r2 = b / a
        self.assertEqual(r1, e1)
        self.assertEqual(r2, e2)
        self.assertNotEqual(r1, r2)

        # Test constant Monomial and int -> verify Quotient
        a = Monomial(4)
        b = 2
        e1 = Quotient(a, b)
        e2 = Quotient(b, a)
        r1 = a / b
        r2 = b / a
        self.assertEqual(r1, e1)
        self.assertEqual(r2, e2)
        self.assertNotEqual(r1, r2)

        # Test Monomial and other Expression -> verify Quotient
        b = Power(2, 2)
        e1 = Quotient(a, b)
        e2 = Quotient(b, a)
        r1 = a / b
        r2 = b / a
        self.assertEqual(r1, e1)
        self.assertEqual(r2, e2)
        self.assertNotEqual(r1, r2)

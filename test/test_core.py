import unittest
import matstep.core as core


class TermAssertions:
    def assertTermAttributes(self, actual, coeff, variables, deg):
        assert actual.coeff == coeff
        assert actual.variables == variables
        assert actual.deg == deg

    def assertZeroTerm(self, actual):
        self.assertTermAttributes(actual, 0, (), -1)

    def assertConstantTerm(self, actual, coeff):
        self.assertTermAttributes(actual, coeff, (), 0)

    def assertTermEqual(self, actual, expected):
        self.assertTermAttributes(actual, expected.coeff, expected.variables, expected.deg)


class PolyAssertions:
    def assertPolyAttributes(self, actual, children, deg):
        assert actual.children == children
        assert actual.deg == deg

    def assertPolyEqual(self, actual, expected):
        self.assertPolyAttributes(actual, expected.children, expected.deg)


class CommutativeAssertions:
    def assertCommutative(self, op_func, op1, op2, assert_eq_func, assert_exp_func, *assert_exp_args):
        ladd = op_func(op1, op2)
        radd = op_func(op2, op1)
        assert_eq_func(ladd, radd)
        assert_exp_func(ladd, *assert_exp_args)
        assert_exp_func(radd, *assert_exp_args)

    def assertAdd(self, op1, op2, assert_eq_func, assert_func, *assert_args):
        self.assertCommutative(lambda a, b: a + b, op1, op2, assert_eq_func, assert_func, *assert_args)

    def assertMul(self, op1, op2, assert_eq_func, assert_func, *assert_args):
        self.assertCommutative(lambda a, b: a * b, op1, op2, assert_eq_func, assert_func, *assert_args)


class TestTerm(unittest.TestCase, TermAssertions, PolyAssertions, CommutativeAssertions):
    def setUp(self):
        self.arit_args = {
            'constterm_int':    (core.Term(1),                  1),
            'varterm_int':      (core.Term(1, (('x', 1),)),     1),
            'unlike_terms':     (core.Term(1, (('x', 2),)),     core.Term(2, (('x', 1),))),
            'like_terms':       (core.Term(1, (('x', 1),)),     core.Term(2, (('x', 1),))),
            'unlike_term_poly': (core.Term(1, (('x', 1),)),     core.Polynomial((core.Term(1, (('x', 3),)),
                                                                                 core.Term(1, (('x', 2),))))),
            'like_term_poly':   (core.Term(1, (('x', 1),)),     core.Polynomial((core.Term(1, (('x', 2),)),
                                                                                 core.Term(1, (('x', 1),))))),
        }

    def test_init(self):
        # Test -> Term(0, ())
        actual = core.Term()
        self.assertZeroTerm(actual)

        # Test 0 -> Term(0, ())
        actual = core.Term(0)
        self.assertZeroTerm(actual)

        # Test coeff != 0 -> Term(coeff, ())
        actual = core.Term(1)
        self.assertConstantTerm(actual, 1)

        # Test variables=() -> Term(0, ())
        actual = core.Term(variables=())
        self.assertZeroTerm(actual)

        # Test variables=(any) -> Term(0, ())
        actual = core.Term(variables=(('x', 1), ))
        self.assertZeroTerm(actual)

        # Test 0, variables=() -> Term(0, ())
        actual = core.Term(0, ())
        self.assertZeroTerm(actual)

        # Test 0, variables=(any) -> Term(0, ())
        actual = core.Term(0, (('x', 1), ))
        self.assertZeroTerm(actual)

        # Test coeff != 0, variables=() -> Term(coeff, ())
        actual = core.Term(1, ())
        self.assertConstantTerm(actual, 1)

        # Test coeff != 0, len(variables) == 1 -> Term(coeff, variables)
        actual = core.Term(1, (('x', 1), ))
        self.assertTermAttributes(actual, 1, (('x', 1), ), 1)

        # Test coeff != 0, len(variables) > 1, power 1 variables -> verify order of variables
        actual = core.Term(1, (('x', 1), ('a', 1), ('g', 1)))
        self.assertTermAttributes(actual, 1, (('a', 1), ('g', 1), ('x', 1)), 3)

        # Test coeff != 0, len(variables) > 1, any power variables -> verify order and sum power of variables
        actual = core.Term(1, (('x', 2), ('y', 4), ('x', 4), ('a', 4), ('y', 1)))
        self.assertTermAttributes(actual, 1, (('a', 4), ('x', 6), ('y', 5)), 15)

        # Test coeff != 0, variables with 0 power -> 0 power variables discarded
        actual = core.Term(1, (('x', 0), ))
        self.assertConstantTerm(actual, 1)

        # Test coeff != 0, variables sum power == 0 -> 0 power variables discarded
        actual = core.Term(1, (('x', 1), ('x', -1)))
        self.assertConstantTerm(actual, 1)

    def test_add(self):
        # Test constant Term + int == int + Term -> constant Term
        a, b = self.arit_args['constterm_int']
        self.assertAdd(a, b, self.assertTermEqual, self.assertConstantTerm, 2)

        # Test variable Term + int == int + Term -> Polynomial
        a, b = self.arit_args['varterm_int']
        self.assertAdd(a, b, self.assertPolyEqual, self.assertPolyAttributes, (a, core.Term(b)), 1)

        # Test unlike Term + Term == Term + Term -> Polynomial
        a, b = self.arit_args['unlike_terms']
        self.assertAdd(a, b, self.assertPolyEqual, self.assertPolyAttributes, (a, b), 2)

        # Test like Term + Term == Term + Term -> Term
        a, b = self.arit_args['like_terms']
        self.assertAdd(a, b, self.assertTermEqual, self.assertTermAttributes, 3, (('x', 1), ), 1)

        # Test unlike Term + Poly == Poly + Term -> Poly
        a, b = self.arit_args['unlike_term_poly']
        self.assertAdd(a, b,
                       self.assertPolyEqual,
                       self.assertPolyAttributes,
                       (core.Term(1, (('x', 3),)), core.Term(1, (('x', 2),)), core.Term(1, (('x', 1),))), 3)

        # Test like Term + Poly == Poly + Term -> Poly
        a, b = self.arit_args['like_term_poly']
        self.assertAdd(a, b,
                       self.assertPolyEqual,
                       self.assertPolyAttributes,
                       (core.Term(1, (('x', 2),)), core.Term(2, (('x', 1),))), 2)

    def test_mul(self):
        # Test constant Term * int == int * Term -> constant Term
        a, b = self.arit_args['constterm_int']
        self.assertMul(a, b, self.assertTermEqual, self.assertConstantTerm, 1)

        # Test variable Term * int == int * Term -> variable Term
        a, b = self.arit_args['varterm_int']
        self.assertMul(a, b, self.assertTermEqual, self.assertTermAttributes, 1, (('x', 1), ), 1)

        # Test unlike Term * Term == Term * Term -> Term
        a, b = self.arit_args['unlike_terms']
        self.assertMul(a, b, self.assertTermEqual, self.assertTermAttributes, 2, (('x', 3), ), 3)

        # Test like Term * Term == Term * Term -> Term
        a, b = self.arit_args['like_terms']
        self.assertMul(a, b, self.assertTermEqual, self.assertTermAttributes, 2, (('x', 2), ), 2)

        # Test unlike Term + Poly == Poly + Term -> Poly
        a, b = self.arit_args['unlike_term_poly']
        self.assertMul(a, b,
                       self.assertPolyEqual,
                       self.assertPolyAttributes,
                       (core.Term(1, (('x', 4),)), core.Term(1, (('x', 3),))), 4)

        # Test like Term + Poly == Poly + Term -> Poly
        a, b = self.arit_args['like_term_poly']
        self.assertMul(a, b,
                       self.assertPolyEqual,
                       self.assertPolyAttributes,
                       (core.Term(1, (('x', 3),)), core.Term(1, (('x', 2),))), 3)

    def test_lt(self):
        # Test constant Terms -> smaller coeff
        a = core.Term(0)
        b = core.Term(1)
        self.assertLess(a, b)

        # Test like Terms -> smaller coeff
        a = core.Term(1, (('x', 1), ))
        b = core.Term(2, (('x', 1), ))
        self.assertLess(a, b)

        # Test unlike Terms by powers -> smaller power
        a = core.Term(1, (('x', 1), ))
        b = core.Term(1, (('x', 2), ))
        self.assertLess(a, b)

        # Test unlike Terms by names -> larger name (alphabetically last)
        a = core.Term(1, (('x', 1), ))
        b = core.Term(1, (('y', 1), ))
        self.assertLess(b, a)

        # Test unlike Terms by names and powers -> smaller degree
        a = core.Term(1, (('x', 1), ))
        b = core.Term(1, (('y', 5), ))
        self.assertLess(a, b)

        # Test unlike multivariate and univariate Terms same degree -> larger name (alphabetically last)
        a = core.Term(1, (('x', 1), ('y', 1)))
        b = core.Term(1, (('z', 2), ))
        self.assertLess(b, a)

        # Test unlike multivariate Terms same degree -> larger name (alphabetically last)
        a = core.Term(1, (('w', 1), ('x', 1)))
        b = core.Term(1, (('y', 1), ('z', 1)))
        self.assertLess(b, a)

    def test_gt(self):
        # Test constant Terms -> larger coeff
        a = core.Term(0)
        b = core.Term(1)
        self.assertGreater(b, a)

        # Test like Terms -> larger coeff
        a = core.Term(1, (('x', 1),))
        b = core.Term(2, (('x', 1),))
        self.assertGreater(b, a)

        # Test unlike Terms by powers -> larger power
        a = core.Term(1, (('x', 1),))
        b = core.Term(1, (('x', 2),))
        self.assertGreater(b, a)

        # Test unlike Terms by names -> smaller name (alphabetically first)
        a = core.Term(1, (('x', 1),))
        b = core.Term(1, (('y', 1),))
        self.assertGreater(a, b)

        # Test unlike Terms by names and powers -> larger degree
        a = core.Term(1, (('x', 1),))
        b = core.Term(1, (('y', 5),))
        self.assertGreater(b, a)

        # Test unlike multivariate and univariate Terms same degree -> smaller name (alphabetically first)
        a = core.Term(1, (('x', 1), ('y', 1)))
        b = core.Term(1, (('z', 2),))
        self.assertGreater(a, b)

        # Test unlike multivariate Terms same degree -> smaller name (alphabetically first)
        a = core.Term(1, (('w', 1), ('x', 1)))
        b = core.Term(1, (('y', 1), ('z', 1)))
        self.assertGreater(a, b)


class TestPolynomial(unittest.TestCase, PolyAssertions, CommutativeAssertions):
    def setUp(self):
        self.terms = {
            'a':    core.Term(1, (('a', 1), )),
            'b':    core.Term(1, (('b', 1), )),
            'c':    core.Term(1, (('c', 1), )),
            'i':    core.Term(1, (('i', 1), )),
            'j':    core.Term(1, (('j', 1), )),
            'k':    core.Term(1, (('k', 1), )),
            'x2':   core.Term(1, (('x', 2), )),
            'x':    core.Term(1, (('x', 1), )),
            'y':    core.Term(1, (('y', 1), )),
            'z':    core.Term(1, (('z', 1), )),
            '1':    core.Term(1)
        }

    def test_init(self):
        # Test in order
        a = self.terms['x2']
        b = self.terms['x']
        c = self.terms['1']
        p = core.Polynomial((a, b, c))
        self.assertPolyAttributes(p, (a, b, c), 2)

        # Test order by powers (univariate)
        p = core.Polynomial((b, c, a))
        self.assertPolyAttributes(p, (a, b, c), 2)

        # Test order by names (multivariate)
        a = self.terms['a']
        b = self.terms['k']
        c = self.terms['y']
        p = core.Polynomial((b, c, a))
        self.assertPolyAttributes(p, (a, b, c), 1)

        # Test order by names and powers -> powers precede
        a = self.terms['a']
        b = self.terms['x2']
        c = self.terms['j']
        p = core.Polynomial((b, c, a))
        self.assertPolyAttributes(p, (b, a, c), 2)

        # Test some terms combinable all same powers -> names precede
        a = self.terms['a']
        b = self.terms['x']
        c = self.terms['x']
        p = core.Polynomial((b, c, a))
        self.assertPolyAttributes(p, (a, core.Term(2, (('x', 1), ))), 1)

        # Test some terms combinable varying powers -> powers precede
        a = self.terms['a']
        b = self.terms['x2']
        c = self.terms['x2']
        p = core.Polynomial((b, c, a))
        self.assertPolyAttributes(p, (core.Term(2, (('x', 2),)), a), 2)

    def test_add(self):
        # Test combinable: Poly + int == int + Poly
        a = core.Polynomial((self.terms['x'], self.terms['1']))
        b = 1
        self.assertAdd(a, b, self.assertPolyEqual, self.assertPolyAttributes, (self.terms['x'], core.Term(2)), 1)

        # Test non-combinable: Poly + int == int + Poly
        a = core.Polynomial((self.terms['x2'], self.terms['x']))
        b = 1
        self.assertAdd(a, b, self.assertPolyEqual, self.assertPolyAttributes, (*a.children, core.Term(1)), 2)

        # Test combinable: Poly + Term == Term + Poly
        a = core.Polynomial((self.terms['x'], self.terms['1']))
        b = self.terms['x']
        self.assertAdd(a, b,
                       self.assertPolyEqual,
                       self.assertPolyAttributes,
                       (core.Term(2, (('x', 1), )),
                        core.Term(1)), 1)

        # Test non-combinable: Poly + Term == Term + Poly
        a = core.Polynomial((self.terms['x'], self.terms['1']))
        b = self.terms['x2']
        self.assertAdd(a, b,
                       self.assertPolyEqual,
                       self.assertPolyAttributes,
                       (b, *a.children), 2)

        # Test combinable: Poly + Poly == Poly + Poly
        a = core.Polynomial((self.terms['x'], self.terms['1']))
        b = core.Polynomial((self.terms['x2'], self.terms['x']))
        self.assertAdd(a, b,
                       self.assertPolyEqual,
                       self.assertPolyAttributes,
                       (self.terms['x2'],
                        core.Term(2, (('x', 1), )),
                        self.terms['1']), 2)

        # Test non-combinable: Poly + Poly == Poly + Poly
        a = core.Polynomial((self.terms['x'], self.terms['1']))
        b = core.Polynomial((self.terms['x2'], self.terms['y']))
        self.assertAdd(a, b,
                       self.assertPolyEqual,
                       self.assertPolyAttributes,
                       (self.terms['x2'],
                        self.terms['x'],
                        self.terms['y'],
                        self.terms['1']), 2)

    def test_mul(self):
        # Test Poly * int == int * Poly
        a = core.Polynomial((self.terms['x2'], self.terms['x'], self.terms['1']))
        b = 2
        self.assertMul(a, b,
                       self.assertPolyEqual,
                       self.assertPolyAttributes,
                       (core.Term(2, (('x', 2), )),
                        core.Term(2, (('x', 1), )),
                        core.Term(2)), 2)

        # Test unlike: Poly * Term == Term * Poly
        a = core.Polynomial((self.terms['x2'], self.terms['x'], self.terms['1']))
        b = self.terms['a']
        self.assertMul(a, b,
                       self.assertPolyEqual,
                       self.assertPolyAttributes,
                       (core.Term(1, (('a', 1), ('x', 2))),
                        core.Term(1, (('a', 1), ('x', 1))),
                        core.Term(1, (('a', 1), ))), 3)

        # Test like: Poly * Term == Term * Poly
        a = core.Polynomial((self.terms['x2'], self.terms['x'], self.terms['1']))
        b = self.terms['x']
        self.assertMul(a, b,
                       self.assertPolyEqual,
                       self.assertPolyAttributes,
                       (core.Term(1, (('x', 3), )),
                        core.Term(1, (('x', 2), )),
                        core.Term(1, (('x', 1), ))), 3)

        # Test unlike: Poly * Poly == Poly * Poly
        a = core.Polynomial((self.terms['a'], self.terms['b']))
        b = core.Polynomial((self.terms['x'], self.terms['y']))
        self.assertMul(a, b,
                       self.assertPolyEqual,
                       self.assertPolyAttributes,
                       (core.Term(1, (('a', 1), ('x', 1))),
                        core.Term(1, (('a', 1), ('y', 1))),
                        core.Term(1, (('b', 1), ('x', 1))),
                        core.Term(1, (('b', 1), ('y', 1)))), 2)

        # Test like: Poly * Poly == Poly * Poly
        a = core.Polynomial((self.terms['x'], core.Term(1)))
        b = core.Polynomial((self.terms['x'], core.Term(2)))
        self.assertMul(a, b,
                       self.assertPolyEqual,
                       self.assertPolyAttributes,
                       (core.Term(1, (('x', 2), )),
                        core.Term(3, (('x', 1), )),
                        core.Term(2)), 2)


if __name__ == '__main__':
    unittest.main()

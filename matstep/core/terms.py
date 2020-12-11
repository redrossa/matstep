from collections import OrderedDict
from typing import Tuple, Iterable
import math

from pymbolic.geometric_algebra.mapper import StringifyMapper
from pymbolic.primitives import Variable, AlgebraicLeaf, Power


class Monomial(AlgebraicLeaf):
    def __init__(self, coeff: int, variables: Tuple[Power, ...] = None):
        self.coeff = coeff
        self.variables = () if not variables or not coeff else _simplify_variables(variables)
        self.deg = sum(var.exponent for var in self.variables)

    def __getinitargs__(self):
        return self.coeff, self.variables

    def is_zero(self):
        return self.coeff == 0

    def is_one(self):
        return self.coeff == 1 and not self.variables

    def is_constant(self):
        return self.deg == 0

    def is_alike(self, other):
        if not isinstance(other, Monomial):
            return False
        if self.deg != other.deg:
            return False
        if len(self.variables) != len(other.variables):
            return False
        for var in self.variables:
            if var not in other.variables:
                return False
        return True

    def is_equal(self, other):
        return self.coeff == other.coeff and self.variables == other.variables if isinstance(other, Monomial) else False

    def __ne__(self, other):
        return not (self == other)

    def __add__(self, other):
        other = _sanitize(other)
        return super(Monomial, self).__add__(other) if not isinstance(other, Monomial) or not self.is_alike(other) \
            else Monomial(self.coeff + other.coeff, self.variables)

    def __radd__(self, other):
        other = _sanitize(other)
        return super(Monomial, self).__radd__(other) if not isinstance(other, Monomial) or not other.is_alike(self) \
            else other + self

    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        other = _sanitize(other)
        return super(Monomial, self).__rsub__(other) if not isinstance(other, Monomial) else other - self

    def __mul__(self, other):
        other = _sanitize(other)
        return super(Monomial, self).__mul__(other) if not isinstance(other, Monomial) else \
            Monomial(self.coeff * other.coeff, self.variables + other.variables)

    def __rmul__(self, other):
        other = _sanitize(other)
        return super(Monomial, self).__rmul__(other) if not isinstance(other, Monomial) else self * other

    def __div__(self, other):
        other = _sanitize(other)
        if not isinstance(other, Monomial):
            return super(Monomial, self).__div__(other)

        if self.is_alike(other):
            if self.coeff % other.coeff == 0:
                return Monomial(self.coeff // other.coeff)
            primitive = math.gcd(self.coeff, other.coeff)
            return super(Monomial, from_int(self.coeff // primitive)).__div__(from_int(other.coeff // primitive))

        factor = gcd(self, other)
        factor_inv_vars = []
        for v in factor.variables:
            v.exponent *= -1
            factor_inv_vars.append(v)
        factor_inv_vars = tuple(factor_inv_vars)

        num = Monomial(self.coeff // factor.coeff, self.variables + factor_inv_vars)
        den = Monomial(other.coeff // factor.coeff, other.variables + factor_inv_vars)

        return num if den.is_one() else super(Monomial, num).__div__(den)
    __truediv__ = __div__

    def __rdiv__(self, other):
        other = _sanitize(other)
        return super(Monomial, self).__rdiv__(other) if not isinstance(other, Monomial) else other / self
    __rtruediv__ = __rdiv__

    def make_stringifier(self, originating_stringifier=None):
        return MonomialStringifyMapper()

    mapper_method = 'map_monomial'


class MonomialStringifyMapper(StringifyMapper):
    def map_monomial(self, expr, enclosing_prec, *args, **kwargs):
        variables = '*'.join([v.base.name if v.exponent == 1 else str(v) for v in expr.variables])
        coeff = '' if expr.coeff == 1 and len(variables) > 0 else str(expr.coeff)
        connector = '*' if len(coeff) > 0 and len(variables) > 0 else ''
        return coeff + connector + variables


def _simplify_variables(variables: Iterable[Power]) -> Tuple[Power]:
    vars_as_dict = {}
    for var in variables:  # must use for loop in case of duplicate variables
        name = var.base.name
        exp = var.exponent
        vars_as_dict[name] = exp if name not in vars_as_dict else vars_as_dict[name] + exp
    return tuple(Power(Variable(name), exp) for name, exp in OrderedDict(sorted(vars_as_dict.items())).items() if exp != 0)


def _strict_sanitize(arg):
    if isinstance(arg, int):
        return from_int(arg)
    elif isinstance(arg, Variable):
        return from_var(arg)
    elif isinstance(arg, Monomial):
        return arg
    else:
        raise TypeError("Unexpected argument type '" + str(type(arg)) + "'")


def _sanitize(arg):
    try:
        return _strict_sanitize(arg)
    except TypeError:
        return arg


def from_int(c: int) -> Monomial:
    if not isinstance(c, int):
        raise TypeError("Unexpected argument type '" + str(type(c)) + "'")
    return Monomial(c)


def from_var(v: Variable) -> Monomial:
    if not isinstance(v, Variable):
        raise TypeError("Unexpected argument type '" + str(type(v)) + "'")
    return Monomial(1, (Power(v, 1),))


def gcd(a: Monomial, b: Monomial, *args) -> Monomial:
    if len(args) > 0:
        args = [_strict_sanitize(arg) for arg in args]
        return gcd(gcd(a, b), args[0], *args[1:])
    a_dict = {p.base.name: p.exponent for p in a.variables}
    b_dict = {p.base.name: p.exponent for p in b.variables}
    smaller = a_dict if len(a_dict) < len(b_dict) else b_dict
    larger = b_dict if smaller == a_dict else a_dict
    common_vars = []
    for name in smaller:
        if name in larger:
            s_exp = smaller[name]
            l_exp = larger[name]
            exp = s_exp if s_exp < l_exp else l_exp
            common_vars.append(Power(Variable(name), exp))
    common_coeff = math.gcd(a.coeff, b.coeff)
    return Monomial(common_coeff, tuple(common_vars))

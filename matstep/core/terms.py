from typing import Tuple, Iterable, Union, NamedTuple
import math

from pymbolic.geometric_algebra.mapper import StringifyMapper
from pymbolic.primitives import Variable, Expression, Sum, Product, Quotient


class PowerVariable(NamedTuple):
    name: str
    power: int = 1

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other: 'PowerVariable') -> bool:
        return self.name == other.name

    def __ne__(self, other: 'PowerVariable') -> bool:
        return not (self == other)

    def __le__(self, other: 'PowerVariable') -> bool:
        return self.name <= other.name

    def __lt__(self, other: 'PowerVariable') -> bool:
        return self.name < other.name

    def __ge__(self, other: 'PowerVariable') -> bool:
        return self.name >= other.name

    def __gt__(self, other: 'PowerVariable') -> bool:
        return self.name > other.name

    def __bool__(self):
        return bool(self.name)

    def __str__(self):
        return '' if self.power == 0 else self.name if self.power == 1 else self.name + '**' + str(self.power)

    def __repr__(self):
        return self.__class__.__name__ + '(' + self.name + ', ' + str(self.power) + ')'


class Monomial(Expression):
    @staticmethod
    def _handle_args(*args) -> Tuple[PowerVariable]:
        if len(args) == 0:
            return ()

        if len(args) == 1 and not isinstance(args[0], PowerVariable):
            if not isinstance(args[0], Iterable):
                raise TypeError("Unexpected argument type '" + str(type(args[0])) + "'")
            return Monomial._handle_args(*args[0])

        vars_as_dict = {}
        for v in args:  # must use for loop in case of duplicate variables
            name = v.name
            power = v.power
            vars_as_dict[name] = power if name not in vars_as_dict else vars_as_dict[name] + power
        return tuple(sorted([PowerVariable(name, power) for name, power in vars_as_dict.items() if power != 0]))

    def __init__(self, coeff: int, *args: Union[Iterable[PowerVariable], PowerVariable]):
        self.coeff = coeff
        self.variables = () if not coeff else Monomial._handle_args(*args)
        self.deg = sum(var.power for var in self.variables)

    def __getinitargs__(self):
        return self.coeff, self.variables

    def is_zero(self) -> bool:
        return self.coeff == 0

    def is_one(self) -> bool:
        return self.coeff == 1 and not self.variables

    def is_constant(self) -> bool:
        return self.deg == 0

    def is_alike(self, other: 'Monomial') -> bool:
        if self.deg != other.deg:
            return False
        if len(self.variables) != len(other.variables):
            return False
        for var in self.variables:
            if var not in other.variables:
                return False
        return True

    def is_equal(self, other: 'Monomial') -> bool:
        return self.coeff == other.coeff and self.variables == other.variables

    def __neg__(self):
        return Monomial(-self.coeff, *self.variables)

    def __add__(self, other: 'Monomial') -> Union['Monomial', Sum]:
        return Sum((self, other)) if not isinstance(other, Monomial) or not self.is_alike(other) \
            else Monomial(self.coeff + other.coeff, self.variables)

    def __radd__(self, other: 'Monomial') -> Sum:
        return Sum((other, self))

    def __sub__(self, other: 'Monomial') -> Union['Monomial', Sum]:
        return self + (-other)

    def __rsub__(self, other: 'Monomial') -> Sum:
        return Sum((other, -self))

    def __mul__(self, other: 'Monomial') -> 'Monomial':
        return Product((self, other)) if not isinstance(other, Monomial) \
            else Monomial(self.coeff * other.coeff, self.variables + other.variables)

    def __rmul__(self, other: 'Monomial') -> Product:
        return Product((other, self))

    def __div__(self, other: 'Monomial') -> Union['Monomial', Quotient]:
        if not isinstance(other, Monomial):
            return Quotient(self, other)

        if self.is_alike(other):
            if self.coeff % other.coeff == 0:
                return Monomial(self.coeff // other.coeff)
            primitive = math.gcd(self.coeff, other.coeff)
            return Quotient(from_int(self.coeff // primitive), from_int(other.coeff // primitive))

        factor = gcd(self, other)
        factor_inv_vars = tuple(PowerVariable(v.name, -v.power) for v in factor.variables)

        num = Monomial(self.coeff // factor.coeff, self.variables + factor_inv_vars)
        den = Monomial(other.coeff // factor.coeff, other.variables + factor_inv_vars)

        return num if den.is_one() else Quotient(num, den)
    __truediv__ = __div__

    def __rdiv__(self, other: 'Monomial') -> Quotient:
        return Quotient(other, self)
    __rtruediv__ = __rdiv__

    def __le__(self, other: 'Monomial') -> bool:
        return self < other or self == other

    def __lt__(self, other: 'Monomial') -> bool:
        return self.deg < other.deg if self.deg != other.deg \
            else self.coeff > other.coeff if self.is_alike(other) \
            else self.variables > other.variables  # assuming Monomial implementation sorts variables lexicographically

    def __ge__(self, other: 'Monomial') -> bool:
        return self > other or self == other

    def __gt__(self, other: 'Monomial') -> bool:
        return self.deg > other.deg if self.deg != other.deg \
            else self.coeff > other.coeff if self.is_alike(other) \
            else self.variables > other.variables  # assuming Monomial implementation sorts variables lexicographically

    def make_stringifier(self, originating_stringifier=None):
        return MonomialStringifyMapper()

    mapper_method = 'map_monomial'


class MonomialStringifyMapper(StringifyMapper):
    def map_monomial(self, expr: Monomial, enclosing_prec, *args, **kwargs) -> str:
        variables = '*'.join([str(v) for v in expr.variables])
        coeff = '' if expr.coeff == 1 and len(variables) > 0 else str(expr.coeff)
        connector = '*' if len(coeff) > 0 and len(variables) > 0 else ''
        return coeff + connector + variables


def from_int(c: int) -> Monomial:
    if not isinstance(c, int):
        raise TypeError("Unexpected argument type '" + str(type(c)) + "'")
    return Monomial(c)


def from_var(v: Union[str, Variable]) -> Monomial:
    if not isinstance(v, (str, Variable)):
        raise TypeError("Unexpected argument type '" + str(type(v)) + "'")
    return Monomial(1, PowerVariable(v if isinstance(v, str) else v.name))


def gcd(a: Monomial, b: Monomial, *args: Monomial) -> Monomial:
    if len(args) > 0:
        return gcd(gcd(a, b), args[0], *args[1:])
    a_dict = {name: power for name, power in a.variables}
    b_dict = {name: power for name, power in b.variables}
    smaller = a_dict if len(a_dict) < len(b_dict) else b_dict
    larger = b_dict if smaller == a_dict else a_dict
    common_vars = []
    for name in smaller:
        if name in larger:
            s_power = smaller[name]
            l_power = larger[name]
            power = s_power if s_power < l_power else l_power
            common_vars.append(PowerVariable(name, power))
    common_coeff = math.gcd(a.coeff, b.coeff)
    return Monomial(common_coeff, common_vars)

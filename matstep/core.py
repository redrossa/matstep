from itertools import zip_longest

from sympy import ZZ
from sympy.polys.densebasic import dmp_from_dict, dmp_to_dict
from sympy.polys.factortools import dmp_factor_list

import matstep.util as util

from pymbolic.primitives import Expression, Sum

from matstep.stringifiers import MatstepStringifyMapper


class Term(Expression):
    def __init__(self, coeff=0, variables=None):
        self.coeff = coeff

        variables = () if not self.coeff or variables is None \
            else tuple(v for v in util.accumulate(variables, lambda v: v[0], lambda v: v[1]) if v[1] != 0)

        self.variables = variables
        self.deg = -1 if not self.coeff else sum(v[1] for v in self.variables)

    def __getinitargs__(self):
        return self.coeff, self.variables

    def is_zero(self):
        return self.coeff == 0

    def is_constant(self):
        return self.deg == 0

    def is_linear(self):
        return self.deg == 1

    def is_quadratic(self):
        return self.deg == 2

    def is_cubic(self):
        return self.deg == 3

    def is_alike(self, other):
        return self.variables == other.variables

    def __int__(self):
        if not self.is_constant():
            raise ValueError
        return self.coeff

    def __abs__(self):
        return Term(abs(self.coeff), self.variables)

    def __add__(self, other):
        other = termify(other)
        return NotImplemented if not isinstance(other, Term) else Polynomial((self, other))

    def __radd__(self, other):
        other = termify(other)
        return other + self
    
    def __sub__(self, other):
        return self + (-self)
    
    def __rsub__(self, other):
        return (-self) + other
    
    def __mul__(self, other):
        other = termify(other)
        return NotImplemented if not isinstance(other, Term) \
            else Term(self.coeff * other.coeff, self.variables + other.variables)
    
    def __rmul__(self, other):
        other = termify(other)
        return other * self

    def __pow__(self, power):
        try:
            power = int(power)
        except ValueError:
            pass
        return NotImplemented if not isinstance(power, int) \
            else Term(self.coeff ** power, tuple((v[0], v[1] * power) for v in self.variables))

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other

    def __lt__(self, other):
        other = termify(other)
        return NotImplemented if not isinstance(other, Term) \
            else self.deg < other.deg if self.deg != other.deg \
            else self.coeff < other.coeff if self.is_alike(other) \
            else self.variables > other.variables

    def __gt__(self, other):
        other = termify(other)
        return NotImplemented if not isinstance(other, Term) \
            else self.deg > other.deg if self.deg != other.deg \
            else self.coeff > other.coeff if self.is_alike(other) \
            else self.variables < other.variables

    def __bool__(self):
        return not self.is_zero()

    def make_stringifier(self, originating_stringifier=None):
        return MatstepStringifyMapper(originating_stringifier)

    def make_stepsimplifier(self):
        from matstep.simplifiers import StepSimplifyMapper
        return StepSimplifyMapper

    def count_pows(self, names=None):
        if names is None:
            return tuple(v[1] for v in self.variables)

        from collections import OrderedDict
        names = OrderedDict.fromkeys(names, 0)
        for name, power in self.variables:
            names[name] += power
        return tuple(names.values())

    mapper_method = 'map_matstep_term'


class Polynomial(Sum):
    @staticmethod
    def as_dict(p):
        return {t.count_pows(p.var_names): t.coeff for t in p.children}

    @staticmethod
    def as_list(p):
        return dmp_from_dict(Polynomial.as_dict(p), not p.is_univariate(), ZZ)

    @staticmethod
    def from_dict(d, names):
        terms = tuple(Term(coeff, tuple((name, power) for name, power in zip_longest(names, powers, fillvalue=0)))
                      for powers, coeff in d.items())
        return Polynomial(terms)

    @staticmethod
    def from_list(ls, names):
        return Polynomial.from_dict(dmp_to_dict(ls, type(ls[0]) == list, ZZ), names)

    def __new__(cls, terms):
        terms = combine_terms(terms)
        self = terms[0] if len(terms) == 1 else super(Polynomial, cls).__new__(cls)
        if isinstance(self, Polynomial):
            self.__init__(terms)
        return self

    def __init__(self, terms):
        if not hasattr(self, 'children'):
            from collections import OrderedDict
            super(Polynomial, self).__init__(terms)
            self.var_names = OrderedDict.fromkeys([v[0] for t in self.children for v in t.variables]).keys()
        self.deg = self.children[0].deg

    def __getinitargs__(self):
        return self.children,

    def is_univariate(self):
        return len(self.var_names) == 1

    def __add__(self, other):
        other = termify(other)
        return Polynomial((*self.children, other)) if isinstance(other, Term) \
            else Polynomial((*self.children, *other.children)) if isinstance(other, Polynomial) \
            else NotImplemented

    def __radd__(self, other):
        return self + other
    
    def __sub__(self, other):
        return self + (-other)
    
    def __rsub__(self, other):
        return (-self) + other
    
    def __mul__(self, other):
        other = termify(other)
        return Polynomial(tuple(t * other for t in self.children)) if isinstance(other, Term) \
            else Polynomial(tuple(t * s for t in self.children for s in other.children)) if isinstance(other, Polynomial) \
            else NotImplemented

    def __rmul__(self, other):
        return self * other

    def __len__(self):
        return len(self.children)

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other

    def __lt__(self, other):
        other = termify(other)
        return NotImplemented if not isinstance(other, Polynomial) \
            else self.children < other.children if len(self) == len(other) \
            else len(self) < len(other)

    def __gt__(self, other):
        other = termify(other)
        return NotImplemented if not isinstance(other, Polynomial) \
            else self.children > other.children if len(self) == len(other) \
            else len(self) > len(other)

    def make_stringifier(self, originating_stringifier=None):
        return MatstepStringifyMapper(originating_stringifier)

    def make_stepsimplifier(self):
        from matstep.simplifiers import StepSimplifyMapper
        return StepSimplifyMapper()
    
    mapper_method = 'map_matstep_polynomial'


def termify(o):
    return Term(o) if isinstance(o, int) else o


def combine_terms(terms):
    return tuple(Term(coeff, variables) for variables, coeff
                 in util.accumulate(terms, lambda t: t.variables, lambda t: t.coeff, reverse=True)
                 if coeff != 0)


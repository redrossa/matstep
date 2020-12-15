import matstep.util as util

from pymbolic.primitives import Expression, Sum, Variable

from matstep.stringifiers import MatstepStringifyMapper


class Term(Expression):
    def __init__(self, coeff=0, variables=None):
        self.coeff = coeff

        variables = () if not self.coeff or variables is None \
            else variables if len(variables) == 1 \
            else tuple(util.accumulate(variables, lambda v: v[0], lambda v: v[1]))

        self.variables = variables
        self.deg = -1 if not self.coeff \
            else self.variables[0][1] if len(variables) == 1 \
            else sum(v[1] for v in self.variables)

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

    def __abs__(self):
        return Term(abs(self.coeff), self.variables)

    def __add__(self, other):
        if isinstance(other, int):
            return self + Term(other)

        if isinstance(other, Variable):
            return self + var(other.name)

        if isinstance(other, Term):
            return Term(self.coeff + other.coeff, self.variables) if self.is_alike(other) else Polynomial((self, other))

        if isinstance(other, Polynomial):
            return Polynomial((self, *other.children))

        return super(Term, self).__add__(other)

    def __radd__(self, other):
        if isinstance(other, int):
            return Term(other) + self

        if isinstance(other, Variable):
            return var(other.name) + self
        
        return super(Term, self).__radd__(other)
    
    def __sub__(self, other):
        return self - var(other.name) if isinstance(other, Variable) else self + (-other)
    
    def __rsub__(self, other):
        return other + (-self)
    
    def __mul__(self, other):
        if isinstance(other, int):
            return self * Term(other)
        
        if isinstance(other, Variable):
            return self * var(other.name)
        
        if isinstance(other, Term):
            return Term(self.coeff * other.coeff, self.variables + other.variables)
        
        if isinstance(other, Polynomial):
            return Polynomial(tuple(self * t for t in other.children))
        
        return super(Term, self).__mul__(other)
    
    def __rmul__(self, other):
        if isinstance(other, int):
            return Term(other) * self
        
        if isinstance(other, Variable):
            return var(other.name) * self
        
        super(Term, self).__rmul__(other)

    def __pow__(self, power):
        if isinstance(power, int):
            return Term(self.coeff ** power, tuple((v[0], v[1] * power) for v in self.variables))

        return super(Term, self).__pow__(power)

    def is_equal(self, other):
        if isinstance(other, int):
            other = Term(other)

        if isinstance(other, Variable):
            other = var(other.name)

        return self.coeff == other.coeff and self.variables == other.variables

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other

    def __lt__(self, other):
        if isinstance(other, int):
            other = Term(other)

        if isinstance(other, Variable):
            other = var(other.name)

        return self.deg < other.deg if self.deg != other.deg \
            else self.coeff < other.coeff if self.is_alike(other) \
            else self.variables > other.variables

    def __gt__(self, other):
        if isinstance(other, int):
            other = Term(other)

        if isinstance(other, Variable):
            other = var(other.name)

        return self.deg > other.deg if self.deg != other.deg \
            else self.coeff > other.coeff if self.is_alike(other) \
            else self.variables < other.variables

    def __bool__(self):
        return not self.is_zero()

    def make_stringifier(self, originating_stringifier=None):
        return MatstepStringifyMapper()

    mapper_method = 'map_term'


class Polynomial(Sum):
    def __init__(self, terms):
        super(Polynomial, self).__init__(combine_terms(terms))
        # self.children = combine_terms(terms)
        self.deg = self.children[0].deg

    def __getinitargs__(self):
        return self.children,
        
    def __add__(self, other):
        if isinstance(other, int):
            return self + Term(other)

        if isinstance(other, Variable):
            return self + var(other.name)

        if isinstance(other, Term):
            tmp = tuple(t for t in combine_terms((*self.children, other)) if not t.is_zero())
            return Term() if not tmp else tmp[0] if len(tmp) == 1 else Polynomial(tmp)

        if isinstance(other, Polynomial):
            tmp = tuple(t for t in combine_terms((*self.children, *other.children)) if not t.is_zero())
            return Term() if not tmp else tmp[0] if len(tmp) == 1 else Polynomial(tmp)

        return super(Polynomial, self).__add__(other)
    
    def __radd__(self, other):
        if isinstance(other, int):
            return Term(other) + self
        
        if isinstance(other, Variable):
            return var(other.name) + self
        
        return super(Polynomial, self).__radd__(other)
    
    def __sub__(self, other):
        return self - var(other.name) if isinstance(other, Variable) else self + (-other)
    
    def __rsub__(self, other):
        return other + (-self)
    
    def __mul__(self, other):
        if isinstance(other, int):
            return self * Term(other)
        
        if isinstance(other, Variable):
            return self * var(other.name)
        
        if isinstance(other, Term):
            return Polynomial(tuple(t * other for t in self.children))
        
        if isinstance(other, Polynomial):
            return Polynomial(tuple(t * s for t in self.children for s in other.children))
        
        return super(Polynomial, self).__mul__(other)
    
    def __rmul__(self, other):
        if isinstance(other, int):
            return Term(other) * self
        
        if isinstance(other, Variable):
            return var(other.name) * self
        
        super(Polynomial, self).__rmul__(other)

    def __len__(self):
        return len(self.children)

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other

    def __lt__(self, other):
        return self.children < other.children if len(self) == len(other) else len(self) < len(other)

    def __gt__(self, other):
        return self.children > other.children if len(self) == len(other) else len(self) > len(other)

    def make_stringifier(self, originating_stringifier=None):
        return MatstepStringifyMapper(originating_stringifier)

    def make_stepsimplifier(self):
        from matstep.simplifiers import StepSimplifyMapper
        return StepSimplifyMapper()
    
    mapper_method = 'map_matstep_polynomial'


def var(name):
    return Term(1, ((name, 1), ))


def combine_terms(terms):
    return tuple(Term(coeff, variables) for variables, coeff
                 in util.accumulate(terms, lambda t: t.variables, lambda t: t.coeff, reverse=True))


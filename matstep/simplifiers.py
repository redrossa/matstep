from pymbolic.mapper import RecursiveMapper
from pymbolic.primitives import Sum, Product

from matstep.core import Term, Polynomial


class StepSimplifyMapper(RecursiveMapper):
    def map_matstep_term(self, expr):
        return expr

    def map_matstep_polynomial(self, expr):
        return expr

    def map_sum(self, expr):
        from pymbolic.primitives import Sum

        flat = flattened_sum(expr.children)

        return sum(flat.children) if all(isinstance(c, (Term, Polynomial)) for c in flat.children) \
            else Sum(tuple(c if isinstance(c, (Term, Polynomial)) else self.rec(c) for c in flat.children))

    def map_product(self, expr):
        from pymbolic.primitives import Product
        from pymbolic import flattened_product
        from functools import reduce

        def is_evaluatable(components):
            return Term in [type(c) for c in components] if len(components) == 2 \
                else all(isinstance(c, Term) for c in components)

        flat = flattened_product(expr.children)

        if is_evaluatable(flat.children):
            return reduce(lambda a, b: a * b, flat.children)

        terms = [c for c in flat.children if isinstance(c, Term)]
        prod_terms = reduce(lambda a, b: a * b, terms, Term(1))
        non_terms = [c for c in flat.children if not isinstance(c, Term)]

        # prepare to distribute Term if exists and wasn't first when passed
        if terms and prod_terms != flat.children[0]:
            return Product((prod_terms, *non_terms))

        # at this point, either all non Term children (then Polynomial distributand) or Term was first when passed

        children = [prod_terms] + non_terms if terms else non_terms

        if not isinstance(children[0], (Term, Polynomial)):
            return Product((self.rec(children[0]), *children[1:]))

        if not isinstance(children[1], Polynomial):
            return Product((children[0], self.rec(children[1]), *children[2:]))

        return Product((children[0] * children[1], *children[2:]))

    def map_foreign(self, expr, *args, **kwargs):
        return expr.make_stepsimplifier()(expr, *args, **kwargs)


def flattened_sum(components):
    from pymbolic.primitives import is_zero
    # flatten any potential sub-sums
    queue = list(components)
    done = []

    while queue:
        item = queue.pop(0)

        if is_zero(item):
            continue

        if type(item) is Sum:
            queue += item.children
        else:
            done.append(item)

    if len(done) == 0:
        return 0
    elif len(done) == 1:
        return done[0]
    else:
        return Sum(tuple(done))


def simplify_step(expr):
    try:
        return expr.make_stepsimplifier()(expr)
    except AttributeError:
        return StepSimplifyMapper()(expr)


def simplify_full(expr):
    last_step = simplify_step(expr)
    while True:
        step = simplify_step(last_step)
        if step == last_step:
            break
        last_step = step
    return step

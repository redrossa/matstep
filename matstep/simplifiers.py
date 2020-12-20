from pymbolic.mapper import RecursiveMapper
from pymbolic.primitives import Sum, Expression

from matstep.core import Term, Polynomial


class StepSimplifyMapper(RecursiveMapper):
    def map_matstep_term(self, expr):
        return expr

    def map_matstep_polynomial(self, expr):
        return expr

    def map_sum(self, expr):
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


class StepSimplifier(RecursiveMapper):
    def eval_unary_expr(self, expr, op_func, *args, **kwargs):
        expr_type = type(expr)
        op, = expr.__getinitargs__()

        try:
            result = op_func(op, *args, **kwargs)
            if result == expr:
                raise TypeError
        except TypeError:
            return expr_type(self.rec(op, *args, *kwargs))

        return result

    def eval_binary_expr(self, expr, op_func, *args, **kwargs):
        expr_type = type(expr)
        op1, op2 = expr.__getinitargs__()

        try:
            result = op_func(op1, op2, *args, **kwargs)
            if result == expr:
                raise TypeError
        except TypeError:
            return expr_type(self.rec(op1, *args, **kwargs), self.rec(op2, *args, **kwargs))

        return result

    def eval_multichild_expr(self, expr, op_func, *args, **kwargs):
        expr_type = type(expr)
        operands = expr.__getinitargs__()[0]  # it returns a tuple of its attributes (only children which is a tuple)
        last_operand = None
        result = []

        for operand in operands:
            eval_operand = self.rec(operand, *args, **kwargs)
            try:
                if isinstance(operand, Expression) or isinstance(last_operand, Expression):
                    raise TypeError
                new_operand = op_func(result.pop(), eval_operand, *args, **kwargs)
            except (TypeError, IndexError):
                new_operand = eval_operand
            result.append(new_operand)
            last_operand = operand

        return result[0] if len(result) == 1 else expr_type(tuple(result))

    def map_call(self, expr, *args, **kwargs):
        expr_type = type(expr)
        func, params = expr.__getinitargs__()
        eval_params = tuple(self.rec(p, *args, **kwargs) for p in params)

        return expr_type(func, eval_params) if any(isinstance(p, Expression) for p in eval_params) \
            else func(*eval_params)

    def map_sum(self, expr, *args, **kwargs):
        return self.eval_multichild_expr(expr, lambda a, b, *args, **kwargs: a + b, *args, **kwargs)

    def map_product(self, expr, *args, **kwargs):
        return self.eval_multichild_expr(expr, lambda a, b, *args, **kwargs: a * b, *args, **kwargs)

    def map_quotient(self, expr, *args, **kwargs):
        return self.eval_binary_expr(expr, lambda a, b, *args, **kwargs: a / b, *args, **kwargs)

    def map_floor_div(self, expr, *args, **kwargs):
        return self.eval_binary_expr(expr, lambda a, b, *args, **kwargs: a // b, *args, **kwargs)

    def map_reminder(self, expr, *args, **kwargs):
        return self.eval_binary_expr(expr, lambda a, b, *args, **kwargs: a % b, *args, **kwargs)

    def map_power(self, expr, *args, **kwargs):
        return self.eval_binary_expr(expr, lambda a, b, *args, **kwargs: a ** b, *args, **kwargs)

    def map_left_shift(self, expr, *args, **kwargs):
        return self.eval_binary_expr(expr, lambda a, b, *args, **kwargs: a << b, *args, **kwargs)

    def map_right_shift(self, expr, *args, **kwargs):
        return self.eval_binary_expr(expr, lambda a, b, *args, **kwargs: a >> b, *args, **kwargs)

    def map_bitwise_not(self, expr, *args, **kwargs):
        return self.eval_unary_expr(expr, lambda a, *args, **kwargs: ~a, *args, **kwargs)

    def map_bitwise_or(self, expr, *args, **kwargs):
        return self.eval_binary_expr(expr, lambda a, b, *args, **kwargs: a | b, *args, **kwargs)

    def map_bitwise_xor(self, expr, *args, **kwargs):
        return self.eval_binary_expr(expr, lambda a, b, *args, **kwargs: a ^ b, *args, **kwargs)

    def map_bitwise_and(self, expr, *args, **kwargs):
        return self.eval_binary_expr(expr, lambda a, b, *args, **kwargs: a & b, *args, **kwargs)

    def map_logical_not(self, expr, *args, **kwargs):
        return self.eval_unary_expr(expr, lambda a, *args, **kwargs: not a, *args, **kwargs)

    def map_logical_or(self, expr, *args, **kwargs):
        return self.eval_binary_expr(expr, lambda a, b, *args, **kwargs: a or b, *args, **kwargs)

    def map_logical_and(self, expr, *args, **kwargs):
        return self.eval_binary_expr(expr, lambda a, b, *args, **kwargs: a and b, *args, **kwargs)

    def map_foreign(self, expr, *args, **kwargs):
        return expr


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

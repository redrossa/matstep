import numpy as np
import pandas as pd
import pymbolic
import pymbolic.mapper.evaluator
import pymbolic.mapper.stringifier


class LogicalExpression(pymbolic.primitives.Expression):
    """
    Overrides logical methods of `pymbolic.primitives.Expression` for `matstep`
    logic operators.
    """

    def __inv__(self):
        return LogicalNot(self)

    __invert__ = __inv__

    def __and__(self, other):
        return LogicalAnd((self, other))

    def __or__(self, other):
        return LogicalOr((self, other))

    def __rshift__(self, other):
        return IfThen(self, other)


class Proposition(LogicalExpression, pymbolic.primitives.Variable):
    """Essentially a `pymbolic.primitives.Variable` with `matstep` compatible operations."""

    def __init__(self, name):
        super().__init__(name)


class LogicalNot(LogicalExpression, pymbolic.primitives.BitwiseNot):
    def __init__(self, child):
        super().__init__(child)


class LogicalAnd(LogicalExpression, pymbolic.primitives.BitwiseAnd):
    def __init__(self, children):
        super().__init__(children)


class LogicalOr(LogicalExpression, pymbolic.primitives.BitwiseOr):
    def __init__(self, children):
        super().__init__(children)


class IfThen(LogicalExpression):
    def __init__(self, condition, then):
        self.condition = condition
        self.then = then

    def __getinitargs__(self):
        return self.condition, self.then

    def make_stringifier(self, originating_stringifier=None):
        return IfThenStringifier(originating_stringifier)

    mapper_method = 'map_matstep_ifthen'


class IfThenStringifier(pymbolic.mapper.stringifier.StringifyMapper):
    def map_matstep_ifthen(self, expr, enclosing_prec, *args, **kwargs):
        return self.parenthesize_if_needed(
            '%s -> %s' % (
                self.rec(expr.condition, pymbolic.mapper.stringifier.PREC_LOGICAL_OR, *args, **kwargs),
                self.rec(expr.then, pymbolic.mapper.stringifier.PREC_LOGICAL_OR, *args, **kwargs)
            ),
            enclosing_prec,
            pymbolic.mapper.stringifier.PREC_IF
        )


class LogicalSplitter(pymbolic.mapper.RecursiveMapper):
    """
    A LogicalSplitter recursively splits a logical expression tree into its component expressions.

    >>> p, q, r = Proposition('p'), Proposition('q'), Proposition('r')
    >>> e = p & q | r
    >>> LogicalSplitter()(e)
    [LogicalOr((LogicalAnd((Proposition('p'), Proposition('q'))), Proposition('r'))),
    ... LogicalAnd((Proposition('p'), Proposition('q'))), Proposition('p'), Proposition('q'), Proposition('r')]
    """

    def map_variable(self, expr, *args, **kwargs):
        return [expr]

    def map_bitwise_and(self, expr, *args, **kwargs):
        return [expr, *[it for c in expr.children for it in self.rec(c, *args, **kwargs)]]

    map_bitwise_or = map_bitwise_and

    def map_bitwise_not(self, expr, *args, **kwargs):
        return [expr, *self.rec(expr.child, *args, **kwargs)]

    def map_matstep_ifthen(self, expr, *args, **kwargs):
        return [expr, *self.rec(expr.condition, *args, **kwargs), *self.rec(expr.then, *args, **kwargs)]


p, q, r = Proposition('p'), Proposition('q'), Proposition('r')
e = p & q | r
print(LogicalSplitter()(e))


class LogicalEvaluator(pymbolic.mapper.evaluator.EvaluationMapper):
    """Evaluator for logical operators."""

    def map_bitwise_not(self, expr):
        return 1 if not self.rec(expr.child) else 0

    def map_bitwise_and(self, expr):
        return 1 if super(LogicalEvaluator, self).map_bitwise_and(expr) else 0

    def map_bitwise_or(self, expr):
        return 1 if super(LogicalEvaluator, self).map_bitwise_or(expr) else 0

    def map_matstep_ifthen(self, expr):
        return int(not (self.rec(expr.condition) and not self.rec(expr.then)))


def combination(n):
    """Returns a combination of 1 and 0 given `n` parameters."""

    return np.array([[int(c) for c in [*('{0:0' + str(n) + 'b}').format(i)]] for i in range(2**n)])


def tabulate(expr):
    """
    Returns a `pandas.DataFrame` whose headers are the component expressions of the
    given `expr` including the `expr` itself and whose data are the results of evaluating
    the column's component expression for each combination of the parameters in `expr`.
    """

    def contextualize(props, vals):
        return dict(zip([p.name for p in props], vals))

    def filter_exprs(split_expr):
        return [*reversed([*filter(lambda it: not isinstance(it, Proposition), split_expr)])]

    def filter_props(split_expr):
        return sorted([*set(filter(lambda it: isinstance(it, Proposition), split_expr))])

    split_expr = LogicalSplitter()(expr)
    exprs = filter_exprs(split_expr)
    props = filter_props(split_expr)
    comb = combination(len(props))
    evaluator = LogicalEvaluator()
    truths = []

    for vals in comb:
        evaluator.context = contextualize(props, vals)
        truths.append((vals.tolist() + [evaluator(e) for e in exprs]))

    columns = [*props, *exprs]
    table = pd.DataFrame(truths, columns=columns)

    return table


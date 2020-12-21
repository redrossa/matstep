import pymbolic.mapper.stringifier


class Function(pymbolic.primitives.FunctionSymbol):
    """
    The base class for a step-by-step simplifiable function.

    Override `__call__` to accept any number of positional
    parameters. Expect the parameters to be simplified i.e.
    not an instance of `pymbolic.primitives.Expression`
    otherwise the function will never be called by the
    step simplifier. It may freely return an instance of
    `pymbolic.primitives.Expression`, which can be further
    simplified by the step simplifier, or a non-pymbolic
    object.

    May optionally have a `name` attribute, which is what the
    stringifier will represent for an instance of this function.

    May optionally have an `arg_count` attribute, which will
    allow `Call` to check the number of arguments.
    """

    mapper_method = 'map_function'

    def make_stringifier(self, originating_stringifier=None):
        return FunctionStringifyMapper(originating_stringifier)


class Identity(Function):
    """An `Identity` function simply returns the given parameter"""

    name = 'id'
    arg_count = 1
    mapper_method = 'map_matstep_id_func'

    def __call__(self, val):
        return val


class SquareRoot(Function):
    """A `SquareRoot` function returns given parameter to the half power"""

    name = 'sqrt'
    arg_count = 1
    mapper_method = 'map_matstep_sqrt_func'

    def __call__(self, val):
        return val ** 0.5


class Root(Function):
    """A `Root` function returns the base to the inverse of nth power"""

    name = 'root'
    arg_count = 2
    mapper_method = 'map_matstep_root_func'

    def __call__(self, base, n):
        return base ** (1 / n)


class FunctionStringifyMapper(pymbolic.mapper.stringifier.StringifyMapper):
    """A mapper to represent a `Function` instance as a string."""

    def map_function(self, expr, enclosing_prec, *args, **kwargs):
        try:
            return expr.name
        except AttributeError:
            return expr.__class__.__name__

    def handle_unsupported_expression(self, expr, enclosing_prec, *args, **kwargs):
        return self.map_function(expr, enclosing_prec, *args, **kwargs) if isinstance(expr, Function) \
            else super(FunctionStringifyMapper, self).handle_unsupported_expression()

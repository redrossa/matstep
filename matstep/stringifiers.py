from pymbolic.geometric_algebra.mapper import StringifyMapper


class StepStringifier(StringifyMapper):
    """
    An subclass of `pymbolic.mapper.stringifier.StringifyMapper` that
    accepts foreign objects to accommodate for the ability of `StepSimplifier`
    to work with them without exceptions.

    Use a `StepStringifier` instance to safely get the string representation
    of the returned value of a call to a `StepSimplifier`.
    """

    def map_foreign(self, expr, *args, **kwargs):
        try:
            return super(StepStringifier, self).map_foreign(expr, *args, **kwargs)
        except ValueError:
            return str(expr)
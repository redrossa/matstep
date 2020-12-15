from pymbolic.mapper.stringifier import StringifyMapper, PREC_SUM


class MatstepStringifyMapper(StringifyMapper):
    def map_matstep_term(self, expr, enclosing_prec, *args, **kwargs):
        variables = '*'.join([v[0] + ('' if v[1] == 1 else '**' + str(v[1])) for v in expr.variables])
        coeff = '' if expr.coeff == 1 and len(variables) > 0 else str(expr.coeff)
        connector = '*' if len(coeff) > 0 and len(variables) > 0 else ''
        return coeff + connector + variables

    def map_matstep_polynomial(self, expr, enclosing_prec, *args, **kwargs):
        return self.parenthesize_if_needed(
            '%s' % expr.children[0] +
            ''.join([(' - ' if c.coeff < 0 else ' + ') + str(abs(c)) for c in expr.children[1:]]),
            enclosing_prec,
            PREC_SUM
        )
        # return self.map_sum(expr, enclosing_prec, *args, **kwargs)

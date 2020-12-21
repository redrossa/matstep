from pymbolic.mapper import RecursiveMapper
from pymbolic.primitives import Expression


class StepSimplifier(RecursiveMapper):
    """
    A step-by-step simplifier for expressions constructed from
    `pymbolic.primitives.Expression` instances. Non-pymbolic
    objects are operands of the expression tree therefore at
    the most simplied form, an expression returns a non-pymbolic
    object. The non-pymbolic operands of an expression should
    overload the necessary Python operators.
    """

    def eval_unary_expr(self, expr, op_func, *args, **kwargs):
        """
        A helper method for evaluating single-operand `pymbolic
        .primitives.Expression` instances.

        :param expr: the single-operand `pymbolic.primitives.
        Expression` instance

        :param op_func: the corresponding operation associated
        with `expr`

        :return: an evaluated, non-pymbolic object as a result
        of applying `op_func` to the operand of `expr` if the
        operand can not be simplified further otherwise a
        pymbolic object of type `type(expr)` with a simplified
        operand
        """

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
        """
        A helper method for evaluating double-operand `pymbolic
        .primitives.Expression` instances.

        :param expr: the double-operand `pymbolic.primitives.
        Expression` instance

        :param op_func: the corresponding operation associated
        with `expr`

        :return: an evaluated, non-pymbolic object as a result
        of applying `op_func` to the operands of `expr` together
        if the any of the operands can not be simplified further
        otherwise a pymbolic object of type `type(expr)` with
        the simplified operands
        """

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
        """
        A helper method for evaluating multi-operand `pymbolic
        .primitives.Expression` instances.

        The multi-operand pymbolic expression follows the convention
        of using a single tuple to store the operands, an important
        difference when creating a new instance of the given expression
        type.

        :param expr: the multi-operand `pymbolic.primitives.
        Expression` instance

        :param op_func: the corresponding operation associated
        with `expr`

        :return: an evaluated, non-pymbolic object as a result
        of applying `op_func` to the operands of `expr` together
        if the any of the operands can not be simplified further
        otherwise a pymbolic object of type `type(expr)` with
        the simplified operands
        """

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
        """
        Simplifies the given `pymbolic.primitives.Call` instance.

        The function operand will not be called until all the parameter
        operands are simplified.
        """

        expr_type = type(expr)
        func, params = expr.__getinitargs__()
        eval_params = tuple(self.rec(p, *args, **kwargs) for p in params)

        return expr_type(func, eval_params) if any(isinstance(p, Expression) for p in params) \
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

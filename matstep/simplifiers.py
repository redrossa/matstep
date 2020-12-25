import numpy as np
from pymbolic.mapper import RecursiveMapper
from pymbolic.primitives import Expression, Sum


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

        Takes the only child attribute of the given unary `pymbolic
        .primitives.Expression` instance and passes it to the
        given op_func and returns the result.

        :param expr: the single-operand `pymbolic.primitives.
        Expression` instance

        :param op_func: at least a single-argument function
        corresponding to the operation associated with `expr`

        :return: an evaluated, non-pymbolic object as a result
        of applying `op_func` to the operand of `expr` if the
        operand can not be simplified further otherwise a
        pymbolic object of type `type(expr)` with a simplified
        operand
        """

        expr_type = type(expr)
        op, = expr.__getinitargs__()
        result = op_func(op, *args, **kwargs)

        return result if result != expr else expr_type(self.rec(op, *args, *kwargs))

    def eval_binary_expr(self, expr, op_func, *args, **kwargs):
        """
        A helper method for evaluating double-operand `pymbolic
        .primitives.Expression` instances.

        Takes the two children attributes of the given binary
        `pymbolic.primitives.Expression` instance and passes them
        to the given op_func and returns the result.

        :param expr: the double-operand `pymbolic.primitives.
        Expression` instance

        :param op_func: at least a double-argument function
        corresponding to the operation associated with `expr`

        :return: an evaluated, non-pymbolic object as a result
        of applying `op_func` to the two operands of `expr` together
        if the any of the operands can not be simplified further
        otherwise a pymbolic object of type `type(expr)` with
        the simplified operands
        """

        expr_type = type(expr)
        op1, op2 = expr.__getinitargs__()
        result = op_func(op1, op2, *args, **kwargs)

        return result if result != expr else expr_type(self.rec(op1, *args, **kwargs), self.rec(op2, *args, **kwargs))

    def eval_multichild_expr(self, expr, op_func, *args, **kwargs):
        """
        A helper method for evaluating multi-operand `pymbolic
        .primitives.Expression` instances.

        Takes the tuple children attribute of the given binary `pymbolic
        .primitives.Expression` instance and apply a reduction operation
        on the tuple elements based on the given function.

        The multi-operand pymbolic expression follows the convention
        of using a single tuple to store the operands, an important
        difference when creating a new instance of the given expression
        type.

        :param expr: the multi-operand `pymbolic.primitives.
        Expression` instance

        :param op_func: a double-argument function corresponding
        to the operation associated with `expr`

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
            if isinstance(operand, Expression) or isinstance(last_operand, Expression) or not result:
                new_operand = eval_operand
            else:
                new_operand = op_func(result.pop(), eval_operand, *args, **kwargs)
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

    def map_constant(self, expr, *args, **kwargs):
        return expr

    def map_numpy_array(self, expr, *args, **kwargs):
        return np.vectorize(self.rec)(expr, *args, **kwargs)

    def map_foreign(self, expr, *args, **kwargs):
        try:
            return super(StepSimplifier, self).map_foreign(expr, *args, **kwargs)
        except ValueError:
            return expr


class MatrixSimplifier(StepSimplifier):
    def map_sum(self, expr, *args, **kwargs):
        def mat_add(mat1, mat2):
            if not isinstance(mat1, np.ndarray) or not isinstance(mat2, np.ndarray):
                raise TypeError("Expected types 'numpy.ndarray', got %s and %s instead"
                                % (str(type(mat1)), str(type(mat2))))
            if mat1.shape != mat2.shape:
                raise ValueError('mismatched dimensions %s and %s' % (str(mat1.shape), str(mat2.shape)))

            return np.array([[Sum((el1, el2)) for el1, el2 in zip(row1, row2)] for row1, row2 in zip(mat1, mat2)])

        try:
            result = self.eval_multichild_expr(expr, mat_add, *args, **kwargs)
        except (TypeError, ValueError):
            result = super(MatrixSimplifier, self).map_sum(expr, *args, **kwargs)

        return result



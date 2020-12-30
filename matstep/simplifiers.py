import numpy as np
from pymbolic.mapper import RecursiveMapper
from pymbolic.primitives import Expression, Sum, Product, Power

from matstep.equalizer import equals


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

        return result if not equals(result, expr) \
            else expr_type(self.rec(op, *args, *kwargs))

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

        return result if not equals(result, expr) \
            else expr_type(self.rec(op1, *args, **kwargs), self.rec(op2, *args, **kwargs))

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

    def next_step(self, expr, *args, **kwargs):
        """
        Returns the next step in the simplification of `expr`.
        Equivalent to calling this instance directly.
        """

        return self.rec(expr, *args, **kwargs)

    def final_step(self, expr, *args, **kwargs):
        """Returns the most simplified step in the simplification of `expr`."""

        return self.all_steps(expr, *args, **kwargs)[-1]

    def all_steps(self, expr, *args, **kwargs):
        """
        Returns a list of steps in the simplification of `expr` starting from
        `expr` all the way to the most simplified step.
        """

        curr = self.next_step(expr, *args, **kwargs)
        steps = [expr]

        while not equals(curr, expr):
            expr = curr
            curr = self.next_step(expr)
            steps.append(expr)

        return steps


class MatrixSimplifier(StepSimplifier):
    """
    A simplifier for more detailed steps on expressions involving matrices.
    This simplifier yields the operations done on each element of the resulting
    matrix. For example, a summation of two matrices results in the following:

    >>> import numpy as np
    >>> from pymbolic.primitives import Sum
    >>> from matstep.simplifiers import MatrixSimplifier
    >>> A = np.array([[1, 2],
    ...               [1, 1]])
    >>> B = np.array([[1, 0],
    ...               [0, 1]])
    >>> MatrixSimplifier()(Sum((A, B)))
    array([[Sum((1, 1)), Sum((2, 0))],
           [Sum((1, 0)), Sum((1, 1))]])

    A `matstep.simplifiers.StepSimplifier` may suffice if expression steps
    inside matrices are not desirable. The above example would instead directly
    yield the `numpy.ndarray` whose elements are sums of the corresponding `int`
    elements of `A` and `B` since `numpy.ndarray` overloads `__add__`.
    """

    def map_sum(self, expr, *args, **kwargs):
        def mat_add(op1, op2):
            if not isinstance(op1, np.ndarray) or not isinstance(op2, np.ndarray):
                raise TypeError("Expected types 'numpy.ndarray', got %s and %s instead"
                                % (str(type(op1)), str(type(op2))))
            if op1.shape != op2.shape:
                raise ValueError('mismatched dimensions %s and %s' % (str(op1.shape), str(op2.shape)))

            return np.array([[Sum((el1, el2)) for el1, el2 in zip(row1, row2)]
                             for row1, row2 in zip(op1, op2)])

        try:
            result = self.eval_multichild_expr(expr, mat_add, *args, **kwargs)
        except TypeError:
            result = super(MatrixSimplifier, self).map_sum(expr, *args, **kwargs)

        return result

    def map_product(self, expr, *args, **kwargs):
        def mat_mul(op1, op2):
            if not isinstance(op1, np.ndarray) or not isinstance(op2, np.ndarray):
                return op1 * op2

            if op1.shape[1] != op2.shape[0]:
                # mat1 cols must equal mat2 rows
                raise ValueError('mismatched dimensions %s and %s' % (str(op1.shape), str(op2.shape)))

            return np.array([[Product((el1, el2)) for el1, el2 in zip(row1, row2)]
                             for row1, row2 in zip(op1.transpose(), op2)])

        return self.eval_multichild_expr(expr, mat_mul, *args, **kwargs)

    def map_power(self, expr, *args, **kwargs):
        def mat_pow(base, exp):
            if not isinstance(base, np.ndarray) or exp < -1:
                return base ** exp

            rows, cols = base.shape
            triu = base[np.triu_indices(rows, k=1)]
            tril = base[np.tril_indices(rows, k=-1)]

            return np.diag([Power(el, exp) for el in base.diagonal()]) if not np.any(triu) and not np.any(tril) \
                else np.array([[Power(el, exp) for el in row] for row in base])

        return self.eval_binary_expr(expr, mat_pow, *args, **kwargs)

    def map_matstep_dot_product(self, expr, *args, **kwargs):
        def vec_dot(lvec, rvec):
            if lvec.shape != rvec.shape:
                raise ValueError('mismatched dimensions: %s and %s' % (str(lvec.shape), str(rvec.shape)))
            if lvec.shape[0] != 1 and lvec.shape[0] != 1:
                raise ValueError("expected 1-D matrix, got %s instead" % str(lvec.shape))

            lvec, rvec = lvec.flatten(), rvec.flatten()
            return Sum(tuple(Product((el1, el2)) for el1, el2 in zip(lvec, rvec)))

        return self.eval_binary_expr(expr, vec_dot, *args, **kwargs)

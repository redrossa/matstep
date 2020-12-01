from linpy.util import eq


class Solver:
    def __init__(self, *args, **kwargs):
        exp = None
        rel = None
        sol = None
        is_exp = False

        if len(args) == 1:
            exp = args[0]
            is_exp = True
        elif len(args) == 2:
            exp = args[0]
            rel = eq
            sol = args[2]
        elif len(args) == 3:
            exp = args[0]
            rel = args[1]
            sol = args[2]

        if exp is None:
            raise ValueError('Invalid argument')

        self.exp = exp
        self.rel = rel
        self.sol = sol
        self.is_exp = is_exp


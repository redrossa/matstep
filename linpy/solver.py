class Relation:
    def __init__(self, *args, **kwargs):
        pass


class Solver:
    def __init__(self, *args, **kwargs):
        initial_exp = None
        relation = None
        final_exp = None
        is_exp = False

        if len(args) == 1:
            initial_exp = args[0]
            is_exp = True
        elif len(args) == 3:
            initial_exp = args[0]
            relation = args[1]
            final_exp = args[2]

        if initial_exp is None:
            raise ValueError('Invalid argument')

        self.initial_exp = initial_exp
        self.relation = relation
        self.final_exp = final_exp
        self.is_exp = is_exp


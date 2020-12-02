class Relation:
    def __init__(self, ascii: str, latex: str):
        self.ascii = ascii
        self.latex = latex


eq = Relation('==', '==')
neq = Relation('!=', r'\neq')
gt = Relation('>', '>')
lt = Relation('<', '<')
geq = Relation('>=', r'\geq')
leq = Relation('<=', r'\leq')


class Solver:
    def __init__(self, *args, **kwargs):
        self.exp = args[0]
        self.rel = args[1]
        self.sol = args[2]

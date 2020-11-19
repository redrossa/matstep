from sympy import Matrix


class Solution:
    def __init__(self, initial: Matrix, final: Matrix):
        self._initial = initial
        self._final = final

    @property
    def initial(self):
        return self._initial

    @property
    def final(self):
        return self._final


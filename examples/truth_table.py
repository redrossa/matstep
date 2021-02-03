"""
Demonstrates the creation of logical expressions and truth tables.

`matstep.logic.Proposition` represents the 'variable' in a logical
expression. The built-in logical operators that can be performed on
a `Proposition` are:
  not (~p)
  and (p & q)
  inclusive or (p | q)
  implication (p >> q) !!! This must be surrounded by parentheses as
  necessary since python (>>) operator has a higher precedence than
  any of the above.
"""

from matstep.logic import Proposition


p, q, r = Proposition('p'), Proposition('q'), Proposition('r')
e = (p | ~(q & ~r)) >> (p & r)

print(e.tabulate().to_markdown(index=False))

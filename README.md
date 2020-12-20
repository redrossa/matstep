# Matstep (linpy)

Matstep (linpy) is an extensible step-by-step symbolic computation library. This project is currently under construction. There are two packages: `matstep` and `linpy`. The `matstep` package is the main package, where it will contain the distribution of this library. The `linpy` package contains some matrix computation methods, but will no longer be updated and will be removed in the future. This repository will change its name to matstep.

### Project updates:

Goals currently being worked on:

- A function class that gives the ability for defining (and getting) an output expression based on an input expression.

Near future goals to implement:
 - A matrix class that represents an array of expressions. A matrix object will probably, like a term, have some degree of basis of expressions.
 - New expression operations for matrices.

Goals implemented:
- A step-by-step expression simplifier that can evaluate any operable objects (i.e. those that overload Python operators)
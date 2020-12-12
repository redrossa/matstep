# Matstep (linpy)

Matstep (linpy) is an extensible step-by-step symbolic computation library. This project is currently under construction. There are two packages: `matstep` and `linpy`. The `matstep` package is the main package, where it will contain the distribution of this library. The `linpy` package contains some matrix computation methods, but will no longer be updated and will be removed in the future. This repository will change its name to matstep.

### Project updates:

Goals currently being worked on:
 - A step-by-step evaluator/simplifier for monomial operations.

Near future goals to implement:
 - A matrix class that represents an array of monomials or expressions of monomials. A matrix object will probably, like a monomial, have some degree of basis of expressions.
 - New expression operations for matrices.
 - A function class that gives the ability for defining (and getting) an output expression based on an input expression.

Goals implemented:
 - A monomial class that represents in algebra a product of power of variables with coefficients. The monomial object must be able to be compared with each other based on their degree and coefficients. A monomial will be used as the basis of expressions.
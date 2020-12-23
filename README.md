# Matstep (linpy)

Matstep (linpy) is an extensible step-by-step symbolic computation library. This project is currently under construction. There are two packages: `matstep` and `linpy`. The `matstep` package is the main package, where it will contain the distribution of this library. The `linpy` package contains some matrix computation methods, but will no longer be updated and will be removed in the future. This repository will change its name to matstep.

### Project updates:

Goals currently being worked on:
- ~~A matrix class that represents an array of expressions. A matrix object will probably, like a term, have some degree of basis of expressions.~~
- Matstep will instead provide matrix computation support using `numpy.ndarray`.
- Matrix expression operations for `numpy.ndarray`:
    - Basic operations: matrix addition and scalar and matrix multiplications
    - Determinant
    - Row echelon form
    - Reduced row echelon form
    - Polynomial characteristic
    - Upper/lower trianglular form
    - Diagonalization
- Vector expression operations:
    - Dot product (either just a 1-D matrix multiplication or a separate implementation)
    - Cross product

Goals implemented:
- A step-by-step expression simplifier that can evaluate any operable objects (i.e. those that overload Python operators).
- A function class that gives the ability for defining (and getting) an output expression based on an input expression.
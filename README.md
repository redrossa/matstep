# Matstep

Matstep is an extensible step-by-step computation library. The library utilizes [pymbolic](https://github.com/inducer/pymbolic)'s expression tree to simplify expressions one step at a time. Initially brought up to find a way to quickly automate printing of matrix computations, matstep supports the simplification of numpy arrays. In addition, the step simplifier is designed to be versatile allowing it to compute any expressions of objects that overload the necessary Python operators.

This project is currently under construction!

### Project updates:

Goals currently being worked on:
- Matstep will instead provide matrix computation support using `numpy.ndarray`.
- Matrix expression operations for `numpy.ndarray`:
    - Row echelon form
    - Upper/lower trianglular form
    - Diagonalization
  
Goals to implement in the future:
- Cross-representation interoperability functions for LaTeX and ASCIIMath
- Calculus module (maybe)

Goals implemented:
- Backbone for logical expressions
- Truth tabulator for logical expressions
- Reduced row echelon form step-by-step simplifier for matrices
- Dot product
- Cross product
- Determinant function
- Basic matrix operations: addition, multiplication, exponential
- A function class that gives the ability for defining (and getting) an output expression based on an input expression
- A step-by-step expression simplifier that can evaluate any operable objects (i.e. those that overload Python operators)

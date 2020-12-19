# Matstep (linpy)

Matstep (linpy) is an extensible step-by-step symbolic computation library. This project is currently under construction. There are two packages: `matstep` and `linpy`. The `matstep` package is the main package, where it will contain the distribution of this library. The `linpy` package contains some matrix computation methods, but will no longer be updated and will be removed in the future. This repository will change its name to matstep.

### Project updates:

Goals currently being worked on:

- Change of goals: A general step-by-step mapper able to evaluate expressions of any operable objects (i.e. those that overload Python operators). Although this project will continue to provide for custom types especially for matrices and functions, they will not be the core of this library. Instead, the core functionality of this library will stick to solely providing a step-by-step expression evaluation mapper. 
- ~~Division operation for terms and polynomials.~~
- ~~Imaginary number class.~~

Near future goals to implement:
 - A matrix class that represents an array of expressions. A matrix object will probably, like a term, have some degree of basis of expressions.
 - New expression operations for matrices.
 - A function class that gives the ability for defining (and getting) an output expression based on an input expression.

Goals implemented:
 - A term class that represents in algebra a product of power of variables with coefficients. A term object must be able to be compared with another based on their degree and coefficients. A term will be used as the basis of expressions.
- A polynomial class, a subclass of `pymbolic.primitives.Sum` that manages only sums of terms. Useful for grouping together unlike terms, sorting them out, while also providing automatic combination of like terms. Together with the term class, it is a basis of expressions of matstep.
- A step-by-step simplifier for term and polynomial addition, subtraction and multiplication.
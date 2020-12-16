def simplify_step(expr):
    try:
        return expr.make_stepsimplifier()(expr)
    except AttributeError:
        from matstep.simplifiers import StepSimplifyMapper
        return StepSimplifyMapper()(expr)


def simplify_full(expr):
    last_step = simplify_step(expr)
    while True:
        step = simplify_step(last_step)
        if step == last_step:
            break
        last_step = step
    return step


def var(name):
    from matstep.core import Term
    return Term(1, ((name, 1), ))

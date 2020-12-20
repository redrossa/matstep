from matstep.simplifiers import StepSimplifier


def simplify_next(expr, simplifier=None):
    simplifier = StepSimplifier() if not simplifier else simplifier
    return simplifier(expr)


def simplify_full(expr, simplifier=None):
    simplifier = StepSimplifier() if not simplifier else simplifier
    last_step = simplifier(expr)

    while True:
        curr_step = simplifier(last_step)
        if curr_step == last_step:
            break
        last_step = curr_step

    return curr_step

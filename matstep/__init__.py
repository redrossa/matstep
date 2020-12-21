import matstep.simplifiers
import matstep.functions


_simplifier = simplifiers.StepSimplifier()


def simplify_next(expr, simplifier=None):
    simplifier = _simplifier if not simplifier else simplifier
    return simplifier(expr)


def simplify_full(expr, simplifier=None):
    simplifier = _simplifier if not simplifier else simplifier
    last_step = simplifier(expr)

    while True:
        curr_step = simplifier(last_step)
        try:
            if curr_step == last_step:
                break
        except Exception:
            pass
        last_step = curr_step

    return curr_step


def get_steps(expr, simplifier=None):
    simplifier = _simplifier if not simplifier else simplifier
    steps = [expr]
    last_step = simplifier(expr)

    while True:
        curr_step = simplifier(last_step)
        try:
            if curr_step == last_step:
                break
        except Exception:
            pass
        steps.append(last_step)
        last_step = curr_step
    steps.append(curr_step)

    return steps

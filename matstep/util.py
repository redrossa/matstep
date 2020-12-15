import itertools


def accumulate(iterable, key_func, item_func, reverse=False):
    it = itertools.groupby(sorted(iterable, reverse=reverse), key_func)
    for key, subiter in it:
        yield key, sum(item_func(item) for item in subiter)

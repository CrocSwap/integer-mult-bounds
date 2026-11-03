"""Check the closed divisor formula against raw integer coefficients."""
from math import comb, gcd

from census import check
from law import order_bound, root_target, unit_repeat_root
from oracle import literal_matrix, matrix_target, primitive_period


def compare_divisors():
    cases = order_tests = unit_tests = 0
    for h in range(2, 17):
        for m in (*range(2, 97), 125, 175, 250, 350, 360, 900):
            divisors = [d for d in range(1, m+1) if m % d == 0]
            raw = {}
            for d in divisors:
                n = m//d
                pure = [(comb(d, j) * pow(n, j, m)) % m for j in range(2, h+1)]
                raw[d] = (any(pure[:-1]), pure[-1])
            for c in range(m):
                bound = order_bound(h, m, c)
                nontrivial = []
                for d in divisors:
                    blocked, offset = raw[d]
                    allowed = not blocked and (c - offset) % d == 0
                    check(allowed == (bound % d == 0), "closed divisor arithmetic")
                    check(allowed == (root_target(h, m//d, d, c) is not None), "root eligibility")
                    if allowed and d > 1:
                        nontrivial.append((d, m//d, ((c-offset)//d) % (m//d)))
                    order_tests += 1
                if gcd(c, m) == 1:
                    pair = unit_repeat_root(h, m, c)
                    check(nontrivial == ([(h, *pair)] if pair else []), "unit root arithmetic")
                    unit_tests += 1
                cases += 1
    return dict(depths=[2, 16], moduli="2..96 and 125,175,250,350,360,900",
                targets=cases, unit_targets=unit_tests, divisibility_comparisons=order_tests)


def zero_spectra():
    cases = 0
    examples = {}
    for h in (2, 3, 4, 5, 7, 8, 11):
        for m in (*range(2, 25), 60, 64, 72, 84, 120, 210, 360):
            bound = order_bound(h, m, 0)
            periods = []
            for d in range(1, bound+1):
                if bound % d:
                    continue
                n = m//d
                word = tuple(label for label in range(1, h+1) for _ in range(n))*d
                check(matrix_target(literal_matrix(word, h), m) == 0, "zero witness endpoint")
                period = primitive_period(word)
                check(period == h*n, "exact zero-target period")
                periods.append(period)
                cases += 1
            if (h, m) in ((5, 360), (7, 84), (4, 64), (5, 20)):
                examples[f"L{h}_m{m}"] = sorted(periods)
    return dict(explicit_words=cases, examples=examples)

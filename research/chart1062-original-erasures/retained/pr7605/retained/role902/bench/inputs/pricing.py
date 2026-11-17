"""Directed interval arithmetic and the retained signed BIT invoice."""
from collections import Counter
from fractions import Fraction
from functools import cache

TARGET = "10018846261809/2500000000000000"
SCALE = 10**49


def rounded(x, upper):
    scaled = SCALE*x
    if upper:
        return Fraction(-((-scaled.numerator) // scaled.denominator), SCALE)
    return Fraction(scaled.numerator // scaled.denominator, SCALE)


@cache
def log_bounds(x):
    z = (x-1)/(x+1)
    terms = 60
    exact_partial = 2*sum(z**(2*i+1)/(2*i+1) for i in range(terms))
    tail = 2*z**(2*terms+1)/((2*terms+1)*(1-z*z))
    return rounded(exact_partial, False), rounded(exact_partial+tail, True)


@cache
def power_bounds(rank, k):
    binary = 2**(rank.bit_length()-1)
    shift = binary.bit_length()-1
    l2, u2 = log_bounds(Fraction(2))
    lo, hi = log_bounds(Fraction(rank, binary))
    lo, hi = k*(lo+shift*l2), k*(hi+shift*u2)
    assert 0 <= lo <= hi < 1

    def exponential(z, terms):
        total = term = Fraction(1)
        for i in range(1, terms+1):
            term *= -z/i
            total += term
        return total

    return rounded(rank*exponential(hi, 35), False), rounded(rank*exponential(lo, 34), True)


def cost(hist, k):
    lower = upper = Fraction(0)
    for r, n in hist.items():
        a, b = (n*x for x in power_bounds(r, k))
        lower += min(a, b)
        upper += max(a, b)
    return lower, upper


def profile(invoice, native, word, ranks):
    copies = invoice["native_calls"]
    assert copies == len(invoice["native_instances"]) == 36
    assert {tuple((r["stage"], r["copy"])) for r in invoice["native_instances"]} == {
        (stage, which) for stage in range(1, 19) for which in (0, 1)
    }
    assert all(r["ports"] == 111 for r in invoice["native_instances"])
    assert native == Counter({int(r): n for r, n in invoice["native_paid"].items()})
    assert sum(native.values()) == 2871
    caller_paid = {1: 444, **{r: 444 for r in range(7, 57, 7)}}
    assert invoice["event_counts"]["QUERY"]*111 == caller_paid[1]
    assert invoice["event_counts"]["IDLE_ONE"]*111 == 8*444
    full_paid = Counter({r: copies*n for r, n in native.items()})
    full_paid.update(caller_paid)

    helpers = Counter(ranks[word["final"][j]]-ranks[word["start"][j]]
                      for j in range(222, word["public"]))
    assert helpers == Counter({int(r): n for r, n in invoice["native_helpers"].items()})
    caller_targets = {**{r: 444 for r in range(8, 65, 7)}, 127: 222}
    full_targets = Counter({r: copies*n for r, n in helpers.items()})
    full_targets.update(caller_targets)
    assert full_paid == Counter({int(r): n for r, n in invoice["paid"].items()})
    assert full_targets == Counter({int(r): n for r, n in invoice["targets"].items()})
    assert sum(full_paid.values()) == invoice["paid_jobs"]
    assert sum(full_targets.values()) == invoice["productive_fields"]
    signed = full_targets.copy()
    signed.subtract(full_paid)
    assert sum(r*n for r, n in signed.items()) == invoice["rank_surplus"]
    return signed, copies

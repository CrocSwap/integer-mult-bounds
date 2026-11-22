"""Compute whole-machine tariffs from the raw words and the actual signed controller."""

from collections import Counter
from fractions import Fraction as Q
import json
from pathlib import Path

from activation import resource_receipt
from installations import BINARY_C, GAUSSIAN_C, PROFILES
from linear_geometry import connected_exponent, entrance_geometry
from ordinary_clock import polynomial_to_fibre_bound
from outer_budget import qualify
from outer_clock import exact_shape_check, financial_checks
from raw_binary_stage import binary_word
from staged_carriers import entrance_logs
from strict_moment import power_interval, UNIT
from unpowered_price import certify, intervals, ranks
from upstream import HERE

HERE_RESULT = Path(__file__).with_name("RESULT.json")
SETUP_LOG = 513


def tariff(c, census, ambient):
    targets, paid = census
    t = 1-c
    margin, cells = certify(c, census)
    assert cells and margin > 0 and min(cells.values()) / sum(targets.values()) > Q(1,2**64)
    assert max(max(targets), max(paid)) <= 129 and min(paid) >= Q(1, 2)
    assert all(4*k >= 5*r for r,k in cells)
    assert max(max(v.numerator.bit_length(), v.denominator.bit_length()) for v in cells.values()) < 512
    p = Q(sum(count * intervals(r, t)[0] for r,count in paid.items()), UNIT)
    total = Q(sum(count * intervals(k, t)[1] for k,count in targets.items()), UNIT)
    assert p/total > Q(99,100) and p > 10
    lower, guard, delta = 2**15, 1024, Q(1,2**128)
    def upper(x, exponent):
        return Q(intervals(x, exponent)[1], UNIT)
    lt = Q(power_interval(lower,t)[0], UNIT)
    assert upper(max(targets),c) < Q(102,100) and lt > 2**14 and t > Q(996,1000)
    factor = (Q(256,255)*Q(4097,4096)*Q(1028,1024)*upper(4*guard*ambient,c)
              * (upper(max(targets)*lower,c) + 60/lt + delta)
              / ((1-Q(10,lower))*(1-delta)**2))
    assert factor**16 < 8
    if ambient == 134:
        assert (factor*Q(19,2))**2 < 128
    else:
        assert cells[56,129] > 0
    return {"productive":sum(targets.values()), "paid":sum(paid.values()), "cells":len(cells),
            "directed_margin":str(margin), "factor_upper_times_1000000":-(-10**6*factor.numerator//factor.denominator)}


def ceiling_log(q):
    answer = max(0, q.numerator.bit_length() - q.denominator.bit_length())
    return answer if 2**answer >= q else answer+1


def profile_row(profile):
    receipt = resource_receipt(profile)
    heights = profile.rank_logs
    cuts = entrance_logs(heights)
    assert tuple(receipt["binary_cuts"]) == tuple(cuts)
    A = connected_exponent(cuts[-1],profile.complex_log)
    assert receipt["public_exponent_A"] == A
    geom = entrance_geometry(A)
    assert geom["public_offset_above_2_to_A"] == receipt["first_public_offset"]
    prev = Q()
    history = []
    for i,h in enumerate(heights):
        covered = BINARY_C-Q(7,2*h)
        limit = min(profile.eta,(249*covered+prev)/250)
        b = profile.ordinary if i+1 == len(heights) else Q(int(limit*10**21)-1,10**21)
        assert prev < b < limit and polynomial_to_fibre_bound()+80*h < 1024*h
        history.append(str(b))
        prev = b
    positive = GAUSSIAN_C-Q(1,5*profile.complex_log)
    signed = qualify(profile.kappa,Q(1,profile.positive_stop_denominator),prev,positive)
    logB = 40 + ceiling_log(Q(133,10)**len(heights)) + 16384*sum(heights)
    logC = 1+max(2**27, 1600 + 220*profile.complex_log + logB + 1)
    return {"kappa":str(profile.kappa),"binary_H":list(heights),"numerical_H":profile.complex_log,
            "width_logs":[92*h for h in (*heights, profile.complex_log)],
            "stage_rates":history,"signed_gate":signed,"geometry":geom,**receipt,
            "log2_fixed_setup_and_install_le":SETUP_LOG,"log2_ordinary_clock_le":logB,
            "log2_C_le":logC}


def baseline():
    from calibration import PROFILES as old, entrance
    result = {}
    for key in ("compact","high-rate","price-match","fixed-stock-stop","small-gap"):
        profile = old[key]
        H, M = profile.rank_logs, profile.complex_log
        logB = 40+16384*sum(H)
        logS = 1024*max(*H,M)+(len(H)+1).bit_length()
        result[key] = {"binary_H":list(H),"numerical_H":M,"kappa":str(profile.kappa),
                       "A":entrance(profile),"log2_S_le":logS,
                       "old_installed_visits_log_gt":7*(max(H)-2-9*profile.power),
                       "log2_C_le":1+max(2**27,1436+100*M+logB+1)}
    return result


def all_results():
    word = binary_word()
    census = Counter(word.targets),Counter(word.paid)
    from independent_binary_price import raw_moments, rank_price
    from strong_binary import graph, caller
    assert census == raw_moments(graph(),caller())
    for grade in set(census[0]) | set(census[1]):
        a,b = rank_price(grade,1-BINARY_C)
        lo,hi = intervals(grade,1-BINARY_C)
        assert Q(lo,UNIT) <= b and a <= Q(hi,UNIT)
    binary = tariff(BINARY_C,census,134)
    positive = tariff(GAUSSIAN_C,ranks(),153)
    assert (binary["cells"],positive["cells"]) == (24,31)
    early = financial_checks()
    regime = exact_shape_check(HERE)
    rows = {name: profile_row(profile) for name,profile in PROFILES.items()}
    from equal_rate import comparisons
    return {"baseline":baseline(),"equal_rate":comparisons(),"binary":binary,"positive":positive,"profiles":rows,
            "prefix":early,"first_controller_shape":regime}


def verify():
    actual = all_results()
    assert actual == json.loads(HERE_RESULT.read_bytes())
    for name, row in actual["profiles"].items():
        print(name, "A", row["public_exponent_A"], "log2 C <=", row["log2_C_le"])
    print("binary / numerical transport pairs", actual["binary"]["cells"], actual["positive"]["cells"])


if __name__ == "__main__":
    print(json.dumps(all_results(),indent=2))

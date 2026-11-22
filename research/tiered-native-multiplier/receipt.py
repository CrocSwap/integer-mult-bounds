"""Recompute the complete rate, calendar, stock and fixed-tape bounds."""

from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import json
import sys

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
from upstream import install
install()
sys.path.append(str(PACKAGE / "source"))
from activation import resource_receipt
from band_product import prepare_native
from grades import SCALES
from independent_binary_price import raw_moments
from installations import BINARY_C, GAUSSIAN_C, ENTRY, TERMINAL, activation, at_public
from linear_geometry import entrance_geometry
from ordinary_clock import first_stage_bound, polynomial_to_fibre_bound
from outer_budget import qualify
from outer_clock import financial_checks
from raw_binary_stage import binary_word
from strong_binary import caller, graph
from strict_moment import UNIT, power_interval
from unpowered_price import certify, intervals


def ceil(x):
    return -(-x.numerator // x.denominator)


def tariff(recipe, target, paid):
    c = recipe.trial
    margin, cells = certify(c, (target, paid))
    assert cells == recipe.cells and margin > 0
    assert min(cells.values()) / sum(target.values()) > Q(1, 2**64)
    assert max(max(v.numerator.bit_length(), v.denominator.bit_length()) for v in cells.values()) < 512
    assert all(5*r <= 4*k for r,k in cells)
    t = 1 - c
    p = sum(n * Q(intervals(r,t)[0], UNIT) for r,n in paid.items())
    total = sum(n * Q(intervals(k,t)[1], UNIT) for k,n in target.items())
    assert p > 10 and p / total > Q(99,100)
    assert t > Q(996,1000) and power_interval(max(target),c)[1] * 100 < 106*UNIT
    lower, delta = 32768, Q(1, 2**128)
    factor = (Q(256,255)*Q(4097,4096)*Q(1028,1024)
              *Q(power_interval(1024*recipe.ambient*lower,c)[1], UNIT)
              *(1+Q(64,lower)+delta)/((1-Q(10,lower))*(1-delta)**3))
    if c == BINARY_C:
        assert (factor*Q(47,20))**8 < 2**11 and Q(75,32)/Q(47,20) == Q(375,376)
    else:
        assert recipe.ambient == 12087 and len(cells) == 62
        assert max(Q(k)/r for r, k in cells) == 9
        assert cells[4424,10191] == 1 and target[10191] == 624
        assert factor < Q(power_interval(2,Q(43,256))[0],UNIT)
    return dict(targets=target.total(), paid=paid.total(), margin=str(margin),
                transport_cells=len(cells), physical_factor_upper_millionths=ceil(factor*10**6))


def bank(profile):
    stages = profile.rank_logs
    previous = Q(0)
    rates = []
    for i, h in enumerate(stages):
        funded = min(profile.eta,(249*(BINARY_C-Q(11,8*h))+previous)/250)
        rate = (profile.ordinary if i+1==len(stages)
                else Q(int(funded*10**21)-1,10**21))
        assert previous < rate < funded
        rates.append(str(rate))
        previous = rate
    num = profile.complex_log
    positive = GAUSSIAN_C-Q(43,256*num)
    stock = resource_receipt(profile)
    A = activation(profile)
    assert A == stock["public_exponent_A"] and min(stages) >= 3000
    signed = qualify(profile.kappa,Q(1,profile.positive_stop_denominator),previous,positive)
    if min(stages) >= 8192:
        assert 2660000*32 < 2**30
        ordinary = 128+320*sum(stages)
        extra = []
    else:
        expense = [first_stage_bound(profile.eta), polynomial_to_fibre_bound()]
        extra = [max(0,e-944*h) for e,h in zip(expense,stages,strict=True)]
        assert Q(376*7,10)**len(stages) < 2**17
        ordinary = 40+17+16384*sum(stages)+sum(extra)
    E = max(84500001,1602+220*num+ordinary)
    return dict(kappa=str(profile.kappa), binary_H=stages, gaussian_H=num,
                width_exponents=[92*h for h in (*stages,num)], rates=rates,
                positive_rate=str(positive), signed=signed, stock=stock,
                geometry=entrance_geometry(A), variable_cost_surcharges=extra,
                log2_B=ordinary, log2_C=E)


def verify():
    early_rec, late_rec = prepare_native()
    early_bit, _, early_num = early_rec
    bit, _, num = late_rec
    assert bit.cells is early_bit.cells and num.targets is early_num.targets
    assert num.cells is early_num.cells and num.paid is early_num.paid
    btarget, bpaid = raw_moments(graph(), caller())
    assert (btarget,bpaid) == (Counter(binary_word().targets),Counter(binary_word().paid))
    assert sum(r*n for r,n in btarget.items()) == 286098
    assert sum(r*n for r,n in bpaid.items()) == 284592
    actual = Counter(num.targets), Counter(num.paid)
    assert actual == (num.targets.histogram,num.paid.histogram)
    assert (len(num.targets),len(num.paid)) == (105216,564144) and SCALES == (1,79)
    b_receipt = tariff(bit,btarget,bpaid)
    n_receipt = tariff(num,*actual)
    early, late = bank(ENTRY), bank(TERMINAL)
    boundary = activation(TERMINAL)
    threshold = 1 << boundary
    assert at_public(threshold-1) is ENTRY and at_public(threshold) is TERMINAL
    # Public precision is a multiple of six. Exercise the last and first such headers.
    first_public = threshold + (-threshold)%6
    assert at_public(first_public-6) is ENTRY and at_public(first_public) is TERMINAL
    premium = ceil((TERMINAL.kappa-ENTRY.kappa)*boundary)
    cost = 1+max(early["log2_C"]+premium,late["log2_C"])
    assert (premium,cost) == (572,339787971)
    delta = TERMINAL.kappa-Q(".0038981721342")
    assert delta == Q(139329,5*10**12) and delta > 0
    prefix = financial_checks()
    return dict(binary=b_receipt,gaussian=n_receipt,entry=early,terminal=late,
                old_rate=".0038981721342",rate_delta=str(delta),entry_premium=premium,
                complete_log2_C=cost,prefix=prefix)


if __name__ == "__main__":
    actual = verify()
    print(json.dumps(actual,indent=2))

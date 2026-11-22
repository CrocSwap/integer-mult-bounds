"""Exploratory seven-stage retimed invoice, not a published theorem."""

from fractions import Fraction as Q
from decimal import Decimal, getcontext
from hashlib import sha256
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

from upstream import install
install()

from activation import resource_receipt
from check_complete import profile_row
from installations import BINARY_C, GAUSSIAN_C, SEVEN_STAGE
from outer_budget import qualify

getcontext().prec = 55

def dec(q):
    return str(Decimal(q.numerator) / Decimal(q.denominator))

p = SEVEN_STAGE
H, K, G = tuple(p.rank_logs), p.kappa, Q(1,p.positive_stop_denominator)
assert H == tuple(10**12 * 16**i for i in range(7))
assert K == Q("0.003890115286594460") and G == Q(1,10**20)
outer_factor_bits = (((128*10**20)**16)-1).bit_length()
assert outer_factor_bits == 1176
assert 1434 - 1024 + outer_factor_bits < 1600
assert max(H).bit_length() <= 64

previous = Q(0)
stages = []
for i,h in enumerate(H):
    covered = BINARY_C-Q(7,2*h)
    limit = min(p.eta,(249*covered+previous)/250)
    booked = K+5*G if i == len(H)-1 else Q((limit*10**21).__floor__()-1,10**21)
    assert previous < booked < limit
    stages.append({"stage":i+1,"height":h,"covered":dec(covered),"limit":dec(limit),
                   "booked":dec(booked),"limit_minus_booked":dec(limit-booked)})
    previous = booked

pos = GAUSSIAN_C-Q(1,5*p.complex_log)
gate = qualify(K,G,previous,pos)
for bad in ((K,Q(0),previous,pos), (K,Q(1,10**17),previous,pos),
            (K,G,K+4*G,pos), (K,G,previous,K+5*G)):
    try:
        qualify(*bad)
    except ArithmeticError:
        pass
    else:
        raise AssertionError("An unfunded signed control passed")
row = profile_row(p)
from dataclasses import replace
try:
    resource_receipt(replace(p,rank_logs=H+(H[-1]*16,)))
except AssertionError:
    pass
else:
    raise AssertionError("An eighth stage crossed the local guard")
assert tuple(row["stage_rates"]) == tuple(str(Q(x["booked"])) for x in stages)
assert max(row["binary_cuts"]).bit_length() <= 64
assert row["public_exponent_A"].bit_length() <= 64
assert row["kappa"] == str(K)
s = row["initial_s"]
bits = (s+128).bit_length()
allowance = 8352+4*bits
head_sum = 2048+32*64+(7+12)+7+5+35+3*bits
assert allowance-head_sum == 4190+bits
assert 7*2**32 < 2**35
assert 2**66 * 2**(83*3000) < 2**(92*3000)
row["stage_analysis"] = stages
row["binary_C_decimal"] = dec(BINARY_C)
row["positive_covered_decimal"] = dec(pos)
row["gate_margins_decimal"] = {k:dec(Q(v)) for k,v in gate.items() if "margin" in k}
row["outer_polynomial_factor_ceiling_log2"] = outer_factor_bits
row["outer_cofinal_extra_factor_log2_le"] = 1434-1024+outer_factor_bits
row["signed_rejection_controls"] = ["g=0", "g=10^-17", "ordinary at k+4g", "positive at k+5g"]
row["physical_scope"] = ("Arithmetic application of #8042 pricing with seven stages; "
 "activation stage-count assertion changed locally from 6 to 7; "
 "full written seven-stage tape proof and production-scale execution not certified")
print(json.dumps(row,indent=2))

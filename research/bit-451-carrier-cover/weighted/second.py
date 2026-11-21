# SPDX-License-Identifier: Apache-2.0
"""Bind the tensor second-moment compiler proof to its complete signed application."""
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
CAP = "0.00387992804513502"
CLAIM = "0.00387992804505"
HASHES = {
    "APPLICATION.json": "038a693200287638feae8d6888d4834577e3eb4b2d95cd75ea607605f1c989a0",
    "AUDIT.json": "bf063d3cee7cdde73575265d2e73f430f71dd98abf611bd63cddcbc8ed0e78e1",
    "adapter/binary/FINITE.json": "7996ddb19a9bf9269a072aee60d331caacda2f3350fbc6c2b8c052701d980e87",
}


def shifted_moments(moments, a, count):
    power = len(moments)-1
    values = [a**i for i in range(power+1)]
    for _ in range(count):
        values = [sum(comb(i,j)*values[i-j]*moments[j] for j in range(i+1)) for i in range(power+1)]
    return values


def coefficient_ratios(moments, a, b, beta):
    power = len(moments)-1
    shifted = shifted_moments(moments,a,1)
    bell = [[Q(0)]*(power+1) for _ in range(power+1)]
    stirling = [[0]*(power+1) for _ in range(power+1)]
    bell[0][0] = stirling[0][0] = 1
    for n in range(1,power+1):
        for k in range(1,n+1):
            bell[n][k] = sum(comb(n-1,j-1)*moments[j]*bell[n-j][k-1] for j in range(1,n-k+2))
            stirling[n][k] = k*stirling[n-1][k]+stirling[n-1][k-1]
    ratios = []
    for k in range(power+1):
        numerator = sum(comb(power,i)*shifted[power-i]*bell[i][k] for i in range(k,power+1))
        denominator = sum(comb(power,i)*b**(power-i)*beta**i*stirling[i][k] for i in range(k,power+1))
        if numerator < 0 or denominator <= 0:
            raise ValueError("invalid coefficient signs")
        ratios.append(numerator/denominator)
    return ratios


def component(base, weighted, previous, proof, seven_stages, check):
    count, h, p = base["partition"]["factors"], weighted["h"], 31
    H = base["uniform"]["H"]
    mean = Q(weighted["q"])
    check(count == 451 and h == proof["h"] == 1804 and p == proof["p"] and
          max(map(int,base["native"]["paid"])) == 56 < 11**2 and
          Q(weighted["mean_plus_tail_ceiling_15dp"]) < mean == Q(3,4), "bounded tensor factors and paid mean")
    raw = ((count-1)*mean**2+2*mean)/count
    sep = base["separation"]
    eps = Q(sep["paid_uplift_upper"][1])/Q(sep["three_engine_intervals"]["source_1"]["alpha"][0])**count
    eps_cap = Q(proof["paid_excess_upper"])
    after = (raw+eps_cap)/(1+eps_cap)
    check(raw == Q(proof["raw_M2"]) and 0 < eps < eps_cap == Q(1,10**15) and
          (raw+eps)/(1+eps) < after == Q(proof["post_split_M2_upper"]) < Q(3,5),
          "completed second-moment bound with every excess paid term")
    a, b, beta = map(Q,(weighted["A_bar"],weighted["B_under"],weighted["beta"]))
    moments = [Q(1),mean]+[Q(3,5)]*(p-1)
    eta, eta_upper = map(Q,base["uniform"]["eta"])
    # Under the old envelope every positive moment used the Bernoulli mean.
    old_at_five = shifted_moments([Q(1)]+[mean]*p,a,6)[p]/(b+5*beta)**p
    at_five = shifted_moments(moments,a,6)[p]/(b+5*beta)**p
    check(old_at_five == Q(previous["negative_ratio"]) == Q(proof["old_height_5"]) and
          at_five == Q(proof["new_height_5"]) and at_five < eta < eta_upper < old_at_five,
          "height-five control and repaired power")
    ratios = coefficient_ratios(moments,a,b,beta)
    peak = max(ratios)
    check(len(ratios) == 32 and ratios == list(map(Q,proof["all_ratios"])) and
          eta == Q(proof["eta_lower"]) and peak == Q(proof["maximum_ratio"]) < eta and
          ratios.index(peak) == proof["peak_index"] == 4, "all Bell and direct-Newton coefficients")
    ambient_floor = (134**451).bit_length()-1
    check(Q(h+ambient_floor,h)**p > Q(base["uniform"]["ambient_power"][1]), "all base ranks")
    top, bottom = (H+h)**p,h**p
    J = (top//bottom).bit_length()
    loss = Q(J,H)
    check(J == proof["uniform_J"] == 1218 and loss == Q(proof["uniform_loss"]) and
          (bottom << (J-1)) <= top < (bottom << J) and (H+h)*loss > 2*p, "least integer loss and tail")
    seven_stages(base,loss,CAP,check)
    check(Q(previous["uniform_loss"]) == Q(1257,H), "fixed power-32 charge")
    old_claim, claim = Q(previous["candidate_grid_claim"]),Q(CLAIM)
    ceiling = Q(base["raw_crossing"][1]) - Q(previous["uniform_loss"]) - Q(7,10**14)
    check(Q(CAP) == Q(proof["cap"]) and claim == Q(proof["candidate_grid_claim"]) and
          claim > ceiling > old_claim and ceiling == Q(proof["old_cover_forgiven_upper"]) and
          claim-ceiling == Q(proof["separation"]), "complete signed separation")
    check(claim-old_claim == Q(proof["absolute_gain"]) == Q(3,10**14) and
          100*(claim-old_claim)/old_claim == Q(proof["exact_relative_percent"]), "exact predecessor gain")
    return {"installed": CAP,"old_fixed_loss_ceiling": str(ceiling)}


def run(source, work, legacy, seven_stages, base):
    check, digest = legacy["check"], legacy["digest"]
    weighted, previous = HERE/"RESULT.json", HERE/"MINIMUM.json"
    check(digest(weighted) == "f2218a9eb212ef7f0ae1c993297df50c401bb6b24537318c2570cea54d6d2b92" and
          digest(previous) == "b8a72fc639fecfe4a815421413ff2d47aa7c65d96b35339285be67c557fbdac5" and
          digest(HERE/"LOG-MOMENTS.md") == "f4a067517ebf1db95b3179f30c4f0ec284666052469ed3502f0eb8cbbc4dc131",
          "pinned first moment, power-32 result and second-moment proof")
    proof = json.loads((HERE/"SECOND.json").read_bytes())
    bound = component(base,json.loads(weighted.read_bytes()),json.loads(previous.read_bytes()),proof,seven_stages,check)
    outer = work/"second-consumer"
    full = legacy["consumer"](source,outer,bound,cap=CAP,expected_claim=CLAIM,expected_hashes=HASHES)
    audit = work/"second.json"
    subprocess.run([sys.executable,"-IB",HERE/"second_audit.py",source,weighted,previous,audit,"--outer",outer],
                   check=True)
    check(json.loads(audit.read_bytes()) == proof and Q(full["tested"]) == Q(proof["candidate_tested"])
          and Q(full["delta"]) == Q(159,10**14), "independent second-moment audit with actual consumer")
    print("PASS_COMPLETE_SECOND_MOMENT",f"claim={full['claim']}",f"delta_vs_power32={proof['absolute_gain']}",
          f"delta_vs_7863={full['delta']}",flush=True)
    return full

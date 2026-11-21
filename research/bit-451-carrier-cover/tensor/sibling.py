# SPDX-License-Identifier: Apache-2.0
"""Rebuild the source-capacity and complete signed power-19 certificate."""
from decimal import Decimal, localcontext
from fractions import Fraction as F
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ARCHITECTURE = HERE.parents[2] / "research/kappa-rebuild/architecture"
NATIVE_PROOF = Path("inputs/framework/research/p104-shared-native-helper-splits/retained/compiler/PROOF.md")
FLOW = ARCHITECTURE / "FINITE-PRECOMPILATION.md"
TREE = ARCHITECTURE / "sources/Sussman-563b4e6/research/record-track/programs/theorem-1g/tree_flow.py"
CAP = "0.00387992804552674"
CLAIM = "0.00387992804544"
V, P = 451, 19
HASHES = {
    "APPLICATION.json": "8d5a5fa30f79b5f39fabc2bb320f38ac291761c0012de5d22540a142b1d767af",
    "AUDIT.json": "e8dbc8054ecd54bb6d089346cf84220499d8683fd2043b0650817ad0bd0dd806",
    "adapter/SOURCE-LOCK.json": "b46b919292e1a1907345056b6925f5f1400d45650e2f0f610779a07163bb64ee",
    "adapter/binary/WORD.json.gz": "d28f0d28d9d87d5fe57b8ef19e12faf98014f0bbef781987ce22daaa82f21cb9",
    "adapter/binary/FINITE.json": "288ac59e27bf7703ffda5b8b3eb91a0f94da2e0d0227e066ae35a73f58c924b6",
}


def check(condition, message):
    if not condition:
        raise ValueError(message)


def logarithm(integer):
    ans = Decimal(integer).ln()
    return F(ans.next_minus()), F(ans.next_plus())


def exp_bound(value, upper):
    arg = Decimal(value.numerator)/Decimal(value.denominator)
    if upper:
        return F(arg.next_plus().exp().next_plus())
    return F(arg.next_minus().exp().next_minus())


def fixed_lower(value):
    return F((value*10**22).__floor__(),10**22)


def profile(data,t):
    one = sum(int(k)*w for k,w in data.items())
    moment_hi = sum(w*(exp_bound(t*logarithm(int(k))[1],True) if int(k)>1 else 1)
                    for k,w in data.items())
    return one,moment_hi


def source_guards(bit):
    sep = bit['separation']
    delta = F(sep['trial'])
    t = 1-delta
    check(0 < t < 1,'trial slope')
    with localcontext() as ctx:
        ctx.prec = 76
        targets, target_upper = profile(bit['native']['targets'],t)
        paid, paid_upper = profile(bit['native']['paid'],t)
        loss = F(sep['discarded_target_upper'][1])
        eps = F(1,10**15)
        alpha = F(sep['three_engine_intervals']['source_1']['alpha'][0])
        check(0 < F(sep['paid_uplift_upper'][1]) < eps*alpha**V,'paid uplift')
        root_guard = (F(targets)/target_upper)**V / exp_bound(V*delta*logarithm(16)[1],True)-loss
        partial_guard = exp_bound(V*delta*(logarithm(16)[0]-logarithm(11)[1]),False)
        full_guard = (F(paid)/paid_upper)**V/(1+eps)
    return {k:fixed_lower(x) for k,x in [('root',root_guard),('partial',partial_guard),('full',full_guard)]}


def toy():
    # Includes a mixed full family and a partially admitted family. Pascal-label
    # multiplicity is per paid label, including three distinct rank-one calls.
    ranks = [1,1,1,4,6]
    floor,J,k,m=10,6,12,7
    counts=[]
    for L in (F(7,2),F(6),F(11),F(12)):
        admitted=[r for r in ranks if r <= L and L < k]
        counts.append(m*len(admitted))
        if L<J:
            check(all(k*r/L >= F(floor,J) for r in admitted),'partial sibling root')
        elif L<k:
            check(admitted==ranks,'whole sibling family')
        else:
            check(not admitted,'matched parent')
    check(counts==[21,35,35,0],'chronological label control')
    return counts


def component(base, old, proof, stages):
    supplier = HERE / "minimum_screen.py"
    exact = {"__name__":"frozen_minimum_power"}
    exec(compile(supplier.read_bytes(),str(supplier),"exec"),exact)
    check(exact["P"] == 21 and exact["H_SHIFT"] == 1804, "original fixed tensor screen")
    exact["P"] = P
    check((old["p"], old["h"], old["uniform_J"]) == (20, 1804, 786)
          and (proof["p"], proof["h"], proof["positive_control_p"]) == (P, 1804, 20), "predecessor and power")
    check(toy() == [21,35,35,0] and proof["edge_control_counts"] == [9,12,15,15,5,0],
          "separate equal-rank labels and boundary source counts")
    targets = base["native"]["targets"]
    counts = {64:151,8:299,2:1}
    check(all(targets[str(rank)] > 0 for rank in counts) and sum(counts.values()) == V
          and {int(k):v for k,v in proof["attained_target_floor"]["tuple_counts"].items()} == counts
          and proof["attained_target_floor"]["two_adic_exponent"] == 4*V and 64**151*8**299*2 == 16**V
          and 64**150*8**300*2 < 16**V, "exact retained productive minimum and below-cutoff control")
    guards = source_guards(base)
    expected = {key:F(value) for key,value in proof["source_lower"].items()}
    check({key:F((value*10**18).__floor__(),10**18) for key,value in guards.items()} == expected
          and min(expected.values()) > F(8,5) == F(proof["capacity_multiplier"]),
          "root, partial sibling and full sibling source lower bounds")
    moments = list(map(F, old["moments"][:P+1]))
    lo, hi = map(F,base["uniform"]["eta"])
    nums, dens = exact["newton"](moments)
    check(len(dens) == P+1 and min(dens) > 0 and min(nums) >= 0, "all coefficient signs")
    ratios = [n/d for n,d in zip(nums,dens,strict=True)]
    peak = max(ratios)
    check(ratios == list(map(F,proof["coefficients"])) and ratios.index(peak) == proof["peak_index"]
          and ratios[-1] == (F(749,1000)/F(23,20))**P and hi < peak < F(8,5)*lo
          and F(8,5)*lo == F(proof["effective_capacity_lower"]) and proof["negative_control_unmodified_capacity"],
          "power 19 fails the old capacity and clears every corrected coefficient")
    h = 1804
    check((1+F((134**V).bit_length()-1,h))**P > F(base["uniform"]["ambient_power"][1]), "normalized base guard")
    H = base["uniform"]["H"]
    cost = exact["price"](base,old)
    check(cost["J"] == proof["uniform_J"] == 747 and F(cost["J"],H) == F(proof["uniform_loss"])
          and cost["stages"] == proof["stages"] and F(cost["cap"]) == F(CAP) and proof["cap"] == CAP
          and cost["passes"] and F(cost["claim"]) == F(CLAIM) == F(proof["candidate_grid_claim"])
          and F(cost["tested"]) == F(proof["candidate_tested"]), "strict terminal, tail and seven ordinary stages")
    stages(base,F(747,H),CAP,check)
    ceiling = F(base["raw_crossing"][1]) - F(old["uniform_loss"]) - F(7,10**14)
    check(ceiling == F(cost["old_relaxed_ceiling"]) == F(proof["old_relaxed_ceiling"])
          and F(CLAIM)-ceiling == F(proof["separation"]) > 0
          and F(CLAIM)-F(old["candidate_grid_claim"]) == F(proof["absolute_gain"]) == F(3,10**14),
          "strict separation from the old complete power-20 ceiling")
    return {"installed":CAP,"old_fixed_loss_ceiling":str(ceiling)}


def run(source, work, legacy, stages, base):
    digest = legacy["digest"]
    checked = HERE / "SIBLING.json"
    check(digest(checked) == "42aede07a16e538f97e43341a605e7a432fc0e600504cb1a381e1476abaa30fd"
          and digest(HERE / "minimum_screen.py") == "2df053c036c3bf8c3f4f6deccdcdfa3d4821b3c801c6410fe0e377dba6149d23",
          "independent receipt and primary coefficient and price implementation")
    proof = json.loads(checked.read_bytes())
    sources = {"bit":source/"BIT-451.json","old":HERE/"MEAN.json","flow":FLOW,"tree":TREE,
               "producer":source/"PROOF.md","ambient":source/NATIVE_PROOF,"tensor":HERE/"audit.py"}
    check({key:digest(path) for key,path in sources.items()} == proof["pins"]
          and digest(source/"replay/BIT-451.json") == proof["pins"]["bit"], "frozen source and original BIT replay")
    bound = component(base,json.loads(sources["old"].read_bytes()),proof,stages)
    outer = work/"sibling-tensor-consumer"
    full = legacy["consumer"](source,outer,bound,cap=CAP,expected_claim=CLAIM,expected_hashes=HASHES)
    audited = work/"sibling-independent.json"
    args = [sys.executable,"-IB",HERE/"sibling_audit.py"]
    for key,path in sources.items():
        args.extend(["--"+key,path])
    subprocess.run([*args,"--out",audited,"--outer",outer],check=True)
    result = json.loads(audited.read_bytes())
    binding = result.pop("outer_binding")
    check(result == proof and all(binding["output_sha256"][key] == value for key,value in HASHES.items())
          and set(binding["controls"]) == {"low_cap_rejected","extra_rank_1_charge_rejected"}
          and F(full["tested"]) == F(proof["candidate_tested"]) and F(full["delta"]) == F(198,10**14),
          "complete independent source complement and signed result")
    print("PASS_COMPLETE_SIBLING_CAPACITY",f"claim={full['claim']}",f"delta_vs_p20={proof['absolute_gain']}",
          f"delta_vs_7863={full['delta']}",flush=True)
    return full

#!/usr/bin/env python3
"""Independent invoice certificate; @CubeJerry, OpenAI assistance, Apache-2.0."""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import tempfile
from functools import lru_cache
from intervals import SCALE, Interval, ZERO, need, power, signed_moment

PACKAGE = Path(__file__).resolve().parent
LOWER = Fraction("0.0033718004754")
UPPER = Fraction("0.0033718004755")
HEAD = "ad24ad966b857dbfed50d9121624db84b2eccc92"
PORTS = 104
HELPERS = {1:14, 2:8, 3:4, 4:109, 5:17, 6:3, 7:10, 8:40, 9:359}
PAID = {1:2234, 2:454, 3:489, 4:110, 5:152, 6:7, 7:9, 8:1}


def profile(raw):
    need(isinstance(raw, dict), "profile object")
    result = {}
    for key, value in raw.items():
        rank = int(key)
        need(str(rank) == key and rank > 0, "canonical positive rank")
        need(type(value) is int and value > 0, "positive integer count")
        result[rank] = value
    return result


def difference(targets, paid):
    return {r:targets.get(r,0)-paid.get(r,0)
            for r in sorted(set(targets)|set(paid))}


def authenticate(root=PACKAGE):
    origins = json.loads((PACKAGE/"ORIGINS.json").read_text())
    need(len(origins["files"]) == 7, "seven retained source files")
    for item in origins["files"]:
        need(item["head"] == HEAD, "frozen predecessor head")
        data = (root/item["local_path"]).read_bytes()
        need(hashlib.sha256(data).hexdigest() == item["sha256"], "source SHA256")
        git_header = ("blob "+str(len(data))+"\0").encode()
        need(hashlib.sha1(git_header+data).hexdigest() == item["git_blob"], "source Git blob")


def family(left, right):
    need(type(left) is int and type(right) is int and min(left,right)>=1,
         "positive integer chain lengths")
    total = left+right
    targets = Counter({r:total*n for r,n in HELPERS.items()})
    paid = Counter({r:total*n for r,n in PAID.items()})
    targets[8*total+1] += PORTS
    for length in (left,right):
        for j in range(1,length+1):
            targets[8*j+1] += PORTS
        for j in range(1,length):
            paid[8*j] += PORTS
    # This all-parity invoice relaxation contains the pinned odd/odd caller.
    # Realizability of other parities is not used for its upper bound.
    if total%2 == 0:
        targets[1] += PORTS
        paid[1] += 3*PORTS
    else:
        paid[1] += 2*PORTS
    return dict(targets), dict(paid)


def source_recount(source, caller):
    need(profile(source["local"]["helpers"]) == HELPERS, "pinned native helpers")
    need(profile(source["local"]["paid"]) == PAID, "pinned native paid profile")
    events = caller["events"]
    locals_ = [event for event in events if event[0] == "LOCAL"]
    need(sorted(event[1] for event in locals_) == list(range(1,19)), "18 native sites")
    need(not any(event[0] == "IDLE" for event in events), "merged idle alphabet")
    targets = Counter({r:18*n for r,n in HELPERS.items()})
    paid = Counter({r:18*n for r,n in PAID.items()})
    need(len(caller["diagonal"]) == 20, "20 caller output rows")
    for row in caller["diagonal"]:
        need(len(row) == 20 and row[:2] == [-1,0], "target q and phase exponents")
        need(all(type(x) is int and x in (0,1) for x in row[2:]), "stage exponents")
        targets[1+8*sum(row[2:])] += PORTS
    for event in events:
        if event[0] == "QUERY":
            paid[1] += PORTS
        elif event[0] == "IDLE_ONE":
            stages = event[2]
            need(len(stages)>0 and len(set(stages)) == len(stages), "idle stage set")
            need(all(type(j) is int and 1<=j<=18 for j in stages), "idle stage range")
            paid[8*len(stages)] += PORTS
    target_dict, paid_dict = dict(targets), dict(paid)
    for key, value in (("targets",target_dict),("paid",paid_dict)):
        need(value == profile(source["price"][key]), "emitted/source "+key)
        need(value == profile(source["independent_invoice"][key]), "independent/source "+key)
    need((target_dict,paid_dict) == family(9,9), "formula/source complete bill")
    return target_dict, paid_dict


def grouped_family(left, right):
    """Source node bill for arbitrary full binary trees; no operator claim."""
    need(left and right, "nonempty lists of binary children")
    nodes = []
    def count(tree):
        if type(tree) is int and tree == 1:
            return 1
        need(isinstance(tree,(tuple,list)) and len(tree) == 2, "full binary tree")
        mass = count(tree[0])+count(tree[1])
        nodes.append(mass)
        return mass
    a, b = [count(x) for x in left], [count(x) for x in right]
    total = sum(a)+sum(b)
    need(len(nodes) == total-len(a)-len(b), "binary nodes equal omitted boundaries")
    targets = Counter({r:total*n for r,n in HELPERS.items()})
    paid = Counter({r:total*n for r,n in PAID.items()})
    targets[8*total+1] += PORTS
    for sizes in (a,b):
        partial = 0
        for size in sizes:
            partial += size
            targets[8*partial+1] += PORTS
            if partial<sum(sizes):
                paid[8*partial] += PORTS
    # Reverse left partitions to convert source suffixes into prefixes.
    # Every ordered partition is allowed, so this preserves the whole domain.
    for size in nodes:
        targets[8*size+1] += 2*PORTS
        paid[8*size] += 2*PORTS
        paid[1] += PORTS
    if (len(a)+len(b))%2 == 0:
        targets[1] += PORTS
        paid[1] += 3*PORTS
    else:
        paid[1] += 2*PORTS
    return dict(targets),dict(paid),len(nodes)


@lru_cache(None)
def trees(leaves):
    if leaves == 1:
        return (1,)
    return tuple((a,b) for left in range(1,leaves)
                 for a in trees(left) for b in trees(leaves-left))


@lru_cache(None)
def forests(leaves):
    if leaves == 0:
        return ((),)
    return tuple((tree,)+rest for first in range(1,leaves+1)
                 for tree in trees(first) for rest in forests(leaves-first))


def power_range(rank, low, high):
    return Interval(power(rank,high).lo,power(rank,low).hi)


def moment_range(coefficients, low, high):
    result = ZERO
    for rank,count in coefficients.items():
        result = result+power_range(rank,low,high).times(count)
    return result


def binary_gap(low=LOWER, high=UPPER, thin_charge=1):
    delta9 = power_range(73,low,high)-power_range(72,low,high)
    delta2 = power_range(17,low,high)-power_range(16,low,high)
    gap = delta9-delta2.times(2)+Interval(thin_charge*SCALE,thin_charge*SCALE)
    need(gap.lo>0, "binary-node envelope agrees with all-one optimum")
    return gap


def balanced_increment(total, low, high=None):
    if high is None:
        high = low
    m = total//2
    native = moment_range(difference(HELPERS,PAID),low,high)
    root = power_range(8*total+9,low,high)-power_range(8*total+1,low,high)
    side = power_range(8*m+9,low,high)-power_range(8*m,low,high)
    return native+(root+side).times(PORTS)


def ceiling_certificate(saving=UPPER, optimum=18):
    before = balanced_increment(optimum-1,saving)
    after = balanced_increment(optimum,saving)
    margin = signed_moment(difference(*family(optimum//2,(optimum+1)//2)),saving)
    need(before.lo>0, "left balanced increment positive")
    need(after.hi<0, "right balanced increment negative")
    need(margin.hi<0, "global maximum negative at upper endpoint")
    return {"before":before.decimal(),"after":after.decimal(),"maximum":margin.decimal()}


def expect_failure(action, label):
    try:
        action()
    except (ValueError,KeyError,TypeError):
        return label
    raise ValueError("negative control accepted: "+label)


def run():
    authenticate()
    source = json.loads((PACKAGE/"retained/RESULT.json").read_text())
    caller = json.loads((PACKAGE/"retained/CALLER.json").read_text())
    targets, paid = source_recount(source,caller)
    coefficients = difference(targets,paid)
    low_margin = signed_moment(coefficients,LOWER)
    high_margin = signed_moment(coefficients,UPPER)
    need(low_margin.lo>0 and high_margin.hi<0, "root bracket signs")
    ceiling = ceiling_certificate()
    left_sign = balanced_increment(17,LOWER,UPPER)
    right_sign = balanced_increment(18,LOWER,UPPER)
    need(left_sign.lo>0 and right_sign.hi<0, "unique maximizer throughout root bracket")
    binary_envelope_gap = binary_gap()
    native = difference(HELPERS,PAID)
    need(sum(native.values()) == -2892, "native count difference")
    need(sum(r*n for r,n in native.items()) == -1720, "native rank-mass difference")
    need(all(native[r]<0 for r in range(1,7)), "native low-rank signs")
    need(native[7] == 1 and native[8] == 39 and native[9] == 359, "native high-rank signs")
    derivative_lower = Fraction(-native[1]*8,81)-Fraction(2*native[7],7)-Fraction(native[8],8)
    need(derivative_lower>0, "normalized native derivative lower bound")
    checked_pairs = 0
    best = high_margin
    for left in range(1,32):
        for right in range(1,32):
            signed = difference(*family(left,right))
            need(sum(r*n for r,n in signed.items()) == 48*(left+right)-104,
                 "family rank-mass identity")
            margin = signed_moment(signed,UPPER)
            need(margin.hi<0, "finite upper-endpoint corroboration")
            if (left,right)!=(9,9):
                need(margin.hi<best.lo, "finite unique maximizer corroboration")
            checked_pairs += 1
    forest_cases = 0
    for total in range(2,8):
        for left in range(1,total):
            right = total-left
            all_one = signed_moment(difference(*family(left,right)),UPPER)
            for a in forests(left):
                for b in forests(right):
                    target, payment, internal = grouped_family(a,b)
                    signed = difference(target,payment)
                    need(sum(signed.values()) == 104-2892*total-104*internal,
                         "grouped zero-power endpoint")
                    need(sum(r*n for r,n in signed.items()) == 48*total-104,
                         "grouped unit-power endpoint")
                    if internal:
                        need(signed_moment(signed,UPPER).hi<all_one.lo,
                             "small grouped tree strictly loses to refinement")
                    else:
                        need((target,payment) == family(left,right), "all-one grouped bill")
                    forest_cases += 1
    gate_tree = ((1,1),(1,1))
    gate_target,gate_paid,gate_internal = grouped_family([1,gate_tree,gate_tree],
                                                       [1,gate_tree,gate_tree])
    gate_coefficients = difference(gate_target,gate_paid)
    gate_low = signed_moment(gate_coefficients,Fraction("0.00330823456614"))
    gate_high = signed_moment(gate_coefficients,Fraction("0.00330823456615"))
    need(gate_internal == 12 and gate_low.lo>0 and gate_high.hi<0,
         "retained (4,4,1|1,4,4) gate crossing")
    exact_power_controls = []
    for rank in (1,2,3,4,8,9,16,17,64,73,81,137,145,153):
        integer_power = power(rank,Fraction(0))
        need(integer_power.lo == integer_power.hi == rank*SCALE, "integer power identity")
        square_root = power(rank,Fraction(1,2))
        need(square_root.lo**2 <= rank*SCALE*SCALE <= square_root.hi**2,
             "square-root algebraic enclosure")
        exact_power_controls.append(rank)
    controls = []
    controls.append(expect_failure(lambda:binary_gap(thin_charge=0),"omit binary internal thin-query charge"))
    controls.append(expect_failure(lambda:ceiling_certificate(LOWER),"favorable lower endpoint cannot certify ceiling"))
    for false_optimum in (17,19):
        controls.append(expect_failure(lambda n=false_optimum:ceiling_certificate(UPPER,n),
                                       "wrong maximizing total "+str(false_optimum)))
    for label,kind in (("omit thin query","QUERY"),("omit merged idle job","IDLE_ONE")):
        changed = deepcopy(caller)
        position = next(i for i,e in enumerate(changed["events"]) if e[0] == kind)
        del changed["events"][position]
        controls.append(expect_failure(lambda c=changed:source_recount(source,c),label))
    changed = deepcopy(caller)
    idle = next(e for e in changed["events"] if e[0] == "IDLE_ONE" and len(e[2])>1)
    idle[2].pop()
    controls.append(expect_failure(lambda:source_recount(source,changed),"undercharge merged rank"))
    changed = deepcopy(caller)
    row = next(row for row in changed["diagonal"] if 1 in row[2:])
    row[2+row[2:].index(1)] = 0
    controls.append(expect_failure(lambda:source_recount(source,changed),"omit productive target axis"))
    changed = deepcopy(caller)
    changed["diagonal"][0][0] = 1
    controls.append(expect_failure(lambda:source_recount(source,changed),"wrong target q exponent"))
    changed_source = deepcopy(source)
    changed_source["local"]["paid"]["1"] -= 1
    controls.append(expect_failure(lambda:source_recount(changed_source,caller),"undercharge native job"))
    for bad_length in (0,True,1.5):
        controls.append(expect_failure(lambda n=bad_length:family(n,9),"invalid chain length "+repr(bad_length)))
    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        (temp/"retained").mkdir()
        origins = json.loads((PACKAGE/"ORIGINS.json").read_text())
        for item in origins["files"]:
            (temp/item["local_path"]).write_bytes((PACKAGE/item["local_path"]).read_bytes())
        authenticate(temp)
        for item in origins["files"]:
            path = temp/item["local_path"]
            original = path.read_bytes()
            path.write_bytes(original+b"\n")
            controls.append(expect_failure(lambda:authenticate(temp),"source mutation "+item["local_path"]))
            path.write_bytes(original)
    return {
        "status":"PASS_CHAIN_ROOT_GLOBAL_CEILING",
        "base_commit":"7c49fe32c55de02c2c873655c804b16e4c3fef0a",
        "source_head":HEAD,
        "source_pr":"CrocSwap/integer-mult-bounds#6833",
        "saving_bracket":[str(LOWER),str(UPPER)],
        "root_margin_lower":low_margin.decimal(),
        "root_margin_upper":high_margin.decimal(),
        "ceiling_certificate":ceiling,
        "root_bracket_increment_signs":{"17_to_18":left_sign.decimal(),"18_to_19":right_sign.decimal()},
        "binary_child_envelope":{"delta9_minus_node_upper":binary_envelope_gap.decimal(),
                                 "arbitrary_tree_corroboration_cases":forest_cases,
                                 "total_leaves":[2,7],"stop_rule":"all ordered pairs of full binary forests in domain",
                                 "gate_crossing_bracket":["0.00330823456614","0.00330823456615"],
                                 "gate_margin_lower":gate_low.decimal(),"gate_margin_upper":gate_high.decimal()},
        "unique_maximizing_lengths":[9,9],
        "normalized_native_derivative_rational_lower_bound":str(derivative_lower),
        "source_counts":{"target_fields":sum(targets.values()),"paid_jobs":sum(paid.values()),
                         "paid_rank_mass":sum(r*n for r,n in paid.items()),
                         "surplus":sum(r*n for r,n in coefficients.items())},
        "finite_corroboration":{"left":[1,31],"right":[1,31],"pairs":checked_pairs,
                                "seed":None,"stop_rule":"exhaust all declared pairs"},
        "exact_power_control_ranks":exact_power_controls,
        "negative_controls":controls,
        "scope":"Declared two-chain invoice family only; analytical proof extends beyond finite corroboration. No new kappa; no supplier admission."
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write",action="store_true",help="regenerate this package's deterministic result")
    args = parser.parse_args()
    result = run()
    destination = PACKAGE/"RESULT.json"
    if args.write:
        destination.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    else:
        need(json.loads(destination.read_text()) == result,"committed deterministic result")
    print(result["status"])
    print(json.dumps({"root_bracket":result["saving_bracket"],"maximizer":[9,9],
                      "negative_controls":len(result["negative_controls"]),
                      "corroborating_pairs":result["finite_corroboration"]["pairs"]},sort_keys=True))


if __name__ == "__main__":
    main()

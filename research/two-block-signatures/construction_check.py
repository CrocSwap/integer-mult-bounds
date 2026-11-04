"""Independent literal reading of every stored construction and the four-port handoff."""
from dataclasses import astuple
from itertools import permutations
from math import factorial, prod

from algebra import inverse, inverse_is_two_sided, masks
from counts import exceptions, ordinary_count
from signatures import Profile, code, multiplicity, profiles, verdict, witness


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def packed(matrix):
    return ["".join("+" if v == 1 else "-" if v == -1 else "." if v == 0 else str(v) for v in row)
            for row in matrix]


def validate_witness(p, q, symbols, field):
    matrix = witness(p,q,symbols,field)
    inv = inverse(matrix,field)
    need(inv is not None, "constructed witness is singular")
    need(inverse_is_two_sided(matrix,inv,field), "two-sided inverse")
    need(masks(matrix,inv,p) == symbols, "literal witness has different masks")
    return matrix


def construction_grid():
    summaries, six = {}, {}
    for n in range(2,7):
        for p in range(1,n):
            q = n-p
            stats = {"profiles":0,"signatures":0,"binary_profiles":0,"binary_signatures":0,"field_witnesses":0}
            for v in profiles(n):
                if verdict(p,q,v) != "ok":
                    continue
                symbols = v.symbols()
                ways = multiplicity(symbols)
                stats["profiles"] += 1
                stats["signatures"] += ways
                rational = validate_witness(p,q,symbols,"Q")
                for field in ("F3","F4"):
                    validate_witness(p,q,symbols,field)
                stats["field_witnesses"] += 3
                reason = verdict(p,q,v,True)
                binary = None
                if reason == "ok":
                    binary = validate_witness(p,q,symbols,"F2")
                    stats["binary_profiles"] += 1
                    stats["binary_signatures"] += ways
                    stats["field_witnesses"] += 1
                if p == q == 3:
                    six[astuple(v)] = dict(multiplicity=ways, rational=packed(rational),
                                           binary=packed(binary) if binary else None, binary_verdict=reason)
            summaries[f"{p}+{q}"] = stats
    return summaries, six


def labeled_codes(p, q, binary=False):
    result = set()
    for v in profiles(p+q):
        if verdict(p,q,v,binary) == "ok":
            for word in set(permutations(v.symbols())):
                result.add(code(word))
    return result


def check_predecessor(package, retained):
    lines = (package/"source/3997-TERNARY-SCREEN.txt").read_text(encoding="ascii").splitlines()
    seen = set()
    for line in lines[1:]:
        fields = line.split()
        claimed = int(fields[0],16)
        vals = list(map(int,fields[1:]))
        need(len(vals) == 16 and set(vals) <= {-1,0,1}, "four-port receipt row")
        matrix = [vals[i:i+4] for i in range(0,16,4)]
        inv = inverse(matrix,"Q")
        need(inv is not None and code(masks(matrix,inv,2)) == claimed, "four-port receipt code")
        seen.add(claimed)
    binary = labeled_codes(2,2,True)
    need(len(seen) == len(lines)-1 == retained["necessary_set_size"] and
         seen == labeled_codes(2,2), "four-port rational codes")
    need(len(binary) == retained["gl4_f2_signatures"] == 355 and
         retained["predecessor_binding"]["receipt_codes"] == 439, "four-port field count")
    header = dict(word.split("=") for word in lines[0].split()[1:])
    need(int(header["binary_signatures"]) == 391, "rational zero-one domain")
    return {"actual_signed_witnesses":len(seen), "F2":len(binary),
            "rational_zero_one_predecessor":int(header["binary_signatures"])}


def check_count_formulas():
    grids = 0
    for n in range(2,14):
        factorial_n = factorial(n)
        ordinary = [0]*n
        losses = [{} for _ in range(n)]
        for v in profiles(n):
            mult = factorial_n // prod(factorial(k) for k in (v.aa,v.am,v.ma,v.bb,v.bm,v.mb,v.mm))
            for p in range(1,n):
                if verdict(p,n-p,v) != "ok":
                    continue
                ordinary[p] += mult
                reason = verdict(p,n-p,v,True)
                if reason != "ok":
                    losses[p][reason] = losses[p].get(reason,0) + mult
        for p in range(1,n):
            need(ordinary_count(p,n-p) == ordinary[p], "ordinary count formula differs")
            expected = exceptions(p,n-p)
            need(all(losses[p].get(k,0) == count for k,count in expected.items()), "exception count formula differs")
            grids += 1
    large = {}
    for d in (3,8,16,32):
        total = ordinary_count(d,d)
        excluded = exceptions(d,d)
        large[str(d)] = dict(ordinary=total, binary=total-sum(excluded.values()), excluded=excluded)
    return dict(exact_profile_grids=grids, balanced=large)


def rejection_controls():
    bad = ((1,1,(6,15),"Q"), (1,1,(9,15),"Q"), (1,1,(0,15),"Q"),
           (0,2,(5,10),"Q"), (2,1,(5,10),"Q"), (1,1,(15,15),"F2"),
           (2,2,(5,5,15,15),"Q"), (3,3,(7,7,13,13,15,15),"Q"))
    for params in bad:
        try:
            witness(*params)
        except ValueError:
            continue
        raise ValueError("impossible fixture unexpectedly constructed")
    return len(bad)


def worked_example():
    matrix = ((0,0,1,0,0,1), (0,0,0,1,0,1), (0,0,0,0,1,1),
              (1,0,0,0,0,0), (0,1,0,0,0,0), (0,0,1,1,1,1))
    symbols = (10,10,15,15,15,15)
    for field in ("Q","F3"):
        inv = inverse(matrix,field)
        need(inv is not None and masks(matrix,inv,3) == symbols, "six-port zero-one example")
    need(inverse(matrix,"F2") is None and verdict(3,3,Profile(0,0,0,2,0,0,4),True) == "binary one B",
         "six-port zero-one field distinction")
    return dict(matrix=packed(matrix), code=code(symbols), price=10)

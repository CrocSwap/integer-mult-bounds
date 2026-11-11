"""Independently certify non-silence for the literal #7277 public MOVE pairs."""

import argparse
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
from hashlib import sha256
from itertools import pairwise
import json
from math import isqrt
from pathlib import Path
from time import monotonic

WORD = "2c523ce6fdd6092d758fedc3602a0bcedb692b9766f1e41f903351ba4dee1756"
PRICE = "b98a469e5250a7644b6e81ade01eb896b5f91bca18465a3166217e03fa35a306"
HEAD = "ed090b57ed88f8859e5ff4643645099e6ba856ea"
MOD = 65521


def read(path,pin):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != pin:
        raise ValueError(f"Bad SHA-256 for {path.name}")
    return json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)


def space(basis):
    result = {0}
    for v in basis:
        assert v not in result
        result.update(v^x for x in list(result))
    return result


def inventory(word, frames):
    program, n = word["program"],word["public"]
    moves, contacts = defaultdict(list),defaultdict(list)
    for index,event in enumerate(program):
        tag, r, *args = event
        if tag == "MOVE":
            assert args[-1] == (r >= n)
            if r < n:
                moves[r].append(index)
        else:
            assert tag in ("ADD","COPY","SCALE","INIT","CLEAR")
            for v in (event[1:3] if tag in ("ADD","COPY") else event[1:2]):
                if v < n:
                    contacts[v].append(index)
    cases = {}
    for role, chain in moves.items():
        between = contacts[role]
        for left,right in pairwise(chain):
            a,b = program[left][2:4]
            mid,c = program[right][2:4]
            assert b == mid and frames[a] < frames[b] < frames[c]
            gap = between[bisect_right(between,left):bisect_left(between,right)]
            assert gap and all(program[t][0] in ("ADD","SCALE") for t in gap)
            cases[left,right] = {"role":role,"charts":[a,b,c],"contacts":gap}
    return moves,cases


def tariff_matching(moves, quotes):
    result = Fraction(0)
    for chain in moves.values():
        prefix = [Fraction(0)]*(len(chain)+1)
        for j in range(2,len(prefix)):
            weight = quotes[chain[j-2],chain[j-1]]
            prefix[j] = max(prefix[j-1],prefix[j-2]+weight)
        result += prefix[-1]
    return result


def coeff(raw):
    q = Fraction(raw)
    assert q and q.denominator % MOD
    return q.numerator*pow(q.denominator,-1,MOD)%MOD


def replay(word, frames, requested, deadline):
    n = word["public"]
    charts = list(word["initial"])+[None]*word["owned_fields"]
    values = [{r:1} for r in range(n)]+[None]*word["owned_fields"]
    fresh, owned = set(),set()
    proofs = {}
    hist = Counter()
    first_unvisited = None
    for i, event in enumerate(word["program"]):
        if i%64 == 0 and monotonic() >= deadline:
            first_unvisited = i
            break
        op,d,*args = event
        if op == "INIT":
            assert d >= n and charts[d] is None
            charts[d], values[d] = args[0],{}
            owned.add(d)
            fresh.add(d)
        elif op == "CLEAR":
            assert d in owned and charts[d] == args[0]
            charts[d], values[d] = None,None
            owned.remove(d)
            fresh.discard(d)
        elif op == "MOVE":
            a,b,flag = args
            assert charts[d] == a and flag == (d in owned) == (d >= n)
            assert frames[a] < frames[b] or (flag and frames[b] < frames[a])
            hist[abs(len(word["frames"][a])-len(word["frames"][b]))] += 1
            charts[d] = b
            fresh.discard(d)
        elif op == "SCALE":
            q,f = args
            assert charts[d] == f
            a = coeff(q)
            assert a
            if i in requested and values[d]:
                j = min(values[d])
                if (w := (a-1)*values[d][j]%MOD):
                    proofs[i] = [i,"scale_row",d,j,values[d][j],w]
            values[d] = {j:a*v%MOD for j,v in values[d].items()}
        else:
            assert op in ("ADD","COPY")
            s,q,f = args
            assert d != s and charts[d] == f == charts[s]
            a = coeff(q)
            if op == "COPY":
                assert d in owned and d in fresh and not values[d]
                values[d] = {}
            if i in requested and op == "ADD" and values[s]:
                j = min(values[s])
                if (w := a*values[s][j]%MOD):
                    proofs[i] = [i,"add_source",s,j,values[s][j],w]
            for j,v in values[s].items():
                x = (values[d].get(j,0)+a*v)%MOD
                if x:
                    values[d][j] = x
                else:
                    values[d].pop(j,None)
            fresh.discard(d)
    if first_unvisited is None:
        assert not owned and charts == word["final"]+[None]*word["owned_fields"]
    return proofs,first_unvisited,hist


def controls():
    word = {"public":1,"owned_fields":1,"frames":[[],[1],[1,2]],"initial":[0],"final":[2],
            "program":[["MOVE",0,0,1,False],["INIT",1,1],["ADD",0,1,"1/2",1],
                       ["SCALE",0,"3/2",1],["CLEAR",1,1],["MOVE",0,1,2,False]]}
    frames = list(map(space,word["frames"]))
    proofs,stop,hist = replay(word,frames,{2,3},monotonic()+1)
    assert stop is None and set(proofs) == {3}
    word["program"][2:2] = [["COPY",1,0,"1",1]]
    proofs,stop,hist = replay(word,frames,{3,4},monotonic()+1)
    assert stop is None and set(proofs) == {3,4}
    assert proofs[3][-1] == pow(2,-1,MOD)
    assert tariff_matching({0:[0,1,2,3]},{(0,1):2,(1,2):3,(2,3):2}) == 4
    return ["zero_source_does_not_certify_nonzero","scale_row_nonzero","add_witness_uses_denominator",
            "overlapping_middle_move_not_credited_twice"]


def main():
    start = monotonic()
    if not __debug__:
        raise RuntimeError("Assertions required")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--word",type=Path,required=True)
    parser.add_argument("--price",type=Path,required=True)
    parser.add_argument("--cap",type=float,default=42)
    args = parser.parse_args()
    assert 0 < args.cap <= 42 and all(MOD%d for d in range(2,isqrt(MOD)+1))
    word,price = read(args.word,WORD),read(args.price,PRICE)
    frames = list(map(space,word["frames"]))
    moves,cases = inventory(word,frames)
    literal_keys = {tuple(row["moves"]):row for row in price["records"]}
    assert len(cases) == len(literal_keys) == len(price["records"]) == 4732
    assert cases.keys() == literal_keys.keys()
    for key,item in cases.items():
        assert all(literal_keys[key][field] == value for field,value in item.items())
    matching = tariff_matching(moves,{k:Fraction(row["saving"][1]) for k,row in literal_keys.items()})
    assert matching == Fraction(price["whole_compatible_upper"])
    requested = {i for pair in cases.values() for i in pair["contacts"]}
    proofs,stop,hist = replay(word,frames,requested,start+args.cap)
    if stop is None:
        assert hist == {int(r):n for r,n in price["old_native_paid"].items()}
    pair_proofs = []
    unresolved = []
    for key,item in sorted(cases.items()):
        certificate = next((proofs[i] for i in item["contacts"] if i in proofs),None)
        if certificate is None:
            unresolved.append(key)
        else:
            pair_proofs.append([*key,certificate])
    receipt = {
        "head":HEAD,"word_sha256":WORD,"price_sha256":PRICE,"prime":MOD,
        "public_pairs":len(cases),"unique_contacts":len(requested),"nonzero_contact_count":len(proofs),
        "certified_pair_exclusions":len(pair_proofs),"unresolved_pairs":unresolved,
        "first_unvisited_literal_index":stop,"whole_compatible_upper_from_pinned_weights":str(matching),
        "proved_pair_witness_kinds":dict(Counter(p[2][1] for p in pair_proofs)),
        "pair_proofs":pair_proofs,"controls":controls(),
    }
    print(json.dumps(receipt,indent=2,sort_keys=True))


if __name__ == "__main__":
    main()

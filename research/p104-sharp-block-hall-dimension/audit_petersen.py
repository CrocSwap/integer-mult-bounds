#!/usr/bin/env python3
"""Independent exact rank-certificate checker; no numerical solver."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import gzip
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[1] / "research" / "p104-designer-toolkit-v2" / "words" / "5561.json.gz"
SOURCE_HASH = "b3701d78bee3661382ebe5414e678dfc9ee292e254cb9dc56339c2d2f45fdf44"
P = [61, 62, 63, 67, 68, 69, 95, 99, 100, 101]
I = [74, 81, 86, 91]

def require(condition, message):
    if not condition:
        raise ValueError(message)

def check_dual(certificate, ports):
    require(certificate["vertices"] == P, "certificate vertex order")
    full = (1 << len(P)) - 1
    result = Counter()
    rhs = Fraction(0)
    def add(S, a):
        result[S] += a
    for kind, entries in (("ub", certificate["ub"]), ("eq", certificate["eq"])):
        for descriptor, multiplier in entries:
            a = Fraction(multiplier)
            if kind == "ub":
                require(a <= 0, "inequality multiplier sign")
            tag, *args = descriptor
            if tag == "empty":
                require(kind == "eq" and not args, "empty equality")
                add(0, a)
                continue
            require(len(args) in (2, 3), "row arity")
            S, i, *tail = args
            require(isinstance(S, int) and 0 <= S <= full, "subset mask")
            require(isinstance(i, int) and 0 <= i < len(P), "vertex index")
            b = 1 << i
            require(not S & b, "vertex must be outside subset")
            if tag == "mono":
                require(kind == "ub" and not tail, "monotonicity row")
                add(S, a)
                add(S | b, -a)
            elif tag == "submod":
                require(kind == "ub" and len(tail) == 1, "submodularity row")
                j = tail[0]
                require(isinstance(j, int) and 0 <= j < len(P) and j != i, "second vertex index")
                c = 1 << j
                require(not S & c, "second vertex must be outside subset")
                add(S, a)
                add(S | b | c, a)
                add(S | b, -a)
                add(S | c, -a)
            elif tag == "zero":
                require(kind == "eq" and not tail, "zero row")
                for j in range(len(P)):
                    if S & (1 << j):
                        require((ports[P[i]] & ports[P[j]]).bit_count() % 2 == 0,
                                "zero row uses an allowed contact")
                add(S | b, a)
                add(S, -a)
                rhs += a
            else:
                raise ValueError("unknown rank axiom")
    require({S: a for S, a in result.items() if a} == {full: Fraction(1)},
            "rank coefficients fail exact identity")
    require(rhs == 5, "right hand side is not 5k")

def rejected(operation, label):
    try:
        operation()
    except ValueError:
        return label
    raise ValueError("negative control accepted: " + label)

def main():
    source = SOURCE.read_bytes()
    require(hashlib.sha256(source).hexdigest() == SOURCE_HASH, "source hash")
    ports = json.loads(gzip.decompress(source))["ports"]
    require(len(ports) == 104 and len(set(ports)) == 104, "source port count")
    require(all(isinstance(p, int) and 0 < p < 512 and p.bit_count() % 2 for p in ports), "source format")
    zero = lambda s, t: s != t and (ports[s] & ports[t]).bit_count() % 2 == 0
    require(all(zero(s, t) for s, t in itertools.combinations(I, 2)), "isolates mutually zero")
    require(all(zero(s, t) for s in I for t in P), "isolate/core contacts")
    require([v for v in range(104) if all(zero(v, i) for i in I)] == P, "common zero neighborhood")
    edges = {frozenset((s, t)) for s, t in itertools.combinations(P, 2) if not zero(s, t)}
    require(len(edges) == 15 and all(sum(v in e for e in edges) == 3 for v in P), "core graph")
    cert = json.loads((HERE / "petersen-dual.json").read_text())
    check_dual(cert, ports)
    def match(rest):
        if not rest:
            return []
        s = rest[0]
        for t in rest[1:]:
            if frozenset((s, t)) in edges:
                tail = match([x for x in rest if x not in (s, t)])
                if tail is not None:
                    return [(s, t)] + tail
        return None
    matching = match(P)
    require(matching is not None and len(matching) == 5, "perfect matching")
    groups = [(i,) for i in I] + matching
    coord = {v: c for c, group in enumerate(groups) for v in group}
    require(len(coord) == 14, "upper witness coverage")
    for s, t in itertools.product(I + P, repeat=2):
        gram = int(coord[s] == coord[t])
        if s == t:
            require(gram == 1, "upper witness diagonal")
        elif zero(s, t):
            require(gram == 0, "upper witness zero")
    basis = {}
    for value in ports:
        while value:
            bit = value.bit_length() - 1
            if bit in basis:
                value ^= basis[bit]
            else:
                basis[bit] = value
                break
    require(len(basis) == 9, "full F2 source span")
    controls = []
    bad = deepcopy(cert)
    bad["ub"][0][1] = "1/2"
    controls.append(rejected(lambda: check_dual(bad, ports), "reversed inequality"))
    bad = deepcopy(cert)
    bad["ub"].pop()
    controls.append(rejected(lambda: check_dual(bad, ports), "missing inequality"))
    bad = deepcopy(cert)
    row = next(x for x in bad["eq"] if x[0][0] == "zero")
    i = row[0][2]
    j = next(j for j in range(10) if j != i and not zero(P[i], P[j]))
    row[0][1] = 1 << j
    controls.append(rejected(lambda: check_dual(bad, ports), "false zero contact"))
    bad = deepcopy(cert)
    bad["eq"][-1][1] = "3/2"
    controls.append(rejected(lambda: check_dual(bad, ports), "altered equality weight"))
    print(json.dumps({"source_sha256": SOURCE_HASH, "core_lower_bound": "5k", "full_lower_bound": "9k",
                      "subset_upper_bound": "9k", "matching": matching, "full_F2_minimum": "9k",
                      "negative_controls_rejected": controls}, indent=2))
    print("PASS_P104_PETERSEN_EXACT_RANK_PROOF")

if __name__ == "__main__":
    main()

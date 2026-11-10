#!/usr/bin/env python3
"""Exhaustive corroboration of the closed form for E8 port counts.

Python 3.12, standard library only.  Run from the repository root:

    python3.12 -I -B -W error research/p104-e8-port-count-closed-form/verify.py

Marker: PASS_P104_E8_PORT_COUNT_CLOSED_FORM

Every subspace of F2^9 is visited once: X in reduced echelon form with
dim X <= 4, and its dot-product orthogonal V = X^perp of dimension >= 5.
For each one the port count, both character sums and the radical of the
polar form are computed from their definitions, and the clauses of
Theorems 1-3 of PROOF.md are required.  The resulting class census must
equal CENSUS.json.  `--write-census PATH` regenerates that file.
"""
import gzip
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
PORTS_FILE = HERE.parent / "p104-designer-toolkit-v2" / "words" / "5561.json.gz"
CENSUS_FILE = HERE / "CENSUS.json"
MARKER = "PASS_P104_E8_PORT_COUNT_CLOSED_FORM"
SIZE = 512
ONE = SIZE - 1
MAX_SMALL_DIM = 4
NODE_BUDGET = 4_141_729  # subspaces of F2^9 of dimension 0..4
SAMPLE_STRIDE = 4001

WT = [bin(x).count("1") for x in range(SIZE)]
PAR = [w & 1 for w in WT]
Q = [(w * (w - 1) // 2) & 1 for w in WT]
QP = [Q[x] ^ PAR[x] for x in range(SIZE)]
TAU = [x ^ (ONE if PAR[x] else 0) for x in range(SIZE)]
SQ = [1 - 2 * v for v in Q]
SQP = [1 - 2 * v for v in QP]
PORT = [PAR[x] & Q[x] for x in range(SIZE)]
P120 = [x for x in range(SIZE) if PORT[x]]


def require(ok, msg):
    if not ok:
        raise ValueError(msg)


def mask_of(vectors):
    return sum(1 << x for x in vectors)


M120 = mask_of(P120)
MQ = mask_of(x for x in range(SIZE) if Q[x])
MQP = mask_of(x for x in range(SIZE) if QP[x])
MODD = mask_of(x for x in range(SIZE) if PAR[x])
PERP = [mask_of(x for x in range(SIZE) if not WT[x & y] & 1) for y in range(SIZE)]


def polar(x, y):
    return (WT[x] * WT[y] + WT[x & y]) & 1


def check_form_facts():
    """The setting of PR 6861 plus the two identities the proof uses."""
    pairs = [(x, y) for x in range(SIZE) for y in range(SIZE)]
    require(all(Q[x ^ y] == Q[x] ^ Q[y] ^ polar(x, y) for x, y in pairs), "q polarises to B")
    require(all(polar(x, y) == WT[x & TAU[y]] & 1 for x, y in pairs), "B(x,y) = x.tau(y)")
    radical = [x for x in range(SIZE) if all(polar(x, y) == 0 for y in range(SIZE))]
    require(radical == [0, ONE] and Q[ONE] == 0 and PAR[ONE] == 1, "radical is <1>, q(1)=0, 1 odd")
    require(all(TAU[x ^ y] == TAU[x] ^ TAU[y] for x, y in pairs), "tau is linear")
    require([x for x in range(SIZE) if TAU[x] == 0] == [0, ONE], "kernel of tau is <1>")
    require(len(P120) == 120 and all(WT[x] in (3, 7) for x in P120), "P120 is weight 3 or 7")
    require(sum(SQ) == 32, "sum of (-1)^q over F2^9 is 32")


def sign(value):
    return (value > 0) - (value < 0)


def clauses(e, delta, radical, sig, sigp, ports):
    """Require Theorems 1-3 for one subspace not inside E; return its class."""
    rho = len(radical).bit_length() - 1
    require(len(radical) == 1 << rho, "radical size is a power of two")
    a = int(all(Q[y] == 0 for y in radical))
    ap = int(all(QP[y] == 0 for y in radical))
    total = e + rho
    require(total % 2 == 0 and total <= 8 + 2 * delta, "Theorem 2(a)")
    require(sig * sig == a << total and sigp * sigp == ap << total, "Theorem 1 squares")
    require(not (delta and ap), "Theorem 2(b)")
    require(not (total == 8 + 2 * delta and a) or sig == 1 << (4 + delta), "Theorem 2(c)")
    require(4 * ports == (1 << e) + sigp - sig, "Theorem 1 count")
    require(4 * ports <= (1 << e) + 16 and 2 * ports <= 1 << e, "Theorem 3 bound")
    require(e != 8 or ports <= 64, "Theorem 3 at dimension 8")
    return (e, delta, rho, sign(sig), sign(sigp), ports)


def small_record(k, elems, vmask):
    """Invariants of X (dimension k) from its element list; None inside E."""
    if not any(PAR[x] for x in elems):
        return None
    radical = [y for y in elems if (vmask >> TAU[y]) & 1]
    sig = sum(SQ[x] for x in elems)
    sigp = sum(SQP[x] for x in elems)
    ports = sum(PORT[x] for x in elems)
    return (k, int(ONE in elems), radical, sig, sigp, ports)


def dual_record(k, elems, vmask):
    """Invariants of V = X^perp (dimension 9-k) from its mask; None inside E."""
    if not vmask & MODD:
        return None
    radical = []
    for z in elems:
        if PAR[z]:
            continue
        if (vmask >> z) & 1:
            radical.append(z)
        if (vmask >> (z ^ ONE)) & 1:
            radical.append(z ^ ONE)
    size = 1 << (9 - k)
    sig = size - 2 * (vmask & MQ).bit_count()
    sigp = size - 2 * (vmask & MQP).bit_count()
    return (9 - k, (vmask >> ONE) & 1, radical, sig, sigp, (vmask & M120).bit_count())


def children(minp, pivmask):
    """Echelon rows that extend a basis whose smallest pivot is minp."""
    rows = []
    for p in range(minp):
        cands = [1 << p]
        for c in range(p + 1, 9):
            if not (pivmask >> c) & 1:
                cands += [v | (1 << c) for v in cands]
        rows.append((p, cands))
    return rows


def basis_of(vectors):
    """Greedy basis of the span of at most 512 vectors."""
    basis, span = [], {0}
    for v in vectors[:SIZE]:
        if v not in span:
            basis.append(v)
            span |= {v ^ s for s in span}
    return basis, span


def direct_record(vectors):
    """The same invariants from first principles, without masks or tau."""
    basis, span = basis_of(vectors)
    require(span == set(vectors), "vectors form a subspace")
    if all(WT[x] % 2 == 0 for x in vectors):
        return None
    radical = sorted(y for y in vectors if all(polar(y, b) == 0 for b in basis))
    sig = sum(1 if (WT[x] * (WT[x] - 1) // 2) % 2 == 0 else -1 for x in vectors)
    sigp = sum(1 if (WT[x] * (WT[x] + 1) // 2) % 2 == 0 else -1 for x in vectors)
    ports = sum(1 for x in vectors if WT[x] in (3, 7))
    return (len(basis), int(ONE in span), radical, sig, sigp, ports)


def cross_check(record, vectors):
    direct = direct_record(vectors)
    if record is None or direct is None:
        require(record is None and direct is None, "even-hyperplane test agrees")
        return
    fast = record[:2] + (sorted(record[2]),) + record[3:]
    require(fast == direct, "mask invariants equal first-principles invariants")


def elements_of(mask):
    return [x for x in range(SIZE) if (mask >> x) & 1]


def census(m104):
    """Visit all 8,283,458 subspaces; return classes, node counts, witnesses."""
    classes, nodes, even, sampled = Counter(), [0] * (MAX_SMALL_DIM + 1), 0, 0
    witnesses = {}
    stack = [(0, 9, 0, [0], (1 << SIZE) - 1)]
    visited = 0
    while stack:
        k, minp, pivmask, elems, vmask = stack.pop()
        visited += 1
        require(visited <= NODE_BUDGET, "node budget exceeded")
        nodes[k] += 1
        small, dual = small_record(k, elems, vmask), dual_record(k, elems, vmask)
        if k <= 1 or visited % SAMPLE_STRIDE == 0:
            cross_check(small, elems)
            cross_check(dual, elements_of(vmask))
            sampled += 2
        for record, mask in ((small, None), (dual, vmask)):
            if record is None:
                even += 1
                continue
            key = clauses(*record)
            classes[key] += 1
            e = key[0]
            if e <= 7 and e not in witnesses and 4 * key[5] == min(2 << e, (1 << e) + 16):
                own = mask_of(elems) if mask is None else mask
                if (own & m104).bit_count() == key[5]:
                    witnesses[e] = basis_of(elements_of(own))[0]
        if k < MAX_SMALL_DIM:
            for p, cands in children(minp, pivmask):
                grown = pivmask | (1 << p)
                for b in cands:
                    stack.append((k + 1, p, grown, elems + [x ^ b for x in elems], vmask & PERP[b]))
    return classes, nodes, even, sampled, witnesses


def summarize(classes, nodes, even, witnesses):
    rows = [
        {"dimension": e, "contains_all_ones": d, "radical_dimension": r, "sign_sigma": s,
         "sign_sigma_prime": sp, "ports": n, "subspaces": count}
        for (e, d, r, s, sp, n), count in sorted(classes.items())
    ]
    best = {e: max(row["ports"] for row in rows if row["dimension"] == e) for e in range(1, 10)}
    attaining = {
        e: sum(row["subspaces"] for row in rows if row["dimension"] == e and row["ports"] == best[e])
        for e in range(1, 10)
    }
    return {
        "schema_version": 1,
        "subspaces_total": 2 * sum(nodes),
        "subspaces_inside_even_hyperplane": even,
        "small_subspaces_by_dimension": nodes,
        "classes": rows,
        "max_ports_by_dimension": {str(e): best[e] for e in best},
        "maximizers_by_dimension": {str(e): attaining[e] for e in attaining},
        "p104_witness_bases": {str(e): witnesses[e] for e in sorted(witnesses)},
    }


def check_summary(doc):
    """Statements of Theorem 3 and Corollary 4 read off the census."""
    require(doc["small_subspaces_by_dimension"] == [1, 511, 43435, 788035, 3309747], "Gaussian binomials")
    require(doc["subspaces_total"] == 8_283_458 and doc["subspaces_inside_even_hyperplane"] == 417_199, "totals")
    counted = sum(row["subspaces"] for row in doc["classes"])
    require(counted + doc["subspaces_inside_even_hyperplane"] == doc["subspaces_total"], "census is complete")
    best = [doc["max_ports_by_dimension"][str(e)] for e in range(1, 10)]
    require(best == [1, 2, 4, 8, 12, 20, 36, 64, 120], "N_e table")
    require(all(best[e - 1] == min(1 << (e - 1), (1 << (e - 2)) + 4) for e in range(2, 8)), "closed form")
    for row in doc["classes"]:
        e, total = row["dimension"], row["dimension"] + row["radical_dimension"]
        s, sp, d = row["sign_sigma"], row["sign_sigma_prime"], row["contains_all_ones"]
        require(4 * row["ports"] == (1 << e) + (sp - s) * (1 << (total // 2)), "class formula")
        equality = (
            (d == 1 and total == 8 and s == -1)
            or (d == 0 and total == 8 and s == 0 and sp == 1)
            or (d == 0 and total == 6 and s == -1 and sp == 1)
        )
        require(equality == (4 * row["ports"] == (1 << e) + 16), "equality classification")


def span_of(basis):
    span = [0]
    for b in basis[:9]:
        span += [x ^ b for x in span]
    return span


def check_witnesses(doc, p104):
    """One explicit subspace per dimension 1..7 attains the bound inside P104."""
    ports = set(p104)
    for e in range(1, 8):
        basis = doc["p104_witness_bases"][str(e)]
        span = span_of(basis)
        require(len(basis) == e and len(set(span)) == 1 << e, "witness has dimension e")
        target = min(1 << (e - 1), (1 << (e - 2)) + 4) if e > 1 else 1
        require(sum(1 for x in span if x in ports) == target, "witness attains the bound in P104")
        require(sum(PORT[x] for x in span) == target, "witness attains the bound in P120")


def expect_failure(action, label):
    try:
        action()
    except ValueError:
        return
    raise ValueError("control did not reject: " + label)


def run_controls(doc, p104):
    radical = [0, ONE]
    require(clauses(9, 1, radical, 32, 0, 120) == (9, 1, 1, 1, 0, 120), "whole space is accepted")
    expect_failure(lambda: clauses(9, 1, radical, 32, 0, 121), "wrong port count")
    expect_failure(lambda: clauses(9, 1, [0], 32, 0, 120), "wrong radical")
    expect_failure(lambda: clauses(9, 1, radical, -32, 0, 136), "negative sign at full radical")
    mutated = json.loads(json.dumps(doc))
    mutated["classes"][0]["ports"] += 1
    expect_failure(lambda: check_summary(mutated), "mutated class row")
    basis = doc["p104_witness_bases"]["7"]
    dropped = next(x for x in span_of(basis) if x in set(p104))
    expect_failure(lambda: check_witnesses(doc, [x for x in p104 if x != dropped]), "port removed from witness")


def load_p104():
    with gzip.open(PORTS_FILE) as handle:
        p104 = json.load(handle)["ports"]
    require(len(p104) == 104 and len(set(p104)) == 104 and set(p104) <= set(P120), "P104 inside P120")
    return p104


def main(argv):
    require(len(argv) in (1, 3) and (len(argv) == 1 or argv[1] == "--write-census"), "usage")
    check_form_facts()
    p104 = load_p104()
    classes, nodes, even, sampled, witnesses = census(mask_of(p104))
    doc = summarize(classes, nodes, even, witnesses)
    check_summary(doc)
    check_witnesses(doc, p104)
    run_controls(doc, p104)
    if len(argv) == 3:
        Path(argv[2]).write_text(json.dumps(doc, indent=1) + "\n")
        print("WROTE", argv[2])
        return 0
    require(json.loads(CENSUS_FILE.read_text()) == doc, "census equals CENSUS.json")
    print(json.dumps({"subspaces": doc["subspaces_total"], "classes": len(doc["classes"]),
                      "first_principles_samples": sampled,
                      "max_ports": doc["max_ports_by_dimension"],
                      "maximizers": doc["maximizers_by_dimension"]}, sort_keys=True))
    print(MARKER)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

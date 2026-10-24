#!/usr/bin/env python3
"""Exact finite checks supporting README's uniform proof; no word census."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    return tuple(1 << i for i in range(n))


def add(a, b):
    return tuple(x ^ y for x, y in zip(a, b, strict=True))


def multiply(a, b):
    out = []
    for row in a:
        value = 0
        for i, other in enumerate(b):
            if row >> i & 1:
                value ^= other
        out.append(value)
    return tuple(out)


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = row
                break
            row ^= pivots[pivot]
    return len(pivots)


def cnot(n, i, j):
    need(0 <= i < n and 0 <= j < n and i != j, "invalid coordinate CNOT")
    rows = list(identity(n))
    rows[i] ^= 1 << j
    return tuple(rows)


def projectors(r):
    return [tuple(y if x >> i & 1 else 0 for i in range(r))
            for x in range(1, 1 << r) for y in range(1, 1 << r)
            if (x & y).bit_count() % 2]


def put(poly, label, coefficient):
    value = add(poly.get(label, (0,) * len(coefficient)), coefficient)
    if any(value):
        poly[label] = value
    else:
        poly.pop(label, None)


def factor(label, coupling):
    need(rank(coupling) == 1 and multiply(coupling, coupling) == coupling,
         "paid coupling must be a rank-one idempotent")
    out = {}
    put(out, identity(len(label)), add(identity(len(coupling)), coupling))
    put(out, label, coupling)
    return out


def formal_multiply(left, right):
    out = {}
    for g, a in left.items():
        for h, b in right.items():
            put(out, multiply(g, h), multiply(a, b))
    return out


def formal_word(n, r, calls):
    out = {identity(n): identity(r)}
    for label, coupling in calls:
        out = formal_multiply(factor(label, coupling), out)
    return out


def natural(poly, n, r):
    """Address-major blocks; coefficient matrices act on scalar roles."""
    rows = [0] * (n * r)
    for label, coefficient in poly.items():
        for i in range(n):
            for j in range(n):
                if label[i] >> j & 1:
                    for u in range(r):
                        rows[i * r + u] ^= coefficient[u] << (j * r)
    return tuple(rows)


def row_update(before, r, i, j, coupling):
    after = list(before)
    update = multiply(coupling, before[j * r:(j + 1) * r])
    for u in range(r):
        after[i * r + u] ^= update[u]
    return tuple(after)


def check_row_budget():
    transitions = row_bounds = single_write_checks = 0
    for r in range(2, 6):
        choices = projectors(r)
        for n in range(2, 7):
            initial = identity(n * r)
            for sample in range(8):
                state = initial
                counts = [0] * n
                for t in range(8):
                    i = (sample + t) % n
                    j = (i + 1 + (t // n) % (n - 1)) % n
                    coupling = choices[(13 * sample + 17 * t + n) % len(choices)]
                    after = row_update(state, r, i, j, coupling)
                    gate = natural(factor(cnot(n, i, j), coupling), n, r)
                    need(after == multiply(gate, state), "row-update convention")
                    need(multiply(gate, after) == state, "paid gate is involutive")
                    need(rank(after) == n * r, "prefix must be invertible")
                    counts[i] += 1
                    for address in range(n):
                        block = slice(address * r, (address + 1) * r)
                        delta_rank = rank(add(after[block], initial[block]))
                        need(delta_rank <= counts[address], "row-write rank budget")
                        row_bounds += 1
                        if counts[address] == 1:
                            need(delta_rank == 1, "a single write cannot restore a row")
                            single_write_checks += 1
                    state = after
                    transitions += 1
    return dict(transitions=transitions, row_bounds=row_bounds,
                single_write_checks=single_write_checks)


def projection(g):
    return g[0] & 3, g[1] & 3


def parabolic(n):
    for a in itertools.product(range(4), repeat=2):
        if rank(a) == 2:
            for b in itertools.product(range(1 << (n - 2)), repeat=2):
                yield (a[0] | b[0] << 2, a[1] | b[1] << 2, *identity(n)[2:])


def check_projection():
    products = labels = 0
    sizes = {}
    for n in (3, 4):
        group = set(parabolic(n))
        sizes[str(n)] = len(group)
        for g in group:
            for h in group:
                gh = multiply(g, h)
                need(gh in group, "parabolic subgroup closure")
                need(projection(gh) == multiply(projection(g), projection(h)),
                     "parabolic projection must preserve products")
                products += 1
    for n in range(2, 9):
        for i in (0, 1):
            for j in range(n):
                if i != j:
                    expected = cnot(2, i, j) if j < 2 else identity(2)
                    need(projection(cnot(n, i, j)) == expected, "projected label")
                    labels += 1
    g, h = cnot(3, 0, 2), cnot(3, 2, 1)
    need(projection(multiply(g, h)) != multiply(projection(g), projection(h)),
         "control: projection is NOT a homomorphism on all GL_n")
    return dict(group_sizes=sizes, products=products, labels=labels,
                outside_subgroup_counterexample=1)


def check_count_budget():
    candidates = admissible = 0
    for n in range(2, 9):
        for k in range(6):
            for writes in itertools.combinations_with_replacement(range(n), k):
                counts = tuple(writes.count(i) for i in range(n))
                candidates += 1
                if counts[0] >= 2 and counts[1] >= 2 and all(c != 1 for c in counts[2:]):
                    need(not any(counts[2:]), "five-call budget permits no spectator writes")
                    admissible += 1
    need(admissible == 21, "bounded count-vector fixture changed")
    boundary = (2, 2, 2)
    need(sum(boundary) == 6 and all(c >= 2 for c in boundary),
         "six-call boundary allows a spectator; no shortest-word classification")
    return dict(count_vectors=candidates, admissible=admissible,
                six_call_boundary=list(boundary))


def direct_word(n, r):
    return [(cnot(n, i, j), tuple(1 << role if u == role else 0 for u in range(r)))
            for role in (0, 1) for i, j in ((0, 1), (1, 0), (0, 1))]


def target(n, r):
    swap = list(identity(n))
    swap[0], swap[1] = swap[1], swap[0]
    active = (1, 2, *((0,) * (r - 2)))
    out = {}
    put(out, identity(n), add(identity(r), active))
    put(out, tuple(swap), active)
    return out


def check_endpoints():
    witnesses = omissions = dirty_faults = 0
    for n in range(2, 7):
        for r in range(2, 6):
            calls = direct_word(n, r)
            expected = target(n, r)
            need(formal_word(n, r, calls) == expected, "six-call formal endpoint")
            need(formal_word(n, r, reversed(calls)) == expected, "reverse formal endpoint")
            image = natural(expected, n, r)
            for i in range(n):
                block = slice(i * r, (i + 1) * r)
                need(rank(add(image[block], identity(n * r)[block])) == (2 if i < 2 else 0),
                     "target row ranks")
            mixing = cnot(r, 0, 1)
            conjugated = [(g, multiply(mixing, multiply(p, mixing))) for g, p in calls]
            need(formal_word(n, r, conjugated) == expected, "free scalar conjugation")
            witnesses += 1
            for deleted in range(6):
                need(formal_word(n, r, calls[:deleted] + calls[deleted + 1:]) != expected,
                     "omitted paid call accepted")
                omissions += 1
            if n >= 3 and r >= 3:
                dirty_projector = (0, 0, 4, *((0,) * (r - 3)))
                damaged = formal_word(n, r, calls + [(cnot(n, 2, 0), dirty_projector)])
                need(damaged != expected, "unrestored dirty role accepted")
                data_columns = sum(3 << (address * r) for address in range(n))
                need(all((x ^ y) & data_columns == 0
                         for x, y in zip(natural(damaged, n, r), image, strict=True)),
                     "dirty-only fault must evade restricted clean-input testing")
                dirty_faults += 1
    try:
        factor(cnot(2, 0, 1), identity(2))
    except ValueError as error:
        need(str(error) == "paid coupling must be a rank-one idempotent", "wrong rejection")
    else:
        raise ValueError("rank-two paid coupling accepted")
    # If rank-two couplings were unit price, three pure-label factors would suffice.
    forbidden = {identity(2): identity(2)}
    for i, j in ((0, 1), (1, 0), (0, 1)):
        forbidden = formal_multiply({cnot(2, i, j): identity(2)}, forbidden)
    need(forbidden == target(2, 2), "changed-alphabet three-call control")
    alias = {g: (1,) for g in itertools.product(range(4), repeat=2) if rank(g) == 2}
    need(len(alias) == 6 and natural(alias, 2, 1) == (0, 0),
         "nonzero formal element with zero natural image")
    return dict(formal_witnesses=witnesses, reverse_witnesses=witnesses,
                scalar_conjugations=witnesses, omission_rejections=omissions,
                dirty_only_fault_rejections=dirty_faults,
                rank_two_tariff_control=1, natural_alias_control=1)


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    checked = {}
    for entry in sources["files"]:
        if entry["usage"] == "input":
            raw = (ROOT / entry["path"]).read_bytes()
            digest = hashlib.sha256(raw).hexdigest()
            need(digest == entry["sha256"], "source SHA256 mismatch: " + entry["path"])
            blob = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
            need(blob == entry["git_blob"], "source Git blob mismatch: " + entry["path"])
            checked[entry["path"]] = digest
    need(len(checked) == 4, "expected four proof/model sources")
    return checked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print recomputed finite evidence")
    args = parser.parse_args()
    result = dict(sources=authenticate(), row_budget=check_row_budget(),
                  projection=check_projection(), count_budget=check_count_budget(),
                  endpoints=check_endpoints())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("PASS_TWO_SWAP_ADDRESS_SPECTATORS finite_checks=passed "
              "uniform_minimum=6_by_written_proof no_new_kappa")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Independent forward integer-dyadic replay; no predecessor executable imports.

Apache-2.0. Prepared by Ross Richardson with OpenAI Codex assistance.
Rows are sparse integer vectors divided by a power of two.  Construct the
invocation reader by forward execution, then remove prefix gates in chronological
order using right multiplication by their inverses.  The primary checker uses
reverse Fraction covectors instead.
"""
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
ARCHIVE = ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"
BASE = "candidate/strict/global/base/providers/gauge44/"
PINS = {
    "CANONICAL-WORD.json.gz": "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219",
    "LOCAL-PROGRAMS.json.gz": "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def reduced(values, exponent):
    values = {j: a for j, a in values.items() if a}
    if not values:
        return {}, 0
    while exponent and all(a % 2 == 0 for a in values.values()):
        values = {j: a // 2 for j, a in values.items()}
        exponent -= 1
    return values, exponent


def coefficient(n, d):
    require(isinstance(n, int) and isinstance(d, int) and d != 0, "bad coefficient")
    if d < 0:
        n, d = -n, -d
    require(d & (d - 1) == 0, "nondyadic coefficient")
    return n, d.bit_length() - 1


def scaled(row, n, d):
    n, shift = coefficient(n, d)
    values, exponent = row
    return reduced({j: n * a for j, a in values.items()}, exponent + shift)


def added(target, source, n, d):
    left, a = target
    right, b = scaled(source, n, d)
    exponent = max(a, b)
    out = {j: x << (exponent - a) for j, x in left.items()}
    for j, y in right.items():
        out[j] = out.get(j, 0) + (y << (exponent - b))
    return reduced(out, exponent)


def forward(gates, size):
    rows = [({j: 1}, 0) for j in range(size)]
    for gate in gates:
        kind, target = gate[:2]
        if kind == "add":
            _, _, source, n, d, _ = gate
            require(target != source, "self addition")
            rows[target] = added(rows[target], rows[source], n, d)
        elif kind == "scale":
            _, _, n, d, _ = gate
            require(n != 0, "singular scale")
            rows[target] = scaled(rows[target], n, d)
        else:
            raise ValueError("unexpected scalar gate")
    return rows


def right_inverse(reader, gate):
    """R at cut k -> R at cut k+1. ADD t+=q*s changes column s by -q*t."""
    result = []
    kind, target = gate[:2]
    for values, exponent in reader:
        if kind == "add":
            _, _, source, n, d, _ = gate
            delta = ({source: values.get(target, 0)}, exponent)
            result.append(added((values, exponent), delta, -n, d))
        elif kind == "scale":
            _, _, n, d, _ = gate
            # Replace just the target column by (d/n) times itself.
            replacement = scaled(({target: values.get(target, 0)}, exponent), d, n)
            without = ({j: x for j, x in values.items() if j != target}, exponent)
            result.append(added(without, replacement, 1, 1))
        else:
            raise ValueError("unexpected inverse gate")
    return result


def integer_rows(rows, size):
    require(all(e == 0 for _, e in rows), "reader endpoint is not integral")
    return [[r.get(j, 0) for j in range(size)] for r, _ in rows]


def gram(dense):
    return [[sum(a * b for a, b in zip(r, s)) for s in dense] for r in dense]


def paired_cycles():
    for p in itertools.permutations(range(8)):
        unseen = set(range(8))
        lengths = []
        while unseen:
            v = min(unseen)
            length = 0
            while v in unseen:
                unseen.remove(v)
                length += 1
                v = p[v]
            lengths.append(length)
        if sorted(lengths) == [4, 4]:
            yield p


def checks():
    raw = ARCHIVE.read_bytes()
    require(hashlib.sha256(raw).hexdigest() ==
            "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6", "archive drift")
    with tarfile.open(ARCHIVE) as archive:
        source = {}
        for name, pin in PINS.items():
            data = archive.extractfile(BASE + name).read()
            require(hashlib.sha256(data).hexdigest() == pin, "member drift: " + name)
            source[name] = json.loads(gzip.decompress(data))
    word = source["CANONICAL-WORD.json.gz"]
    program = source["LOCAL-PROGRAMS.json.gz"]["forward"]
    prefix = word["precondition"] + word["compensation"]
    size = len(word["start"])
    require(size == 704 and len(prefix) == 7400 and len(word["A"]) == 3451, "dimensions")
    require(program[0] == ["phase", "zero_frame_precondition"] and
            program[7401] == ["phase", "entry_adapters"] and
            program[8106] == ["phase", "A"] and
            program[12550] == ["phase", "centers"], "phase boundaries")

    def emitted(g):
        if g[0] == "add":
            return ["scalar", ["add", ["L", g[1]], ["L", g[2]], g[3], g[4]], g[5]]
        return ["scalar", ["scale", ["L", g[1]], g[2], g[3]], g[4]]

    require(program[1:7401] == [emitted(g) for g in prefix], "prefix source/emission disagreement")
    require([e for e in program[8107:12550] if e[0] == "scalar"] ==
            [emitted(g) for g in word["A"]], "A source/emission disagreement")
    targets = {g[1] for g in prefix}
    touched = targets | {g[2] for g in prefix if g[0] == "add"}
    entry = program[7402:8106]
    require(len(entry) == size and {e[2] for e in entry} == set(range(size)), "entry coverage")
    require(all(e[3] == word["start"][e[2]] for e in entry), "entry frame mismatch")
    residual = {e[2] for e in entry if e[0] == "residual_adapter"}
    ordinary = {e[2] for e in entry if e[0] == "adapter" and e[1] == "old_to_new"}
    require(len(residual) == 240 and len(ordinary) == 464, "adapter counts")
    require(targets == set(range(112, 224)), "write support")
    require(len(touched) == 352 and touched <= ordinary and not touched & residual,
            "prefix touches a residual wrapper")
    require(all(word["start"][j] == 0 for j in touched), "prefix start frame")

    # Independent forward construction at both endpoint cuts, with all dirty bases.
    a_full = forward(word["A"], size)
    invocation_full = forward(prefix + word["A"], size)
    reader = [a_full[j] for j in word["centers"]]
    invocation = [invocation_full[j] for j in word["centers"]]
    require(invocation == reader, "forward invocation reader differs")
    require(all(not (targets & values.keys()) for values, _ in reader), "written column not annihilated")
    dense = integer_rows(reader, size)
    reference_bytes = (HERE / "inputs/PR2491-RESULT.json").read_bytes()
    require(hashlib.sha256(reference_bytes).hexdigest() ==
            "8c4cfe3caaf745e9b2516b5583494c808fc435e8e00d1b8711c17c75ef29d5b3",
            "predecessor certificate drift")
    reference = json.loads(reference_bytes)
    require(dense == [[int(x) for x in row] for row in reference["reader"]],
            "independent complete reader differs from predecessor certificate")
    g = gram(dense)
    norms = [g[i][i] for i in range(8)]
    require(norms == [150, 130, 146, 134, 122, 126, 142, 146], "norm diagonal")

    current = invocation
    for k, gate in enumerate(prefix, 1):
        current = right_inverse(current, gate)
        require(current == reader, "reader changed at cut " + str(k))
    permutations = list(paired_cycles())
    require(len(permutations) == 1260, "cycle census")
    witnesses = [next((i for i in range(8) if norms[i] != norms[p[i]]), None)
                 for p in permutations]
    require(all(w is not None for w in witnesses), "cycle survived norm condition")

    # Omission control: clean-data-only calculation loses the obstruction.
    data_gram = gram([row[:112] for row in dense])
    require(data_gram == [[56 * (i == j) for j in range(8)] for i in range(8)], "data positive control")
    require(data_gram != g, "dropping dirty helpers went undetected")

    # Sign/order changes inside the annihilated write subspace are VALID positives.
    flipped = [[g[0], g[1], g[2], -g[3], g[4], g[5]] if g[0] == "add" else g[:]
               for g in prefix]
    for variant in (list(reversed(prefix)), flipped):
        changed = forward(variant + word["A"], size)
        require([changed[j] for j in word["centers"]] == reader, "kernel-preserving positive rejected")
    require(right_inverse(reader, ["add", 224, 0, 1, 1, 0]) != reader,
            "live-column write defect was accepted")

    # Noncommuting complete-state fixture checks inverse signs AND product order.
    fixture = [["add", 0, 1, 1, 2, 0], ["add", 1, 0, -2, 1, 0]]
    product = forward(fixture, 2)
    identity = [({0: 1}, 0), ({1: 1}, 0)]
    recovered = product
    for gate in fixture:
        recovered = right_inverse(recovered, gate)
    require(recovered == identity, "inverse chronological positive")
    wrong_order = product
    for gate in reversed(fixture):
        wrong_order = right_inverse(wrong_order, gate)
    require(wrong_order != identity, "wrong inverse order missed")
    wrong_sign = [["add", 0, 1, -1, 2, 0], fixture[1]]
    bad = product
    for gate in wrong_sign:
        bad = right_inverse(bad, gate)
    require(bad != identity, "wrong inverse sign missed")
    require(product == [({0: 2, 1: 1}, 1), ({0: -2}, 0)], "noncommuting fixture exact product")

    # Explicit invertible nonunitary prefix can erase a diagonal obstruction.
    diagonal = [({i: 1 << i}, 0) for i in range(8)]
    for i in range(8):
        diagonal = right_inverse(diagonal, ["scale", i, 1 << i, 1, 0])
    require(diagonal == [({i: 1}, 0) for i in range(8)], "generic prefix counterexample")
    return {
        "status": "PASS_INDEPENDENT_PRECONDITION_CUTS",
        "method": "forward integer dyadic operators then chronological inverse column updates",
        "all_input_fields": size,
        "reader_entries_compared": 8 * size,
        "prefix_gates": len(prefix),
        "prefix_write_targets": sorted(targets),
        "prefix_touched_fields": len(touched),
        "residual_entry_fields": len(residual),
        "reader_support_columns": len(set().union(*(r.keys() for r, _ in reader))),
        "all_cut_readers_equal": 7401,
        "row_norms_every_cut": norms,
        "gram_every_cut": g,
        "paired_cycles_rejected_per_cut": len(permutations),
        "cut_cycle_pairs_excluded": 7401 * len(permutations),
        "controls": ["data-only Gram56I", "actual prefix sign changes accepted",
                     "actual prefix reversed order accepted", "live-column write rejected",
                     "noncommuting inverse sign rejected", "noncommuting inverse order rejected",
                     "generic nonunitary prefix changes obstruction"],
        "scope": "Finite scalar census; native implication conditional on retained typed frame identities. No new kappa.",
    }


if __name__ == "__main__":
    print(json.dumps(checks(), indent=2))

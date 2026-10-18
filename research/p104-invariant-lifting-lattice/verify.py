"""Read-only exact finite certificate for the common lifting lattice.

Ross Richardson with OpenAI Codex assistance. Apache-2.0.
"""

import argparse
import hashlib
import json
from pathlib import Path
import types


HERE = Path(__file__).resolve().parent
PINS = {
    "vendor/lattice.py": "c6563f7c94dfc751db65ecf10d07501722bccfdf5eda519348f2711eb7811655",
    "vendor/period-PROOF.md": "c0122fdb326b36b42ecb22958aff55199364c7d822d3fad56fda9e00408bd8df",
}
COMMON = [2, 7, 17, 39, 87, 187, 401]


def need(value, reason):
    if not value:
        raise ValueError(reason)


def unique(pairs):
    result = dict(pairs)
    need(len(result) == len(pairs), "duplicate JSON key")
    return result


def read_json(path):
    raw = path.read_bytes()
    need(len(raw) <= 100_000, "JSON size limit")
    return json.loads(raw, object_pairs_hook=unique)


def load_model():
    # Check inherited proof/source bytes before executing any package module.
    for name, digest in PINS.items():
        raw = (HERE / name).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == digest, "source pin: " + name)
    raw = (HERE / "model.py").read_bytes()
    need(len(raw) <= 40_000, "model size limit")
    module = types.ModuleType("common_lattice_model")
    exec(compile(raw, str(HERE / "model.py"), "exec"), module.__dict__)
    return module


def combination(basis, salt, wide=False):
    weights = [((j * 17 + salt * 13) % 19) - 9 for j in range(len(basis))]
    if wide:
        weights[salt % len(weights)] = -(1 << 4000) - 19
    return [sum(x * c for x, c in zip(row, weights, strict=True)) for row in basis]


def controls(m):
    gamma, common, _, _ = m.construct(2)
    # Dropping the reverse system keeps the 6-bit forward lattice and fails U closure.
    need(not m.member(m.apply(gamma, 2, range(2)), 2, range(2)),
         "missing reverse constraints must fail")
    need(m.member(m.apply(common, 2, range(2)), 2, range(2)),
         "common lattice positive control")
    phase_witnesses = 0
    coordinate_witnesses = 0
    quarter_witnesses = 0
    signed_macros = 0
    for rank in range(1, 8):
        _, basis, _, _ = m.construct(rank)
        order, reverse = range(rank), reversed(range(rank))
        ones = [1 if c == 0 else 0 for _ in range(1 << rank) for c in range(2)]
        need(m.member(m.as_column(ones), rank, order) and
             m.member(m.as_column(ones), rank, reverse), "constant lattice member")
        for bit in range(rank):
            phased = [v for a in range(1 << rank)
                      for v in ((0, 1) if (a >> bit) & 1 else (1, 0))]
            need(not m.member(m.as_column(phased), rank, range(rank)),
                 "address-dependent phase must leave period lattice")
            phase_witnesses += 1
        spike = [1] + [0] * (m.size(rank) - 1)
        need(not m.member(m.as_column(spike), rank, range(rank)),
             "single-coordinate ADD must leave period lattice")
        coordinate_witnesses += 1
        # A real scalar spike needs 2^(floor(r/2)+1); it lies in both order domains.
        period = 1 << (rank // 2 + 1)
        multiple = [period * x for x in spike]
        need(m.member(m.as_column(multiple), rank, range(rank)) and
             m.member(m.as_column(multiple), rank, reversed(range(rank))),
             "uniform scalar-period spike")
        if period >= 4:
            quarter = [x // 4 for x in multiple]
            need(not m.member(m.as_column(quarter), rank, range(rank)),
                 "integral quarter quotient must leave period lattice")
            quarter_witnesses += 1
        for salt in range(5):
            x = combination(basis, salt, wide=salt == 4)
            y = combination(basis, salt + 7, wide=salt == 4)
            ux = [row[0] for row in m.apply(m.as_column(x), rank, range(rank))]
            transformed = m.lift(x, rank)
            updated = [a + b for a, b in zip(y, transformed, strict=True)]
            restored = m.lift(transformed, rank, inverse=True)
            need(restored == x and updated == [a + b for a, b in zip(y, ux, strict=True)],
                 "exact dirty source-preserving shear")
            need(m.member(m.as_column(updated), rank, range(rank)) and
                 m.member(m.as_column(updated), rank, reversed(range(rank))),
                 "whole-array ADD stays in common lattice")
            need(m.lift(m.lift(x, rank, inverse=True), rank) == x,
                 "other literal inverse order")
            signed_macros += 1
    # Broader exactness is a different premise: (a,b)=(1+i,0) is outside Gamma_1,
    # but both parity corrections agree, so L=U exactly and its whole C orbit is exact.
    value = [1, 1, 0, 0]
    need(not m.member(m.as_column(value), 1, range(1)), "larger exactness control")
    for _ in range(4):
        exact = [row[0] for row in m.apply(m.as_column(value), 1, range(1))]
        need(m.lift(value, 1) == exact, "period domain is not every exactness domain")
        value = exact
    return {"missing_reverse_rejected": True,
            "linear_address_phase_counterexamples": phase_witnesses,
            "coordinate_ADD_counterexamples": coordinate_witnesses,
            "integral_quarter_counterexamples": quarter_witnesses,
            "signed_dirty_macros": signed_macros,
            "maximum_input_coefficient_bits": 4001,
            "larger_rank_one_exactness_orbit": True}


def compute():
    m = load_model()
    rows = [m.report(rank) for rank in range(1, 8)]
    need([row["common_index_bits"] for row in rows] == COMMON,
         "common finite index certificate")
    return {"status": "PASS_COMMON_INVARIANT_LIFTING_LATTICE",
            "ranks": rows, "controls": controls(m),
            "source_sha256": PINS,
            "scope": "Finite ranks 1..7; written maximality only inside Gamma; no full consumer or kappa."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Create absent RESULT.json exclusively")
    args = parser.parse_args()
    result = compute()
    if args.write:
        with (HERE / "RESULT.json").open("x", encoding="utf-8") as output:
            json.dump(result, output, indent=2, sort_keys=True)
            output.write("\n")
    else:
        expected = read_json(HERE / "RESULT.json")
        # Canonical JSON comparison distinguishes bool from integer receipt corruption.
        need(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
             "receipt equality including scalar types")
    print(result["status"])
    print("Common indices: 2,7,17,39,87,187,401; rank7 adds58 period constraints.")


if __name__ == "__main__":
    main()

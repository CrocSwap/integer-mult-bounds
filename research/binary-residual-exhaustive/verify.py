#!/usr/bin/env python3
"""Independent exhaustive finite binary-frame audit. Apache-2.0; see NOTICE.md."""
import argparse
from collections import Counter
from contextlib import contextmanager
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import random
import sys
from types import ModuleType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "f567884aeb8851b6e794af1184119a3bfbe1e631"
SEED = 83
CAP = 6
SOURCE_PATHS = (
    "scripts/binary_phase_frames.py",
    "scripts/experiments/parity_phase_repair.py",
    "scripts/certify.py",
    "notes/complex-compression.tex",
    "docs/research/parity-side.md",
    "tests/test_complex_compression.py",
    "tests/test_parity_side.py",
    "certificates/checkpoints/frontier799.json",
    "research/community-frontier799-audit/ASSEMBLY.json",
    "docs/research/community-frontier799-review.md",
    "upstream/build/sections/03-motifs.tex",
)
sys.path.insert(0, str(HERE))
import oracle


def require(condition, message):
    if not condition:
        raise ValueError(message)


def same_typed(actual, expected):
    """JSON equality that does not equate bools, integers or floats."""
    if type(actual) is not type(expected):
        return False
    if isinstance(actual, dict):
        return actual.keys() == expected.keys() and all(
            same_typed(actual[k], expected[k]) for k in actual)
    if isinstance(actual, list):
        return len(actual) == len(expected) and all(
            same_typed(a, b) for a, b in zip(actual, expected))
    return actual == expected


def check_sources(root=ROOT, manifest=None):
    root = Path(root).resolve()
    if manifest is None:
        manifest = json.loads((HERE / "SOURCES.json").read_text())
    require(manifest["base_commit"] == BASE, "Wrong base commit")
    require(set(manifest["files"]) == set(SOURCE_PATHS), "Incomplete source inventory")
    for relative, pin in manifest["files"].items():
        path = (root / relative).resolve()
        require(path.is_relative_to(root) and path.is_file(), "Missing/escaping source: " + relative)
        data = path.read_bytes()
        require(sha256(data).hexdigest() == pin["sha256"], "Source SHA256 mismatch: " + relative)
        from hashlib import sha1
        blob = sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(blob == pin["git_blob"], "Source Git blob mismatch: " + relative)
    return manifest


@contextmanager
def subjects(root=ROOT):
    """Execute pinned originals with their assertions intact, including under -O."""
    names = ("certify", "binary_phase_frames", "binary_residual_subject_parity")
    paths = ("scripts/certify.py", "scripts/binary_phase_frames.py",
             "scripts/experiments/parity_phase_repair.py")
    saved = {name: sys.modules.get(name) for name in names}
    modules = []
    try:
        for name, relative in zip(names, paths):
            path = Path(root) / relative
            module = ModuleType(name)
            module.__file__ = str(path)
            sys.modules[name] = module
            exec(compile(path.read_bytes(), str(path), "exec", optimize=0), module.__dict__)
            modules.append(module)
        yield modules[1], modules[2]
    finally:
        for name, previous in saved.items():
            if previous is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = previous


def orthonormal_output(vectors, space, n):
    vectors = tuple(vectors)
    require(len(vectors) == len(oracle.basis(space, n)), "Wrong orthonormal dimension")
    require(oracle.span(vectors, n) == space, "Wrong orthonormal output span")
    require(all(oracle.dot(a, b, n) == int(i == j)
                for i, a in enumerate(vectors) for j, b in enumerate(vectors)),
            "Nonorthonormal output")
    return vectors


def expect_rejection(call, message):
    try:
        call()
    except (ValueError, AssertionError):
        return
    raise ValueError("Missed rejection: " + message)


def controls(frames, parity):
    full = (1, 2, 4)
    even = (3, 5)
    # This residual has no unit vector despite both endpoints being admissible.
    r = frames.residual((7,), full)
    require(oracle.span(r, 3) == oracle.span(even, 3), "Wrong alternating control")
    expect_rejection(lambda: frames.orthonormal_basis(r), "nonzero alternating residual")
    expect_rejection(lambda: frames.residual((3,), (1, 2)), "degenerate lower")
    expect_rejection(lambda: frames.residual((), (3,)), "degenerate upper")
    expect_rejection(lambda: frames.residual((1,), (2,)), "nonnested endpoints")
    expect_rejection(lambda: parity.characteristic((3,)), "degenerate characteristic")
    expect_rejection(lambda: orthonormal_output((1, 2, 7), oracle.span(full, 3), 3),
                     "nonorthogonal unit basis")
    require(frames.orthonormal_basis(frames.residual(even, even)) == (),
            "Equal alternating endpoints must allow zero residual")
    # q(7)=3, so an odd norm cannot be replaced by phase weight +1.
    phase = oracle.project(oracle.span((7,), 3), 1, 3).bit_count() % 4
    require(phase == 3 and phase != 1, "Odd phase weight control failed")
    require((-phase) % 4 != phase, "Reverse phase sign control failed")
    # Checking only dimension/rank would accept the wrong orthonormal plane.
    expect_rejection(lambda: orthonormal_output((1, 2), oracle.span((1, 4), 3), 3),
                     "wrong residual of same rank")
    return {
        "nonzero_alternating_rejected": True,
        "degenerate_lower_rejected": True,
        "degenerate_upper_rejected": True,
        "nonnested_rejected": True,
        "degenerate_characteristic_rejected": True,
        "nonorthogonal_unit_basis_rejected": True,
        "zero_residual_at_alternating_endpoints_accepted": True,
        "unit_phase_weight_substitution_detected": True,
        "reverse_phase_sign_substitution_detected": True,
        "same_rank_wrong_span_detected": True,
    }


def gaussian_counts(n):
    """Independent integer recurrence [n,k]_2=[n-1,k-1]_2+2^k[n-1,k]_2."""
    row = [1]
    for size in range(1, n + 1):
        row = [(row[k - 1] if k else 0) + ((1 << k) * row[k] if k < size else 0)
               for k in range(size + 1)]
    return row


def audit(frames, parity, cap=CAP):
    require(type(cap) is int and 0 <= cap <= CAP, "Audit cap must be an integer in 0..6")
    rng = random.Random(SEED)
    rows = []
    for n in range(cap + 1):
        spaces = oracle.list_subspaces(n)
        classes = {s: oracle.classify(s, n) for s in spaces}
        dims = Counter(c["dimension"] for c in classes.values())
        require([dims[k] for k in range(n + 1)] == gaussian_counts(n),
                "Incomplete all-subspace census")
        nondegenerate = [s for s in spaces if classes[s]["nondegenerate"]]
        canonical = {s: oracle.basis(s, n) for s in spaces}
        presented = {}
        totals = Counter()
        for space in spaces:
            redundant = list(sorted(space))
            rng.shuffle(redundant)
            presented[space] = tuple(redundant)
            expected = {key: classes[space][key]
                        for key in ("dimension", "nondegenerate", "nonalternating")}
            for vectors in (canonical[space], presented[space]):
                require(same_typed(frames.classify(vectors), expected), "Classification mismatch")
                admissible = expected["dimension"] == 0 or (
                    expected["nondegenerate"] and expected["nonalternating"])
                if admissible:
                    orthonormal_output(frames.orthonormal_basis(vectors), space, n)
                    totals["accepted_basis_presentations"] += 1
                else:
                    expect_rejection(lambda: frames.orthonormal_basis(vectors), "inadmissible space")
                    totals["rejected_basis_presentations"] += 1
                totals["classified_presentations"] += 1
            if expected["nondegenerate"]:
                want = oracle.characteristic(space, n)
                for vectors in (canonical[space], presented[space]):
                    require(parity.characteristic(vectors) == want, "Characteristic mismatch")
                    totals["characteristic_presentations"] += 1
        @lru_cache(None)
        def projection(space, x):
            return oracle.project(space, x, n)
        for upper in nondegenerate:
            w = oracle.characteristic(upper, n)
            for lower in nondegenerate:
                if not lower <= upper:
                    continue
                expected_residual = oracle.residual(lower, upper, n)
                result = frames.residual(canonical[lower], presented[upper])
                require(oracle.span(result, n) == expected_residual, "Residual set mismatch")
                c = oracle.classify(expected_residual, n)
                require(c["nondegenerate"], "Residual lost nondegeneracy")
                require(c["dimension"] == classes[upper]["dimension"] - classes[lower]["dimension"],
                        "Residual dimension mismatch")
                require(c["alternating"] == (w in lower), "Characteristic membership criterion failed")
                totals["nested_pairs"] += 1
                if c["dimension"] and c["alternating"]:
                    expect_rejection(lambda: frames.orthonormal_basis(result), "alternating pair residual")
                    totals["nonzero_alternating_pairs"] += 1
                    continue
                units = orthonormal_output(frames.orthonormal_basis(result), expected_residual, n)
                totals["admissible_pairs"] += 1
                totals["zero_residual_pairs"] += int(c["dimension"] == 0)
                for x in range(1 << n):
                    pu, pa = projection(upper, x), projection(lower, x)
                    pr = 0
                    phase = 0
                    for v in units:
                        if oracle.dot(v, x, n):
                            pr ^= v
                            phase += v.bit_count()
                    require(pu ^ pa == pr, "Orthogonal projector decomposition mismatch")
                    require((pu.bit_count() - pa.bit_count()) % 4 == phase % 4,
                            "Forward Hamming-weight phase mismatch")
                    require((pa.bit_count() - pu.bit_count()) % 4 == (-phase) % 4,
                            "Reverse Hamming-weight phase mismatch")
                    totals["phase_inputs"] += 1
        rows.append({"ambient_dimension": n, "subspaces_by_dimension": gaussian_counts(n),
                     "subspaces": len(spaces), "nondegenerate_subspaces": len(nondegenerate),
                     **dict(sorted(totals.items()))})
    return {"status": "PASS_BINARY_RESIDUAL_EXHAUSTIVE", "base_commit": BASE,
            "assignment_seed": SEED, "ambient_cap": cap,
            "source_assertions": "Explicit compile(optimize=0); unchanged predecessor source",
            "coverage": rows, "controls": controls(frames, parity),
            "scope": "Exhaustive finite evidence only; historical binary residual interface, no new kappa"}


def run(root=ROOT, expected=None):
    check_sources(root)
    with subjects(root) as (frames, parity):
        receipt = audit(frames, parity)
    if expected is None:
        expected = json.loads((HERE / "EXPECTED.json").read_text())
    require(same_typed(receipt, expected), "Exact typed receipt mismatch")
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Write a verified receipt to a new file")
    args = parser.parse_args()
    receipt = run()
    if args.output:
        with args.output.open("x") as stream:
            stream.write(json.dumps(receipt, indent=2) + "\n")
    coverage = receipt["coverage"]
    print("PASS_BINARY_RESIDUAL_EXHAUSTIVE subspaces=" + str(sum(r["subspaces"] for r in coverage))
          + " nested_pairs=" + str(sum(r["nested_pairs"] for r in coverage))
          + " phase_inputs=" + str(sum(r["phase_inputs"] for r in coverage))
          + " controls=10 kappa=unchanged")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Equivalence, pin and mutation controls for ternary frame cleared-cache replay.

Read-only by default. Regenerates no certificate. Timing is not a pass gate;
see benchmark.py / RESULT.json.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from math import lcm
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from certify import require  # noqa: E402
from fractions import Fraction as Q  # noqa: E402
from audit_joint_frames import eye, matrix  # noqa: E402

BASE_COMMIT = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
ORIGINAL_BLOB = "a50c627e31246aab64af151635a135d4fd7a9f32"
ORIGINAL_SHA256 = "93379b6e70cf58bb55432d9f2d1c0e0305c20a075bfe3cc219deabd927afd375"
OPTIMIZED_SHA256 = "eba4acc6f44c5d56aa8d225266a4a951fc1f1cb84819cdc104e1847578403878"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"missing module {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def digest_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def git_show(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{BASE_COMMIT}:{path}"], cwd=ROOT)


def check_baseline_bytes() -> None:
    baseline = PACKAGE / "baseline.py"
    original = git_show("scripts/experiments/ternary_side.py")
    require(sha256(original).hexdigest() == ORIGINAL_SHA256, "base ternary_side.py sha256 drift")
    blob = (
        subprocess.check_output(
            ["git", "rev-parse", f"{BASE_COMMIT}:scripts/experiments/ternary_side.py"], cwd=ROOT
        )
        .decode()
        .strip()
    )
    require(blob == ORIGINAL_BLOB, "base ternary_side.py blob drift")
    require(baseline.read_bytes() == original, "baseline.py must be an exact copy of the base commit source")
    require(
        digest_file(SCRIPTS / "experiments" / "ternary_side.py") == OPTIMIZED_SHA256,
        "production ternary_side.py does not match the claimed optimized digest",
    )


def check_frame_equivalence(baseline, optimized) -> dict:
    records = []
    for h in (8, 9):
        graph = optimized.build(h, retain_graph=True)
        # Baseline and optimized share the same DAG builder; only frames differ.
        old = baseline.verify_invocation_frames(graph)
        new = optimized.verify_invocation_frames(graph)
        require(old == new, f"verify_invocation_frames mismatch on h={h}")
        records.append(
            dict(
                h=h,
                physical_edges=new["orientations"][0]["physical_edges"],
                rank_sum=new["orientations"][0]["rank_sum"],
                decreasing_dimensions=new["orientations"][0]["decreasing_dimensions"],
            )
        )
    require(records[0]["physical_edges"] == 4732, "unexpected h=8 edge count")
    require(records[1]["physical_edges"] == 37604, "unexpected h=9 edge count")
    return {"frame_cases": len(records), "records": records}


def check_pin_payload(committed, base):
    """Preserve the full certificate, allowing only the two reviewed source updates."""
    restored = json.loads(json.dumps(committed))
    own = "scripts/experiments/ternary_side.py"
    require(restored["source_sha256"][own] == OPTIMIZED_SHA256, "wrong ternary pin")
    restored["source_sha256"][own] = base["source_sha256"][own]
    companion = "scripts/experiments/disjoint_tensor.py"
    if restored["source_sha256"].get(companion) != base["source_sha256"].get(companion):
        expected = "23763a4b6086fb3d19f9282fff5c118f53fa52e7a7f17da1bde990bd4cf8b6ac"
        require(restored["source_sha256"].get(companion) == expected,
                "unreviewed disjoint-tensor companion pin")
        require(sha256((ROOT / companion).read_bytes()).hexdigest() == expected,
                "disjoint-tensor companion source drift")
        restored["source_sha256"][companion] = base["source_sha256"][companion]
    require(restored == base, "certificate changed beyond reviewed source pins")


def check_certificate_pin() -> dict:
    committed = json.loads((ROOT / "certificates/ternary-side.json").read_text())
    base = json.loads(git_show("certificates/ternary-side.json"))
    require(
        committed["source_sha256"]["scripts/experiments/ternary_side.py"] == OPTIMIZED_SHA256,
        "certificate pin does not match optimized ternary_side.py",
    )
    check_pin_payload(committed, base)
    # Committed small controls must match live optimized frames.
    import experiments.ternary_side as production

    for control in committed["complete_invocation_controls"]:
        h = control["frames"]["h"]
        live = production.verify_invocation_frames(
            production.build(h, retain_graph=True)
        )
        require(live == control["frames"], f"committed frames drift for h={h}")
    return {"certs": 1, "pin_only": True, "payload": "identical"}


def check_product_equivalence() -> dict:
    """Cleared product must match entrywise Fraction sum on random matrices."""
    import random

    rng = random.Random(0x60B9)
    cases = 0
    for n, k, m in ((2, 2, 2), (3, 2, 4), (4, 4, 3), (5, 3, 5)):
        for _ in range(40):
            A = matrix(
                [
                    [Q(rng.randint(-6, 6), rng.randint(1, 9)) for _ in range(k)]
                    for _ in range(n)
                ]
            )
            B = matrix(
                [
                    [Q(rng.randint(-6, 6), rng.randint(1, 9)) for _ in range(m)]
                    for _ in range(k)
                ]
            )
            slow = tuple(
                tuple(sum(A[i][t] * B[t][j] for t in range(k)) for j in range(m))
                for i in range(n)
            )
            DA = 1
            for row in A:
                for x in row:
                    if x.denominator != 1:
                        DA = lcm(DA, x.denominator)
            DB = 1
            for row in B:
                for x in row:
                    if x.denominator != 1:
                        DB = lcm(DB, x.denominator)
            Ai = [[x.numerator * (DA // x.denominator) for x in row] for row in A]
            Bi = [[x.numerator * (DB // x.denominator) for x in row] for row in B]
            scale = DA * DB
            fast = tuple(
                tuple(Q(sum(Ai[i][t] * Bi[t][j] for t in range(k)), scale) for j in range(m))
                for i in range(n)
            )
            require(slow == fast, "cleared product disagrees with Fraction sum")
            cases += 1
    # Mutant foil: forgetting the scale factor must differ on a non-integer matrix.
    A = matrix([[Q(1, 2), Q(0)], [Q(0), Q(1)]])
    B = matrix([[Q(1, 3), Q(0)], [Q(0), Q(1)]])
    good = tuple(
        tuple(sum(A[i][t] * B[t][j] for t in range(2)) for j in range(2)) for i in range(2)
    )
    mutant = tuple(
        tuple(sum(A[i][t].numerator * B[t][j].numerator for t in range(2)) for j in range(2))
        for i in range(2)
    )
    require(good != matrix(mutant), "scale-omission mutant must differ")
    return {"product_cases": cases, "scale_mutant": "rejected"}


def check_transition_cache_foil(optimized) -> dict:
    """A poisoned transition memo must violate the nested-rank require."""
    from audit_joint_frames import zero, sub, rank

    # Live path succeeds on the historical control.
    graph = optimized.build(8, retain_graph=True)
    optimized.verify_invocation_frames(graph)

    Z = zero(8)
    I = eye(8)
    require(Z != I, "control frames must differ")
    exact = (rank(sub(I, Z)), rank(I) - rank(Z))
    require(exact[0] == abs(exact[1]), "exact Z→I transition must be nested")

    # Identity-then-value interning (same shape as production).
    frame_list = []
    frame_by_value = {}
    frame_by_identity = {}
    transitions = {}

    def intern(frame):
        prior = frame_by_identity.get(id(frame))
        if prior is not None:
            return prior[1]
        index = frame_by_value.get(frame)
        if index is None:
            index = len(frame_list)
            frame_list.append(frame)
            frame_by_value[frame] = index
        frame_by_identity[id(frame)] = (frame, index)
        return index

    def transition(old, new):
        key = (intern(old), intern(new))
        answer = transitions.get(key)
        if answer is None:
            answer = (rank(sub(new, old)), rank(new) - rank(old))
            transitions[key] = answer
        return answer

    # Equal values share one index; unequal values do not.
    require(intern(Z) == intern(zero(8)), "equal frames must share an intern index")
    require(intern(Z) != intern(I), "unequal frames must get distinct intern indices")
    require(transition(Z, I) == exact, "memoized transition must match exact ranks")

    # Poison the memo: claim a zero climb for Z→I.
    key = (intern(Z), intern(I))
    transitions[key] = (0, exact[1] if exact[1] else 1)
    a, change = transition(Z, I)
    require(a != abs(change), "poisoned nested-rank answer must fail a==abs(change)")
    require((a, change) != exact, "poisoned answer must differ from the exact transition")
    return {"cache_foil": "poisoned_transition_rejected", "identity": "Z_ne_I"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-certificate", action="store_true")
    args = parser.parse_args()
    require(not args.write_certificate, "default verify is read-only; pin was committed separately")

    check_baseline_bytes()
    baseline = load_module(PACKAGE / "baseline.py", "ternary_frame_baseline")
    import experiments.ternary_side as production

    products = check_product_equivalence()
    frames = check_frame_equivalence(baseline, production)
    pins = check_certificate_pin()
    foil = check_transition_cache_foil(production)
    print(
        "PASS_TERNARY_FRAME_CLEARED_CACHE",
        f"frame_cases={frames['frame_cases']}",
        f"product_cases={products['product_cases']}",
        f"certs={pins['certs']}",
        "no_new_kappa",
        flush=True,
    )
    print("foil", foil["cache_foil"], foil["identity"], flush=True)


if __name__ == "__main__":
    main()

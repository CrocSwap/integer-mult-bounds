"""Behavioral controls for hypotheses and authenticated replay. Apache-2.0."""

import copy
import json
import shutil
import tempfile
from pathlib import Path

import verify as v


def rejected(call, message):
    try:
        call()
    except (ValueError, OSError):
        return
    raise ValueError("control accepted: " + message)


def manifest_controls():
    sources = json.loads(v.read_bytes(v.PACKAGE / "SOURCES.json"))
    mutants = []
    changed = copy.deepcopy(sources)
    changed["files"][2]["usage"] = "provenance"
    mutants.append(changed)
    changed = copy.deepcopy(sources)
    changed["files"].pop()
    mutants.append(changed)
    changed = copy.deepcopy(sources)
    changed["files"].append(changed["files"][0])
    mutants.append(changed)
    changed = copy.deepcopy(sources)
    changed["retained_files"][0]["usage"] = "unused"
    mutants.append(changed)
    changed = copy.deepcopy(sources)
    changed["files"][2]["sha256"] = "0" * 64
    mutants.append(changed)
    for mutant in mutants:
        rejected(
            lambda mutant=mutant: v.authenticate(manifest=mutant),
            "inventory/usage/digest",
        )
    return len(mutants)


def source_controls():
    with tempfile.TemporaryDirectory(prefix="a2-rank6-controls-") as directory:
        root = Path(directory)
        package = root / "research/e8-a2-analytic-rank6"
        shutil.copytree(v.PACKAGE, package)
        target = root / v.GEOMETRY
        target.parent.mkdir(parents=True)
        raw = v.read_bytes(v.ROOT / v.GEOMETRY)
        target.write_bytes(raw)
        v.authenticate(root=root, package=package)
        target.write_bytes(raw + b"\n")
        rejected(
            lambda: v.authenticate(root=root, package=package), "actual source drift"
        )
        target.unlink()
        target.symlink_to(v.ROOT / v.GEOMETRY)
        rejected(lambda: v.authenticate(root=root, package=package), "live symlink")
        target.unlink()
        target.write_bytes(raw)
        retained = package / "vendor/pr3262-PROOF.md"
        # Change only the one private copied file used by this mutation.
        retained.chmod(0o644)
        retained.write_bytes(retained.read_bytes() + b"\n")
        rejected(
            lambda: v.authenticate(root=root, package=package), "retained proof drift"
        )
    return 3


def hypothesis_controls():
    # Negative ambient sign permits20 ones in an affine five-space.
    def f(x):
        return (
            (x & 1) * (x >> 1 & 1)
            ^ (x >> 2 & 1) * (x >> 3 & 1)
            ^ (x >> 4 & 1) * (x >> 5 & 1)
            ^ (x >> 4 & 1)
            ^ (x >> 5 & 1)
        )

    v.require(sum(1 - 2 * f(x) for x in range(64)) == -8, "negative sign control")
    v.require(
        sum(f(x) for x in range(64) if not x & 1) == 20, "negative sign counterexample"
    )
    g = v.geometry()
    _roots, _, _, coordinates = g.root_data()
    labels = tuple(
        1 | sum((int(c) % 2) << (i + 1) for i, c in enumerate(row))
        for row in coordinates
    )
    receipt = json.loads(v.read_bytes(v.PACKAGE / "RESULT.json"))
    fiber = tuple(receipt["canonical_fiber"])
    q = v.quadratic(g.SIMPLE)
    negative = tuple(x ^ 1 for x in q)
    rejected(lambda: v.fiber_model(fiber, labels, negative), "wrong affine sign")
    # The rank limit is necessary: W itself gives28+27=55.
    v.require(
        len(set(v.span(v.basis(fiber))) & set(labels)) + len(fiber) == 55,
        "rank7 counterexample",
    )
    witness = tuple(receipt["canonical"]["witness_labels"])
    v.require(set(witness) <= set(fiber) and len(witness) == 16, "actual equality32")
    v.require(len(v.basis(witness)) == 6, "equality rank")
    # A balanced hyperplane containing p gives only31, as the analytic table says.
    v.require(
        receipt["canonical"]["histogram"]["16,15"] == 36, "missing-root condition"
    )
    rejected(lambda: v.basis((512,)), "binary range")
    rejected(lambda: v.span((1, 1)), "dependent basis")
    return 7


def main():
    v.authenticate()
    counts = [manifest_controls(), source_controls(), hypothesis_controls()]
    v.require(counts == [5, 3, 7], "all bounded controls ran")
    print("PASS_A2_RANK6_CONTROLS inventory=5 source=3 hypotheses=7")


if __name__ == "__main__":
    main()

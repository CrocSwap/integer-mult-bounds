"""Source-boundary and changed-hypothesis controls, including optimized Python."""

import copy
import json
import shutil
import tempfile
from itertools import combinations
from pathlib import Path

import common as c


def rejected(call, message):
    try:
        call()
    except (ValueError, OSError, KeyError, TypeError):
        return
    raise ValueError("control accepted: " + message)


def source_controls():
    with tempfile.TemporaryDirectory(prefix="d6-controls-") as directory:
        root = Path(directory)
        package = root / "research/d6-punctured-capacity18"
        shutil.copytree(c.PACKAGE, package)
        target = root / c.GEOMETRY
        target.parent.mkdir(parents=True)
        raw = (c.ROOT / c.GEOMETRY).read_bytes()
        target.write_bytes(raw)
        c.authenticate(package=package, root=root)
        target.write_bytes(raw + b"\n")
        rejected(lambda: c.authenticate(package, root), "live source drift")
        target.write_bytes(raw)
        receipt = package / "vendor/pr3267-PROOF.md"
        receipt.chmod(0o600)
        proof_bytes = receipt.read_bytes()
        receipt.write_bytes(proof_bytes + b"\n")
        rejected(lambda: c.authenticate(package, root), "retained source drift")
        receipt.write_bytes(proof_bytes)
        c.authenticate(package, root)
        original = json.loads((c.PACKAGE / "SOURCES.json").read_text())
        for kind in range(5):
            mutant = copy.deepcopy(original)
            if kind == 0:
                mutant["files"][2]["usage"] = "provenance"
            elif kind == 1:
                mutant["files"][2]["path"] = "unexpected.py"
            elif kind == 2:
                mutant["files"].append(mutant["files"][0])
            elif kind == 3:
                mutant["retained_files"][0]["source_commit"] = "0" * 40
            else:
                mutant["files"][0]["extra"] = "unexpected"
            manifest = package / "SOURCES.json"
            manifest.chmod(0o600)
            manifest.write_text(json.dumps(mutant))
            rejected(
                lambda: c.authenticate(package, root), "inventory, usage or schema"
            )
    return 7


def hypothesis_controls():
    g = c.geometry()
    roots, _, _, coordinates = g.root_data()
    labels = tuple(
        1 | sum((int(x) % 2) << (j + 1) for j, x in enumerate(row))
        for row in coordinates
    )
    result = json.loads((c.PACKAGE / "RESULT.json").read_text())
    a, b = (roots[j] for j in result["pair"])
    bulk = tuple(
        i for i, r in enumerate(roots) if g.dot(a, r) and not g.dot(b, r) and r != a
    )
    mapping = c.coordinate_map(tuple(labels[i] for i in bulk))
    sections = tuple(
        tuple(i for i in bulk if not (mapping[labels[i]] & f).bit_count() % 2)
        for f in range(1, 128)
    )
    twenty = next(s for s in sections if len(s) == 20)
    outside = tuple(i for i in bulk if i not in twenty)
    # Two punctures can miss an actual twenty-point section entirely.
    two = next(
        p for p in combinations(outside, 2) if not g.dot(roots[p[0]], roots[p[1]])
    )
    c.require(not set(two) & set(twenty), "two-puncture losing control")
    c.require(
        len(c.basis(tuple(labels[i] for i in twenty))) == 6, "twenty-point rank six"
    )
    four = outside[:4]
    c.require(len(set(twenty) - set(four)) == 20, "nonorthogonal four-puncture control")
    c.require(
        any(g.dot(roots[i], roots[j]) for i, j in combinations(four, 2)),
        "changed orthogonality hypothesis",
    )
    quad = result["witness"]["puncture"]
    c.require(len(set(bulk) - set(quad)) == 28, "rank-seven losing control")
    c.require(
        len(c.basis(tuple(labels[i] for i in bulk if i not in quad))) == 7,
        "surviving bulk has rank seven",
    )
    rejected(lambda: c.basis((512,)), "out-of-range binary label")
    return 4


def main():
    c.authenticate()
    c.require([source_controls(), hypothesis_controls()] == [7, 4], "all controls ran")
    print("PASS_D6_CONTROLS source=7 hypotheses=4")


if __name__ == "__main__":
    main()

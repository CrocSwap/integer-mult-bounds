"""Semantic and source-boundary controls, including optimized execution."""

import copy
import json
import runpy
import tempfile
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
v = runpy.run_path(str(PACKAGE / "verify.py"))
require = v["require"]


def rejected(function, message):
    try:
        function()
    except (ValueError, FileNotFoundError, TypeError):
        return
    raise ValueError("control was accepted: " + message)


def source_controls():
    original = json.loads((PACKAGE / "SOURCES.json").read_text())
    mutant = copy.deepcopy(original)
    mutant["schema_version"] = True
    rejected(lambda: v["authenticate"](manifest=mutant), "boolean schema")
    mutant = copy.deepcopy(original)
    mutant["files"][2]["usage"] = "provenance"
    rejected(lambda: v["authenticate"](manifest=mutant), "reclassified live source")
    mutant = copy.deepcopy(original)
    mutant["files"].append(mutant["files"][2])
    rejected(lambda: v["authenticate"](manifest=mutant), "duplicate inventory")
    mutant = copy.deepcopy(original)
    mutant["files"][2]["sha256"] = "0" * 64
    rejected(lambda: v["authenticate"](manifest=mutant), "digest corruption")
    with tempfile.TemporaryDirectory(prefix="rank7-controls-") as directory:
        root = Path(directory)
        target = root / v["GEOMETRY"]
        target.parent.mkdir(parents=True)
        target.write_bytes(v["authenticate"]() + b"\n# private mutation\n")
        rejected(lambda: v["authenticate"](root=root), "actual source corruption")
        target.unlink()
        target.symlink_to(PACKAGE / "SOURCES.json")
        rejected(lambda: v["authenticate"](root=root), "symlink input")


def geometry_controls():
    q, live, _ = v["model"]()
    pair = lambda a, b: q[a ^ b] ^ q[a] ^ q[b]
    a, b = next((a, b) for a in range(1, 256) for b in range(a + 1, 256) if pair(a, b))
    valid = []
    for section in range(4):
        try:
            v["equality_kind"](q, a, b, section)
            valid.append(section)
        except ValueError:
            pass
    require(len(valid) == 1, "one extremal coset")
    rejected(lambda: v["equality_kind"](q, a, b, valid[0] ^ 1), "wrong coset")
    c = next(c for c in range(1, 256) if c != a and pair(a, c) == 0)
    rejected(lambda: v["equality_kind"](q, a, c, 0), "degenerate equality plane")
    receipt = json.loads((PACKAGE / "RESULT.json").read_text())
    labels = receipt["witness"]["support_labels"]
    require(
        len(labels) == 36
        and len(set(labels)) == 36
        and all(x >> 1 in live for x in labels)
        and v["binary_rank"](labels) == 7,
        "literal rank-seven P112 attainment",
    )
    # Changing the Gauss-sum sign permits 40, so nondegeneracy alone is insufficient.
    z = next(x for x in range(256) if q[x])
    minus = [q[x] ^ pair(z, x) for x in range(256)]
    require(sum(minus) == 136, "minus-type control")
    counts = []
    for a in range(1, 256):
        for b in range(a + 1, 256):
            if pair(a, b) == 0:
                bins = [0] * 4
                for x in range(256):
                    bins[pair(a, x) + 2 * pair(b, x)] += minus[x]
                if max(bins) == 40:
                    counts.append(40)
                    break
        if counts:
            break
    require(counts == [40], "wrong-sign counterexample must attain forty")


def main():
    source_controls()
    geometry_controls()
    print(
        "PASS_E8_RANK7_CONTROLS source_groups=6 geometry_groups=4 optimized_safe=true"
    )


if __name__ == "__main__":
    main()

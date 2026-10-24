"""Check the small E8 certificates and their binary Schur constraints."""

import argparse
import hashlib
import itertools
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("package", type=Path)
parser.add_argument("--output", type=Path)
args = parser.parse_args()
package = args.package.resolve()
relative = "historical/work/p518-next/bit/weighted/rank9/quick.json"
data = json.loads((package / relative).read_text())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(left, right):
    return sum(x * y for x, y in zip(left, right))


roots = set()
for i, j in itertools.combinations(range(8), 2):
    for first, second in itertools.product((-2, 2), repeat=2):
        row = [0] * 8
        row[i], row[j] = first, second
        roots.add(tuple(row))
roots.update(row for row in itertools.product((-1, 1), repeat=8)
             if row.count(-1) % 2 == 0)
require(len(roots) == 240, "Expected all signed E8 roots")
require(sorted(item["node"] for item in data["parabolics"]) == list(range(1, 9)),
        "Each node must occur once")
pairs = [tuple(pair) for pair in data["pairs"]]
require(len(pairs) == len(set(pairs)) == 5, "Expected five distinct pairs")
require(all(len(pair) == len(set(pair)) == 2 for pair in pairs), "Pairs need two endpoints")
require(len(set().union(*map(set, pairs))) == 4, "Expected four endpoints")
require(all(0 <= x < 8 for pair in pairs for x in pair), "Anchor index out of range")


def states(pair):
    masks = [sum((1 << anchor) for k, anchor in enumerate(pair) if (choice >> k) & 1)
             for choice in range(4)]
    return [(c, b) for c in masks for b in masks if (c & b).bit_count() % 2 == 1]


reports = []
for item in data["parabolics"]:
    normal = item["normal"]
    rows = [tuple(row) for row in item["certificate"]]
    require(len(rows) == 13 and all(row in roots for row in rows), "Invalid certificate root")
    require(len({min(row, tuple(-x for x in row)) for row in rows}) == 13,
            "Repeated root line")
    require(all(dot(normal, row) != 0 for row in rows), "Certificate must avoid the hyperplane")
    require([j + 1 for j, root in enumerate(data["simple_roots"]) if dot(normal, root)]
            == [item["node"]], "Normal has the wrong deleted node")
    require(sum(dot(normal, row) == 0 for row in roots) == 2 * item["roots_in_hyperplane"],
            "Wrong hyperplane count")
    anchors, witnesses = rows[:8], rows[8:]
    require(all(dot(a, b) for a, b in itertools.combinations(anchors, 2)), "Anchor block is not I8")
    for pair, witness in zip(pairs, witnesses):
        require(tuple(j for j, anchor in enumerate(anchors) if dot(anchor, witness) == 0) == pair,
                "Wrong witness support")
    forced = [(e, f) for e in range(5) for f in range(5)
              if e != f and dot(witnesses[e], witnesses[f]) != 0]
    choices = [states(pair) for pair in pairs]
    require(all(len(choice) == 6 for choice in choices), "Expected six binary diagonal states")
    feasible = 0
    tested = 0
    for candidate in itertools.product(*choices):
        tested += 1
        if all((candidate[e][0] & candidate[f][1]).bit_count() % 2 == 0 for e, f in forced):
            feasible += 1
    require(tested == 7776 and feasible == 0, "A rank-eight fitting Schur completion survived")
    # Four witnesses have a rank-eight completion. This checks the five-edge boundary.
    four = next((candidate for candidate in itertools.product(*choices[:4])
                 if all((candidate[e][0] & candidate[f][1]).bit_count() % 2 == 0
                        for e, f in forced if e < 4 and f < 4)), None)
    require(four is not None, "Four-witness positive control failed")
    reports.append({"deleted_node": item["node"], "rank_eight_assignments_checked": tested,
                    "rank_eight_assignments_feasible": feasible,
                    "four_witness_positive_control": [[c, b] for c, b in four]})

controls = []
with tempfile.TemporaryDirectory(prefix="e8-parabolic-controls-") as temporary:
    temporary = Path(temporary)
    copied = temporary / "package"
    shutil.copytree(package, copied)

    def reject(name, expected, optimized=False):
        command = [sys.executable, "-E", "-B"]
        if optimized:
            command.append("-O")
        command += [str(copied / "verify.py"), "--build", str(temporary / name)]
        completed = subprocess.run(command, capture_output=True, text=True, timeout=60)
        require(completed.returncode != 0 and expected in completed.stderr,
                "Wrong rejection point: " + name)
        controls.append({"name": name, "exit_code": completed.returncode,
                         "expected_stderr": expected, "actual_stderr": completed.stderr})

    raw = (copied / relative).read_bytes()
    (copied / relative).write_bytes(raw + b" ")
    reject("changed_certificate_hash", "Source hash:")
    (copied / relative).write_bytes(raw)

    mutated = json.loads(raw)
    mutated["parabolics"][1] = mutated["parabolics"][0]
    (copied / relative).write_text(json.dumps(mutated) + "\n")
    manifest_path = copied / "SOURCE-MANIFEST.json"
    manifest_raw = manifest_path.read_bytes()
    manifest = json.loads(manifest_raw)
    for item in manifest["files"]:
        if item["package"] == relative:
            item["sha256"] = hashlib.sha256((copied / relative).read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest) + "\n")
    reject("missing_node_with_updated_hash", "The certificate must cover each deleted node once.")
    (copied / relative).write_bytes(raw)
    manifest_path.write_bytes(manifest_raw)

    reject("optimized_mode", "Run this verifier without -O.", optimized=True)

result = {"status": "PASS", "package": str(package), "binary_field": "F2",
          "signed_roots": len(roots), "certificates": reports,
          "total_schur_assignments": sum(row["rank_eight_assignments_checked"] for row in reports),
          "negative_controls": controls,
          "scope": "Exact finite certificate and Schur checks. Universal coverage also uses the written Weyl-chamber proof."}
if args.output:
    args.output.write_text(json.dumps(result, indent=2) + "\n")
print("PASS_E8_PARABOLIC_INDEPENDENT certificates=8 schur_assignments=62208 rejected=3")

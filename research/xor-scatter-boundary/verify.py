"""Exact XOR boundary evidence. Nick Petalas. Apache-2.0."""

import argparse
import copy
import hashlib
import itertools
import json
import struct
import sys
import tempfile
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import boundary

WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"


def sources(root):
    pins = json.loads(boundary.read_bounded(PACKAGE / "SOURCES.json"))["files"]
    for row in pins:
        if row["usage"] == "input":
            body = boundary.read_bounded(root / row["path"])
            boundary.require(
                hashlib.sha256(body).hexdigest() == row["sha256"], "input pin"
            )
    return json.loads(boundary.read_bounded(root / WORD, compressed=True))


def row_action(row, retained):
    value = 0
    for slot in row:
        value ^= 1 << retained[slot]
    return value


def exhaustive():
    """Independent coefficients, with every alias map of three slots to three helpers."""
    rows, cases = 0, 0
    for length in range(7):
        for row in itertools.product(range(3), repeat=length):
            word = {"v": 1, "R": 3, "ret": [2, 3, 4], "scatter": [list(row)]}
            original = copy.deepcopy(word)
            normal, count = boundary.normalize(word)
            boundary.require(
                word == original and count == length, "nonmutating boundary"
            )
            expected = [k for k in range(3) if row.count(k) % 2]
            boundary.require(
                normal["scatter"] == [expected], "independent counting oracle"
            )
            again, _ = boundary.normalize(normal)
            boundary.require(again == normal, "idempotence")
            for retained in itertools.product(range(3), repeat=3):
                boundary.require(
                    row_action(row, retained) == row_action(expected, retained),
                    "alias-safe scalar semantics",
                )
                cases += 1
            rows += 1
    return {"rows": rows, "alias_cases": cases, "max_row_length": 6}


def word_action(word):
    """Formal F2 inputs, independent of the selected symbolic checker."""
    n, v = 2 * word["v"] + word["R"], word["v"]
    values = [1 << i for i in range(n)]
    for section in ("D", "A", "scatter", "B", "C"):
        if section == "scatter":
            copied = [values[q] for q in word["ret"]]
            for t, row in enumerate(word["scatter"]):
                for slot in row:
                    values[v + t] ^= copied[slot]
        else:
            for _frame, target, operands in word[section]:
                for source in operands:
                    values[target] ^= values[source]
    return values


def record_action(raw, n):
    """Scalar projection only. Frame legality remains the authenticated checker's job."""
    boundary.require(len(raw) % 24 == 0 and len(raw) <= 100000 * 24, "record size")
    values, opened = [1 << i for i in range(n)] + [0], None
    for op, a, b, coefficient, _frame, _phase in struct.iter_unpack("<6i", raw):
        if op == 0:
            continue
        boundary.require(0 <= a <= n and 0 <= b <= n, "record register")
        if op == 1:
            boundary.require(a < n and (b < n or opened is not None), "ADD lifetime")
            if coefficient % 2:
                values[a] ^= values[b]
        elif op == 2:
            boundary.require(a < n and b == n and opened is None, "COPY lifetime")
            values[n], opened = values[a], a
        elif op == 3:
            boundary.require(opened == a and b == n, "ERASE source")
            values[n], opened = 0, None
        else:
            raise ValueError("record opcode")
    boundary.require(opened is None and values[n] == 0, "temporary not restored")
    return values[:n]


def fixture(word, name):
    changed = copy.deepcopy(word)
    if name == "paired_absent":
        changed["scatter"][0].extend([0, 0])
    elif name == "tripled_existing":
        changed["scatter"][0].extend([4, 4])
    elif name == "retained_alias":
        changed["ret"].append(changed["ret"][0])
        changed["scatter"][0].extend([9, 9])
    elif name == "odd_absent":
        changed["scatter"][0].extend([0, 0, 0])
    else:
        boundary.require(name == "baseline", "unknown fixture")
    return changed


def check_fixture(word, name, directory, root, bodies):
    changed = fixture(word, name)
    input_path, output = directory / (name + ".json"), directory / name
    input_path.write_text(json.dumps(changed), encoding="utf-8")
    result = boundary.execute("export", input_path, output, root, directory)
    raw = (output / "249-records.bin").read_bytes()
    n = 2 * word["v"] + word["R"]
    boundary.require(
        record_action(raw, n) == word_action(changed), "full word/export semantics"
    )
    boundary.require(word_action(changed) == word_action(word), "selected endpoint")
    legacy = directory / (name + "-legacy")
    boundary.delegate(
        bodies[boundary.EXPORTER], input_path, directory, "raw-exporter.py", legacy
    )
    legacy_raw = (legacy / "249-records.bin").read_bytes()
    result["legacy_scalar_agrees"] = record_action(legacy_raw, n) == word_action(
        changed
    )
    result["legacy_artifacts_equal"] = all(
        (legacy / p).read_bytes() == (output / p).read_bytes()
        for p in boundary.ARTIFACTS
    )
    return result


def audit(root, directory):
    word = sources(root)
    boundary.require(word["v"] == 111 and word["R"] == 439, "fixture dimensions")
    boundary.require(word["scatter"][0] == [4, 5, 6, 7, 8], "mutation site")
    bodies = boundary.scripts(root)
    results = {
        name: check_fixture(word, name, directory, root, bodies)
        for name in ("baseline", "paired_absent", "tripled_existing", "retained_alias")
    }
    baseline = results["baseline"]["export"]
    for name in ("paired_absent", "tripled_existing"):
        boundary.require(
            results[name]["export"] == baseline, "baseline byte preservation"
        )
    boundary.require(
        not results["paired_absent"]["legacy_scalar_agrees"], "old mismatch control"
    )
    boundary.require(
        results["baseline"]["legacy_artifacts_equal"], "selected artifact bytes"
    )
    boundary.require(
        results["tripled_existing"]["legacy_artifacts_equal"], "odd existing bytes"
    )
    boundary.require(
        results["retained_alias"]["export"]["copy_erase_pairs"] == 10,
        "aliases remain separately charged",
    )
    bad = directory / "odd-absent.json"
    bad.write_text(json.dumps(fixture(word, "odd_absent")), encoding="utf-8")
    try:
        boundary.execute("export", bad, directory / "rejected", root, directory)
    except ValueError as error:
        boundary.require(
            "checker.py rejected" in str(error), "actual checker rejection"
        )
    else:
        raise ValueError("wrong endpoint accepted")
    boundary.require(
        not (directory / "rejected").exists(), "rejected endpoint published output"
    )
    return {
        "status": "PASS_XOR_SCATTER_BOUNDARY",
        "columns": 661,
        "exhaustive": exhaustive(),
        "fixtures": results,
        "odd_absent_rejected": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="xor-boundary-audit-") as temporary:
        result = audit(boundary.ROOT, Path(temporary))
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        expected = json.loads((PACKAGE / "RESULT.json").read_bytes())
        boundary.require(result == expected, "deterministic evidence differs")
        print(result["status"], "columns=661 alias_safe=true no_supplier_adoption")


if __name__ == "__main__":
    main()

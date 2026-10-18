"""Source-bound scatter/export counterexample. Nick Petalas, Apache-2.0."""

import argparse
import copy
import gzip
import hashlib
import json
import struct
import subprocess
import sys
import tempfile
import types
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PREFIX = "research/e8-bit-p111-tuned/"
WORD = PREFIX + "tune/bitE8mut-p111-tuned.json.gz"
CHECKER = PREFIX + "code/xcheck_p.py"
EXPORTER = "research/e8-bit-carrier-skeleton/code/bit/export_records.py"
SELECTED = "research/community-frontier1094-audit/SELECTED-SOURCE.json"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sources(root):
    rows = json.loads((PACKAGE / "SOURCES.json").read_bytes())["files"]
    require(0 < len(rows) <= 24, "bounded source inventory")
    result = {}
    for row in rows:
        if row["usage"] != "input":
            continue
        path = row["path"]
        require(
            not Path(path).is_absolute() and ".." not in Path(path).parts,
            "contained input",
        )
        require(path not in result, "unique source input")
        target = root / path
        require(target.stat().st_size <= 5 * 1024 * 1024, "bounded source bytes")
        body = target.read_bytes()
        require(hashlib.sha256(body).hexdigest() == row["sha256"], "source: " + path)
        result[path] = body
    selected = json.loads(result[SELECTED])["files"]
    for path in (WORD, CHECKER, EXPORTER):
        require(
            hashlib.sha256(result[path]).hexdigest() == selected[path],
            "selected source binding: " + path,
        )
    return result


def checked_module(body):
    module = types.ModuleType("pinned_xcheck")
    # Exact authenticated module; retain its checks under an optimized caller.
    exec(compile(body, CHECKER, "exec", optimize=0), module.__dict__)  # noqa: S102
    return module


def validate_scatter(word):
    """Sufficient boundary guard; deliberately requires a simple support list."""
    rows, retained = word["scatter"], word["ret"]
    require(type(rows) is list and len(rows) == word["v"], "scatter row inventory")
    require(type(retained) is list and len(retained) == 9, "retained inventory")
    for row in rows:
        require(type(row) is list and len(row) <= len(retained), "scatter row shape")
        require(
            all(type(k) is int and 0 <= k < len(retained) for k in row), "scatter index"
        )
        require(len(row) == len(set(row)), "duplicate scatter index")


def symbolic(checker, word):
    _, labels, full, hypotheses, conclusions, _ = checker.check(word)
    require(labels["labels"] == 111 and full["columns"] == 661, "selected dimensions")
    require(all(hypotheses.values()) and all(conclusions.values()), "full interface")
    return {
        "columns": full["columns"],
        "scatter_terms": full["scatter_terms"],
        "hypotheses": hypotheses,
        "conclusions": conclusions,
    }


def export(body, word, directory):
    directory.mkdir()
    script = directory / "export_records.py"
    script.write_bytes(body)
    argument = directory / "word.json"
    argument.write_text(json.dumps(word))
    output = directory / "records"
    run = subprocess.run(
        [sys.executable, "-I", "-B", str(script), str(argument), str(output)],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    require(run.returncode == 0, "export failed: " + run.stderr)
    records = (output / "249-records.bin").read_bytes()
    require(
        0 < len(records) <= 30000 * 24 and len(records) % 24 == 0,
        "bounded aligned record stream",
    )
    return records


def replay(records, word):
    """Independent F2 row-bitsets, one bit for every arbitrary input column."""
    require(
        0 < len(records) <= 30000 * 24 and len(records) % 24 == 0,
        "bounded aligned record stream",
    )
    n, v = 2 * word["v"] + word["R"], word["v"]
    require(n == 661, "bounded column inventory")
    values = [1 << i for i in range(n)] + [0]
    opened = None
    for op, first, second, coefficient, _frame, _phase in struct.iter_unpack(
        "<6i", records
    ):
        require(0 <= first <= n and 0 <= second <= n, "record register")
        if op == 0:
            continue  # Frame movement does not alter this scalar projection.
        if op == 1:
            require(first != n and (second != n or opened is not None), "ADD shape")
            if coefficient % 2:
                values[first] ^= values[second]
        elif op == 2:
            require(opened is None and second == n and first < n, "COPY shape")
            values[n], opened = values[first], first
        elif op == 3:
            require(opened == first and second == n, "ERASE source binding")
            values[n], opened = 0, None
        else:
            raise ValueError("record opcode")
    require(opened is None and values[n] == 0, "temporary closes")
    expected = [1 << i for i in range(n)]
    for t in range(v):
        expected[v + t] ^= 1 << t
    differences = [
        (i, values[i] ^ expected[i]) for i in range(n) if values[i] != expected[i]
    ]
    return values, differences


def witness(values, differences, word):
    require(
        len(differences) == 1 and differences[0][0] == word["v"],
        "only first target differs",
    )
    register, delta = differences[0]
    require(delta >> 472 & 1, "independent dirty-input witness")
    return {
        "output_register": register,
        "input_column": 472,
        "actual_bit": (values[register] >> 472) & 1,
        "expected_bit": 0,
        "difference_support": [i for i in range(661) if delta >> i & 1],
    }


def audit(root, directory):
    data = sources(root)
    checker = checked_module(data[CHECKER])
    word = json.loads(gzip.decompress(data[WORD]))
    validate_scatter(word)
    original = symbolic(checker, word)
    require(
        0 not in word["scatter"][0] and word["ret"][0] == 472, "exact mutation site"
    )
    baseline = export(data[EXPORTER], word, directory / "baseline")
    _, bad = replay(baseline, word)
    require(not bad, "positive exported endpoint")
    mutant = copy.deepcopy(word)
    mutant["scatter"][0].extend([0, 0])
    changed = symbolic(checker, mutant)
    require(
        changed == {**original, "scatter_terms": original["scatter_terms"] + 2},
        "symbolic mutation is null except term count",
    )
    broken = export(data[EXPORTER], mutant, directory / "mutant")
    values, differences = replay(broken, mutant)
    counterexample = witness(values, differences, mutant)
    try:
        validate_scatter(mutant)
    except ValueError as error:
        guard = str(error)
    else:
        raise ValueError("boundary guard accepted duplicate")
    normalized = copy.deepcopy(mutant)
    normalized["scatter"][0] = [
        k for k in range(9) if mutant["scatter"][0].count(k) % 2
    ]
    require(normalized == word, "parity normalization recovers this exact source")
    repaired = export(data[EXPORTER], normalized, directory / "normalized")
    require(repaired == baseline, "normalized export byte identity")
    return {
        "status": "PASS_SELECTED_SCATTER_EXPORT_PARITY_AUDIT",
        "columns": 661,
        "retained_register": 472,
        "target_row": 0,
        "baseline": {
            "records": len(baseline) // 24,
            "records_sha256": hashlib.sha256(baseline).hexdigest(),
            "symbolic": original,
        },
        "mutant": {
            "appended_indices": [0, 0],
            "records": len(broken) // 24,
            "records_sha256": hashlib.sha256(broken).hexdigest(),
            "symbolic": changed,
            "witness": counterexample,
        },
        "duplicate_guard": guard,
        "normalized_export_equals_baseline": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="scatter-export-audit-") as temporary:
        result = audit(args.root, Path(temporary))
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        expected = json.loads((PACKAGE / "RESULT.json").read_bytes())
        require(
            json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
            "typed deterministic receipt",
        )
        print(result["status"], "columns=661 changed_targets=1 no_new_kappa")


if __name__ == "__main__":
    main()

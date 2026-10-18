#!/usr/bin/env python3
"""Compare the selected scatter word with one even duplicate on the real actions.

The symbolic replay XORs a retained total once per list occurrence. The exporter
emits one ADD when the index is merely present. This check runs both on the
pinned tuned word. It does not change kappa or the frozen exporter.
"""

import copy
import gzip
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
WORD = ROOT / "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
EXPORT = ROOT / "research/e8-bit-carrier-skeleton/code/bit/export_records.py"
CHECKER = ROOT / "research/e8-bit-p111-tuned/code/xcheck_p.py"
GENERATOR = ROOT / "research/e8-bit-p111-tuned/code/gen_p3.py"
EXPORT_LINE = "        if k in row: rec.append((1,v+t,temp,1,ZERO,3))"
REPLAY_LINE = "                        val[v + t] ^= copies[k]"
GENERATOR_LINE = "            for C in itertools.combinations(range(len(cvals)), k):"
MARKER = (
    "PASS_SCATTER_DUPLICATE_BOUNDARY v=111 rows=111 unique "
    "mutant_disagreements=1 triple_disagreements=0 repair_adopted=false no_new_kappa"
)


def fail(message):
    raise SystemExit("FAIL_SCATTER_DUPLICATE_BOUNDARY " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def unique_rows(rows):
    return all(len(row) == len(set(row)) for row in rows)


def odd_positive_multiplicities(rows):
    for row in rows:
        counts = Counter(row)
        if any(count % 2 == 0 for count in counts.values()):
            return False
    return True


def load_checker():
    spec = importlib.util.spec_from_file_location("xcheck_p", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def export_coefficients(word, scatter):
    """Run the pinned exporter's scatter statements and read the emitted ADDs."""
    lines = EXPORT.read_text(encoding="utf-8").splitlines()
    loop = "\n".join(lines[58:63])
    require(EXPORT_LINE.strip() in loop, "export loop is not the pinned membership action")
    record = []
    dimension = word["v"]
    namespace = {
        "c": {"ret": word["ret"], "scatter": scatter},
        "rec": record,
        "cur": [0] * (2 * dimension + word["R"]),
        "dim": [0],
        "ZERO": 0,
        "temp": 2 * dimension + word["R"],
        "v": dimension,
    }
    exec(loop, namespace)
    coefficients = [[0 for _ in word["ret"]] for _ in range(dimension)]
    retained = 0
    for opcode, destination, _source, _one, _zero, phase in record:
        if opcode == 2:
            retained += 1
        elif opcode == 1 and phase == 3:
            coefficients[destination - dimension][retained - 1] = 1
    require(retained == len(word["ret"]), "export did not visit every retained total")
    return coefficients


def symbolic_coefficients(checker, word):
    values, _frames, stats = checker.Word(word).replay(sections=("scatter",), frames_on=False)
    dimension = word["v"]
    retained = word["ret"]
    coefficients = [
        [(values[dimension + target] >> retained[index]) & 1 for index in range(len(retained))]
        for target in range(dimension)
    ]
    return coefficients, stats["scatter_terms"]


def disagreements(symbolic, exported):
    found = []
    for target, (left, right) in enumerate(zip(symbolic, exported)):
        for index, (symbolic_bit, exported_bit) in enumerate(zip(left, right)):
            if symbolic_bit != exported_bit:
                found.append([target, index])
    return found


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "research/e8-bit-carrier-skeleton/code/bit/export_records.py",
        "research/e8-bit-p111-tuned/code/xcheck_p.py",
        "research/e8-bit-p111-tuned/code/gen_p3.py",
        "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)
    export = EXPORT.read_text(encoding="utf-8")
    checker = CHECKER.read_text(encoding="utf-8")
    generator = GENERATOR.read_text(encoding="utf-8")
    require(EXPORT_LINE in export, "exporter no longer uses membership")
    require("validate_scatter" not in export, "an unexpected scatter guard is installed")
    require(REPLAY_LINE in checker, "symbolic replay no longer XORs once per occurrence")
    require(GENERATOR_LINE in generator, "generator no longer builds rows by combinations")


def evaluate():
    authenticate()
    checker = load_checker()
    with gzip.open(WORD, "rt", encoding="utf-8") as handle:
        selected = json.load(handle)
    require(selected["scatter"][0] == [4, 5, 6, 7, 8], "selected first row changed")
    require(unique_rows(selected["scatter"]), "a selected scatter row repeats an index")
    require(odd_positive_multiplicities(selected["scatter"]), "a selected row has even multiplicity")
    symbolic, terms = symbolic_coefficients(checker, selected)
    exported = export_coefficients(selected, selected["scatter"])
    baseline = disagreements(symbolic, exported)

    even = copy.deepcopy(selected)
    even["scatter"][0] = list(even["scatter"][0]) + [0, 0]
    even_symbolic, even_terms = symbolic_coefficients(checker, even)
    even_exported = export_coefficients(even, even["scatter"])
    even_gap = disagreements(even_symbolic, even_exported)

    triple = copy.deepcopy(selected)
    triple["scatter"][0] = list(triple["scatter"][0]) + [0, 0, 0]
    triple_symbolic, triple_terms = symbolic_coefficients(checker, triple)
    triple_exported = export_coefficients(triple, triple["scatter"])
    triple_gap = disagreements(triple_symbolic, triple_exported)
    return {
        "repair_adopted": False,
        "v": selected["v"],
        "rows": len(selected["scatter"]),
        "first_row": selected["scatter"][0],
        "selected_rows_unique": True,
        "selected_scatter_terms": terms,
        "selected_disagreements": baseline,
        "even_appended": [0, 0],
        "even_scatter_terms": even_terms,
        "even_disagreements": even_gap,
        "even_symbolic": even_symbolic[0][0],
        "even_export": even_exported[0][0],
        "uniqueness_accepts_selected": True,
        "uniqueness_rejects_even": not unique_rows(even["scatter"]),
        "triple_appended": [0, 0, 0],
        "triple_scatter_terms": triple_terms,
        "triple_disagreements": triple_gap,
        "triple_symbolic": triple_symbolic[0][0],
        "triple_export": triple_exported[0][0],
        "uniqueness_rejects_triple": not unique_rows(triple["scatter"]),
        "odd_multiplicity_accepts_triple": odd_positive_multiplicities(triple["scatter"]),
        "odd_multiplicity_rejects_even": not odd_positive_multiplicities(even["scatter"]),
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()

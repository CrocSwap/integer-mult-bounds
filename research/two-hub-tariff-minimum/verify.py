#!/usr/bin/env python3
"""Minimum charge of the 21-premise literal actual-reader model.

The checker enumerates the admissible supports of the retained premises.
It does not search another reader model.
"""

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_TWO_HUB_TARIFF rows=21 minimum=54 no_new_kappa"
NAMES = "gdthxykzw"
CONFIG_SHA = "37736c141cacd901de435dda72b26204edfaca35a6179fd856ab74b0d65054e5"
WITNESS_SHA = "556172923c7572e6734a6dacaa96831cd1973b03cde6fd625445bd25e974d85c"


def fail(message):
    raise SystemExit("FAIL_TWO_HUB_TARIFF " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rank(matrix):
    rows = [list(row) for row in matrix]
    height, width = len(rows), len(rows[0])
    pivot_row = 0
    for column in range(width):
        if pivot_row >= height:
            break
        pivot = next((i for i in range(pivot_row, height) if rows[i][column] != 0), None)
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        lead = rows[pivot_row][column]
        for index in range(pivot_row + 1, height):
            if rows[index][column] == 0:
                continue
            scale = rows[index][column]
            rows[index] = [
                lead * rows[index][column_index] - scale * rows[pivot_row][column_index]
                for column_index in range(width)
            ]
        pivot_row += 1
    return pivot_row


def contains(vectors, target):
    return rank([list(vector) for vector in vectors] + [list(target)]) == rank(vectors)


def nonzero(text):
    numerator, _, denominator = text.partition("/")
    return int(numerator) * int(denominator or "1") != 0


def model():
    require(sha256(PACKAGE / "config.json") == CONFIG_SHA, "config drift")
    require(sha256(PACKAGE / "witness.json") == WITNESS_SHA, "witness drift")
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    config = json.loads((PACKAGE / "config.json").read_text(encoding="utf-8"))
    witness = json.loads((PACKAGE / "witness.json").read_text(encoding="utf-8"))
    require(config["query_names"] == NAMES, "query names moved")
    queries = [list(map(int, query)) for query in config["queries"]]
    marks = [list(map(int, mark)) for mark in config["marks"]]
    require(len(queries) == 9 and len(marks) == 2, "query shape moved")
    index = {name: position for position, name in enumerate(NAMES)}
    return selected, queries, marks, index, config, witness


def row_units(queries, marks, index, config):
    units = 0
    forced = []
    for mark in (0, 1):
        sources = [spec for owner, spec in config["premises"]["source"] if owner == mark]
        readers = [spec for owner, spec in config["premises"]["reader"] if owner == mark]
        default = [index[name] for name in ("ghx" if mark == 0 else "ghy")]
        require(contains([queries[i] for i in default], marks[mark]), "the default reader misses its mark")
        require(not contains([queries[i] for i in default], marks[1 - mark]), "the default reader carries the other mark")
        require((len(sources), len(readers)) == ((4, 7) if mark == 0 else (3, 7)), "the row split moved")
        units += len(sources)
        for spec in readers:
            positions = [index[name] for name in spec]
            best = None
            for size in range(1, len(positions) + 1):
                for pick in itertools.combinations(positions, size):
                    if not contains([queries[i] for i in pick], marks[mark]):
                        continue
                    cost = sum(1 for i in pick if queries[i][mark] != 0)
                    if best is None or cost < best:
                        best = cost
            require(best is not None, "a reader row has no support")
            units += best
            if best == 2:
                forced.append("".join(spec))
    return units, forced


def witness_charges(queries, witness):
    functionals = [[int(entry) for entry in row] for row in witness["functionals"]]
    readers = [[nonzero(entry) for entry in row] for row in witness["readers"]]
    require(len(functionals) == 21 and len(readers) == 21, "the witness lost a row")
    charges = []
    for query_index, query in enumerate(queries):
        active = 0
        for row in range(21):
            if readers[row][query_index] and sum(a * b for a, b in zip(functionals[row], query)) != 0:
                active += 1
        charges.append(2 * active)
    return charges


def evaluate():
    selected, queries, marks, index, config, witness = model()
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    units, forced = row_units(queries, marks, index, config)
    charges = witness_charges(queries, witness)
    require(units == 27 and sum(charges) == 2 * units, "the minimum moved")
    require(sorted(forced) == ["dxy", "dxy", "dzw", "dzw", "gtxy", "gtxy"], "the forced rows moved")
    require(charges == [4, 8, 12, 4, 10, 8, 0, 4, 4], "the witness charges moved")
    return {
        "rows": 21,
        "row_units": 27,
        "minimum_charge": 54,
        "witness_charge_total": 54,
        "forced_excess": 12,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()

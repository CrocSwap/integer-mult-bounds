#!/usr/bin/env python3
"""Agreement of the checker and exporter gate operators.

The checker enumerates the published domain. It does not scan the selected word.
"""

import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_GATE_OPERAND_AGREEMENT divergent=3492 checker=1230 no_new_kappa"
CHECKER = "research/e8-bit-p111-tuned/code/xcheck_p.py"
EXPORTER = "research/e8-bit-carrier-skeleton/code/bit/export_records.py"
REGISTERS = 6
MAX_LENGTH = 4


def fail(message):
    raise SystemExit("FAIL_GATE_OPERAND_AGREEMENT " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    require(set(pinned) == {CHECKER, EXPORTER}, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)
    checker = (ROOT / CHECKER).read_text(encoding="utf-8")
    exporter = (ROOT / EXPORTER).read_text(encoding="utf-8")
    require("acc ^= val[s]" in checker and "val[d] ^= acc" in checker, "the checker write moved")
    require("for s in srcs: rec.append((1,d,s,1,f,ph))" in exporter, "the exporter add moved")


def checker_value(destination, sources, state):
    accumulator = 0
    for source in sources:
        accumulator ^= state[source]
    updated = list(state)
    updated[destination] ^= accumulator
    return updated


def exporter_value(destination, sources, state):
    updated = list(state)
    for source in sources:
        updated[destination] ^= updated[source]
    return updated


def simulated(destination, sources):
    state = [1 << register for register in range(REGISTERS)]
    return checker_value(destination, sources, state)[destination] == exporter_value(destination, sources, state)[destination]


def predicted(destination, sources):
    multiplicity = sources.count(destination)
    if multiplicity == 0:
        return True
    last = len(sources) - 1 - sources[::-1].index(destination)
    if multiplicity % 2 == 0:
        return False
    return all(count % 2 == 0 for count in Counter(sources[:last]).values())


def evaluate():
    authenticate()
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    pairs = destination_free = divergent = agreeing_in = checker_accepted = simple_admits = 0
    for destination in range(REGISTERS):
        for length in range(MAX_LENGTH + 1):
            for index in range(REGISTERS ** length):
                sources = []
                cursor = index
                for _ in range(length):
                    sources.append(cursor % REGISTERS)
                    cursor //= REGISTERS
                agrees = simulated(destination, sources)
                require(agrees == predicted(destination, sources), "the operators left the contract")
                pairs += 1
                if destination not in sources:
                    destination_free += 1
                    require(agrees, "a destination-free gate diverges")
                elif agrees:
                    agreeing_in += 1
                else:
                    divergent += 1
                if sources and len({destination, *sources}) == len(sources) + 1:
                    checker_accepted += 1
                    require(agrees, "the checker accepts a divergent gate")
                if len(set(sources)) == len(sources) and not agrees:
                    simple_admits += 1
    require(checker_accepted == REGISTERS * (5 + 20 + 60 + 120), "the checker count left its closed form")
    require(pairs == 9330 and destination_free == 4686 and divergent == 3492, "the domain counts moved")
    require(agreeing_in == 1152 and simple_admits == 1350, "the residue counts moved")
    return {
        "pairs": pairs,
        "dest_free": destination_free,
        "divergent": divergent,
        "agreeing_dest_in": agreeing_in,
        "checker_accepted": checker_accepted,
        "simple_admits": simple_admits,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()

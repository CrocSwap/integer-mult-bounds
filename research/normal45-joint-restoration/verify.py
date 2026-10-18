#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent complete free-group/dyadic replay of PR2942's literal words.

No predecessor code is imported. Rows use one integer denominator rather than
one Fraction per coefficient. Every dirty input is a separate formal column.
Prepared for Ross Richardson with substantial OpenAI Codex assistance.
"""
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
import copy
import gzip
import hashlib
import json

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PIVOTS = (249, 267, 251, 265)


def require(ok, message):
    if not ok:
        raise ValueError(message)


class Row:
    """Sparse sum a[word,input] * K_word(input) / 2**exponent."""
    __slots__ = ("terms", "exponent")

    def __init__(self, terms=None, exponent=0):
        self.terms = {} if terms is None else terms
        self.exponent = exponent
        self.normalize()

    def normalize(self):
        if not self.terms:
            self.exponent = 0
            return
        if self.exponent < 0:
            self.terms = {key: value << -self.exponent for key, value in self.terms.items()}
            self.exponent = 0
        if self.exponent:
            shift = min(self.exponent, min((abs(n) & -abs(n)).bit_length() - 1
                                           for n in self.terms.values()))
            if shift:
                self.terms = {key: value >> shift for key, value in self.terms.items()}
                self.exponent -= shift

    @classmethod
    def unit(cls, register):
        return cls({((), register): 1})

    def scaled(self, coefficient):
        q = Fraction(coefficient)
        require(q.denominator & (q.denominator - 1) == 0, "dyadic coefficient")
        return Row({key: value * q.numerator for key, value in self.terms.items() if value * q.numerator},
                   self.exponent + q.denominator.bit_length() - 1)

    def plus(self, other, coefficient=1):
        other = other.scaled(coefficient)
        exponent = max(self.exponent, other.exponent)
        result = {key: value << (exponent - self.exponent) for key, value in self.terms.items()}
        for key, value in other.terms.items():
            value = result.get(key, 0) + (value << (exponent - other.exponent))
            if value:
                result[key] = value
            else:
                result.pop(key, None)
        return Row(result, exponent)

    def left(self, operator):
        result = {}
        for (word, column), value in self.terms.items():
            new = word[1:] if word and word[0] == -operator else (operator,) + word
            result[new, column] = value
        return Row(result, self.exponent)

    def __eq__(self, other):
        return self.exponent == other.exponent and self.terms == other.terms


def inverse(gate):
    result = list(gate)
    if gate[0] == "add":
        result[3] = -result[3]
    elif gate[0] == "scale":
        result[2], result[3] = result[3], result[2]
    elif gate[0] == "warp":
        result[2] = -result[2]
    else:
        raise ValueError("unknown invertible primitive")
    return result


def registers(gate):
    return gate[1:3] if gate[0] == "add" else gate[1:2]


def bword(word):
    at = defaultdict(list)
    for index, record in enumerate(word["warps"], 1):
        require(0 <= record[0] <= len(word["B"]), "warp position")
        at[record[0]].append(["warp", record[1], index])
    result = []
    for index in range(len(word["B"]) + 1):
        result.extend(at[index])
        if index < len(word["B"]):
            result.append(word["B"][index])
    return result


def derived_cleanup(word):
    """Reverse the entire non-target middle; use private zero slots for cold ends."""
    size = 224 + word["report"]["R"]
    cold = set(map(int, word["helper_final"]))
    middle = word["A"][word["prelude_events"]:] + bword(word) + word["restore"]
    recorded = [g for g in middle if g[0] == "warp" or not 112 <= g[1] < 224]
    result = []
    full = [256, 128, 64, 32, 16, 8, 4, 2, 1]
    for gate in reversed(recorded):
        g = inverse(gate)
        if g[0] == "warp":
            g = g[:3] + [full]
        else:
            g[-1] = full
        for index in (1, 2) if g[0] == "add" else (1,):
            if g[index] in cold:
                g[index] += size
        result.append(g)
    return result


def program(word):
    corrections = [["correction", c["target"], c["source"], c["operator_word"], c["coefficient"]]
                   for c in word["initial_corrections"]]
    return corrections + word["precondition"] + word["compensation"] + word["A"] + word["cut"] + bword(word) + word["restore"]


def action(rows, gate, dual=False):
    kind = gate[0]
    if kind == "add":
        target, source = gate[1:3]
        q = Fraction(gate[3], gate[4])
        require(target != source, "self-add")
        if dual:
            target, source, q = source, target, -q
        rows[target] = rows[target].plus(rows[source], q)
    elif kind == "scale":
        q = Fraction(gate[2], gate[3])
        require(q != 0, "zero scale")
        rows[gate[1]] = rows[gate[1]].scaled(1 / q if dual else q)
    elif kind == "warp":
        op = gate[2]
        require(op != 0, "zero operator")
        if dual:
            op = (1 if op > 0 else -1) * (1000 + abs(op))
        rows[gate[1]] = rows[gate[1]].left(op)
    elif kind == "correction":
        target, source, operators, coefficient = gate[1:]
        q = Fraction(coefficient)
        if dual:
            target, source, q = source, target, -q
            # K_a K_b -> (K_a K_b)^T = D_b^-1 D_a^-1.
            operators = [-(1 if op > 0 else -1) * (1000 + abs(op)) for op in operators]
        else:
            operators = list(reversed(operators))
        row = rows[source]
        for op in operators:
            row = row.left(op)
        rows[target] = rows[target].plus(row, q)
    else:
        raise ValueError("unknown primitive " + str(kind))


def replay(word, dual=False, check_cleanup=True, dirty_buffer=None):
    size = 224 + word["report"]["R"]
    live = sorted(set(range(size)) - set(word["removed"]))
    require(len(live) == 632 and size == 704, "source domain")
    cold = set(map(int, word["helper_final"]))
    require(cold <= set(live) - set(range(224)), "cold helper domain")
    if check_cleanup:
        require(word["cleanup"] == derived_cleanup(word), "literal inverse-cleanup recipe")
    for g in word["cleanup"]:
        require(not (set(registers(g)) & cold), "direct cleanup touch of a cold endpoint")
    rows = {r: Row.unit(r) for r in live}
    rows.update({r + size: Row() for r in cold})
    if dirty_buffer is not None:
        rows[dirty_buffer + size] = Row.unit(dirty_buffer + size)
    for gate in program(word):
        action(rows, gate, dual)
    if not dual:
        for r in range(112):
            require(rows[r + 112] == Row.unit(r + 112).plus(Row.unit(r)), "target at delivery cut " + str(r))
        for r in cold:
            require(rows[r] == Row.unit(r), "isolated cold row " + str(r))
        for r, row in rows.items():
            require(all(column not in cold or column == r for _, column in row.terms), "cold column leakage at delivery cut")
        require(all(rows[r + size] == Row() for r in cold), "private zero at cleanup entry")
    max_terms = max(len(row.terms) for row in rows.values())
    for gate in word["cleanup"]:
        action(rows, gate, dual)
    for r in live:
        expected = Row.unit(r)
        if dual and r < 112:
            expected = expected.plus(Row.unit(r + 112), -1)
        if not dual and 112 <= r < 224:
            expected = expected.plus(Row.unit(r - 112))
        require(rows[r] == expected, "complete endpoint " + str((dual, r)))
    for r in sorted(cold):
        row = rows[r + size]
        if row.terms:
            key = min(row.terms)
            coefficient = Fraction(row.terms[key], 1 << row.exponent)
            raise ValueError("private zero at return " + str(r + size) + ": " + str(coefficient)
                             + " * K" + str(key[0]) + " input[" + str(key[1]) + "]")
    return {"independent_inputs": len(live), "restored_helpers": len(cold), "private_zero_buffers": len(cold),
            "orientation": "inverse-transpose" if dual else "forward", "largest_delivery_row_terms": max_terms,
            "literal_cleanup_gates": len(word["cleanup"])}


def source_data():
    pins = json.loads((PACKAGE / "SOURCES.json").read_bytes())
    values = {}
    for entry in pins["files"]:
        if entry["usage"] != "input":
            continue
        raw = (ROOT / entry["path"]).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == entry["sha256"], "source SHA256 " + entry["path"])
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(blob == entry["git_blob"], "source Git blob " + entry["path"])
        values[Path(entry["path"]).name] = json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)
    require(len(values) == 8, "all eight source inputs")
    return values


def rejected(word, label, expected_error, **kwargs):
    try:
        replay(word, **kwargs)
    except ValueError as error:
        require(str(error).startswith(expected_error), "control rejected by unintended rule: " + label + ": " + str(error))
        return {"control": label, "rejected_by": str(error)}
    raise RuntimeError("unexpected mutant acceptance: " + label)


def algebra_sanity():
    """Small exact controls for denominator alignment and operator order."""
    samples = [Fraction(a, 1 << k) for a in range(-3, 4) for k in range(4)]
    for a in samples:
        for b in samples:
            actual = Row.unit(0).scaled(a).plus(Row.unit(0).scaled(b))
            expected = Row.unit(0).scaled(a + b)
            require(actual == expected, "independent rational sum fixture")
    ab = Row.unit(0).left(2).left(1)
    ba = Row.unit(0).left(1).left(2)
    require(ab != ba and ab.left(-1).left(-2) == Row.unit(0), "noncommuting free-group fixture")
    rows = {0: Row.unit(0), 1: Row.unit(1)}
    action(rows, ["correction", 1, 0, [1, 2], "3/8"], True)
    expected = Row.unit(0).plus(Row({((-1002, -1001), 1): -3}, 3))
    require(rows[0] == expected and rows[1] == Row.unit(1), "two-symbol adjoint correction order")
    return {"rational_sums": len(samples) ** 2, "noncommuting_word": True, "two_symbol_adjoint": True}


def main():
    arithmetic = algebra_sanity()
    data = source_data()
    results, controls = {}, []
    for tag in ("base", "extra"):
        parent, final = (data[f"{kind}-{tag}.json.gz"] for kind in ("PARENT", "WORD"))
        require(set(map(int, final["helper_final"])) == set(map(int, parent["helper_final"])) | set(PIVOTS), "four added cold ends")
        require(all(final["helper_final"][h] == U for h, U in parent["helper_final"].items()), "inherited cold endpoints")
        require(len(parent["helper_final"]) == 82 and len(final["helper_final"]) == 86, "private buffer invoice")
        results[tag] = {kind: [replay(word), replay(word, True)] for kind, word in (("parent", parent), ("final", final))}

        bad = copy.deepcopy(final)
        bad["compensation"] = copy.deepcopy(parent["compensation"])
        controls.append(rejected(bad, tag + ":stale-parent-compensation", "target at delivery cut 0"))

        bad = copy.deepcopy(final)
        length = sum(len(data[f"TRANSFORM-{h}.json"]["after"]) for h in PIVOTS)
        chunks = [data[f"TRANSFORM-{h}.json"]["after"] for h in PIVOTS]
        bad["restore"][-length:] = [g for chunk in reversed(chunks) for g in chunk]
        bad["cleanup"] = derived_cleanup(bad)
        controls.append(rejected(bad, tag + ":reversed-terminal-blocks", "isolated cold row 249"))

        bad = copy.deepcopy(final)
        del bad["cleanup"][0]
        # The first inverse gate reads a still-zero private buffer in the
        # forward orientation. Its dual writes that buffer, so both are needed.
        replay(bad, check_cleanup=False)
        controls.append(rejected(bad, tag + ":forward-invisible-cleanup-omission", "private zero at return 969:", dual=True, check_cleanup=False))

        bad = copy.deepcopy(final)
        del bad["cleanup"][-1]
        controls.append(rejected(bad, tag + ":last-cleanup-omission", "private zero at return 969:", check_cleanup=False))

        bad = copy.deepcopy(final)
        bad["initial_corrections"][0]["operator_word"][0] *= -1
        controls.append(rejected(bad, tag + ":inverted-anticipatory-operator", "target at delivery cut 3"))

        controls.append(rejected(final, tag + ":dirty-private-buffer", "private zero at cleanup entry", dirty_buffer=PIVOTS[0]))

        # Algebraic positive control; it does not claim canonical recipe equality.
        split = copy.deepcopy(final)
        first = split["cleanup"].pop(0)
        require(first[0] == "add", "positive fixture is an addition")
        half = list(first)
        half[4] *= 2
        split["cleanup"][:0] = [list(half), list(half)]
        replay(split, check_cleanup=False)
        replay(split, True, check_cleanup=False)
    print(json.dumps({"status": "PASS_NORMAL45_JOINT_RESTORATION", "arithmetic_fixtures": arithmetic, "providers": results,
                      "negative_controls": controls, "positive_split_controls": 4,
                      "scope": "Finite exact free-group algebra, all 632 arbitrary original inputs and declared zero private buffers; no native/owner/outer admission or new kappa."}, sort_keys=True))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""The other rank-2 coframed carriers do not beat the published #5718 prefix.

On the pinned PR5713 word, every rank-2 coframed main-partner carrier with a
legal dyadic coefficient and empty-frame support is one of three carriers on
helper 708 at frame 602. All three produce the same terminal output defect.
The published partner 154 has the strictly cheapest ordinary prefix.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
"""
import gzip
import json
import tarfile
from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_TAR = ROOT / "research/p104-two-boundary-helper-split/inputs/pr5713-source.tar"
SOURCE_MEMBER = "research/p104-temporal-updates/WORD.json.gz"
SOURCE_SHA = "32adce6656e49aa020d3e6317f1c45c11fccadeeb67a8d506172d101703d2138"
PIVOT = 708
FRAME = 602
EXPECTED = {
    (PIVOT, 154, "1/2", FRAME): (13657, 14336, 87, 1118),
    (PIVOT, 127, "-1/2", FRAME): (13653, 14139, 89, 1142),
    (PIVOT, 119, "1/4", FRAME): (13658, 13658, 104, 1612),
}
COLUMN = {126: Fraction(-2), 188: Fraction(2), 708: Fraction(1)}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def combine(left, right, coefficient):
    for index, value in tuple(right.items()):
        updated = left.get(index, Fraction(0)) + coefficient * value
        if updated:
            left[index] = updated
        else:
            left.pop(index, None)


def apply(rows, event):
    operation, destination = event[:2]
    if operation == "MOVE":
        return
    if operation in ("INIT", "CLEAR"):
        rows[destination] = {}
    elif operation == "SCALE":
        rows[destination] = {index: Fraction(event[-2]) * value for index, value in rows[destination].items()}
    else:
        if operation == "COPY":
            rows[destination] = {}
        combine(rows[destination], rows[event[2]], Fraction(event[-2]))


def legal(coefficient):
    if coefficient == 0:
        return False
    denominator = coefficient.denominator
    return denominator & (denominator - 1) == 0 and abs(coefficient) + 1 < 2**16


def scalar_cost(coefficient):
    numerator = abs(coefficient.numerator)
    denominator = coefficient.denominator
    return 2 * (2 + numerator.bit_length() + numerator.bit_count() + denominator.bit_length() - 1)


def load_source():
    with tarfile.open(SOURCE_TAR) as archive:
        member = archive.extractfile(SOURCE_MEMBER)
        need(member is not None, "PR5713 source word is missing")
        payload = member.read()
    word = json.loads(gzip.decompress(payload))
    encoded = json.dumps(word, sort_keys=True, separators=(",", ":")).encode()
    need(sha256(encoded).hexdigest() == SOURCE_SHA, "PR5713 canonical source hash")
    return word


def solve(pivot_row, partner_row, partner, pivot, empty, public):
    coefficient = None

    def bind(value):
        nonlocal coefficient
        if coefficient is None:
            coefficient = value
            return True
        return coefficient == value

    if partner_row.get(pivot, 0) != 0:
        if not bind((1 - pivot_row.get(pivot, 0)) / partner_row[pivot]):
            return None
    elif pivot_row.get(pivot, 0) != 1:
        return None
    for index in set(pivot_row) | set(partner_row):
        if index < public and index in empty:
            continue
        left = pivot_row.get(index, 0)
        right = partner_row.get(index, 0)
        if right == 0:
            if left != 0:
                return None
        elif not bind(-left / right):
            return None
    if coefficient is None or not legal(coefficient):
        return None
    if pivot_row.get(partner, 0) + coefficient * partner_row.get(partner, 0) == 0:
        return None
    return coefficient


def census(word):
    public = word["public"]
    total = public + word["owned_fields"]
    main = set(word["live"]) | {index + 112 for index in word["live"]}
    empty = {index for index in range(public) if word["initial"][index] == 3}
    rank = [len(basis) for basis in word["frames"]]
    final_rank = [rank[word["final"][index]] for index in range(public)]
    rows = [{index: Fraction(1)} for index in range(total)]
    current = list(word["initial"]) + [None] * word["owned_fields"]
    occupants = defaultdict(set)
    for index, frame in enumerate(current):
        if frame is not None:
            occupants[frame].add(index)
    found = {}
    free = 0
    for index, event in enumerate(word["program"]):
        operation, register = event[:2]
        if operation == "MOVE":
            occupants[event[2]].discard(register)
            occupants[event[3]].add(register)
            current[register] = event[3]
        elif operation == "INIT":
            current[register] = event[2]
            occupants[event[2]].add(register)
            apply(rows, event)
        elif operation == "CLEAR":
            occupants[current[register]].discard(register)
            current[register] = None
            apply(rows, event)
        else:
            apply(rows, event)
        for frame, people in occupants.items():
            if len(people) < 2 or rank[frame] != 2:
                continue
            helpers = [
                person for person in people
                if person < public and person not in main and word["initial"][person] == 3
                and final_rank[person] == 9 and rows[person].get(person) == 1
            ]
            partners = [person for person in people if person in main]
            if not helpers or not partners:
                continue
            for pivot in helpers:
                for partner in partners:
                    partner_row = rows[partner]
                    pivot_row = rows[pivot]
                    if partner_row.get(pivot, 0) == 0 and pivot_row.get(pivot, 0) == 1:
                        if all((j < public and j in empty) or pivot_row.get(j, 0) == 0 for j in pivot_row) and all(
                            (j < public and j in empty) or partner_row.get(j, 0) == 0 for j in partner_row
                        ):
                            free += 1
                            continue
                    coefficient = solve(pivot_row, partner_row, partner, pivot, empty, public)
                    if coefficient is None:
                        continue
                    key = (pivot, partner, str(coefficient), frame)
                    found.setdefault(key, []).append(index)
    return found, free, rows, current


def nuisance(word, cut, partner, coefficient):
    public = word["public"]
    total = public + word["owned_fields"]
    rows = [{index: Fraction(1)} for index in range(total)]
    for event in word["program"][:cut + 1]:
        apply(rows, event)
    carrier = dict(rows[PIVOT])
    combine(carrier, rows[partner], coefficient)
    combine(carrier, {PIVOT: Fraction(1)}, Fraction(-1))
    need(PIVOT not in carrier and rows[PIVOT].get(PIVOT) == 1, "pivot coefficient")
    return carrier


def prefix_cost(carrier, restore):
    return sum(scalar_cost(value) for value in carrier.values()) + scalar_cost(Fraction(-2)) + scalar_cost(Fraction(2)) + scalar_cost(restore)


def suffix_column(word, cut):
    total = word["public"] + word["owned_fields"]
    column = [Fraction(0)] * total
    column[PIVOT] = Fraction(1)
    for event in word["program"][cut + 1:]:
        operation, destination = event[:2]
        if operation == "MOVE":
            continue
        if operation in ("INIT", "CLEAR"):
            column[destination] = Fraction(0)
        elif operation == "SCALE":
            column[destination] *= Fraction(event[-2])
        elif operation == "COPY":
            column[destination] = Fraction(event[-2]) * column[event[2]]
        else:
            column[destination] += Fraction(event[-2]) * column[event[2]]
    return {index: value for index, value in enumerate(column) if value}


def output_defect(word, cut, partner, coefficient):
    public = word["public"]
    total = public + word["owned_fields"]
    fresh = public
    carrier = nuisance(word, cut, partner, coefficient)
    program = [["ADD", PIVOT, index, str(-value), 3] for index, value in sorted(carrier.items())]
    program.extend([["ADD", 126, PIVOT, "-2", 3], ["ADD", 188, PIVOT, "2", 3]])

    def rename(register, index):
        if index > cut and register == PIVOT:
            return fresh
        return register + 1 if register >= public else register

    for index, original in enumerate(word["program"]):
        event = list(original)
        event[1] = rename(event[1], index)
        if event[0] in ("ADD", "COPY"):
            event[2] = rename(event[2], index)
        program.append(event)
        if index == cut:
            program.append(["ADD", PIVOT, partner, str(coefficient), FRAME])
    replayed = [{index: Fraction(1)} for index in range(total + 1)]
    for event in program:
        apply(replayed, event)
    live = set(word["live"])
    defects = {}
    for index, row in enumerate(replayed):
        expected = {index: Fraction(1)} if index < public + 1 else {}
        if index - 112 in live:
            expected[index - 112] = Fraction(1)
        if row != expected:
            difference = dict(row)
            combine(difference, expected, Fraction(-1))
            defects[index] = tuple(sorted((key, str(value)) for key, value in difference.items()))
    need(all(event[0] != "MOVE" for event in program[:len(carrier) + 3]), "prefix inserts only ADDs")
    return defects


def main():
    word = load_source()
    found, free, _rows, _current = census(word)
    need(word["program"][14140][:4] == ["MOVE", 127, 602, 637], "127 leaves frame 602 at 14140")
    need(word["program"][14330][:4] == ["MOVE", 119, 602, 684], "published cut moves 119 at 14330")
    need(word["program"][14337][:4] == ["MOVE", 154, 602, 685], "154 leaves frame 602 at 14337")
    need(free == 0, "a rank-2 carrier had a free coefficient")
    need(set(found) == set(EXPECTED), "rank-2 carrier set")
    published = output_defect(word, 14330, 154, Fraction(1, 2))
    need(set(published) == {126, 188, 743}, "published defect rows")
    for key, (start, end, terms, cost) in EXPECTED.items():
        pivot, partner, text, frame = key
        coefficient = Fraction(text)
        need(found[key] == list(range(start, end + 1)), "carrier span " + text)
        column = suffix_column(word, end)
        need(column == COLUMN, "suffix column " + text)
        carrier = nuisance(word, end, partner, coefficient)
        need(len(carrier) == terms, "nuisance terms " + text)
        need(prefix_cost(carrier, coefficient) == cost, "prefix cost " + text)
        need(all(legal(value) for value in carrier.values()), "nuisance coefficients " + text)
        if key == (PIVOT, 154, "1/2", FRAME):
            opening = nuisance(word, start, partner, coefficient)
            middle = nuisance(word, 14330, partner, coefficient)
            need(start <= 14330 <= end, "published cut lies in the 154 span")
            need(opening == middle == carrier, "154 nuisance is constant on its span")
            need(output_defect(word, end, partner, coefficient) == published, "154 endpoint defect")
        else:
            need(output_defect(word, end, partner, coefficient) == published, "alternate endpoint defect " + text)
    need(EXPECTED[(PIVOT, 154, "1/2", FRAME)][3] < EXPECTED[(PIVOT, 127, "-1/2", FRAME)][3] < EXPECTED[(PIVOT, 119, "1/4", FRAME)][3], "154 is the unique cheapest prefix")
    # The same meeting does not admit the unit coefficient: the solver returns one coefficient or none.
    need((PIVOT, 154, "1", FRAME) not in found, "unit coefficient is a different carrier")
    print(
        "PASS_P104_OTHER_BOUNDARY_PAIR carriers=3 output=identical "
        "prefix_scalar=154:1118,127:1142,119:1612 minimum=154 "
        "target=H2+H7-H9 paid_moves_added=0 no_new_kappa=true"
    )


if __name__ == "__main__":
    main()

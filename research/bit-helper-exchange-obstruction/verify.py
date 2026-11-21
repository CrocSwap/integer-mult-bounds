#!/usr/bin/env python3
"""Check one-chart helper swaps on the deposited paid-packet graph."""
import gzip
import hashlib
import itertools
import json
import runpy
from collections import defaultdict
from fractions import Fraction
from functools import cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORD = "d3aa4426fa8fe7dc167270d01f2515184f2bff6a82744a14e941c5dd3afca27d"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate_sources():
    for name, origin in json.loads((HERE / "ORIGINS.json").read_bytes()).items():
        data = (HERE / name).read_bytes()
        blob = f"blob {len(data)}\0".encode() + data
        require(hashlib.sha256(data).hexdigest() == origin["sha256"], name)
        require(hashlib.sha1(blob).hexdigest() == origin["git_blob"], name)


def improving_pairs(word):
    frames = word["frames"]

    @cache
    def grade(a, b):
        low, high = sorted((frames[str(a)], frames[str(b)]), key=lambda f: f["dim"])
        size = high["dim"] - low["dim"]
        if size == 0:
            return 0
        for row in low["B"]:
            for dual in high["A"]:
                if sum(Fraction(x) * Fraction(y) for x, y in zip(row, dual, strict=True)):
                    return 0
        return size

    starts, ends = word["start"], word["final"]
    owners = range(222, word["public"])
    grades = {i: grade(starts[i], ends[i]) for i in owners}
    require(min(grades.values()) > 0, "existing helpers must be nested")
    pairs = []
    for i, j in itertools.combinations(owners, 2):
        old_low, old_high = sorted((grades[i], grades[j]))
        if old_high - old_low < 2 or starts[i] == starts[j] or ends[i] == ends[j]:
            continue
        a, b = grade(starts[i], ends[j]), grade(starts[j], ends[i])
        if min(a, b) > old_low and a + b == old_low + old_high:
            pairs.append((i, j))
    return pairs


def echelon(rows):
    basis = {}
    for row in rows:
        while row:
            pivot = (row & -row).bit_length() - 1
            if pivot not in basis:
                basis[pivot] = row
                break
            row ^= basis[pivot]
    return basis


def residues(rows, owners):
    basis = echelon(rows)
    ordered = sorted(basis.items())
    result = {}
    for i in owners:
        row = 1 << i
        for pivot, vector in ordered:
            if (row >> pivot) & 1:
                row ^= vector
        result[i] = row
    return len(basis), result


def main():
    authenticate_sources()
    edge = runpy.run_path(str(HERE / "sources/bit_native.py"))
    word = json.loads(gzip.decompress((HERE / "sources/WORD.json.gz").read_bytes()))
    require(edge["digest"](word) == WORD, "canonical binary word")
    initial, final, moves, rows, _ = edge["extract"](word)
    order = edge["schedule"](initial, final, moves, rows)
    columns = edge["basis"](initial, moves, rows, order)
    values = {owner: 1 << owner for owner in initial}
    for packet in order:
        values[packet] = edge["combine"](rows[packet], values)

    arrivals, departures = defaultdict(list), defaultdict(list)
    for owner in initial:
        arrivals[initial[owner]].append(1 << owner)
        departures[final[owner]].append(1 << owner)
    for packet, (source, receiver) in moves.items():
        arrivals[receiver].append(values[packet])
        departures[source].append(columns[packet])

    pairs = improving_pairs(word)
    owners = sorted({i for pair in pairs for i in pair})
    expected = json.loads((HERE / "EXPECTED.json").read_bytes())
    packed = json.dumps(pairs, separators=(",", ":")).encode()
    require(len(pairs) == expected["pairs"] == 3112, "profitable pair count")
    require(hashlib.sha256(packed).hexdigest() == expected["pair_sha256"], "pair identity")

    charts, matches = [], []
    for chart in sorted(map(int, word["frames"])):
        read_rank, read = residues(arrivals[chart], owners)
        write_rank, write = residues(departures[chart], owners)
        accepted = [(i, j) for i, j in pairs if read[i] == read[j] and write[i] == write[j]]
        charts.append([chart, read_rank, write_rank, len(accepted)])
        matches.extend([chart, i, j] for i, j in accepted)
    require(charts == expected["charts"] and len(charts) == 636, "two quotient ranks at every chart")
    require(matches == expected["compatible"] == [], "one-chart necessity")
    # Matching only the read side is insufficient. Adding the missing response
    # on the write side must turn this small controlled instance into a match.
    _, left = residues([3], (0, 1))
    _, unavailable = residues([], (0, 1))
    _, restored = residues([3], (0, 1))
    require(left[0] == left[1] and unavailable[0] != unavailable[1]
            and restored[0] == restored[1], "one-sided and restored controls")
    print("PASS_PACKET_GRAPH_EXCHANGE_EXCLUSION 3112 pairs, 636 charts, 0 matches")


if __name__ == "__main__":
    main()

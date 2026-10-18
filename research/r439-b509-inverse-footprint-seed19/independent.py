#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Literal Boolean-table / integer-minor check, without importing verify.py.

Written by the same OpenAI Codex session for @CubeJerry. Separate code and
representations are not independent human review or a proof-assistant proof.
"""
from collections import Counter
from itertools import permutations
from pathlib import Path
import gzip
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def gram_determinant(vectors):
    """Leibniz determinant of an integer Gram matrix; no rational elimination."""
    gram = [[sum(x * y for x, y in zip(a, b)) for b in vectors] for a in vectors]
    total = 0
    for p in permutations(range(len(vectors))):
        sign = (-1) ** sum(p[i] > p[j] for i in range(len(p)) for j in range(i + 1, len(p)))
        term = sign
        for i, j in enumerate(p):
            term *= gram[i][j]
        total += term
    return total


def span_rank(roots, lines):
    selected = []
    for root in sorted(set(roots)):
        if gram_determinant([*selected, lines[root]]) > 0:
            selected.append(lines[root])
    return len(selected)


def boolean_table(gates, registers):
    result = []
    for x in range(2 ** len(registers)):
        values = {r: (x // 2 ** i) % 2 for i, r in enumerate(registers)}
        for _, destination, sources in gates:
            require(destination not in sources and len(sources) == len(set(sources)), "bad gate")
            values[destination] = (values[destination] + sum(values[s] for s in sources)) % 2
        result.append(sum(values[r] * 2 ** i for i, r in enumerate(registers)))
    require(len(set(result)) == len(result), "non-bijective Boolean table")
    return result


def apply_rows(rows, x):
    coordinates = [(x // 2 ** j) % 2 for j in range(len(rows))]
    return sum((sum(coordinates[j] for j in range(len(rows)) if (row // 2 ** j) % 2) % 2) * 2 ** i
               for i, row in enumerate(rows))


def verify_fixture(word, fixture, shared):
    frame, source = 509, 22
    positions = [i for i, g in enumerate(word["B"]) if g[0] == frame]
    require(positions == list(range(*fixture["B_slice"])), "block slice")
    gates = [word["B"][i] for i in positions]
    regs = sorted({r for _, d, ss in gates for r in [d, *ss]})
    require(regs == shared["registers"] and len(regs) == 11, "register inventory")
    require(sum(len(g[2]) for g in gates) == fixture["block_adds"], "block cost")
    entry = list(word["start"])
    for section in (word["D"], word["A"], word["B"][:positions[0]]):
        for f, d, sources in section:
            for r in [d, *sources]:
                entry[r] = f
    entry = [entry[r] for r in regs]
    require(entry == shared["entry_frames"], "entry frame reconstruction")
    # Scatter does not change these source/helper frames.
    require(all(r < word["v"] or r >= 2 * word["v"] for r in regs), "unexpected target wire")
    table = boolean_table(gates, regs)
    undo = [None] * len(table)
    for x, y in enumerate(table):
        undo[y] = x
        require(y == apply_rows(shared["matrix_rows"], x), "forward Boolean map")
    require(all(any(((table[x] // 2 ** i) % 2) != ((x // 2 ** i) % 2) for x in range(len(table)))
                or table[2 ** i] != 2 ** i for i in range(len(regs))), "inessential original wire")
    require(boolean_table(list(reversed(gates)), regs) == undo, "reverse Boolean map")
    for y, x in enumerate(undo):
        require(x == apply_rows(shared["inverse_rows"], y), "inverse Boolean map")
    frames, lines = word["frames"], word["lines"]
    require(frames[frame] == shared["block_frame_roots"], "frame roots")
    witness = shared["rank_witness_roots"]
    require(all(r in frames[frame] for r in witness), "witness outside frame")
    require([lines[r] for r in witness] == shared["rank_witness_vectors"], "witness vectors")
    require(gram_determinant([lines[r] for r in witness]) > 0, "singular rank-four witness")
    require(span_rank(frames[frame], lines) == 4, "block rank")
    entry_ranks = [span_rank(frames[f], lines) for f in entry]
    require(entry_ranks == shared["entry_ranks"], "entry ranks")
    for i, register in enumerate(regs):
        # Extract coefficient supports from truth tables, not matrix inversion.
        forward = [j for j in range(len(regs)) if (table[2 ** j] // 2 ** i) % 2]
        backward = [j for j in range(len(regs)) if (undo[2 ** i] // 2 ** j) % 2]
        forward_roots = {r for j in {i, *forward} for r in frames[entry[j]]}
        all_roots = forward_roots | {r for j in backward for r in frames[entry[j]]}
        observed = dict(register=register, forward_support=[regs[j] for j in forward],
                        inverse_column=[regs[j] for j in backward], forward_rank=span_rank(forward_roots, lines),
                        two_sided_rank=span_rank(all_roots, lines))
        require(observed == shared["footprints"][i], "Boolean/minor footprint")
        require(observed["two_sided_rank"] == 4, "unforced exit")
    s = regs.index(source)
    require(shared["footprints"][s]["forward_support"] == [source], "source identity row")
    require(shared["footprints"][s]["inverse_column"] == [17, 22, 33, 38, 77, 87, 468], "source inverse column")
    require([regs[j] for j in range(len(regs)) if (undo[2 ** s] // 2 ** j) % 2 and entry[j] == frame]
            == shared["full_frame_inverse_donors"] == [17, 468], "full-frame donors")
    climbs = Counter(4 - rank for rank in entry_ranks if rank < 4)
    require({str(k): v for k, v in climbs.items()} == shared["minimal_block_climbs"] == {"2": 7, "3": 2},
            "all-carrier climb bill")
    return table, gram_determinant([lines[r] for r in witness])


def main():
    receipt = json.loads((HERE / "CERTIFICATE.json").read_text())
    pins = json.loads((HERE / "SOURCES.json").read_text())
    source_pins = {r["path"]: r["sha256"] for r in pins["files"] if r["usage"] == "input"}
    require(len(receipt["fixtures"]) == 3 and {f["path"] for f in receipt["fixtures"]} == set(source_pins),
            "fixture coverage")
    tables = []
    for fixture in receipt["fixtures"]:
        raw = (ROOT / fixture["path"]).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == fixture["sha256"] == source_pins[fixture["path"]], "source SHA256")
        table, determinant = verify_fixture(json.loads(gzip.decompress(raw)), fixture, receipt["shared"])
        tables.append(table)
    require(tables[0] == tables[1] == tables[2], "fixture maps differ")
    require(gram_determinant([[1, 0], [1, 0]]) == 0 and gram_determinant([[1, 0], [0, 1]]) == 1,
            "integer determinant controls")
    print(f"PASS_INDEPENDENT_B509 Boolean_inputs=2048 fixtures=3 Gram_determinant={determinant} no_new_kappa")


if __name__ == "__main__":
    main()

# SPDX-License-Identifier: Apache-2.0
"""Sufficient native A-stage formats, conditional on exact adapter endpoints."""

import hashlib
import json
from fractions import Fraction as Q

MAX_EVENTS = 30_000
MAX_SUPPORT = 4096


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def depth(row):
    require(len(row) <= MAX_SUPPORT, "bounded row support")
    require(all(q.denominator.bit_count() == 1 for q in row.values()), "dyadic row")
    require(
        all(abs(q.numerator).bit_length() <= 256 for q in row.values()),
        "coefficient bound",
    )
    return max((q.denominator.bit_length() - 1 for q in row.values()), default=0)


def norm(row):
    return sum(map(abs, row.values()), Q(0))


def add(left, right, factor):
    out = left.copy()
    for atom, q in right.items():
        value = out.get(atom, Q(0)) + factor * q
        if value:
            out[atom] = value
        else:
            out.pop(atom, None)
    depth(out)
    return out


def warp(row, operation):
    require(type(operation) is int and operation != 0, "nonzero warp")
    out = {}
    for (variable, word), q in row.items():
        moved = word[1:] if word and word[0] == -operation else (operation, *word)
        require(len(moved) <= 256, "bounded warp word")
        out[variable, moved] = q
    require(len(out) == len(row), "injective formal warp")
    return out


def exponent(rank, paired):
    require(type(rank) is int and 0 <= rank <= 9, "nine-axis frame rank")
    return (rank + 1) // 2 if paired else rank


class Ledger:
    def __init__(self, paired, correlated=False):
        self.paired = paired
        self.correlated = correlated
        self.grid = 0
        self.amplitude = Q(1)
        self.grid_witness = None
        self.range_witness = None
        self.observations = 0

    def observe(self, d, bound, event, kind):
        require(0 <= d <= 64 and 0 <= bound <= 2**64, "bounded capacity observation")
        self.observations += 1
        require(self.observations <= 100_000, "bounded capacity ledger")
        if d > self.grid:
            self.grid, self.grid_witness = d, [event, kind]
        if bound > self.amplitude:
            self.amplitude, self.range_witness = bound, [event, kind]

    def field(self, row, rank, event, kind):
        e = exponent(rank, self.paired)
        self.observe(depth(row) + e, norm(row) * 2**e, event, kind)

    def conversion(self, row, old_rank, new_rank, event):
        for rank, inverse in ((old_rank, True), (new_rank, False)):
            self.field(row, rank, event, "conversion endpoint")
            if rank:
                # Undoing the old frame cancels its suffix. Forward assembly
                # uses at most rank-1 completed C gates before its last C.
                before = rank if inverse else rank - 1
                e = exponent(before, self.paired)
                factor = 4 * 2**e
                if self.correlated:
                    factor = 2 ** (1 + (rank // 2 if inverse else (rank + 1) // 2))
                self.observe(
                    depth(row) + e,
                    factor * norm(row),
                    event,
                    "C numerator partial sum",
                )

    def result(self, precision):
        radius = self.amplitude * 2 ** (precision - 1 + self.grid)
        require(radius.denominator == 1, "integral common-grid radius")
        return {
            "fractional_bits": self.grid,
            "symmetric_amplitude_in_input_L": str(self.amplitude),
            "signed_width": 1 + int(radius).bit_length(),
            "observations": self.observations,
            "grid_witness": self.grid_witness,
            "range_witness": self.range_witness,
        }


def scalar(state, gate):
    require(gate[0] in ("add", "scale"), "ordinary A-prefix scalar")
    target = tuple(gate[1])
    require(target in state and target[0] == "L", "ordinary target")
    before = state[target]
    if gate[0] == "scale":
        require(len(gate) == 4 and gate[2] and gate[3], "invertible scale")
        after = {a: q * Q(gate[2], gate[3]) for a, q in before.items()}
        increment = {}
        source = None
    else:
        require(len(gate) == 5 and gate[4], "ADD shape")
        source = tuple(gate[2])
        require(source in state and source != target, "distinct ordinary ADD ports")
        increment = {a: q * Q(gate[3], gate[4]) for a, q in state[source].items()}
        after = add(before, increment, Q(1))
    depth(after)
    state[target] = after
    return target, source, before, increment, after


def apply_event(event, state, current, frames, active):
    tag = event[0]
    if tag == "climb":
        require(active and event[1] == "A", "ordinary A climb")
        target = ("L", event[2])
        old, new = event[3:5]
        require(
            current[target] == old
            and 0 <= old < len(frames)
            and 0 <= new < len(frames),
            "chronological climb frames",
        )
        require(
            event[5] == len(frames[new]) - len(frames[old]) > 0,
            "positive declared climb rank",
        )
        before = after = state[target]
        source, increment = None, {}
    elif tag == "warp":
        target, operation, old, new = tuple(event[1]), *event[2:]
        require(
            current[target] == old and 0 <= new < len(frames),
            "chronological warp frame",
        )
        require(active or old == new == 0, "zero-frame prelude warp")
        before = state[target]
        after = warp(before, operation)
        state[target] = after
        source, increment = None, {}
    else:
        require(tag == "scalar", "ordinary emitted event")
        target, source, before, increment, after = scalar(state, event[1])
        old = new = event[2]
        require(
            current[target] == old and (source is None or current[source] == old),
            "common scalar frame",
        )
        require(active or old == 0, "zero-frame prelude scalar")
    current[target] = new
    return target, source, before, increment, after, old, new


def record_event(ledgers, event, record, frames, index, active):
    _, source, before, increment, after, old, new = record
    if event[0] in ("warp", "climb"):
        if active:
            for ledger in ledgers:
                ledger.conversion(before, len(frames[old]), len(frames[new]), index)
        return
    rank = len(frames[old]) if active else 0
    for ledger in ledgers:
        ledger.field(before, rank, index, "scalar input")
        ledger.field(after, rank, index, "scalar output")
        if source is not None:
            ledger.field(increment, rank, index, "ADD increment")
            e = exponent(rank, ledger.paired)
            ledger.observe(
                max(depth(before), depth(increment)) + e,
                (norm(before) + norm(increment)) * 2**e,
                index,
                "ADD partial sum",
            )


def row_record(index, target, row):
    return [
        index,
        list(target),
        [[v, list(w), q.numerator, q.denominator] for (v, w), q in sorted(row.items())],
    ]


def stage(events, word, precision=64):
    require(type(precision) is int and 3 <= precision <= 128, "input precision 3..128")
    require(1 <= len(events) <= MAX_EVENTS, "bounded emitted stream")
    frames = word["frames"]
    require(len(frames) <= 4096 and len(word["start"]) == 632, "frame inventory")
    current = {("L", r): f for r, f in enumerate(word["start"])}
    state = {r: {(r[1], ()): Q(1)} for r in current}
    ledgers = [Ledger(False), Ledger(True), Ledger(True, correlated=True)]
    digest = hashlib.sha256()
    counts = {
        "prelude_scalars": 0,
        "prelude_warps": 0,
        "A_scalars": 0,
        "A_warps": 0,
        "A_climbs": 0,
    }
    active = ended = False
    operations = {w["op"] for w in word["warps"]}
    for index, event in enumerate(events):
        tag = event[0]
        if tag == "phase":
            if event[1] == "A":
                require(not active, "one A phase")
                active = True
                for r, row in state.items():
                    for ledger in ledgers:
                        ledger.field(row, len(frames[current[r]]), index, "A entrance")
            elif active:
                require(event[1] == "centers", "A terminates at centers")
                ended = True
                break
            continue
        require(
            tag in ("scalar", "warp", "climb", "adapter", "residual_adapter"),
            "known pre-centre event",
        )
        if tag in ("adapter", "residual_adapter"):
            require(not active, "adapters outside A")
            continue  # Their exact endpoint interpretation is a theorem hypothesis.
        if tag == "warp":
            require(abs(event[2]) in operations, "declared logical warp")
        record = apply_event(event, state, current, frames, active)
        record_event(ledgers, event, record, frames, index, active)
        counts[
            {
                "scalar": "A_scalars" if active else "prelude_scalars",
                "warp": "A_warps" if active else "prelude_warps",
                "climb": "A_climbs",
            }[tag]
        ] += 1
        if tag in ("warp", "scalar"):
            target, _, _, _, row, _, _ = record
            digest.update(canonical(row_record(index, target, row)))
    require(active and ended and counts["A_scalars"] > 1000, "complete A stage")
    return {
        "counts": counts,
        "prefix_rows_sha256": digest.hexdigest(),
        "end_event": index,
        "normalized_exit_fractional_bits": max(map(depth, state.values())),
        "gatewise": ledgers[0].result(precision),
        "paired": ledgers[1].result(precision),
        "pair_first": ledgers[2].result(precision),
    }


def capacity(report, precision, grid, width):
    require(type(precision) is int and 3 <= precision <= 128, "input precision 3..128")
    require(
        type(grid) is int and report["fractional_bits"] <= grid <= 64,
        "sufficient common grid",
    )
    require(type(width) is int and 2 <= width <= 256, "bounded signed capacity")
    radius = Q(report["symmetric_amplitude_in_input_L"]) * 2 ** (precision - 1 + grid)
    require(radius < 2 ** (width - 1), "strict symmetric signed capacity")
    return True


def fourier_controls():
    """Enumerate one exact row; independent axes make every row a permutation."""
    row = [(Q(1), Q(0))]
    result = []
    for rank in range(10):
        d = max((max(a.denominator, b.denominator).bit_length() - 1 for a, b in row))
        n = sum((abs(a) + abs(b) for a, b in row), Q(0))
        require(d == exponent(rank, True) and n == 2**d, "paired Fourier law")
        result.append(
            {
                "rank": rank,
                "real_terms": sum(bool(a) + bool(b) for a, b in row),
                "grid": d,
                "norm": str(n),
            }
        )
        if rank < 9:
            row = [((a - s * b) / 2, (b + s * a) / 2) for a, b in row for s in (-1, 1)]
    return result

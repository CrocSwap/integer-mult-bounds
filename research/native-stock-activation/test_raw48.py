"""Compare the physical operations with independent exact coordinate oracles."""

from argparse import ArgumentParser
from collections import Counter
from contextlib import contextmanager
from fractions import Fraction
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import patch

import spool

from compact_columns import Columns
from raw48 import Artifacts, ComplexRaw, monomial, read_json
from positive import Positive, one_axis
from spool import Arena, cold_swap, integer_scale, quarter, short_divisors


@contextmanager
def count_heads():
    original = spool.TemporaryFile
    count = {"open": 0, "peak": 0}

    class Tape:
        def __init__(self):
            self.stream = original()
            count["open"] += 1
            count["peak"] = max(count["open"], count["peak"])

        def __getattr__(self, key):
            return getattr(self.stream, key)

        def close(self):
            if not self.stream.closed:
                count["open"] -= 1
                self.stream.close()

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            self.close()

    with patch.object(spool, "TemporaryFile", Tape):
        yield count
    assert count["open"] == 0


def recursive_heads():
    from periodic import Rule

    trials = []
    for h, depth in ((3, 1), (6, 2), (12, 3)):
        with count_heads() as heads:
            # A two-row leaf plan isolates the genuine recursive frame lifecycle.
            service = Positive(None, lambda *args, **kwargs: None, 2)
            service.rule = Rule(2, (2,), (1, 1))
            service._owners = 2
            service.planner = lambda width: SimpleNamespace(width=2, forest=None)
            pool = Arena(h + depth, 4)
            field = pool.field()
            field.clear()
            service.apply(field, 0, h, Columns(1, 0, 1, 0, 0, 0, 0, cold_swap))
            assert heads["open"] == 1
            field.retire()
            pool.close()
        assert heads["peak"] == 4
        trials.append({"service_heights": depth, "peak_tape_handles": heads["peak"]})
    return trials


def main():
    parser = ArgumentParser()
    parser.add_argument("bounded", type=Path)
    parser.add_argument("grade", type=Path)
    args = parser.parse_args()
    sys.path.insert(0, str(args.bounded.resolve()))
    from tagged_sources import read_words

    a = Artifacts(args.grade.resolve())
    from periodic import Job

    _, actual_word = read_words()
    root_tag = ("root", "rotated", 191, 9825, 1)
    target_index = next(i for i, port in enumerate(actual_word.targets) if port.tag == root_tag)
    raw_rank = actual_word.targets[target_index].rank
    assert (
        raw_rank == 129
        and sum(p.rank == raw_rank and p.tag[0] == "root" for p in actual_word.targets) == 624
    )
    witness = actual_word.target((target_index,) * actual_word.power)
    assert witness.rank == raw_rank**264 and witness.rank >= actual_word.floor**264
    assert list(ComplexRaw.axis_list(3, (0, 9, 17)))[:3] == [0, 1, 2]
    scheduled = []
    counts = Counter()
    for clock, row in enumerate(a.instructions()):
        op = row[0]
        counts[op] += 1
        if op == "NATIVE":
            for node in a.graph["schedule"]:
                if node in a.moves:
                    scheduled.append(("return", clock, row[1], node))
        elif op == "QUERY" or op.startswith("IDLE_"):
            scheduled.append((op, clock, row[1]))
    assert scheduled == [p.tag for p in actual_word.paid]
    contacts = 0
    placed_basis = 0
    basis = read_json(args.grade / "retained/data/CALLER-PHASE-BASES.json")["by_q"]
    for q, (move, delta) in zip(a.layout["ports"], a.contacts, strict=True):
        rows = (q, *basis[str(q)])
        sites = (0, *range(9, 17))
        expected = (q, *(1 << j for j in range(9, 17)), *basis[str(q)])
        for j, column in enumerate(expected):
            addr = 1 << j
            for op, dest, src in move:
                assert op == "ROW"
                addr ^= ((addr >> src) & 1) << dest
            assert addr == column
            for op, dest, src in reversed(move):
                addr ^= ((addr >> src) & 1) << dest
            assert addr == 1 << j
            placed_basis += 1
        for k in range(512):
            image = 0
            for j, v in enumerate(rows):
                if (k >> j) & 1:
                    image ^= v
            correction = sum(k >> sites.index(axis) & 1 for _, axis in delta) % 2
            assert (image.bit_count() - k.bit_count()) % 4 == 2 * correction
            contacts += 1
    chart_cases = []
    atlas = read_json(args.grade / "complex-atlas.json.gz")
    rows = {(i, j): rec for i, j, rec in atlas["pairs"]}
    for pair in [(0, 249), *list(rows)[-2:]]:
        for side in ("left", "right"):
            rec = rows[pair][side]
            pool = Arena(9, 4)
            field = pool.field()
            original = [(17 * i - 83, 3 * i * i + 2) for i in range(512)]
            field.write(original)
            cols = Columns(1, 0, 1, 0, 0, 0, 0, cold_swap)
            raw = ComplexRaw(a, {}, cols, low=0, bundle=1, slots=9)
            target = [None] * 512
            for src, z in enumerate(original):
                signed = rec["phase"]
                for i, linear in enumerate(rec["linear_Z4"]):
                    signed += linear * ((src >> i) & 1)
                    if (src >> i) & 1:
                        signed += (
                            2 * (src & rec["quadratic_rows"][i] & ~((1 << (i + 1)) - 1)).bit_count()
                        )
                out = rec["offset"]
                for i, linear in enumerate(rec["matrix_rows"]):
                    out ^= ((src & linear).bit_count() % 2) << i
                target[out] = quarter(z, signed)
            raw.chart(field, monomial(rec), range(9), 1)
            assert list(field.values()) == target
            raw.chart(field, monomial(rec), range(9), 1, inverse=True)
            assert list(field.values()) == original
            field.retire()
            pool.close()
            chart_cases.append([*pair, side])
    compact = []
    for k, src, tgt in ((2, 3, 7), (2, 7, 3), (5, None, 2), (2, None, 3)):
        f = 2
        body = (2 if src is not None else 1) * k * f
        ambient = 3 + body
        pool = Arena(ambient, 3)
        field = pool.field()
        original = [(i, -i - 1) for i in range(1 << ambient)]
        field.write(original)
        # Tests use one back guard followed by complete slot fields and two fronts.
        if src is not None:
            target = 1 + (0 if tgt < src else k * f)
            source = 1 + (0 if src < tgt else k * f)
        else:
            target = 1
            source = None
        col = Columns(k, 0, 1, 1 + body, 2 + body, 0, 0, cold_swap)
        ys = tuple(target + i * k for i in range(f))
        xs = None if source is None else tuple(source + i * k for i in range(f))
        col.row(field, ys, xs)
        oracle = [None] * len(original)
        for i, z in enumerate(original):
            new = i
            for j, y in enumerate(ys):
                new ^= (1 if xs is None else (i >> xs[j]) & 1) << y
            oracle[new] = z
        assert list(field.values()) == oracle
        col.row(field, ys, xs)
        assert list(field.values()) == original
        field.retire()
        pool.close()
        compact.append([ambient, src, tgt, len(original)])
    helper_receipts = []
    for before, after in ((0, 249), (1102, 266), (1102, 1051)):
        rank, _, _ = a.factors[before, after]
        graph = {"initial": [before], "final": [after], "schedule": [7, 13], "first_output": 13}
        fixture = SimpleNamespace(
            regs=[],
            main=set(),
            graph=graph,
            odd=a.odd,
            layout={"source_labels": [91]},
            moves={7: (before, after)},
            factors=a.factors,
            forms={7: ((~0, Fraction(1, 3)), (~0, Fraction(2, 3))), 13: ((7, Fraction(1)),)},
        )
        with count_heads() as heads:
            pool = Arena(9, 32)
            field = pool.field()
            original = [((17 * i - 83) << 10, (3 * i * i + 2) << 10) for i in range(512)]
            field.write(original)
            owner = "true 91"
            chosen = tuple(range(8, 8 - rank, -1))
            cols = Columns(1, 0, 1, 0, 0, 0, 0, cold_swap)
            raw = ComplexRaw(fixture, {owner: field}, cols, low=0, bundle=1, slots=9)
            iterator = raw.graph(12, 3, 0, (), {("helper", 12, 3, 91): Job(owner, chosen)}, {}, 1)
            tag, request = next(iterator)
            assert heads["open"] == 1
            assert tag == ("return", 12, 3, 7) and request.owner != owner
            for axis in request.axes:
                one_axis(raw.fields[request.owner], axis)
            assert next(iterator, None) is None
            numerical = list(original)
            for bit in chosen:
                nxt = []
                for i, (u, v) in enumerate(numerical):
                    c, d = numerical[i ^ (1 << bit)]
                    nxt.append(((u - v + c + d) // 2, (u + v - c + d) // 2))
                numerical = nxt
            assert list(field.values()) == numerical
            assert len(raw.fields) == 1 and pool.live == 1
            field.retire()
            pool.close()
        helper_receipts.append([before, after, rank])
    scalar_cases = {c for terms in a.forms.values() for _, c in terms}
    scalar_cases.update((Fraction(1, 2025), Fraction(1, a.odd), Fraction(a.odd)))
    for ratio in scalar_cases:
        x = -131 * ratio.denominator
        assert integer_scale(x, ratio) == x * ratio
        assert all(0 < factor < 1 << 24 for factor in short_divisors(ratio.denominator))
    try:
        integer_scale(1, Fraction(1, 3))
    except ArithmeticError:
        pass
    else:
        raise AssertionError("Accepted an inexact internal scalar")
    from powered import Port, PoweredWord

    toy_word = PoweredWord(
        2, (Port(("two",), 2),), (Port(("left",), 1), Port(("right",), 1)), 1, 1, 1, 1
    )
    issued = []

    class TwoAxisRaw:
        def __init__(self, fields, columns, **geometry):
            self.fields = fields

        def raw(self, inputs, cols):
            [(tag, job)] = inputs
            assert tag == ("two",) and len(job.axes) == 2 * cols
            for i, paid in enumerate(("left", "right")):
                issued.append((job.owner, i, cols))
                yield (paid,), Job(job.owner, job.axes[i * cols : (i + 1) * cols])

    small = Positive(toy_word, TwoAxisRaw, 8)
    assert small.owners == 16
    pool = Arena(13, 8)
    field = pool.field()
    field.write((((17 * i - 83) << 9, (i * i + 7) << 9) for i in range(8192)))
    reference = field.copy()
    cols = Columns(1, 0, 1, 0, 0, 0, 0, cold_swap)
    small.apply(field, 0, 9, cols)
    for bit in range(9):
        one_axis(reference, bit)
    assert list(reference.values()) == list(field.values()) and len(issued) == 128
    original = [(i - 123, (7 * i + 5) % 1009 - 503) for i in range(8192)]
    field.write(original)
    small.hadamard(field, 0, 9, cols)
    independent = list(original)
    for b in range(9):
        bit = 1 << b
        for j in range(8192):
            if j & bit:
                continue
            l, r = independent[j], independent[j | bit]
            independent[j] = (l[0] + r[0], l[1] + r[1])
            independent[j | bit] = (l[0] - r[0], l[1] - r[1])
    assert list(field.values()) == independent
    field.retire()
    reference.retire()
    pool.close()
    print(
        json.dumps(
            {
                "raw_targets": len(actual_word.targets),
                "ordered_paid_tags": len(scheduled),
                "connected_root_label": root_tag,
                "connected_raw_target_rank": raw_rank,
                "connected_powered_positive_rank_bits": witness.rank.bit_length(),
                "physical_contacts_checked": contacts,
                "emitted_contact_basis_columns_and_inverses": placed_basis,
                "actual_root_opcodes": dict(counts),
                "raw_atlas_spool_and_inverse": chart_cases,
                "helper_positive_paid_resume_and_final_odd_conversion": helper_receipts,
                "exact_fixed_rational_scalars": len(scalar_cases),
                "rank8_nested_controller": {
                    "independent_rows": 16,
                    "cohort_inputs": 8192,
                    "changed_child_returns_across_C_and_H": len(issued),
                },
                "compact_dirty_spool_and_return": compact,
                "heads_open_at_each_suspended_helper": 1,
                "independent_recursive_tape_lifetimes": recursive_heads(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

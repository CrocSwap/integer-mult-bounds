"""Run each new positive child on a dense numerical field with its actual charts."""

from argparse import ArgumentParser
from pathlib import Path
import sys

from strong_complex import artifacts, packed


def direct(circuit, values, engine, quarter):
    for gate in circuit:
        op = gate[0]
        if op == "P":
            dest = engine.action(gate)
            out = [None] * len(values)
            for pos, new in enumerate(dest):
                out[new] = values[pos]
            values = out
        elif op == "D":
            values = [quarter(z, q) for z, q in zip(values, engine.action(gate), strict=True)]
        elif op == "phase":
            values = [quarter(z, gate[1]) for z in values]
        elif op == "X":
            values = [values[x ^ gate[1]] for x in range(len(values))]
        elif op == "C":
            _, v, sign = gate
            out = []
            for x, (a, b) in enumerate(values):
                c, d = values[x ^ v]
                a, b = a + c + sign * (d - b), b + d + sign * (a - c)
                if (a | b) & 1:
                    raise ArithmeticError("The direct Clifford oracle lost its grid")
                out.append((a // 2, b // 2))
            values = out
        else:
            raise ValueError("Unknown independent frame gate")
    return values


def run(grade, data):
    from compact_columns import Columns
    from positive import one_axis
    from raw48 import ComplexRaw
    from spool import Arena, cold_swap, quarter
    import native_verify as independent

    art = artifacts(grade, data)
    new = packed(data / "new-charts.json.gz")
    frames = art.graph["frames"]
    checked = 0
    for a, b, rec in new:
        rank, right, left = art.factors[a, b]
        if rank != rec["rank"]:
            raise ValueError("The paid slot width differs")
        amp = [((17 * j - 11 * a + b) << 18, (3 * j * j + 2 * a - b) << 18) for j in range(512)]
        expected = direct(
            independent.adjoint(independent.frame(tuple(frames[a]), 9))
            + independent.frame(tuple(frames[b]), 9),
            amp,
            independent,
            quarter,
        )
        pool = Arena(9, 16)
        field = pool.field()
        field.write(amp)
        slots = Columns(1, 0, 1, 0, 0, 0, 0, cold_swap)
        raw = ComplexRaw(art, {0: field}, slots, low=0, bundle=1, slots=9)
        raw.chart(field, right, range(9), 1)
        for axis in range(rank):
            one_axis(field, axis)
        raw.chart(field, left, range(9), 1)
        if list(field.values()) != expected:
            raise ValueError("Physical child differs from its independent true frame transport")
        raw.chart(field, left, range(9), 1, inverse=True)
        for axis in range(rank):
            one_axis(field, axis)
            slots.row(field, (axis,))
        raw.chart(field, right, range(9), 1, inverse=True)
        if list(field.values()) != amp:
            raise ValueError("The paid inverse did not restore the original field")
        field.retire()
        pool.close()
        checked += 1
    return {"supplemental_dense_children": checked, "complex_values_per_direction": 512 * checked}


if __name__ == "__main__":
    p = ArgumentParser(description=__doc__)
    for key in ("grade", "engine", "native", "bounded", "data"):
        p.add_argument(key, type=Path)
    args = p.parse_args()
    sys.path.extend(str(path.resolve()) for path in (args.engine, args.native, args.bounded))
    print(run(args.grade, args.data))

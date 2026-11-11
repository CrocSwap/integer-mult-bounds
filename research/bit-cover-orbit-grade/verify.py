"""Verify the cover-orbit grade criterion and price the complete BIT stock."""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import json
from pathlib import Path

PINS = {
    "EFREE-CALLER.json.gz": "757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b",
    "EFREE-RESULT.json": "a46b6c6040f75184cab5467656811ad988c216e3bc8e44d595a5015b6e49620b",
    "independent/interval_gate.py": "8dc2bc4c64cba3f83c664373984a075f1a14b4d53958084091345c8cab189dec",
}
TARGET = Fraction("0.0040075385047236")
TRIAL = Fraction("0.004008162992724")


def read(root, key):
    data = (root / key).read_bytes()
    if sha256(data).hexdigest() != PINS[key]:
        raise ValueError(f"SHA-256 mismatch: {key}")
    return data


def axis(dimension, j):
    return tuple(int(i == j) for i in range(dimension))


def signed_permutation(images):
    """Construct a matrix in column form from (output, sign) per input."""
    d = len(images)
    assert sorted(out for out, _ in images) == list(range(d))
    assert all(sign in (-1, 1) for _, sign in images)
    return tuple(tuple(sign if i == out else 0 for i in range(d)) for out, sign in images)


def act(columns, vector):
    return tuple(sum(c * v for c, v in zip(row, vector, strict=True)) for row in zip(*columns, strict=True))


def insert(basis, vector):
    row = list(map(Fraction, vector))
    for k in sorted(basis):
        if row[k]:
            f = row[k]
            row = [x - f * y for x, y in zip(row, basis[k], strict=True)]
    pivot = next((i for i, x in enumerate(row) if x), None)
    if pivot is None:
        return None
    v = tuple(x / row[pivot] for x in row)
    basis[pivot] = v
    return v


def orbit_grade_dimension(target, first, last, right):
    # W0 consists of covectors with l P=l, l Q_first=l Q_last=0.
    # Its annihilator is spanned by columns of I-P, Q_first and Q_last.
    dimension = len(target)
    columns = [tuple(a-b for a, b in zip(axis(dimension, i), p, strict=True))
               for i, p in enumerate(target)] + list(first) + list(last)
    basis = {}
    queue = []
    for col in columns:
        value = insert(basis, col)
        if value is not None:
            queue.append(value)
    initial_dim = dimension - len(basis)
    for vector in queue:
        for matrix in right:
            value = insert(basis, act(matrix, vector))
            if value is not None:
                queue.append(value)
    return initial_dim, dimension - len(basis)


def layout_controls(d, active):
    active = list(active)
    x, z = active[0], active[-1]
    middle = set(active[1:-1])
    zero = (0,) * d
    P = [axis(d, i) if i in active else zero for i in range(d)]
    Q1 = [axis(d, i) if i == x else zero for i in range(d)]
    Q3 = [axis(d, i) if i == z else zero for i in range(d)]
    # The explicit table swaps the outer axes and negates every middle
    # covector. None of those normalized covectors is fixed individually.
    S = signed_permutation([(z if i == x else x if i == z else i, -1 if i in middle else 1)
                            for i in range(d)])
    cycles = dict(zip(active, active[1:] + active[:1], strict=True))
    escape = signed_permutation([(cycles.get(i, i), 1) for i in range(d)])
    base, invariant = orbit_grade_dimension(P, Q1, Q3, [S])
    _, rotated = orbit_grade_dimension(P, Q1, Q3, [escape])
    assert base == invariant == len(active) - 2 and rotated == 0
    assert all(act(S, axis(d, i)) == tuple(-v for v in axis(d, i)) for i in middle)
    return {"ambient": d, "target_rank": len(active), "outer_ranks": [1, 1],
            "middle_rank": len(middle), "initial_grade_space": base,
            "orbit_grade_space": invariant, "pointwise_fixed_middle_grades": 0,
            "cycle_control_orbit_grade_space": rotated}


def physical(columns, z, active, cardinality):
    u = act(tuple(zip(*columns, strict=True)), z)
    v = tuple(-x if i in active else x for i, x in enumerate(u))
    return tuple(x % cardinality for x in act(columns, v))


def finite_control(s):
    identity = signed_permutation([(0, 1), (1, 1), (2, 1)])
    exchange = signed_permutation([(2, 1), (1, -1), (0, 1)])
    change_grade = signed_permutation([(1, 1), (0, 1), (2, 1)])
    orbits = [(g, tuple(act(g, c) for c in exchange)) for g in (identity, change_grade)]
    assert len({g for orbit in orbits for g in orbit}) == 4
    selected = 0
    middle_crossings = 0
    for (g0, g1) in orbits:
        inverse = tuple(zip(*g0, strict=True))

        def grade(z):
            return act(inverse, z)[1] % s

        for g in (g0, g1):
            for z in product(range(s), repeat=3):
                value = grade(z)
                for axes in ({0}, {2}):
                    assert grade(physical(g, z, axes, s)) == value
                mid = physical(g, z, {1}, s)
                assert physical(g, mid, {1}, s) == z
                target = physical(g, z, {0, 1, 2}, s)
                assert grade(target) == (-value) % s
                if grade(mid) != value:
                    middle_crossings += 1
                if 0 < value <= (s - 1) // 2:
                    selected += 2  # independent external roles
    volume = 4 * s ** 3
    assert selected == volume - volume // s
    assert middle_crossings == selected and middle_crossings % 2 == 0
    return {"digit_cardinality": s, "cover_orbits": 2, "field_volume": volume,
            "target_minor_rank_two_fields": selected,
            "one_middle_field_rank_defect": middle_crossings // 2,
            "required_middle_field_multiplier": 2}


def caller_stock(caller, invoice):
    mask_counts = Counter(tuple(e[2]) for e in caller["events"] if e[0] == "IDLE_ONE")
    assert len(mask_counts) == 16 and set(mask_counts.values()) == {2}
    assert invoice["event_counts"]["IDLE_ONE"] == 32
    assert (caller["ports"], caller["body_rank"], caller["ambient_rank"]) == (111, 7, 127)
    assert caller["events"][19] == ["IDLE_ONE", 2, list(range(2, 10))]
    assert caller["events"][24] == ["IDLE_ONE", 21, list(range(2, 10))]
    ranks = Counter()
    for mask, count in mask_counts.items():
        ranks[len(mask) * caller["body_rank"]] += (count // 2) * caller["ports"]
    assert ranks == {rank: 222 for rank in range(7, 57, 7)}
    return ranks


def directed(gate, invoice, stock, kappa):
    paid = {int(r): count for r, count in invoice["paid"].items()}
    targets = {int(r): count for r, count in invoice["targets"].items()}
    deficit = gate.sub(gate.moment(paid, kappa), gate.moment(targets, kappa))
    minimum = gate.exact(0)
    for rank, n in sorted(stock.items()):
        delta = gate.moment({1: 4, rank - 2: 2, rank: -2}, kappa)
        assert delta[0] > 0
        minimum = gate.add(minimum, gate.mul(gate.exact(n), delta))
    assert deficit[0] > 0 and minimum[0] > 0
    return {"kappa": str(kappa), "unchanged_raw_deficit": gate.show(deficit),
            "optimistic_optional_saving": ["0", "0"],
            "minimum_surcharge_if_all_1776_qualifying_pairs_replaced": gate.show(minimum),
            "rank56_minimum_surcharge": gate.show(gate.moment({1: 4, 54: 2, 56: -2}, kappa))}


def main():
    if not __debug__:
        raise RuntimeError("Run with assertions enabled")
    p = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parents[2]
    p.add_argument("--bit-package", type=Path, default=root / "research/paired-query-only-bit")
    p.add_argument("--expected", type=Path)
    a = p.parse_args()
    caller = json.loads(gzip.decompress(read(a.bit_package, "EFREE-CALLER.json.gz")))
    invoice = json.loads(read(a.bit_package, "EFREE-RESULT.json"))
    gate = a.bit_package / "independent/interval_gate.py"
    read(a.bit_package, "independent/interval_gate.py")
    spec = spec_from_file_location("directed_gate", gate)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    stock = caller_stock(caller, invoice)
    result = {"pins": PINS, "pair_stock_upper": dict(stock),
              "pair_stock_total_upper": sum(stock.values()),
              "rank56_layout": layout_controls(127, range(8, 64)),
              "finite_controls": [finite_control(s) for s in (3, 5, 9)],
              "directed_prices": [directed(module, invoice, stock, k) for k in (TARGET, TRIAL)]}
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if a.expected is not None and a.expected.read_text(encoding="utf-8") != encoded:
        raise ValueError("Frozen exact receipt mismatch")
    print(encoded, end="")
    if a.expected is not None:
        print("PASS_BIT_COVER_ORBIT_GRADE middle_dimension=54 pair_stock_upper=1776 credit=0 no_new_kappa")


if __name__ == "__main__":
    main()

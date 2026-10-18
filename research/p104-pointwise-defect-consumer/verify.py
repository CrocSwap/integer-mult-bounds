"""Read-only exact census, standard library and source-byte loaders."""

from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import types

ROOT = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def source_module(path, name):
    data = path.read_bytes()
    module = types.ModuleType(name)
    module.__file__ = str(path)
    # The separate review script uses assertions. Keep them active under -O.
    exec(compile(data, str(path), "exec", optimize=0), module.__dict__)
    return module


def authenticate():
    manifest = json.loads((ROOT / "PREDECESSOR.json").read_text())
    need(len(manifest["files"]) == 2, "two predecessor files")
    for row in manifest["files"]:
        path = ROOT / row["local"]
        need(path.resolve().is_relative_to(ROOT) and not path.is_symlink(), "source path")
        data = path.read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        need(hashlib.sha256(data).hexdigest() == row["sha256"], "predecessor source SHA256")
        need(blob == row["git_blob"], "predecessor Git blob")
    return source_module(ROOT / "vendor/lattice.py", "pinned_lattice")


def determinant(matrix):
    """Fraction-free Bareiss determinant, used only for small census bases."""
    a = [list(row) for row in matrix]
    n, previous, sign = len(a), 1, 1
    for k in range(n - 1):
        if a[k][k] == 0:
            pivot = next((i for i in range(k + 1, n) if a[i][k]), None)
            if pivot is None:
                return 0
            a[k], a[pivot] = a[pivot], a[k]
            sign = -sign
        value = a[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = a[i][j] * value - a[i][k] * a[k][j]
                need(numerator % previous == 0, "Bareiss exact division")
                a[i][j] = numerator // previous
            a[i][k] = 0
        previous = value
    return sign * a[-1][-1]


def typed_equal(actual, expected):
    if type(actual) is not type(expected):
        return False
    if isinstance(actual, dict):
        return actual.keys() == expected.keys() and all(
            typed_equal(actual[k], expected[k]) for k in actual)
    if isinstance(actual, list):
        return len(actual) == len(expected) and all(
            typed_equal(a, b) for a, b in zip(actual, expected, strict=True))
    return actual == expected


def result():
    predecessor = authenticate()
    model = source_module(ROOT / "model.py", "defect_model")
    rows, tables = [], []
    source_comparisons = 0
    expected_indices = [2, 6, 15, 34, 75, 161, 343]
    for rank, exponent in enumerate(expected_indices, 1):
        need(sum(predecessor.index_counts(rank)) == exponent, "prefix index")
    for rank in (1, 2, 3):
        dimension = model.shape(rank)
        basis, generators, stage_indices = model.transversal(rank)
        need(stage_indices == predecessor.index_counts(rank), "transversal stage counts")
        need(abs(determinant(basis)) == 1 << len(generators), "basis determinant")
        predecessor.prefix_member(basis, rank)
        q = 1 << (rank // 2 + 1)
        predecessor.prefix_member([[q * int(i == j) for j in range(dimension)]
                                   for i in range(dimension)], rank)
        images = Counter()
        for value in model.representatives(generators, dimension):
            need(model.lift(value, rank) == predecessor.lift(value, rank), "pinned floor word")
            images[model.defect(value, rank)] += 1
            source_comparisons += 1
        row = model.census(rank)
        rows.append(row)
        tables.append({"rank": rank, "address_contract": "given binary transversal label",
                       **model.table_invoice(len(generators), images,
                                             row["signed_defect_coordinate_bits"])})
        if rank <= 2:
            cube = model.full_box(rank)
            factor = q ** dimension // (1 << len(generators))
            need(cube == Counter({x: n * factor for x, n in images.items()}),
                 "full-box versus transversal fibers")
            tables.append({"rank": rank, "address_contract": "raw low input bits",
                           **model.table_invoice((rank // 2 + 1) * dimension, cube,
                                                 row["signed_defect_coordinate_bits"])})
    independent = source_module(ROOT / "independent.py", "independent_box_review")
    independent.local_floor_identity()
    # JSON arrays are the explicit receipt representation of coordinate tuples.
    independent_controls = json.loads(json.dumps(independent.controls()))
    independent_rows = json.loads(json.dumps([independent.census(rank) for rank in (1, 2)]))
    for primary, second in zip(rows[:2], independent_rows, strict=True):
        rank = primary["rank"]
        factor = second["domain_size"] // primary["cosets"]
        need(second["image_size"] == primary["defect_values"], "independent defect image")
        need(second["fiber_size_histogram"] == {
            str(int(k) * factor): v for k, v in primary["fiber_histogram"].items()},
            "independent complete fibers")
    signed_period_cases = 0
    for rank in range(1, 8):
        dimension, divisor = model.shape(rank), 1 << rank
        q = 1 << (rank // 2 + 1)
        for bits in (0, 3, 63, 4090):
            x = [(-1 if i % 3 == 0 else 1) * ((1 << bits) + i) for i in range(dimension)]
            z = [((i * 7 + bits) % 11) - 5 for i in range(dimension)]
            translated = [a + q * b for a, b in zip(x, z, strict=True)]
            need(model.defect(x, rank) == model.defect(translated, rank), "signed scalar period")
            need(model.lift(x, rank) == predecessor.lift(x, rank), "wide signed floor word")
            ideal = model.numerator([q * b for b in z], rank)
            need(all(v % divisor == 0 for v in ideal), "integer ideal period increment")
            need([v // divisor for v in ideal] == predecessor.ideal([q * b for b in z], rank),
                 "pinned ideal period increment")
            signed_period_cases += 1
    witnesses = []
    for rank in range(1, 8):
        repeats = 1 << (rank - 1)
        zero = [0, 0, 0, 0] * repeats
        y = [0, 0, 1, 1] * repeats
        t = [1, 0, 0, 0] * repeats
        yt = [a + b for a, b in zip(y, t, strict=True)]
        need(model.defect(zero, rank) == model.defect(y, rank) == tuple(zero),
             "equal pointwise labels")
        dt, dyt = model.defect(t, rank), model.defect(yt, rank)
        expected = tuple(x * (1 << (rank - 1)) for x in [-1, 1, -1, 1] * repeats)
        need(dt == expected and dyt == tuple(-x for x in expected),
             "source translation must split merged states")
        need(model.lift(yt, rank) == predecessor.lift(yt, rank), "witness literal word")
        witnesses.append({"rank": rank, "repeated_blocks": repeats,
                          "scaled_defect_magnitude": 1 << (rank - 1)})
    gates = model.pair_gates()
    pair_tests = 0
    for source in itertools.product((0, 1), repeat=4):
        encoded = model.signed_encode(model.defect(source, 1), 2)
        for target in range(1 << 8):
            state = list(source) + [0, 0] + [(target >> i) & 1 for i in range(8)] + [1]
            actual = model.run_gates(state, gates)
            need(actual[:6] == state[:6] and actual[-1] == 1, "source/work/spectator restored")
            output = sum(bit << i for i, bit in enumerate(actual[6:14]))
            need(output == target ^ encoded, "literal arbitrary-target defect oracle")
            pair_tests += 1
    # This exact signed-integer identity permits an immutable-source consumer.
    dirty_cases = 0
    for rank in (1, 2, 3):
        dimension, divisor = model.shape(rank), 1 << rank
        for seed in range(12):
            x = [((i * 31 + seed * 19) % 43) - 21 for i in range(dimension)]
            a, d, wanted = model.numerator(x, rank), model.defect(x, rank), model.lift(x, rank)
            for dirty in (-10003, -9, -1, 0, 1, 17, 10003):
                scratch = [dirty + 7 * i for i in range(dimension)]
                target = [13 - 3 * i for i in range(dimension)]
                old_scratch, old_target = scratch[:], target[:]
                target = [y - b // divisor for y, b in zip(target, scratch, strict=True)]
                scratch = [b + u + e for b, u, e in zip(scratch, a, d, strict=True)]
                target = [y + b // divisor for y, b in zip(target, scratch, strict=True)]
                scratch = [b - u - e for b, u, e in zip(scratch, a, d, strict=True)]
                need(scratch == old_scratch, "dirty scratch restoration")
                need(target == [y + z for y, z in zip(old_target, wanted, strict=True)],
                     "exact dirty consumer result")
                dirty_cases += 1
    return {
        "status": "PASS_P104_POINTWISE_DEFECT_BOUNDARY_NO_NEW_KAPPA",
        "censuses": rows, "lookup_invoices": tables,
        "raw_rank3_full_scan_toffoli": 2 * (32 - 1) * (1 << 32),
        "word_source_comparisons": source_comparisons,
        "independent_box_censuses": independent_rows,
        "independent_controls": independent_controls,
        "signed_period_cases": signed_period_cases,
        "translated_collision_witnesses": witnesses,
        "source_bound_rank7_index_bits": expected_indices[-1],
        "rank1_structured_oracle": {"gates": dict(sorted(Counter(g[0] for g in gates).items())),
                                     "clean_work_bits": 2, "target_bits": 8,
                                     "exhaustive_source_target_pairs": pair_tests},
        "signed_dirty_consumer_cases": dirty_cases,
        "scope": "Complete rank1..3 transversal images; all-integer source coverage uses the written period proof. Translation-closed-code theorem is written, not formal-kernel checked. No rank7 defect image or favorable full recursive cost is established.",
    }


def main():
    actual = result()
    expected = json.loads((ROOT / "RESULT.json").read_text())
    need(typed_equal(actual, expected), "typed mathematical receipt mismatch")
    print(actual["status"])


if __name__ == "__main__":
    main()

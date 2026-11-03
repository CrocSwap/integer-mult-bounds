"""Check the stochastic native interface and its stated limits."""

import gzip
import hashlib
import itertools
import json
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from kernel import center, layer, monomial, native, pair, phase, route

M = ((1, -1, 1, 1), (1, 1, -1, 1), (1, 1, 1, -1), (-1, 1, 1, 1))


def need(ok, label):
    if not ok:
        raise ValueError(label)


def flatten(values):
    return tuple(v for z in values for v in z)


def ideal_pair(values, inverse=False):
    x = flatten(values)
    matrix = tuple(zip(*M)) if inverse else M
    return tuple(sum(a * b for a, b in zip(row, x)) for row in matrix)


def squared_error4(y, twice_exact):
    return sum((2 * a - b) ** 2 for a, b in zip(flatten(y), twice_exact))


def kernel_checks():
    count = phases = 0
    for x in itertools.product(range(-4, 5), repeat=4):
        values = (x[:2], x[2:])
        p = sum(x) % 2
        for inv in (False, True):
            ys = [pair(*values, s, inv) for s in (-1, 1)]
            oracle = ideal_pair(values, inv)
            need(tuple(a + b for a, b in zip(flatten(ys[0]), flatten(ys[1]))) == oracle,
                 "exact two-seed expectation")
            for s, y in zip((-1, 1), ys):
                need(pair(*y, s, not inv) == values, "literal two-sided inverse")
                need(squared_error4(y, oracle) == 4 * p, "pointwise grid minimum")
                need(tuple(y[0][j] + y[1][j] for j in (0, 1)) ==
                     tuple(values[0][j] + values[1][j] for j in (0, 1)), "complex sum")
                for unit in range(4):
                    need(pair(*(phase(z, unit) for z in values), s, inv) ==
                         tuple(phase(z, unit) for z in y), "Gaussian phase covariance")
                    phases += 1
                count += 1
    wide = 0
    for bits in (16, 64, 257, 1024):
        for signs in itertools.product((-1, 1), repeat=4):
            x = tuple(s * ((1 << bits) + j) for j, s in enumerate(signs))
            for seed in (-1, 1):
                values = (x[:2], x[2:])
                y = pair(*values, seed)
                need(pair(*y, seed, True) == values, "wide signed inverse")
                need(max(abs(a) for a in flatten(y)) <= 2 * max(map(abs, x)) + 1, "range")
                wide += 1
    return {"pair_directions": count, "phase_checks": phases, "wide_pairs": wide}


def prefix_witness(word):
    prefix = word["program"][:9896]
    row = {236: Fraction(1)}
    for e in reversed(prefix):
        op, r = e[:2]
        if op == "ADD":
            row[e[2]] = row.get(e[2], Fraction(0)) + Fraction(e[3]) * row.get(r, Fraction(0))
        elif op == "SCALE":
            row[r] = row.get(r, Fraction(0)) * Fraction(e[2])
        elif op in ("INIT", "CLEAR"):
            row.pop(r, None)
        elif op == "COPY":
            value = row.pop(r, Fraction(0))
            row[e[2]] = row.get(e[2], Fraction(0)) + Fraction(e[3]) * value
        else:
            raise ValueError("unexpected prefix operation")
        row = {r: q for r, q in row.items() if q}
    source, coeff = next(iter(sorted(row.items())))
    values = {r: Fraction(0) for r in range(word["public"])}
    need(source in values, "witness input is public")
    need(word["initial"][source] == 3, "witness input starts in the empty frame")
    values[source] = 1 / coeff
    max_denominator = values[source].denominator
    max_absolute = abs(values[source])
    for e in prefix:
        op, r = e[:2]
        if op in ("INIT", "CLEAR"):
            values[r] = Fraction(0)
        elif op == "ADD":
            values[r] += Fraction(e[3]) * values[e[2]]
        elif op == "SCALE":
            values[r] *= Fraction(e[2])
        elif op == "COPY":
            values[r] = Fraction(e[3]) * values[e[2]]
        max_denominator = max(max_denominator, values[r].denominator)
        max_absolute = max(max_absolute, abs(values[r]))
    need(values[236] == 1, "reverse row agrees with literal forward prefix")
    return {"input_field": source, "input_scalar": str(1 / coeff),
            "coefficient": str(coeff), "row_support": len(row), "prefix_events": len(prefix),
            "max_prefix_denominator": max_denominator, "max_prefix_absolute": str(max_absolute)}


def matrix_vector(real, imag, values):
    out = []
    for r, im in zip(real, imag):
        out.append((sum(int(a) * x - int(b) * y for a, b, (x, y) in zip(r, im, values)),
                    sum(int(a) * y + int(b) * x for a, b, (x, y) in zip(r, im, values))))
    return out


def native_checks(source, real, imag):
    recipes = source["recipe"]
    counts = {"native_basis_inputs": 0, "native_signed_inputs": 0, "tensor_seed_words": 0}
    sums = hashlib.sha256()
    for j in range(512):
        for unit in (0, 1):
            x = [(0, 0)] * 512
            x[j] = phase((1, 0), unit)
            ys = [native(x, recipes, (s,)) for s in (-1, 1)]
            exact = [phase((int(real[i, j]), int(imag[i, j])), unit) for i in range(512)]
            need([(a + c, b + d) for (a, b), (c, d) in zip(*ys)] == exact,
                 "source column expectation")
            for s, y in zip((-1, 1), ys):
                need(native(y, recipes, (s,), True) == x, "source basis inverse")
            counts["native_basis_inputs"] += 1
    for k in range(8):
        x = [(((i * 17 + k) % 23 - 11) * (1 << (9 * k)),
              ((i * i + 3 * k) % 19 - 9) * (1 << (5 * k))) for i in range(512)]
        exact = matrix_vector(real, imag, x)
        ys = [native(x, recipes, (s,)) for s in (-1, 1)]
        need([(a + c, b + d) for (a, b), (c, d) in zip(*ys)] == exact, "dense native expectation")
        right = monomial(x, route(recipes["right"]), 0)
        odd = sum(sum(flatten(right[j:j + 2])) % 2 for j in range(0, 512, 2))
        for s, y in zip((-1, 1), ys):
            need(native(y, recipes, (s,), True) == x, "dense native inverse")
            need(sum((2 * a - c) ** 2 + (2 * b - d) ** 2
                     for (a, b), (c, d) in zip(y, exact)) == 4 * odd, "native exact error")
        sums.update(json.dumps(ys, separators=(",", ":")).encode())
        counts["native_signed_inputs"] += 1
    # A full 512**2 tensor input; the independent oracle uses a Kronecker product.
    u = [((j % 5) - 2, 0) for j in range(512)]
    v = [((j % 7) - 3, (j % 3) - 1) for j in range(512)]
    x = [(a * c - b * d, a * d + b * c) for c, d in v for a, b in u]
    au, av = matrix_vector(real, imag, u), matrix_vector(real, imag, v)
    exact4 = [(a * c - b * d, a * d + b * c) for c, d in av for a, b in au]
    total = [(0, 0)] * len(x)
    mse16_sum = 0
    for seeds in itertools.product((-1, 1), repeat=2):
        y = native(x, recipes, seeds)
        need(native(y, recipes, seeds, True) == x, "full tensor inverse")
        total = [(a + c, b + d) for (a, b), (c, d) in zip(total, y)]
        mse16_sum += sum((4 * a - c) ** 2 + (4 * b - d) ** 2
                        for (a, b), (c, d) in zip(y, exact4))
        counts["tensor_seed_words"] += 1
    need(total == exact4, "full tensor expectation")
    need(mse16_sum <= 64 * len(x), "two-stage martingale second moment")
    counts.update(tensor_coordinates=len(x), tensor_mse=str(Fraction(mse16_sum, 64)),
                  native_output_sha256=sums.hexdigest())
    unit = [(1, 0)] + [(0, 0)] * 511
    x = monomial(unit, route(recipes["right"]), 0, True)
    exact = matrix_vector(real, imag, x)
    need(sum(a * a + b * b for a, b in x) == 1, "native relative witness has unit norm")
    for seed in (-1, 1):
        y = native(x, recipes, (seed,))
        need(sum((2 * a - c) ** 2 + (2 * b - d) ** 2
                 for (a, b), (c, d) in zip(y, exact)) == 4,
             "actual native relative witness has unit error")
    counts["relative_witness"] = [{"coordinate": j, "value": list(z)}
                                  for j, z in enumerate(x) if z != (0, 0)]
    return counts


def controls():
    x = ((1, 0), (0, 0))
    y = pair(*x, 1)
    need(pair(*y, -1, True) != x, "wrong retained seed must fail")
    need(flatten(y) != tuple(Fraction(v, 2) for v in ideal_pair(x)), "one fixed seed is biased")
    exact = ideal_pair(x)
    floor = tuple(v // 2 for v in exact)
    need(tuple(2 * v for v in floor) != exact, "deterministic floor is not unbiased")
    need(squared_error4(y, exact) == 4 and sum(v * v for v in flatten(x)) == 1,
         "relative error u<1 fails on a unit grid input")
    fixed_center_at_i = ((0, 0), (0, 1))
    need(fixed_center_at_i != tuple(phase(z, 1) for z in y),
         "a fixed real center fails phase covariance on (i,0)")
    try:
        pair(*x, 0)
    except ValueError:
        pass
    else:
        raise ValueError("invalid seed accepted")
    # Independent coins are enumerated before a search for a reuse witness.
    witness = None
    for reals in itertools.product(range(-1, 2), repeat=4):
        values = [(a, 0) for a in reals]
        ys = [layer(layer(values, s), t, 2) for s, t in itertools.product((-1, 1), repeat=2)]
        fresh4 = [tuple(sum(z[j][c] for z in ys) for c in (0, 1)) for j in range(4)]
        reused2 = [tuple(ys[0][j][c] + ys[3][j][c] for c in (0, 1)) for j in range(4)]
        if any(2 * a != b for a, b in zip(flatten(reused2), flatten(fresh4))):
            witness = {"input": list(reals), "fresh_mean": [str(Fraction(a, 4)) for a in flatten(fresh4)],
                       "reused_mean": [str(Fraction(a, 2)) for a in flatten(reused2)]}
            break
    need(witness is not None, "seed-reuse control needs an actual witness")
    return {"semantic_controls": 7, "reused_seed_witness": witness}


def main():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    inputs = [x for x in sources["files"] if x["usage"] == "input"]
    for item in inputs:
        data = (ROOT / item["path"]).read_bytes()
        need(hashlib.sha256(data).hexdigest() == item["sha256"], "input source hash")
        need(hashlib.sha256(data + b"!").hexdigest() != item["sha256"], "source corruption control")
    with tempfile.TemporaryDirectory(prefix="selected-native-unbiased-") as tmp:
        subprocess.run([sys.executable, "-I", "-W", "error", "-B", str(HERE / "produce.py"), tmp],
                       check=True, capture_output=True, text=True, timeout=120)
        source = json.loads((Path(tmp) / "source.json").read_text())
        with np.load(Path(tmp) / "oracle.npz") as arrays:
            real, imag = arrays["real"], arrays["imag"]
        word = json.loads(gzip.decompress((ROOT / inputs[0]["path"]).read_bytes()))
        result = {"source": source, "kernel": kernel_checks(),
                  "native": native_checks(source, real, imag), "prefix_witness": prefix_witness(word),
                  "controls": controls(), "source_corruption_controls": len(inputs)}
    if "--write-result" in sys.argv:
        (HERE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    else:
        need(result == json.loads((HERE / "RESULT.json").read_text()), "committed result differs")
    print("PASS_SELECTED_NATIVE_UNBIASED_ROUNDING")
    print(json.dumps({"kernel": result["kernel"], "native": result["native"],
                      "prefix_witness": result["prefix_witness"], "controls": result["controls"]}, sort_keys=True))


if __name__ == "__main__":
    main()

"""Check quotient endpoints, exact native columns and stochastic moments."""

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
from codec import Codec


def need(ok, label):
    if not ok:
        raise ValueError(label)


def check_source(data, expected):
    need(hashlib.sha256(data).hexdigest() == expected, "source bytes")


def gauss_mul(x, y):
    a, b = x
    c, d = y
    return a * c - b * d, a * d + b * c


def direct_tensor(values, axes, inverse=False):
    """Use a dense product of scalar coefficients, not butterfly stages."""
    mask = sum(1 << b for b in axes)
    out = []
    for row in range(len(values)):
        sr = si = 0
        for col, value in enumerate(values):
            if (row ^ col) & ~mask:
                continue
            coefficient = (1, 0)
            for axis in axes:
                same = ((row ^ col) >> axis & 1) == 0
                sign = (1 if same else -1) * (-1 if inverse else 1)
                coefficient = gauss_mul(coefficient, (1, sign))
            a, b = gauss_mul(coefficient, value)
            sr, si = sr + a, si + b
        out.append((Fraction(sr, 1 << len(axes)), Fraction(si, 1 << len(axes))))
    return out


def exact_moments(c, values, numerators):
    sums = [[0, 0] for _ in values]
    squares = 0
    d = c.seed_count
    for seed in range(d):
        # This loop checks the actual public quantizer for every seed.
        result = c.rounded(values, seed)
        for j, (out, raw) in enumerate(zip(result, numerators)):
            for component in (0, 1):
                sums[j][component] += out[component]
                squares += (d * out[component] - raw[component]) ** 2
    need([tuple(z) for z in sums] == numerators, "all-seed exact mean")
    variance_numerator = sum((v % d) * (d - v % d) for z in numerators for v in z)
    need(squares == d * variance_numerator, "exact pointwise minimum second moment")
    need(variance_numerator * 2 <= c.n * d * d, "native variance upper bound")
    return {"seeds": d, "variance": str(Fraction(variance_numerator, d * d))}


def finite_quotients():
    count = collisions = 0
    for h, r, k in ((1, 0, 1), (1, 1, 1), (2, 2, 1)):
        c = Codec({"rank": r, "left": None, "right": None}, h, 1, k)
        if c.n == 2:
            outputs = [list(zip(v[::2], v[1::2])) for v in itertools.product((-1, 0, 1), repeat=4)]
        else:
            outputs = [[(0, 0)] * c.n]
            for j in range(2 * c.n):
                for sign in (-1, 1):
                    out = [[0, 0] for _ in range(c.n)]
                    out[j // 2][j % 2] = sign
                    outputs.append([tuple(z) for z in out])
        for seed in range(c.seed_count):
            seen = set()
            for label in range(1 << c.bits):
                packed = label.to_bytes((c.bits + 7) // 8, "little")
                for index, q in enumerate(outputs):
                    x = c.restore(q, packed, seed)
                    actual, residue = c.encode(x, seed)
                    need(actual == q and residue == packed, "arbitrary coarse/label endpoint")
                    if index == 0:
                        seen.add(tuple(x))
                    count += 1
            need(len(seen) == 1 << c.bits, "every residue labels a distinct input at one output")
        zero = bytes((c.bits + 7) // 8)
        first = c.restore([(0, 0)] * c.n, zero, 0)
        for bit in range(c.bits):
            packed = (1 << bit).to_bytes(len(zero), "little")
            x = c.restore([(0, 0)] * c.n, packed, 0)
            need(x != first and c.rounded(x, 0) == c.rounded(first, 0), "each retained bit can matter")
            collisions += 1
    fixtures = stages = 0
    for h, r, f in ((1, 1, 1), (1, 1, 2), (1, 1, 3), (2, 1, 2), (2, 2, 2), (3, 2, 1)):
        a = r * f
        for k in ((a + 1) // 2, (a + 1) // 2 + 1):
            c = Codec({"rank": r, "left": None, "right": None}, h, f, k)
            for t in range(3):
                x = [((j * 13 + t) % 9 - 4, (j * j + 2 * t) % 11 - 5) for j in range(c.n)]
                oracle = direct_tensor(x, c.axes)
                actual = c.exact(x)
                need([(Fraction(a, 1 << c.d), Fraction(b, 1 << c.d)) for a, b in actual] == oracle,
                     "dense tensor oracle")
                inverse = c.exact(actual, True)
                need(inverse == [(a << (2 * c.d), b << (2 * c.d)) for a, b in x], "exact tensor inverse")
                moments = exact_moments(c, x, actual)
                for seed in range(c.seed_count):
                    q, packed = c.encode(x, seed)
                    need(c.restore(q, packed, seed) == x, "small tensor data return")
                    stages += 1
                fixtures += 1
    return {"complete_quotient_endpoints": count, "retained_bit_witnesses": collisions,
            "dense_tensor_fixtures": fixtures, "small_seed_roundtrips": stages}


def oracle_vector(real, imag, values, exponent, d):
    out = []
    for rr, ii in zip(real, imag):
        a = sum(int(r) * x - int(i) * y for r, i, (x, y) in zip(rr, ii, values))
        b = sum(int(r) * y + int(i) * x for r, i, (x, y) in zip(rr, ii, values))
        scale = 1 << max(exponent - d, 0)
        if exponent >= d:
            need(a % scale == b % scale == 0, "source oracle numerator reduction")
            out.append((a // scale, b // scale))
        else:
            out.append((a << (d - exponent), b << (d - exponent)))
    return out


def source_checks(source, arrays):
    columns = returns = endpoints = seeds = 0
    moment_records = []
    first = None
    for item in source["representatives"]:
        r = item["rank"]
        c = Codec(item["recipe"], 9, 1, 5)
        real, imag = arrays[f"r{r}_real"], arrays[f"r{r}_imag"]
        exp = item["oracle_exponent"]
        for col in range(512):
            x = [(0, 0)] * 512
            x[col] = (1, 0)
            actual = c.exact(x)
            need(all(a * (1 << exp) == int(real[row, col]) * (1 << c.d) and
                     b * (1 << exp) == int(imag[row, col]) * (1 << c.d)
                     for row, (a, b) in enumerate(actual)), "new interpreter source columns")
            if col == 0:
                need(any(abs(v) == 1 for z in actual for v in z), "primitive seed-denominator witness")
            columns += 1
        for t, bits in enumerate((0, 8, 64, 257)):
            x = [(((j * 13 + t) % 17 - 8) << bits,
                  ((j * j + 3 * t) % 19 - 9) << max(bits - 1, 0)) for j in range(512)]
            actual = c.exact(x)
            need(actual == oracle_vector(real, imag, x, exp, c.d), "signed dense source oracle")
            for seed in (0, 1, c.seed_count // 2, c.seed_count - 1):
                q, packed = c.encode(x, seed)
                need(len(packed) == 640 and c.restore(q, packed, seed) == x, "actual native changed-grid return")
                returns += 1
            if t == 0:
                record = exact_moments(c, x, actual)
                seeds += record["seeds"]
                moment_records.append({"rank": r, **record})
        for byte in (0, 85, 170, 255):
            packed = bytes([byte]) * 640
            q = [((j % 7) - 3, (j % 5) - 2) for j in range(512)]
            for seed in (0, c.seed_count - 1):
                x = c.restore(q, packed, seed)
                need(c.encode(x, seed) == (q, packed), "full source arbitrary output/residue endpoint")
                endpoints += 1
        if r == 1:
            first = item["recipe"]
    need(first is not None, "selected rank-one source exists")
    c = Codec(first, 9, 2, 1)
    # A complete tensor field, with a coarse/fine ratio of two.
    x = [((j % 5) - 2, (j % 7) - 3) for j in range(c.n)]
    actual = c.exact(x)
    tensor = exact_moments(c, x, actual)
    digest = hashlib.sha256()
    for seed in range(c.seed_count):
        q, packed = c.encode(x, seed)
        need(c.restore(q, packed, seed) == x, "full 512**2 changed-grid inverse")
        digest.update(packed)
        digest.update(json.dumps(q, separators=(",", ":")).encode())
    return {"new_interpreter_columns": columns, "signed_native_roundtrips": returns,
            "arbitrary_source_endpoints": endpoints, "native_seed_executions": seeds,
            "native_moments": moment_records, "tensor_coordinates": c.n,
            "tensor_residue_bits": c.bits, "tensor_seed_roundtrips": c.seed_count,
            "tensor_moments": tensor, "tensor_output_sha256": digest.hexdigest()}


def controls(source, arrays):
    small = Codec({"rank": 1, "left": None, "right": None}, 1, 1, 1)
    q = [(0, 0), (0, 0)]
    a = small.restore(q, b"\x00", 0)
    b = small.restore(q, b"\x01", 0)
    need(a != b and small.rounded(a, 0) == small.rounded(b, 0), "coarse output alone loses information")
    need(small.restore(q, b"\x01", small.seed_count - 1) != b, "wrong retained seed")
    for action in (lambda: Codec({"rank": 1, "left": None, "right": None}, 1, 1, 0),
                   lambda: small.restore(q, b"\x10", 0),
                   lambda: small.restore(q, b"", 0),
                   lambda: small.rounded(q, True),
                   lambda: small.rounded(q, small.seed_count)):
        try:
            action()
        except ValueError:
            pass
        else:
            raise ValueError("invalid grid, residue or seed accepted")
    period = direct_tensor([(1, 0), (0, 0)], (0,), True)
    need(any(v.denominator != 1 for z in period for v in z), "k=0 inverse-period integrality witness")
    d = small.seed_count
    need(sum(small.rounded([(1, 0), (0, 0)], u)[0][0] for u in range(0, d, 2)) == 0,
         "one fewer fair bit can bias a primitive fraction")
    need(small.rounded([(-1, 0), (0, 0)], 0)[0][0] == -1 and int(Fraction(-1, d)) == 0,
         "signed floor is not truncation")
    item = source["representatives"][0]
    bad = json.loads(json.dumps(item["recipe"]))
    bad["left"]["phase"] = (bad["left"]["phase"] + 1) % 4
    c = Codec(bad, 9, 1, 5)
    x = [(1, 0)] + [(0, 0)] * 511
    actual = c.exact(x)
    real, imag = arrays['r1_real'], arrays['r1_imag']
    expected = oracle_vector(real, imag, x, item["oracle_exponent"], c.d)
    need(actual != expected, "changed native global phase rejected by the source oracle")
    return {"semantic_and_domain_controls": 11}


def main():
    files = [x for x in json.loads((HERE / "SOURCES.json").read_text())["files"] if x["usage"] == "input"]
    for item in files:
        data = (ROOT / item["path"]).read_bytes()
        check_source(data, item["sha256"])
        try:
            check_source(data + b"!", item["sha256"])
        except ValueError:
            pass
        else:
            raise ValueError("changed source bytes were accepted")
    with tempfile.TemporaryDirectory(prefix="native-coarse-grid-") as tmp:
        subprocess.run([sys.executable, "-I", "-W", "error", "-B", str(HERE / "produce.py"), tmp],
                       check=True, capture_output=True, text=True, timeout=240)
        source = json.loads((Path(tmp) / "source.json").read_text())
        with np.load(Path(tmp) / "oracle.npz") as archive:
            arrays = {k: archive[k] for k in archive.files}
        result = {"source": source, "finite": finite_quotients(), "native": source_checks(source, arrays),
                  "controls": controls(source, arrays), "source_corruption_controls": len(files)}
    if "--write-result" in sys.argv:
        (HERE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    else:
        need(result == json.loads((HERE / "RESULT.json").read_text()), "committed result differs")
    print("PASS_NATIVE_COARSE_GRID_RESIDUE_CODEC")
    print(json.dumps({k: v for k, v in result.items() if k != "source"}, sort_keys=True))


if __name__ == "__main__":
    main()

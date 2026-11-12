#!/usr/bin/env python3
"""Exact four-coordinate rounded half-shear certificate. Read-only, stdlib."""

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
import struct


def require(condition, message):
    if not condition:
        raise ValueError(message)


def half_round(n):
    """Nearest-even rounding of n/2, including negative n."""
    return n // 2 + (n % 4 == 3)


def evaluate(x, target, source):
    require(type(target) is int and type(source) is int, "integer indices")
    require(0 <= target < 4 and 0 <= source < 4 and target != source,
            "distinct indices in 0..3")
    require(len(x) == 4, "four coordinates")
    require(all(type(v) is int and abs(v) < 2**128 for v in x),
            "integer coordinates of fewer than 129 signed bits")
    return evaluate_core(x, target, source)


def evaluate_core(x, target, source):
    # Both butterfly inputs are read before either output is stored.
    a, b, c, d = x
    y = (half_round(a + b), half_round(a - b),
         half_round(c + d), half_round(c - d))
    z = list(y)
    z[target] = half_round(2 * y[target] + y[source])
    output = (half_round(z[0] + z[2]), half_round(z[1] + z[3]),
              half_round(z[0] - z[2]), half_round(z[1] - z[3]))
    # u is four times S A x. The source is unchanged by the shear.
    u = [2 * (a + b), 2 * (a - b), 2 * (c + d), 2 * (c - d)]
    u[target] += u[source] // 2
    ideal8 = (u[0] + u[2], u[1] + u[3], u[0] - u[2], u[1] - u[3])
    error8 = tuple(8 * output[j] - ideal8[j] for j in range(4))
    return y, tuple(z), output, ideal8, error8


def census():
    digest = hashlib.sha256()
    rows = []
    total = 0
    for target in range(4):
        for source in range(4):
            if target == source:
                continue
            counts = [0] * 10
            witness = None
            for x in itertools.product(range(16), repeat=4):
                error = evaluate_core(x, target, source)[4]
                peak = max(abs(v) for v in error)
                require(peak <= 9, "universal residue upper bound")
                counts[peak] += 1
                digest.update(struct.pack("4b", *error))
                if peak == 9 and witness is None:
                    witness = list(x)
                total += 1
            require(counts[9] > 0, "each orientation attains 9/8")
            require(sum(counts) == 16**4, "complete residue domain")
            rows.append({"target": target, "source": source,
                         "max_error8": 9, "peak_histogram": counts,
                         "first_witness": witness})
    require(total == 12 * 16**4, "complete directed-pair domain")
    return {"cases": total, "coordinates": 4 * total, "rows": rows,
            "error_stream_sha256": digest.hexdigest()}


def controls():
    for n in range(-257, 258):
        require(half_round(n) == round(Fraction(n, 2)), "signed nearest-even")
    period_checks = 0
    for target in range(4):
        for source in range(4):
            if target == source:
                continue
            for x in ((0, 0, 0, 0), (1, 4, 0, 1), (-3, 2, -1, 7)):
                base = evaluate(x, target, source)
                for axis in range(4):
                    for shift in (-2**80, -1, 1, 2**80):
                        moved = list(x)
                        moved[axis] += 16 * shift
                        require(evaluate(moved, target, source)[4] == base[4],
                                "signed and large period translation")
                        period_checks += 1
    require(evaluate((0, 0, 0, 2), 0, 1)[4] !=
            evaluate((8, 0, 0, 2), 0, 1)[4], "period eight is insufficient")
    require(evaluate((1, 4, 0, 1), 0, 1)[4] == (-9, 0, -5, -4),
            "sharp complete endpoint")
    require(half_round(1) != 1 and half_round(-1) != -1, "ties away differ")
    invalid = [((0, 0, 0), 0, 1), ((0, 0, 0, 0), 1, 1),
               ((0, 0, 0, 0), -1, 1), ((0, 0, 0, 0), 0, 4),
               ((0, 0, 0, 0), True, 1), ((0, 0, 0, 0.5), 0, 1),
               ((True, 0, 0, 0), 0, 1), ((2**128, 0, 0, 0), 0, 1)]
    for x, target, source in invalid:
        try:
            evaluate(x, target, source)
        except ValueError:
            continue
        raise ValueError("invalid input accepted")
    return {"rounding_checks": 515, "period_checks": period_checks,
            "rejected_inputs": len(invalid), "semantic_controls": 3}


def package_hashes():
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "CODE-BOUNDS.md", "TASK.json",
             "SOURCES.json", "VERIFY.json", "verify.py", "independent.py")
    result = {}
    for name in names:
        path = package / name
        require(path.is_file() and not path.is_symlink(), "regular package input")
        require(path.stat().st_size <= 1024**2, "bounded receipt input")
        result[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    source_path = package.parent / "walsh-interleaved-shear" / "PROOF.md"
    require(source_path.stat().st_size <= 1024**2, "bounded predecessor input")
    source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    require(source_hash == "e16cb441209c6a093c2f21eeec96819b88a7f8a74bd7df103267ddf88c9f644a",
            "predecessor context pin")
    result["../walsh-interleaved-shear/PROOF.md"] = source_hash
    return result


def main():
    report = {"status": "PASS_ROUNDED_HALF_SHEAR_WALSH",
              "claim_type": "scoped proof with exhaustive finite corroboration",
              "sharp_error": "9/8", "package_sha256": package_hashes(),
              "controls": controls(), "census": census()}
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()

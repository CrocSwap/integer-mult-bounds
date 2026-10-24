"""Independent finite corroboration and source-bound stdout receipt."""
import hashlib
import itertools
import json
import platform
import sys
from fractions import Fraction
from pathlib import Path

# An isolated script starts here; no external package implementation is imported.
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from box import analyze, MAX_BITS


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def literal(value, gap):
    """Separate quotient/remainder implementation of both signed roundings."""
    integer, remainder = divmod(value.numerator, value.denominator)
    coarse = integer + (2 * remainder >= value.denominator)
    scaled = value * (1 << gap)
    integer, remainder = divmod(scaled.numerator, scaled.denominator)
    fine = Fraction(integer + (2 * remainder >= scaled.denominator), 1 << gap)
    return coarse == fine


def compare(offset, coefficients, widths, gap):
    safe, witness, _, _ = analyze(offset, coefficients, widths, gap)
    failures = []
    points = 0
    for point in itertools.product(*(range(b + 1) for b in widths)):
        points += 1
        value = offset + sum(a * z for a, z in zip(coefficients, point, strict=True))
        if not literal(value, gap):
            failures.append(point)
    require(safe == (not failures), "box verdict differs from literal rounding")
    require((witness is None) == safe, "witness presence differs from verdict")
    if not safe:
        require(witness in failures, "witness is not an actual failing point")
    return points, int(safe)


def exhaustive():
    alphabet = tuple(sorted({Fraction(a, d) for d in range(1, 7)
                             for a in range(-d, d + 1)}))
    counts = {"boxes": 0, "points": 0, "safe_boxes": 0}
    offsets = (Fraction(0), Fraction(1, 4), Fraction(-1, 4),
               Fraction(1, 8), Fraction(-1, 8), Fraction(7, 8))
    for coefficients in itertools.product(alphabet, repeat=2):
        for widths in ((0, 0), (0, 3), (1, 1), (1, 2), (2, 2), (3, 2)):
            for offset, gap in itertools.product(offsets, (1, 2, 3)):
                points, safe = compare(offset, coefficients, widths, gap)
                counts["boxes"] += 1
                counts["points"] += points
                counts["safe_boxes"] += safe
    return counts


def extra_dimensions():
    cases = points = 0
    alphabet = (Fraction(-1, 5), Fraction(0), Fraction(1, 5))
    for coefficients in itertools.product(alphabet, repeat=4):
        for offset in (Fraction(0), Fraction(-1, 4), Fraction(1, 8)):
            count, _ = compare(offset, coefficients, (1, 2, 1, 2), 1)
            cases += 1
            points += count
    for gap in range(1, 9):
        for offset in (Fraction(0), Fraction(-1, 4), Fraction(1, 4)):
            count, _ = compare(offset, (), (), gap)
            cases += 1
            points += count
    return {"boxes": cases, "points": points}


def controls():
    # Every listed example has an independent literal expected behavior.
    fixtures = (
        (Fraction(0), (Fraction(1, 8),) * 2, (1, 1), 1, False),
        (Fraction(0), (Fraction(-1, 8),) * 2, (1, 1), 1, True),
        (Fraction(-1, 4), (Fraction(1, 2),), (1,), 1, False),
        (Fraction(-1, 5), (Fraction(2, 5),), (1,), 1, True),
        (Fraction(0), (Fraction(9, 10),), (2,), 1, True),
        (Fraction(0), (Fraction(1, 2),), (0,), 1, True),
        (Fraction(1, 4), (Fraction(0),), (1,), 1, False),
        (Fraction(-1, 4), (Fraction(0),), (1,), 1, True),
    )
    for offset, coeff, widths, gap, expected in fixtures:
        compare(offset, coeff, widths, gap)
        require(analyze(offset, coeff, widths, gap)[0] == expected, "control verdict")
    # Endpoints alone are insufficient: both endpoints are integral.
    result = analyze(0, (Fraction(1, 2),), (2,), 1)
    require(result[1] == (1,), "must find interior failure between safe endpoints")
    # Large dimensions/widths use arithmetic jumps, never a box enumeration.
    big = 1 << 200
    result = analyze(0, (Fraction(1, 8 * big),) * 32, (big,) * 32, 1)
    require(result[1] == (big, big) + (0,) * 30, "huge-box first exit")
    require(analyze(0, (Fraction(1, 256 * big),) * 32, (big,) * 32, 1)[0],
            "nonintegral huge box is safe")
    invalid = (
        (0.0, (), (), 1), (True, (), (), 1), (0, [1], (1,), 1),
        (0, (1,), (True,), 1), (0, (1,), (-1,), 1),
        (0, (1,), (), 1), (0, (1,) * 33, (1,) * 33, 1),
        (0, (), (), 0), (0, (), (), True), (0, (), (), 257),
        (1 << MAX_BITS, (), (), 1), (0, (1,), (1 << MAX_BITS,), 1),
    )
    for args in invalid:
        try:
            analyze(*args)
        except ValueError:
            continue
        raise AssertionError("invalid boundary accepted")
    return {"semantic_fixtures": len(fixtures) + 1, "huge_boxes": 2,
            "invalid_inputs": len(invalid)}


def dirty_targets():
    total = 0
    for gap in range(1, 6):
        radius = Fraction(1, 2 << gap)
        coefficients = (radius / 3, -radius / 3)
        for point in itertools.product(range(3), repeat=2):
            value = sum(a * z for a, z in zip(coefficients, point, strict=True))
            for dirt in (Fraction(-17, 3), Fraction(0), Fraction(29, 7)):
                def rounded(v, scale):
                    n, r = divmod((v * scale).numerator, (v * scale).denominator)
                    return Fraction(n + (2 * r >= (v * scale).denominator), scale)
                require(dirt + rounded(value, 1) - rounded(value, 1 << gap) == dirt,
                        "safe unequal-precision inverse did not restore dirty target")
                total += 1
    return total


def main():
    require(len(sys.argv) == 1, "no command-line arguments are supported")
    payload = {"two_dimensional": exhaustive(), "additional": extra_dimensions(),
               "controls": controls(), "dirty_target_cases": dirty_targets()}
    root = Path(__file__).resolve().parent
    names = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "box.py", "verify.py")
    sources = {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
               for name in names}
    print(json.dumps({"status": "PASS_AFFINE_BOX_INVERSE_PRECISION", "result": payload,
                      "sources_sha256": sources, "python": platform.python_version()},
                     sort_keys=True))


if __name__ == "__main__":
    main()

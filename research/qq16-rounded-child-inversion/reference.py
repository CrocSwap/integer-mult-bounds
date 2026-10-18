#!/usr/bin/env python3
"""Finite QQ16 rank-one child and rounded half-ADD. Apache-2.0."""

import argparse
import gzip
import hashlib
import io
import json
import tarfile
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DIM = 512
MEMBER = "slots/local/CLIFFORD-RECIPES.json"
MEMBER_SHA = "d0768f2164d5f64a2fdbec422f1cfde4e400818792f1904ca541958377243731"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def bounded(path, cap):
    need(path.is_file() and not path.is_symlink(), "plain input file")
    with path.open("rb") as stream:
        raw = stream.read(cap + 1)
    need(len(raw) <= cap, "input size capacity")
    return raw


def load():
    inventory = json.loads(bounded(HERE / "SOURCES.json", 32768))
    need(len(inventory["files"]) <= 16, "source inventory capacity")
    for pin in inventory["files"]:
        if pin["usage"] == "input":
            raw = bounded(ROOT / pin["path"], 24_000_000)
            need(hashlib.sha256(raw).hexdigest() == pin["sha256"], "source hash")
    raw = bounded(ROOT / "research/joint-query/certificate.json.gz", 1_000_000)
    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
        decoded = stream.read(12_000_001)
    need(len(decoded) <= 12_000_000, "decoded packet capacity")
    packet = json.loads(decoded)
    events = []
    for event in packet["programs"]["B_1_2"]:
        kind = event[0]
        if kind == "retained_core":
            events.extend(packet["core_words"][event[1]])
        elif kind in ("private_sweep", "cover_sweep"):
            events.extend(event[2])
        else:
            events.append(event)
    need(len(events) == 27019, "literal B1 event count")
    expected = {
        11795: ["climb", "A", 470, 0, 5, 1],
        11796: ["scalar", ["add", ["L", 524], ["L", 470], -1, 2], 5],
        13489: ["climb", "A", 344, 226, 236, 1],
        13491: ["scalar", ["add", ["L", 346], ["L", 344], -1, 1], 236],
    }
    need(
        all(events[i] == value for i, value in expected.items()), "literal pair binding"
    )
    archive_path = ROOT / "research/community-frontier1042-audit/selected-replay.tar.gz"
    with tarfile.open(archive_path) as archive:
        member = archive.getmember(MEMBER)
        need(member.isfile() and member.size <= 4_000_000, "bounded recipe member")
        stream = archive.extractfile(member)
        need(stream is not None, "regular recipe member")
        raw = stream.read(4_000_001)
    need(hashlib.sha256(raw).hexdigest() == MEMBER_SHA, "recipe member hash")
    children = json.loads(raw)["children"]
    need(len(children) <= 10000, "recipe count capacity")
    recipes = []
    for old, new in ((0, 5), (226, 236)):
        matches = [r for r in children if (r["old"], r["new"]) == (old, new)]
        need(len(matches) == 1 and matches[0]["rank"] == 1, "unique rank-one child")
        recipes.append(matches[0])
    return expected, recipes


def table(record):
    rows, quad, linear = (
        record[k] for k in ("matrix_rows", "quadratic_rows", "linear_Z4")
    )
    need(len(rows) == len(quad) == len(linear) == 9, "nine-axis monomial")
    need(all(type(v) is int and 0 <= v < DIM for v in rows + quad), "binary masks")
    need(all(type(v) is int and 0 <= v < 4 for v in linear), "phase coefficients")
    result = []
    for x in range(DIM):
        dest = record["offset"] ^ sum(
            ((x & r).bit_count() % 2) << j for j, r in enumerate(rows)
        )
        angle = record["phase"] + sum(linear[j] for j in range(9) if (x >> j) & 1)
        angle += 2 * sum(
            (quad[j] & x & ~((1 << (j + 1)) - 1)).bit_count()
            for j in range(9)
            if (x >> j) & 1
        )
        result.append((dest, angle % 4))
    need(sorted(i for i, _ in result) == list(range(DIM)), "monomial permutation")
    return result


def rotate(a, b, phase):
    return ((a, b), (-b, a), (-a, -b), (b, -a))[phase]


def monomial(source, target, mapping, counts):
    for x in range(DIM):
        dest, phase = mapping[x]
        target[dest] = rotate(*source[x], phase)
    counts["signed_component_moves"] += 2 * DIM


def nearest(n, precision):
    """Round an integer to p significant bits, ties to even; no float or underflow."""
    shift = max(0, abs(n).bit_length() - precision)
    quantum = 1 << shift
    lower, remainder = divmod(abs(n), quantum)
    increment = 2 * remainder > quantum or (2 * remainder == quantum and lower % 2)
    rounded = (lower + int(increment)) * quantum
    return -rounded if n < 0 else rounded


def checked_round(n, precision, width, counts):
    need(abs(n) < 1 << (width - 1), "temporary signed width")
    out = nearest(n, precision)
    need(abs(out) < 1 << (width - 1), "rounded signed width")
    counts["rounds"] += 1
    counts["nonzero_rounds"] += int(out != n)
    return out


def entry_width(source, destination, precision, span):
    need(type(precision) is int and 2 <= precision <= 4096, "precision capacity")
    need(type(span) is int and 1 <= span <= 2048, "entry exponent span")
    need(
        type(source) is list
        and type(destination) is list
        and source is not destination,
        "distinct owned destination arrays",
    )
    need(len(source) == len(destination) == DIM, "payload dimensions")
    bound, width = 4 << span, span + 6
    for value in source + destination:
        need(
            len(value) == 2
            and all(
                type(n) is int
                and abs(n) < bound
                and n % 4 == 0
                and nearest(n, precision) == n
                for n in value
            ),
            "entry format",
        )
    return width


def run(source, destination, recipe, precision, span):
    width = entry_width(source, destination, precision, span)
    right, left = table(recipe["right"]), table(recipe["left"])
    a, b = [(0, 0)] * DIM, [(0, 0)] * DIM
    counts = Counter()
    counts["scratch_component_clears"] += 4 * DIM
    monomial(source, a, right, counts)
    for x in range(0, DIM, 2):
        ar, ai = a[x]
        br, bi = a[x + 1]
        pair = [
            checked_round(n, precision, width, counts)
            for n in (ar + br, ai + bi, ar - br, ai - bi)
        ]
        sr, si, dr, di = pair
        cross = [
            checked_round(n, precision, width, counts)
            for n in (sr - di, si + dr, sr + di, si - dr)
        ]
        need(all(n % 2 == 0 for n in cross), "exact native halving lattice")
        b[x], b[x + 1] = (cross[0] // 2, cross[1] // 2), (cross[2] // 2, cross[3] // 2)
    counts["additions"] += 4 * DIM
    counts["exact_halvings"] += 2 * DIM
    counts["native_nonzero_rounds"] = counts["nonzero_rounds"]
    monomial(b, source, left, counts)
    for x in range(DIM):
        need(all(n % 2 == 0 for n in source[x]), "exact half-ADD multiplication")
        destination[x] = tuple(
            checked_round(d - s // 2, precision, width, counts)
            for d, s in zip(destination[x], source[x], strict=True)
        )
    counts["additions"] += 2 * DIM
    counts["exact_halvings"] += 2 * DIM
    counts["halfadd_nonzero_rounds"] = (
        counts["nonzero_rounds"] - counts["native_nonzero_rounds"]
    )
    a[:] = b[:] = [(0, 0)] * DIM
    counts["scratch_component_clears"] += 4 * DIM
    need(
        not any(ar or ai or br or bi for (ar, ai), (br, bi) in zip(a, b, strict=True)),
        "scratch return",
    )
    return source, destination, dict(sorted(counts.items()))


def norm2(value):
    return sum(a * a + b * b for a, b in value)


def error2(left, right):
    return sum(
        (a - c) ** 2 + (b - d) ** 2 for (a, b), (c, d) in zip(left, right, strict=True)
    )


def exact(source, destination, recipe):
    """Separate direct four-term Gaussian formula, with no rounded butterfly."""
    a, transformed = [(0, 0)] * DIM, [(0, 0)] * DIM
    monomial(source, a, table(recipe["right"]), Counter())
    for x in range(DIM):
        ar, ai = a[x]
        br, bi = a[x ^ 1]
        transformed[x] = (Q(ar - ai + br + bi, 2), Q(ai + ar + bi - br, 2))
    result = [(0, 0)] * DIM
    monomial(transformed, result, table(recipe["left"]), Counter())
    return result, [
        (Q(a) - c / 2, Q(b) - d / 2)
        for (a, b), (c, d) in zip(destination, result, strict=True)
    ]


def fixtures(recipes):
    results = []
    for recipe in recipes:
        for precision in (2, 3, 5, 11, 53, 104, 256):
            span = precision + 3
            top = 1 << (precision - 1)
            source = [
                (
                    4 * (top + (x * 37 + 11) % top) * (-1 if x % 3 else 1),
                    4 * (top + (x * 19 + 3) % top) * (-1 if x % 5 else 1),
                )
                for x in range(DIM)
            ]
            destination = [(b, -a) for a, b in reversed(source)]
            before = source.copy(), destination.copy()
            ideal, _ = exact(source, destination, recipe)
            out, added, counts = run(source, destination, recipe, precision, span)
            eps = Q(1, 1 << precision)
            rho = 2 * eps + eps * eps
            need(norm2(ideal) == norm2(before[0]), "exact child isometry")
            need(
                error2(out, ideal) <= rho * rho * norm2(before[0]),
                "native relative contract",
            )
            half_ideal = [
                (Q(a) - Q(c, 2), Q(b) - Q(d, 2))
                for (a, b), (c, d) in zip(before[1], out, strict=True)
            ]
            need(
                error2(added, half_ideal) <= eps * eps * norm2(half_ideal),
                "half-ADD actual-operand contract",
            )
            need(
                out is source and added is destination,
                "only the two declared destinations",
            )
            need(counts["additions"] == counts["rounds"] == 3072, "arithmetic counts")
            need(
                counts["native_nonzero_rounds"] > 0
                and counts["halfadd_nonzero_rounds"] > 0,
                "nonzero native and half-ADD rounding fixture",
            )
            digest = hashlib.sha256(repr((out, added)).encode()).hexdigest()
            results.append(
                {
                    "old": recipe["old"],
                    "new": recipe["new"],
                    "precision": precision,
                    "counts": counts,
                    "endpoint_sha256": digest,
                }
            )
    return results


def audit():
    events, recipes = load()
    values = fixtures(recipes)
    for precision in range(2, 9):
        for n in range(-2048, 2049):
            out = nearest(n, precision)
            need(
                abs(out - n) <= Q(abs(n), 1 << precision),
                "integer rounding relative bound",
            )
            need(nearest(-n, precision) == -out, "signed rounding symmetry")
    for target_bits in (1, 10, 102, 2048):
        eps = Q(1, 1 << (target_bits + 2))
        need(2 * eps + eps * eps <= Q(1, 1 << target_bits), "PR3235 local tolerance")
    return {
        "schema_version": 1,
        "status": "PASS_QQ16_FINITE_CHILD_HALFADD",
        "event_bindings": {str(k): v for k, v in events.items()},
        "fixture_cases": values,
        "rounding_scalar_checks": 28679,
        "working_grid": "entry_quantum/4",
        "signed_width": "entry_exponent_span+6",
        "precision_for_PR3235": "p >= beta+delta+104",
        "logical_live_component_words": 4104,
        "physical_owner_routing_priced": False,
        "recursive_tariff_priced": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    result = audit()
    if args.write:
        with args.write.open("x") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        need(
            result == json.loads(bounded(HERE / "RESULT.json", 100000)),
            "receipt equality",
        )
    print(result["status"])


if __name__ == "__main__":
    main()

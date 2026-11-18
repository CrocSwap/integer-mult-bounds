"""Check row descriptors against the retained canonical routing compiler.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import random

from row import MAX_HEIGHT, Countdown, Row, binary_template, describe, require, stream

PACKAGE = Path(__file__).resolve().parent


def load_sources():
    for pin in json.loads((PACKAGE / "SOURCE-PINS.json").read_text()):
        require(hashlib.sha256((PACKAGE / pin["path"]).read_bytes()).hexdigest()
                == pin["sha256"], "retained source hash")
    modules = []
    for name, path in (("canonical", "retained/pr4100/check_batched_crt.py"),
                       ("closed", "retained/pr7734/query.py")):
        spec = importlib.util.spec_from_file_location(name, PACKAGE / path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        modules.append(module)
    return modules


def inspect_row(row):
    require(len(row.rectangles) <= 3, "rectangle cap")
    previous = 0
    for t0, t1, y0, y1 in row.rectangles:
        require(previous <= t0 < t1 <= 1 << row.depth, "disjoint remainder strips")
        require(0 <= y0 < y1 <= 1 << (row.height - row.depth), "quotient bounds")
        require(y0 % 2 == y1 % 2 == 0, "switch-pair endpoints")
        previous = t1


def census(canonical, closed):
    result = dict(networks=0, rows=0, canonical_entries=0, closed_entries=0,
                  streamed_entries=0, switch_pairs=0, first_rows=0, center_rows=0)
    histogram = {str(k): 0 for k in range(4)}
    digest = hashlib.sha256()
    total_stats = dict(template_bits=0, counter_bits_copied=0,
                       counter_bit_visits=0, emitted_bits=0, blocks=0, phases=0)
    mutants = {}
    for h in range(1, 7):
        size = 1 << h
        for s in range(1, size + 1):
            for a in range(s):
                layers = canonical.benes(canonical.rotation(size, s, a))
                result["networks"] += 1
                for j, (axis, expected) in enumerate(layers):
                    row = describe(h, s, a, j)
                    inspect_row(row)
                    require(axis == row.depth, "canonical row axis")
                    if j < h - 1:
                        require(len(row.rectangles) <= 1, "first row cap")
                        result["first_rows"] += 1
                    if j == h - 1:
                        require(len(row.rectangles) <= 1, "center row cap")
                        result["center_rows"] += 1
                    bits = [row.bit(x) for x in range(size)]
                    require(bits == list(expected), "canonical row mismatch")
                    require(bits == [closed.switch_bit(h, s, a, j, x) for x in range(size)],
                            "closed point mismatch")
                    stats = {}
                    require(list(stream(row, stats)) == bits, "stream order or value")
                    require(stats["counter_bit_visits"] < 4 * size, "counter work")
                    require(stats["counter_bits_copied"] <= size + 7 * (h + 1), "counter copies")
                    require(stats["template_bits"] <= 56 * (h + 1), "template work")
                    require(stats["emitted_bits"] == size and stats["phases"] <= 7,
                            "stream output size")
                    for key, value in stats.items():
                        total_stats[key] += value
                    require(row.ones() == sum(expected), "rectangle areas")
                    for x in range(size):
                        require(bits[x] == bits[x ^ (1 << axis)], "paired switch bits")
                    result["switch_pairs"] += size // 2
                    histogram[str(len(row.rectangles))] += 1
                    result["rows"] += 1
                    for key in ("canonical_entries", "closed_entries", "streamed_entries"):
                        result[key] += size
                    digest.update(bytes(bits))
                    if row.rectangles:
                        rects = row.rectangles
                        t0, t1, y0, y1 = rects[0]
                        candidates = {
                            "lost rectangle": rects[1:],
                            "short quotient interval": ((t0, t1, y0, y1 - 1),) + rects[1:],
                            "lost remainder boundary": ((t0 + 1, t1, y0, y1),) + rects[1:],
                        }
                        for name, changed in candidates.items():
                            if name not in mutants:
                                mutant = Row(h, row.depth, changed)
                                witness = next((x for x in range(size) if mutant.bit(x) != bits[x]), None)
                                if witness is not None:
                                    mutants[name] = dict(query=[h, s, a, j, witness], expected=bits[witness],
                                                         mutant=mutant.bit(witness))
    require(len(mutants) == 3, "undetected rectangle mutation")
    result.update(rectangle_histogram=histogram, table_sha256=digest.hexdigest(),
                  stream_work=total_stats, semantic_mutants=mutants)
    return result


def sharpness(closed):
    row = describe(6, 53, 25, 7)
    expected = ((0, 4, 2, 8), (4, 7, 0, 6), (7, 8, 0, 4))
    require(row.rectangles == expected, "sharp row descriptor")
    points = [(0, 6), (4, 4), (7, 0)]
    cross_zeros = []
    for t, y in points:
        require(closed.switch_bit(6, 53, 25, 7, 8*y+t) == 1, "fooling-set point")
    for i, (t, y) in enumerate(points):
        for u, v in points[i+1:]:
            candidates = [(t, v), (u, y)]
            zero = next(((r, q) for r, q in candidates
                         if closed.switch_bit(6, 53, 25, 7, 8*q+r) == 0), None)
            require(zero is not None, "rectangle fooling-set cross")
            cross_zeros.append(list(zero))
    return dict(parameters=[6, 53, 25, 7], rectangles=[list(r) for r in expected],
                one_points=[list(p) for p in points], cross_zeros=cross_zeros,
                active_bits=row.ones(), active_switches=row.ones() // 2)


def wide_checks(closed):
    rng = random.Random(637734)
    descriptors = queries = 0
    for h in (7, 31, 65, 127, 511, 4096, 65536):
        for _ in range(40):
            s = rng.randrange(1, (1 << h) + 1)
            a, j = rng.randrange(s), rng.randrange(2*h-1)
            row = describe(h, s, a, j)
            inspect_row(row)
            if j <= h - 1:
                require(len(row.rectangles) <= 1, "wide first or center cap")
            addresses = {0, (1 << h) - 1, rng.getrandbits(h)}
            for t0, t1, y0, y1 in row.rectangles:
                for t in {max(0, t0 - 1), t0, t1 - 1, min((1 << row.depth)-1, t1)}:
                    for y in {max(0, y0-1), y0, y1-1,
                              min((1 << (h-row.depth))-1, y1)}:
                        addresses.add((y << row.depth) + t)
            for x in addresses:
                require(row.bit(x) == closed.switch_bit(h, s, a, j, x), "wide boundary query")
                queries += 1
            descriptors += 1
    return dict(wide_descriptors=descriptors, wide_queries=queries, maximum_height=MAX_HEIGHT)


def counter_controls():
    checks = 0
    for value in range(513):
        stats = dict(template_bits=0, counter_bits_copied=0, counter_bit_visits=0)
        counter = Countdown(binary_template(value, stats), stats)
        for remaining in range(value, 0, -1):
            require(counter.take(), "counter stopped early")
            represented = sum(bit << i for i, bit in enumerate(counter.bits))
            require(represented == remaining - 1, "counter value")
            require(not counter.bits or counter.bits[-1] == 1, "counter canonical end")
            checks += 1
        require(not counter.take(), "counter did not stop")
        require(stats["counter_bit_visits"] == 2*value - value.bit_count(), "exact counter work")
    row = describe(6, 53, 25, 7)
    correct = [row.bit(x) for x in range(64)]
    reversed_coordinates = [row.bit(((x % 8) << 3) + x // 8) for x in range(64)]
    require(correct != reversed_coordinates, "stream coordinate mutation")
    return dict(counter_decrements=checks, counter_starts=513,
                stream_order_mutant_rejected=True)


def domain_controls():
    invalid = [(0, 1, 0, 0), (MAX_HEIGHT + 1, 1, 0, 0), (2, 0, 0, 0),
               (2, 5, 0, 0), (2, 3, -1, 0), (2, 3, 3, 0),
               (2, 3, 0, -1), (2, 3, 0, 3), (True, 1, 0, 0), (2, 3.0, 0, 0)]
    for case in invalid:
        try:
            describe(*case)
        except ValueError:
            continue
        raise ValueError("invalid descriptor accepted")
    row = describe(2, 3, 1, 1)
    for x in (-1, 4, True, 0.0):
        try:
            row.bit(x)
        except ValueError:
            continue
        raise ValueError("invalid address accepted")
    return len(invalid) + 4


def calculate():
    canonical, closed = load_sources()
    result = census(canonical, closed)
    result.update(wide_checks(closed))
    result.update(counter_controls())
    result["sharpness"] = sharpness(closed)
    result["domain_rejections"] = domain_controls()
    result["scope"] = "Three rectangles per canonical row and optimal output bit work; no physical row producer or kappa"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = calculate()
    if args.write_result:
        (PACKAGE / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(result == json.loads((PACKAGE / "RESULT.json").read_text()), "result mismatch")
    print("PASS_ROTATION_ROW_RECTANGLES sharp three-rectangle row and output-linear stream")


if __name__ == "__main__":
    main()

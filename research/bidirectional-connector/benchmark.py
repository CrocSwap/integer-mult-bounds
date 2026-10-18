#!/usr/bin/env python3
"""Matched RAM benchmark: arbitrary dense B maps, identity A, dirty work restored.

This measures these batch programs, not integer multiplication or tape hosting.
No persistent map-image cache. Apache-2.0; conorholds with Codex assistance.
"""
import argparse
import json
from pathlib import Path
import random
from statistics import median
from time import perf_counter

import families


def run_inplace(word, data, maps, n, roots):
    root_base = n + (1 << n) - 1
    private = root_base + roots
    scratch = data[private]
    incoming_scratch = scratch
    for op in word:
        if op[0] == "A":
            data[n + op[1] - 1] ^= data[root_base + op[2]]
        elif op[0] == "C":
            data[root_base + op[1]] ^= data[root_base + 1 - op[1]]
        elif op[0] == "B":
            j, port = op[1:]
            source = data[j]
            value = data[root_base + port]
            for coordinate, coefficients in enumerate(maps[j]):
                # A dirty scalar echo. Both coefficient/source traversals are executed.
                value ^= scratch << coordinate
                scratch ^= (coefficients & source).bit_count() & 1
                value ^= scratch << coordinate
                scratch ^= (coefficients & source).bit_count() & 1
            data[root_base + port] = value
        else:
            raise ValueError("unknown RAM instruction")
    if scratch != incoming_scratch:
        raise ValueError("private scalar was not restored")
    data[private] = scratch


def incoming_data(n, width, roots, rng):
    return [rng.getrandbits(width) for _ in range(n + (1 << n) - 1 + roots)] + [rng.randrange(2)]


def expected(data, maps, n, roots):
    out = list(data)
    images = [sum(((row & data[j]).bit_count() & 1) << i for i, row in enumerate(matrix))
              for j, matrix in enumerate(maps)]
    # This direct evaluator is outside timing; neither benchmark caches these images.
    sums = [0] * (1 << n)
    for mask in range(1, 1 << n):
        bit = mask & -mask
        sums[mask] = sums[mask ^ bit] ^ images[bit.bit_length() - 1]
        out[n + mask - 1] ^= sums[mask]
    return out


def measure_frontier(n, width, rounds=9):
    """Screen every count-Pareto reference, then compare the best three afresh."""
    if not (3 <= n <= 18 and 1 <= width <= 4096 and rounds >= 3):
        raise ValueError("n=3..18, width=1..4096 and rounds>=3 required")
    rng = random.Random(20261014 + n * 1009 + width)
    maps = [[rng.getrandbits(width) for _ in range(width)] for _ in range(n)]
    data2 = incoming_data(n, width, 2, rng)
    data1 = data2[:-2] + [data2[-1]]
    sizes = families.balanced_three(n)
    candidate = families.construct_palette(sizes)
    candidate_want = expected(data2, maps, n, 2)
    check = list(data2); run_inplace(candidate, check, maps, n, 2)
    if check != candidate_want:
        raise ValueError("palette benchmark endpoint")
    screen = []
    for partition in families.single_frontier(n):
        word = families.construct(partition)
        check = list(data1); run_inplace(word, check, maps, n, 1)
        if check != expected(data1, maps, n, 1):
            raise ValueError("reference benchmark endpoint")
        timings = []
        for _ in range(3):
            start = perf_counter(); values = list(data1); run_inplace(word, values, maps, n, 1)
            timings.append(perf_counter() - start)
        screen.append({"blocks": list(partition), "counts": families.screen(partition),
                       "seconds": timings, "median_seconds": median(timings)})
    finalists = sorted(screen, key=lambda row: row["median_seconds"])[:3]
    results = []
    for finalist in finalists:
        reference = families.construct(finalist["blocks"])
        trials = [[], []]
        for r in range(rounds):
            for index in ((0, 1) if r % 2 == 0 else (1, 0)):
                word, data, roots = (reference, data1, 1) if index == 0 else (candidate, data2, 2)
                start = perf_counter(); values = list(data); run_inplace(word, values, maps, n, roots)
                trials[index].append(perf_counter() - start)
        results.append({"reference_blocks": finalist["blocks"], "reference_seconds": trials[0],
                        "palette_seconds": trials[1], "reference_median": median(trials[0]),
                        "palette_median": median(trials[1]), "speedup": median(trials[0]) / median(trials[1])})
    best = min(results, key=lambda row: row["reference_median"])
    return {"sources": n, "width": width, "rounds": rounds, "candidate_counts": families.palette_screen(sizes),
            "reference_family": "Every count-Pareto one-root Gray-block partition, three screening trials; three fastest references receive fresh alternating comparisons. Not unrestricted synthesis.",
            "reference_screen": screen, "finalists": results, "best_reference": best,
            "speedup": best["speedup"], "fraction_time_saved": 1 - 1 / best["speedup"],
            "timing_scope": "RAM batch with dense B, identity A, no persistent map-image cache, exact dirty scalar restoration. Input copying included; shared coefficient and program preparation excluded. Extra root and Python arithmetic temporaries are explicit; no native tape, supplier or multiplication-runtime claim."}


def run_signed_inplace(word, data, maps, n, roots):
    """Integer RAM child with two coefficient traversals and arbitrary dirty work."""
    base = n + (1 << n) - 1
    scratch = data[-1]
    old_scratch = scratch
    for op in word:
        sign = op[-1]
        if op[0] == "B":
            source = data[op[1]]
            target = data[base + op[2]]
            for coordinate, row in enumerate(maps[op[1]]):
                target[coordinate] -= sign * scratch
                for coefficient, value in zip(row, source):
                    scratch += coefficient * value
                target[coordinate] += sign * scratch
                for coefficient, value in zip(row, source):
                    scratch -= coefficient * value
        else:
            if op[0] == "A":
                source = data[base + op[2]]
                target = data[n + op[1] - 1]
            elif op[0] == "C":
                source = data[base + 1 - op[1]]
                target = data[base + op[1]]
            else:
                raise ValueError("unknown signed RAM instruction")
            for coordinate, value in enumerate(source):
                target[coordinate] += sign * value
    if scratch != old_scratch:
        raise ValueError("signed private work was not restored")
    data[-1] = scratch


def expected_signed(data, maps, n):
    out = [list(row) for row in data[:-1]] + [data[-1]]
    images = [[sum(coefficient * value for coefficient, value in zip(row, data[j]))
               for row in matrix] for j, matrix in enumerate(maps)]
    sums = [[0] * len(data[0]) for _ in range(1 << n)]
    for mask in range(1, 1 << n):
        bit = mask & -mask
        sums[mask] = [a+b for a,b in zip(sums[mask ^ bit], images[bit.bit_length()-1])]
        out[n+mask-1] = [a+b for a,b in zip(out[n+mask-1], sums[mask])]
    return out


def measure_signed_frontier(n, width, rounds=9):
    if not (3 <= n <= 15 and 1 <= width <= 128 and rounds >= 3):
        raise ValueError("signed benchmark requires n=3..15, width=1..128, rounds>=3")
    rng = random.Random(20261014 + n*1009 + width)
    maps = [[[rng.randrange(-2,3) for _ in range(width)] for _ in range(width)] for _ in range(n)]
    data2 = [[rng.randrange(-3,4) for _ in range(width)] for _ in range(n+(1<<n)-1+2)] + [7]
    data1 = data2[:-2] + [data2[-1]]
    def copied(data):
        return [list(row) for row in data[:-1]] + [data[-1]]
    def checked(word, data, roots):
        values = copied(data)
        run_signed_inplace(word, values, maps, n, roots)
        if values != expected_signed(data, maps, n):
            raise ValueError("signed RAM endpoint")
        inverse = [op[:-1]+[-op[-1]] for op in reversed(word)]
        run_signed_inplace(inverse, values, maps, n, roots)
        if values != data:
            raise ValueError("signed RAM inverse")
    candidate = families.construct_signed_palette(families.balanced_three(n))
    checked(candidate, data2, 2)
    screen = []
    for sizes in families.signed_single_frontier(n):
        word = families.construct_signed_single(sizes)
        checked(word, data1, 1)
        timings = []
        for _ in range(3):
            start = perf_counter()
            values = copied(data1)
            run_signed_inplace(word, values, maps, n, 1)
            timings.append(perf_counter()-start)
        screen.append({"blocks":list(sizes), "counts":families.signed_single_screen(sizes),
                       "seconds":timings, "median_seconds":median(timings)})
    finalists = sorted(screen, key=lambda row:row["median_seconds"])[:3]
    results = []
    for finalist in finalists:
        reference = families.construct_signed_single(finalist["blocks"])
        trials = [[],[]]
        for r in range(rounds):
            for index in ((0,1) if r%2 == 0 else (1,0)):
                word, data, roots = (reference,data1,1) if index == 0 else (candidate,data2,2)
                start = perf_counter()
                values = copied(data)
                run_signed_inplace(word, values, maps, n, roots)
                trials[index].append(perf_counter()-start)
        results.append({"reference_blocks":finalist["blocks"], "reference_seconds":trials[0],
                        "palette_seconds":trials[1], "reference_median":median(trials[0]),
                        "palette_median":median(trials[1]), "speedup":median(trials[0])/median(trials[1])})
    best = min(results, key=lambda row:row["reference_median"])
    return {"field":"exact integers", "sources":n, "width":width, "rounds":rounds,
            "candidate_counts":families.signed_palette_screen(families.balanced_three(n)),
            "reference_family":"Every count-Pareto signed one-root Gray-block partition; largest cube first. Three screens, then three finalists with fresh alternating samples. Not unrestricted synthesis.",
            "reference_screen":screen, "finalists":results, "best_reference":best,
            "speedup":best["speedup"], "fraction_time_saved":1-1/best["speedup"],
            "timing_scope":"Integer RAM, dense B and identity A, full dirty-integer scratch restoration, both coefficient traversals executed, no map-image cache. Deep input copies included; shared input/matrix/program preparation excluded. Python temporaries and extra root admitted; no native tape, floating-complex or multiplication-runtime claim."}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--sources',type=int,default=15)
    p.add_argument('--width',type=int,default=128)
    p.add_argument('--rounds',type=int,default=9)
    p.add_argument('--out',type=Path)
    p.add_argument('--signed',action='store_true')
    args=p.parse_args()
    measure=measure_signed_frontier if args.signed else measure_frontier
    result=measure(args.sources,args.width,args.rounds)
    if args.out:args.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('sources','width','speedup','fraction_time_saved')},indent=2))


if __name__ == "__main__":main()

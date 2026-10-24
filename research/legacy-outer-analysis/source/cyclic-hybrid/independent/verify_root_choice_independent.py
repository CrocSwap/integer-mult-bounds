#!/usr/bin/env python3
"""Check root selection, rational blocks, and exact interval counts."""

from fractions import Fraction
from math import isqrt
from pathlib import Path
import hashlib
import json
import os
import platform
import resource
import time


def prime(q):
    return q >= 2 and all(q % k for k in range(2, isqrt(q)+1))


def convergents(a, q):
    result = [(0, 1)]
    previous_p, p = 1, 0
    previous_d, d = 0, 1
    numerator, denominator = q, a
    while denominator:
        partial, remainder = divmod(numerator, denominator)
        previous_p, p = p, partial*p+previous_p
        previous_d, d = d, partial*d+previous_d
        result.append((p, d))
        numerator, denominator = denominator, remainder
    assert result[-1] == (a, q)
    return result


def interval_bound(points, q):
    count = len(points)
    numerators = [0]
    for i, residue in enumerate(sorted(points)):
        numerators.extend((q*i-count*residue, q*(i+1)-count*residue))
    return Fraction(max(numerators)-min(numerators), q)


def audit(q, use_mirror=False):
    assert q > 2 and prime(q)
    h = (q-1).bit_length()
    b = 16*h
    bad_union = set()
    bad_sum = 0
    for j in range(1, q):
        bound = (q-1)//(b*j)
        bad_count = 2*bound
        assert bad_count*b*j < 2*q
        bad_sum += bad_count
        inverse = pow(j, -1, q)
        for distance in range(1, bound+1):
            bad_union.add(distance*inverse % q)
            bad_union.add(-distance*inverse % q)
    assert len(bad_union) <= bad_sum
    harmonic = sum((Fraction(1, j) for j in range(1, q)), Fraction())
    assert harmonic <= 2*h
    assert Fraction(2*q, b)*harmonic <= Fraction(q, 4) < q-1
    assert 4*bad_sum < q
    a = next(a for a in range(1, q) if a not in bad_union)
    if use_mirror:
        a = q-a
    for j in range(1, q):
        residue = a*j % q
        assert b*j*min(residue, q-residue) >= q
    cf = convergents(a, q)
    assert len(cf) <= 2*h+1
    block_rows = []
    for k, (p, denominator) in enumerate(cf[:-1]):
        nxt = cf[k+1][1]
        assert nxt <= b*denominator
        assert abs(a*denominator-p*q)*nxt <= q
        assert abs(a*denominator-p*q)*denominator <= q
        discrepancy = interval_bound([a*s % q for s in range(1, denominator+1)], q)
        assert discrepancy <= 10
        block_rows.append({"p": p, "denominator": denominator,
                           "next_denominator": nxt, "interval_discrepancy": str(discrepancy)})
    denominators = sorted({d for _, d in cf[:-1]}, reverse=True)
    largest_blocks = 0
    for length in range(q):
        remaining = length
        blocks = 0
        for denominator in denominators:
            count, remaining = divmod(remaining, denominator)
            assert count <= b
            blocks += count
        assert remaining == 0
        assert blocks <= b*(2*h+1)
        assert 10*blocks <= 480*h*h
        largest_blocks = max(largest_blocks, blocks)
    return {"q": q, "a": a, "h": h, "B": b,
            "bad_sum": bad_sum, "bad_union": len(bad_union),
            "convergents": cf, "block_checks": block_rows,
            "all_prefixes_checked": q, "largest_greedy_block_count": largest_blocks,
            "duplicate_initial_denominator": cf[0][1] == cf[1][1],
            "canonical_a1_admitted": q <= b}


def main():
    directory = Path(__file__).resolve().parent
    usage = os.statvfs(directory)
    assert usage.f_bavail*usage.f_frsize >= 3*1024**3
    resource.setrlimit(resource.RLIMIT_CPU, (60, 60))
    started = time.perf_counter()
    rows = [audit(q, use_mirror) for q in (3, 5, 7, 11, 17, 31, 67, 127, 263, 523, 1021, 2053)
            for use_mirror in (False, True)]
    assert any(row["a"] > 1 and not row["canonical_a1_admitted"] for row in rows)
    assert any(row["duplicate_initial_denominator"] for row in rows)
    raw_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    rss = raw_rss if platform.system() == "Darwin" else raw_rss*1024
    assert rss < 512*1024**2
    result = {
        "status": "pass", "scope": "Exact root selection and rational-block checks; no numerical target or tape compiler",
        "prime_cases": rows, "prefixes_checked": sum(row["all_prefixes_checked"] for row in rows),
        "block_checks": sum(len(row["block_checks"]) for row in rows),
        "elapsed_seconds": time.perf_counter()-started, "peak_rss_bytes": rss,
        "free_after_bytes": os.statvfs(directory).f_bavail*os.statvfs(directory).f_frsize,
        "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    }
    (directory/'root-choice-independent-receipt.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({key: result[key] for key in (
        "status", "prefixes_checked", "block_checks", "elapsed_seconds", "peak_rss_bytes")}, indent=2))


if __name__ == '__main__':
    main()

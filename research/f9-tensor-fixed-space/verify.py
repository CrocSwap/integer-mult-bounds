#!/usr/bin/env python3
"""Exact signed-orbit and tensor fixed-space certificate. Apache-2.0."""

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
SIZE = 512
EXPECTED_CYCLES = {(1, 0): 16, (2, 0): 8, (5, 0): 48, (10, 0): 24}
EXPECTED_TRACES = [512, 16, 32, 16, 32, 256, 32, 16, 32, 16]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def checked_bytes(path, sha256, blob):
    require(path.stat().st_size <= 131072, "source exceeds byte budget")
    data = path.read_bytes()
    require(hashlib.sha256(data).hexdigest() == sha256, "source SHA256")
    header = b"blob " + str(len(data)).encode() + b"\0"
    require(hashlib.sha1(header + data).hexdigest() == blob, "source Git blob")
    return data


def load_monomial():
    pins = json.loads((ROOT / "SOURCE-PINS.json").read_text())
    require(pins["source_pr"] == 7447, "wrong predecessor")
    require(pins["head"] == "a60ddc19848b945250a78a1e3daea94e3c96b2f5", "source head")
    require(len(pins["files"]) == 2, "source inventory")
    sources = {}
    for row in pins["files"]:
        require(row["path"] in ("sources/pr7447-RESULT.json", "sources/pr7447-PROOF.md"),
                "unexpected source path")
        sources[row["path"]] = checked_bytes(ROOT / row["path"], row["sha256"], row["git_blob"])
    data = json.loads(sources["sources/pr7447-RESULT.json"])["monomial"]
    require(data["offset"] == data["global_phase"] == 0, "source affine convention")
    rows, quadratic, linear = (data[k] for k in ("matrix_rows", "quadratic_rows", "linear_Z4"))
    require(len(rows) == len(quadratic) == len(linear) == 9, "nine source coordinates")
    require(all(type(x) is int and 0 <= x < SIZE for x in rows + quadratic), "binary rows")
    require(all(type(x) is int and 0 <= x < 4 for x in linear), "Z4 coefficients")
    destinations, phases = [], []
    for x in range(SIZE):
        bits = [(x >> i) & 1 for i in range(9)]
        destinations.append(sum(((row & x).bit_count() % 2) << i for i, row in enumerate(rows)))
        value = sum(a * bit for a, bit in zip(linear, bits, strict=True))
        value += 2 * sum(bits[i] * bits[j] * ((quadratic[i] >> j) & 1)
                         for i in range(9) for j in range(i + 1, 9))
        phases.append(value % 4)
    require(sorted(destinations) == list(range(SIZE)), "source is a permutation")
    return destinations, phases


def signed_cycles(destinations, phases):
    require(len(destinations) == len(phases) == SIZE, "table size")
    seen = bytearray(SIZE)
    cycles, histogram = [], {}
    for start in range(SIZE):
        if seen[start]:
            continue
        orbit, x, phase = [], start, 0
        for _ in range(SIZE):
            if seen[x]:
                break
            seen[x] = 1
            orbit.append(x)
            phase = (phase + phases[x]) % 4
            x = destinations[x]
        require(x == start, "orbit must close at its start")
        key = (len(orbit), phase)
        histogram[key] = histogram.get(key, 0) + 1
        cycles.append((orbit, phase))
    require(sum(map(len, (orbit for orbit, _ in cycles))) == SIZE, "complete orbit partition")
    return cycles, histogram


def check_gauge(cycles, destinations, phases):
    gauge = [0] * SIZE
    for orbit, total in cycles:
        require(total == 0, "nontrivial cycle holonomy")
        exponent = 0
        for x in orbit:
            gauge[x] = exponent
            exponent = (exponent + phases[x]) % 4
    for x in range(SIZE):
        require((gauge[destinations[x]] - gauge[x]) % 4 == phases[x], "diagonal gauge equation")
    return hashlib.sha256(bytes(gauge)).hexdigest()


def direct_traces(destinations, phases):
    traces = []
    for power in range(10):
        counts = [0, 0, 0, 0]
        for start in range(SIZE):
            x, exponent = start, 0
            for _ in range(power):
                exponent = (exponent + phases[x]) % 4
                x = destinations[x]
            if x == start:
                counts[exponent] += 1
        require(counts[1] == counts[3], "trace must be real")
        traces.append(counts[0] - counts[2])
    return traces


def fixed_dimension(width):
    require(type(width) is int and 1 <= width <= 64, "reference width budget")
    numerator = SIZE**width + 256**width + 4 * 32**width + 4 * 16**width
    require(numerator % 10 == 0, "integer character average")
    return numerator // 10


def check_tensor_characters(cycles):
    multiplicities = [0] * 10
    for orbit, total in cycles:
        require(total == 0 and 10 % len(orbit) == 0, "tenth-root cycle spectrum")
        for k in range(10):
            if (k * len(orbit)) % 10 == 0:
                multiplicities[k] += 1
    require(multiplicities == [96, 24, 72, 24, 72, 32, 72, 24, 72, 24], "one-column spectrum")
    tensor = [1] + [0] * 9
    for width in range(1, 65):
        tensor = [sum(tensor[j] * multiplicities[(k - j) % 10] for j in range(10))
                  for k in range(10)]
        require(sum(tensor) == SIZE**width, "complete tensor spectrum")
        require(tensor[0] == fixed_dimension(width), "tensor character formula")
    return multiplicities


def two_column_fixed_dimension(destinations, phases):
    seen = bytearray(SIZE * SIZE)
    fixed, orbit_count = 0, 0
    for start in range(SIZE * SIZE):
        if seen[start]:
            continue
        x, exponent = start, 0
        for _ in range(10):
            if seen[x]:
                break
            seen[x] = 1
            a, b = divmod(x, SIZE)
            exponent = (exponent + phases[a] + phases[b]) % 4
            x = destinations[a] * SIZE + destinations[b]
        require(x == start, "two-column orbit closure")
        orbit_count += 1
        fixed += exponent == 0
    require(sum(seen) == SIZE * SIZE, "all literal two-column addresses")
    require(fixed == fixed_dimension(2) == 33280, "literal two-column fixed space")
    return orbit_count


def modular_correction_rank(destinations, phases):
    # 16^2 = -1 mod 257. Signed-permutation cycle ranks are preserved here.
    pivots = {}
    for x in range(SIZE):
        vector = {destinations[x]: pow(16, phases[x], 257)}
        vector[x] = (vector.get(x, 0) - 1) % 257
        vector = {key: value for key, value in vector.items() if value}
        for _ in range(SIZE):
            if not vector:
                break
            row = min(vector)
            if row not in pivots:
                scale = pow(vector[row], -1, 257)
                pivots[row] = {key: value * scale % 257 for key, value in vector.items()}
                vector = {}
                break
            scale = vector[row]
            for key, value in pivots[row].items():
                updated = (vector.get(key, 0) - scale * value) % 257
                if updated:
                    vector[key] = updated
                else:
                    vector.pop(key, None)
        require(not vector, "bounded Gaussian elimination exhausted")
    require(len(pivots) == 416 == SIZE - fixed_dimension(1), "literal correction rank")
    return len(pivots)


def check_controls(destinations, phases):
    changed = phases.copy()
    changed[0] = (changed[0] + 1) % 4
    cycles, histogram = signed_cycles(destinations, changed)
    require(histogram != EXPECTED_CYCLES, "single fixed-address phase fault detected")
    try:
        traces = direct_traces(destinations, changed)
    except ValueError:
        pass
    else:
        require(traces != EXPECTED_TRACES, "trace phase fault detected")
    try:
        check_gauge(cycles, destinations, changed)
    except ValueError:
        pass
    else:
        raise ValueError("bad gauge accepted")
    require(16 != fixed_dimension(1), "basis-address count is not fixed-space dimension")
    require(2 * 416 != SIZE**2 - fixed_dimension(2), "tensor rank is not twice local rank")
    for width in (0, -1, 65, True):
        try:
            fixed_dimension(width)
        except ValueError:
            continue
        raise ValueError("width budget accepted")
    return 9


def main():
    require(len(sys.argv) == 1, "no command-line arguments supported")
    destinations, phases = load_monomial()
    cycles, histogram = signed_cycles(destinations, phases)
    require(histogram == EXPECTED_CYCLES, "signed cycle certificate")
    gauge_digest = check_gauge(cycles, destinations, phases)
    require(direct_traces(destinations, phases) == EXPECTED_TRACES, "literal traces")
    spectrum = check_tensor_characters(cycles)
    orbits = two_column_fixed_dimension(destinations, phases)
    rank = modular_correction_rank(destinations, phases)
    controls = check_controls(destinations, phases)
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "SOURCE-PINS.json",
             "VERIFY.json", "verify.py", "sources/pr7447-PROOF.md", "sources/pr7447-RESULT.json")
    hashes = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in names}
    result = {
        "marker": "PASS_F9_TENSOR_FIXED_SPACE", "claim_type": "scoped proof and finite certificate",
        "signed_cycles": [[length, phase, count] for (length, phase), count in sorted(histogram.items())],
        "trace_powers_0_through_9": EXPECTED_TRACES, "tenth_root_multiplicities": spectrum,
        "diagonal_gauge_sha256": gauge_digest, "one_column_correction_rank": rank,
        "literal_two_column_addresses": SIZE**2, "literal_two_column_orbits": orbits,
        "character_widths_checked": 64, "controls": controls,
        "fixed_dimensions_1_through_8": [fixed_dimension(f) for f in range(1, 9)],
        "package_sha256": hashes,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

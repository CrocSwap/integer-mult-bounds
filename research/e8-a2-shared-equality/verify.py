"""Exact cross-fiber A2 equality incidence. Produced by Nick Petalas.

Apache-2.0. Individual-fiber results are premises from PR3288.
"""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

from independent import independent_incidence


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
HYPERBOLIC_COLUMNS = (3, 6, 18, 34, 76, 78, 130, 208)
SIMPLE_EDGES = ((0, 2), (1, 3), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7))
SIMPLE_WITNESS = (3, 11, 27, 31, 39, 47, 59, 63, 71, 79, 83, 87, 103, 111, 123, 127)
SOURCE_MANIFEST_SHA256 = "cbd2e3530c026ff5f5e5303f1f705e70c47d5b2175e76d0f2ffc5cb5d7dfeb08"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def quadratic(x):
    return ((x & (x >> 1) & 0x55).bit_count()) % 2


def source_quadratic(x):
    return (x.bit_count() + sum((x >> i & 1) * (x >> j & 1)
                               for i, j in SIMPLE_EDGES)) % 2


def transform(x):
    result = 0
    for i, column in enumerate(HYPERBOLIC_COLUMNS):
        if x >> i & 1:
            result ^= column
    return result


def basis(values):
    require(len(values) <= 512, "binary inventory bound")
    rows = []
    for value in values:
        require(type(value) is int and 0 <= value < 512, "binary vector domain")
        for row in rows:
            value = min(value, value ^ row)
        if value:
            rows = sorted([min(row, row ^ value) for row in rows] + [value],
                          reverse=True)
    return tuple(rows)


def authenticate():
    raw_sources = (PACKAGE / "SOURCES.json").read_bytes()
    require(sha256(raw_sources).hexdigest() == SOURCE_MANIFEST_SHA256,
            "exact source manifest")
    sources = json.loads(raw_sources)
    require(len(sources["files"]) == 4, "source inventory")
    paths = []
    for row in sources["files"]:
        if row["usage"] == "input":
            path = ROOT / row["path"]
            require(path.is_file() and not path.is_symlink(), "regular source")
            raw = path.read_bytes()
            require(len(raw) <= 100_000, "source byte bound")
            require(sha256(raw).hexdigest() == row["sha256"], "source hash")
            paths.append(row["path"])
    require(sorted(paths) == ["research/e8-a2-analytic-rank6/PROOF.md",
                             "research/p112-root-simplex-exclusion/geometry.py"],
            "exact live inputs")
    require(len({transform(x) for x in range(256)}) == 256, "invertible transport")
    require(all(source_quadratic(transform(x)) == quadratic(x) for x in range(256)),
            "transport to the pinned simple-root polynomial")


def fiber_inventory(q, polar):
    roots = tuple(x for x in range(256) if q[x])
    planes = sorted({tuple(sorted((a, b, a ^ b)))
                     for a, b in combinations(roots, 2) if polar[a][b]})
    fibers = []
    for plane in planes:
        a, b = plane[:2]
        for point in plane:
            roots_in_section = tuple(x for x in roots
                                     if polar[x][a] == polar[point][a]
                                     and polar[x][b] == polar[point][b])
            fiber = tuple(x for x in roots_in_section if x != point)
            fibers.append((plane, point, roots_in_section, fiber))
    require(len(fibers) == 3360, "complete normal-plane inventory")
    return fibers


def primal_incidence(fibers):
    incidence = {}
    for plane, point, section, fiber in fibers:
        rows = basis(tuple(1 | (x << 1) for x in fiber))
        require(len(rows) == 7, "inherited fiber-span contract")
        coordinates = {0: 0}
        for i, row in enumerate(rows):
            coordinates.update({x ^ row: c | (1 << i)
                                for x, c in tuple(coordinates.items())})
        for normal in range(1, 128):
            support = tuple(x for x in section
                            if not (coordinates[1 | (x << 1)] & normal).bit_count() % 2)
            if len(support) == 16 and point not in support:
                mask = sum(1 << x for x in support)
                if mask not in incidence:
                    require(len(basis(tuple(1 | (x << 1) for x in support))) == 6,
                            "root support determines its six-space")
                    incidence[mask] = []
                incidence[mask].append((plane, point))
    return {mask: tuple(sorted(entries)) for mask, entries in incidence.items()}


def missing_point_control(fiber_record):
    _, point, section, fiber = fiber_record
    rows = basis(tuple(1 | (x << 1) for x in fiber))
    coordinates = {0: 0}
    for i, row in enumerate(rows):
        coordinates.update({x ^ row: c | (1 << i)
                            for x, c in tuple(coordinates.items())})
    found = False
    for normal in range(1, 128):
        support = {x for x in section
                   if not (coordinates[1 | (x << 1)] & normal).bit_count() % 2}
        if len(support) == 16 and point in support:
            require(len(support) + len(support.intersection(fiber)) == 31,
                    "balanced section containing the singleton has score 31")
            found = True
            break
    require(found, "genuine missing-point countercontrol")


def summarize(incidence):
    require(Counter(map(len, incidence.values())) == {3: 30240}, "sharp multiplicity")
    degrees, pairs = Counter(), set()
    digest = sha256()
    for mask, entries in sorted(incidence.items()):
        require(len(set(entries)) == 3, "three distinct fibers")
        digest.update((json.dumps([hex(mask), entries], separators=(",", ":"))
                       + "\n").encode())
        for pair in combinations(entries, 2):
            require(pair not in pairs, "two fibers share at most one equality space")
            pairs.add(pair)
            degrees.update(pair)
    require(len(pairs) == 90720 and Counter(degrees.values()) == {54: 3360},
            "complete compatibility graph")
    witness = min(tuple(x for x in range(256) if mask >> x & 1) for mask in incidence)
    mask = sum(1 << x for x in witness)
    source_labels = sorted(1 | (transform(x) << 1) for x in witness)
    require(tuple(source_labels) == SIMPLE_WITNESS, "literal simple-root witness")
    return {"supports": len(incidence), "incidences": 3 * len(incidence),
            "fibers_per_support": 3, "neighbors_per_fiber": 54,
            "compatible_unordered_fiber_pairs": len(pairs),
            "incidence_sha256": digest.hexdigest(),
            "simple_root_witness": source_labels,
            "canonical_witness_fibers": incidence[mask]}


def controls(incidence, q, polar):
    mask = next(iter(incidence))
    plane, point = incidence[mask][0]
    support = tuple(x for x in range(256) if mask >> x & 1)
    require(point not in support and all(q[x] for x in support), "valid witness")
    require(all(q[x] and q[y] and q[x ^ y] and polar[x][y]
                for x, y in combinations(plane, 2)), "anisotropic normal plane")
    for invalid in ((True,), (-1,), (512,), tuple(range(513))):
        rejected = False
        try:
            basis(invalid)
        except ValueError:
            rejected = True
        require(rejected, "invalid binary input rejected")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    authenticate()
    q = tuple(quadratic(x) for x in range(256))
    polar = tuple(tuple(q[x ^ y] ^ q[x] ^ q[y] for y in range(256))
                  for x in range(256))
    fibers = fiber_inventory(q, polar)
    incidence = primal_incidence(fibers)
    independent, dual_checks = independent_incidence()
    require(incidence == independent, "complete primal/dual incidence agreement")
    controls(incidence, q, polar)
    missing_point_control(fibers[0])
    result = summarize(incidence)
    result["dual_checks"] = dual_checks
    result["status"] = "PASS_A2_SHARED_EQUALITY"
    if args.receipt is not None:
        require(not args.receipt.resolve().is_relative_to(ROOT.resolve()),
                "receipt destination must be outside the checkout")
        files = sorted(p for p in PACKAGE.iterdir() if p.is_file())
        require(len(files) <= 12, "package receipt inventory bound")
        hashes = {p.name: sha256(p.read_bytes()).hexdigest() for p in files}
        receipt = {"result": result, "package_sha256": hashes,
                   "input_sha256": {r["path"]: r["sha256"] for r in
                                    json.loads((PACKAGE / "SOURCES.json").read_text())["files"]
                                    if r["usage"] == "input"}}
        args.receipt.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 thakrarsagar. Developed with OpenAI Codex assistance.
"""Independent dense-rank, rational-elimination and cost-layered certificate.

No primary or predecessor executable is imported. The written rank/trace
argument reduces arbitrary finite factorizations to the support tests checked
here; this script is not a formal-kernel proof of that reduction.
"""

from fractions import Fraction
import gzip
import hashlib
import io
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUTS = {
    "research/c5-dyadic-decoder-gate/inputs/DATA-PHASES.json.gz",
    "research/c5-dyadic-decoder-gate/inputs/MATCHING.json",
}
CORE = (13, 23, 35, 16, 34)
PAIRS = ((0, 2), (0, 3), (1, 3), (1, 4))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def sources():
    records = json.loads((HERE / "SOURCES.json").read_text())["files"]
    records = [row for row in records if row["usage"] == "input"]
    need(len(records) == 2 and {row["path"] for row in records} == INPUTS,
         "exact two-source inventory")
    payloads = {}
    for row in records:
        path = ROOT / row["path"]
        need(path.is_file() and not path.is_symlink()
             and path.resolve().is_relative_to(ROOT) and path.stat().st_size <= 8_000_000,
             "bounded regular scientific source")
        raw = path.read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row["sha256"], "source SHA256")
        blob = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
        need(blob == row["git_blob"], "source Git blob")
        if path.suffix == ".gz":
            with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
                raw = stream.read(8_000_001)
            need(len(raw) <= 8_000_000, "bounded decompressed source")
            need(hashlib.sha256(raw).hexdigest()
                 == "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
                 "selected phase payload")
        payloads[path.name] = raw
    matching = json.loads(payloads["MATCHING.json"])["matching"]
    recipes = json.loads(payloads["DATA-PHASES.json.gz"])["recipes"]
    labels = {row["port"]: row["q"] for row in recipes}
    need(len(recipes) == len(labels) == 112 and sorted(labels) == list(range(112)),
         "complete source labels")
    need(len(matching) == 56 and sorted(x for pair in matching for x in pair) == list(range(112)),
         "paired-port partition")
    planes = [[labels[port] for port in matching[group]] for group in CORE]
    need(planes == [[289, 49], [194, 134], [304, 56], [50, 193], [200, 196]],
         "named physical C5")
    return planes


def dot(x, y):
    return sum(((x >> bit) & 1) * ((y >> bit) & 1) for bit in range(9)) % 2


def dense_rank(matrix):
    rows = [row[:] for row in matrix]
    rank = 0
    for column in range(len(rows[0]) if rows else 0):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(rank + 1, len(rows)):
            if rows[i][column]:
                rows[i] = [x ^ y for x, y in zip(rows[i], rows[rank])]
        rank += 1
    return rank


def support_records(planes):
    for i, plane in enumerate(planes):
        need([[dot(x, y) for y in plane] for x in plane] == [[1, 0], [0, 1]],
             "complete plane is nondegenerate")
        for j, other in enumerate(planes):
            orthogonal = not any(dot(x, y) for x in plane for y in other)
            need(orthogonal == ((i - j) % 5 in (1, 4)), "exact induced C5 mask")
    records = []
    for left in range(32):
        a = [x for i in range(5) if (left >> i) & 1 for x in planes[i]]
        for right in range(32):
            b = [x for i in range(5) if (right >> i) & 1 for x in planes[i]]
            cost = dense_rank([[dot(x, y) for y in b] for x in a])
            hit = lambda mask: int(bool(left & mask) and bool(right & mask))
            counts = [hit((1 << i) | (1 << j)) for i, j in PAIRS]
            counts += [hit(4), hit(16)]
            defect = 2 * cost - 2 * sum(counts[:4]) - sum(counts[4:])
            need(defect >= 0, "weighted support inequality")
            profile = tuple(counts + [defect, hit(20)])
            records.append((left, right, cost, profile))
    return records


def trace_consistent(left, right, profile, target):
    """Solve necessary trace equations over Q, with no sign restrictions."""
    equations = []
    for i in range(5):
        if not ((left & right) >> i) & 1:
            row = [Fraction(0)] * 6
            row[i] = Fraction(1)
            equations.append(row)
    for j, (a, b) in enumerate(PAIRS):
        if target[j] == 4:
            row = [Fraction(0)] * 6
            row[a] = row[b] = Fraction(1)
            row[5] = Fraction(profile[j])
            equations.append(row)
    for j, i in enumerate((2, 4), 4):
        if target[j] == 2:
            row = [Fraction(0)] * 6
            row[i], row[5] = Fraction(1), Fraction(profile[j])
            equations.append(row)
    rank = 0
    for column in range(5):
        pivot = next((i for i in range(rank, len(equations))
                      if equations[i][column]), None)
        if pivot is None:
            continue
        equations[rank], equations[pivot] = equations[pivot], equations[rank]
        divisor = equations[rank][column]
        equations[rank] = [x / divisor for x in equations[rank]]
        for i in range(rank + 1, len(equations)):
            multiplier = equations[i][column]
            if multiplier:
                equations[i] = [x - multiplier * y
                                for x, y in zip(equations[i], equations[rank])]
        rank += 1
    return not any(not any(row[:5]) and row[5] for row in equations)


def reachable_by_cost(records, target, limit=19, expected=False):
    profiles = sorted({(cost, profile) for left, right, cost, profile in records
                       if cost > 0 and profile[6] <= target[6]
                       and trace_consistent(left, right, profile, target)})
    layers = [set() for _ in range(limit + 1)]
    layers[0].add((0,) * 8)
    for paid in range(limit + 1):
        for state in layers[paid]:
            for cost, increment in profiles:
                if paid + cost > limit:
                    continue
                new = tuple(state[j] + increment[j] for j in range(7))
                new += (min(4, state[7] + increment[7]),)
                if all(new[j] <= target[j] for j in range(7)):
                    layers[paid + cost].add(new)
    reachable = tuple(target) + (4,) in layers[limit]
    need(reachable == expected, "support reachability at cost " + str(limit))
    return {"target": list(target), "profiles": len(profiles),
            "states": sum(map(len, layers)), "reachable": reachable}


def baseline(planes, records):
    rows = []
    for i in range(5):
        for edge in ((i - 1) % 5, i):
            rows.append([int(j == edge) for j in range(5)])
    for i in range(10):
        for j in range(10):
            if any(dot(a, b) for a in planes[i // 2] for b in planes[j // 2]):
                need(sum(x * y for x, y in zip(rows[i], rows[j])) == int(i == j),
                     "unit edge-column strict fit")
    bill = 0
    witness = []
    for edge in range(5):
        mask = sum(1 << i for i in range(5) if rows[2 * i][edge] or rows[2 * i + 1][edge])
        record = records[32 * mask + mask]
        bill += record[2]
        witness.append(record)
    need(bill == 20, "positive cost-20 witness")
    target = tuple(sum(record[3][j] for record in witness) for j in range(7))
    return {"term_count": 5, "cost": bill,
            "reachability": reachable_by_cost(witness, target, limit=20, expected=True)}


def generate():
    planes = sources()
    records = support_records(planes)
    tariffs = [cost for _, _, cost, _ in records]
    zero = [record for record in records if record[2] == 0]
    # These include nonzero free-cross terms, not only empty supports.
    need(all(record[3] == (0,) * 8 for record in zero), "zero-price terms are count self-loops")
    tight = [record for record in records if record[3][6] == 0]
    target18 = (4, 4, 4, 4, 2, 2, 0)
    feasible18 = [record for record in tight
                  if trace_consistent(record[0], record[1], record[3], target18)]
    need(all(record[3][7] == record[3][4] == record[3][5] for record in feasible18),
         "cost-18 missing-block hit equals both singleton hits")
    missing = [[left, right] for left, right, cost, profile in feasible18
               if cost > 0 and profile[7]]
    cases = [(4, 4, 4, 4, 2, 2, 2)]
    for i in range(4):
        target = [4, 4, 4, 4, 2, 2, 0]
        target[i] += 1
        cases.append(tuple(target))
    cases += [(4, 4, 4, 4, 2 + x, 2 + y, 2 - x - y)
              for x, y in ((1, 0), (0, 1), (2, 0), (0, 2), (1, 1))]
    # Independently enumerate the whole nonnegative slack equation of budget two.
    expected = set()
    for x0 in range(2):
        for x1 in range(2):
            for x2 in range(2):
                for x3 in range(2):
                    for y2 in range(3):
                        for y4 in range(3):
                            debt = 2 - 2 * (x0 + x1 + x2 + x3) - y2 - y4
                            if debt >= 0:
                                expected.add((4 + x0, 4 + x1, 4 + x2, 4 + x3,
                                              2 + y2, 2 + y4, debt))
    need(len(cases) == 10 and set(cases) == expected, "complete cost-19 budget cases")
    return {
        "support_certificate": {
            "ordered_pairs": len(records), "zero_tariff_pairs": len(zero),
            "nonempty_zero_tariff_pairs": sum(bool(a) and bool(b) for a, b, _, _ in zero),
            "tariff_sha256": digest(tariffs), "weighted_lower_bound": 18,
            "tight_pairs": len(tight), "tight_positive_pairs": sum(r[2] > 0 for r in tight),
        },
        "cost18": {"trace_compatible_pairs": len(feasible18),
                   "positive_trace_compatible_pairs": sum(r[2] > 0 for r in feasible18),
                   "missing_pair_positive_supports": missing, "excluded": True},
        "cost19_cases": [reachable_by_cost(records, target) for target in cases],
        "baseline": baseline(planes, records),
    }


def main():
    observed = generate()
    retained = json.loads((HERE / "RESULT.json").read_text())
    for key, value in observed.items():
        need(retained[key] == value, "independent receipt section: " + key)
    print("PASS_INDEPENDENT_C5_ASYMMETRIC_COST_FLOOR "
          f"support_pairs=1024 cost19_states={sum(r['states'] for r in observed['cost19_cases'])} minimum=20")


if __name__ == "__main__":
    main()

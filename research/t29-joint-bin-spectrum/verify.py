"""Exact T29 joint-bin constructions. Produced by Nick Petalas. Apache-2.0."""

import hashlib
import json
from collections import Counter
from pathlib import Path


QUOTAS = {8: 19488, 16: 12992, 32: 12992, 48: 12992}
DEMAND = {4: 20880, 5: 8352, 7: 14094, 8: 31842, 9: 56376}
PROFILE = {0: 49770, 1: 4, 2: 1, 48: 8689}
PRICES = {4: -1, 5: -20, 7: -8, 8: -2, 9: 4}
BONUS = {8: 2, 16: 4, 32: 8, 48: -13}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def starting_rows(x):
    """The cited affine family in woklerx PR1844, displayed in its README."""
    require(type(x) is int and 4824 <= x <= 12992, "x domain")
    t, e = divmod(x - 4824, 2)
    return [
        (8, (8,), 11202), (8, (4, 4), 8286),
        (16, (7, 9), x), (16, (8, 8), 8168 - 2*t - e),
        (32, (5, 9, 9, 9), 8352), (32, (4, 9, 9, 9), 4),
        (32, (4, 8, 9, 9), 1),
        (32, (7, 7, 9, 9), 4635 - t - e),
        (32, (7, 8, 8, 9), e), (32, (8, 8, 8, 8), t),
        (48, (), 8689), (48, (4, 8, 9, 9, 9, 9), 4303),
    ]


def replace_eights(widths, number):
    require(0 <= number <= widths.count(8), "replacement capacity")
    result = list(widths)
    for _ in range(number):  # At most four eights in a starting pattern.
        result.remove(8)
        result.extend((4, 4))
    return tuple(sorted(result))


def witness(x, y):
    require(type(y) is int and 0 <= y <= 8286, "y domain")
    rows = starting_rows(x)
    remaining = 8286 - y
    out = Counter({(8, (8,)): 19488 - y, (8, (4, 4)): y})
    for cap, widths, count in rows:  # Exactly twelve starting groups.
        if cap == 8:
            continue
        slots = widths.count(8)
        spent = min(remaining, count * slots)
        remaining -= spent
        full, partial = divmod(spent, slots) if slots else (0, 0)
        if full:
            out[cap, replace_eights(widths, slots)] += full
        if partial:
            out[cap, replace_eights(widths, partial)] += 1
        out[cap, widths] += count - full - bool(partial)
    require(remaining == 0, "conversion pool exhausted")
    return {key: count for key, count in out.items() if count}


def invoice(entries, x, y):
    require(len(entries) <= 36, "pattern capacity")
    caps, widths, remainders = Counter(), Counter(), Counter()
    score = 0
    for (cap, ws), count in entries.items():
        require(cap in QUOTAS and type(count) is int and count > 0,
                "pattern tag or count")
        require(len(ws) <= 12 and all(w in DEMAND for w in ws), "width domain")
        require(sum(ws) <= cap, "bin overflow")
        caps[cap] += count
        remainders[cap - sum(ws)] += count
        score += count * (BONUS[cap] + sum(PRICES[w] for w in ws))
        for w in ws:
            widths[w] += count
    require(dict(caps) == QUOTAS, "capacity invoice")
    require(dict(widths) == DEMAND, "helper invoice")
    require(dict(remainders) == PROFILE, "remainder invoice")
    require(score == -112868, "price invoice")
    require(entries.get((16, (7, 9)), 0) == x, "x projection")
    require(entries.get((8, (4, 4)), 0) == y, "y projection")


def check_exchange_types():
    """Check the new local move on every shape used by the construction."""
    shapes = {(cap, ws) for x in (4824, 4825, 12992)
              for cap, ws, _ in starting_rows(x) if cap != 8 and 8 in ws}
    checks = 0
    for cap, ws in sorted(shapes):  # Five shapes, each with at most four eights.
        for k in range(ws.count(8) + 1):
            changed = replace_eights(ws, k)
            require(sum(changed) == sum(ws), "local remainder invariance")
            require(sum(PRICES[w] for w in changed) == sum(PRICES[w] for w in ws),
                    "local price invariance")
            before = Counter(ws) + Counter({4: 2*k})
            after = Counter(changed) + Counter({8: k})
            require(before == after, "paired helper invariance")
            require(sum(changed) <= cap, "local legality")
            checks += 1
    return checks


def rejection_checks():
    controls = 0
    for x, y in ((4823, 0), (12993, 0), (4824, -1), (4824, 8287),
                 (True, 0), (4824, True), (4824.0, 0), (4824, 0.0)):
        try:
            witness(x, y)
        except ValueError:
            controls += 1
        else:
            raise ValueError("invalid projection accepted")
    for variant in range(3):
        bad = witness(4825, 0)
        if variant == 0:  # A missing compensation violates the helper invoice.
            key = next(key for key in bad if key[0] == 16 and 4 in key[1])
            cap, ws = key
            bad[key] -= 1
            changed = list(ws)
            changed.remove(4)
            changed.remove(4)
            changed.append(8)
            bad[cap, tuple(sorted(changed))] = 1
        elif variant == 1:
            bad[8, (8,)] += 1
        else:  # The invoice holds, but the claimed projection is false.
            bad = witness(4825, 1)
        bad = {key: n for key, n in bad.items() if n}
        try:
            invoice(bad, 4825, 0)
        except ValueError:
            controls += 1
        else:
            raise ValueError("corrupted construction accepted")
    return controls


def run():
    digest = hashlib.sha256()
    constructions = 0
    pool_checks = 0
    for x in range(4824, 12993):
        pool = sum(n * ws.count(8) for cap, ws, n in starting_rows(x) if cap != 8)
        require(pool == 20640 and pool >= 8286, "uniform conversion pool")
        pool_checks += 1
        ys = (range(8287) if x in (4824, 4825, 12991, 12992)
              else (0, 1, 3982, 3983, 8285, 8286))
        for y in ys:
            entries = witness(x, y)
            invoice(entries, x, y)
            encoded = [[cap, list(ws), n] for (cap, ws), n in sorted(entries.items())]
            digest.update(json.dumps([x, y, encoded], separators=(",", ":")).encode())
            constructions += 1
    require(2*8286 + 4 + 1 + 4303 == DEMAND[4], "sharp four budget")
    return {
        "status": "PASS_T29_JOINT_BIN_SPECTRUM",
        "x_range": [4824, 12992], "y_range": [0, 8286],
        "pool_checks": pool_checks, "joint_constructions": constructions,
        "local_exchange_checks": check_exchange_types(),
        "rejection_controls": rejection_checks(),
        "constructions_sha256": digest.hexdigest(), "new_kappa": False,
    }


if __name__ == "__main__":
    result = run()
    here = Path(__file__).resolve().parent
    result["source_sha256"] = {
        name: hashlib.sha256((here / name).read_bytes()).hexdigest()
        for name in ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    }
    print(json.dumps(result, sort_keys=True))

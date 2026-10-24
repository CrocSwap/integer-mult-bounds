#!/usr/bin/env python3
"""Exact complete-packet checks, not a native or owner-fill replay.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
from itertools import product
import json
from pathlib import Path
import re

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE = ROOT / "research/staged544-mixed-fourth-entry"
EXPECTED = {1: 8060060, 2: 2310120, 3: 751813, 4: 327210,
            5: 66425, 8: 25920, 48: 138492}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as stream:
        return json.load(stream)


def reject(name, action):
    try:
        action()
    except ValueError:
        return name
    raise ValueError("mutation accepted: " + name)


def bind_inventory():
    for row in read(PACKAGE / "SOURCES.json")["files"]:
        if row["usage"] == "input":
            raw = (ROOT / row["path"]).read_bytes()
            require(hashlib.sha256(raw).hexdigest() == row["sha256"],
                    "source bytes: " + row["path"])
    order = read(SOURCE / "owner/ORDER.json")
    dispatch = read(SOURCE / "owner/MIXED-DISPATCH.json")
    require(len(order) == len(dispatch) == 3240, "call count")
    require({tuple(call) for call in order} == set(product(range(9), range(360))),
            "complete ordered calls")
    clock = {tuple(call): tick for tick, call in enumerate(order)}
    require({tuple(call[:2]) for call in dispatch} == set(clock), "literal dispatch coverage")
    counts = Counter()
    local = {}
    for kind, evidence in (("THREE", "THREE-LOCAL"), ("FOUR", "NATIVE-LOCAL")):
        for tag in ("base", "extra"):
            report = read(SOURCE / f"inputs/{kind}-{tag}.json.gz")["report"]
            profile = {int(r): n for r, n in report["local_profile"].items()}
            require(all(type(n) is int and n > 0 for n in profile.values()), "local counts")
            receipt = read(SOURCE / f"evidence/{evidence}-{tag}.json")
            for orientation in ("forward", "backward"):
                require({int(r): n for r, n in receipt[orientation]["paid_profile"].items()} == profile,
                        "scalar emitted local invoice")
            require(local.setdefault(kind, profile) == profile, "orientation invoice")
    for stage, replica, provider in dispatch:
        tick = clock[stage, replica]
        fourth = tick * 109 % 324 < 109
        require(provider in {"gauge44", "extra", "gauge44-four", "extra-four"}, "provider")
        require(provider.endswith("-four") == fourth, "actual mixed selector")
        counts["FOUR" if fourth else "THREE"] += 1
    require(counts == {"THREE": 2150, "FOUR": 1090}, "selected provider counts")
    result = read(SOURCE / "RESULT.json")
    idle = {int(r): n for r, n in result["idle"].items()}
    require(idle == {3: 22783, 5: 1625, 48: 138492}, "inherited residual invoice")
    histogram = Counter(idle)
    for kind in counts:
        histogram.update({r: counts[kind] * n for r, n in local[kind].items()})
    require(dict(histogram) == EXPECTED, "all seven paid bins")
    require(EXPECTED == {int(r): n for r, n in result["profile"].items()}, "source total")
    text = (ROOT / "research/unconditional-batched-crt/COMPLEX.md").read_text()
    match = re.search(r"exact paid histogram is\s+\{([0-9:,]+)\}", text)
    require(match is not None, "caller histogram")
    require({int(r): int(n) for r, n in (p.split(":") for p in match[1].split(","))} == EXPECTED,
            "actual COMPLEX caller invoice")
    require(sum(r * n for r, n in histogram.items()) == 65088 * 360, "rank mass")
    return histogram


def volume_law(histogram, extra_cover_division=False, factorwise=False):
    w = 322560
    gamma = 2**1296
    for i in range(1, 37):
        gamma *= 2**(2 * i) - 1
    cases = 0
    for f, remainder, rank in product((1, 2, 3, 73), range(73), histogram):
        e = 73 * f + remainder
        stock = 3 * (w * gamma)**2
        record_bits, spectators = 19, 2**11
        parent = stock * 2**e * spectators * record_bits
        child = (stock // (w * gamma)) * 2**(rank * f) * 2**(e - rank * f)
        child *= spectators * record_bits
        require(child * w * gamma == parent, "complete packet cardinality")
        require((stock // (w * gamma)) % (w * gamma) == 0, "remaining stock")
        jobs = gamma * histogram[rank] * (f if factorwise else 1)
        billed_child = Fraction(child, gamma if extra_cover_division else 1)
        require(jobs * billed_child / parent == Fraction(histogram[rank], w),
                "normalized whole-job invoice")
        cases += 1
    return cases


def affine(x, columns, offset):
    for bit, column in enumerate(columns):
        if x >> bit & 1:
            offset ^= column
    return offset


def address_fixture(rank, drop=None, columns=(3, 2, 4)):
    """Small m=3, f=2, remainder=1 rectangle; no tensor matrix is materialized."""
    chart = [affine(x, columns, 5) for x in range(8)]
    require(len(set(chart)) == 8, "affine chart must be bijective")
    inverse = {y: x for x, y in enumerate(chart)}
    labels = (1, 2, 17)
    rows = set()
    for row in range(12):
        family, rest = divmod(row, 6)
        cover, stock = divmod(rest, 2)
        require((family * 3 + cover) * 2 + stock == row, "row inverse")
        rows.add((family, cover, stock))
    require(rows == set(product(range(2), range(3), range(2))), "row rectangle")
    seen = set()
    for parent_row, address, compact, payload, prefix in product(range(10, 12), range(128), range(2), range(2), range(2)):
        stock = parent_row % 2
        chunks = [chart[(address >> (3 * col)) & 7] for col in range(2)]
        packet = {"stock": stock,
                  "active": tuple(x & ((1 << rank) - 1) for x in chunks),
                  "inactive": tuple(x >> rank for x in chunks),
                  "remainder": address >> 6,
                  "compact": compact, "payload": payload, "prefix": prefix,
                  "return_labels": labels}
        if drop:
            packet.pop(drop)
        require(packet.get("return_labels") == labels, "return labels")
        key = tuple((k, packet[k]) for k in sorted(packet))
        require(key not in seen, "packet collision")
        seen.add(key)
        restored = packet.get("remainder", 0) << 6
        for col in range(2):
            chunk = packet["active"][col] | (packet.get("inactive", (0, 0))[col] << rank)
            restored |= inverse[chunk] << (3 * col)
        require((packet.get("stock", 0), restored, packet.get("compact", 0), packet.get("payload", 0), packet.get("prefix", 0))
                == (stock, address, compact, payload, prefix), "unpack inverse")
        require((labels[0] * 3 + labels[1]) * 2 + packet.get("stock", 0) == parent_row,
                "source row and cover restoration")
    expected = 2 * 2**(rank * 2) * 2**((3 - rank) * 2) * 2 * 2**3
    require(len(seen) == expected == 2048, "complete fixture target cardinality")
    return len(seen)


def missing_residual(histogram):
    bad = dict(histogram)
    bad[48] -= 1
    require(bad == EXPECTED, "one residual occurrence omitted")


def main():
    histogram = bind_inventory()
    cases = volume_law(histogram)
    fixtures = {str(r): address_fixture(r) for r in (1, 2)}
    controls = [reject("double_cover_division", lambda: volume_law(histogram, extra_cover_division=True)),
                reject("factorwise_invoice", lambda: volume_law(histogram, factorwise=True)),
                reject("missing_residual", lambda: missing_residual(histogram)),
                reject("singular_chart", lambda: address_fixture(1, columns=(3, 3, 4)))]
    for field in ("inactive", "remainder", "compact", "payload", "prefix", "stock", "return_labels"):
        controls.append(reject("omit_" + field, lambda field=field: address_fixture(1, drop=field)))
    print(json.dumps({"status": "PASS_COMPLEX_CHILD_PACKET_VOLUME",
                      "scope": "conditional address lemma; inherited scalar/owner claims; no physical adapter acceptance",
                      "profile": dict(sorted(histogram.items())), "volume_cases": cases,
                      "small_address_counts": fixtures, "controls_rejected": controls}, sort_keys=True))


if __name__ == "__main__":
    main()

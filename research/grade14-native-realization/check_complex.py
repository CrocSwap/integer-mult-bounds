"""Verify the complete complex supplier in its positive-child normalization."""

from collections import Counter
from functools import reduce
from hashlib import sha256
from operator import xor
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE / "retained")]
from charts import action, encode, monomial_records, native_catalogue, packed, require
from contacts import contact_receipt
from graph_identity import graph_identity
from closed_caller import placement, templates
from mixed_caller import instructions, layout_bindings
from mixed_grid import exact

DATA = HERE / "retained/data"


def all_images(atlas):
    all_bits = (1 << 512) - 1
    digits = [sum(1 << x for x in range(512) if x >> i & 1) for i in range(9)]
    factors = [m for _, _, r in atlas["pairs"] for m in (r["left"], r["right"])]
    factors.extend(m for _, a, b in atlas["ports"] for m in (a, b))
    unique = {encode(m): m for m in factors}
    maximum = 0
    for m in unique.values():
        ops = monomial_records(m)
        maximum = max(
            maximum,
            sum(
                row[2] if row[0] == "S" else row[1] if row[0] == "I" else 1
                for row in ops
            ),
        )
        wires = digits.copy()
        lo = hi = 0
        for op, *a in ops:
            i = a[0]
            if op == "ROW":
                wires[i] ^= wires[a[1]]
            elif op == "NOT":
                wires[i] ^= all_bits
            elif op == "CZ":
                hi ^= wires[i] & wires[a[1]]
            else:
                term, times = (wires[i], a[1]) if op == "S" else (all_bits, i)
                for _ in range(times):
                    hi ^= lo & term
                    lo ^= term
        want = [
            reduce(xor, (v for j, v in enumerate(digits) if row >> j & 1), 0)
            ^ (all_bits if m["offset"] >> i & 1 else 0)
            for i, row in enumerate(m["matrix_rows"])
        ]
        require(wires == want, "all 512 affine addresses")
        even = all_bits if m["phase"] & 2 else 0
        odd = all_bits if m["phase"] & 1 else 0
        for j, b in enumerate(digits):
            c = m["linear_Z4"][j]
            if c & 1:
                even ^= odd & b
                odd ^= b
            if c & 2:
                even ^= b
            for k in range(j + 1, 9):
                if m["quadratic_rows"][j] >> k & 1:
                    even ^= b & digits[k]
        require((lo, hi) == (odd, even), "all 512 absolute phases")
        require(maximum <= 171, "monomial tariff")
    rec = next(r["right"] for a, b, r in atlas["pairs"] if (a, b) == (0, 249))
    require(
        rec["phase"] == 1 and action(monomial_records(rec), (0,) * 9 + (3,), 2)[1] == 2,
        "two-column absolute phase",
    )
    return dict(
        factor_occurrences=len(factors),
        distinct_factors=len(unique),
        basis_images=512 * len(unique),
        maximum_factor_records=maximum,
    )


def completed_caller(graph, layout):
    source = packed(DATA / "CALLER.json.gz")
    words, roots = templates(source), placement(source)
    bound, offsets, owners = layout_bindings(words, roots, layout, 48)
    targets = Counter()
    paid = Counter()
    for events, diagonal in words.values():
        certificate = exact(events, diagonal, 2025 << 9)
        require(
            exact(events, diagonal, certificate["minimum_grid"]) == certificate,
            "exact signed native caller",
        )
    for root, visits in roots.items():
        colors = [t % 16 for t, _ in visits]
        require(sorted(colors) == list(range(16)), "complete fresh bodies")
        for sign, entries in words[root[0]][1]:
            require(
                sign in (-1, 1) and len(set(entries)) == len(entries),
                "whole root output",
            )
            targets[1 + 8 * len(entries)] += 1
    digest = sha256()
    calls = normalizers = events_count = 0
    for row in instructions(words, roots, bound, offsets):
        digest.update(json.dumps(row, separators=(",", ":")).encode())
        events_count += 1
        op = row[0]
        if op == "QUERY":
            paid[1] += 1
        elif op.startswith("IDLE_"):
            paid[8 * len(row[2]) + int(op == "IDLE_ODD")] += 1
        elif op == "NATIVE":
            calls += 1
        elif op == "LAMBDA":
            normalizers += 1
    mains = (
        set(layout["live"])
        | {i + 112 for i in layout["live"]}
        | set(layout["hosted"]["X2"])
        | set(layout["hosted"]["Y2"])
    )
    dims = list(map(len, graph["frames"]))
    for _, a, b in graph["moves"]:
        paid[abs(dims[a] - dims[b])] += calls
    for i, (a, b) in enumerate(zip(graph["initial"], graph["final"], strict=True)):
        if i not in mains:
            targets[dims[b] - dims[a]] += calls
    price = json.loads((HERE / "retained/grade14-audit.json").read_bytes())
    require(
        digest.hexdigest() == price["signed"]["caller_sha256"],
        "chronological source digest",
    )
    require(
        dict(paid) == {int(k): v for k, v in price["signed"]["paid"].items()}
        and dict(targets)
        == {int(k): v for k, v in price["signed"]["productive"].items()},
        "complete signed price",
    )
    return dict(
        events=events_count,
        calls=calls,
        normalizers=normalizers,
        main_bindings=owners["native_main_bindings"],
        targets=sum(targets.values()),
        paid=sum(paid.values()),
    )


def run():
    graph, layout = [packed(DATA / f) for f in ("complex.json.gz", "layout.json.gz")]
    receipt = json.loads((HERE / "retained/grade14-result.json").read_bytes())
    require(
        sha256(encode(graph)).hexdigest() == receipt["rational_word"],
        "priced rational word",
    )
    atlas = native_catalogue(graph, layout, packed(HERE / "complex-atlas.json.gz"))
    result = dict(
        relative_pairs=len(atlas["pairs"]),
        ports=len(atlas["ports"]),
        atlas_sha256=sha256(encode(atlas)).hexdigest(),
        factors=all_images(atlas),
        graph=graph_identity(graph, layout),
        caller=completed_caller(graph, layout),
        phases=contact_receipt(
            layout, json.loads((DATA / "CALLER-PHASE-BASES.json").read_bytes())["by_q"]
        ),
    )
    return result


if __name__ == "__main__":
    result = run()
    if "--emit" not in sys.argv:
        require(
            result == json.loads((HERE / "RESULT.json").read_bytes())["complex"],
            "frozen complex evidence",
        )
    print(json.dumps(result, sort_keys=True))
    print("PASS_GRADE14_ALL_COLUMN_COMPLEX")

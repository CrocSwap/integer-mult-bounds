"""Whole BIT exterior correction kernel under a fixed old paid schedule."""
from collections import defaultdict
import gzip
from hashlib import sha256
import json
from pathlib import Path
import runpy
from time import monotonic

ROOT = Path(__file__).resolve().parent
PINS = {
    "prior.py": "4fb801c8219cf4f356b9eab7108a8f2497cc3bc49b089d87086b8ba3c8b13a84",
    "PRIOR.json": "42d7c43180690bcbd062fe011d3e4a0f12305d952e823afb34a1f76a4872b82b",
    "SOURCES.tsv": "f7d91bad2f7fb645e7d931a9aaeb1e572ed864c7d6057eae53c2f6eefa05a7e9",
}


def libraries(word, events, deadline):
    n = word["public"]
    chart = word["start"] + [None] * word["owned_fields"]
    rows = [1 << i for i in range(n)] + [0] * word["owned_fields"]
    marker = [0] * len(chart)
    all_rows, clean = defaultdict(set), defaultdict(set)
    wanted = set(word["final"]) - {1}

    def observe(i):
        if rows[i] and chart[i] in wanted:
            all_rows[chart[i]].add(rows[i])
            if not marker[i]:
                clean[chart[i]].add(rows[i])

    for i in range(n):
        observe(i)
    for t, (op, i, *a) in enumerate(word["program"]):
        if t % 1024 == 0 and monotonic() >= deadline:
            raise TimeoutError("late exterior compensation cap")
        if op == "MOVE":
            assert chart[i] == a[0]
            if t in events:
                marker[i] ^= 1 << events[t]
            chart[i] = a[1]
        elif op == "ADD":
            j, f = a
            assert chart[i] == chart[j] == f
            rows[i] ^= rows[j]
            marker[i] ^= marker[j]
        elif op == "SWAP":
            j = a[0]
            chart[i], chart[j] = chart[j], chart[i]
            rows[i], rows[j] = rows[j], rows[i]
            marker[i], marker[j] = marker[j], marker[i]
            observe(j)
        else:
            assert op in ("INIT", "CLEAR") and a[0] != 1
            chart[i], rows[i], marker[i] = (a[0] if op == "INIT" else None), 0, 0
        observe(i)
    assert chart == word["final"] + [None] * word["owned_fields"]
    final = defaultdict(set)
    for i, f in enumerate(chart):
        if not marker[i] and rows[i] and f in wanted:
            final[f].add(rows[i])
    return (final, clean, all_rows), marker


def kernel(spaces, constraints, lin):
    cols = [(i, row) for i, s in enumerate(spaces) for row in s]
    pivots, equations = {}, []
    for mask, span in constraints:
        here = defaultdict(int)
        for j, (i, row) in enumerate(cols):
            if (mask >> i) & 1:
                for k in lin.positions(lin.reduce(span, row)[0]):
                    here[k] ^= 1 << j
        for row in here.values():
            if row:
                lin.insert(pivots, row)
                equations.append(row)
    null = []
    for j in range(len(cols)):
        if j in pivots:
            continue
        vector = 1 << j
        for k, (row, _) in sorted(pivots.items()):
            if (vector & row).bit_count() & 1:
                vector ^= 1 << k
        assert all((row & vector).bit_count() % 2 == 0 for row in equations)
        output = [0] * len(spaces)
        for k in lin.positions(vector):
            i, row = cols[k]
            output[i] ^= row
        null.append(output)
    assert len(null) + len(pivots) == len(cols)
    return len(cols), len(pivots), null


def watch_sites(incidence, marks, singleton):
    watch, virtual = defaultdict(list), defaultdict(set)
    for j in singleton:
        p = marks[j]
        limits = p["event"], p["quiet_window"][1]
        for f in {p["source_chart"], *p["compatible_literal_charts"]}:
            watch[f].append((j, limits))
        for v in p["_variants"]:
            for e in v["virtual_bank_events"]:
                for mode, limit in enumerate(limits):
                    if (e if mode == 0 else incidence[e]["quiet_window"][0]) <= limit:
                        virtual[e].add((j, mode, v["literal_chart"]))
    return watch, virtual


def evaluate(inputs):
    deadline = monotonic() + 480
    for p, sha in PINS.items():
        if sha256((ROOT / p).read_bytes()).hexdigest() != sha:
            raise ValueError(f"SHA-256 mismatch: {p}")
    old = runpy.run_path(str(ROOT / "prior.py"))
    frozen = json.loads((ROOT / "PRIOR.json").read_bytes())
    source, pins = old["read"](inputs)
    lin = old["load"]("r22", inputs / "round22/verify.py")
    pricing = old["load"]("p7209", inputs / "pr7209/verify.py")
    bit = json.loads(gzip.decompress(source[old["NATIVE"]]))
    invoice = json.loads(source[old["INVOICE"]])
    dims = {int(f): x["dim"] for f, x in bit["frames"].items()}
    r24 = json.loads(source["round24/RESULT.json"])
    r22 = json.loads(source["round22/RESULT.json"])
    tariff = json.loads(source["bit-price/RESULT.json"])
    ports = {p["event"]: p for p in r24["incidence"]}
    marks = [p for p in ports.values() if p["marked"]]
    bank_events = [p["event"] for p in marks]
    markmap = json.loads(source["pr7209/RESULT.json"])["bank_maps"]
    for p, m in zip(marks, markmap, strict=True):
        assert p["event"] == m["event"]
        p["_variants"] = m["variants"]
    singleton = [0, 1, 2, 3, 4, 5, 6, 10, 14, 17]
    watch, virtual = watch_sites(ports, marks, singleton)
    carriers = {c["event"]: {**c, "old_row": lin.encoded(c["old_row"])}
                for c in frozen["carriers"]}
    _, protected, exterior, terminal, required, seen = old["record_timeline"](
        bit, carriers, watch, virtual, deadline)
    events = {t: c["index"] for t, c in carriers.items()}
    libs, marker = libraries(bit, events, deadline)
    assert all(marker[i] == m for i, m in exterior.items())
    assert (len(events), len(protected), len(exterior), len(terminal)) == (60, 2266, 114, 545)
    W = {}
    donors = sorted(set(terminal) - set(bank_events))
    for i, t in enumerate(donors + bank_events):
        assert lin.insert(W, terminal[t], 1 << i)[0]
    assert len(W) == lin.rnk(required) == 545 and all(not lin.reduce(W, row)[0] for row in required)
    spaces = [[lin.encoded(row) for row in item["rows"]]
              for item in frozen["scopes"][-1]["carrier_source_bases"]]
    hard = [(m, {}) for m in sorted(set(protected.values()) - {0})]
    n, raw_rank, _ = kernel(spaces, hard + [(m, {}) for m in exterior.values()], lin)
    assert n == raw_rank == 148
    reports = []
    labels = ("final live marker-free", "historical marker-free", "all old historical",
              "ignore all protected and exterior constraints")
    for tag, lib in zip(labels, (*libs, {}), strict=True):
        bases = {}
        for frame, rows in lib.items():
            basis = {}
            for row in sorted(rows):
                lin.insert(basis, row)
            bases[frame] = basis
        combined = hard + [(m, bases.get(bit["final"][i], {})) for i, m in exterior.items()]
        if tag == labels[-1]:
            combined = []
        size, rank, null = kernel(spaces, combined, lin)
        for vec in null:
            assert all(not lin.reduce(base, old["xor"](vec[j] for j in lin.positions(mask)))[0]
                       for mask, base in combined)
        names = []
        for j in singleton:
            base = {lin.encoded(row["row"]) for row in r22["scope"][1]["banks"][j]["source_witnesses"]}
            candidates = {old["xor"](v[i] for i in lin.positions(m)) for m in seen[1][j] for v in null}
            _, intersection = lin.intersection_projection(lin.raw_basis(sorted(base | candidates)), W)
            new = {}
            for projection, row in intersection:
                lin.insert(new, (projection >> 523) & ~(1 << j), row)
            if new:
                names.append([j, len(new)])
        reports.append({"scope": tag, "variables": size, "rank": rank, "nullity": len(null),
                        "coframed_libraries": len(bases), "expansions": names,
                        "price": old["price"](inputs, pricing, bit, dims, invoice, len(names), tariff)})
        if monotonic() >= deadline:
            raise TimeoutError("late exterior compensation cap")
    print(json.dumps({"status": "EXACT_LATE_EXTERIOR_COMPENSATION_UPPER", "pins": PINS,
                      "input_pins": pins, "scope": reports, "paid": len(protected),
                      "exterior": len(exterior), "deferred_terminal": len(terminal)},
                     sort_keys=True, indent=2))


if __name__ == "__main__":
    assert __debug__
    evaluate(ROOT / "inputs")

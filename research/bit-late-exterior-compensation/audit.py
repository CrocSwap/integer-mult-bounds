"""Independent column-space and terminal-intersection audit for BIT compensation."""
from collections import defaultdict
from hashlib import sha256
import gzip
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def encode(row):
    return sum(1 << j for j in row)


def basis(rows):
    result = {}
    for v in rows:
        while v:
            p = v.bit_length() - 1
            if p not in result:
                result[p] = v
                break
            v ^= result[p]
    return result


def residual(v, pivots):
    for p, row in pivots:
        if v >> p & 1:
            v ^= row
    return v


def trace(word, carriers, marked, markmap, ports, singletons):
    rows = [1 << i for i in range(word["public"])] + [0] * word["owned_fields"]
    markers = [set() for _ in rows]
    chart = word["start"] + [None] * word["owned_fields"]
    scope = set(word["final"]) - {1}
    history, clean = defaultdict(set), defaultdict(set)
    near, virtual = defaultdict(list), defaultdict(list)
    seen = defaultdict(set)
    for j in singletons:
        p = marked[j]
        cutoff = p["quiet_window"][1]
        for f in {p["source_chart"], *p["compatible_literal_charts"]}:
            near[f].append((j, cutoff))
        for v in markmap[j]["variants"]:
            for t in v["virtual_bank_events"]:
                if ports[t]["quiet_window"][0] <= cutoff:
                    virtual[t].append(j)

    def observation(i, cut):
        f, value = chart[i], rows[i]
        if f in scope and value:
            history[f].add(value)
            if not markers[i]:
                clean[f].add(value)
        for j, lim in near[f]:
            if cut <= lim:
                seen[j].update(markers[i])

    for i in range(word["public"]):
        observation(i, 0)
    term, hard = {}, set()
    for t, (op, i, *a) in enumerate(word["program"]):
        if op == "MOVE":
            old, new = a
            assert chart[i] == old
            if new == 1:
                term[t] = rows[i]
                for j in virtual[t]:
                    seen[j].update(markers[i])
            elif t not in carriers:
                hard.add(frozenset(markers[i]))
            if t in carriers:
                assert not markers[i]
                markers[i] = {carriers[t]}
            chart[i] = new
        elif op == "ADD":
            j = a[0]
            rows[i] ^= rows[j]
            markers[i] = markers[i] ^ markers[j]
        elif op == "SWAP":
            j = a[0]
            for seq in (rows, markers, chart):
                seq[i], seq[j] = seq[j], seq[i]
            observation(j, t + 1)
        else:
            assert op in ("INIT", "CLEAR")
            rows[i], markers[i] = 0, set()
            chart[i] = a[0] if op == "INIT" else None
        observation(i, t + 1)
    exterior = [(frozenset(m), f) for m, f in zip(markers, chart, strict=True)
                if f in scope]
    final = defaultdict(set)
    for row, m, f in zip(rows, markers, chart, strict=True):
        if f in scope and not m and row:
            final[f].add(row)
    return term, hard - {frozenset()}, exterior, seen, (final, clean, history)


def joint_rank(sources, hard, exterior, lib):
    cache = {f: sorted(basis(rows).items(), reverse=True) for f, rows in lib.items()}
    cols = []
    for i, rows in enumerate(sources):
        for row in rows:
            col = 0
            for m in hard:
                col = (col << 659) | (row if i in m else 0)
            for m, f in exterior:
                rem = residual(row, cache.get(f, ())) if i in m else 0
                col = (col << 659) | rem
            cols.append(col)
    return len(basis(cols))


def main():
    result = json.loads((ROOT / "RESULT.json").read_bytes())
    frozen_bytes = (ROOT / "PRIOR.json").read_bytes()
    assert sha256(frozen_bytes).hexdigest() == result["pins"]["PRIOR.json"]
    frozen = json.loads(frozen_bytes)
    blobs = {}
    for p, expected in result["input_pins"].items():
        raw = (ROOT / "inputs" / p).read_bytes()
        assert sha256(raw).hexdigest() == expected, p
        blobs[p] = raw
    word = json.loads(gzip.decompress(blobs["research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz"]))
    r24 = json.loads(blobs["round24/RESULT.json"])
    r22 = json.loads(blobs["round22/RESULT.json"])
    markmap = json.loads(blobs["pr7209/RESULT.json"])["bank_maps"]
    ports = {p["event"]: p for p in r24["incidence"]}
    marked = [p for p in ports.values() if p["marked"]]
    singles = [0, 1, 2, 3, 4, 5, 6, 10, 14, 17]
    carriers = {c["event"]: c["index"] for c in frozen["carriers"]}
    sources = [[encode(row) for row in c["rows"]]
               for c in frozen["scopes"][-1]["carrier_source_bases"]]
    term, hard, exterior, seen, libs = trace(word, carriers, marked, markmap, ports, singles)
    assert len(term) == 545 and len(exterior) == 114
    ranks = [joint_rank(sources, hard, exterior, lib) for lib in libs]
    assert ranks == [x["rank"] for x in result["scope"][:3]] == [148, 148, 100]
    assert result["scope"][-1]["rank"] == 0
    U = [v for t, v in term.items() if t not in {p["event"] for p in marked}]
    W = list(term.values())
    assert len(basis(U)) == 523 and len(basis(W)) == 545
    pooled = [row for s in sources for row in s]

    def expansion(S, j):
        W0 = U + [term[marked[j]["event"]]]
        return 21 - len(basis([*S, *W])) + len(basis([*S, *W0]))

    live_dims, pooled_dims = [], []
    for j in singles:
        b = [encode(p["row"]) for p in r22["scope"][1]["banks"][j]["source_witnesses"]]
        live_dims.append(expansion([*b, *(row for i in seen[j] for row in sources[i])], j))
        pooled_dims.append(expansion([*b, *pooled], j))
    assert live_dims == [0] * 10 and pooled_dims == [9] * 10
    print(json.dumps({"status": "PASS_INDEPENDENT_COLUMN_RANK_AND_INTERSECTION_DIMENSIONS",
                      "ranks": ranks, "exterior": len(exterior), "protected_mask_classes": len(hard),
                      "source_pool_rank": len(basis(pooled)), "unrestricted_fixed_trace_expansions": live_dims,
                      "arbitrary_chart_clock_pool_expansions": pooled_dims}, sort_keys=True))


if __name__ == "__main__":
    assert __debug__
    main()

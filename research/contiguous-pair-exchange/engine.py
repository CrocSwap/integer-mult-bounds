"""Contiguous-pair coordinate pricing, two-round carry exchange, and min-cost circuit reclamation.
Prepared by Thomas Marchand with Google Antigravity assistance. Apache-2.0.
"""
import sys
if sys.flags.optimize:
    raise ValueError("Assertions must remain enabled")
sys.dont_write_bytecode = True

import copy
import gzip
import importlib.util
import json
import os
import shlex
import struct
import subprocess
import time
from collections import Counter
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts/experiments"))

import aligned_composition_engine as base_engine
import aligned_composition_graph as base_graph
from aligned_composition_nodeops import relabel, verify_dense
from binary_frame_math import logs

ORACLE_COORDS_STAGE_A = {
    23: [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 17, 19, 20, 21, 22, 0, 1, 3, 2, 4],
    25: [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24, 1, 0, 2, 3, 23],
}

ORACLE_COORDS_STAGE_B = {
    23: [6, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 17, 19, 20, 21, 22, 1, 2, 4, 3, 0],
    25: [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24, 1, 0, 2, 3, 23],
}

FINAL_COORDS = {
    23: [6, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 17, 19, 20, 21, 22, 1, 2, 4, 3, 0],
    25: [5, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24, 1, 0, 2, 3, 23],
}


def compile_oracle_exe(work):
    exe = work / "oracle"
    subprocess.run(
        [
            *shlex.split(os.environ.get("CXX", "c++")),
            "-O3",
            "-std=c++17",
            "-I",
            str(ROOT / "references/frame-compiler/pr48/scripts/partial_swap"),
            str(HERE / "profile_oracle_cached.cpp"),
            "-o",
            str(exe),
        ],
        check=True,
    )
    return exe


def compile_stage_a_axis(h, work, oracle_exe=None):
    """Compile h=25 with the pristine unchanged PR91 engine and contiguous-pair ORACLE_COORDINATES."""
    if oracle_exe is None:
        oracle_exe = compile_oracle_exe(work)
    if h == 23:
        parent_word = json.loads(gzip.decompress((ROOT / "certificates/aligned-composition-word-23.json.gz").read_bytes()))
        inv23 = [ORACLE_COORDS_STAGE_A[23].index(i) for i in range(23)]
        raw_word = relabel(copy.deepcopy(parent_word), inv23)
        word = relabel(raw_word, FINAL_COORDS[23])
        raw = (json.dumps(word, separators=(",", ":")) + "\n").encode()
        assert raw == gzip.decompress((HERE / "stage-a-word-23.json.gz").read_bytes()), "Stage A h=23 word differs"
        return dict(h=23, roles=word["R"], word_sha256=sha256(raw).hexdigest())

    source = ROOT / "scripts/experiments/aligned_composition_engine.py"
    previous = sys.path[:]
    try:
        spec = importlib.util.spec_from_file_location("stage_a_pr91_engine", source)
        eng = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(eng)
    finally:
        sys.path[:] = previous

    config = base_graph.configuration(h)
    eng.graph = base_graph.graph
    eng.PENDING_COST = True
    eng.OUTPUT_MODE = config["output_mode"]
    eng.THREE_CYCLE_PASSES = config["three_cycle_passes"]
    eng.ORACLE_COORDINATES = ORACLE_COORDS_STAGE_A[h]
    eng.ORACLE_EXE = str(oracle_exe)
    eng.ORACLE_INPUT = str(work / f"stage-a-oracle-{h}.bin")
    eng.oracles = []
    try:
        result, word = eng.compile_(h, matching=True, reclaim=True, dirty=True)
    finally:
        for proc in eng.oracles:
            proc.stdin.close()
            assert proc.wait(timeout=10) == 0

    word = relabel(word, FINAL_COORDS[h])
    raw = (json.dumps(word, separators=(",", ":")) + "\n").encode()
    assert raw == gzip.decompress((HERE / f"stage-a-word-{h}.json.gz").read_bytes()), f"Stage A h={h} word differs"
    assert result["roles"] == word["R"] == 34771
    return dict(
        h=h,
        roles=word["R"],
        word_sha256=sha256(raw).hexdigest(),
        engine_sha256=sha256(source.read_bytes()).hexdigest(),
        oracle_coordinates=ORACLE_COORDS_STAGE_A[h],
        final_coordinates=FINAL_COORDS[h],
    )


def compile_stage_b_axis(h, work, oracle_exe=None):
    """Compile h in {23, 25} with two-round carry exchange, min-cost circuit reclamation, and contiguous-pair pricing."""
    if oracle_exe is None:
        oracle_exe = compile_oracle_exe(work)
    t0 = time.time()
    config = base_graph.configuration(h)
    output_mode = config["output_mode"]
    three_cycle_passes = 3
    outer_exchange_rounds = 2
    oracle_map = ORACLE_COORDS_STAGE_B[h]
    assert sorted(oracle_map) == list(range(h))

    base_engine.graph = base_graph.graph
    c, blocks, uses, value_uses, owner, signal, order, contains = base_engine.build(h)
    v = len(c.inputs)
    position = {g: i for i, g in enumerate(order)}
    edges, chosen, right, stats = base_engine.match(blocks, uses, True)

    slots = []
    frames = []
    ops = []
    events = []
    hist = Counter()
    assign = {}
    sources = {}
    retired = set()
    retired_index = base_engine.RetiredIndex(h)
    pending = {}
    pending_index = base_engine.PendingIndex(h)
    stats["regions"] = len(blocks)
    stats["matched"] = len(chosen)
    stats["multi_node_regions"] = sum(len(b["nodes"]) > 1 for b in blocks)

    def new(g):
        s = len(slots)
        slots.append(0)
        frames.append(g)
        hist[blocks[g]["rank"]] += 1
        events.append((s, -1, g))
        return s

    def raise_(s, g):
        old = frames[s]
        assert contains(blocks[old]["frame"], blocks[g]["frame"])
        if s in retired:
            retired_index.remove(s, blocks[old]["frame"], blocks[old]["rank"])
            retired_index.insert(s, blocks[g]["frame"], blocks[g]["rank"])
        if s in pending:
            pending_index.move(s, blocks[old]["frame"], blocks[g]["frame"])
        hist[blocks[g]["rank"] - blocks[old]["rank"]] += 1
        frames[s] = g
        events.append((s, old, g))

    def xor(a, b, g):
        assert a != b
        raise_(a, g)
        raise_(b, g)
        slots[a] ^= slots[b]
        ops.append((a, b, g))

    weights = [0] + [int(t * sum(logs(t)) * 10**30 // 2) for t in range(1, h + 1)]
    oracle_input = work / f"stage-b-oracle-{h}.bin"
    with oracle_input.open("wb") as stream:
        stream.write(struct.pack("<6I2Q", h, v, 0, len(blocks) + 2, 0, 0, h * (h - 1), h * (h - 1)))
        stream.write(struct.pack("<2QI", 0, 0, 0))
        stream.write(struct.pack("<2QI", 0, 0, h))
        for b in blocks:
            stream.write(
                struct.pack(
                    "<2QI",
                    *[sum(1 << oracle_map[i] for i in range(h) if mask >> i & 1) for mask in b["frame"]],
                    b["rank"],
                )
            )
    oracle = subprocess.Popen(
        [str(oracle_exe), str(oracle_input)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    try:
        cache = {}

        def profile_entropy(a, b):
            if (a, b) not in cache:
                oracle.stdin.write(f"{a} {b}\n")
                oracle.stdin.flush()
                answer = oracle.stdout.readline()
                assert answer
                parts = list(map(int, answer.split()))
                assert len(parts) == h + 1
                cache[a, b] = sum(n * w for n, w in zip(parts, weights))
            return cache[a, b]

        def profile_cost(a, g):
            old = frames[a] + 2
            target = g + 2
            endpoint = pending[a] + 2 if a in pending else 1
            return profile_entropy(old, endpoint) - profile_entropy(old, target) - profile_entropy(target, endpoint)

        def carry_price(edge):
            g, u, i = edge
            producer = owner[blocks[g]["inputs"][i]]
            target = uses[u][1]
            return (
                -profile_entropy(g + 2, target + 2)
                + profile_entropy(g + 2, 1)
                + profile_entropy(0, producer + 2)
                + profile_entropy(producer + 2, target + 2)
            )

        prices = [carry_price(edge) for edge in edges]
        priority = sorted(range(len(edges)), key=lambda e: (prices[e], edges[e]))
        initial_count = len(chosen)
        initial_price = sum(prices[e] for e in chosen)

        def carry_can(e, drop=None):
            g, u, i = edges[e]
            rows = blocks[g]["outbasis"] + [1 << edges[f][2] for f in blocks[g]["selected"] if f != drop]
            return base_engine.independent(base_engine.basis(rows), 1 << i)

        lookup = {(g, u): e for e, (g, u, i) in enumerate(edges)}

        for _outer in range(outer_exchange_rounds):
            any_outer = 0
            for _phase in range(3):
                changes = 0
                for e in priority:
                    if e in chosen:
                        continue
                    g, u, i = edges[e]
                    f = right.get(u)
                    if f is not None:
                        if prices[e] >= prices[f]:
                            continue
                        if not carry_can(e, f if edges[f][0] == g else None):
                            continue
                    else:
                        f = next(
                            (
                                z
                                for z in sorted(blocks[g]["selected"], key=lambda z: (-prices[z], z))
                                if prices[e] < prices[z] and carry_can(e, z)
                            ),
                            None,
                        )
                        if f is None:
                            continue
                    fg, fu, fi = edges[f]
                    chosen.remove(f)
                    blocks[fg]["selected"].remove(f)
                    del right[fu]
                    chosen.add(e)
                    blocks[g]["selected"].add(e)
                    assert u not in right
                    right[u] = e
                    changes += 1
                stats["carry_exchanges"] += changes
                any_outer += changes
                if not changes:
                    break

            for _phase in range(3):
                changes = 0
                for e in priority:
                    if e in chosen:
                        continue
                    g, u, i = edges[e]
                    f = right.get(u)
                    if f is None:
                        continue
                    fg, fu, fi = edges[f]
                    if fg == g:
                        continue
                    options = []
                    for z in sorted(blocks[g]["selected"]):
                        zg, zu, zi = edges[z]
                        other = lookup.get((fg, zu))
                        if other is None or other in chosen:
                            continue
                        gain = prices[f] + prices[z] - prices[e] - prices[other]
                        if gain > 0 and carry_can(e, z) and carry_can(other, f):
                            options.append((-gain, z, other))
                    if not options:
                        continue
                    _, z, other = min(options)
                    for old in (f, z):
                        og, ou, oi = edges[old]
                        chosen.remove(old)
                        blocks[og]["selected"].remove(old)
                        del right[ou]
                    for new_edge in (e, other):
                        ng, nu, ni = edges[new_edge]
                        assert nu not in right
                        chosen.add(new_edge)
                        blocks[ng]["selected"].add(new_edge)
                        right[nu] = new_edge
                    changes += 1
                stats["carry_two_cycles"] += changes
                any_outer += changes
                if not changes:
                    break

            for _phase in range(three_cycle_passes):
                changes = base_engine.improve_three_cycles(blocks, edges, chosen, right, prices, priority, carry_can)
                stats["carry_three_cycles"] += changes
                any_outer += changes
                if not changes:
                    break

            if not any_outer:
                break

        assert len(chosen) == len(right) == initial_count
        assert sum(prices[e] for e in chosen) <= initial_price

        def bits(e):
            out = []
            while e:
                bit = e & -e
                out.append(bit.bit_length() - 1)
                e ^= bit
            return out

        def acquire(g, anchors):
            bb = {}
            circuits = []
            candidates = []

            def ins(s):
                row = slots[s]
                expr = 1 << s
                while row:
                    p = row.bit_length() - 1
                    if p not in bb:
                        bb[p] = (row, expr)
                        return None
                    old, e = bb[p]
                    row ^= old
                    expr ^= e
                return expr

            slot_prices = {}

            def s_price(s):
                if s not in slot_prices:
                    slot_prices[s] = profile_cost(s, g)
                return slot_prices[s]

            for s in anchors:
                e = ins(s)
                if e is not None:
                    circuits.append(e)

            elig_pending = sorted(
                pending_index.eligible(blocks[g]["frame"]),
                key=lambda s: (s_price(s), pending_index.order[s]),
            )
            for s in elig_pending:
                e = ins(s)
                stats["live_anchor_candidates"] += 1
                if e is not None:
                    circuits.append(e)

            for s in retired_index.eligible(blocks[g]["frame"]):
                e = ins(s)
                if e is None:
                    continue
                assert e >> s & 1
                candidates.append((s, e))
                circuits.append(e)

            if not candidates:
                return new(g)

            if circuits:
                top_circuits = sorted(set(circuits), key=lambda e: (e.bit_count(), e))[:64]
                expanded = [(c_mask, bits(c_mask)) for c_mask in top_circuits]
            else:
                expanded = []

            best = None
            for s, e in candidates:
                cost = sum(s_price(z) for z in bits(e))
                count = e.bit_count()
                for _phase in range(2):
                    changed = False
                    for circuit, zz in expanded:
                        if circuit >> s & 1:
                            continue
                        delta = sum((-s_price(z) if e >> z & 1 else s_price(z)) for z in zz)
                        alternative = e ^ circuit
                        newcount = alternative.bit_count()
                        if (cost + delta, newcount) < (cost, count):
                            e = alternative
                            cost += delta
                            count = newcount
                            changed = True
                            stats["zero_circuit_toggles"] += 1
                    if not changed:
                        break
                aa = bits(e ^ (1 << s))
                key = (cost, len(aa), s)
                if best is None or key < best[0]:
                    best = (key, s, aa)

            _, s, aa = best
            for a in aa:
                if a in pending:
                    stats["live_anchor_xors"] += 1
                xor(s, a, g)
            assert not slots[s]
            retired_index.remove(s, blocks[frames[s]]["frame"], blocks[frames[s]]["rank"])
            retired.remove(s)
            stats["reclaimed"] += 1
            stats["clearing_xors"] += len(aa)
            return s

        for step, g in enumerate(order):
            b = blocks[g]
            outuses = [u for u in b["uses"] if u not in right]
            outvalues = sorted({uses[u][0] for u in outuses})
            assert outvalues == b["outvalues"]
            if output_mode.startswith("route-"):
                def deadline(u):
                    return len(order) + 1 if uses[u][2] is not None else position[uses[u][1]]
                outuses.sort(key=lambda u: ((1 if output_mode == "route-early" else -1) * deadline(u), u))
            if b["source"]:
                x = b["nodes"][0]
                s = new(g)
                sources[x - 1] = s
                slots[s] = signal[x]
                value_slots = {x: s}
            else:
                ins_slots = [assign[next(u for u in value_uses[y] if uses[u][1] == g and uses[u][2] is None)] for y in b["inputs"]]
                for s in ins_slots:
                    pending_index.remove(s, blocks[frames[s]]["frame"], blocks[g]["frame"])
                    del pending[s]
                for s, y in zip(ins_slots, b["inputs"]):
                    raise_(s, g)
                rows = []
                labels = []
                echelon = []
                for x in outvalues:
                    r = b["coeff"][x]
                    if base_engine.independent(echelon, r):
                        rows.append(r)
                        labels.append(("value", x))
                        echelon = base_engine.basis(rows)
                for e in sorted(b["selected"]):
                    _, u, i = edges[e]
                    r = 1 << i
                    rows.append(r)
                    labels.append(("carry", u))
                    echelon = base_engine.basis(rows)

                def future_priority(i):
                    compatible = sum(
                        position[uses[u][1]] > step and contains(b["frame"], blocks[uses[u][1]]["frame"])
                        for u in value_uses[b["inputs"][i]]
                    )
                    return (-compatible, slots[ins_slots[i]].bit_count(), i)

                for i in sorted(range(len(ins_slots)), key=future_priority):
                    if base_engine.independent(echelon, 1 << i):
                        rows.append(1 << i)
                        labels.append(("retire", i))
                        echelon = base_engine.basis(rows)
                rr = rows.copy()
                elim = []
                for i in range(len(ins_slots)):
                    j = next(j for j in range(i, len(ins_slots)) if rr[j] >> i & 1)
                    if j != i:
                        for a, z in ((i, j), (j, i), (i, j)):
                            rr[a] ^= rr[z]
                            elim.append((a, z))
                    for j in range(len(ins_slots)):
                        if j != i and rr[j] >> i & 1:
                            rr[j] ^= rr[i]
                            elim.append((j, i))
                for a, z in reversed(elim):
                    xor(ins_slots[a], ins_slots[z], g)
                value_slots = {}
                for s, (kind, key) in zip(ins_slots, labels):
                    if kind == "value":
                        value_slots[key] = s
                    elif kind == "carry":
                        assign[key] = s
                        pending[s] = uses[key][1]
                        pending_index.insert(s, blocks[frames[s]]["frame"], blocks[pending[s]]["frame"])
                    else:
                        retired.add(s)
                        retired_index.insert(s, blocks[frames[s]]["frame"], blocks[frames[s]]["rank"])
                ob = list(value_slots)
                bb_out = {}
                for i, x in enumerate(ob):
                    r = b["coeff"][x]
                    e = 1 << i
                    while r:
                        p = r.bit_length() - 1
                        if p not in bb_out:
                            bb_out[p] = (r, e)
                            break
                        old, ee = bb_out[p]
                        r ^= old
                        e ^= ee
                for x in outvalues:
                    if x in value_slots:
                        continue
                    r = b["coeff"][x]
                    e = 0
                    while r:
                        p = r.bit_length() - 1
                        old, ee = bb_out[p]
                        r ^= old
                        e ^= ee
                    s = acquire(g, list(value_slots.values()))
                    for i, y in enumerate(ob):
                        if e >> i & 1:
                            xor(s, value_slots[y], g)
                    value_slots[x] = s
            used = set()
            for u in outuses:
                x = uses[u][0]
                s = value_slots[x]
                if x in used:
                    ss = acquire(g, list(value_slots.values()))
                    xor(ss, s, g)
                    s = ss
                used.add(x)
                assign[u] = s
                pending[s] = uses[u][1]
                pending_index.insert(s, blocks[frames[s]]["frame"], blocks[pending[s]]["frame"])
    finally:
        oracle.stdin.close()
        assert oracle.wait(timeout=10) == 0

    output_records = []
    scatter = [0] * v
    J = []
    for u, (x, g, target) in enumerate(uses):
        if target is None:
            continue
        s = assign[u]
        raise_(s, g)
        common, triple = target
        output_records.append((s, g, common, triple))
        targets = [i for i, t in enumerate(c.inputs) if common in t] if len(triple) == 1 else [c.inputs.index(triple)]
        for i in targets:
            scatter[i] ^= slots[s]
            J.append((v + i, 2 * v + s))
        rank = blocks[g]["rank"]
        if len(triple) == 1:
            hist[rank] += 1
            hist[h - rank] += 1
        else:
            hist[h - 1 - rank] += 1
            hist[1] += 1
    for s in retired:
        hist[h - blocks[frames[s]]["rank"]] += 1
    R = len(slots)
    mass = sum(k * val for k, val in hist.items())
    assert mass == h * R + h * (h - 1)
    word = dict(
        h=h,
        v=v,
        R=R,
        ops=ops,
        sources=sources,
        scatter=J,
        outputs=output_records,
        frames=[b["frame"] for b in blocks],
        events=events,
    )
    word = relabel(word, FINAL_COORDS[h])
    raw = (json.dumps(word, separators=(",", ":")) + "\n").encode()
    assert raw == gzip.decompress((HERE / f"word-{h}.json.gz").read_bytes()), f"Stage B h={h} word differs"
    scalar = verify_dense(base_graph.graph(h))
    assert json.loads(json.dumps(scalar)) == json.loads((HERE / f"scalar-{h}.json").read_text())
    return dict(
        h=h,
        roles=R,
        word_sha256=sha256(raw).hexdigest(),
        oracle_coordinates=ORACLE_COORDS_STAGE_B[h],
        final_coordinates=FINAL_COORDS[h],
        stats=dict(stats),
        seconds=time.time() - t0,
    )

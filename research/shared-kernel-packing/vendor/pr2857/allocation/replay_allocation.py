#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay the exact T37 integer flow and realize every literal helper owner.

Per-pattern/time flow and edge-coloring method: Marius-Paul Dumitrean, PR2843.
Changed-word construction and exact-flow replay prepared with OpenAI Codex.
This is a finite allocation replay; full native/outer admission remains separate.
"""
import sys
sys.dont_write_bytecode = True
import argparse
import collections
import gzip
import hashlib
import json
import pathlib
import types

HERE = pathlib.Path(__file__).resolve().parent
T = 37
WID = (4, 5, 7, 8, 9)


def read(path):
    raw = pathlib.Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(path, digest):
    require(path.is_file() and not path.is_symlink(), 'missing or symlink input: ' + str(path))
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == digest, 'input digest mismatch: ' + str(path))
    return raw


def encode(obj, compressed=False):
    raw = json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()
    if compressed:
        raw = bytearray(gzip.compress(raw, mtime=0))
        raw[9] = 255
        raw = bytes(raw)
    return raw


def positive_integer(n):
    return type(n) is int and n > 0


def authenticate_output(name, raw, pins):
    """Regenerated gzip containers may differ; bind the complete payload bytes."""
    if name.endswith('.gz'):
        payload = gzip.decompress(raw)
        expected = pins['expected_output_payload_sha256'][name]
    else:
        payload = raw
        expected = pins['expected_output_sha256'][name]
    require(hashlib.sha256(payload).hexdigest() == expected,
            'realization differs from stored witness payload: ' + name)


def realize_pattern(n, pattern, counts, np, csr_matrix, maximum_bipartite_matching):
    """Use n matchings of an n-regular bipartite multigraph as literal bins."""
    slots = [w for j, w in enumerate(WID) for _ in range(pattern[j])]
    if not slots:
        require(not counts, 'empty pattern has nonempty time flow')
        return [[] for _ in range(n)]
    times = sorted({t for t, w in counts})
    K = len(times)
    require(K >= len(slots), 'insufficient distinct times for a pattern')
    ti = {t: j for j, t in enumerate(times)}
    A = np.zeros((K, K), dtype=np.int64)
    slot_by_w = collections.defaultdict(list)
    for j, w in enumerate(slots):
        slot_by_w[w].append(j)
    for w, js in slot_by_w.items():
        atslot, remaining = 0, n
        for t in times:
            needed = counts.get((t, w), 0)
            while needed:
                take = min(needed, remaining)
                A[ti[t], js[atslot]] += take
                needed -= take
                remaining -= take
                if remaining == 0:
                    atslot += 1
                    remaining = n
        require(atslot == len(js), 'slot supply mismatch')
    require(all(v <= n for v in A.sum(axis=1)), 'time degree exceeds bin count')
    j, remaining = len(slots), n
    for r in range(K):
        needed = n - int(A[r].sum())
        while needed:
            require(j < K, 'dummy slot overflow')
            take = min(needed, remaining)
            A[r, j] += take
            needed -= take
            remaining -= take
            if remaining == 0:
                j += 1
                remaining = n
    require(np.all(A.sum(axis=0) == n) and np.all(A.sum(axis=1) == n), 'graph is not regular')
    output = []
    for color in range(n):
        matching = maximum_bipartite_matching(csr_matrix(A > 0), perm_type='column')
        require(len(matching) == K and min(matching) >= 0 and len(set(map(int, matching))) == K,
                'perfect matching failure')
        output.append([(times[r], slots[int(c)]) for r, c in enumerate(matching) if c < len(slots)])
        A[np.arange(K), matching] -= 1
    require(not A.any(), 'unassigned graph edges')
    return output


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', required=True, type=pathlib.Path,
                    help='Exact extracted PR2833 gmx-t74-borrow43-handoff directory')
    ap.add_argument('--owner-engine', required=True, type=pathlib.Path,
                    help='Pinned independent_candidate_owners_retired7.py from PR2839')
    ap.add_argument('--work', required=True, type=pathlib.Path, help='Fresh output directory')
    args = ap.parse_args()
    source, out = args.source.resolve(), args.work.resolve()
    require(not out.exists(), 'output must be fresh')
    require(not out.is_relative_to(source) and not out.is_relative_to(HERE), 'output must be outside sources')
    require(not any(p.name == '__pycache__' or p.suffix == '.pyc' for p in source.rglob('*')),
            'source contains bytecode artifacts')
    pins = read(HERE / 'PINS.json')
    for name, digest in pins['source_sha256'].items():
        authenticate(source / name, digest)
    owner_code = authenticate(args.owner_engine, pins['owner_engine_sha256'])
    authenticate(HERE / 'construction/FLOW.json.gz', pins['flow_sha256'])

    # Imports occur only after the immutable scientific inputs are authenticated.
    import numpy as np
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import maximum_bipartite_matching

    owner = types.ModuleType('pinned_owner')
    exec(compile(owner_code, str(args.owner_engine), 'exec'), owner.__dict__)
    template = read(source / 'inputs/GLOBAL-TEMPLATE.json.gz')
    plan = read(source / 'inputs/PLAN.json')
    historical_owners = read(source / 'inputs/OWNERS.json.gz')
    timecalls = {}
    for row in historical_owners:
        key, call = row['time'], (row['stage'], row['replica'])
        require(key not in timecalls or timecalls[key] == call, 'ambiguous historical time')
        timecalls[key] = call
    require(set(timecalls) == set(range(9 * T)), 'historical call coverage')
    order = [list(timecalls[t]) for t in range(9 * T)]
    dispatch = read(source / 'inputs/DISPATCH.json')
    require(len(dispatch) == 9 * T and {(s, r) for s, r, pid in dispatch} == set(map(tuple, order)),
            'dispatch coverage')
    require({pid for s, r, pid in dispatch} == {'gauge44', 'extra'}, 'provider coverage')

    providers = read(source / 'new/BORROW-PROVIDERS.json')
    for pid in providers:
        widths = providers[pid]['widths']
        require(len(widths) == 408, 'source helper count')
        for register in (478, 460, 462, 480):
            require(widths[register - 224] == 9, 'source changed-helper width')
            widths[register - 224] = 8
        providers[pid]['actual_paid_profile'] = {1: 2394, 2: 642, 3: 266, 4: 128, 5: 26, 8: 8}
    widths = providers['gauge44']['widths']
    require(widths == providers['extra']['widths'], 'provider inventory mismatch')
    require(collections.Counter(widths) == {4: 26, 5: 2, 7: 62, 8: 84, 9: 234}, 'new width inventory')

    win = owner.windows(template, order, T)
    family = lambda b: b[0] * 896 + (2 * plan['pairs'][str(b[1])] + plan['sides'][str(b[1])]) * 112 + b[2]
    family_windows = collections.defaultdict(list)
    for (o, c), (cap, lo, hi) in win.items():
        family_windows[family((o, c, 0))].append((lo, hi, c))
    for windows in family_windows.values():
        for i, (lo, hi, c) in enumerate(windows):
            require(all(max(lo, l) >= min(hi, h) for l, h, d in windows[i + 1:]),
                    'overlapping source windows in one physical family')

    groups = collections.defaultdict(list)
    for (o, c), (cap, lo, hi) in win.items():
        times = tuple(range(max(0, lo + 1), min(len(order), hi + 1)))
        for port in range(112):
            groups[cap, times].append((o, c, port))
    G = sorted(groups)
    patterns = {
        8: [(0, 0, 0, 1, 0)],
        16: [(0, 0, 1, 0, 1), (0, 0, 0, 2, 0), (0, 0, 1, 0, 0)],
        32: [(0, 0, 2, 0, 2), (0, 0, 0, 0, 3), (1, 0, 0, 0, 3), (0, 1, 0, 0, 3)],
        48: [(0, 0, 0, 0, 0), (0, 0, 0, 0, 5)],
    }
    target = {
        (8, (0, 0, 0, 1, 0)): 672 * T,
        (16, (0, 0, 1, 0, 1)): 406 * T - 1,
        (16, (0, 0, 0, 2, 0)): 42 * T,
        (16, (0, 0, 1, 0, 0)): 1,
        (32, (0, 0, 2, 0, 2)): 76 * T,
        (32, (0, 0, 0, 0, 3)): 120 * T,
        (32, (1, 0, 0, 0, 3)): 234 * T,
        (32, (0, 1, 0, 0, 3)): 18 * T,
        (48, (0, 0, 0, 0, 5)): (432 * T + 1) // 5,
        (48, (0, 0, 0, 0, 0)): 448 * T - (432 * T + 1) // 5,
    }
    flow = read(HERE / 'construction/FLOW.json.gz')
    xc, zc = collections.defaultdict(collections.Counter), collections.defaultdict(collections.Counter)
    global_count = collections.Counter()
    for gi, raw_pattern, n in flow['x']:
        require(type(gi) is int and 0 <= gi < len(G) and positive_integer(n), 'invalid pattern count')
        pattern = tuple(raw_pattern)
        require(pattern in patterns[G[gi][0]] and pattern not in xc[gi], 'invalid or duplicate pattern')
        xc[gi][pattern] = n
        global_count[G[gi][0], pattern] += n
    require(dict(global_count) == target, 'global integer pattern counts differ')
    for gi in range(len(G)):
        require(sum(xc[gi].values()) == len(groups[G[gi]]), 'window class bin count')
    call_count = collections.defaultdict(collections.Counter)
    for gi, raw_pattern, t, w, n in flow['z']:
        pattern = tuple(raw_pattern)
        require(type(gi) is int and 0 <= gi < len(G) and pattern in xc[gi], 'unknown pattern flow')
        require(type(t) is int and t in G[gi][1] and w in WID and pattern[WID.index(w)] > 0,
                'ineligible time/width flow')
        require(positive_integer(n) and (t, w) not in zc[gi, pattern], 'invalid or duplicate time flow')
        zc[gi, pattern][t, w] = n
        call_count[t][w] += n
    for gi, counts in xc.items():
        for pattern, n in counts.items():
            by_width, by_time = collections.Counter(), collections.Counter()
            for (t, w), count in zc[gi, pattern].items():
                by_width[w] += count
                by_time[t] += count
            require(all(by_width[w] == pattern[j] * n for j, w in enumerate(WID)), 'pattern-width supply')
            require(all(count <= n for count in by_time.values()), 'more than one role per bin/time')
    require(set(call_count) == set(range(9 * T)), 'flow call coverage')
    require(all(call_count[t] == collections.Counter(widths) for t in range(9 * T)), 'flow call width demand')

    slots = []
    for gi, (cap, times) in enumerate(G):
        bins, offset = groups[G[gi]], 0
        for pattern, n in sorted(xc[gi].items()):
            assigned = realize_pattern(n, pattern, zc[gi, pattern], np, csr_matrix, maximum_bipartite_matching)
            for b, entries in zip(bins[offset:offset + n], assigned):
                z = 0
                for t, w in sorted(entries):
                    slots.append((t, w, *b, z))
                    z += w
                require(z <= cap, 'bin capacity exceeded')
            offset += n
        require(offset == len(bins), 'unassigned literal bins')
    available = {t: collections.defaultdict(list) for t in range(9 * T)}
    for t in available:
        for h, w in enumerate(widths):
            available[t][w].append(h)
    rows = []
    for t, w, o, c, port, z in sorted(slots):
        require(available[t][w], 'helper width shortage')
        rows.append([t, available[t][w].pop(), o, c, port, z])
    require(not any(v for d in available.values() for v in d.values()), 'unassigned literal helpers')
    fill = {'columns': ['time', 'helper', 'owner_replica', 'child', 'port', 'offset'],
            'dispatch_overrides': [], 'rows': sorted(rows)}
    profile = {1: 805860, 2: 213786, 3: 91775, 4: 42624, 5: 13098, 8: 2664, 9: 1, 48: 13379}
    result, _, _ = owner.check(T, order, fill, {(s, r): pid for s, r, pid in dispatch},
                               profile, plan, template, providers)
    payloads = {'ORDER.json': order, 'FILL.json.gz': fill, 'DISPATCH.json': dispatch,
                'PROFILE.json': profile, 'PROVIDERS.json': providers}
    encoded = {name: encode(obj, name.endswith('.gz')) for name, obj in payloads.items()}
    for name, raw in encoded.items():
        authenticate_output(name, raw, pins)
    out.mkdir(parents=True)
    for name, raw in encoded.items():
        (out / name).write_bytes(raw)
    result.update(status='PASS_EXACT_FLOW_LITERAL_ALLOCATION_REPLAY',
                  full_native_and_outer_admission='required separately',
                  source_head=pins['source_head'])
    (out / 'ALLOCATION-REPLAY.json').write_bytes(encode(result))
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()

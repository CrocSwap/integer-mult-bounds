#!/usr/bin/env python3
"""R420 target forests: exact scalar costs, dirty endpoints and forest bound.
Oscar Fennell, with substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
from collections import Counter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'research/e8-bit-r420/data/bitE8mut-r420.json.gz'
PHASES = ('D', 'A', 'scatter', 'B', 'C')


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()


def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def load_source():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    for path, expected in pins['files'].items():
        raw = (ROOT / path).read_bytes()
        if path.endswith('.gz'):
            raw = canonical(json.loads(gzip.decompress(raw)))
        need(hashlib.sha256(raw).hexdigest() == expected, 'source pin: ' + path)
    return json.loads(gzip.decompress(SOURCE.read_bytes()))


def rows(word):
    out = [0] * 120
    for frame, dst, sources in word['D']:
        need(frame == 0 and 120 <= dst < 240, 'baseline D shape')
        for source in sources:
            need(240 <= source < 660, 'baseline helper source')
            out[dst-120] ^= 1 << source
    return out


def traversal(parents):
    need(len(parents) == 120 and all(type(p) is int and 0 <= p <= 120 for p in parents), 'parent range')
    order, reached = [], {120}
    while len(order) < 120:
        layer = [v for v in range(120) if v not in reached and parents[v] in reached]
        need(layer, 'cycle or disconnected forest')
        order += layer
        reached.update(layer)
    return order


def edge_weight(K, u, v):
    return K[v if u == 120 else u].bit_count() if 120 in (u, v) else (K[u] ^ K[v]).bit_count() + 2


def all_edges(K):
    return [(edge_weight(K, u, v), u, v) for u in range(121) for v in range(u)]


def forest_cost(K, parents):
    traversal(parents)
    return sum(edge_weight(K, v, p) for v, p in enumerate(parents))


def certify_mst(K, parents):
    """Cycle property is a certificate, not a replay of the nomination solver."""
    traversal(parents)
    adj = [[] for _ in range(121)]
    for v, p in enumerate(parents):
        c = edge_weight(K, v, p)
        adj[v].append((p, c))
        adj[p].append((v, c))
    checked = 0
    for u in range(121):
        stack = [(u, -1, 0)]
        maximum = {}
        while stack:
            v, prev, m = stack.pop()
            maximum[v] = m
            stack.extend((n, v, max(m, c)) for n, c in adj[v] if n != prev)
        for v in range(u):
            need(edge_weight(K, u, v) >= maximum[v], 'MST cycle inequality')
            checked += 1
    return {'cost': forest_cost(K, parents), 'cycle_inequalities': checked}


def construct(word, parents):
    K = rows(word)
    order = traversal(parents)
    prep = [[0, 120+v, [120+parents[v]]] for v in reversed(order) if parents[v] != 120]
    correction = []
    for v, p in enumerate(parents):
        row = K[v] ^ (K[p] if p != 120 else 0)
        src = [s for s in range(240, 660) if row >> s & 1]
        if src:
            correction.append([0, 120+v, src])
    changed = copy.deepcopy(word)
    changed['D'] = prep + correction + list(reversed(prep))
    return changed


def semantic_D(word, baseline):
    """All 660 symbolic columns; target inputs are independent and nonzero."""
    state = [1 << r for r in range(660)]
    for f, d, srcs in word['D']:
        need(f == 0 and 120 <= d < 240, 'D must touch only frame-zero targets')
        need(srcs and len(set([d] + srcs)) == 1+len(srcs), 'D operands')
        for s in srcs:
            need(120 <= s < 660, 'D source must be target or helper')
            state[d] ^= state[s]
    want = [1 << r for r in range(660)]
    for t, row in enumerate(rows(baseline)):
        want[120+t] ^= row
    need(state == want, 'dirty D endpoint')


def records(word, dims):
    cur = list(word['start'])
    result = []
    def move(r, frame):
        if cur[r] != frame:
            result.append((0, r, cur[r], frame, dims[frame]-dims[cur[r]], 0))
            cur[r] = frame
    for phase, name in enumerate(PHASES, 1):
        if name == 'scatter':
            for k, q in enumerate(word['ret']):
                f = cur[q]
                result.append((2, q, 660, f, 0, dims[f]))
                for t, row in enumerate(word['scatter']):
                    if k in row:
                        result.append((1, 120+t, 660, 1, 0, 3))
                result.append((3, q, 660, f, 0, 0))
        else:
            for f, d, srcs in word[name]:
                for r in [d] + srcs:
                    move(r, f)
                result.extend((1, d, s, 1, f, phase) for s in srcs)
    for r, f in enumerate(word['final']):
        move(r, f)
    return result


def prefix_bounds(rec):
    maxima = []
    for reverse in (False, True):
        norms = [1] * 661
        largest, opened = 1, False
        for op, a, b, c, f, z in (reversed(rec) if reverse else rec):
            if op == 1:
                norms[a] += abs(c)*norms[b]
                largest = max(largest, norms[a])
            elif op in (2, 3):
                opening = (op == 2) != reverse
                need(opened != opening, 'copy lifecycle')
                norms[b] = norms[a] if opening else 0
                opened = opening
        need(not opened, 'open copy at endpoint')
        maxima.append(largest)
    F, B = maxima
    payload = 64 * F**3 * B**2
    return {'forward': F, 'reverse': B, 'payload': str(payload), 'payload_bits': payload.bit_length()}


def independent_set_replay(rec):
    """Separate set-valued interpreter for the actual binary native stream."""
    for backwards in (False, True):
        state = [{r} for r in range(660)] + [set()]
        opened = False
        for op, a, b, c, f, z in (reversed(rec) if backwards else rec):
            if op == 1 and c % 2:
                state[a].symmetric_difference_update(state[b])
            elif op in (2, 3):
                opening = (op == 2) != backwards
                need(opened != opening, 'set copy lifecycle')
                state[b] = set(state[a]) if opening else set()
                opened = opening
        want = [{r} if not 120 <= r < 240 else {r, r-120} for r in range(660)] + [set()]
        need(state == want and not opened, 'independent full endpoint')


def inventory(word, rec):
    profile = Counter()
    for op, a, b, c, f, z in rec:
        if op == 0:
            profile[f] += 1
        elif op == 2:
            profile[z] += 1
    return {'D_XORs': sum(len(g[2]) for g in word['D']),
            'ADDs': sum(r[0] == 1 for r in rec), 'records': len(rec),
            'COPYs': sum(r[0] == 2 for r in rec),
            'ERASEs': sum(r[0] == 3 for r in rec),
            'profile': {str(k): v for k, v in sorted(profile.items())},
            'rank_mass': sum(k*v for k, v in profile.items()),
            'prefix': prefix_bounds(rec), 'word_sha256': digest(word)}


def expect_rejection(fn, label):
    try:
        fn()
    except (ValueError, RuntimeError):
        return label
    raise ValueError('control was accepted: ' + label)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-certificate', action='store_true')
    parser.add_argument('--native', action='store_true')
    args = parser.parse_args()
    baseline = load_source()
    recipe = json.loads((HERE / 'RECIPE.json').read_text())
    K = rows(baseline)
    optimum = certify_mst(K, recipe['minimum_parents'])
    changed = construct(baseline, recipe['feasible_parents'])
    minword = construct(baseline, recipe['minimum_parents'])
    semantic_D(changed, baseline)
    semantic_D(minword, baseline)
    need({k:v for k,v in changed.items() if k != 'D'} == {k:v for k,v in baseline.items() if k != 'D'}, 'changed exterior')
    spec = importlib.util.spec_from_file_location('r420_pinned_xcheck', ROOT / 'research/e8-bit-r420/code/xcheck.py')
    xc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(xc)
    check = xc.Word(baseline)
    labels = check.labels()
    check.full()
    H, C, _ = check.interface()
    need(all(H.values()) and all(C.values()), 'baseline interface')
    check.w = changed
    check.full()
    H, C, _ = check.interface()
    need(not H['H2_D_frame0_targets_from_helpers'], 'literal H2 must reject new syntax')
    need(not C['K_equals_D'], 'literal K extractor must reject new syntax')
    need(all(v for k,v in H.items() if k != 'H2_D_frame0_targets_from_helpers'), 'other interface hypotheses')
    need(all(v for k,v in C.items() if k != 'K_equals_D'), 'other interface conclusions')
    rec0, rec1, recmin = [records(w, check.fdim) for w in (baseline, changed, minword)]
    need([r for r in rec0 if r[0] != 1] == [r for r in rec1 if r[0] != 1], 'paid movement/copy/erase subsequence changed')
    controls = []
    cyc = recipe['feasible_parents'][:]
    cyc[5] = 5
    controls.append(expect_rejection(lambda: traversal(cyc), 'cyclic parent'))
    badtree = [120]*120
    controls.append(expect_rejection(lambda: certify_mst(K, badtree), 'nonminimum tree'))
    preparation_count = sum(p != 120 for p in recipe['feasible_parents'])
    for label, index in [('missing preparation', 0), ('missing restoration', len(changed['D'])-1), ('missing correction', preparation_count)]:
        mutant = copy.deepcopy(changed)
        del mutant['D'][index]
        controls.append(expect_rejection(lambda: semantic_D(mutant, baseline), label))
    mutant = copy.deepcopy(changed)
    mutant['D'][0][0] = 1
    controls.append(expect_rejection(lambda: semantic_D(mutant, baseline), 'nonzero D frame'))
    mutant = copy.deepcopy(changed)
    mutant['D'][0][1] = 240
    controls.append(expect_rejection(lambda: semantic_D(mutant, baseline), 'helper write'))
    need(prefix_bounds(rec1)['payload_bits'] <= 104, 'feasible forest exceeds payload cap')
    controls.append(expect_rejection(lambda: need(prefix_bounds(recmin)['payload_bits'] <= 104, 'payload cap'), 'minimum-cost nominated tree exceeds payload cap'))
    neutral = copy.deepcopy(changed)
    neutral['D'][:0] = [[0, 120, [121]], [0, 120, [121]]]
    semantic_D(neutral, baseline)
    need(inventory(neutral, records(neutral, check.fdim))['ADDs'] == len([r for r in rec1 if r[0] == 1])+2, 'neutral pair must be paid')
    with tempfile.TemporaryDirectory(prefix='r420-forest-') as tmp:
        tmp = Path(tmp)
        exporter = ROOT / 'research/e8-bit-carrier-skeleton/code/bit/export_records.py'
        for label, word, expected in [('baseline', baseline, rec0), ('forest', changed, rec1)]:
            path = tmp / (label+'.json')
            path.write_text(json.dumps(word))
            out = tmp / label
            subprocess.run([sys.executable, '-I', '-B', str(exporter), str(path), str(out)], check=True, capture_output=True, text=True)
            actual = list(struct.iter_unpack('<6i', (out/'249-records.bin').read_bytes()))
            need(actual == expected, 'official record stream mismatch')
            independent_set_replay(actual)
        if args.native:
            spec = importlib.util.spec_from_file_location("forest_native", HERE / "native.py")
            native = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(native)
            native.run(ROOT, tmp, recmin)
    result = {'base_commit': '66849e1475c930fd7732b1a0067ffee7e1e95f60',
              'labels': labels, 'minimum_forest_certificate': optimum,
              'minimum_nominated_tree': inventory(minword, recmin),
              'baseline': inventory(baseline, rec0), 'feasible_forest': inventory(changed, rec1),
              'roots': sum(p == 120 for p in recipe['feasible_parents']),
              'preparation_XORs': sum(p != 120 for p in recipe['feasible_parents']),
              'columns_per_direction': 660, 'negative_controls': controls,
              'positive_control': 'F2-neutral target pair costs two ADDs',
              'interface': 'Semantic H2-prime; literal H2 and literal K extractor reject. All other H and C predicates pass.',
              'scope': 'Finite F2 circuit and exact rooted-forest cost optimum; feasible cut is not claimed precision-constrained optimal; no new kappa.'}
    certificate = HERE / 'CERTIFICATE.json'
    if args.write_certificate:
        certificate.write_text(json.dumps(result, indent=2)+'\n')
    else:
        need(json.loads(certificate.read_text()) == result, 'certificate mismatch')
    print('PASS_R420_TARGET_FOREST D=19922->15138 ADDs=26916->22132 saved=4784 forest_floor=14921 payload_bits=104 columns=660 controls=8 no_new_kappa')


if __name__ == '__main__':
    main()

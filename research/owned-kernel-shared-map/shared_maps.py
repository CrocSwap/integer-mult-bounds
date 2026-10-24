"""Optional discovery model: nonmonotone owned contacts and shared late G.

Cinna Davis / 1337isnot1337, substantial OpenAI Codex assistance; Apache-2.0.
Reuses the credited general Gaussian model without changing its source bytes.
Owned release follows the earlier prototype at8052b4818, reimplemented here.
"""
from collections import Counter, defaultdict
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIOR = ROOT / 'research/general-gaussian-contact-search'
SOURCE = ROOT / 'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    for row in json.loads((HERE / 'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            need(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'],
                 'Pinned live source: ' + row['path'])


authenticate()
spec = importlib.util.spec_from_file_location('owned_shared_prior_model', PRIOR / 'model.py')
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)
original_build = M.build


def minimum_rank(A, B, line=None):
    """min_G d(GA,B), optionally with G(a)=b; A/B are bitset subspaces."""
    k, l = M.dimension(A), M.dimension(B)
    if line is None:
        return abs(k - l)
    a, b = line
    sa, sb = (A >> a) & 1, (B >> b) & 1
    if k <= l:
        maximal_intersection = 0 <= sb - sa <= int(k < l)
    else:
        maximal_intersection = 0 <= sa - sb <= int(l < k)
    return abs(k - l) + (0 if maximal_intersection else 2)


def trace(payload, model):
    """Align chronological scalar and native nodes against the actual graph."""
    c = payload['canonical']
    cursor = 2 + len(c['start'])
    copies, centers, warps = [], [], []
    for i, e in enumerate(payload['programs']['forward']):
        if e[0] == 'scalar':
            need(model['nodes'][cursor] == e[2], 'Exact scalar node alignment')
            if e[1][0] == 'copy':
                need(e[1][1] == ['C', 0] and e[1][2][0] == 'L', 'Actual owned source')
                copies.append({'node': cursor, 'frame': e[2], 'role': e[1][2][1]})
            cursor += 1
        elif e[0] == 'warp':
            need(model['nodes'][cursor:cursor + 2] == e[3:5], 'Exact native node alignment')
            warps.append({'event': i, 'operator': e[2], 'input': cursor,
                          'output': cursor + 1, 'frames': e[3:5]})
            cursor += 2
        elif e[0] == 'center':
            centers.append(e)
    need(cursor + len(c['final']) == len(model['nodes']), 'Complete occurrence graph')
    need(len(copies) == len(centers) == 8, 'Eight separate owned lifetimes')
    for row, e in zip(copies, centers):
        need(e == ['center', 0, row['frame'], 0, 8], 'Actual descending rank-eight center')
    return copies, warps


def build(payload, forms):
    model = original_build(payload, forms)
    p0, h0 = M.invoice(model, [])
    copies, warps = trace(payload, model)
    frames = payload['canonical']['frames']
    frozen = set(model['fixed'])
    grouped = defaultdict(list)
    for w in warps:
        grouped[abs(w['operator'])].append(w)
    selected, lines = {}, {}
    for operator, occurrences in grouped.items():
        candidates = [w for w in occurrences if any(len(frames[f]) not in (0, 9) for f in w['frames'])]
        chosen = max(candidates, key=lambda w: len(frames[w['frames'][0]]))
        need(chosen['operator'] > 0, 'Positive selected late native occurrence')
        selected[chosen['input'], chosen['output']] = operator
        others = [w for w in candidates if w is not chosen]
        if others:
            pairs = {(w['frames'][0], w['frames'][1]) if w['operator'] > 0
                     else (w['frames'][1], w['frames'][0]) for w in others}
            need(len(pairs) == 1, 'One preserved shared prelude line pair')
            a, b = next(iter(pairs))
            need(len(frames[a]) == len(frames[b]) == 1, 'Actual fixed prelude line')
            lines[operator] = frames[a][0], frames[b][0]
        for w in occurrences:
            if w is not chosen:
                frozen.update((w['input'], w['output']))
    need(len(selected) == 72 and len(lines) == 12, 'All72 shared late maps and12 prelude constraints')
    changed = 0
    new_edges = []
    for kind, a, b, ranks in model['edges']:
        if kind == 'warp' and (a, b) in selected:
            operator = selected[a, b]
            fa, fb = model['nodes'][a], model['nodes'][b]
            A = [model['old_spaces'][fa], model['new_spaces'][fa]]
            B = [model['old_spaces'][fb], model['new_spaces'][fb]]
            fresh = [minimum_rank(A[i], B[j], lines.get(operator))
                     for i, j in ((0, 0), (1, 0), (0, 1), (1, 1))]
            need(fresh[0] == 0 and all(x <= y for x, y in zip(fresh, ranks)),
                 'Incumbent feasible in shared-map relaxation')
            changed += fresh != ranks
            ranks = fresh
        new_edges.append((kind, a, b, ranks))
    model['edges'] = new_edges
    model['centers'] = {}
    for row in copies:
        n, f = row['node'], row['frame']
        need(n in frozen, 'Owned COPY starts frozen')
        frozen.remove(n)
        sink = len(model['nodes'])
        model['nodes'].append(0)
        frozen.add(sink)
        old = M.dimension(model['old_spaces'][f])
        new = M.dimension(model['new_spaces'][f])
        # The solver prices every paid table by full r^t. In particular a
        # variable center must not use a rank-subtracted bridge price.
        model['edges'].append(('center', n, sink, [old, new, old, new]))
    model['fixed'] = sorted(frozen)
    model['shared_late_maps'] = selected
    model['prelude_lines'] = lines
    model['owned_copies'] = copies
    model['changed_native_tables'] = changed
    p, h = M.invoice(model, [])
    need(p == p0 == Counter({1: 2201, 2: 412, 3: 510, 4: 127, 5: 40, 8: 8}), 'Whole baseline paid profile')
    need(h == h0 == Counter({4: 28, 7: 7, 8: 47, 9: 326}), 'All408 independent productive helpers')
    return model


def payload():
    return json.loads(gzip.decompress(SOURCE.read_bytes()))

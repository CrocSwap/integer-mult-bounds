#!/usr/bin/env python3
"""Source witnesses for gatewise coherent-frame additivity; no new kappa.

Cinna Davis, with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter, defaultdict, deque
from fractions import Fraction as F
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'
SOURCE_SHA = '7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05'


class Rejected(ValueError):
    pass


def need(ok, reason):
    if not ok:
        raise Rejected(reason)


def power_two(x):
    return type(x) is int and x > 0 and x & (x - 1) == 0


def coefficient(g):
    need(type(g[-2]) is int and type(g[-1]) is int and g[-1] != 0,
         'rational coefficient')
    return F(g[-2], g[-1])


def unit_dyadic(c):
    return power_two(abs(c.numerator)) and power_two(c.denominator)


def graph_counts(edges):
    parent = {}

    def find(v):
        parent.setdefault(v, v)
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v

    tree, chords = [], []
    for event, a, b in edges:
        ra, rb = find(a), find(b)
        if ra == rb:
            chords.append(event)
        else:
            parent[ra] = rb
            tree.append(event)
    components = len({find(v) for v in parent})
    simple = {tuple(sorted((a, b))) for _, a, b in edges}
    # Independent component/rank count by breadth-first search.
    adjacency = defaultdict(set)
    for a, b in simple:
        adjacency[a].add(b); adjacency[b].add(a)
    unseen = set(adjacency)
    bfs_components = 0
    while unseen:
        bfs_components += 1
        queue = deque([unseen.pop()])
        while queue:
            for v in adjacency[queue.popleft()]:
                if v in unseen:
                    unseen.remove(v); queue.append(v)
    need(bfs_components == components, 'independent component count')
    need(len(tree) == len(parent) - components, 'spanning forest size')
    need(len(chords) == len(edges) - len(parent) + components, 'fundamental cycle count')
    return {'vertices': len(parent), 'components': components,
            'paid_occurrences': len(edges), 'simple_edges': len(simple),
            'occurrence_cycle_rank': len(chords),
            'simple_cycle_rank': len(simple) - len(parent) + components,
            'forest_event_ids': tree, 'chord_event_ids': chords}


def census(src, orientation):
    canonical = src['canonical']
    frames = canonical['frames']
    p = src['programs'][orientation]
    now = {('L', i): f for i, f in enumerate(canonical['start'])}
    used, witnesses, paid = set(), {}, []
    scalar_counts, paid_counts = Counter(), Counter()
    macros, macro, macro_open = [], [], False

    def frame(f):
        need(type(f) is int and 0 <= f < len(frames), 'valid frame id')
        used.add(f)

    def role(r):
        need(isinstance(r, list) and len(r) == 2 and type(r[1]) is int, 'role shape')
        need((r[0] == 'L' and 0 <= r[1] < len(canonical['start'])) or
             r == ['C', 0], 'declared role')
        return tuple(r)

    for i, e in enumerate(p):
        k = e[0]
        if k == 'scalar':
            g, f = e[1:]
            frame(f)
            op = g[0]; scalar_counts[op] += 1
            d = role(g[1])
            if op == 'clear':
                need(d == ('C', 0), 'only owned center is cleared')
                if not macro_open:
                    macro_open, macro = True, [i]
                else:
                    macro.append(i); macros.append(macro)
                    macro_open, macro = False, []
                now[d] = f
                continue
            if op == 'copy':
                s = role(g[2])
                need(d == ('C', 0) and now.get(s) == f, 'center COPY input frame')
                now[d] = f
            elif op == 'add':
                s, c = role(g[2]), coefficient(g)
                need(d != s and c != 0, 'nonzero distinct-register ADD')
                need(now.get(d) == now.get(s) == f, 'ADD frame chronology')
                if d[0] == s[0] == 'L' and unit_dyadic(c):
                    need(not macro_open, 'persistent witness outside owned macro')
                    witnesses.setdefault(f, {'frame': f, 'dimension': len(frames[f]),
                                            'event': i, 'record': e,
                                            'coefficient': [c.numerator, c.denominator]})
            elif op == 'scale':
                c = coefficient(g)
                need(d[0] == 'L' and now.get(d) == f and unit_dyadic(c),
                     'invertible dyadic persistent SCALE')
            else:
                raise Rejected('unknown scalar operation')
        elif k == 'climb':
            _, tag, a, old, new, rank = e
            frame(old); frame(new)
            need(tag == 'warp_retimed' and now.get(('L', a)) == old, 'paid entrance frame')
            need(type(rank) is int and len(frames[new]) - len(frames[old]) == rank > 0,
                 'paid rank increment')
            now[('L', a)] = new
            paid.append((i, old, new)); paid_counts[rank] += 1
        elif k == 'center':
            _, a, old, new, rank = e
            frame(old); frame(new)
            need(macro_open and a == 0 and now.get(('C', a)) == old, 'owned center entrance')
            need(type(rank) is int and abs(len(frames[new]) - len(frames[old])) == rank,
                 'owned center rank')
            now[('C', a)] = new
            paid.append((i, old, new)); paid_counts[rank] += 1
        elif k == 'warp':
            _, r, op, old, new = e
            frame(old); frame(new)
            a = role(r)
            need(type(op) is int and op != 0 and abs(op) <= len(canonical['warps']),
                 'declared warp id')
            need(now.get(a) == old and len(frames[old]) == len(frames[new]),
                 'warp frame chronology')
            now[a] = new
        else:
            need(k in ('phase', 'adapter'), 'supported event kind')
        if macro_open:
            macro.append(i)
    need(not macro_open and len(macros) == 8, 'eight closed owned macros')
    need([now[('L', a)] for a in range(len(canonical['start']))] == canonical['final'],
         'persistent endpoint frames')
    need(set(witnesses) == used, 'every active frame has a unit persistent ADD witness')
    for ids in macros:
        block = [p[i] for i in ids]
        need(len(block) == 26 and sum(e[0] == 'center' for e in block) == 1, 'owned macro shape')
        captures, destinations = set(), set()
        for e in block:
            if e[0] != 'scalar' or e[1][0] == 'clear':
                continue
            g = e[1]
            if g[1] == ['C', 0]:
                need(g[0] in ('add', 'copy') and g[2][0] == 'L', 'center capture')
                captures.add(g[2][1])
            else:
                need(g[0] == 'add' and g[2] == ['C', 0], 'center fanout')
                destinations.add(g[1][1])
        need(captures and destinations and not captures & destinations,
             'capture sources disjoint from destinations')
    need(dict(sorted(paid_counts.items())) ==
         {int(k): v for k, v in canonical['local_profile'].items()}, 'paid profile binding')
    return {'source_events': len(p), 'active_frames': len(used),
            'persistent_roles': len(canonical['start']), 'owned_macros': len(macros),
            'scalar_counts': dict(sorted(scalar_counts.items())),
            'frame_dimension_histogram': dict(sorted(Counter(len(frames[f]) for f in used).items())),
            'witnesses': [witnesses[f] for f in sorted(witnesses)], 'paid_graph': graph_counts(paid)}


def plus(x, y):
    return tuple(a + b for a, b in zip(x, y))


def times(c, x):
    return tuple(c * a for a in x)


def commute(A, c, x, y):
    return A(plus(x, times(c, y))) == plus(A(x), times(c, A(y)))


def rounded_shear(v, inverse=False):
    x, y = v
    increment = y // 2
    return (x - increment if inverse else x + increment, y)


def radial(v):
    return times(sum(x*x for x in v), v)


def mathematical_checks():
    points = [(F(a, 2), F(b, 2)) for a in range(-3, 4) for b in range(-3, 4)]
    coeffs = [F(1), F(-1), F(1, 2), F(-1, 4), F(2)]
    linear = lambda v: (v[0] + 2*v[1], v[0] + 3*v[1])
    checked = 0
    for x in points:
        need(rounded_shear(rounded_shear(x), True) == x, 'rounded forward/inverse')
        need(rounded_shear(rounded_shear(x, True)) == x, 'rounded inverse/forward')
        for y in points:
            for c in coeffs:
                need(commute(linear, c, x, y), 'linear ADD positive control')
                checked += 1
    x = (F(0), F(1))
    need(not commute(rounded_shear, F(1), x, x), 'nonlinear rounded ADD counterexample')
    u = (F(1), F(0))
    need(not commute(radial, F(1), u, u), 'radial ADD counterexample')
    unitary_checks = 0
    for a, b in [(F(0), F(1)), (F(3, 5), F(4, 5)), (F(5, 13), F(12, 13))]:
        W = lambda v: (a*v[0] - b*v[1], b*v[0] + a*v[1])
        for v in points:
            need(radial(W(v)) == W(radial(v)), 'radial unitary equivariance')
            unitary_checks += 1
    S = lambda v: (v[0] + v[1], v[1])
    Sinv = lambda v: (v[0] - v[1], v[1])
    need(all(Sinv(S(v)) == S(Sinv(v)) == v for v in points), 'edge inverse pairs')
    need(S(x) != x, 'nontrivial triangle holonomy')
    return {'linear_gate_cases': checked, 'rounded_two_sided_round_trips': 2*len(points),
            'radial_unitary_cases': unitary_checks,
            'rounded_counterexample': {'x': [0, 1], 'y': [0, 1], 'coefficient': 1,
                                       'left': [1, 2], 'right': [0, 2]},
            'radial_counterexample': {'x': [1, 0], 'y': [1, 0], 'coefficient': 1,
                                      'left': [8, 0], 'right': [2, 0]}}


def controls(src):
    tests = []

    def reject(name, change, expected):
        altered = json.loads(json.dumps(src)); change(altered)
        try:
            census(altered, 'forward')
        except Rejected as e:
            need(str(e) == expected, 'specified rejection: ' + name + ': ' + str(e))
            tests.append(name)
        else:
            raise Rejected('mutation accepted: ' + name)

    event = census(src, 'forward')['witnesses'][0]['event']
    def gate(s):
        return s['programs']['forward'][event][1]
    reject('self_add', lambda s: gate(s).__setitem__(2, gate(s)[1]),
           'nonzero distinct-register ADD')
    reject('zero_coefficient', lambda s: gate(s).__setitem__(3, 0),
           'nonzero distinct-register ADD')
    reject('boolean_coefficient', lambda s: gate(s).__setitem__(3, True), 'rational coefficient')
    reject('wrong_frame', lambda s: s['programs']['forward'][event].__setitem__(2, 1),
           'ADD frame chronology')
    return tests


def result(raw):
    need(hashlib.sha256(raw).hexdigest() == SOURCE_SHA, 'source bytes')
    src = json.loads(gzip.decompress(raw))
    need(set(src['programs']) == {'forward', 'backward'}, 'two source orientations')
    return {'schema_version': 1, 'claim': 'gatewise_frame_additivity_no_new_kappa',
            'source': SOURCE, 'source_sha256': SOURCE_SHA,
            'orientations': {o: census(src, o) for o in ('forward', 'backward')},
            'mathematical_checks': mathematical_checks(), 'rejection_controls': controls(src)}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write-result', type=Path)
    args = ap.parse_args()
    raw = (ROOT / SOURCE).read_bytes(); actual = result(raw)
    vendor = json.loads((HERE / 'VENDORED.json').read_text())['files'][0]
    context = (HERE / vendor['path']).read_bytes()
    need(hashlib.sha256(context).hexdigest() == vendor['sha256'], 'predecessor context bytes')
    blob = hashlib.sha1(b'blob ' + str(len(context)).encode() + b'\0' + context).hexdigest()
    need(blob == vendor['source_blob'], 'predecessor context Git blob')
    actual['predecessor_context'] = vendor
    certificate = {}
    for orientation, data in actual['orientations'].items():
        certificate[orientation] = {'witnesses': data.pop('witnesses')}
        for key in ('forest_event_ids', 'chord_event_ids'):
            certificate[orientation][key] = data['paid_graph'].pop(key)
    payload = (json.dumps(certificate, sort_keys=True, separators=(',', ':')) + '\n').encode()
    actual['certificate'] = {'path': 'CERTIFICATE.json.gz',
                             'canonical_payload_sha256': hashlib.sha256(payload).hexdigest()}
    try:
        result(raw + b'changed')
    except Rejected as e:
        need(str(e) == 'source bytes', 'source-byte rejection reason')
    else:
        raise Rejected('changed source accepted')
    if args.write_result:
        with args.write_result.with_name('CERTIFICATE.json.gz').open('xb') as stream:
            stream.write(gzip.compress(payload, mtime=0))
        with args.write_result.open('x') as stream:
            json.dump(actual, stream, indent=2, sort_keys=True); stream.write('\n')
    else:
        need(gzip.decompress((HERE / 'CERTIFICATE.json.gz').read_bytes()) == payload,
             'canonical certificate payload equality')
        expected = json.loads((HERE / 'RESULT.json').read_text())
        need(json.loads(json.dumps(actual)) == expected, 'committed result equality')
    print('PASS_COHERENT_FRAME_ADDITIVITY frames_per_orientation=1002 '
          'paid_cycle_rank=2297 controls=5 no_new_kappa')


if __name__ == '__main__':
    main()

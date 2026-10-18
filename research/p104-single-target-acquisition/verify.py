"""Exact all-episode antichains and complete dirty words, no search imports.

Prepared for commdata2338 with substantial OpenAI Codex assistance. Apache-2.0.
The acquisition argument and dirt compensation extend PR2393/PR2496.
"""
import argparse
from collections import Counter, defaultdict
import copy
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import subprocess
import sys
import tempfile

P = Path(__file__).resolve().parent
ROOT = P.parents[1]


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def load(path):
    def unique(items):
        result = {}
        for k, v in items:
            need(k not in result, 'duplicate JSON key')
            result[k] = v
        return result
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique)


@lru_cache(None)
def echelon(vectors):
    b = {}
    for x in vectors:
        need(type(x) is int and 0 < x < 512, 'binary frame vector')
        for p in sorted(b, reverse=True):
            if x >> p & 1:
                x ^= b[p]
        need(x != 0, 'independent frame basis')
        p = x.bit_length() - 1
        for q in b:
            if b[q] >> p & 1:
                b[q] ^= x
        b[p] = x
    return tuple(b[p] for p in sorted(b, reverse=True))


def frame(vectors):
    need(isinstance(vectors, (list, tuple)), 'frame list')
    return echelon(tuple(vectors))


@lru_cache(None)
def contained(a, b):
    for x in a:
        for y in b:
            if x >> (y.bit_length() - 1) & 1:
                x ^= y
        if x:
            return False
    return True


FULL = frame([1 << i for i in range(9)])


def inputs():
    for item in load(P / 'SOURCES.json')['files']:
        if item['usage'] == 'input':
            need(hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest()
                 == item['sha256'], 'source pin: ' + item['path'])
    ip = ROOT / 'research/p104-native-channel/inputs'
    w = load(ip / 'LOWRANK-WITNESS.json')
    fixture = load(ip / 'P104-FIXTURE.json')['section4_explicit_P104']
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            r = [0] * 8
            r[i], r[j] = 2, 2 * sign
            roots.add(tuple(r))
    roots.update((1, *tail) for tail in product((-1, 1), repeat=7)
                 if tail.count(-1) % 2 == 0)
    need(len(roots) == 120, '120 E8 root lines')
    removed = set(map(tuple, fixture['F0'] + fixture['C']))
    need(len(removed) == 16 and removed <= roots, 'two puncture frames')
    roots = sorted(roots - removed)
    gram_half = [[Q(sum(x*y for x, y in zip(a, b)), 8)
                  for b in roots] for a in roots]
    return w, gram_half


def chronology(w):
    need(len(w['program']) == 4058 and len(w['initial_frames']) == 280,
         'original word dimensions')
    current = {r: frame(f) for r, f in w['initial_frames'].items()}
    episodes = {s: [[0, None, current[f'X{s}']]] for s in range(104)}
    for s in range(104):
        need(len(current[f'X{s}']) == 1 and current[f'Y{s}'] == (), 'data entrance')
    for i, e in enumerate(w['program']):
        if e[0] == 'transport' and e[1][0] in 'XY':
            r, a, b = e[1], frame(e[2]), frame(e[3])
            need(current[r] == a and a != b and contained(a, b), 'monotone data path')
            current[r] = b
            if r.startswith('X'):
                s = int(r[1:])
                episodes[s][-1][1] = i
                episodes[s].append([i+1, None, b])
        if e[0] in ('add', 'copy'):
            need(not e[1].startswith('X') and not e[2].startswith('Y'),
                 'immutable X and unread Y')
        if e[0] in ('zero', 'erase'):
            need(e[1] == 'C', 'private lifetime only')
    for s in range(104):
        episodes[s][-1][1] = len(w['program'])
        need(current[f'X{s}'] == frame(w['final_frames'][f'X{s}']) == FULL,
             'completed source frame')
        need(current[f'Y{s}'] == frame(w['final_frames'][f'Y{s}'])
             and len(current[f'Y{s}']) == 8, 'target endpoint hyperplane')
    return episodes


def coefficients(t, gram_half):
    return {s: Q(s == t) - x for s, x in enumerate(gram_half[t])
            if Q(s == t) != x}


def check_certificate(row, w, gram_half, episodes):
    t = row['target']
    need(type(t) is int and 0 <= t < 104, 'target index')
    c = coefficients(t, gram_half)
    need(len(c) == 48, '48 correction entries')
    h = frame(w['final_frames'][f'Y{t}'])
    allowed = {s: [e for e in episodes[s] if contained(e[2], h)] for s in c}
    need(all(allowed.values()), 'source access')
    anti = row['antichain_sources']
    need(all(type(s) is int and s in c for s in anti)
         and len(set(anti)) == len(anti), 'required distinct antichain sources')
    pairs = 0
    for s, r in combinations(anti, 2):
        for a in allowed[s]:
            for b in allowed[r]:
                need(not contained(a[2], b[2]) and not contained(b[2], a[2]),
                     'all-episode incomparability')
                pairs += 1
    seen = []
    for path in row['paths']:
        need(path, 'nonempty acquisition lifetime')
        old, time = (), 0
        for s, cut, raw in path:
            need(type(s) is int and s in c and type(cut) is int, 'capture types')
            f = frame(raw)
            need(cut >= time and contained(old, f), 'monotone chronological capture path')
            need(any(lo <= cut <= hi and f == sf for lo, hi, sf in allowed[s]),
                 'actual contained source-frame episode')
            seen.append(s)
            old, time = f, cut
    need(sorted(seen) == sorted(c), 'complete one-capture source partition')
    need(type(row['lower_bound']) is int and type(row['upper_bound']) is int
         and row['lower_bound'] == len(anti) == len(row['paths']) == row['upper_bound'],
         'matched lower and upper certificates')
    return pairs


def word(row, w, gram_half):
    """Expand the compact witness into literal insertions at original cuts."""
    t = row['target']
    target = f'Y{t}'
    h = w['final_frames'][target]
    c = coefficients(t, gram_half)
    ins = defaultdict(list)
    full = list(FULL)
    last = len(w['program'])
    for i, path in enumerate(row['paths']):
        helper, old = f'L{i}', []
        ins[0].append(['add', target, helper, '-1', []])
        for s, cut, f in path:
            if frame(old) != frame(f):
                ins[cut].append(['transport', helper, old, f, len(f)-len(old)])
            ins[cut].append(['add', helper, f'X{s}', str(c[s]), f])
            old = f
        if frame(old) != frame(h):
            ins[last].append(['transport', helper, old, h, len(h)-len(old)])
        ins[last].append(['add', target, helper, '1', h])
        ins[last].append(['transport', helper, h, full, 1])
        for s, _, _ in path:
            ins[last].append(['add', helper, f'X{s}', str(-c[s]), full])
    return dict(ins)


def replay(row, ins, w, gram_half):
    t, n = row['target'], len(row['paths'])
    new = [f'L{i}' for i in range(n)]
    names = list(w['initial_frames']) + new
    need(len(set(names)) == 280+n, 'independent dirty inputs')
    states = {r: {r: Q(1)} for r in names}
    frames = {r: frame(f) for r, f in w['initial_frames'].items()} | {r: () for r in new}
    initial = set(new)
    paid, added, counts = Counter(), Counter(), Counter()
    need(all(type(cut) is int and 0 <= cut <= len(w['program']) for cut in ins), 'insertion cuts')
    for cut in range(len(w['program'])+1):
        events = [(e, True) for e in ins.get(cut, [])]
        if cut < len(w['program']):
            events.append((w['program'][cut], False))
        for e, is_new in events:
            op, r = e[:2]
            counts['full_events'] += 1
            if is_new:
                need(op in ('add', 'transport'), 'no new allocation or disposal')
                counts['added_' + op] += 1
            if op == 'transport':
                _, _, a, b, rank = e
                a, b = frame(a), frame(b)
                need(frames[r] == a and a != b and (contained(a, b) or contained(b, a)),
                     'nested literal transport')
                need(type(rank) is int and rank == abs(len(a)-len(b)), 'paid dimension gap')
                if is_new:
                    need(r in initial and contained(a, b), 'monotone new helper')
                    added[rank] += 1
                paid[rank] += 1
                frames[r] = b
            elif op == 'add':
                _, _, s, coefficient, f = e
                need(r != s and frames[r] == frames[s] == frame(f), 'same-frame ADD')
                if is_new:
                    need((r == f'Y{t}' and s in initial) or
                         (r in initial and s.startswith('X')), 'declared X-only upper word')
                q = Q(coefficient)
                for key, value in states[s].items():
                    states[r][key] = states[r].get(key, Q(0)) + q*value
                    if not states[r][key]:
                        del states[r][key]
            elif op == 'zero':
                need(r == 'C' and r not in states, 'private allocation')
                states[r], frames[r] = {}, frame(e[2])
            elif op == 'copy':
                need(r == 'C' and not states[r] and frames[r] == frames[e[2]] == frame(e[3]),
                     'private copy into zero')
                states[r] = states[e[2]].copy()
            elif op == 'erase':
                need(r == 'C' and frames[r] == frame(e[2]), 'inherited private discard')
                del frames[r], states[r]
            else:
                raise ValueError('unknown opcode')
    need(set(states) == set(names), 'private lifetimes closed')
    for r in names:
        expected = {r: Q(1)}
        if r.startswith('Y'):
            j = int(r[1:])
            if j == t:
                expected[f'X{t}'] = Q(1)
            else:
                expected.update({f'X{s}': q for s, q in enumerate(gram_half[j]) if q})
        need(states[r] == expected, 'all-column endpoint: ' + r)
        need(frames[r] == (FULL if r in initial else frame(w['final_frames'][r])),
             'prescribed final frame')
    mass = sum(rank*count for rank, count in added.items())
    need(mass == 9*n, 'ZERO-to-FULL telescoping bill')
    need(counts['added_add'] == 96+2*n, 'complete ADD invoice')
    need(dict(paid-added) == {1:1074, 2:58, 3:86, 4:104, 5:48, 6:24, 7:8, 8:8},
         'unchanged channel profile')
    return {'target': t, 'minimum_lifetimes': n, 'columns': len(names),
            'endpoint_coefficients': len(names)**2, 'added_rank_mass': mass,
            'added_profile': {str(k):v for k,v in sorted(added.items())}, **counts}


def controls(rows, w, gram_half, episodes):
    results = []
    reasons = {
        'duplicate_lower_witness': 'required distinct antichain sources',
        'comparable_allowed_frames': 'all-episode incomparability',
        'premature_late_capture': 'actual contained source-frame episode',
        'omitted_required_capture': 'complete one-capture source partition',
        'missing_dirt_compensation': 'all-column endpoint',
        'wrong_capture_sign': 'all-column endpoint',
        'missing_dirty_cleanup': 'all-column endpoint',
        'undercharged_transport': 'paid dimension gap',
    }
    def rejects(name, fn):
        try:
            fn()
        except ValueError as error:
            need(reasons[name] in str(error), 'wrong rejection reason: ' + name + ': ' + str(error))
            results.append(name)
        else:
            raise ValueError('control accepted: ' + name)
    r = copy.deepcopy(rows[2])
    r['antichain_sources'][1] = r['antichain_sources'][0]
    rejects('duplicate_lower_witness', lambda: check_certificate(r, w, gram_half, episodes))
    r = copy.deepcopy(rows[2])
    r['antichain_sources'] = [0, 20]
    r['lower_bound'] = 2
    rejects('comparable_allowed_frames', lambda: check_certificate(r, w, gram_half, episodes))
    r = copy.deepcopy(rows[2])
    late = next(v for p in r['paths'] for v in p if v[1] > 0)
    late[1] = 0
    rejects('premature_late_capture', lambda: check_certificate(r, w, gram_half, episodes))
    r = copy.deepcopy(rows[2])
    r['paths'][0].pop()
    rejects('omitted_required_capture', lambda: check_certificate(r, w, gram_half, episodes))
    row = rows[53]
    good = word(row, w, gram_half)
    mutations = [
        ('missing_dirt_compensation', lambda x: x[0].pop(0)),
        ('wrong_capture_sign', lambda x: next(e for b in x.values() for e in b
            if e[0] == 'add' and e[1].startswith('L')).__setitem__(3, '0')),
        ('missing_dirty_cleanup', lambda x: x[len(w['program'])].pop()),
        ('undercharged_transport', lambda x: next(e for b in x.values() for e in b
            if e[0] == 'transport').__setitem__(4, 0)),
    ]
    for name, mutate in mutations:
        bad = copy.deepcopy(good)
        mutate(bad)
        rejects(name, lambda: replay(row, bad, w, gram_half))
    equivalent = copy.deepcopy(good)
    for events in equivalent.values():
        for e in events:
            if e[0] == 'add':
                e[4] = list(reversed(e[4]))
            elif e[0] == 'transport':
                e[2] = list(reversed(e[2]))
                e[3] = list(reversed(e[3]))
    need(replay(row, equivalent, w, gram_half) == replay(row, good, w, gram_half),
         'equivalent basis positive control')
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write-result', action='store_true')
    ap.add_argument('--regenerate', action='store_true')
    ap.add_argument('--emit-target', type=int)
    ap.add_argument('--out', type=Path)
    args = ap.parse_args()
    w, gram_half = inputs()
    episodes = chronology(w)
    cert = load(P / 'CERTIFICATE.json')
    need(type(cert['schema_version']) is int and cert['schema_version'] == 1, 'certificate schema')
    rows = cert['targets']
    need([r['target'] for r in rows] == list(range(104)), 'all 104 targets exactly once')
    pairs = sum(check_certificate(r, w, gram_half, episodes) for r in rows)
    if args.emit_target is not None:
        need(0 <= args.emit_target < 104 and args.out is not None, 'emit target/output')
        r = rows[args.emit_target]
        payload = {'target': r['target'], 'new_helpers': len(r['paths']),
                   'insertions': [{'completed_cut': cut, 'events': events}
                                  for cut, events in sorted(word(r, w, gram_half).items())]}
        with args.out.open('x', encoding='utf-8') as f:
            json.dump(payload, f, indent=2)
            f.write('\n')
        print('EMITTED_P104_TARGET_WORD', r['target'])
        return
    need(args.out is None, '--out requires --emit-target')
    results = [replay(r, word(r, w, gram_half), w, gram_half) for r in rows]
    rejects = controls(rows, w, gram_half, episodes)
    distribution = Counter(r['minimum_lifetimes'] for r in results)
    result = {'status':'PASS_P104_SINGLE_TARGET_ACQUISITION',
              'distribution':{str(k):v for k,v in sorted(distribution.items())},
              'all_episode_frame_pair_checks':pairs,
              'total_endpoint_coefficients':sum(r['endpoint_coefficients'] for r in results),
              'rejecting_controls':rejects, 'targets':results,
              'scope':'Separate single-target minima; no additive lower bound under sharing; no new kappa.'}
    if args.regenerate:
        with tempfile.TemporaryDirectory(prefix='p104-acquisition-') as d:
            out = Path(d) / 'certificate.json'
            subprocess.run([sys.executable, '-I', '-B', str(P/'build.py'), '--out', str(out)], check=True)
            need(load(out) == cert, 'complete certificate regeneration')
    if args.write_result:
        with (P/'RESULT.json').open('x', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
            f.write('\n')
    else:
        need(json.dumps(load(P/'RESULT.json'), sort_keys=True) == json.dumps(result, sort_keys=True),
             'typed complete result equality')
    print('PASS_P104_SINGLE_TARGET_ACQUISITION targets=104 min=37 max=48 '
          'matched=104 controls=8 no_new_kappa')


if __name__ == '__main__':
    main()

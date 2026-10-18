"""Independent sparse replay and exact read-frame antichain, no producer imports."""
import argparse
from collections import Counter
import copy
from fractions import Fraction as Q
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import subprocess
import sys
import tempfile

P = Path(__file__).resolve().parent
ROOT = P.parents[1]


def need(ok, why):
    if not ok:
        raise ValueError(why)


def load(path):
    def pairs(items):
        out = {}
        for k, v in items:
            need(k not in out, 'duplicate JSON key')
            out[k] = v
        return out
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=pairs)


def space(vs):
    need(isinstance(vs, list) and all(type(v) is int and 0 < v < 512 for v in vs), 'binary frame type')
    out = {0}
    for v in vs:
        out |= {x ^ v for x in tuple(out)}
    need(len(out) == 2**len(vs), 'frame basis independence')
    return frozenset(out)


def inputs():
    sources = load(P/'SOURCES.json')
    for item in sources['files']:
        if item.get('usage') == 'input':
            need(hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest() == item['sha256'], 'source pin '+item['path'])
    ip = ROOT/'research/p104-native-channel/inputs'
    w = load(ip/'LOWRANK-WITNESS.json')
    f = load(ip/'P104-FIXTURE.json')['section4_explicit_P104']
    rr = set()
    for i, j in combinations(range(8), 2):
        for s in (-1, 1):
            r = [0]*8
            r[i], r[j] = 2, 2*s
            rr.add(tuple(r))
    for tail in product((-1, 1), repeat=7):
        if tail.count(-1) % 2 == 0:
            rr.add((1, *tail))
    need(len(rr) == 120, 'E8 root lines')
    rr = sorted(rr - set(map(tuple, f['F0']+f['C'])))
    need(len(rr) == 104, 'P104 puncture')
    gram = [[Q(sum(a*b for a, b in zip(r, s)), 4) for s in rr] for r in rr]
    return w, gram


def access_proof(w, gram):
    h = space(w['final_frames']['Y2'])
    target_frame = space(w['initial_frames']['Y2'])
    required = [s for s in range(104) if Q(s == 2)-gram[2][s]/2]
    frames = {s: w['initial_frames'][f'X{s}'] for s in required}
    paths = {s: [[0, None, frames[s]]] for s in required}
    for i, e in enumerate(w['program']):
        if e[0] == 'transport' and e[1] == 'Y2':
            need(target_frame == space(e[2]) and target_frame < space(e[3]) <= h,
                 'monotone target inside its endpoint')
            target_frame = space(e[3])
        if e[0] == 'transport' and e[1].startswith('X') and int(e[1][1:]) in paths:
            s = int(e[1][1:])
            need(space(frames[s]) == space(e[2]), 'source path adjacency')
            need(space(e[2]) < space(e[3]), 'monotone original source')
            paths[s][-1][1] = i
            paths[s].append([i+1, None, e[3]])
            frames[s] = e[3]
        if e[0] in ('add', 'copy'):
            need(not e[1].startswith('X'), 'immutable original sources')
            need(e[2] != 'Y2', 'original word does not read corrected target')
    for p in paths.values():
        p[-1][1] = len(w['program'])
    allowed = {s: [x for x in p if space(x[2]) <= h] for s, p in paths.items()}
    forced = sorted(s for s, p in allowed.items() if len(p) == 1 and len(p[0][2]) == 1)
    witness = forced+[3, 6, 15]
    need(len(required) == 48 and len(forced) == 36 and len(set(witness)) == 39, 'read-antichain size')
    for a, b in combinations(witness, 2):
        need(all(not (space(x[2]) <= space(y[2]) or space(y[2]) <= space(x[2]))
                 for x in allowed[a] for y in allowed[b]), 'pairwise incomparable allowable source frames')
    need(all(allowed[s] for s in required), 'every required source has access')
    return {'required_sources': required, 'forced_initial_sources': forced,
            'antichain_sources': witness,
            'exceptional_paths': {str(s): allowed[s] for s in required if s not in forced},
            'pairwise_source_checks': len(witness)*(len(witness)-1)//2}


def replay(w, gram, c):
    need(c['schema_version'] == 1 and c['targets'] == [2], 'circuit schema/target')
    new = c['initial_frames']
    need(set(new) == {f'L{i}' for i in range(39)}, '39 distinct arbitrary dirty lifetimes')
    need(all(f == [] for f in new.values()), 'ZERO entry frames')
    full = frozenset(range(512))
    need(set(c['final_frames']) == set(new) and all(space(f) == full for f in c['final_frames'].values()), 'FULL exit frames')
    names = list(w['initial_frames'])+list(new)
    need(len(names) == len(set(names)) == 319, 'independent input names')
    frames = {r: space(f) for r, f in (w['initial_frames'] | new).items()}
    state = {r: {r: Q(1)} for r in names}
    ins = {}
    for block in c['insertions']:
        cut = block['completed_cut']
        need(type(cut) is int and 0 <= cut <= len(w['program']) and cut not in ins, 'chronological insertion cut')
        ins[cut] = block['events']
    paid, addpaid, counts = Counter(), Counter(), Counter()
    actual_captures = []
    for cut in range(len(w['program'])+1):
        todo = [(e, True) for e in ins.get(cut, [])]
        if cut < len(w['program']):
            todo.append((w['program'][cut], False))
        for e, added in todo:
            op = e[0]
            counts['all_events'] += 1
            if added:
                counts['added_events'] += 1
                need(op in ('transport', 'add'), 'no added allocation/disposal')
            if op == 'transport':
                _, r, old, newf, rank = e
                A, B = space(old), space(newf)
                need(frames[r] == A and (A < B or B < A), 'literal nested source/target frames')
                need(type(rank) is int and rank == abs(len(newf)-len(old)), 'dimension-gap invoice')
                if added:
                    need(r in new and A < B, 'only new helpers move monotonically')
                    addpaid[rank] += 1
                frames[r] = B
                paid[rank] += 1
            elif op == 'zero':
                _, r, f = e
                need(r == 'C' and r not in state, 'original private allocation')
                frames[r], state[r] = space(f), {}
            elif op == 'erase':
                _, r, f = e
                need(r == 'C' and frames[r] == space(f), 'original private discard')
                del frames[r], state[r]
            elif op == 'copy':
                _, r, s, f = e
                need(not state[r] and frames[r] == frames[s] == space(f), 'original private copy')
                state[r] = state[s].copy()
            else:
                need(op == 'add', 'event opcode')
                _, r, s, value, f = e
                need(r != s and frames[r] == frames[s] == space(f), 'common-chart ADD')
                q = Q(value)
                if added:
                    counts['added_ADD'] += 1
                    need((r == 'Y2' and s in new) or (r in new and s.startswith('X')), 'X-only acquisitions and additive target')
                    if r in new and frames[r] != full:
                        actual_captures.append({'cut': cut, 'source': int(s[1:]), 'helper': r,
                                                'frame': f, 'coefficient': str(q)})
                    if r in new:
                        counts['added_source_reads'] += 1
                for key, value in state[s].items():
                    state[r][key] = state[r].get(key, Q(0))+q*value
                    if not state[r][key]:
                        del state[r][key]
    need(actual_captures == c['captures'], 'complete capture witness binding')
    need(len(actual_captures) == 48 and len({x['source'] for x in actual_captures}) == 48, 'one capture per required source')
    need(set(state) == set(names), 'private lifetimes closed')
    for r in names:
        expected = {r: Q(1)}
        if r.startswith('Y'):
            t = int(r[1:])
            if t == 2:
                expected['X2'] = Q(1)
            else:
                expected.update({f'X{s}': v/2 for s, v in enumerate(gram[t]) if v})
        need(state[r] == expected, 'all-input endpoint '+r)
        end = c['final_frames'][r] if r in new else w['final_frames'][r]
        need(frames[r] == space(end), 'restored endpoint frame '+r)
    need(sum(k*v for k, v in addpaid.items()) == 39*9, 'telescoping added rank mass')
    return dict(counts) | {'input_columns': len(names), 'helper_lifetimes': 39,
                          'added_profile': dict(sorted(addpaid.items())),
                          'full_profile': dict(sorted(paid.items())),
                          'added_rank_mass': sum(k*v for k, v in addpaid.items()),
                          'full_rank_mass': sum(k*v for k, v in paid.items())}


def controls(w, gram, c):
    out = []
    for name, mutate in [
        ('missing_dirty_compensation', lambda x: x['insertions'][0]['events'].pop(0)),
        ('wrong_capture_coefficient', lambda x: next(e for b in x['insertions'] for e in b['events'] if e[0] == 'add' and e[1].startswith('L')) .__setitem__(3, '0')),
        ('wrong_target', lambda x: x['insertions'][-1]['events'].__setitem__(next(i for i,e in enumerate(x['insertions'][-1]['events']) if e[0]=='add' and e[1]=='Y2'), ['add','Y1','L0','1',w['final_frames']['Y2']])),
        ('missing_cleanup', lambda x: x['insertions'][-1]['events'].pop()),
        ('wrong_capture_cut', lambda x: next(b for b in x['insertions'] if b['completed_cut']==618).__setitem__('completed_cut', 617)),
        ('false_rank', lambda x: next(e for b in x['insertions'] for e in b['events'] if e[0]=='transport').__setitem__(4, 2)),
    ]:
        bad = copy.deepcopy(c)
        mutate(bad)
        try:
            replay(w, gram, bad)
        except (ValueError, KeyError):
            out.append(name)
        else:
            raise ValueError('control accepted '+name)
    bad = copy.deepcopy(w)
    # Enlarging one constrained source to another witness frame must invalidate the proof premise.
    bad['initial_frames']['X3'] = bad['initial_frames']['X6']
    try:
        access_proof(bad, gram)
    except ValueError:
        out.append('altered_source_frame_antichain')
    else:
        raise ValueError('antichain control accepted')
    # Equivalent bases are a positive control, not a new physical realization.
    equivalent = copy.deepcopy(c)
    for block in equivalent['insertions']:
        for e in block['events']:
            if e[0] == 'add':
                e[4] = list(reversed(e[4]))
    for rec in equivalent['captures']:
        rec['frame'] = list(reversed(rec['frame']))
    need(replay(w, gram, equivalent) == replay(w, gram, c), 'equivalent basis positive control')
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--regenerate', action='store_true')
    args = ap.parse_args()
    w, gram = inputs()
    c = load(P/'CIRCUIT.json')
    result = {'status': 'PASS_P104_Y2_LATE_ACQUISITION', 'access': access_proof(w, gram),
              'word': replay(w, gram, c), 'rejecting_controls': controls(w, gram, c),
              'scope': 'Sharp 39 new helper lifetimes in the stated X-only monotone relay model; finite abstract frame word; no native/global/all-size supplier or kappa.'}
    result = json.loads(json.dumps(result))
    if args.regenerate:
        with tempfile.TemporaryDirectory(prefix='p104-y2-') as tmp:
            dest = Path(tmp)/'circuit.json'
            subprocess.run([sys.executable, '-I', '-O', '-B', str(P/'build.py'), '--out', str(dest)], check=True)
            need(load(dest) == c, 'complete literal regeneration')
    if args.write:
        with (P/'RESULT.json').open('x', encoding='utf-8', newline='\n') as out:
            json.dump(result, out, indent=2)
            out.write('\n')
    else:
        need(load(P/'RESULT.json') == result, 'exact receipt drift')
    print('PASS_P104_Y2_LATE_ACQUISITION helpers=39 antichain=39 columns=319 added_rank=351 controls=7 no_new_kappa')


if __name__ == '__main__':
    main()

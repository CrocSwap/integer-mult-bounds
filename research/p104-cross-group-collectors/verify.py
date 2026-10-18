#!/usr/bin/env python3
"""Sparse exact replay adapted from PR2460, with new source-bound cross-group checks; no producer imports. ywz65 + OpenAI Codex, Apache-2.0."""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
INPUT = HERE.parent / 'p104-native-channel' / 'inputs'
PINS = {'LOWRANK-WITNESS.json': '0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e',
        'P104-FIXTURE.json': '516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4'}


def need(p, msg):
    if not p:
        raise ValueError(msg)


def frame(xs):
    seen = {0}
    for x in xs:
        need(type(x) is int and 0 < x < 512 and x not in seen, 'invalid basis')
        seen |= {v ^ x for v in tuple(seen)}
    return frozenset(seen)


def rank(a):
    a = [list(map(Q, row)) for row in a]
    r = 0
    for j in range(len(a[0])):
        p = next((i for i in range(r, len(a)) if a[i][j]), None)
        if p is None:
            continue
        a[p], a[r] = a[r], a[p]
        q = a[r][j]
        a[r] = [x/q for x in a[r]]
        for i in range(len(a)):
            if i != r:
                q = a[i][j]
                a[i] = [x-q*y for x, y in zip(a[i], a[r])]
        r += 1
        if r == len(a):
            break
    return r


def geometry(word, fixture):
    roots = []
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0]*8
            row[i], row[j] = 2, 2*sign
            roots.append(tuple(row))
    roots.extend((1, *s) for s in product((-1, 1), repeat=7) if sum(s) % 4 == 3)
    p = fixture['section4_explicit_P104']
    ports = sorted(set(roots) - set(map(tuple, p['F0']+p['C'])))
    need(len(ports) == 104, 'root count')
    half = [[Q(sum(x*y for x, y in zip(a, b)), 8) for b in ports] for a in ports]
    corr = [[Q(t == s)-half[t][s] for s in range(104)] for t in range(3)]
    supports = [{s for s in range(104) if corr[t][s]} for t in range(3)]
    need(list(map(len, supports)) == [48]*3, 'support sizes')
    ends = [frame(word['final_frames'][f'Y{t}']) for t in range(3)]
    need(all(len(x) == 256 for x in ends) and len(set(ends)) == 3, 'endpoint incomparability')
    paths = {r: [frame(f)] for r, f in word['initial_frames'].items()}
    for e in word['program']:
        if e[0] == 'transport' and e[1] in paths:
            need(paths[e[1]][-1] == frame(e[2]), 'source path binding')
            paths[e[1]].append(frame(e[3]))
        if e[0] in ('add', 'copy'):
            need(not e[1].startswith('X') and not e[2].startswith('Y'), 'original data contract')
    for r, path in paths.items():
        if r.startswith(('X', 'Y')):
            need(all(a <= b for a, b in zip(path, path[1:])), 'data monotonicity')
    union = set.union(*supports)
    need(len({paths[f'X{s}'][0] for s in union}) == 90, '90 distinct acquisition lines')
    escapes, late = [], []
    for t in range(3):
        for s in sorted(supports[t]):
            xp, yp = paths[f'X{s}'], paths[f'Y{t}']
            line = xp[0]
            need(len(line) == 2 and line <= ends[t], 'initial source access')
            escaped = sorted(xp[1]-ends[t])
            if not escaped:
                late.append([t, s, len(xp[1]).bit_length()-1])
            else:
                escapes.append([t, s, next(x for x in line if x), escaped[0]])
            if t < 2:
                need(escaped and all(x == line for x in xp if x <= ends[t]), 'two-target escape')
                need(all(x != line for x in yp), 'two-target direct access')
    groups = []
    for mask in range(1, 8):
        targets = [t for t in range(3) if mask >> t & 1]
        sources = [s for s in range(104) if [t for t in range(3) if corr[t][s]] == targets]
        common = set.intersection(*(set(ends[t]) for t in targets))
        r = rank([[corr[t][s] for s in sources] for t in targets])
        need(all(paths[f'X{s}'][0] <= common for s in sources), 'common-frame source access')
        groups.append({'targets': targets, 'sources': sources, 'coefficient_rank': r,
                       'common_dimension': len(common).bit_length()-1,
                       'extra_collector_floor': len(targets)-r})
    need(sum(len(g['sources']) for g in groups) == 90, 'union size')
    need(sum(g['extra_collector_floor'] for g in groups) == 4, 'collector deficit')
    return half, {'groups': groups, 'escape_witnesses': escapes, 'first_expansion_still_contained': late,
                  'union_support_size': 90, 'separated_collector_minimum': 94, 'exclusive_y2_sources': sorted(supports[2]-supports[0]-supports[1])}


def replay(word, circuit, half):
    new = circuit['initial_frames'] if circuit else {}
    need(not set(new) & set(word['initial_frames']), 'new alias')
    fs = {r: frame(f) for r, f in {**word['initial_frames'], **new}.items()}
    names = sorted(fs)
    rows = {r: {r: Q(1)} for r in names}
    full = frozenset(range(512))
    need(all(fs[r] == {0} for r in new), 'dirty entrance')
    profile, added, counts = Counter(), Counter(), Counter()
    max_l1, max_denom = Q(1), 1
    insert = {i['completed_cut']: i['events'] for i in circuit['insertions']} if circuit else {}
    need(not circuit or len(insert) == len(circuit['insertions']) and all(type(k) is int and 0 <= k <= len(word['program']) for k in insert), 'insertion cuts')

    def event(e, is_new):
        nonlocal max_l1, max_denom
        op, dst = e[:2]
        counts['events'] += 1
        if is_new:
            need(op in ('add', 'transport') and dst in set(new) | {'Y0', 'Y1', 'Y2'}, 'new alphabet')
        if op == 'add':
            _, dst, src, coefficient, basis = e
            need(dst != src and src in rows and dst in rows, 'ADD roles')
            need(fs[dst] == fs[src] == frame(basis), 'ADD frame')
            q = Q(coefficient)
            need(q and q.denominator & (q.denominator-1) == 0, 'dyadic ADD')
            if is_new:
                need(src in new or src.startswith('X'), 'forbidden read')
                need(dst in new or src in new, 'direct target read')
                counts['added_ADDs'] += 1
                counts['source_reads'] += int(src.startswith('X'))
            for col, v in rows[src].items():
                value = rows[dst].get(col, Q(0)) + q*v
                if value:
                    rows[dst][col] = value
                else:
                    rows[dst].pop(col, None)
        elif op == 'transport':
            _, dst, old, newf, cost = e
            a, b = frame(old), frame(newf)
            need(dst in rows and fs[dst] == a, 'transport entrance')
            need(a < b or b < a, 'nested frame')
            need(type(cost) is int and cost == abs(len(old)-len(newf)), 'transport invoice')
            if is_new:
                need(dst in new and a < b, 'new monotonicity')
                added[cost] += 1
            else:
                need(a < b or dst == 'C', 'original descent')
            profile[cost] += 1
            fs[dst] = b
        elif op == 'zero':
            need(dst == 'C' and dst not in rows, 'private allocation')
            rows[dst], fs[dst] = {}, frame(e[2])
        elif op == 'copy':
            _, dst, src, b = e
            need(dst == 'C' and rows[dst] == {} and fs[dst] == fs[src] == frame(b), 'private copy')
            rows[dst] = dict(rows[src])
        elif op == 'erase':
            need(dst == 'C' and fs[dst] == frame(e[2]), 'private discard')
            del rows[dst], fs[dst]
            return
        else:
            raise ValueError('unknown operation')
        max_l1 = max(max_l1, sum(map(abs, rows[dst].values()), Q(0)))
        max_denom = max([max_denom] + [v.denominator for v in rows[dst].values()])

    for cut in range(len(word['program'])+1):
        for e in insert.get(cut, []):
            event(e, True)
        if cut < len(word['program']):
            event(word['program'][cut], False)
    expected_frames = {**word['final_frames'], **(circuit['final_frames'] if circuit else {})}
    need(set(rows) == set(names) == set(expected_frames), 'final roles')
    for r in names:
        need(fs[r] == frame(expected_frames[r]), 'final frame')
        if r in new:
            need(fs[r] == full, 'dirty exit')
        expected = {r: Q(1)}
        if r.startswith('Y'):
            t = int(r[1:])
            cs = [Q(t == s) for s in range(104)] if circuit and t < 3 else half[t]
            expected.update({f'X{s}': q for s, q in enumerate(cs) if q})
        need(rows[r] == expected, 'endpoint '+r)
    return {**dict(counts), 'columns': len(names), 'helpers': len(new),
            'added_profile': dict(sorted(added.items())), 'full_profile': dict(sorted(profile.items())),
            'added_transports': sum(added.values()), 'added_rank_mass': sum(k*v for k, v in added.items()),
            'full_rank_mass': sum(k*v for k, v in profile.items()),
            'logical_prefix_l1': str(max_l1), 'logical_denominator': max_denom}


RETAINED_PINS = {'inputs/PR2460-CIRCUIT.json': {'sha256': 'ce1b033ae8b826eec87d70246a13a6034e177ef4863bf7f7c24631c79e5202c9', 'git_blob': 'a43c67a0d00c79ea70c4ed9002ce338790a34cf7'}, 'inputs/PR2460-README.md': {'sha256': 'e17214bd1bf5b27aedad3b40920d6c45eb664b717c5f1e098612ff014bcdb44e', 'git_blob': '7d43a1eae8d4520e63a3fa1b2ec63d66c8e60f60'}, 'inputs/PR2504-CIRCUIT.json': {'sha256': '96459a07c79fd1b711af6343bc9c004d91e28cd0da3306c290cff657082b110d', 'git_blob': '51d73e47e7d3ffff4a7b1632cacbd8a97e96c0a1'}, 'inputs/PR2504-README.md': {'sha256': '9c9afffe4c13f405e5bf274ab0d67b15c6cefece0a12621d0d99d3e6bc8fa7af', 'git_blob': '8b3ee7165aa9f952ffcd95edafaaa5f3cb5f6ee7'}}

def blob(data):
    from hashlib import sha1
    return sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def load_sources():
    for name, digest in PINS.items():
        need(sha256((INPUT/name).read_bytes()).hexdigest() == digest, 'live source pin '+name)
    manifest = json.loads((HERE/'PREDECESSORS.json').read_text())
    records = {r['path']: r for r in manifest['retained']}
    need(set(records) == set(RETAINED_PINS), 'retained source coverage')
    for path, pins in RETAINED_PINS.items():
        data = (HERE/path).read_bytes()
        need(sha256(data).hexdigest() == pins['sha256'] == records[path]['sha256'], 'retained sha256 '+path)
        need(blob(data) == pins['git_blob'] == records[path]['git_blob'], 'retained blob '+path)
    word = json.loads((INPUT/'LOWRANK-WITNESS.json').read_text())
    fixture = json.loads((INPUT/'P104-FIXTURE.json').read_text())
    old = json.loads((HERE/'inputs/PR2460-CIRCUIT.json').read_text())
    late = json.loads((HERE/'inputs/PR2504-CIRCUIT.json').read_text())
    return word, fixture, old, late


def events(circuit):
    return [e for insertion in circuit['insertions'] for e in insertion['events']]


def touches(event, names):
    return event[1] in names or event[0] == 'add' and event[2] in names


def projection(circuit, names, keep):
    out = {}
    for item in circuit['insertions']:
        subset = [e for e in item['events'] if touches(e, names) == keep]
        if subset:
            out[item['completed_cut']] = subset
    return out


def construction_binding(word, old, late, cross, final, geo):
    """Verify exact retained components separately from all-input correctness."""
    exclusive = next(g['sources'] for g in old['groups'] if g['targets'] == [2])
    need(exclusive == geo['exclusive_y2_sources'], 'actual exclusive source set')
    need(exclusive == [0,1,3,6,8,11,16,19,25,28,97,99], 'exclusive source witness')
    contained_late = {s for t,s,d in geo['first_expansion_still_contained'] if t == 2}
    need(set(exclusive) != contained_late, 'do not conflate the two twelve-source sets')
    removed = {'N'+str(s) for s in exclusive}
    new_late = set(late['initial_frames'])-set(old['initial_frames'])
    need(len(new_late) == 10 and not new_late & set(cross['initial_frames']), 'late component roles')
    need(projection(final, new_late, True) == projection(late, new_late, True), 'literal late component')
    need(projection(final, new_late, False) == projection(cross, removed, False), 'literal cross complement')
    need(final['late_acquisition'] == late['late_acquisition'], 'late route metadata')
    for field in ('initial_frames','final_frames'):
        need({r:f for r,f in final[field].items() if r not in new_late}
             == {r:f for r,f in cross[field].items() if r not in removed}, 'cross component boundary')
        need({r:final[field][r] for r in new_late}
             == {r:late[field][r] for r in new_late}, 'late component boundary')
    changed_groups = {(0,1,2),(0,2),(1,2)}
    old_changed = {f'N{s}' for g in old['groups'] if tuple(g['targets']) in changed_groups for s in g['sources']}
    old_changed |= {r for g in old['groups'] if tuple(g['targets']) in changed_groups for r in g['extra_helpers']}
    new_changed = (old_changed & set(cross['initial_frames'])) | {'C012_0','C012_1'}
    need(projection(old, old_changed, False) == projection(cross, new_changed, False), 'untouched incidence groups')
    need(set(old['initial_frames'])-set(cross['initial_frames']) == {'E012_1','E012_2','E02_2','E12_2'}, 'old collectors')
    need(set(cross['initial_frames'])-set(old['initial_frames']) == {'C012_0','C012_1'}, 'new collectors')
    need(len(cross['initial_frames']) == 92 and len(final['initial_frames']) == 90, 'helper counts')
    cross_before = next(x['events'] for x in cross['insertions'] if x['completed_cut'] == 0)
    cross_after = next(x['events'] for x in cross['insertions'] if x['completed_cut'] == len(word['program']))
    ends = [frame(word['final_frames'][f'Y{t}']) for t in range(3)]
    joint = frozenset.intersection(*ends)
    witnesses = []
    for target in (0,1):
        group = next(g for g in old['groups'] if g['targets'] == [target,2])
        reg, carried = f"N{group['sources'][0]}", f'C012_{target}'
        common = frame(group['common_frame'])
        need(joint < common < ends[target] and common < ends[2], 'cross-group frame inclusions')
        pair = [['add',reg,carried,'1',group['common_frame']],
                ['add',carried,reg,'-1',group['common_frame']]]
        need(any(cross_before[i:i+2] == pair for i in range(len(cross_before)-1)), 'determinant-one branch shear')
        need(any(e[:4] == ['add',f'Y{target}',reg,'1'] for e in cross_after), 'first branch delivery')
        need(any(e[:4] == ['add','Y2',carried,'-1'] for e in cross_after), 'second branch delivery sign')
        witnesses.append({'targets':[target,2], 'total_register':reg, 'carried_register':carried,
                          'joint_dimension':len(joint).bit_length()-1,
                          'meeting_dimension':len(common).bit_length()-1})
    # (B,C) -> (B+C,-B) is invertible, with determinant one; it is not a copy.
    matrix = [[Q(1),Q(1)],[Q(-1),Q(0)]]
    inverse = [[Q(0),Q(-1)],[Q(1),Q(1)]]
    need(all(sum(matrix[i][k]*inverse[k][j] for k in range(2)) == Q(i == j)
             for i in range(2) for j in range(2)), 'branch shear inverse')
    return {'exclusive_sources':exclusive, 'late_compatible_sources':sorted(contained_late),
            'cross_branch_witnesses':witnesses, 'late_helpers_retained_literally':sorted(new_late),
            'retained_other_incidence_groups':[[0],[0,1],[1],[2]],
            'unrestricted_minimum_claimed':False}


def rejecting_controls(word, circuit, half):
    failures = []
    def reject(label, mutate):
        broken = deepcopy(circuit)
        mutate(broken)
        try:
            replay(word, broken, half)
        except (ValueError, KeyError, IndexError, TypeError):
            failures.append(label)
            return
        raise ValueError('accepted broken control '+label)
    def locate(c, predicate):
        return next(e for e in events(c) if predicate(e))
    reject('cross-shear sign', lambda c: locate(c,lambda e:e[:3]==['add','C012_0','N39']).__setitem__(3,'1'))
    reject('Y2 branch sign', lambda c: locate(c,lambda e:e[:3]==['add','Y2','C012_0']).__setitem__(3,'1'))
    reject('missing dirty compensation', lambda c: locate(c,lambda e:e[0]=='add' and e[1]=='Y0' and e[2]=='C012_0' and e[4]==[]).__setitem__(3,'1'))
    reject('missing cross inverse', lambda c: locate(c,lambda e:e[0]=='add' and e[1]=='C012_0' and e[4]==[1<<i for i in range(9)]).__setitem__(3,'-1'))
    reject('forbidden original helper read', lambda c: locate(c,lambda e:e[0]=='add' and e[2].startswith('X')).__setitem__(2,'G0'))
    reject('undercharged cross transport', lambda c: locate(c,lambda e:e[:2]==['transport','C012_0'] and len(e[2])==6).__setitem__(4,0))
    reject('late capture coefficient', lambda c: locate(c,lambda e:e[:3]==['add','LATE0','X1']).__setitem__(3,'1/2'))
    reject('late source cleanup', lambda c: locate(c,lambda e:e[:3]==['add','LATE0','X6'] and len(e[4])==9).__setitem__(3,'-1/2'))
    return failures


def compute():
    word, fixture, old, late = load_sources()
    half, geo = geometry(word, fixture)
    cross = json.loads((HERE/'CROSS-CONTROL.json').read_text())
    final = json.loads((HERE/'CIRCUIT.json').read_text())
    binding = construction_binding(word,old,late,cross,final,geo)
    receipts = {name:replay(word,c,half) for name,c in
                [('original',None),('predecessor94',old),('late92',late),('cross92',cross),('combined90',final)]}
    need(receipts['predecessor94']['helpers'] == 94 and receipts['late92']['helpers'] == 92, 'predecessor helper invoice')
    for left,right in [('predecessor94','cross92'),('late92','combined90')]:
        a,b = receipts[left],receipts[right]
        need(a['added_ADDs'] == b['added_ADDs'] and a['source_reads'] == b['source_reads'], 'no additional scalar operations')
        need(a['added_rank_mass']-b['added_rank_mass'] == 18 and a['added_transports']-b['added_transports'] == 4, 'cross-group saving')
        delta = Counter(a['added_profile'])
        delta.subtract(b['added_profile'])
        need({r:n for r,n in delta.items() if n} == {2:2,7:2}, 'exact saved profile')
    controls = rejecting_controls(word, final, half)
    # Equivalent independent basis presentations are not rejected as semantic errors.
    equivalent = deepcopy(final)
    for e in events(equivalent):
        if e[0] == 'transport':
            e[2].reverse(); e[3].reverse()
        else:
            e[4].reverse()
    for f in ('initial_frames','final_frames'):
        for basis in equivalent[f].values():
            basis.reverse()
    need(replay(word,equivalent,half) == receipts['combined90'], 'equivalent frame basis')
    return {'scope':'finite three-target cross-group construction; no new kappa',
            'binding':binding,'replays':receipts,'rejected_controls':controls,
            'equivalent_frame_basis':'accepted'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,help='write a new caller-selected receipt; never overwrite')
    parser.add_argument('--regenerate',action='store_true')
    args = parser.parse_args()
    result = compute()
    expected = json.loads((HERE/'RESULT.json').read_text())
    need(json.loads(json.dumps(result)) == expected, 'complete result receipt')
    if args.regenerate:
        with tempfile.TemporaryDirectory() as tmp:
            for filename, flag in [('CIRCUIT.json',[]),('CROSS-CONTROL.json',['--cross-only'])]:
                output = Path(tmp)/filename
                subprocess.run([sys.executable,'-I','-O','-B',str(HERE/'build.py'),'--out',str(output),*flag],check=True)
                need(json.loads(output.read_text()) == json.loads((HERE/filename).read_text()), 'complete literal regeneration')
    if args.out:
        with args.out.open('x',encoding='utf-8',newline='\n') as output:
            json.dump(result,output,indent=2);output.write('\n')
    print('PASS_P104_CROSS_GROUP helpers=90 ADDs=517 transports=279 rank_mass=810 inputs=370 controls=8 no_new_kappa')


if __name__ == '__main__':
    main()

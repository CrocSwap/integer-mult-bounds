#!/usr/bin/env python3
"""Independent exact-projector PR589 ledger. Standard library only.

Prepared for commdata2338 with substantial OpenAI Codex assistance.
Construction credit: DreamingOfClouds, eumemic and the README's lineage.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import json
from math import gcd, lcm
from pathlib import Path
import struct

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BIT = 'research/e8-bit-p111-tuned/'
VENDOR = BIT + 'vendor/pr510/e8-r480-nine-stage/vendor/'
H = 8


class Reject(ValueError):
    pass


def need(ok, message):
    if not ok:
        raise Reject(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()


def integer(x, lo=0, hi=None):
    return type(x) is int and x >= lo and (hi is None or x <= hi)


def hist(counter):
    return {str(k): counter[k] for k in sorted(counter) if counter[k]}


def check_digest(raw, expected):
    need(digest(raw) == expected, 'source digest')


def inputs():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    raw = {}
    for row in manifest['files']:
        if row['usage'] == 'input':
            path = (ROOT / row['path']).resolve()
            need(path.is_relative_to(ROOT), 'source outside repository')
            raw[row['path']] = path.read_bytes()
            check_digest(raw[row['path']], row['sha256'])
    return raw


def dot(x, y):
    return sum(a*b for a, b in zip(x, y))


@lru_cache(maxsize=2048)
def projector(rows):
    """Gram-Schmidt P=sum uu^t/(u^t u); exact integer numerator M/den.

    The cache key contains all coordinates, never just a frame ID or digest.
    This uses neither the predecessor's row reduction nor its nullspace code.
    """
    basis = []
    for row in rows:
        need(len(row) == H and all(type(x) is int for x in row), 'label coordinates')
        u = list(map(Q, row))
        for v, norm in basis:
            c = dot(u, v)/norm
            u = [a-c*b for a, b in zip(u, v)]
        norm = dot(u, u)
        if norm:
            basis.append((u, norm))
        if len(basis) == H:
            break  # geometry() still checks closure against every live label
    p = [[sum((u[i]*u[j]/norm for u, norm in basis), Q(0))
          for j in range(H)] for i in range(H)]
    den = lcm(*(x.denominator for row in p for x in row))
    a = tuple(tuple(int(x*den) for x in row) for row in p)
    common = gcd(den, *(x for row in a for x in row))
    a = tuple(tuple(x//common for x in row) for row in a)
    den //= common
    rank = len(basis)
    out = (a, den, rank)
    validate_projector(out)
    return out


def validate_projector(p):
    a, den, rank = p
    need(integer(den, 1) and integer(rank, 0, H), 'projector header')
    need(len(a) == H and all(len(row) == H for row in a), 'projector shape')
    need(all(a[i][j] == a[j][i] for i in range(H) for j in range(H)), 'symmetry')
    need(all(sum(a[i][k]*a[k][j] for k in range(H)) == den*a[i][j]
             for i in range(H) for j in range(H)), 'idempotence')
    need(sum(a[i][i] for i in range(H)) == den*rank, 'integer trace')


def fixes(p, v):
    a, den, _ = p
    return all(dot(row, v) == den*x for row, x in zip(a, v))


@lru_cache(maxsize=16384)
def increase(old, new):
    """Nested orthogonal projectors have rank(new-old)=trace(new)-trace(old)."""
    a, da, ra = old
    b, db, rb = new
    need(all(sum(a[i][k]*b[k][j] for k in range(H)) == db*a[i][j]
             for i in range(H) for j in range(H)), 'non-nested projectors')
    need(rb >= ra, 'negative projector difference')
    return rb-ra


def complement(p):
    a, den, rank = p
    return (tuple(tuple(den*int(i == j)-a[i][j] for j in range(H))
                  for i in range(H)), den, H-rank)


def geometry(word):
    need(word['h'] == H and word['form'] == '<x,y>/2', 'label-space contract')
    v, r = word['v'], word['R']
    need(integer(v, 1) and integer(r, 1), 'register counts')
    lines = tuple(tuple(row) for row in word['lines'])
    need(len(lines) == v and len(set(lines)) == v, 'label inventory')
    need(all(len(x) == H and all(type(y) is int for y in x) and dot(x, x) == 4
             for x in lines), 'root norms')
    need(all(abs(dot(x, y)) <= 2 for i, x in enumerate(lines) for y in lines[i+1:]),
         'distinct root lines')
    spaces = []
    for frame in word['frames']:
        need(frame == sorted(set(frame)) and all(integer(i, 0, v-1) for i in frame),
             'frame index set')
        p = projector(tuple(lines[i] for i in frame))
        need([i for i, row in enumerate(lines) if fixes(p, row)] == frame, 'frame closure')
        spaces.append(p)
    zero = [i for i, p in enumerate(spaces) if p[2] == 0]
    full = [i for i, p in enumerate(spaces) if p[2] == H]
    need(len(zero) == len(full) == 1, 'unique zero/full')
    n = 2*v+r
    for label in ('start', 'final'):
        need(len(word[label]) == n and all(integer(f, 0, len(spaces)-1) for f in word[label]),
             label+' frame inventory')
    for i in range(n):
        start, final = spaces[word['start'][i]], spaces[word['final'][i]]
        if i < v:
            need(start == projector((lines[i],)) and final[2] == H, 'source boundary')
        elif i < 2*v:
            need(start[2] == 0 and final == complement(projector((lines[i-v],))), 'target boundary')
        else:
            need(start[2] == 0 and final[2] == H, 'helper boundary')
    return spaces, zero[0]


def records(word, spaces, zero):
    """Independently expand gates into the source's six-integer record vocabulary."""
    v, n = word['v'], 2*word['v']+word['R']
    current, out = list(word['start']), []

    def move(register, frame):
        old = current[register]
        if old != frame:
            cost = increase(spaces[old], spaces[frame])
            need(cost > 0, 'distinct frame with no rank change')
            out.append((0, register, old, frame, cost, 0))
            current[register] = frame

    def gates(section, phase):
        for frame, target, sources in word[section]:
            need(integer(frame, 0, len(spaces)-1), 'gate frame')
            operands = [target, *sources]
            need(all(integer(i, 0, n-1) for i in operands) and len(set(operands)) == len(operands),
                 'gate operands')
            for i in operands:
                move(i, frame)
            out.extend((1, target, source, 1, frame, phase) for source in sources)

    gates('D', 1)
    gates('A', 2)
    need(len(word['scatter']) == v, 'scatter rows')
    retained = word['ret']
    need(len(set(retained)) == len(retained) and all(integer(q, 2*v, n-1) for q in retained),
         'retained helpers')
    need(all(row == sorted(set(row)) and all(integer(k, 0, len(retained)-1) for k in row)
             for row in word['scatter']), 'scatter indices')
    for k, center in enumerate(retained):
        frame = current[center]
        out.append((2, center, n, frame, zero, spaces[frame][2]))
        out.extend((1, v+t, n, 1, zero, 3) for t, row in enumerate(word['scatter']) if k in row)
        out.append((3, center, n, frame, zero, 0))
    gates('B', 4)
    gates('C', 5)
    for register, frame in enumerate(word['final']):
        move(register, frame)
    return out


def replay(word, spaces, tape, reverse=False):
    """All dirty columns at once; the reverse uses complementary projectors."""
    v, n = word['v'], 2*word['v']+word['R']
    current = list(word['final'] if reverse else word['start'])+[None]
    value = [1 << i for i in range(n)]+[0]
    effective = [complement(p) for p in spaces] if reverse else spaces
    center = None
    paid, counts, phases = Counter(), Counter(), Counter()
    for op, x, y, a, b, c in (reversed(tape) if reverse else tape):
        need(op in (0, 1, 2, 3) and integer(x, 0, n-1), 'record opcode/role')
        if op == 0:
            old, new = (a, y) if reverse else (y, a)
            need(integer(old, 0, len(spaces)-1) and integer(new, 0, len(spaces)-1), 'MOVE frames')
            need(current[x] == old, 'MOVE chronology')
            rank = increase(effective[old], effective[new])
            need(integer(b, 1, H) and b == rank and c == 0, 'MOVE rank')
            current[x] = new
            paid[rank] += 1
            counts['moves'] += 1
        elif op == 1:
            need(integer(y, 0, n) and x != y and a == 1, 'ADD operands')
            need(current[x] == current[y] == b, 'ADD common frame')
            need(x != center and (y != n or center is not None), 'COPY lifetime')
            value[x] ^= value[y]
            counts['adds'] += 1
            phases[c] += 1
        elif op == (3 if reverse else 2):
            need(center is None and y == n and value[n] == 0 and current[n] is None,
                 'COPY clean temporary')
            need(current[x] == a and integer(b, 0, len(spaces)-1), 'COPY frame')
            source, target = effective[a], effective[b]
            rank = increase(source, target) if source[2] <= target[2] else increase(target, source)
            need(rank > 0 and c == (0 if reverse else rank), 'COPY rank')
            center, current[n], value[n] = x, b, value[x]
            paid[rank] += 1
            counts['copies'] += 1
        else:
            need(center == x and y == n and current[x] == a and current[n] == b, 'ERASE lifetime')
            need(value[n] == value[x], 'ERASE dirty residue')
            need(c == (abs(effective[a][2]-effective[b][2]) if reverse else 0), 'ERASE metadata')
            center, current[n], value[n] = None, None, 0
            counts['erasures'] += 1
    need(center is None and current[n] is None and value[n] == 0, 'temporary restoration')
    need(current[:n] == (word['start'] if reverse else word['final']), 'final frames')
    want = [(1 << i) ^ ((1 << (i-v)) if v <= i < 2*v else 0) for i in range(n)]
    need(value[:n] == want, 'arbitrary-dirty scalar endpoint')
    return {'profile': hist(paid), 'rank_mass': sum(k*v for k, v in paid.items()),
            'counts': dict(sorted(counts.items())), 'adds_by_phase': hist(phases),
            'formal_columns': n, 'records': len(tape)}


def schedule():
    """Derive idle ranks by aligning pair levels before each source-recipe bridge."""
    levels, events = [-1]*4, []
    idle_index = 0

    def advance(pair, level):
        nonlocal idle_index
        need(level >= levels[pair], 'schedule descent')
        events.append({'kind': 'idle', 'pair': pair, 'rank': 7*(level-levels[pair]),
                       'from': levels[pair], 'to': level, 'idx': idle_index})
        levels[pair] = level
        idle_index += 1

    for stage in range(9):
        pair = max(0, (stage-1)//2)
        need(levels[pair] == stage-1, 'local schedule level')
        events.append({'kind': 'local', 'stage': stage, 'pair': pair, 'reverse': bool(stage % 2)})
        levels[pair] = stage
        if 1 <= stage <= 6:
            advance(pair+1, stage)
            events.append({'kind': 'bridge', 'dst': pair, 'src': pair+1})
    for pair in range(4):
        advance(pair, 8)
    for pair in (2, 1, 0):
        events.append({'kind': 'bridge', 'dst': pair+1, 'src': pair})
    return events


def global_ledger(local, selection, v, helpers, replicas=32):
    events, windows = schedule(), {}
    for pos, event in enumerate(events):
        if event['kind'] != 'idle':
            continue
        pair, stages = event['pair'], []
        for prior in reversed(events[:pos]):
            if (prior['kind'] == 'local' and prior['pair'] == pair) or (
                prior['kind'] == 'bridge' and pair in (prior['dst'], prior['src'])):
                break
            if prior['kind'] == 'local':
                stages.append(prior['stage'])
        windows[event['idx']] = {**event, 'stages': sorted(stages)}
    available = {i: w for i, w in windows.items() if w['rank'] and w['stages']}
    copies, capacities, stage_totals, idle = Counter(), Counter(), Counter(), Counter()
    seen = set()
    for index, widths, count in selection['patterns']:
        need(index in available and integer(count, 1), 'pattern index/count')
        need(all(type(w) is int and w == H for w in widths), 'helper width')
        need((index, tuple(widths)) not in seen, 'duplicate pattern')
        seen.add((index, tuple(widths)))
        remainder = available[index]['rank']-sum(widths)
        need(remainder >= 0, 'pattern exceeds capacity')
        copies[index] += count
        capacities[index] += count*len(widths)
        if remainder:
            idle[remainder] += count
    need(dict(copies) == {i: 2*v for i in available}, 'pattern family coverage')
    allocated, seen = Counter(), set()
    for index, width, stage, count in selection['stages']:
        need(index in available and stage in available[index]['stages'], 'stage outside idle window')
        need(type(width) is int and width == H and integer(count, 1), 'allocation width/count')
        need((index, width, stage) not in seen, 'duplicate allocation')
        seen.add((index, width, stage))
        allocated[index] += count
        stage_totals[stage] += count
    need(allocated == capacities, 'allocation/pattern counts')
    need(dict(stage_totals) == {s: helpers for s in range(9)}, 'helper stage inventory')
    for index, window in windows.items():
        if index not in available and window['rank']:
            idle[window['rank']] += 2*v
    need(integer(replicas, 1), 'replica count')
    calls = sum(e['kind'] == 'local' for e in events)*replicas
    paid = Counter({int(k): count*calls for k, count in local.items()})
    paid.update({rank: count*replicas for rank, count in idle.items()})
    live, width = 2*4*v*replicas, 1+7*9
    mass = sum(rank*count for rank, count in paid.items())
    return {'profile': hist(paid), 'local_calls': calls, 'replicas': replicas,
            'live': live, 'width': width, 'rank_mass': mass, 'deficit': width*live-mass,
            'idle_per_replica': hist(idle), 'idle_windows': list(windows.values()),
            'hosted_helpers': sum(stage_totals.values())*replicas,
            'pending_mass_per_replica': sum(2*v*w['rank'] for w in windows.values())}


def compare(actual, expected):
    need(actual == expected, 'ledger / receipt mismatch')


def reject_control(name, action, reason):
    try:
        action()
    except Reject as exc:
        need(reason in str(exc), name+': unexpected rejection: '+str(exc))
        return name
    raise Reject(name+': accepted')


def controls(word, spaces, zero, tape, global_result, selection):
    passed = []
    def check(name, action, reason):
        passed.append(reject_control(name, action, reason))

    e0 = projector(((1, 0, 0, 0, 0, 0, 0, 0),))
    e1 = projector(((0, 1, 0, 0, 0, 0, 0, 0),))
    need(e0[2] == e1[2], 'equal-dimension control premise')
    check('same-rank non-nesting', lambda: increase(e0, e1), 'non-nested')
    bad = deepcopy(word); bad['A'][0][0] = word['start'][1]
    # This deliberately weakened calculation is a failure-control premise only.
    # It ignores subspace containment, and must never be an acceptance path.
    def dimension_only(w):
        cur, bill = list(w['start']), Counter()
        def move(i, f):
            rank = spaces[f][2]-spaces[cur[i]][2]
            need(rank >= 0, 'dimension-only control has a descent')
            if rank:
                bill[rank] += 1
            cur[i] = f
        for section in ('D', 'A', 'B', 'C'):
            if section == 'B':
                bill.update(spaces[cur[q]][2] for q in w['ret'])
            for f, target, sources in w[section]:
                for i in [target, *sources]:
                    move(i, f)
        for i, f in enumerate(w['final']):
            move(i, f)
        return hist(bill)
    need(dimension_only(bad) == dimension_only(word), 'same-histogram frame mutant premise')
    need(all([g[1:] for g in bad[s]] == [g[1:] for g in word[s]] for s in ('D', 'A', 'B', 'C')),
         'same-scalar-program frame mutant premise')
    check('same-dimension gate frame', lambda: records(bad, spaces, zero), 'non-nested')
    for name, op, field, reason in (
        ('wrong MOVE invoice', 0, 4, 'MOVE rank'),
        ('wrong COPY invoice', 2, 5, 'COPY rank'),
        ('wrong ERASE metadata', 3, 5, 'ERASE metadata')):
        mutated = list(tape)
        i = next(i for i, e in enumerate(tape) if e[0] == op)
        e = list(mutated[i]); e[field] += 1; mutated[i] = tuple(e)
        check(name, lambda t=mutated: replay(word, spaces, t), reason)
    for name, section in (('missing dirty restoration', 'C'), ('omitted dirt compensation', 'D')):
        bad = deepcopy(word)
        if section == 'C':
            bad[section].pop(0)
        else:
            bad[section][0][2].pop()
        bad_tape = records(bad, spaces, zero)
        check(name, lambda: replay(bad, spaces, bad_tape), 'scalar endpoint')
    bad_tape = list(tape)
    i = next(i for i, e in enumerate(tape) if e[0] == 1 and e[5] == 3)
    e = list(bad_tape[i]); e[4] = word['start'][0]; bad_tape[i] = tuple(e)
    check('wrong scatter frame', lambda: replay(word, spaces, bad_tape), 'common frame')
    bad_tape = list(tape); bad_tape.pop(next(i for i, e in enumerate(tape) if e[0] == 3))
    check('missing temporary erase', lambda: replay(word, spaces, bad_tape), 'clean temporary')
    local = replay(word, spaces, tape)['profile']
    for name, mutate, reason in (
        ('idle overfill', lambda s: s['patterns'][0][1].append(8), 'exceeds capacity'),
        ('missing family', lambda s: s['patterns'][0].__setitem__(2, 221), 'family coverage'),
        ('wrong stage window', lambda s: s['stages'][0].__setitem__(2, 2), 'outside idle window'),
        ('missing hosted helper', lambda s: s['stages'][0].__setitem__(3, 221), 'allocation/pattern')):
        bad = deepcopy(selection); mutate(bad)
        check(name, lambda s=bad: global_ledger(local, s, word['v'], word['R']), reason)
    wrong = global_ledger(local, selection, word['v'], word['R'], replicas=31)
    check('wrong replica multiplicity', lambda: compare(wrong, global_result), 'ledger')
    bad = deepcopy(local); bad['1'] += 2; bad['2'] -= 1
    need(sum(int(k)*v for k, v in bad.items()) == sum(int(k)*v for k, v in local.items()),
         'rank-mass-preserving control premise')
    check('rank-mass-preserving histogram mutation', lambda: compare(bad, local), 'ledger')
    check('corrupt source pin', lambda: check_digest(b'bad', digest(b'good')), 'source digest')
    return passed


def compute():
    raw = inputs()
    config = raw[VENDOR+'e8-r740-replica32/code/config.py'].decode()
    need('\nREPLICAS = 32\n' in config, 'replica source binding')
    selection = json.loads(raw[BIT+'data/selection9-p111.json'])['bit']
    reports, words, all_spaces, all_tapes = {}, {}, {}, {}
    for label, word_path, expected_path in (
        ('PR555', BIT+'data/bitE8mut-p111.json.gz', BIT+'EXPECTED.json'),
        ('PR589', BIT+'tune/bitE8mut-p111-tuned.json.gz', BIT+'tune/EXPECTED.json')):
        word = json.loads(gzip.decompress(raw[word_path]))
        expected = json.loads(raw[expected_path])
        need(digest(canonical(word)) == expected['word']['content_sha256'], 'word payload binding')
        spaces, zero = geometry(word)
        tape = records(word, spaces, zero)
        forward, reverse = replay(word, spaces, tape), replay(word, spaces, tape, True)
        need(forward == reverse, 'forward/reverse ledger')
        need(forward['profile'] == expected['word']['local_histogram'], 'local histogram')
        copies = [e[5] for e in tape if e[0] == 2]
        need(forward['rank_mass'] == H*word['R']+2*word['v']*(H-1)+sum(copies),
             'local telescoping rank mass')
        need({'records': len(tape), 'common_frame_ADDs': forward['counts']['adds'],
              'rank_mass': forward['rank_mass']} == expected['word']['legality'], 'record inventory')
        need(copies == expected['word']['copy_ranks'], 'COPY ranks')
        global_result = global_ledger(forward['profile'], selection, word['v'], word['R'])
        need(global_result['profile'] == expected['nine']['profile'], 'nine-stage histogram')
        need(global_result['rank_mass'] == expected['nine']['bit']['rank_mass'], 'global rank mass')
        need(global_result['deficit'] == 32*(8*word['v']-9*sum(copies)), 'global coverage identity')
        reports[label] = {'local': forward, 'copy_ranks': copies, 'global': global_result,
                          'frames': len(spaces), 'projectors_sha256': digest(canonical(spaces)),
                          'record_bytes_sha256': digest(b''.join(struct.pack('<6i', *e) for e in tape)),
                          'word_payload_sha256': digest(canonical(word))}
        words[label], all_spaces[label], all_tapes[label] = word, spaces, tape
    assembly = json.loads(raw['research/community-frontier1094-audit/ASSEMBLY.json'])
    supplier = assembly['bit_supplier']
    need(supplier['path'] == BIT+'tune/EXPECTED.json' and supplier['commit'] ==
         'a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46', 'assembly supplier identity')
    need(assembly['input_sha256'].get('package:inputs/PR589-EXPECTED.json') ==
         digest(raw[BIT+'tune/EXPECTED.json']), 'assembly expected-record digest')
    need(supplier['derived_deficit'] == reports['PR589']['global']['deficit'], 'assembly deficit')
    delta = {str(k): reports['PR589']['local']['profile'].get(str(k), 0)-
                    reports['PR555']['local']['profile'].get(str(k), 0) for k in range(1, H+1)}
    delta = {k: v for k, v in delta.items() if v}
    need(delta == {'1': 2, '3': -1, '4': -3, '6': 1, '7': 1}, 'transport delta')
    word, spaces, tape = words['PR589'], all_spaces['PR589'], all_tapes['PR589']
    zero = next(i for i, p in enumerate(spaces) if p[2] == 0)
    checks = controls(word, spaces, zero, tape, reports['PR589']['global'], selection)
    return {'status': 'PASS_BIT589_PROJECTOR_LEDGER', 'result_kind': 'independent finite audit',
            'suppliers': reports, 'local_profile_delta': delta, 'negative_controls': checks,
            'scope': 'Exact local frame/scalar/record and fixed-selection accounting; physical, compiler, precision and analytic obligations remain.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', action='store_true', help='create RESULT.json exclusively')
    args = parser.parse_args()
    result = compute()
    path = HERE/'RESULT.json'
    if args.write_result:
        with path.open('x') as stream:
            stream.write(json.dumps(result, indent=2)+'\n')
    else:
        compare(result, json.loads(path.read_text()))
    print(result['status'], 'local_mass=5129 global_mass=1808352 deficit=10272',
          'controls='+str(len(result['negative_controls'])))


if __name__ == '__main__':
    main()

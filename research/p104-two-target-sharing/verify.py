#!/usr/bin/env python3
"""Exact fixed-certificate replay; imports no generator or predecessor checker.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
"""
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
ROOT = HERE.parent.parent
INPUT = ROOT / 'research/p104-native-channel/inputs'
PINS = {
    'LOWRANK-WITNESS.json': '0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e',
    'P104-FIXTURE.json': '516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4',
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def unique(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def read(path):
    return json.loads(path.read_text(), object_pairs_hook=unique)


def frame(basis):
    need(isinstance(basis, list), 'frame basis is not a list')
    space = {0}
    for v in basis:
        need(type(v) is int and 0 < v < 512 and v not in space, 'invalid binary basis')
        space |= {x ^ v for x in tuple(space)}
    return frozenset(space)


def reconstruct(fixture):
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            roots.add(tuple(row))
    for signs in product((-1, 1), repeat=7):
        if signs.count(-1) % 2 == 0:
            roots.add((1, *signs))
    p = fixture['section4_explicit_P104']
    ports = sorted(roots - set(map(tuple, p['F0'] + p['C'])))
    need(len(ports) == 104, 'wrong puncture')
    half = [[Q(sum(a*b for a, b in zip(x, y)), 8) for y in ports] for x in ports]
    need(all(half[i][i] == 1 for i in range(104)), 'root norm')
    correction = [[Q(int(t == s)) - half[t][s] for s in range(104)] for t in (0, 1)]
    return half, correction


def premise_check(word, correction):
    supports = [{s for s in range(104) if correction[t][s]} for t in (0, 1)]
    union, shared = supports[0] | supports[1], supports[0] & supports[1]
    need([len(s) for s in supports] == [48, 48], 'correction support')
    need(len(union) == 78 and len(shared) == 18, 'union support')
    ends = [frame(word['final_frames'][f'Y{t}']) for t in (0, 1)]
    need([len(h) for h in ends] == [256, 256] and len(ends[0] & ends[1]) == 128,
         'endpoint/intersection dimensions')
    paths = {r: [frame(f)] for r, f in word['initial_frames'].items()}
    for e in word['program']:
        op, dst = e[:2]
        if op == 'transport' and dst in paths:
            need(paths[dst][-1] == frame(e[2]), 'source path continuity')
            paths[dst].append(frame(e[3]))
        if op in ('add', 'copy'):
            need(not e[2].startswith('Y') and not dst.startswith('X'), 'original data contract')
    for r, path in paths.items():
        if r.startswith(('X', 'Y')):
            need(all(a <= b for a, b in zip(path, path[1:])), 'nonmonotone data path')
    lines = {s: frame(word['initial_frames'][f'X{s}']) for s in union}
    need(len(set(lines.values())) == 78 and all(len(v) == 2 for v in lines.values()),
         'initial source lines not distinct')
    witnesses = []
    for t in (0, 1):
        yp = paths[f'Y{t}']
        need(all(v <= ends[t] for v in yp), 'target path leaves endpoint')
        for s in sorted(supports[t]):
            xp, line = paths[f'X{s}'], lines[s]
            need(line <= ends[t] and len(xp) > 1, 'initial source access')
            need(all(v == line for v in xp if v <= ends[t]), 'late contained source access')
            need(all(v != line for v in yp), 'direct target source access')
            escape = sorted(xp[1] - ends[t])
            need(escape, 'missing first-expansion escape')
            witnesses.append([t, s, next(v for v in line if v), escape[0]])
    ratios = Counter(str(correction[1][s]/correction[0][s]) for s in shared)
    need(ratios == {'-1': 9, '1': 9}, 'shared total independence')
    need(all(lines[s] <= ends[0] & ends[1] for s in shared), 'shared source frame')
    return {'union': sorted(union), 'shared': sorted(shared),
            'exclusive': [sorted(supports[t] - shared) for t in (0, 1)],
            'escape_witnesses': witnesses, 'shared_ratios': dict(sorted(ratios.items()))}


def add_rows(left, right, coefficient):
    result = dict(left)
    for key, value in right.items():
        value = result.get(key, Q(0)) + coefficient*value
        if value:
            result[key] = value
        else:
            result.pop(key, None)
    return result


def replay(word, circuit, gram_half):
    new = circuit['initial_frames'] if circuit else {}
    names = list(word['initial_frames']) + sorted(new)
    need(len(names) == len(set(names)), 'aliased new helper')
    rows = {name: {name: Q(1)} for name in names}
    frames = {name: frame(f) for name, f in {**word['initial_frames'], **new}.items()}
    full = frozenset(range(512))
    for name in new:
        need(name.startswith('N') and frames[name] == {0}, 'new entrance')
        need(frame(circuit['final_frames'][name]) == full, 'new exit')
    insertion = {}
    if circuit:
        for item in circuit['insertions']:
            cut = item['completed_cut']
            need(type(cut) is int and 0 <= cut <= len(word['program']) and cut not in insertion,
                 'bad insertion cut')
            insertion[cut] = item['events']
    all_profile, extra_profile, coefficients = Counter(), Counter(), Counter()
    source_reads, events, extra_adds = 0, 0, 0
    max_l1, denominator_bits = Q(1), 0

    def execute(e, added):
        nonlocal source_reads, events, extra_adds, max_l1, denominator_bits
        need(isinstance(e, list) and e, 'bad event')
        op, dst = e[:2]
        events += 1
        if added:
            need(op in ('add', 'transport'), 'new operation outside alphabet')
            need(dst in new or dst in ('Y0', 'Y1'), 'new destination outside contract')
        if op == 'add':
            _, dst, src, coefficient, declared = e
            need(dst != src and dst in rows and src in rows, 'ADD role')
            f = frame(declared)
            need(frames[dst] == frames[src] == f, 'ADD frame')
            need(type(coefficient) in (str, int), 'invalid coefficient type')
            c = Q(coefficient)
            need(c and c.denominator & (c.denominator-1) == 0, 'non-dyadic or zero ADD')
            if added:
                need(src in new or src.startswith('X'), 'prohibited original helper/target read')
                if dst in ('Y0', 'Y1'):
                    need(src in new, 'new direct source-target contact')
                extra_adds += 1
                source_reads += int(src.startswith('X'))
                coefficients[str(c)] += 1
            rows[dst] = add_rows(rows[dst], rows[src], c)
        elif op == 'transport':
            _, dst, before, after, cost = e
            a, b = frame(before), frame(after)
            need(dst in rows and frames[dst] == a, 'transport entrance')
            need(a <= b or b <= a, 'nonnested transport')
            need(type(cost) is int and cost == abs(len(after)-len(before)) and cost > 0,
                 'transport invoice')
            if added:
                need(dst in new and a < b, 'nonmonotone new lifetime')
                extra_profile[cost] += 1
            elif b < a:
                need(dst == 'C', 'unexpected original descent')
            all_profile[cost] += 1
            frames[dst] = b
        elif op == 'zero':
            _, dst, declared = e
            need(dst not in rows and dst == 'C', 'private allocation')
            rows[dst], frames[dst] = {}, frame(declared)
        elif op == 'copy':
            _, dst, src, declared = e
            need(dst == 'C' and not rows[dst] and frames[dst] == frames[src] == frame(declared),
                 'private copy')
            rows[dst] = dict(rows[src])
        elif op == 'erase':
            _, dst, declared = e
            need(dst == 'C' and frames[dst] == frame(declared), 'private discard')
            del rows[dst], frames[dst]
            return
        else:
            raise ValueError('unknown operation')
        max_l1 = max(max_l1, sum(map(abs, rows[dst].values()), Q(0)))
        for v in rows[dst].values():
            need(v.denominator & (v.denominator-1) == 0, 'nondyadic row')
            denominator_bits = max(denominator_bits, v.denominator.bit_length()-1)

    for cut in range(len(word['program'])+1):
        for event in insertion.get(cut, []):
            execute(event, True)
        if cut < len(word['program']):
            execute(word['program'][cut], False)
    expected_frames = {**word['final_frames'], **(circuit['final_frames'] if circuit else {})}
    need(set(rows) == set(names) == set(expected_frames), 'endpoint registers')
    for name, f in expected_frames.items():
        need(frames[name] == frame(f), 'endpoint frame')
        expected = {name: Q(1)}
        if name.startswith('Y'):
            t = int(name[1:])
            transfer = [Q(int(t == s)) for s in range(104)] if circuit and t in (0, 1) else gram_half[t]
            for s, c in enumerate(transfer):
                if c:
                    expected[f'X{s}'] = c
        need(rows[name] == expected, 'endpoint coefficients: '+name)
    canonical = [[name, [[c, str(v)] for c, v in sorted(row.items())]]
                 for name, row in sorted(rows.items())]
    digest = sha256(json.dumps(canonical, separators=(',', ':')).encode()).hexdigest()
    return {'columns': len(names), 'events': events, 'endpoint_sha256': digest,
            'paid_profile': dict(sorted(all_profile.items())),
            'added_profile': dict(sorted(extra_profile.items())),
            'rank_mass': sum(k*v for k, v in all_profile.items()),
            'added_rank_mass': sum(k*v for k, v in extra_profile.items()),
            'added_transports': sum(extra_profile.values()), 'added_ADDs': extra_adds,
            'added_ADD_coefficients': dict(sorted(coefficients.items())),
            'added_source_reads': source_reads,
            'ideal_prefix_l1': str(max_l1), 'ideal_denominator_bits': denominator_bits}


def controls(word, circuit, gram_half, correction):
    rejected = []

    def bad(name, mutate, reason='endpoint coefficients:'):
        candidate = deepcopy(circuit)
        mutate(candidate)
        try:
            replay(word, candidate, gram_half)
        except ValueError as exc:
            need(reason in str(exc), 'control failed at unintended check: '+name+': '+str(exc))
            rejected.append(name)
        else:
            raise ValueError('control accepted: '+name)

    def remove_first(c, which, predicate):
        events = c['insertions'][which]['events']
        events.pop(next(i for i, e in enumerate(events) if predicate(e)))

    bad('dirty-compensation-omission', lambda c: c['insertions'][0]['events'].pop(0))
    bad('capture-omission', lambda c: remove_first(c, 0, lambda e: e[0] == 'add' and e[2].startswith('X')))
    bad('unmerge-omission', lambda c: remove_first(c, 1, lambda e: e[0] == 'add' and e[1].startswith('N') and e[2].startswith('N')))
    bad('source-cleanup-omission', lambda c: c['insertions'][1]['events'].pop())

    def delivery(c):
        e = next(e for e in c['insertions'][1]['events'] if e[0] == 'add' and e[1] == 'Y1' and Q(e[3]) == 2)
        e[3] = '1'
    bad('half-total-delivery-factor', delivery)

    def shear(c):
        e = next(e for e in c['insertions'][0]['events'] if e[0] == 'add' and e[1].startswith('N') and e[2].startswith('N') and Q(e[3]) == Q(-1, 2))
        e[3] = '1/2'
    bad('shared-basis-sign', shear)

    def bill(c):
        e = next(e for e in c['insertions'][0]['events'] if e[0] == 'transport')
        e[4] += 1
    bad('underived-transport-charge', bill, 'transport invoice')
    bad('early-delivery', lambda c: c['insertions'][1].update(completed_cut=1), 'ADD frame')

    def wrong_frame(c):
        e = next(e for e in c['insertions'][1]['events'] if e[0] == 'add' and e[1] == 'Y0')
        e[4] = []
    bad('wrong-target-frame', wrong_frame, 'ADD frame')

    def wrong_read(c):
        c['insertions'][0]['events'][0][2] = 'Q0'
    bad('forbidden-original-helper-read', wrong_read, 'prohibited original helper/target read')

    w = deepcopy(word)
    _, s, _, _ = premise_check(word, correction)['escape_witnesses'][0]
    e = next(e for e in w['program'] if e[0] == 'transport' and e[1] == f'X{s}')
    # Alter the first before-frame, explicitly testing the path binding.
    e[2] = []
    try:
        premise_check(w, correction)
    except ValueError as exc:
        need('source path continuity' in str(exc), 'wrong source path rejection')
        rejected.append('source-path-continuity-drift')
    else:
        raise ValueError('source-path control accepted')
    changed = deepcopy(circuit)
    # Reverse each distinct list exactly once: the loaded JSON has no aliases.
    for f in [*changed['initial_frames'].values(), *changed['final_frames'].values()]:
        f.reverse()
    for item in changed['insertions']:
        for e in item['events']:
            if e[0] == 'add':
                e[4].reverse()
            else:
                e[2].reverse(); e[3].reverse()
    replay(word, changed, gram_half)
    return {'rejected': rejected, 'accepted': ['equivalent-binary-bases']}


def verify(regenerate=False):
    for name, digest in PINS.items():
        need(sha256((INPUT/name).read_bytes()).hexdigest() == digest, 'source hash: '+name)
    word, fixture, circuit = read(INPUT/'LOWRANK-WITNESS.json'), read(INPUT/'P104-FIXTURE.json'), read(HERE/'CIRCUIT.json')
    need(type(circuit['schema_version']) is int and circuit['schema_version'] == 1
         and circuit['targets'] == [0, 1] and all(type(x) is int for x in circuit['targets']),
         'circuit schema/targets')
    need(circuit['source_witness_sha256'] == PINS['LOWRANK-WITNESS.json'], 'circuit source binding')
    gram_half, correction = reconstruct(fixture)
    premises = premise_check(word, correction)
    need(circuit['shared'] == premises['shared'] and circuit['exclusive'] == premises['exclusive'], 'group declarations')
    need(set(circuit['initial_frames']) == {f'N{s}' for s in premises['union']}, 'helper/source bijection')
    need(set(circuit['final_frames']) == set(circuit['initial_frames']), 'lifetime endpoints')
    baseline = replay(word, None, gram_half)
    separate = replay(word, read(HERE/'SEPARATE.json'), gram_half)
    need(separate['columns'] == 376 and separate['added_profile'] == {1: 192, 7: 96}
         and separate['added_ADDs'] == 384 and separate['added_rank_mass'] == 864,
         'no-sharing reference invoice')
    result = replay(word, circuit, gram_half)
    need(result['added_profile'] == {1: 142, 2: 16, 6: 18, 7: 60}, 'added profile')
    need(result['added_ADDs'] == 440 and result['added_source_reads'] == 156, 'scalar invoice')
    need(result['columns'] == 358 and result['events'] == 4734 and result['added_rank_mass'] == 702,
         'complete finite domain')
    tests = controls(word, circuit, gram_half, correction)
    if regenerate:
        with tempfile.TemporaryDirectory(prefix='p104-two-target-regenerate-') as d:
            output = Path(d)/'circuit.json'
            subprocess.run([sys.executable, '-I', '-B', str(HERE/'build.py'), '--out', str(output)], check=True)
            need(read(output) == circuit, 'regenerated complete circuit payload')
            reference = Path(d)/'separate.json'
            subprocess.run([sys.executable, '-I', '-B', str(HERE/'build.py'), '--separate', '--out', str(reference)], check=True)
            need(read(reference) == read(HERE/'SEPARATE.json'), 'regenerated no-sharing payload')
    return {'schema_version': 1, 'scope': 'two-target logical common-chart word; no_new_kappa',
            'targets': [0, 1], 'minimum_helper_lifetimes': 78,
            'minimum_rank_mass_under_zero_full_boundary': 702,
            'premises': premises, 'baseline': baseline, 'separate': separate,
            'result': result, 'controls': tests}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='exclusive receipt output, after fixed-result comparison')
    parser.add_argument('--emit-initial-result', type=Path, help='explicit authoring only; exclusive generation')
    parser.add_argument('--regenerate', action='store_true')
    args = parser.parse_args()
    need(not (args.out and args.emit_initial_result), 'choose one output mode')
    result = json.loads(json.dumps(verify(args.regenerate)))
    if not args.emit_initial_result:
        need(read(HERE/'RESULT.json') == result, 'fixed receipt mismatch')
    output = args.emit_initial_result or args.out
    if output:
        with output.open('x') as stream:
            json.dump(result, stream, indent=2, sort_keys=True); stream.write('\n')
    print('PASS_P104_TWO_TARGET_SHARING targets=2 lifetimes=78 columns=358 added_rank=702 added_ADD=440 controls=11+1 no_new_kappa')


if __name__ == '__main__':
    main()

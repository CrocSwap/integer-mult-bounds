#!/usr/bin/env python3
"""Dense dyadic-integer and binary-elimination audit; imports no package code.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
This is a second implementation by the same AI-assisted contributor, not an
independent human review. The inherited contracts are credited in README.md.
"""
from collections import Counter
from copy import deepcopy
from functools import reduce
from hashlib import sha256
from itertools import combinations, product
import json
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
NATIVE = HERE.parent / 'p104-native-channel' / 'inputs'


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def load(path, digest):
    raw = path.read_bytes()
    require(sha256(raw).hexdigest() == digest, 'input hash')
    return json.loads(raw)


def echelon(vectors):
    pivots = {}
    for original in vectors:
        require(type(original) is int and 0 < original < 512, 'binary vector')
        value = original
        for bit in sorted(pivots, reverse=True):
            if value >> bit & 1:
                value ^= pivots[bit]
        require(value != 0, 'dependent basis')
        bit = value.bit_length() - 1
        for other in pivots:
            if pivots[other] >> bit & 1:
                pivots[other] ^= value
        pivots[bit] = value
    return tuple(pivots[bit] for bit in sorted(pivots, reverse=True))


def contained(A, B):
    for value in A:
        for row in B:
            if value >> (row.bit_length()-1) & 1:
                value ^= row
        if value:
            return False
    return True


def dyadic(text):
    require(type(text) in (int, str), 'exact coefficient type')
    pieces = str(text).split('/')
    require(len(pieces) in (1, 2), 'coefficient syntax')
    n, d = int(pieces[0]), int(pieces[1]) if len(pieces) == 2 else 1
    require(d > 0 and n != 0, 'nonzero rational coefficient')
    g = gcd(abs(n), d)
    n, d = n//g, d//g
    require(d & (d-1) == 0, 'dyadic denominator')
    return n, d.bit_length()-1


def normalize(values, exponent):
    divisor = reduce(gcd, values, 0)
    shift = min(exponent, (abs(divisor) & -abs(divisor)).bit_length()-1) if divisor else exponent
    return [v >> shift for v in values], exponent-shift


def roots240(fixture):
    roots = set()
    for positions in combinations(range(8), 2):
        for signs in product((-2, 2), repeat=2):
            row = [0]*8
            for index, value in zip(positions, signs):
                row[index] = value
            roots.add(tuple(row))
    roots.update(s for s in product((-1, 1), repeat=8) if sum(x == -1 for x in s) % 2 == 0)
    require(len(roots) == 240, '240 roots')
    lines = set()
    for root in roots:
        first = next(x for x in root if x)
        lines.add(root if first > 0 else tuple(-x for x in root))
    p = fixture['section4_explicit_P104']
    ports = sorted(lines - set(map(tuple, p['F0'] + p['C'])))
    require(len(lines) == 120 and len(ports) == 104, 'canonical P104 lines')
    return [[sum(x*y for x, y in zip(a, b)) for b in ports] for a in ports]


def replay(word, circuit, dots):
    extra = circuit['initial_frames'] if circuit else {}
    require(not set(extra) & set(word['initial_frames']), 'helper alias')
    frames = {r: echelon(f) for r, f in {**word['initial_frames'], **extra}.items()}
    names = sorted(frames)
    positions = {r: i for i, r in enumerate(names)}
    rows = {r: ([int(j == i) for j in range(len(names))], 0) for r, i in positions.items()}
    require(all(not frames[r] for r in extra), 'dirty entry')
    added_at = {}
    if circuit:
        require(circuit['targets'] == [0, 1, 2], 'targets')
        for item in circuit['insertions']:
            cut = item['completed_cut']
            require(type(cut) is int and 0 <= cut <= len(word['program']) and cut not in added_at, 'cut')
            added_at[cut] = item['events']
    profile, added, counts = Counter(), Counter(), Counter()
    peak_n, peak_e, max_e = 1, 0, 0

    def step(e, fresh):
        nonlocal peak_n, peak_e, max_e
        op, dst = e[:2]
        counts['events'] += 1
        if fresh:
            require(op in ('add', 'transport'), 'fresh alphabet')
        if op == 'transport':
            A, B = echelon(e[2]), echelon(e[3])
            require(dst in rows and frames[dst] == A, 'transport state')
            require(A != B and (contained(A, B) or contained(B, A)), 'nested frames')
            require(type(e[4]) is int and e[4] == abs(len(A)-len(B)), 'transport price')
            if fresh:
                require(dst in extra and contained(A, B), 'fresh upward helper')
                added[e[4]] += 1
            else:
                require(contained(A, B) or dst == 'C', 'private descent')
            frames[dst] = B
            profile[e[4]] += 1
        elif op == 'add':
            _, dst, src, q, F = e
            require(src in rows and dst in rows and src != dst, 'ADD role')
            require(frames[src] == frames[dst] == echelon(F), 'ADD frames')
            n, exponent = dyadic(q)
            a, ae = rows[dst]
            b, be = rows[src]
            common = max(ae, be+exponent)
            rows[dst] = normalize([(x << (common-ae)) + n*(y << (common-be-exponent))
                                   for x, y in zip(a, b)], common)
            if fresh:
                require(dst in extra or dst in ('Y0', 'Y1', 'Y2'), 'fresh destination')
                require(src in extra or src.startswith('X'), 'fresh source')
                counts['added_adds'] += 1
                counts['source_reads'] += int(src.startswith('X'))
        elif op == 'zero':
            require(dst == 'C' and dst not in rows, 'owned zero')
            rows[dst], frames[dst] = ([0]*len(names), 0), echelon(e[2])
            counts['private_allocations'] += 1
        elif op == 'copy':
            require(dst == 'C' and dst in rows and not any(rows[dst][0]), 'owned copy')
            require(frames[dst] == frames[e[2]] == echelon(e[3]), 'COPY frames')
            values, exponent = rows[e[2]]
            rows[dst] = (list(values), exponent)
            counts['private_copies'] += 1
        elif op == 'erase':
            require(dst == 'C' and dst in rows and frames[dst] == echelon(e[2]), 'owned discard')
            del rows[dst], frames[dst]
            counts['private_discards'] += 1
            return
        else:
            raise ValueError('operation')
        values, exponent = rows[dst]
        total = sum(map(abs, values))
        if total * (1 << peak_e) > peak_n * (1 << exponent):
            peak_n, peak_e = total, exponent
        max_e = max(max_e, exponent)

    for cut in range(len(word['program'])+1):
        for event in added_at.get(cut, []):
            step(event, True)
        if cut < len(word['program']):
            step(word['program'][cut], False)
    final = {**word['final_frames'], **(circuit['final_frames'] if circuit else {})}
    require(set(rows) == set(names) == set(final), 'final coverage')
    serialized = []
    for register in names:
        values, exponent = rows[register]
        denominator = 1 << exponent
        require(frames[register] == echelon(final[register]), 'exit frame')
        require(register not in extra or len(frames[register]) == 9, 'FULL exit')
        coefficients = []
        for column, value in zip(names, values):
            expected_eighths = 8 if register == column else 0
            if register.startswith('Y') and column.startswith('X'):
                t, s = int(register[1:]), int(column[1:])
                expected_eighths = 8*int(t == s) if circuit and t < 3 else dots[t][s]
            require(8*value == expected_eighths*denominator, 'endpoint coefficient')
            if value:
                g = gcd(abs(value), denominator)
                n, d = value//g, denominator//g
                coefficients.append([column, str(n) if d == 1 else f'{n}/{d}'])
        serialized.append([register, coefficients])
    g = gcd(peak_n, 1 << peak_e)
    n, d = peak_n//g, (1 << peak_e)//g
    return {**dict(sorted(counts.items())), 'helper_lifetimes': len(extra), 'input_columns': len(names),
            'endpoint_coefficients': len(names)**2, 'added_profile': dict(sorted(added.items())),
            'full_profile': dict(sorted(profile.items())), 'added_transports': sum(added.values()),
            'added_rank_mass': sum(r*n for r, n in added.items()),
            'full_rank_mass': sum(r*n for r, n in profile.items()),
            'logical_prefix_l1': str(n) if d == 1 else f'{n}/{d}', 'maximum_logical_denominator': 1 << max_e,
            'endpoint_sha256': sha256(json.dumps(serialized, separators=(',', ':')).encode()).hexdigest()}


def bound(word, dots):
    supports = [{s for s in range(104) if 8*int(t == s)-dots[t][s]} for t in range(3)]
    sources = sorted(supports[2] - supports[0] - supports[1])
    frames = {r: echelon(f) for r, f in word['initial_frames'].items() if r.startswith(('X', 'Y'))}
    H = echelon(word['final_frames']['Y2'])
    allowed = {s: set() for s in sources}
    direct_contacts = 0
    for cut in range(len(word['program'])+1):
        for s in sources:
            F = frames[f'X{s}']
            if contained(F, H):
                allowed[s].add(F)
            direct_contacts += int(F == frames['Y2'])
        if cut < len(word['program']):
            e = word['program'][cut]
            if e[0] == 'transport' and e[1] in frames:
                frames[e[1]] = echelon(e[3])
    core = [1, 3, 8, 11, 16, 19, 25, 28, 97, 99]
    checks = 0
    for a, b in combinations(core, 2):
        require(allowed[a] and allowed[b], 'antichain contacts')
        for A, B in product(allowed[a], allowed[b]):
            require(not contained(A, B) and not contained(B, A), 'antichain')
            checks += 1
    require(direct_contacts == 0, 'unexpected direct X-to-Y2 access')
    return {'exclusive_sources': sources, 'antichain_size': len(core),
            'frame_pairs': checks, 'direct_contacts': direct_contacts}


def main():
    word = load(NATIVE / 'LOWRANK-WITNESS.json', '0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e')
    fixture = load(NATIVE / 'P104-FIXTURE.json', '516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4')
    ancestor = load(HERE / 'inputs' / 'PR2460-CIRCUIT.json', 'ce1b033ae8b826eec87d70246a13a6034e177ef4863bf7f7c24631c79e5202c9')
    candidate = json.loads((HERE / 'CIRCUIT.json').read_text())
    receipt = json.loads((HERE / 'RESULT.json').read_text())
    dots = roots240(fixture)
    for name, circuit in [('original_channel', None), ('PR2460_literal', ancestor), ('candidate', candidate)]:
        require(json.loads(json.dumps(replay(word, circuit, dots))) == receipt[name], 'independent receipt: ' + name)
    proof = bound(word, dots)
    require(proof['exclusive_sources'] == receipt['exclusive_Y2_sources'], 'independent sources')
    faults = []
    for kind in ('delivery', 'cleanup', 'cut', 'price'):
        c = deepcopy(candidate)
        if kind in ('delivery', 'cleanup'):
            tail = next(ins['events'] for ins in c['insertions'] if ins['completed_cut'] == len(word['program']))
            prefix = ['add', 'Y2', 'LATE0'] if kind == 'delivery' else ['add', 'LATE0', 'X1']
            tail.pop(next(i for i, e in enumerate(tail) if e[:3] == prefix))
        elif kind == 'cut':
            next(ins for ins in c['insertions'] if ins['completed_cut'] == 669)['completed_cut'] = 668
        else:
            next(e for ins in c['insertions'] for e in ins['events'] if e[:2] == ['transport', 'LATE0'])[4] += 1
        try:
            replay(word, c, dots)
        except ValueError as error:
            expected = {'delivery': 'endpoint', 'cleanup': 'endpoint', 'cut': 'ADD frames', 'price': 'transport price'}[kind]
            require(expected in str(error), 'wrong fault rejection')
            faults.append(kind)
        else:
            raise ValueError('accepted independent fault: ' + kind)
    # These are intervals, not privileged event numbers: nearby legal cuts work.
    later = deepcopy(candidate)
    for ins in later['insertions']:
        if ins['completed_cut'] in (669, 842):
            ins['completed_cut'] += 1
    require(replay(word, later, dots) == replay(word, candidate, dots), 'legal later-cut control')
    print('PASS_INDEPENDENT_P104_LATE_Y2_S34 ' + json.dumps({**proof, 'rejected_controls': faults}, sort_keys=True))


if __name__ == '__main__':
    main()

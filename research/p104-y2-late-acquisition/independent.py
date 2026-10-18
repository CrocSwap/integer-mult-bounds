"""Second implementation: dense scaled integers and binary echelon frames.

Imports neither the builder nor the sparse checker. Apache-2.0, ywz65 + Codex.
"""
from collections import Counter
import copy
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]


def check(ok, message):
    if not ok:
        raise ValueError(message)


def echelon(vectors):
    pivots = {}
    for value in vectors:
        check(type(value) is int and 0 < value < 512, 'binary coordinate')
        for bit, row in sorted(pivots.items(), reverse=True):
            if (value >> bit) & 1:
                value ^= row
        if value:
            bit = value.bit_length()-1
            for k, row in list(pivots.items()):
                if (row >> bit) & 1:
                    pivots[k] ^= value
            pivots[bit] = value
    check(len(pivots) == len(vectors), 'independent basis')
    return tuple(row for _, row in sorted(pivots.items(), reverse=True))


def subset(a, b):
    for value in a:
        for row in b:
            if value & (1 << (row.bit_length()-1)):
                value ^= row
        if value:
            return False
    return True


def run(word, circuit, gram8):
    allframes = word['initial_frames'] | circuit['initial_frames']
    names = sorted(allframes)
    index = {name: i for i, name in enumerate(names)}
    state = {name: [4*int(i == index[name]) for i in range(len(names))] for name in names}
    frame = {name: echelon(v) for name, v in allframes.items()}
    insertions = {x['completed_cut']: x['events'] for x in circuit['insertions']}
    count = Counter()
    for cut in range(len(word['program'])+1):
        stream = [(e, True) for e in insertions.get(cut, [])]
        if cut < len(word['program']):
            stream.append((word['program'][cut], False))
        for e, added in stream:
            op = e[0]
            if op == 'transport':
                _, r, a, b, rank = e
                A, B = echelon(a), echelon(b)
                check(frame[r] == A and (subset(A, B) or subset(B, A)), 'physical frame adjacency')
                check(rank == abs(len(A)-len(B)), 'rank price')
                frame[r] = B
                if added:
                    check(subset(A, B), 'monotone new helper')
                    count[rank] += 1
            elif op == 'zero':
                _, r, f = e
                check(r not in frame, 'fresh private lifetime')
                frame[r], state[r] = echelon(f), [0]*len(names)
            elif op == 'erase':
                _, r, f = e
                check(frame[r] == echelon(f), 'discard frame')
                del frame[r], state[r]
            elif op == 'copy':
                _, r, s, f = e
                check(not any(state[r]) and frame[r] == frame[s] == echelon(f), 'zero/common-frame copy')
                state[r] = state[s][:]
            elif op == 'add':
                _, r, s, q, f = e
                check(r != s and frame[r] == frame[s] == echelon(f), 'common-frame ADD')
                q = Fraction(q)
                numerator = [x*q.numerator for x in state[s]]
                check(all(x % q.denominator == 0 for x in numerator), 'quarter-integer row lattice')
                state[r] = [a+b//q.denominator for a, b in zip(state[r], numerator)]
            else:
                raise ValueError('unknown event')
    check(set(state) == set(names), 'private storage closed')
    for r in names:
        expected = [4*int(i == index[r]) for i in range(len(names))]
        if r.startswith('Y'):
            t = int(r[1:])
            for s in range(104):
                # gram8 is the doubled-coordinate inner product: 4*(G/2)=gram8/2.
                expected[index[f'X{s}']] += 4*int(s == 2) if t == 2 else gram8[t][s]//2
        check(state[r] == expected, 'dense endpoint '+r)
        wanted = (word['final_frames'] | circuit['final_frames'])[r]
        check(frame[r] == echelon(wanted), 'dense endpoint frame '+r)
    return dict(sorted(count.items())), len(names)**2


def main():
    for rec in json.loads((P/'SOURCES.json').read_text())['files']:
        if rec.get('usage') == 'input':
            check(hashlib.sha256((ROOT/rec['path']).read_bytes()).hexdigest() == rec['sha256'], 'source drift')
    ip = ROOT/'research/p104-native-channel/inputs'
    word = json.loads((ip/'LOWRANK-WITNESS.json').read_text())
    fixture = json.loads((ip/'P104-FIXTURE.json').read_text())['section4_explicit_P104']
    rr = []
    for i in range(8):
        for j in range(i+1, 8):
            for sign in [-1, 1]:
                r = [0]*8
                r[i], r[j] = 2, sign*2
                rr.append(tuple(r))
    rr.extend((1, *tail) for tail in product([-1, 1], repeat=7) if sum(x == -1 for x in tail) % 2 == 0)
    rr = sorted(set(rr)-set(map(tuple, fixture['F0']+fixture['C'])))
    gram8 = [[sum(x*y for x, y in zip(a, b)) for b in rr] for a in rr]
    c = json.loads((P/'CIRCUIT.json').read_text())
    count, columns = run(word, c, gram8)
    receipt = json.loads((P/'RESULT.json').read_text())
    check({str(k): v for k, v in count.items()} == receipt['word']['added_profile'], 'independent invoice')
    h = echelon(word['final_frames']['Y2'])
    sources = receipt['access']['antichain_sources']
    access = {s: [echelon(word['initial_frames'][f'X{s}'])] for s in sources}
    for e in word['program']:
        if e[0] == 'transport' and e[1].startswith('X') and int(e[1][1:]) in access:
            s, frame = int(e[1][1:]), echelon(e[3])
            if subset(frame, h):
                access[s].append(frame)
    check(len(set(sources)) == 39 and all(gram8[2][s] and s != 2 for s in sources), '39 required source witnesses')
    for a, b in combinations(sources, 2):
        check(all(not subset(x, y) and not subset(y, x) for x in access[a] for y in access[b]), 'independent frame antichain')
    for which in ('compensation', 'cleanup'):
        bad = copy.deepcopy(c)
        if which == 'compensation':
            bad['insertions'][0]['events'].pop(0)
        else:
            bad['insertions'][-1]['events'].pop()
        try:
            run(word, bad, gram8)
        except ValueError:
            pass
        else:
            raise ValueError('independent fault accepted '+which)
    print(f'PASS_P104_Y2_INDEPENDENT coefficients={columns} antichain=39 controls=2')


if __name__ == '__main__':
    main()

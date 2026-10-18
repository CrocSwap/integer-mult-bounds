#!/usr/bin/env python3
"""Dense dyadic endpoint and echelon-frame audit; imports neither build nor verify.

ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
INPUT = HERE.parent / 'p104-native-channel' / 'inputs'


def require(ok, why):
    if not ok:
        raise RuntimeError(why)


def canonical(values):
    rows = [0]*9
    for value in values:
        require(isinstance(value, int) and 0 < value < 512, 'basis range')
        x = value
        for j in range(8, -1, -1):
            if x >> j & 1:
                if rows[j]:
                    x ^= rows[j]
                else:
                    rows[j] = x
                    break
        require(x != 0, 'basis dependence')
    for j in range(9):
        for k in range(j+1, 9):
            if rows[k] >> j & 1:
                rows[k] ^= rows[j]
    return tuple(x for x in rows if x)


def contains(big, small):
    pivots = {x.bit_length()-1: x for x in big}
    for v in small:
        while v:
            pivot = pivots.get(v.bit_length()-1)
            if pivot is None:
                return False
            v ^= pivot
    return True


def scalar(s):
    parts = str(s).split('/')
    n = int(parts[0]); d = int(parts[1]) if len(parts) == 2 else 1
    require(d > 0 and d & (d-1) == 0, 'dyadic scalar')
    return n, d.bit_length()-1


def audit(word, circuit, ports):
    init = {**word['initial_frames'], **circuit['initial_frames']}
    names = sorted(init); index = {name: i for i, name in enumerate(names)}
    n = len(names)
    values = {r: ([int(i == index[r]) for i in range(n)], 0) for r in names}
    frames = {r: canonical(f) for r, f in init.items()}
    events = circuit['insertions'][0]['events'] + word['program'] + circuit['insertions'][1]['events']
    profile = Counter()
    for e in events:
        op, dst = e[:2]
        if op == 'add':
            src = e[2]
            require(frames[dst] == frames[src] == canonical(e[4]), 'equal chart')
            a, ka = values[dst]; b, kb = values[src]
            q, kq = scalar(e[3]); k = max(ka, kb+kq)
            out = [(x << (k-ka)) + q*(y << (k-kb-kq)) for x, y in zip(a, b)]
            while k and all(x % 2 == 0 for x in out):
                out = [x//2 for x in out]; k -= 1
            values[dst] = out, k
        elif op == 'transport':
            a, b = canonical(e[2]), canonical(e[3])
            require(frames[dst] == a, 'frame continuity')
            require(contains(a, b) or contains(b, a), 'nested transport')
            require(e[4] == abs(len(a)-len(b)) and e[4] > 0, 'paid rank')
            profile[e[4]] += 1
            frames[dst] = b
        elif op == 'zero':
            require(dst == 'C' and dst not in values, 'owned zero')
            values[dst], frames[dst] = ([0]*n, 0), canonical(e[2])
        elif op == 'copy':
            require(dst == 'C' and not any(values[dst][0]), 'owned copy')
            require(frames[dst] == frames[e[2]] == canonical(e[3]), 'copy frame')
            values[dst] = (list(values[e[2]][0]), values[e[2]][1])
        elif op == 'erase':
            require(dst == 'C' and frames[dst] == canonical(e[2]), 'owned erase')
            del frames[dst], values[dst]
        else:
            raise RuntimeError('unknown op')
    require(set(values) == set(names), 'endpoint roles')
    for name, f in {**word['final_frames'], **circuit['final_frames']}.items():
        require(frames[name] == canonical(f), 'endpoint frame')
        expected = [0]*n
        expected[index[name]] = 8
        if name.startswith('Y'):
            t = int(name[1:])
            for s in range(104):
                expected[index[f'X{s}']] = (8*int(t == s) if t < 3 else
                    sum(ports[t][j]*ports[s][j] for j in range(8)))
        row, k = values[name]
        require(all(8*x == (y << k) for x, y in zip(row, expected)), 'endpoint coefficients '+name)
    return {'columns': n, 'endpoint_coefficients': n*n, 'events': len(events),
            'profile': dict(sorted(profile.items()))}


def main():
    for name, h in [('LOWRANK-WITNESS.json', '0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e'),
                    ('P104-FIXTURE.json', '516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4')]:
        require(sha256((INPUT/name).read_bytes()).hexdigest() == h, 'source pin')
    word = json.loads((INPUT/'LOWRANK-WITNESS.json').read_text())
    f = json.loads((INPUT/'P104-FIXTURE.json').read_text())['section4_explicit_P104']
    roots = set()
    for pair in combinations(range(8), 2):
        for s in (-2, 2):
            root = [0]*8; root[pair[0]] = 2; root[pair[1]] = s
            roots.add(tuple(root))
    for signs in product((-1, 1), repeat=8):
        if signs[0] == 1 and sum(x < 0 for x in signs) % 2 == 0:
            roots.add(signs)
    ports = sorted(roots.difference(map(tuple, f['F0']+f['C'])))
    require(len(ports) == 104, 'ports')
    circuit = json.loads((HERE/'CIRCUIT.json').read_text())
    result = audit(word, circuit, ports)
    receipt = json.loads((HERE/'RESULT.json').read_text())['circuit']
    require(result['columns'] == receipt['columns'] and result['events'] == receipt['events'], 'receipt counts')
    require({str(k): v for k, v in result['profile'].items()} == receipt['full_profile'], 'receipt histogram')
    for condition in ('missing-extra-compensation', 'wrong-third-delivery', 'missing-unmerge'):
        bad = deepcopy(circuit)
        before, after = [x['events'] for x in bad['insertions']]
        if condition == 'missing-extra-compensation':
            before.pop(next(i for i, e in enumerate(before) if e[0]=='add' and e[1].startswith('Y') and e[2].startswith('E')))
        elif condition == 'wrong-third-delivery':
            next(e for e in after if e[0]=='add' and e[1]=='Y2')[3] = '2'
        else:
            after.pop(next(i for i, e in enumerate(after) if e[0]=='add' and e[1].startswith('E')))
        try:
            audit(word, bad, ports)
        except RuntimeError as exc:
            require('endpoint coefficients' in str(exc), 'wrong control rejection')
        else:
            raise RuntimeError('mutation accepted: '+condition)
    print('PASS_P104_THIRD_TARGET_DENSE '+json.dumps(result, sort_keys=True)+' controls=3')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, ValueError, KeyError) as e:
        print('FAIL_P104_THIRD_TARGET_DENSE: '+str(e), file=sys.stderr)
        sys.exit(1)

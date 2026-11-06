#!/usr/bin/env python3
"""Independent reverse-row / interpolation oracle for a binary cut escape.

Jerry Chen / @CubeJerry, with substantial OpenAI Codex assistance.
Cinna Davis supplies the binary-query lineage; Ali Romman #6348/#6398,
thu-nmrc #6716 and zxv #6726 retain their source and caller credit.
Apache-2.0. No source implementation or author replay is imported.
"""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path


def need(ok, text):
    if not ok:
        raise ValueError(text)


def prefix(split_both):
    # Normalized literal binary supplier, x=0,y=1,a=2,b=3.
    out = [('swap', 0, 3), ('swap', 1, 2), ('swap', 2, 3),
           ('add', 0, 2, 1, 0), ('add', 3, 1, -1, 0),
           ('add', 2, 3, 1, 1), ('add', 3, 1, 1, 0),
           ('add', 0, 2, -1, 0), ('body', 2, 'L'), ('body', 3, 'L')]
    if not split_both:
        out += [('body', 3, 'R')]
    out += [('scale', 1, -1), ('add', 1, 0, 1, 1),
            ('body', 1, 'L'), ('body', 0, 'L'), ('scale', 1, -1)]
    return out


def suffix(split_both):
    out = [('body', 2, 'R')]
    if split_both:
        out += [('body', 3, 'R')]
    return out + [('add', 0, 1, 1, 1), ('body', 0, 'R'), ('body', 1, 'R'),
                  ('add', 0, 2, 1, 0), ('scale', 2, -1),
                  ('add', 2, 0, 1, 0), ('swap', 1, 3),
                  ('scale', 3, -1), ('add', 3, 1, 1, 0)]


def inv(word):
    out = []
    for gate in reversed(word):
        if gate[0] == 'add':
            out.append(gate[:3] + (-gate[3], gate[4]))
        elif gate[0] in ('swap', 'scale'):
            need(gate[0] == 'swap' or abs(gate[2]) == 1, 'Unit scale inverse')
            out.append(gate)
        else:
            raise ValueError('Inverse uses ordinary/control gates only')
    return out


def escape(two=True):
    G = ([('add', 0, 1, 1, 1), ('add', 2, 0, 1, 0),
          ('add', 1, 3, -1, 0), ('scale', 1, -1)] if two else
         [('add', 0, 1, 1, 1), ('add', 2, 0, 1, 0), ('swap', 0, 2)])
    handoff = [('swap', 0, 4), ('swap', 1, 5)] if two else [('swap', 2, 4)]
    final = [('swap', 2, 4), ('swap', 3, 5)] if two else [('swap', 2, 4)]
    before = prefix(two) + G
    return before + handoff + inv(G) + suffix(two) + final, before, G


def degree_bound(word, n):
    # Cancellation-free path support proves the interpolation degree bound.
    state = [{(0, 0)} for _ in range(n)]
    for g in word:
        if g[0] == 'add':
            state[g[1]] |= state[g[2]]
        elif g[0] == 'swap':
            state[g[1]], state[g[2]] = state[g[2]], state[g[1]]
        elif g[0] == 'body':
            d = (1, 0) if g[2] == 'L' else (0, 1)
            state[g[1]] = {(a+d[0], b+d[1]) for a, b in state[g[1]]}
        elif g[0] != 'scale':
            raise ValueError('Unknown gate')
    need(all(a <= 1 and b <= 1 for row in state for a, b in row),
         'Every output is polynomial of degree at most one in each body')
    return state


def reverse(word, n, left, right):
    """Pull each output functional backwards; S is its faithful regular swap."""
    out = []
    for output in range(n):
        row = [[0, 0] for _ in range(n)]
        row[output][0] = 1
        for g in reversed(word):
            op = g[0]
            if op == 'add':
                _, d, s, c, odd = g
                a, b = row[d]
                if odd:
                    a, b = b, a
                row[s][0] += c*a
                row[s][1] += c*b
            elif op == 'swap':
                row[g[1]], row[g[2]] = row[g[2]], row[g[1]]
            elif op == 'scale':
                row[g[1]] = [g[2]*a for a in row[g[1]]]
            elif op == 'body':
                t = left if g[2] == 'L' else right
                row[g[1]] = [t*a for a in row[g[1]]]
            else:
                raise ValueError('Unknown gate')
        out.append(row)
    return out


def polynomial(word, n):
    degree_bound(word, n)
    corners = {(a, b): reverse(word, n, a, b) for a in (0, 1) for b in (0, 1)}
    out = {}
    for i in range(n):
        for j in range(n):
            for s in (0, 1):
                v00, v10, v01, v11 = [corners[t][i][j][s]
                                     for t in ((0, 0), (1, 0), (0, 1), (1, 1))]
                for l, r, value in ((0, 0, v00), (1, 0, v10-v00),
                                    (0, 1, v01-v00), (1, 1, v11-v10-v01+v00)):
                    if value:
                        out[i, j, s, l, r] = value
    return out


def expected(two):
    n = 6 if two else 5
    out = {(0, 0, 0, 1, 1): 1, (0, 1, 1, 1, 1): 1,
           (1, 1, 0, 1, 1): 1, (2, 2, 1, 1, 0): 1,
           (3, 3, 1, 1, 0 if two else 1): 1, (4, 4, 0, 0, 1): 1}
    if two:
        out[5, 5, 0, 0, 1] = 1
    return n, out


def check_source(data):
    expected = 'e99e4287091c6ce4ec9a563cb9ac6f45be35ff1ef421b4efa8c200cb9d639d6c'
    need(sha256(data).hexdigest() == expected, 'Pinned #6726 caller source bytes')
    return expected


def main():
    source = Path(__file__).with_name('frozen').joinpath('caller6726.py').read_bytes()
    bound = check_source(source)
    try:
        check_source(source + b'\n')
    except ValueError:
        pass
    else:
        raise ValueError('Corrupt source accepted')
    receipt = {'schema': 'independent-reverse-interpolation/1', 'source_commit': '435bbe91fb28cb1d7a569ca70c6c4e9eb302d486',
               'source_sha256': bound, 'cases': [], 'controls': []}
    for two in (False, True):
        n, target = expected(two)
        word, before, G = escape(two)
        for gate in before:
            slots = gate[1:3] if gate[0] in ('add', 'swap') else gate[1:2]
            need(all(r < 4 for r in slots), 'Fresh arbitrary inputs untouched before handoff')
        kf = sum(g[0] == 'add' and g[4] for g in G)
        kr = sum(g[0] == 'add' and g[4] for g in inv(G))
        need((kf, kr) == (1, 1), 'Actual forward and inverse query counts')
        actual = polynomial(word, n)
        need(actual == target, 'Complete arbitrary-input endpoint')
        prefix_target = {(0, 2, 1, 1, 0): 1, (1, 3, 1, 1, 0): 1,
                         (2, 0, 0, 1, 0): 1, (2, 1, 1, 1, 0): 1,
                         (3, 1, 0, 1, 0): 1, (4, 4, 0, 0, 0): 1,
                         (5, 5, 0, 0, 0): 1}
        if two:
            need(polynomial(before, n) == prefix_target, 'Two-channel prefix before fresh handoff')
        original = polynomial(prefix(two) + suffix(two), 4)
        original_target = {(0, 0, 0, 1, 1): 1, (0, 1, 1, 1, 1): 1,
                           (1, 1, 0, 1, 1): 1, (2, 2, 1, 1, 1): 1,
                           (3, 3, 1, 1, 1): 1}
        need(original == original_target, 'Complete unchanged binary source endpoint')
        central = [i for i, g in enumerate(word) if g[0] == 'add' and g[4]]
        restor = central[-2]
        mutants = []
        bad = deepcopy(word); del bad[restor]; mutants.append(('missing_restore_query', bad))
        bad = deepcopy(word); bad[restor] = bad[restor][:4] + (0,); mutants.append(('ordinary_restore_query', bad))
        bad = deepcopy(word); del bad[len(before)]; mutants.append(('missing_fresh_handoff', bad))
        bad = deepcopy(word); del bad[-1]; mutants.append(('missing_output_swap', bad))
        for name, bad in mutants:
            need(polynomial(bad, n) != target, 'Reject ' + name)
            receipt['controls'].append({'two_channels': two, 'name': name})
        receipt['cases'].append({'channels': 2 if two else 1, 'inputs': n,
                                 'gates': len(word), 'coefficient_cells': n*n*8,
                                 'nonzero_coefficients': len(actual),
                                 'extra_forward_queries': kf, 'extra_restore_queries': kr,
                                 'canonical_endpoint': [[*key, value] for key, value in sorted(actual.items())]})
    data = json.dumps(receipt, sort_keys=True, separators=(',', ':')).encode()
    print(json.dumps(receipt, indent=2, sort_keys=True))
    print('CERTIFICATE_SHA256', sha256(data).hexdigest())
    print('PASS_INDEPENDENT_BINARY_RETIREMENT_REVERSE_INTERPOLATION')


if __name__ == '__main__':
    main()

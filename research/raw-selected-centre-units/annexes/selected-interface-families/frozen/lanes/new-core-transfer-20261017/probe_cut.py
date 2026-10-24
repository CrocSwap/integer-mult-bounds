#!/usr/bin/env python3
"""Read the candidate cut without importing source code."""
from pathlib import Path
from fractions import Fraction
import gzip
import json
import hashlib

HERE = Path(__file__).resolve().parent
INTERFACE = HERE.parent / 'circuit-interface' / 'INTERFACE.json'
WORDS = HERE.parents[1] / 'upstream-refresh-20261017' / 'pr3148' / 'research' / 'coupled-carrier-cap740' / 'words'


def add(row, other, q):
    for key, value in other.items():
        value = row.get(key, 0) + q * value
        if value:
            row[key] = value
        else:
            row.pop(key, None)


def step(rows, gate):
    op, target = gate[:2]
    if op == 'add':
        add(rows[target], rows[gate[2]], Fraction(gate[3], gate[4]))
    elif op == 'scale':
        q = Fraction(gate[2], gate[3])
        rows[target] = {key: q * v for key, v in rows[target].items()}
    elif op == 'warp':
        symbol = gate[2]
        rows[target] = {
            (source, word[:-1] if word and word[-1] == -symbol else word + (symbol,)): v
            for (source, word), v in rows[target].items()
        }
    else:
        raise ValueError(op)


def chronological(w):
    at = {}
    for number, gate in enumerate(w['warps'], 1):
        at.setdefault(gate[0], []).append(['warp', gate[1], number])
    result = []
    for index in range(len(w['B']) + 1):
        result.extend(at.get(index, []))
        if index < len(w['B']):
            result.append(w['B'][index])
    return result


def encode(row):
    return [[key[0], list(key[1]), str(v)] for key, v in sorted(row.items())]


def main():
    old = json.loads(INTERFACE.read_text())
    reports = {}
    for name in ['base', 'extra']:
        raw = gzip.decompress((WORDS / (name + '.json.gz')).read_bytes())
        require = {'base': '49bdc172f1f53253c15fa4bf5be2d5741701d2fe9d18943f8b79c3ded0b96a3e', 'extra': '34af6f955bf8d95f68868cc282fa739532a5a6117df50d753fd996d44cea6731'}
        if hashlib.sha256(raw).hexdigest() != require[name]:
            raise RuntimeError('Source word pin')
        w = json.loads(raw)
        live = sorted(set(range(704)) - set(w['removed']))
        rows = {r: {(r, ()): Fraction(1)} for r in live}
        for gate in w['A']:
            if not 112 <= gate[1] < 224:
                step(rows, gate)
        center = [rows[r] for r in w['centers']]
        source = [{str(k): str(v) for (k, word), v in row.items() if k < 112 and not word} for row in center]
        helper = [{str(k): str(v) for (k, word), v in row.items() if k >= 224 and not word} for row in center]
        mixed_words = [encode({key: v for key, v in row.items() if key[1]}) for row in center]
        response = {r: {} for r in live}
        for gate in w['cut']:
            add(response[gate[1]], {(w['centers'].index(gate[2]), ()): Fraction(1)}, Fraction(gate[3], gate[4]))
        for gate in chronological(w) + w['restore'] + w['cleanup']:
            if 112 <= gate[1] < 224:
                step(response, gate)
        krows = [{str(k): str(v) for (k, word), v in response[112 + p].items()} for p in range(112)]
        expected = [{str(i): str(Fraction(old['R'][i].get(str(p), '0')) / 4) for i in range(8) if old['R'][i].get(str(p), '0') != '0'} for p in range(112)]
        report = {
            'payload_sha256': hashlib.sha256(raw).hexdigest(),
            'ports_equal': w['ports'] == old['ports'],
            'R_equal': source == old['R'],
            'H_equal': helper == old['H'],
            'K_equal_R_transpose_over_4': krows == expected,
            'center_R': source,
            'center_H': helper,
            'center_operator_terms': mixed_words,
            'target_K': krows,
            'private_cold_roles': sorted(map(int, w['helper_final'])),
            'centers': w['centers'],
            'center_frames': w['center_frames'],
            'live': live,
        }
        reports[name] = report
        print(name, {key: value for key, value in report.items() if key.endswith('_equal') or key in ['ports_equal', 'K_equal_R_transpose_over_4']}, 'word terms', [len(x) for x in mixed_words], 'R/H terms', [sum(len(x) for x in source), sum(len(x) for x in helper)])
    (HERE / 'CUT-PROBE.json').write_text(json.dumps(reports, indent=2) + '\n')


if __name__ == '__main__':
    main()

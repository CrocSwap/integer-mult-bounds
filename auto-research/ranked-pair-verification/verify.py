#!/usr/bin/env python3
"""Offline exact profile/arithmetic checks; full physical replay is separate.

No network access or contributor arithmetic imports. This command never
regenerates a tracked certificate, so stale receipts fail rather than update.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import comb
from pathlib import Path
import gzip
import json
import re

from concave_dominance import certify
from independent_assembly import assemble
from independent_moment import encode, require, run

ROOT = Path(__file__).resolve().parent


def read(name):
    return json.loads((ROOT / name).read_text())


def main():
    selected = read('selected-certificate.json')
    manifest = read('finite-frames/source-word-manifest.json')
    caps = read('concave-dominance.json')
    N, m = comb(23, 3) * comb(25, 3), 575
    parts = {'data': Counter({1: 18*N, 21: 2*N, 17: 2*N, 481: 2*N}),
             'paid_endpoint_copy': Counter({1: N})}
    banks, L = [], 0
    lean_caps = (ROOT / 'lean/CappedMass.lean').read_text()
    for h in (23, 25):
        receipts = [read(f'finite-frames/pair-{kind}-{h}-receipt.json')
                    for kind in ('original', 'ranked')]
        old, new = receipts
        packed = (ROOT / f'finite-frames/pair-ranked-word-{h}.json.gz').read_bytes()
        raw = gzip.decompress(packed)
        word = json.loads(raw)
        digest = sha256(raw).hexdigest()
        require(digest == new['word_sha256'] == manifest['words'][str(h)]['word_sha256'],
                f'h{h} word hash binding')
        require(sha256(packed).hexdigest() == manifest['words'][str(h)]['gzip_sha256'],
                f'h{h} compressed word hash')
        profile = new['profile']
        R, v = profile['R'], comb(h, 3)
        require(word['h'] == h and word['R'] == R and word['v'] == v, 'word dimensions')
        require(R == old['profile']['R'] and new['pin'] == manifest['upstream_pin'],
                'construction provenance')
        require(new['compiler_source_sha256'] == old['compiler_source_sha256'] ==
                manifest['sources']['scripts/experiments/binary_frame_compiler.py'],
                'compiler source pin')
        require(new['graph_source_sha256'] == old['graph_source_sha256'] ==
                manifest['sources']['research/pair-assembly/pair_graph.py'], 'graph source pin')
        require(new['sort_key'] == manifest['compiler_transform']['new'], 'rank-order transform')
        blocks = profile['blocks']
        require(len(blocks) == h + 1 and blocks[0] == blocks[h] == 0, 'profile domain')
        require(all(type(n) is int and n >= 0 for n in blocks), 'integer multiplicities')
        require(sum(t*n for t, n in enumerate(blocks)) == h*R + h*(h-1), 'local rank mass')
        cap = certify(old['profile']['blocks'], blocks)
        recorded = next(row for row in caps['axes'] if row['h'] == h)
        for name, value in cap.items():
            require(encode(value) == recorded[name], f'h{h} cap receipt: {name}')
        definition = re.search(rf'def delta{h}Z :.*?(?=\n\n)', lean_caps, re.S)
        require(definition is not None, 'literal Lean profile definition')
        lean_delta = {int(t): int(n) for t, n in
                      re.findall(r'\| (\d+) => (-?\d+)', definition.group())}
        require(lean_delta == cap['signed_multiplicities'], 'Lean/finite profile binding')
        rep, bank = N // v, N // v * R
        banks.append(bank)
        L += rep * h * (h - 1)
        parts[f'internal_{h}'] = Counter({t: rep*n for t, n in enumerate(blocks) if t and n})
        parts[f'exterior_{h}'] = Counter({h: bank, m-2*h: bank})
        parts[f'data_growth_{h}'] = Counter({1: 2*N, h-2: 2*N})
    children = sum(parts.values(), Counter())
    W = 2*N + sum(banks)
    mass = sum(t*n for t, n in children.items())
    p = selected['bit']
    require((p['m'], p['N'], p['W'], p['L'], p['total_rank'], p['deficit'], p['maxchild'])
            == (m, N, W, L, mass, m*W-mass, max(children)), 'global dimensions')
    require(mass == m*W-N+L, 'global deficit identity')
    require(children == Counter({int(t): n for t, n in p['child_multiplicities'].items()}),
            'complete child multiplicities')
    require({name: dict(value) for name, value in parts.items()} ==
            {name: {int(t): n for t, n in value.items()} for name, value in p['parts'].items()},
            'all charged component counts')
    arithmetic = assemble(selected, Q(selected['bit_saving']), Q(selected['kappa']),
                          Q(selected['assembly']['parameters']['h']))
    require(encode(arithmetic) == read('selected-assembly-verification.json')['published'],
            'assembly receipt')
    require(encode(arithmetic['constraints']) == selected['assembly']['constraints'],
            '47 selected constraints')
    require(encode(arithmetic['margins']) == selected['assembly']['margins'], 'seven margins')
    require(encode(run(ROOT / 'selected-certificate.json', True)) ==
            read('selected-moment-verification.json'), 'exact characteristic/root receipt')
    lean_assembly = (ROOT / 'lean/ConcreteAssembly.lean').read_text()
    for name, value in [('a', selected['bit_saving']), ('kappa', selected['kappa']),
                        ('h', selected['assembly']['parameters']['h'])]:
        found = re.search(rf'def {name} : ℝ := (\d+) / (\d+)\n', lean_assembly)
        require(found is not None and Q(int(found[1]), int(found[2])) == Q(value),
                'Lean arithmetic parameter ' + name)
    print('PASS ranked pair: word hashes, all child counts, concrete Lean/profile binding, '
          'strict concave dominance, exact root bracket, 47 inequalities and seven margins')
    print('Scope: supplied finite profile and arithmetic; run the separate full word/CRT '
          'audit and Lean checker. Physical/analytic multiplication transfer remains external.')


if __name__ == '__main__':
    main()

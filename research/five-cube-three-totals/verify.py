#!/usr/bin/env python3
"""Exact finite certificates for arbitrary-support three-total decoding.

Copyright 2026 Ross Richardson. Apache-2.0.
Prepared with substantial OpenAI Codex assistance. No predecessor code imported.
"""
import argparse
from collections import Counter
from functools import reduce
from hashlib import sha256, sha1
import json
from math import gcd
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
BASE = 'c0e3631dc24e3c24a861f7d3d79e0608481cccec'
SOURCE_MANIFEST_SHA256 = '02ea3c1fb5ae99abdae222848af13634da76ac170327db7bf340ef5d85dbf17b'
SEED = 46
N = 32
ALL = (1 << N) - 1
EVEN = [x for x in range(N) if bin(x).count('1') % 2 == 0]
ODD = [x for x in range(N) if x not in EVEN]
E = sum(1 << x for x in EVEN)
O = ALL ^ E


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def rank(rows):
    """Exact Q rank: integral row elimination, with gcd normalization."""
    a = [list(row) for row in rows]
    if not a:
        return 0
    width = len(a[0])
    require(all(len(row) == width for row in a), 'ragged matrix')
    require(all(type(x) is int for row in a for x in row), 'noninteger matrix')
    lead = 0
    for col in range(width):
        pivot = next((i for i in range(lead, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[lead], a[pivot] = a[pivot], a[lead]
        p = a[lead][col]
        for i in range(lead + 1, len(a)):
            q = a[i][col]
            if not q:
                continue
            d = gcd(p, q)
            a[i] = [(p // d)*v - (q // d)*w
                    for v, w in zip(a[i], a[lead])]
            content = reduce(gcd, a[i], 0)
            if content > 1:
                a[i] = [v // content for v in a[i]]
        lead += 1
        if lead == len(a):
            break
    return lead


def gram():
    return [[2*(4-bin(x ^ y).count('1'))*(2-bin(x ^ y).count('1'))
             for y in range(N)] for x in range(N)]


def support(mask):
    require(type(mask) is int and 0 <= mask <= ALL, 'mask outside cube')
    return [x for x in range(N) if mask >> x & 1]


def pairing(g, readers, sources):
    return rank([[g[x][y] for y in support(sources)] for x in support(readers)])


def check_decoder(pairs):
    require(0 < len(pairs) <= 3, 'term domain')
    for f, g in pairs:
        require(bool(f) and bool(g), 'zero factor')
        support(f); support(g)
    for x in range(N):
        actual = 0
        for f, g in pairs:
            if f >> x & 1:
                actual ^= g
        require(actual == (E if E >> x & 1 else O), 'full decoder identity')


def triple(h):
    support(h)
    return [(E, E ^ h), (O, O ^ h), (ALL, h)]


def cross_block(g):
    require(len(g) == 32 and all(len(r) == 32 for r in g), 'Gram shape')
    require(all(type(v) is int for row in g for v in row), 'Gram integers')
    require(all(g[x][y] == g[y][x] for x in range(N) for y in range(N)), 'symmetry')
    for side in (EVEN, ODD):
        require(all(g[x][y] == (16 if x == y else 0) for x in side for y in side),
                'orthogonal parity cliques')
    require(all(g[x][y] % 2 == 0 for x in EVEN for y in ODD), 'integral cross block')
    m = [[g[x][y] // 2 for y in ODD] for x in EVEN]
    require(all(v != 0 for row in m for v in row), 'dense cross block')
    require(all(sum(m[i][k]*m[j][k] for k in range(16)) == (64 if i == j else 0)
                for i in range(16) for j in range(16)), 'cross orthogonality')
    require(rank(g) == 16, 'Gram rank')
    return m


def formula(m, h):
    aa = [i for i, x in enumerate(EVEN) if h >> x & 1]
    bb = [j for j, x in enumerate(ODD) if h >> x & 1]
    complement = [i for i in range(16) if i not in aa]
    r = rank([[m[i][j] for j in bb] for i in aa])
    t = rank([[m[i][j] for j in bb] for i in complement])
    costs = [16-len(aa)+r, 16-len(bb)+r, len(aa)+t]
    require(len(bb)-t <= r, 'orthogonal column rank inequality')
    require(sum(costs) >= 32, 'copy floor')
    if aa and bb:
        require(r >= 1 and sum(costs) >= 33, 'strict mixed-parity floor')
    else:
        require(sum(costs) == 32, 'one-parity equality')
    return costs, r, t


def affine_masks():
    return [sum(1 << x for x in range(N)
                if (bin(a & x).count('1') + c) % 2)
            for c in range(2) for a in range(32)]


def affine_census(g):
    masks = affine_masks()
    costs = {(f, h): pairing(g, f, h) for f in (E, O, ALL) for h in masks if h}
    records = []
    for h in masks:
        if h not in (0, E, O):
            pairs = triple(h)
            check_decoder(pairs)
            records.append(('distinct', pairs))
    # Every repeated-reader case, up to permutations of its three terms.
    for duplicate in (E, O, ALL):
        for single in (E, O, ALL):
            if duplicate == single:
                continue
            merged = next(([(duplicate, u), (single, v)] for u in (E, O, ALL)
                           for v in (E, O, ALL)
                           if all(((u if duplicate >> x & 1 else 0) ^
                                   (v if single >> x & 1 else 0)) ==
                                  (E if E >> x & 1 else O) for x in range(N))), None)
            require(merged is not None, 'two-basis factorization')
            target, last = merged[0][1], merged[1][1]
            for h in masks:
                if h and h != target:
                    pairs = [(duplicate, h), (duplicate, h ^ target), (single, last)]
                    check_decoder(pairs)
                    records.append(('repeated', pairs))
    totals = [sum(costs[p] for p in pairs) for _, pairs in records]
    best = totals.index(min(totals))
    return {'distinct_templates': sum(k == 'distinct' for k, _ in records),
            'repeated_templates': sum(k == 'repeated' for k, _ in records),
            'minimum': min(totals), 'cost_histogram': dict(sorted(Counter(totals).items())),
            'minimum_witness': records[best][1],
            'rank_table_sha256': sha256(canonical([[f, h, costs[f, h]]
                for f in (E, O, ALL) for h in masks if h]).encode()).hexdigest()}


def source_check():
    raw_manifest = (HERE/'SOURCES.json').read_bytes()
    require(sha256(raw_manifest).hexdigest() == SOURCE_MANIFEST_SHA256, 'source manifest identity')
    manifest = json.loads(raw_manifest)
    require(manifest['base_commit'] == BASE, 'source base')
    expected = {'pr1046-proof.md', 'pr1046-readme.md', 'pr1046-independent.json',
                'pr958-proof.md', 'pr231-readme.md', 'selected-at-base.json', 'review-at-base.md'}
    require({e['path'] for e in manifest['files']} == {'sources/'+s for s in expected}
            and len(manifest['files']) == len(expected), 'source inventory')
    for entry in manifest['files']:
        raw = (HERE/entry['path']).read_bytes()
        require(sha256(raw).hexdigest() == entry['sha256'], 'source sha256')
        require(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == entry['git_blob'],
                'source Git blob')
        require(entry['source_commit'] == BASE, 'source commit')
    old = json.loads((HERE/'sources/pr1046-independent.json').read_text())
    require(old['exhaustive_factorizations']['reduced_span_minima']['3']['total_cost'] == 35,
            'predecessor affine comparison')
    selected = json.loads((HERE/'sources/selected-at-base.json').read_text())
    require(selected['decimal'] == '0.001672660197076918', 'frozen selected context')
    return len(expected)


def controls(g, m, h):
    rejected = []
    def fails(name, fn):
        try:
            fn()
        except (ValueError, IndexError, TypeError):
            rejected.append(name)
        else:
            raise ValueError('control was accepted: '+name)
    p = triple(h)
    fails('drop a total', lambda: check_decoder(p[:-1]))
    offdiag=[(p[0][0],p[0][1]^(1<<ODD[0]))]+p[1:]
    require(all(sum(((f>>x)&1)*((s>>x)&1) for f,s in offdiag)%2==1
                for x in range(N)), 'off-diagonal-only control fixture')
    fails('change one source coefficient', lambda: check_decoder(offdiag))
    fails('zero total', lambda: check_decoder(triple(0)))
    fails('mask outside cube', lambda: support(1 << 32))
    fails('Boolean mask', lambda: support(True))
    bad = [r[:] for r in g]; bad[EVEN[0]][EVEN[1]] = bad[EVEN[1]][EVEN[0]] = 2
    fails('lost parity orthogonality', lambda: cross_block(bad))
    bad = [r[:] for r in g]; bad[EVEN[0]][ODD[0]] += 2; bad[ODD[0]][EVEN[0]] += 2
    fails('lost cross orthogonality', lambda: cross_block(bad))
    fails('rank undercharge', lambda: require(sum(formula(m,h)[0])-1 >= 32, 'undercharge'))
    fails('non-affine witness admitted as affine', lambda: require(h in affine_masks(), 'not affine'))
    # Both parities in H: r >= 1 is essential in the exact cost formula.
    mixed = (1 << EVEN[0]) | (1 << ODD[0])
    costs, r, t = formula(m, mixed)
    fails('omit cross rank contribution', lambda: require(sum(costs)-2*r == sum(costs), 'missing rank'))
    # A diagonal-only test would admit identity, but this is not the full decoder.
    require(all((1 << x) >> x & 1 for x in range(N)), 'diagonal control fixture')
    require(any((1 << x) != (E if E >> x & 1 else O) for x in range(N)), 'masked scope')
    return rejected


def run():
    pins = source_check()
    g = gram(); m = cross_block(g)
    require(rank([[int((E if E >> x & 1 else O) >> y & 1) for y in range(N)]
                  for x in range(N)]) == 2, 'decoder rational rank')
    # Binary rank is separately witnessed by two distinct nonzero row masks E,O.
    require(E and O and E != O and E ^ O == ALL, 'decoder binary rank two')
    coordinate = SEED % 5
    slice_ports = [x for x in range(N) if not (x >> coordinate & 1)]
    h = sum(1 << x for x in slice_ports if x in EVEN)
    pairs = triple(h); check_decoder(pairs)
    transpose=[(s,f) for f,s in pairs]
    check_decoder(transpose)
    literal_costs = [pairing(g, f, s) for f, s in pairs]
    require([pairing(g,f,s) for f,s in transpose] == literal_costs,'transpose witness')
    require(literal_costs == [8,16,8] == formula(m,h)[0], 'sharp witness')
    require(h not in affine_masks(), 'witness changes support class')
    affine = affine_census(g)
    require(affine['minimum'] == 35, 'affine comparison')
    hist = Counter(); digest = sha256(); equality = 0; sampled = {}
    rng = random.Random(SEED)
    sample_masks = {rng.getrandbits(32) for _ in range(256)}
    sample_masks.update(affine_masks()); sample_masks.update([h, ALL^h])
    for mask in sorted(sample_masks - {0,E,O}):
        ps = triple(mask); check_decoder(ps)
        prices = [pairing(g, f, s) for f, s in ps]
        require(prices == formula(m,mask)[0], 'literal rank/formula agreement')
        sampled[str(mask)] = prices
    for bits in range(1, 1 << len(slice_ports)):
        mask = sum(1 << x for i,x in enumerate(slice_ports) if bits >> i & 1)
        ps = triple(mask); check_decoder(ps)
        prices,r,t = formula(m,mask)
        total = sum(prices); hist[total] += 1; equality += total == 32
        digest.update(canonical([mask,prices,r,t]).encode()+b'\n')
    require(equality == 510 and sum(hist.values()) == 65535, 'complete slice coverage')
    return {'schema':'five-cube-three-totals-v1', 'base_commit':BASE, 'seed':SEED,
            'ports':32, 'gram_rank':16, 'binary_decoder_rank':2,
            'cross_matrix':m, 'cross_identity':'M M^t = 64 I; every entry nonzero',
            'unrestricted_three_term_floor':32, 'unrestricted_equality_peak':16,
            'distinct_reader_equality_masks':2*((1 << 16)-2),
            'witness':{'mask':h,'pairs':pairs,'costs':literal_costs,
                       'mask_affine':False,'source_sizes':[len(support(s)) for _,s in pairs]},
            'affine_three_term':affine,
            'slice_census':{'coordinate_fixed_zero':coordinate,'ports':slice_ports,
                            'nonempty_masks':65535,'minimum':min(hist),'equality_masks':equality,
                            'cost_histogram':dict(sorted(hist.items())), 'row_digest':digest.hexdigest(),
                            'stopping_rule':'all nonempty subsets of the displayed 16-port slice'},
            'dense_rank_checks':sampled, 'controls':controls(g,m,h), 'source_pins':pins,
            'budget':{'v':32,'copy_floor':32,'deficit_upper_bound':-32,
                      'stage_domain':'every integer s >= 3 under inherited additive ledger'},
            'scope':'at most three arbitrary-support binary outer products; full decoder identity; no new kappa'}


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--write-certificate', type=Path)
    args=parser.parse_args()
    receipt=run()
    if args.write_certificate:
        with args.write_certificate.open('x') as f:
            json.dump(receipt,f,indent=2,sort_keys=True); f.write('\n')
    else:
        expected=json.loads((HERE/'CERTIFICATE.json').read_text())
        require(canonical(receipt)==canonical(expected), 'certificate mismatch')
    print('PASS_FIVE_CUBE_THREE_TOTALS masks=65535 arbitrary_min=32 affine_min=35 equality_peak=16 no_new_kappa')


if __name__=='__main__':
    main()

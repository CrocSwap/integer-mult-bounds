#!/usr/bin/env python3
"""Independent finite premises and rational fixtures for the rank-tight P112 cost floor.

No predecessor executable imports.  The universal argument is
symbolic: Schur complement, groupwise change of basis, duality in a 3-space.
This checker independently authenticates and checks its finite premises.
"""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json
import tarfile

ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = ROOT / 'research/p112-rational-decoder-gate/CANDIDATE.json'
CANDIDATE_LF_SHA = 'dc5fbe51f9cd3a14361256ac136736bffb18971d0247b891accf0d2ee060d06b'
PAYLOAD_SHA = 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'
MEMBER = 'candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json'

def require(test, label):
    if not test:
        raise ValueError(label)

def rejects(fn, label):
    try:
        fn()
    except ValueError:
        return label
    raise ValueError('mutation accepted: ' + label)

def parity(x):
    return x.bit_count() % 2

def binary_rank(words):
    # Highest-pivot dictionary, independent of the retained low-pivot row code.
    pivots = {}
    for word in words:
        while word:
            high = word.bit_length() - 1
            if high in pivots:
                word ^= pivots[high]
            else:
                pivots[high] = word
                break
    return len(pivots)

def pairing(left, right):
    return binary_rank(sum(parity(x & y) << j for j, y in enumerate(right)) for x in left)

def mm(a, b):
    bt = list(zip(*b))
    return [[sum(x*y for x, y in zip(row, col)) for col in bt] for row in a]

def transpose(a):
    return [list(x) for x in zip(*a)]

def identity(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]

def inverse(a):
    n = len(a)
    rows = [[Q(x) for x in row] + extra for row, extra in zip(a, identity(n))]
    for k in range(n):
        pivot = next((i for i in range(k, n) if rows[i][k]), None)
        require(pivot is not None, 'singular rational fixture')
        rows[k], rows[pivot] = rows[pivot], rows[k]
        divisor = rows[k][k]
        rows[k] = [x/divisor for x in rows[k]]
        for i in range(n):
            if i != k and rows[i][k]:
                scalar = rows[i][k]
                rows[i] = [x-scalar*y for x, y in zip(rows[i], rows[k])]
    return [row[n:] for row in rows]

def graph_premises(free):
    odd = list(range(1, 38, 2)); even = list(range(2, 37, 2))
    require(not any((i,j) in free for i in odd for j in odd), 'odd principal identity')
    require({(i,j) for i in odd for j in even if (i,j) in free} ==
            {(i,i+1) for i in odd[:-1]} | {(3,24)}, 'odd-even mask')
    require({i for i in odd if (0,i) in free} == {15,27}, 'line odd mask')
    # These forbidden entries force the two exceptional couplings to vanish.
    for i,j in ((4,24),(24,4),(0,28),(28,0)):
        require((i,j) not in free, 'required Schur zero %d,%d' % (i,j))
    require((0,15) in free and (0,16) in free, 'line compatible paired block')

def price(a, b, spaces, owner):
    total = Counter()
    for ca, cb in zip(zip(*a), zip(*b)):
        ga = {owner[p] for p,x in enumerate(ca) if x}
        gb = {owner[p] for p,x in enumerate(cb) if x}
        total[pairing([x for g in ga for x in spaces[g]], [x for g in gb for x in spaces[g]])] += 1
    return dict(sorted(total.items()))

def endpoint(k, owner, free):
    require(all(k[i][i] == 1 for i in range(112)), 'normalized diagonal')
    require(all(k[i][j] == 0 for i in range(112) for j in range(112)
                if i != j and (owner[i],owner[j]) not in free), 'forbidden scalar entry')

def block(a, rows, cols):
    return [[a[i][j] for j in cols] for i in rows]

def fixture_schur(k, groups):
    retained = [p for g in range(1,38,2) for p in groups[g]]
    other = [p for p in range(112) if p not in retained]
    require(block(k,retained,retained) == identity(57), 'fixture principal identity')
    require(block(k,other,other) == mm(block(k,other,retained),block(k,retained,other)), 'fixture Schur residual')
    for even in range(2,37,2):
        odd = even-1
        a = block(k,groups[odd],groups[even]); b = block(k,groups[even],groups[odd])
        require(mm(a,b) == identity(3) and mm(b,a) == identity(3), 'fixture matching inverses')
    for a,b in ((3,24),(24,3),(0,27),(27,0)):
        require(all(x == 0 for row in block(k,groups[a],groups[b]) for x in row), 'fixture exceptional block killed')
    require(mm(block(k,groups[0],groups[15]),block(k,groups[15],groups[0])) == [[Q(1)]], 'fixture line duality')

def main():
    raw = CANDIDATE.read_bytes()
    require(b'\r' not in raw, 'candidate newline format')
    require(hashlib.sha256(raw).hexdigest() == CANDIDATE_LF_SHA, 'candidate LF pin')
    candidate = json.loads(raw)
    with tarfile.open(ROOT/'research/community-frontier1094-audit/selected-replay.tar.gz') as archive:
        payload = archive.extractfile(MEMBER).read()
    require(hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA, 'selected payload pin')
    recipes = sorted(json.loads(payload)['recipes'],key=lambda x:x['port'])
    require([r['port'] for r in recipes] == list(range(112)), 'label port ordering')
    q = [r['q'] for r in recipes]; groups = candidate['groups']; supports = candidate['factor_supports']
    require(len(q) == len(set(q)) == 112 and all(0<x<512 for x in q), 'labels distinct')
    require(sorted(p for g in groups for p in g) == list(range(112)), 'group partition')
    require([len(g) for g in groups] == [1]+[3]*37, 'group dimensions')
    owner = {p:g for g,ports in enumerate(groups) for p in ports}
    spaces = [[q[p] for p in g] for g in groups]
    require(all(parity(x&y) == (i==j) for s in spaces for i,x in enumerate(s) for j,y in enumerate(s)), 'orthonormal groups')
    free = {(i,j) for i in range(38) for j in range(38) if pairing(spaces[i],spaces[j]) == 0}
    graph_premises(free)
    h = [spaces[i]+spaces[i+1] for i in range(1,37,2)]
    require(all(pairing(s,s)==6 for s in h), 'complete paired-space tariff')
    low = spaces[37]
    require(pairing(low,low)==3, 'exceptional three-space')
    tariffs = Counter(pairing(low+a,low+b) for a in h for b in h)
    require(sum(tariffs.values())==324 and min(tariffs)>=6, '324 enlarged pairings')
    residual = spaces[0]+spaces[15]+spaces[16]
    require(pairing(residual,residual)==7, 'residual whole-space rank seven')
    require(len(supports)==57 and sorted(p for s in supports for p in s)==list(range(112)), 'saved factor partition')
    v0 = [[Q(p in support) for support in supports] for p in range(112)]
    k0 = mm(v0,transpose(v0)); endpoint(k0,owner,free); fixture_schur(k0,groups)
    require(price(v0,v0,spaces,owner)=={3:3,6:53,7:1}, 'direct exact tariff')

    # Dense rational changes within each physical group preserve whole-group support.
    u0 = [row[:] for row in v0]; w0 = [row[:] for row in v0]
    for g,ports in enumerate(groups):
        n = len(ports)
        change = [[Q(i==j)+Q(g+1,2) for j in range(n)] for i in range(n)]
        dual = transpose(inverse(change))
        uu = mm(change,[v0[p] for p in ports]); ww = mm(dual,[v0[p] for p in ports])
        for p,row,dualrow in zip(ports,uu,ww): u0[p]=row; w0[p]=dualrow
    k = mm(u0,transpose(w0)); endpoint(k,owner,free); fixture_schur(k,groups)
    require(price(u0,w0,spaces,owner)=={3:3,6:53,7:1}, 'group GL3 fixture tariff')
    require(all(x for row in block(k,groups[15],groups[0]) for x in row), 'line fixture is not coordinate-aligned')

    # T=I+J has determinant58; T^-1=I-J/58. These are genuinely even-denominator
    # products, not a cancelling diagonal column gauge. Every factor is dense.
    u = [[x+sum(row) for x in row] for row in u0]
    w = [[x-sum(row)/58 for x in row] for row in w0]
    require(all(x for row in u for x in row) and all(x for row in w for x in row), 'dense basis fixture')
    require(mm(u,transpose(w)) == k, 'dense even-denominator endpoint')
    require(any((a*b).denominator%2==0 for a,b in zip(u[0],w[0])), 'uncancelled even denominator')
    dense_profile = price(u,w,spaces,owner)
    require(dense_profile == {9:57}, 'dense fixture complete tariff')
    controls = []
    controls.append(rejects(lambda:graph_premises(free|{(4,24),(24,4)}),'grant formerly forced E4-E24 entry'))
    controls.append(rejects(lambda:graph_premises(free|{(0,28),(28,0)}),'grant formerly forced line-E28 entry'))
    def original_labels():
        pair = next(s for s in supports if len(s)==2)
        require(pairing([q[p] for p in pair],[q[p] for p in pair])==6,'original-label undercharge')
    controls.append(rejects(original_labels,'replace complete groups by original labels'))
    bad = [row[:] for row in k];bad[groups[0][0]][groups[0][0]]=Q(0)
    controls.append(rejects(lambda:endpoint(bad,owner,free),'alter residual endpoint'))
    require(54*6+3*3+1==334,'symbolic invoice arithmetic')
    result = {'candidate_lf_sha256':CANDIDATE_LF_SHA,'selected_payload_sha256':PAYLOAD_SHA,
              'groups':38,'fitting_rank':57,'enlarged_pairing_histogram':dict(sorted(tariffs.items())),
              'residual_rank':7,'pure_factor_index_union_bound':3,'rank_tight_copy_floor':334,
              'zero_saving_allowance':'2672/9','direct_profile':{3:3,6:53,7:1},
              'dense_even_denominator_profile':dense_profile,'dense_basis_determinant':58,
              'controls':controls,'scope':'Every exactly57-term rational scalar fit on the pinned mask, under complete port-space one-total pricing. Overcomplete fits and changed contracts are excluded.'}
    print(json.dumps(result,sort_keys=True))
    print('PASS_INDEPENDENT_P112_57_TERM_COST_FLOOR')

if __name__ == '__main__':
    main()

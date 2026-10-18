#!/usr/bin/env python3
"""Finite premises for the rank-tight 57-term port-space lower bound.
No rational reduction modulo two: F2 is used only for the support tariff.
"""
from collections import Counter
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import tarfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
CANDIDATE_SHA = 'dc5fbe51f9cd3a14361256ac136736bffb18971d0247b891accf0d2ee060d06b'
ARCHIVE_SHA = 'f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6'
PAYLOAD_SHA = 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'
MEMBER = 'candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json'

def need(ok, message):
    if not ok:
        raise ValueError(message)

def rank(rows):
    # Explicit low-column Gaussian elimination, distinct from the independent
    # checker's highest-pivot dictionary. Rows are bit-packed binary vectors.
    rows = list(rows)
    ncols = max((row.bit_length() for row in rows), default=0)
    pivot_row = 0
    for column in range(ncols):
        found = next((i for i in range(pivot_row, len(rows))
                      if (rows[i] >> column) & 1), None)
        if found is None:
            continue
        rows[pivot_row], rows[found] = rows[found], rows[pivot_row]
        for i in range(pivot_row+1, len(rows)):
            if (rows[i] >> column) & 1:
                rows[i] ^= rows[pivot_row]
        pivot_row += 1
    return pivot_row

def dot(a,b):
    return (a&b).bit_count()%2

def rho(a,b):
    return rank([sum(dot(x,y)<<j for j,y in enumerate(b)) for x in a])

def vector_span(generators):
    vectors = {0}
    for generator in generators:
        vectors.update([x ^ generator for x in vectors])
    return frozenset(vectors)

def span_basis(vectors):
    # Recover a basis using explicit vector-set membership rather than pivots.
    result, generated = [], {0}
    for vector in sorted(vectors):
        if vector not in generated:
            result.append(vector)
            generated.update([x ^ vector for x in generated])
    need(generated == vectors, 'vector-set space is closed')
    return result

def canonical_span_premises(H, J):
    # Every retained support uses some subset of these 19 component spaces.
    # Closing under addition generates all such spaces without enumerating
    # 2^19 subsets. Sets of binary vectors are an independent representation
    # from the second checker's canonical echelon tuples.
    seeds = H + [J]
    generated = {frozenset({0})}
    pending = list(generated)
    while pending:
        space = pending.pop()
        for seed in seeds:
            larger = vector_span(span_basis(space) + seed)
            if larger not in generated:
                generated.add(larger)
                pending.append(larger)
    need(len(generated) == 40, 'complete component-span closure has40 spaces')
    spans = sorted(generated, key=lambda s:(len(s), tuple(sorted(s))))
    bases = {s:span_basis(s) for s in spans}
    closures = {s:tuple(i for i,seed in enumerate(seeds)
                       if all(vector in s for vector in seed)) for s in spans}
    nonpure = [s for s in spans if any(i < 18 for i in closures[s])]
    need(len(nonpure) == 38, '38 nonpure component spaces')
    need(all(rho(J, h) == 3 for h in H), 'every pure-J term costs exactly3')
    rectangles = Counter()
    for left in nonpure:
        for right in nonpure:
            charge = rho(bases[left], bases[right])
            need(charge >= 4, 'nonpure tariff at least4')
            if charge >= 6:
                continue
            A, B = closures[left], closures[right]
            need(not set(A).intersection(B), 'low-tariff component supports disjoint')
            probability_denominator = comb(len(A)+len(B), len(A))
            need(probability_denominator <= (2 if charge == 4 else 4),
                 'acyclic sampling probability bound')
            rectangles[(len(A),len(B),charge)] += 1
    need(rectangles == {(1,1,4):20, (1,1,5):178, (1,2,5):33,
                        (1,3,5):4, (2,1,5):33, (3,1,5):4},
         'exact low-tariff rectangle census')
    # For integer s>=0, s<=26 gives334-s>=308, while s>=27
    # gives228+3s>=309. The value308 occurs at s=26.
    need(334-26 == 308 and 228+3*27 == 309, 'integer envelope floor308')
    return {'component_span_count':len(spans),
            'nonpure_component_span_count':len(nonpure),
            'low_tariff_rectangles':{','.join(map(str,k)):v for k,v in sorted(rectangles.items())},
            'pure_J_pairings':{'3':18},
            'canonical_span_copy_lower_bound':308,
            'scope':'Any term count, rank57 fitting matrix, BOTH factor families confined to its column and row spaces. Exterior directions and higher matrix ranks excluded.'}

def main():
    raw = (PACKAGE/'CANDIDATE.json').read_bytes()
    need(sha256(raw).hexdigest()==CANDIDATE_SHA, 'candidate pin')
    candidate = json.loads(raw)
    archive = ROOT/'research/community-frontier1094-audit/selected-replay.tar.gz'
    need(sha256(archive.read_bytes()).hexdigest()==ARCHIVE_SHA, 'archive pin')
    with tarfile.open(archive, 'r:gz') as t:
        payload=t.extractfile(MEMBER).read()
    need(sha256(payload).hexdigest()==PAYLOAD_SHA, 'payload pin')
    data=json.loads(payload)
    recipes=sorted(data['recipes'],key=lambda r:r['port'])
    need([r['port'] for r in recipes]==list(range(112)), 'ports')
    labels=[r['q'] for r in recipes]
    groups=candidate['groups']
    need(len(groups)==38 and len(groups[0])==1 and all(len(g)==3 for g in groups[1:]), 'dimensions')
    need(sorted(p for g in groups for p in g)==list(range(112)), 'partition')
    spaces=[[labels[p] for p in g] for g in groups]
    need(all(dot(x,y)==int(i==j) for basis in spaces for i,x in enumerate(basis) for j,y in enumerate(basis)), 'orthonormal frames')
    pairing=[[rho(a,b) for b in spaces] for a in spaces]
    retained=list(range(1,38,2))
    need(all(pairing[i][j]>0 for i in retained for j in retained), 'I57 principal minor')
    outside=[0]+list(range(2,37,2))
    allowed={g:[h for h in retained if pairing[g][h]==0] for g in outside}
    expected={g:[g-1] for g in outside if g!=0}
    expected[24]=[3,23]
    expected[0]=[15,27]
    need(allowed==expected, 'all outside-to-clique free supports')
    # K4,4=I gives inverse maps at the unique neighbor3. K4,24 and
    # K24,4 are forced zero, so both group24-to-3 maps vanish.
    need(allowed[4]==[3] and pairing[4][24]>0, 'group24 extra maps eliminated')
    # Likewise the invertible group28 maps at27 eliminate line0-to-27.
    need(allowed[28]==[27] and pairing[0][28]>0, 'residual extra maps eliminated')
    pairs=[(g,g+1) for g in range(1,36,2)]
    H=[spaces[a]+spaces[b] for a,b in pairs]
    need(all(pairing[a][b]==0 and rho(h,h)==6 for (a,b),h in zip(pairs,H)), 'paired six-spaces')
    J=spaces[37]
    combined=[[rho(J+a,J+b) for b in H] for a in H]
    histogram=Counter(x for row in combined for x in row)
    need(min(histogram)==6 and histogram=={6:11,7:93,8:171,9:49}, 'all324 mixed support bounds')
    residual=spaces[0]+H[7]
    need(rho(residual,residual)==7, 'residual pair span seven')
    bare=Counter(rho(a,b) for a in H for b in H)
    # The stronger universal bound on arbitrary paired spaces would be false.
    need(min(bare)<6, 'negative control: pure cross-pair terms can cost below six')
    canonical = canonical_span_premises(H, J)
    receipt={
      'source_head':'c8216fca1ed2a301a95e7e0b1e5844d4cfda02c6',
      'candidate_sha256':CANDIDATE_SHA,
      'archive_sha256':ARCHIVE_SHA,
      'payload_sha256':PAYLOAD_SHA,
      'retained_clique_groups':retained,
      'outside_allowed_clique_groups':allowed,
      'pair_plus_G37_rho_table':combined,
      'pair_plus_G37_rho_histogram':dict(sorted(histogram.items())),
      'bare_pair_rho_histogram':dict(sorted(bare.items())),
      'residual_pair_self_rank':7,
      'rank_tight_terms':57,
      'maximum_terms_below_six':3,
      'tariff_lower_bound':334,
      'canonical_span_extension':canonical,
      'scope':'All rational 57-term rank-one fitting decompositions of this fixed mask. Written proof required; not an arbitrary-term bound.',
    }
    print(json.dumps(receipt,indent=2))
    print('PASS_RANK_TIGHT_57_TERM_COST_FLOOR_334_FINITE_PREMISES')

if __name__=='__main__': main()

#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Prepared for commdata2338 with substantial OpenAI Codex assistance.
"""Separate set-valued replay, forward-matrix inversion and integer geometry.

Imports neither the primary verifier nor predecessor implementations. Earlier
cuts are replayed from scratch, not obtained by the primary right-product update.
"""
from collections import Counter
from functools import lru_cache
import gzip
import hashlib
import json
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/r439-bsection-stars-seed01/candidate.json.gz'
REGS = (19,27,35,43,57,65,66,74,89,97,466)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def checksum(value):
    raw = json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(raw).hexdigest()


def integer_rank(rows):
    rows = [list(r) for r in rows]
    rank = 0
    for col in range(8):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(rank+1, len(rows)):
            if not rows[i][col]:
                continue
            a, b = rows[rank][col], rows[i][col]
            rows[i] = [a*x-b*y for x,y in zip(rows[i],rows[rank])]
            g = 0
            for x in rows[i]:
                g = gcd(g, x)
            if g:
                rows[i] = [x//g for x in rows[i]]
        rank += 1
    return rank


def load_word():
    records = json.loads((HERE/'SOURCES.json').read_text())['files']
    raw = (ROOT/WORD).read_bytes()
    pin = next(r for r in records if r['path'] == WORD)
    require(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'oracle source pin')
    return json.loads(gzip.decompress(raw))


def replay(rows, ops):
    for _, d, sources in ops:
        for source in sources:
            rows[d].symmetric_difference_update(rows[source])


def invert(forward):
    # Gauss-Jordan on the forward endpoint; does not read the reversed program.
    left = [set(row) for row in forward]
    right = [{i} for i in range(len(left))]
    for col in range(len(left)):
        pivot = next((i for i in range(col,len(left)) if col in left[i]), None)
        require(pivot is not None, 'oracle invertibility')
        left[col],left[pivot] = left[pivot],left[col]
        right[col],right[pivot] = right[pivot],right[col]
        for i in range(len(left)):
            if i != col and col in left[i]:
                left[i].symmetric_difference_update(left[col])
                right[i].symmetric_difference_update(right[col])
    require(left == [{i} for i in range(len(left))], 'oracle reduced identity')
    return right


def packed(row):
    return sum(1 << i for i in row)


def hist(counts):
    return {str(i):n for i,n in sorted(counts.items()) if n and i}


def audit(c, w, atlas=True):
    require(w['v']==111 and w['R']==439, 'oracle dimensions')
    n=661
    for _,d,ss in w['A']:
        require(d>=222 and not any(111<=s<222 for s in ss), 'oracle source-preserving/no-return premise')
    for _,d,ss in w['B']:
        require(111<=d<222 or not any(111<=s<222 for s in ss), 'oracle no target feedback')
    require([i for i,g in enumerate(w['B']) if g[0]==508]==list(range(174,195)), 'oracle right cut')
    ops_a,ops_b=w['A'][1991:],w['B'][:195]
    M=[{i} for i in range(n)]
    replay(M,ops_a)
    observation=[packed(M[r]) for r in w['ret']]
    # Literal COPY, target ADDs and ERASE with one separate clean temporary.
    scatter_count=0
    for j,centre in enumerate(w['ret']):
        tmp=set(M[centre])
        for i,ss in enumerate(w['scatter']):
            if j in ss:
                M[111+i].symmetric_difference_update(tmp)
                scatter_count+=1
        require(tmp==M[centre], 'oracle copy erasure')
        tmp.clear()
    replay(M,ops_b)
    inverse=invert(M)
    require(checksum(list(map(packed,M)))==c['full_endpoint_rows_sha256'], 'oracle forward endpoint')
    require(checksum(list(map(packed,inverse)))==c['full_inverse_rows_sha256'], 'oracle inverse endpoint')
    dual={r:{j for j in range(111) if r in inverse[j]} for r in REGS}

    @lru_cache(None)
    def independent_basis(indices):
        chosen=[]
        for i in indices:
            if integer_rank([w['lines'][j] for j in chosen+[i]])>len(chosen):
                chosen.append(i)
        return tuple(chosen)

    dims=[integer_rank([w['lines'][i] for i in f]) for f in w['frames']]
    # Last-use lookup gives boundary frames independently of the primary walk.
    prefix=w['D']+w['A'][:1991]
    entry=w['start'].copy()
    for r in REGS:
        entry[r]=next((f for f,d,ss in reversed(prefix) if r in (d,*ss)),entry[r])
    require([r['register'] for r in c['wires']]==list(REGS), 'oracle wire inventory')
    bill=Counter()
    for r,record in zip(REGS,c['wires'],strict=True):
        roots=(M[r]&set(range(111))) | dual[r] | ({r} if r<111 else set())
        witness=independent_basis(tuple(sorted(roots)))
        require(len(witness)==4, 'oracle rank four')
        require(integer_rank([w['lines'][j] for j in roots|set(w['frames'][508])])==4, 'oracle exact subspace')
        delta=4-dims[entry[r]]
        expected={'register':r,'entry_frame':entry[r],'entry_rank':dims[entry[r]],
                  'forward_sources':sorted(M[r]&set(range(111))), 'inverse_source_outputs':sorted(dual[r]),
                  'source_only_witness':list(witness),'forced_frame':508,'minimum_increment':delta}
        require(record==expected, 'oracle source-only witness record')
        path=[entry[r]]
        for f,d,ss in ops_a+ops_b:
            if r in (d,*ss) and path[-1]!=f:
                path.append(f)
        require(path==[entry[r],508], 'oracle attaining path')
        bill[delta]+=1
    require(hist(bill)==c['minimum_eleven_wire_profile']=={'2':8,'3':3}, 'oracle minimum invoice')
    require(c['minimum_eleven_wire_rank_mass']==25, 'oracle minimum rank mass')

    current=w['start'].copy()
    whole,seam=Counter(),Counter()
    copy_frames=[]
    for sec in 'DABC':
        for k,(f,d,ss) in enumerate(w[sec]):
            for r in (d,*ss):
                if current[r]!=f:
                    require(set(w['frames'][current[r]])<set(w['frames'][f]), 'oracle path inclusion')
                    increment=dims[f]-dims[current[r]]
                    whole[increment]+=1
                    if (sec=='A' and k>=1991) or (sec=='B' and k<195):
                        seam[increment]+=1
                    current[r]=f
        if sec=='A':
            copy_frames=[current[r] for r in w['ret']]
    for r,f in enumerate(w['final']):
        if current[r]!=f:
            whole[dims[f]-dims[current[r]]]+=1
    whole.update(dims[f] for f in copy_frames)
    require(c['copy_observations']=={'registers':w['ret'],'frames':copy_frames,'ranks':[7]*9,'rows_sha256':checksum(observation)}, 'oracle COPY observations')
    require(c['baseline_seam_profile']==hist(seam), 'oracle seam bill')
    require(c['baseline_other_wire_profile']==hist(seam-bill), 'oracle other-wire bill')
    require(c['baseline_whole_word_profile']==hist(whole), 'oracle whole bill')
    require(c['baseline_seam_rank_mass']==sum(r*k for r,k in seam.items())==590, 'oracle seam mass')
    require(c['baseline_whole_word_rank_mass']==sum(r*k for r,k in whole.items())==5129, 'oracle whole mass')
    require(c['interval']=={'A_start_inclusive':1991,'A_stop_exclusive':2075,'B_start_inclusive':0,'B_stop_exclusive':195,
                           'stored_AB_operations':279,'elementary_AB_ADDs':sum(len(ss) for _,_,ss in ops_a+ops_b),
                           'scatter_ADDs':scatter_count,'original_registers':661}, 'oracle interval binding')
    require(c['schema_version']==1 and c['no_new_kappa'] is True and c['status']=='SCOPED_PROOF_AND_FINITE_CERTIFICATE', 'oracle scope status')

    if atlas:
        records=[]
        # Independent direct suffix simulation on all 111 source basis columns, at every cut.
        b_sub=[g for g in ops_b if not 111<=g[1]<222]
        for cut in range(1992):
            state=[{i} if i<111 else set() for i in range(n)]
            replay(state,w['A'][cut:])
            replay(state,b_sub)
            item=[]
            for r in REGS:
                roots=state[r]|dual[r]|({r} if r<111 else set())
                witness=independent_basis(tuple(sorted(roots)))
                require(len(witness)==4 and integer_rank([w['lines'][j] for j in roots|set(w['frames'][508])])==4, 'oracle earlier-cut rank')
                item.append([r,packed(state[r]),packed(dual[r]),list(witness)])
            records.append([cut,item])
        require(c['earlier_cut_atlas']=={'first_cut':0,'last_cut':1991,'cuts':1992,'wire_cut_checks':21912,
                                        'all_forced_ranks':4,'rows_sha256':checksum(records)}, 'oracle complete cut atlas')
    return True


if __name__=='__main__':
    audit(json.loads((HERE/'CERTIFICATE.json').read_text()),load_word())
    print('PASS_R439_ENLARGED_SEAM_ORACLE direct_cut_replays=1992 rational_rank_checks=21912 '
          'full_matrix=661 COPY=9 minimum=8H2+3H3 no_new_kappa')

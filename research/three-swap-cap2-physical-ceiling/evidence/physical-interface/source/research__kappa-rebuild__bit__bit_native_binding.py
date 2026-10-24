#!/usr/bin/env python3
"""Bind the p3 BIT physical controller to exact local rational port charts.

The cover is a formal GL_N row until a complete finite uniform program is
compiled. This verifier checks every fixed port map and actual local data
endpoint, plus the native helper ownership and complete recursive invoice.
Apache-2.0. Substantial OpenAI assistance; retained source attribution is
in the immutable PR589/PR555 notices and the companion README.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json
import struct
import time

import mixed_productive_bit as B

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]


def ident(n):
    return [[Q(i==j) for j in range(n)] for i in range(n)]


def multiply(a,b):
    out=[[Q(0)]*len(b[0]) for _ in a]
    for i,row in enumerate(a):
        for k,value in enumerate(row):
            if value:
                for j,second in enumerate(b[k]):
                    if second:
                        out[i][j]+=value*second
    return out


def transpose(a):
    return list(map(list,zip(*a)))


def subtract(a,b):
    return [[x-y for x,y in zip(row,second)] for row,second in zip(a,b)]


def serialize(a):
    return [[str(x) for x in row] for row in a]


def partial_swap(p):
    n=len(p)
    return [[(int(i==j)-p[i][j] if i<n and j<n else
              p[i][j-n] if i<n else p[i-n][j] if j<n else
              int(i==j)-p[i-n][j-n]) for j in range(2*n)] for i in range(2*n)]


def run():
    start=time.monotonic()
    word_path=HERE/'sources/pr589-regenerated/WORD.json.gz'
    receipt_path=HERE/'MIXED-PRODUCTIVE-BIT.json'
    data=json.loads(receipt_path.read_text())
    case=next(c for c in data['candidates'] if c['pairs']==3)
    B.need(case['keep_idle_mask']==43,'The chosen seven-stage controller')
    B.need(sha256(word_path.read_bytes()).hexdigest()==B.WORD_HASH,'Actual retained local word')
    word=json.loads(gzip.decompress(word_path.read_bytes()))
    folder=word_path.parent/'records'
    frame_data=json.loads((folder/'frames.json').read_text())['frames']
    projectors=B.frame_projectors(frame_data)
    records=list(struct.iter_unpack('<6i',(folder/'249-records.bin').read_bytes()))
    eye,zero=ident(8),[[Q(0)]*8 for _ in range(8)]
    ports=[]
    full_swap=partial_swap(eye)
    for port,q in enumerate(word['lines']):
        q=list(map(Q,q))
        B.need(sum(x*x for x in q)==4,'Exact root norm')
        p=[[x*y/4 for y in q] for x in q]
        k=subtract(eye,p)
        u=[Q(i==0)-q[i]/2 for i in range(8)]
        norm=sum(x*x for x in u)
        g=eye if not norm else [[Q(i==j)-2*u[i]*u[j]/norm for j in range(8)] for i in range(8)]
        a=[row[1:] for row in g]
        B.need(multiply(transpose(g),g)==eye,'Rational orthogonal port chart')
        B.need([2*row[0] for row in g]==q,'The chart sends2e0 exactly to q')
        B.need(multiply(transpose(a),a)==ident(7) and multiply(a,transpose(a))==k,
               'Exact orthonormal complement columns')
        rho=[p[i]+a[i] for i in range(8)]+[row+[Q(0)]*7 for row in transpose(a)]
        B.need(multiply(rho,rho)==ident(15),'Each port route is its exact inverse')
        local8=[[Q(i==j and i<8) for j in range(15)]for i in range(15)]
        active=[[p[i][j] if i<8 and j<8 else Q(i==j and i>=8) for j in range(15)]for i in range(15)]
        B.need(multiply(multiply(rho,local8),rho)==active,'Local helper rank8 map under the port chart')
        B.need(projectors[word['start'][port]]==p and projectors[word['start'][111+port]]==zero,
               'Actual local data entrance frames')
        B.need(projectors[word['final'][port]]==eye and projectors[word['final'][111+port]]==k,
               'Actual local data exit frames')
        B.need(multiply(full_swap,partial_swap(p))==partial_swap(k),'Exact physical local factorD_I D_P=D_K')
        ports.append(dict(port=port,root=[str(x) for x in q],
                          central_projector=serialize(p),complement_columns=serialize(a),
                          chart_15=serialize(rho),
                          lifted_routes=[dict(stage=s,axes=list(range(8))+list(range(8+7*(s-1),8+7*s)))
                                         for s in range(1,7)]))
    copy_checks=0
    for op,x,y,c,f,z in records:
        if op==2:
            a,b=projectors[c],projectors[f]
            low,high=(a,b) if sum(a[i][i]for i in range(8))<sum(b[i][i]for i in range(8)) else (b,a)
            B.need(multiply(low,high)==low and multiply(high,low)==low,'Native COPY projectors nested')
            difference=subtract(high,low)
            B.need(multiply(difference,difference)==difference and sum(difference[i][i]for i in range(8))==7,
                   'Each copied center has exactly one rank7 request under the retained contract')
            copy_checks+=1
    B.need(copy_checks==9,'All retained copied centers')
    owners=[]
    for stage in range(7):
        fields=list(range(666+439*stage,666+439*(stage+1)))
        owners.append(dict(stage=stage,independent_helper_fields=fields,
                           endpoint_projector='diag(I8,0_(N-8)) at the local invocation cover row h',
                           arbitrary_original_inputs=True))
    B.need(len({x for row in owners for x in row['independent_helper_fields']})==3073,'All helper owners injective')
    paid=Counter({r:7*n for r,n in B.LOCAL.items()})
    paid[7]+=2*111*sum(len(row['stages'])for row in case['idle_events']if row['retained'])
    targets=Counter({8:3073})
    endpoint=[]
    for role,term in enumerate(case['factorization']['diagonal_monomials']):
        stages=[s for s in range(7)if term>>(s+1)&1]
        rank=(term&1)+7*len(stages)
        targets[rank]+=111
        endpoint.append(dict(data_role=role,central_q=bool(term&1),stages=stages,rank=rank,
                             projector='P_q + selected pairwise perpendicular K_q/B_s blocks'))
    B.need(dict(sorted(paid.items()))=={int(r):n for r,n in case['paid'].items()},'Literal complete paid ledger')
    B.need(dict(sorted(targets.items()))=={int(r):n for r,n in case['targets'].items()},'Actual endpoint rank credit')
    B.need(max(paid)<min(targets),'Strict mixed recursive separation')
    sources=[Path(__file__),word_path,receipt_path,HERE/'mixed_productive_bit.py',
             folder/'frames.json',folder/'249-records.bin',
             ROOT/'research/e8-bit-carrier-skeleton/code/nine/geometry.py',
             ROOT/'notes/three-stage-cover-bit.tex',ROOT/'notes/three-stage-cover-rows.tex']
    return dict(schema='native-p3-BIT-common-cover-binding/1',status='PASS_FIXED_RATIONAL_PORTS_AND_PHYSICAL_ENDPOINTS',
                source_sha256={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest()for p in sources},
                ambient_rank=50,local_rank=8,ports=ports,helper_owners=owners,
                main_endpoints=endpoint,targets=dict(sorted(targets.items())),paid=dict(sorted(paid.items())),
                formal_cover_contract='All local projectors, per-port right routes and unit matchers embed into one future ambient GL_N. No smaller cover is instantiated or lowered first.',
                scalar_operation_counts=dict(unit_ADDs_including_arithmetic_final_swaps=174908,
                                             source_owned_COPY_episodes=63,COPY_or_ERASE_records=126,
                                             nonidentity_port_right_routes_including_inverses=6*111*2*2,
                                             maximum_owned_center_fibers_per_base_unit=1),
                local_word_all_columns_evidence='MIXED-PRODUCTIVE-BIT.json and regenerated XCHECK.json',
                all_f_lift='Every head projector and chart is tensor-multiplied by I_f; the reversed tail block uses C_(Nf). Polynomial identities remain exact, and routes change only cover coordinates.',
                scope='Native finite schematic unit plus exact source binding, not materialization of GL_N or the final precompiled uniform word.',
                runtime_seconds=time.monotonic()-start,new_kappa=False)


if __name__=='__main__':
    result=run()
    (HERE/'BIT-P3-NATIVE-BINDING.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:result[k]for k in ('status','ambient_rank','targets','paid','scalar_operation_counts','runtime_seconds')}))

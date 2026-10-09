#!/usr/bin/env python3
"""Selected structured-basis and semantic-bulk arithmetic certificate.

Copyright 2026 icekylinx. Apache-2.0.
Prepared with substantial OpenAI GPT-6 Astra and Codex assistance.
The assembly adapts PR23 (Zhihao Chen / jacklightChen), building on RaD
(hipotures); see references/semantic-bulk and SOURCES.json.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import comb, prod
from pathlib import Path
import json
import sys

from certify import require
from partial_swap_network import moment
from structured_bulk_assembly import assembly, finite_bridge, js

ROOT=Path(__file__).resolve().parents[1]
AB=Q(1252373,10**11)
AC=Q(131,5000000)
KAPPA=Q(2504683,200000000000)


def bit_profile(rows, structured):
    a, b, k = (row['h'] for row in rows)
    assert (a, b, k) == (32, 30, 36)
    H, m = a*b, a*b*k
    N = rows[0]['v']*rows[1]['v']*rows[2]['v']
    B1, B2, B3 = (N//row['v']*row['R'] for row in rows)
    assert B3 >= B1
    E, W = B3-B1, 2*N+B2+B3
    L = sum(N//row['v']*row['loss'] for row in rows)
    z = Counter()
    sources = {}

    def add(n, *widths):
        for t in widths:
            if n and t:
                assert 0 < t < m and n > 0
                z[t] += n

    # New A1: the first-a/rightmost-a null corner is lower triangular.
    add(B1, a, m-2*(a+k))
    add(B1*k, 1)
    add(E, k, m-2*k)
    # Inherited merged stage-two auxiliary endpoint gauge.
    add(B2, b, m-2*b)
    # Inherited full physical A3 and new A5 corner refinement.
    add(2*N, k-2, H-2*k+2, m-2*H-2*k+2)
    add(2*N*(2*k-1), 1)
    add(2*N, b-2, H-2*a-2*b+2)
    add(2*N*(a+1), 1)

    for row in rows:
        h = row['h']
        assert row['loss'] == h*(h-1)
        # Three physical data fronts retain their proved corank-one profile.
        add(2*N, 1, h-2)
        if h == 30:
            assert row['internal_profile_mode'] == 'fixed_I_plus_J'
            for field in ('h', 'v', 'R', 'loss'):
                assert structured[field] == row[field]
            blocks = structured['blocks']
            assert sum(t*n for t, n in enumerate(blocks)) == h*row['R']+2*row['loss']
            for t, n in enumerate(blocks):
                add(N//row['v']*n, t)
            sources[str(h)] = 'Fixed I+J axis; exact CRT-certified physical internal block profile'
        else:
            assert row['internal_profile_mode'] == 'generic'
            histogram = row['histogram']
            assert sum(r*n for r, n in enumerate(histogram)) == h*row['R']+2*row['loss']
            for r, n in enumerate(histogram):
                copies = N//row['v']*n
                if 2*r > h:
                    add(copies, 2*r-h)
                    add(copies*(h-r), 1)
                else:
                    add(copies*r, 1)
            sources[str(h)] = 'Inherited generic projector profile applied to supplied rank histogram'

    rank = W*m-2*N+2*L
    assert sum(t*n for t, n in z.items()) == rank
    return dict(dimensions=[a,b,k], m=m, N=N, B1=B1, B2=B2, B3=B3,
                E=E, W=W, L=L, total_rank=rank, deficit=2*N-2*L,
                maxchild=max(z), singletons=z[1], internal_profile_sources=sources,
                child_multiplicities=dict(sorted(z.items())))


def complex_profile(data):
    rows=data['scalar_circuits']
    require([r['h'] for r in rows]==[30,30,40], 'Selected complex axes')
    require(data['central_disjoint']==[19,19,35], 'Selected mixed centers')
    for row in rows:
        h=row['h'];v=comb(h,3)
        require(row['v']==v and row['q']==4*v+h, 'Complex output count')
        require(row['baseline_R']==row['c']+row['q'], 'Complex unmatched roles')
        require(row['R']==row['baseline_R']-row['matched'], 'Complex matched roles')
        require(row['loss']==h*(h-1), 'Mixed-center loss')
        hist=row['histogram']
        require(len(hist)==h+1 and all(n>=0 for n in hist), 'Complex histogram')
        require(sum(r*n for r,n in enumerate(hist))==row['rank_sum']==h*row['R']+2*row['loss'], 'Complex internal rank')
    a,b,k=(r['h'] for r in rows);m=a*b*k;N=prod(r['v'] for r in rows)
    B1,B2,B3=(N//r['v']*r['R'] for r in rows)
    require(B3>=B1,'Complex bank pairing')
    W=2*N+B2+B3;L=sum(N//r['v']*r['loss'] for r in rows)
    s=W*m-2*N+2*L
    macros=[(m-a-k,B1),(m-k,B3-B1),(m-b,B2),((a*b-1)*(k-1),2*N),((a-1)*(b-1),2*N)]
    z=Counter()
    for t,n in macros:z[t]+=n
    for row in rows:
        for r,n in enumerate(row['histogram']):
            if r:z[r]+=N//row['v']*n
    physical=2*N*sum(h-1 for h in (a,b,k))
    require(s-sum(t*n for t,n in z.items())==physical,'Complete physical-data rank')
    for h in (a,b,k):z[h-1]+=2*N
    computed=dict(m=m,N=N,B1=B1,B2=B2,B3=B3,W=W,L=L,total_rank=s,deficit=2*N-2*L,
                  physical_data_rank=physical,unaccounted_rank=0)
    for key,value in computed.items():require(value==data[key],'Complex global count: '+key)
    require(macros==[(p['width'],p['count']) for p in data['macros']], 'Complex macro table')
    require([(h-1,2*N) for h in (a,b,k)]==[(p['width'],p['count']) for p in data['physical_data_batches']], 'Complex fronts')
    require(dict(z)=={int(t):n for t,n in data['child_multiplicities'].items()}, 'Complete complex child list')
    require(sum(t*n for t,n in z.items())==s,'Complex rank mass')
    return computed,z


def curated_sources():
    folder=ROOT/'references/semantic-bulk'
    manifest=json.loads((folder/'MANIFEST.json').read_text())
    for name,digest in manifest['files'].items():
        require(sha256((folder/name).read_bytes()).hexdigest()==digest,'Dependency source hash: '+name)
    return manifest


def certificate():
    require(not sys.flags.optimize,'Run without -O to preserve finite assertions')
    def read(name):return json.loads((ROOT/'certificates'/('structured-bulk-'+name+'.json')).read_text())
    saved,rows,structured,complex_data=map(read,('input','bit-axes','rankone-profiles','complex-input'))
    for row in rows:
        h=row['h'];require(row['v']==comb(h,3),'Bit triple count')
        require(row['q']==3*row['v']+h,'Bit output uses')
        require(row['baseline_R']==row['c']+row['q'] and row['R']==row['baseline_R']-row['matched'],'Bit roles')
    bit=bit_profile(rows,structured)
    require(js(bit)==saved['bit'],'Saved complete bit profile')
    cn,cr=complex_profile(complex_data)
    bm=moment(bit['m'],bit['W'],bit['child_multiplicities'],AB,True)
    cm=moment(cn['m'],cn['W'],cr,AC,False)
    require(bm['strict_gap']==Q(saved['bit_moment_gap']),'Saved bit gap')
    require(cm['strict_gap']==Q(saved['complex_moment_gap'])==Q(complex_data['strict_gap']),'Saved complex gap')
    bridge=finite_bridge(bit['m'],bit['W'],bit['maxchild'],complex_data)
    assembled=assembly(AB,AC,bridge,KAPPA)
    require(js(bridge)==saved['finite_bridge'],'Saved semantic and row bridge')
    require(js(assembled)==saved['assembly'],'Saved assembly')
    require(len(assembled['strict_constraints'])==47,'47 strict constraints')
    require(len(assembled['margins'])==7,'Seven assembly margins')
    sources=sorted((ROOT/'certificates').glob('structured-bulk-*.json'))
    sources=[p for p in sources if p.name!='structured-bulk-network.json']
    sources+=sorted((ROOT/'scripts').glob('structured_bulk*.py'))
    sources+=sorted(p for p in (ROOT/'scripts/structured_bulk').iterdir() if p.is_file())
    sources+=sorted((ROOT/'notes').glob('structured-bulk-*.tex'))
    sources+=[ROOT/'references/semantic-bulk/MANIFEST.json']
    return dict(status='Conditional structured-basis and semantic-bulk multiplication witness',kappa=KAPPA,
                bit=dict(counts=bit,**bm),complex=dict(counts=cn,**cm),finite_bridge=bridge,assembly=assembled,
                inherited_commit='ed90fd940279c336ebc45968631bdebfb087b505',
                adopted_sources=curated_sources(),
                source_sha256={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sources},
                scope='Exact moments and assembly; producer regeneration and bounded-minor CRT profiles are checked separately. '
                      'Simultaneous basis existence, analytic/tape interfaces and eventual thresholds remain written proof dependencies.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'certificates/structured-bulk-network.json')
    args=parser.parse_args();result=certificate()
    args.output.write_text(json.dumps(js(result),indent=2,sort_keys=True)+'\n')
    print('PASS kappa=2504683/200000000000 = 1.2523415e-5')
    print('Both moments; semantic C1=1; product row stock; 47 strict constraints and seven margins')

if __name__=='__main__':main()

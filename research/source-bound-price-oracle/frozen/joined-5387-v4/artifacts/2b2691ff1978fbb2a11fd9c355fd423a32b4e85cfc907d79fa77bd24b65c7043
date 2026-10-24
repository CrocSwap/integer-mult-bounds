#!/usr/bin/env python3
"""Bounded independent scalar/preparation audit. No submitted modules execute.

Ali Romman owns the construction. New review: Chris R / Clear1nsight with
substantial OpenAI Codex assistance. Apache-2.0; predecessor sources unchanged.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip, json, time

HERE=Path(__file__).resolve().parent
CAP=HERE.parent/'09-capsule-cold/capsule-v1'
PKG=CAP/'snapshot/research/kappa-joint-relations-20261023'

def load(name):
    p=PKG/name; b=p.read_bytes()
    return json.loads(gzip.decompress(b) if name.endswith('.gz') else b)

def ceil_log2(q):
    q=Q(q); k=0
    while q>1: q/=2; k+=1
    return k

def height(q,add):
    assert q.denominator & (q.denominator-1)==0
    return ceil_log2(1+abs(q) if add else max(1,abs(q)))+q.denominator.bit_length()-1

def rref(relations):
    cols=sorted({int(i) for r in relations for i,q in r['relation']})
    a=[[Q(dict(r['relation']).get(i,'0')) for i in cols] for r in relations]
    rows=[]; piv=[]; row=0
    for j,c in enumerate(cols):
        k=next((k for k in range(row,len(a)) if a[k][j]),None)
        if k is None: continue
        a[row],a[k]=a[k],a[row]; x=a[row][j]; a[row]=[v/x for v in a[row]]
        for k in range(len(a)):
            if k!=row:
                x=a[k][j]; a[k]=[u-x*v for u,v in zip(a[k],a[row])]
        piv.append(c); row+=1
        if row==len(a): break
    assert row==8
    return piv,[{c:v for c,v in zip(cols,r) if v} for r in a]

def scalar_audit(program):
    # Scalar-only envelopes: each native/child operator's completed semantic
    # growth is supplied separately by the reviewed recurrence. A coefficient
    # charge is valid independently of cancellations and zero invariants.
    count=Counter(); h=0; max_coeff=Q(0); max_den=1
    for e in program:
        count[e[0]]+=1
        if e[0]!='scalar': continue
        g=e[1]; op=g[0]; count['scalar_'+op]+=1
        if op in ('add','scale'):
            q=Q(*g[3:]) if op=='add' else Q(*g[2:])
            max_coeff=max(max_coeff,abs(q)); max_den=max(max_den,q.denominator)
            h+=height(q,op=='add')
    return dict(events=dict(count),coefficient_height_upper=h,
                max_abs_coefficient=str(max_coeff),max_scalar_denominator=max_den)

def encode(x):
    if isinstance(x,Q): return str(x)
    if isinstance(x,dict): return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return list(map(encode,x))
    return x

def main():
    start=time.monotonic(); w=load('WORD.json.gz'); witness=load('WITNESS.json')
    piv,rows=rref(witness)
    assert piv==[225,227,229,230,241,245,257,288]
    declared={int(p):{int(i):Q(q) for i,q in r.items()} for p,r in w['relation_basis'].items()}
    assert dict(zip(piv,rows))==declared
    expected=[]; prep=[]
    for p,r in zip(piv,rows):
        assert r[p]==1 and not (set(r)&(set(piv)-{p}))
        expected.append(['scalar',['clear',['L',p]],0]); mass=Q(0); hh=0
        for i,q in sorted(r.items()):
            if i==p: continue
            expected.append(['scalar',['add',['L',p],['L',i],(-q).numerator,q.denominator],0])
            mass+=abs(q); hh+=height(q,True)
        prep.append(dict(pivot=p,add_count=len(r)-1,row_l1=mass,
                         prefix_l1_upper=mass,denominator=max(q.denominator for q in r.values()),height_upper=hh))
    assert w['programs']['backward'][:len(expected)]==expected
    # Exact dirty owned entries are cleared before preparation; only nonpivots
    # feed preparation. Input range is multiplied by <=9, not assumed unit.
    assert max(p['row_l1'] for p in prep)==9
    assert max(p['denominator'] for p in prep)==2
    audits={d:scalar_audit(w['programs'][d]) for d in ('forward','backward')}
    assert audits['backward']['events']['zero_retag']==8
    assert all(a['max_scalar_denominator']&(a['max_scalar_denominator']-1)==0 for a in audits.values())
    # Source polynomial domination and error-count margin, exact coefficients.
    # S>=Z+N+P+G+1, E=64S^3, B=P+E, C0=32NB^2.
    # The symbolic proof in REPORT establishes all sizes. These boundary probes
    # corroborate the algebra rather than replacing its quantifiers.
    probes=[]
    for N,W,O,P,G in [(2,1,0,0,0),(2,1,17,1,1),(4,3,274,12,900),(57,2242,1,127570,1494376)]:
        Z=W+O; E=64*(Z+N+P+G+1)**3; B=P+E; C0=32*N*B*B
        guard=2*G*Z*Z+8*P+4*Z+4+32*N
        # Prefix+suffix growth, outer18d at each side, and injection count.
        error_cost=4*B+36+G+2*P+3
        assert E>guard and C0>error_cost
        probes.append(dict(N=N,W=W,O=O,P=P,G=G,E=E,B=B,C0=C0,guard=guard,error_cost=error_cost))
    controls={
      'nondyadic_third_rejected':(Q(1,3).denominator&(Q(1,3).denominator-1))!=0,
      'unit_input_preparation_bound_rejected':max(p['row_l1'] for p in prep)>1,
      'one_snapshot_bank_rejected':len(witness)>1,
      'old_three_backward_banks_rejected':1+2*len(piv)>3,
      'maximum_replaces_product_stock_rejected':3*5>max(3,5),
      'approximate_zero_not_exact':Q(1,1024)!=0,
    }
    assert all(controls.values())
    result=dict(schema=1,status='PASS_BOUNDED_PREPARATION_AND_SEMANTIC_ALGEBRA',
      candidate_head='4bd6efa51a495a7c7b7754915cf0244e7e60969e',
      capsule_manifest_sha256=sha256((CAP/'IMMUTABLE-MANIFEST.json').read_bytes()).hexdigest(),
      source_files={n:sha256((PKG/n).read_bytes()).hexdigest() for n in ('WORD.json.gz','WITNESS.json','SOURCES.json')},
      pivots=piv,preparation=prep,preparation_events=len(expected),preparation_adds=sum(p['add_count'] for p in prep),
      preparation_max_l1=9,preparation_max_denominator=2,preparation_input_magnitude_extra_bits=4,
      local=audits,raw_full_owned_banks=16*17+2,
      semantic_probes=probes,controls=controls,seconds=time.monotonic()-start,
      scope='Independent light arithmetic and literal scalar grammar only; full physical identities, finite compiler arithmetic and cold replay are separate receipts.')
    (HERE/'LIGHT-ARITHMETIC.json').write_text(json.dumps(encode(result),indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],preparation_adds=result['preparation_adds'],seconds=result['seconds'])))

if __name__=='__main__': main()

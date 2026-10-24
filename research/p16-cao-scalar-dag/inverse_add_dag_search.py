#!/usr/bin/env python3
"""Exact additive inverse-pair elimination on Cao Yifan's frozen native word.

A candidate removes two ADD instructions A_i<-c*A_j and A_i<--c*A_j
separated solely by gates commuting with that ADD, so their product is
the identity. The removal is applied to BOTH directions; native words are
regenerated; full paid profiles, and 632-column identities when applicable,
are checked. Zero candidates is an exact restriction on this bounded family.
"""
from collections import Counter
from copy import deepcopy
from pathlib import Path
from fractions import Fraction
from decimal import Decimal,localcontext
import gzip,json,sys
HERE=Path(__file__).resolve().parent
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else HERE.parents[2]
sys.path.insert(0,str(ROOT/'research/warp-interface-20261022'))
import warp_merge as W
F=W.F
def read(f):return json.loads(gzip.decompress(f.read_bytes()))
def operand(e):
    if e[0]!='scalar':return None
    g=e[1]
    if g[0]!='add' or g[1][0]!='L' or g[2][0]!='L':return None
    return (tuple(g[1]),tuple(g[2]),Fraction(g[3],g[4]))
def touches(e,regions):
    if e[0]=='scalar':
        return bool(set(W.roles(e)) & regions)
    if e[0]=='warp':
        return e[1][0]=='L' and e[1][1] in regions
    return False
def commute_with_pair(e,source,target):
    if e[0]=='warp':
        return not touches(e,{source,target})
    if e[0]!='scalar':return True
    g=e[1]
    if g[0]!='add':
        return not touches(e,{source,target})
    if g[1][0]!='L' or g[2][0]!='L':
        return not touches(e,{source,target})
    d,s=g[1][1],g[2][1]
    # [E_target,source, E_d,s]=0 iff target!=s and d!=source
    return target!=s and d!=source
def paid(w):
    return Counter(e[-1] for e in w if e[0] in ('climb','center'))
def scan():
    c,allwords=None,None
    data=read(ROOT/'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz')
    c=data['canonical'];allwords=data['programs']
    raw={d:[deepcopy(e) for e in word if e[0]!='climb']
         for d,word in allwords.items()}
    f=raw['forward'];b=raw['backward']
    assert len(f)==len(b)
    base=paid(allwords['forward'])
    assert base==Counter({1:2201,2:412,3:510,4:127,5:40,8:8})
    opportunities=[];considered=0
    for right in range(len(f)):
        x=operand(f[right])
        if x is None:continue
        tgt,src,coeff=x
        for left in range(max(0,right-160),right):
            y=operand(f[left])
            if y is None:continue
            if y[:2]!=(tgt,src) or y[2]!=-coeff:continue
            considered+=1
            if any(not commute_with_pair(f[k],src[1],tgt[1])
                   for k in range(left+1,right)):continue
            # Independently require ordinary inverse-transpose commuting
            # and cancellation at the SAME chronological event indices.
            bb1=operand(b[left]);bb2=operand(b[right])
            if bb1 is None or bb2 is None or bb1[:2]!=bb2[:2] or bb1[2]!=-bb2[2]:
                continue
            if any(not commute_with_pair(b[k],bb1[1][1],bb1[0][1])
                   for k in range(left+1,right)):continue
            opportunities.append((left,right))
    receipts={'status':'NO_GLOBAL_CLAIM',
      'pinned_source':'20bb93cd990d2ff683e4d0fc56b87a42cd5d3296',
      'candidate_window':160,
      'inverse_add_pairs_considered':considered,
      'commuting_dual_legal_pairs':len(opportunities),
      'examples':opportunities[:35],
      'source_paid_before':dict(sorted(base.items())),
      'new_kappa':False,'candidate_receipts':[]}
    V=None;X=None
    for left,right in opportunities[:15]:
        compiled={}
        try:
            for direction in ('forward','backward'):
                word=[e for i,e in enumerate(raw[direction]) if i not in (left,right)]
                compiled[direction]=W.synthesize(c,word)
            a=paid(compiled['forward']);bpaid=paid(compiled['backward'])
            assert a==bpaid
            with localcontext() as ctx:
                ctx.prec=55;t=Decimal(1)-Decimal('0.0030217758')
                delta=sum(Decimal(k)**t*(base[k]-a[k]) for k in set(base)|set(a))
            rec={'left':left,'right':right,'paid_gain':str(delta),
                 'modified_paid':dict(sorted(a.items()))}
            if delta>0:
                if V is None:
                    V=F.load(ROOT/'research/kappa-causal-continuation/buffer-borrowing/verify_buffers.py','cao_dag_rows')
                    X=F.load(ROOT/'research/kappa-rebuild/complex/native_extensions.py','cao_dag_literal')
                for direction in compiled:
                    rows,r=X.literal_replay(V,c,compiled[direction],direction=='backward')
                    assert all(rows['L',i]==V.expected(('L',i),[],direction=='backward',False) for i in range(632))
                rec['both_literal_directions']='PASS'
                receipts['status']='POSITIVE_NATIVE_MOMENT_DUAL_LITERAL_PHASE_OPEN'
            receipts['candidate_receipts'].append(rec)
        except (ValueError,AssertionError) as err:
            receipts['candidate_receipts'].append({'left':left,'right':right,
                                                   'rejection':str(err)})
    if receipts['status']=='NO_GLOBAL_CLAIM':
        receipts['status']='PASS_BOUNDED_INVERSE_ADD_SEARCH_NO_ADMITTED_NEW_KAPPA'
    (HERE/'SCALAR_DAG_INVERSE_PAIRS_RECEIPT.json').write_text(
        json.dumps(receipts,indent=2,sort_keys=True)+'\n')
    print(receipts['status'],'inverse_pair_considered',considered,
          'commuting_in_both_orientations',len(opportunities))
    print('SCREEN',receipts['candidate_receipts'][:3])
if __name__=='__main__':scan()

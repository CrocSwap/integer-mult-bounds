#!/usr/bin/env python3
"""Independent reverse-functionals, source frames and full BIT invoice audit.

Imports neither the new caller emitter nor its binary matrix/search code.
The unchanged native realization and common-head interface theorem are retained.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import gzip,hashlib,json,time
H=Path(__file__).resolve().parent
BASE=H.parent
CALLER=BASE/'bit_mixed_caller/BINARY-MIXED-CALLER.json.gz'
SOURCE=H/'inputs/BIT-NATIVE-WORD.json.gz'
CALLER_SHA='86c4574d47e406e560b3ae2602e52501d4da4bc4c082b4f31b21f6cfef362cc3'
SOURCE_SHA='51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78'

def need(v,s):
    if not v:raise ValueError(s)

def load(p,sha):
    b=p.read_bytes();need(hashlib.sha256(b).hexdigest()==sha,'exact input bytes')
    return json.loads(gzip.decompress(b))

def toggle(dst,src):
    dst.symmetric_difference_update(src)

def shift(a,body=(),head=False):
    out=set()
    for q,dd in a:
        r=list(dd)
        for s in body:r[s-1]+=1
        z=(q^int(head),tuple(r))
        if z in out:out.remove(z)
        else:out.add(z)
    return out

def backward(c,events=None):
    events=c['events']if events is None else events
    n=c['roles'];s=c['stages'];zero=(0,(0,)*s);checked=0
    for output in range(n):
        rr=[set()for _ in range(n)];rr[output]={zero}
        for e in reversed(events):
            op=e[0]
            if op=='ADD':_,a,b=e;toggle(rr[b],rr[a])
            elif op=='SWAP':_,a,b=e;rr[a],rr[b]=rr[b],rr[a]
            elif op=='QUERY':_,a,b=e;toggle(rr[b],shift(rr[a],head=True))
            elif op=='LOCAL':
                _,j,a,b=e
                rr[a]=shift(rr[a],[j])^shift(rr[b],[j],True)
                rr[b]=shift(rr[b],[j])
            elif op=='IDLE':_,a,b,ss=e;rr[a]=shift(rr[a],ss);rr[b]=shift(rr[b],ss)
            elif op=='IDLE_ONE':_,a,ss=e;rr[a]=shift(rr[a],ss)
            else:raise ValueError(op)
        diag=c['diagonal'][output]
        target=(diag['q'],tuple(int(j in diag['stages'])for j in range(1,s+1)))
        for i,row in enumerate(rr):
            need(row==({target}if i==output else set()),f'reverse coefficient {output},{i}')
            checked+=1
    return checked

def included(a,b):
    return all(sum(Q(x)*Q(y)for x,y in zip(v,w))==0 for v in a['B']for w in b['A'])

def matrix_inverse(a):
    n=len(a);r=[[Q(x)for x in row]+[Q(i==j)for j in range(n)]for i,row in enumerate(a)]
    det=Q(1)
    for j in range(n):
        k=next((i for i in range(j,n)if r[i][j]),None);need(k is not None,'invertible physical chart')
        if k!=j:r[k],r[j]=r[j],r[k];det=-det
        z=r[j][j];det*=z;r[j]=[x/z for x in r[j]]
        for i in range(n):
            if i!=j:
                z=r[i][j];r[i]=[x-z*y for x,y in zip(r[i],r[j])]
    return [row[n:]for row in r],det

def source_audit(w):
    n=w['public'];N=n+w['owned_fields'];at=w['start']+[None]*(N-n)
    rows=[1<<i for i in range(n)]+[0]*(N-n);ff=w['frames'];paid=Counter();lives=0;peak=0;live=0;cleared_nonzero=0
    for e in w['program']:
        op,a=e[:2]
        if op=='INIT':
            need(a>=n and at[a]is None,'fresh owned activation');at[a]=e[2];rows[a]=0;lives+=1;live+=1;peak=max(peak,live)
        elif op=='CLEAR':
            need(a>=n and at[a]==e[2],'owned erasure');cleared_nonzero+=bool(rows[a]);at[a]=None;rows[a]=0;live-=1
        elif op=='ADD':
            b=e[2];need(a!=b and at[a]==at[b]==e[3],'literal same-frame contact');rows[a]^=rows[b]
        elif op=='SWAP':
            b=e[2];at[a],at[b]=at[b],at[a];rows[a],rows[b]=rows[b],rows[a]
        elif op=='MOVE':
            old,new=e[2:];need(at[a]==old,'literal native entrance')
            A,B=ff[str(old)],ff[str(new)];r=abs(A['dim']-B['dim'])
            need(r>0 and(included(A,B)or included(B,A)),'nested native interface');at[a]=new;paid[r]+=1
        else:raise ValueError(op)
    need(at==w['final']+[None]*(N-n)and live==0,'all endpoints and owned lifetimes')
    for i in range(n):
        expected=(1<<i)if i<111 or i>=222 else(1<<i)^(1<<(i-111))
        need(rows[i]==expected,'all-column native scalar endpoint')
    charts=[]
    for i in range(111):
        U=ff[str(w['start'][i])];V=ff[str(w['final'][i+111])]
        need(U['dim']==1 and V['dim']==7,'main head and body dimensions')
        need(ff[str(w['final'][i])]['dim']==8 and ff[str(w['start'][i+111])]['dim']==0,'remaining quartet frames')
        u=U['B'][0];need(all(sum(Q(x)*Q(y)for x,y in zip(u,v))==0 for v in V['B']),'head/body annihilation')
        columns=[u]+V['B'];G=[list(x)for x in zip(*columns)];Gi,det=matrix_inverse(G)
        for row in range(8):
            for col in range(8):need(sum(Q(G[row][k])*Gi[k][col]for k in range(8))==int(row==col),'physical chart inverse')
        charts.append(dict(port=i,input_frame=w['start'][i],output_frame=w['final'][i+111],basis=G,inverse=[[str(x)for x in r]for r in Gi],determinant=str(det)))
    helpers=Counter()
    for i in range(222,n):
        a,b=ff[str(w['start'][i])],ff[str(w['final'][i])]
        need(included(a,b)or included(b,a),'productive helper frames')
        helpers[abs(a['dim']-b['dim'])]+=1
    return paid,helpers,dict(public=n,owned_labels=w['owned_fields'],owned_lifetimes=lives,peak_owned=peak,nonzero_owned_erasures=cleared_nonzero,checked_public_matrix_coefficients=n*n,exact_scalar_endpoint='X_i→X_i; Y_i→Y_i+X_i; each helper independent',native_edges=sum(paid.values()),charts=charts)

def main():
    start=time.monotonic();c=load(CALLER,CALLER_SHA);w=load(SOURCE,SOURCE_SHA)
    need((c['ports'],c['body_rank'],c['ambient_rank'])==(111,7,127),'actual BIT dimensions')
    need(c['native_source_sha256']==SOURCE_SHA,'source binding')
    count=backward(c);negative={}
    for op in ('LOCAL','QUERY','IDLE','IDLE_ONE'):
        es=[e[:]for e in c['events']];del es[next(i for i,e in enumerate(es)if e[0]==op)]
        try:backward(c,es)
        except ValueError as ex:negative[op]=str(ex)
        else:raise ValueError('unpaid operation was accepted')
    p0,t0,source=source_audit(w);ops=Counter(e[0]for e in c['events']);P=Counter({r:18*v for r,v in p0.items()});T=Counter({r:18*v for r,v in t0.items()})
    stages=[];embeddings=[]
    for e in c['events']:
        if e[0]=='LOCAL':
            stages.append(e[1]);embeddings.append(dict(stage=e[1],source=e[2],destination=e[3],head_axis=0,body_axes=list(range(1+7*(e[1]-1),1+7*e[1]))))
        elif e[0]=='QUERY':P[1]+=111
        elif e[0]=='IDLE':P[7*len(e[3])]+=222
        elif e[0]=='IDLE_ONE':P[7*len(e[2])]+=111
    need(sorted(stages)==list(range(1,19)),'fresh local stage allocation')
    need(set(x for e in embeddings for x in e['body_axes'])==set(range(1,127)),'disjoint body axes')
    for d in c['diagonal']:
        need(len(set(d['stages']))==len(d['stages'])and set(d['stages'])<=set(stages),'genuine target stage set')
        T[1+7*len(d['stages'])]+=111
    proposal=json.loads((BASE/'bit_mixed_caller/BINARY-MIXED-CALLER-RESULT.json').read_text())['invoice']
    need(dict(P)=={int(k):v for k,v in proposal['paid_profile'].items()},'independently rebuilt paid bill')
    need(dict(T)=={int(k):v for k,v in proposal['productive_profile'].items()},'independently rebuilt productive bill')
    report=dict(status='PASS_INDEPENDENT_BINARY_MIXED_CALLER_AND_SOURCE_BINDING',caller_sha256=CALLER_SHA,source_sha256=SOURCE_SHA,reverse_polynomial_coefficients=count,independent_body_variables=True,mutation_controls=negative,source=source,stage_embeddings=embeddings,physical_main_boundary_contacts=18*111*4,physical_binding_scope='Actual rational head/body quartet charts, literal nested source frames, disjoint fresh stage embeddings and exact all-column scalar source endpoint. Native transform realization and all-width common-head normalization use the unchanged retained frame/interface theorem; not an independent reproof of that theorem.',native_paid=dict(sorted(p0.items())),native_helpers=dict(sorted(t0.items())),paid=dict(sorted(P.items())),targets=dict(sorted(T.items())),event_counts=dict(ops),paid_jobs=sum(P.values()),productive_jobs=sum(T.values()),rank_surplus=sum(r*n for r,n in T.items())-sum(r*n for r,n in P.items()),new_global_kappa_claim=False,seconds=time.monotonic()-start)
    (H/'INDEPENDENT-BINARY-MIXED-AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items()if k not in ('source','stage_embeddings')},indent=2))

if __name__=='__main__':main()

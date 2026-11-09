#!/usr/bin/env python3
"""Independent reverse-mode native and formal caller audit; imports no author replay."""
from fractions import Fraction as Q
from pathlib import Path
from collections import Counter
import argparse, copy, gzip, hashlib, json, time

def read(path):
    raw=Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)

def need(ok,why):
    if not ok: raise ValueError(why)

def add_row(dst,src,value):
    for col,coef in src.items():
        new=dst.get(col,0)+value*coef
        if new: dst[col]=new
        else: dst.pop(col,None)

def native_dual(w):
    n=len(w['initial']); total=n+w['owned_fields']
    main=set(w['live'])|{r+112 for r in w['live']}|set(w['hosted']['X2'])|set(w['hosted']['Y2'])
    need(len(main)==400,'mixed-port main inventory')
    for i,x2,y2 in zip(w['hosted']['Dports'],w['hosted']['X2'],w['hosted']['Y2']):
        x,q=w['live'][i],w['ports'][i]
        y=x+112
        need(w['frames'][w['initial'][x]]==[q] and len(w['frames'][w['final'][x]])==9,'X charts')
        need(len(w['frames'][w['initial'][y]])==0,'Y initial chart')
        need((w['initial'][x2],w['final'][x2])==(w['initial'][x],w['final'][x]),'second X charts unchanged')
        need((w['initial'][y2],w['final'][y2])==(w['initial'][y],w['final'][y]),'second Y charts unchanged')
    known_zero=set(range(n,total))
    for idx,e in enumerate(w['program']):
        op,r=e[:2]
        if op in ('INIT','CLEAR'): known_zero.add(r)
        elif op in ('ADD','COPY'):
            if op=='COPY': need(r in known_zero,'COPY must enter a statically fresh zero')
            if e[2] not in known_zero: known_zero.discard(r)
    rows=[{i:Q(1)} for i in range(n)]+[{} for _ in range(total-n)]
    peak=0
    for idx,e in reversed(list(enumerate(w['program']))):
        op,dst,*a=e
        if op in ('ADD','COPY'):
            add_row(rows[a[0]],rows[dst],Q(a[1]))
            if op=='COPY': rows[dst]={}  # transpose of overwrite, not inverse
        elif op=='SCALE': rows[dst]={j:v*Q(a[0]) for j,v in rows[dst].items()}
        elif op in ('INIT','CLEAR'): rows[dst]={}  # dual ideal reset projection
        elif op!='MOVE': raise ValueError('unknown native operation '+op)
        if idx%100==0: peak=max(peak,sum(map(len,rows)))
    expected=[{i:Q(1)} for i in range(n)]+[{} for _ in range(total-n)]
    active={w['live'][i] for i in w['hosted']['Dports']}
    al,be=Q(w['hosted']['alpha']),Q(w['hosted']['beta'])
    for x in w['live']:
        if x in active: expected[x][x+112]=Q(1)
        else:
            expected[x][x+112]=be
            expected[x+112]={x:al,x+112:1+al*be}
    for x2,y2 in zip(w['hosted']['X2'],w['hosted']['Y2']):
        expected[y2][x2]=Q(w['hosted']['alpha2'])
    bad=[i for i in range(total) if rows[i]!=expected[i]]
    need(not bad,'native transpose mismatch '+str(bad[:12]))
    return dict(public=n,owned=total-n,endpoint_coefficients=n*n,events=len(w['program']),sampled_peak_nonzero_duals=peak,exact_transpose=True)

# Q(i)[q,D1,...,DL]/(q^4-1). A stage exponent has six bits; adding
# encodings adds exponents, rather than incorrectly treating them as idempotent.
ZERO=(Q(0),Q(0)); ONE=(Q(1),Q(0))
def cmul(x,y): return (x[0]*y[0]-x[1]*y[1],x[0]*y[1]+x[1]*y[0])
def add_poly(dst,src,coef=ONE,qs=0,ds=0):
    for (col,q,m),v in src.items():
        key=(col,(q+qs)%4,m+ds); v=cmul(v,coef); old=dst.get(key,ZERO)
        v=(old[0]+v[0],old[1]+v[1])
        if v!=ZERO: dst[key]=v
        else: dst.pop(key,None)
def scale_poly(src,coef=ONE,qs=0,ds=0):
    out={}; add_poly(out,src,coef,qs,ds); return out

def caller_dual(c):
    n,L=c['roles'],c['stages']
    # One monomial can acquire a given stage exponent at most once per
    # occurrence of that stage in an event. This conservative whole-program
    # bound prevents a six-bit carry from impersonating the next variable.
    occurrences=Counter()
    for e in c['events']:
        stages=[e[1]] if e[0]=='J' else e[3] if e[1]=='IDLE_ONE' else []
        need(all(type(s) is int and 1<=s<=L for s in stages),'stage exponent range')
        occurrences.update(stages)
    need(all(v<64 for v in occurrences.values()),'no packed polynomial exponent overflow')
    rows=[{(i,0,0):ONE} for i in range(n)]; peak=0
    for idx,e in reversed(list(enumerate(c['events']))):
        if e[0]=='J':
            st=e[1]; x,y,x2,y2=e[2]; shift=1<<(6*(st-1))
            for r in (x,y,x2,y2): rows[r]=scale_poly(rows[r],ds=shift)
            add_poly(rows[x],rows[y],qs=-1)
            add_poly(rows[y2],rows[x2],(Q(c['types']['A']['alpha2']),Q(0)),qs=1)
            u,v,al,be,*_=e[3]; al,be=Q(al),Q(be); ru,rv=rows[u],rows[v]
            nu=scale_poly(ru,ds=shift);add_poly(nu,rv,(be,Q(0)),qs=-1,ds=shift)
            nv=scale_poly(rv,(1+al*be,Q(0)),ds=shift);add_poly(nv,ru,(al,Q(0)),qs=1,ds=shift)
            rows[u],rows[v]=nu,nv
            continue
        op,*a=e[1:]
        if op=='ADD': add_poly(rows[a[1]],rows[a[0]],(Q(a[2]),Q(0)))
        elif op=='QUERY': add_poly(rows[a[1]],rows[a[0]],qs=a[2])
        elif op=='SCALE': rows[a[0]]=scale_poly(rows[a[0]],(Q(a[1]),Q(0)))
        elif op=='SWAP': rows[a[0]],rows[a[1]]=rows[a[1]],rows[a[0]]
        elif op=='LAMBDA':
            r,s=a; old=rows[r]; rows[r]=scale_poly(old,(Q(1,2),Q(s,2)))
            add_poly(rows[r],old,(Q(1,2),Q(-s,2)),qs=2)
        elif op=='IDLE_ONE': rows[a[0]]=scale_poly(rows[a[0]],ds=sum(1<<(6*(s-1)) for s in a[1]))
        elif op=='HOST2':
            st,x,y,x2,y2=a; shift=1<<(6*(st-1))
            for r in (x,y,x2,y2): rows[r]=scale_poly(rows[r],ds=shift)
            add_poly(rows[x],rows[y],qs=-1); add_poly(rows[y2],rows[x2],(Q(-1),Q(0)),qs=1)
        else: raise ValueError('unknown caller operation '+op)
        if idx%100==0: peak=max(peak,sum(map(len,rows)))
    expected=[None]*n
    for meta in c['types'].values():
        for i,(q,z,*mask) in enumerate(meta['diagonal']):
            need(z==0 and len(mask)==L,'diagonal schema')
            role=meta['offset']+i
            expected[role]={(role,q%4,sum(v<<(6*j) for j,v in enumerate(mask))):ONE}
    bad=[i for i in range(n) if rows[i]!=expected[i]]
    need(not bad,'formal caller transpose mismatch '+str(bad))
    return dict(roles=n,stage_variables=L,events=len(c['events']),matrix_coefficients=n*n,sampled_peak_monomials=peak,ring='Q(i)[q,D1,...,DL]/(q^4-1)',exact_transpose=True)

def fails(fn):
    try: fn()
    except ValueError: return True
    return False

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--word',required=True); ap.add_argument('--caller',required=True); ap.add_argument('--controls',action='store_true'); ap.add_argument('--output'); a=ap.parse_args()
    t=time.monotonic(); w,c=read(a.word),read(a.caller)
    out=dict(word_sha256=hashlib.sha256(Path(a.word).read_bytes()).hexdigest(),caller_sha256=hashlib.sha256(Path(a.caller).read_bytes()).hexdigest())
    out['native']=native_dual(w); print('PASS_NATIVE_EXACT_DUAL',json.dumps(out['native']),flush=True)
    out['caller']=caller_dual(c); print('PASS_CALLER_FORMAL_DUAL',json.dumps(out['caller']),flush=True)
    if a.controls:
        controls={}
        for ty in ('A','B'):
            for op in ('QUERY','IDLE_ONE','LAMBDA'):
                m=copy.deepcopy(c);del m['events'][next(i for i,e in enumerate(m['events']) if e[0]==ty and e[1]==op)]
                controls['delete_'+ty+'_'+op]=fails(lambda:caller_dual(m))
        m=copy.deepcopy(c);del m['events'][next(i for i,e in enumerate(m['events']) if e[0]=='J')]
        controls['delete_joint']=fails(lambda:caller_dual(m))
        m=copy.deepcopy(c);m['types']['B']['diagonal'][0][2]^=1
        controls['wrong_B_mask']=fails(lambda:caller_dual(m))
        m=copy.deepcopy(w);i=next(i for i,e in enumerate(m['program']) if e[0]=='SCALE');m['program'][i][2]=str(2*Q(m['program'][i][2]))
        controls['wrong_native_scale']=fails(lambda:native_dual(m))
        need(all(controls.values()),'nonrejecting controls '+str(controls));out['controls']=controls
        print('PASS_MIXED_DUAL_CONTROLS',json.dumps(controls),flush=True)
    out['elapsed_seconds']=time.monotonic()-t
    if a.output: Path(a.output).write_text(json.dumps(out,indent=2)+'\n')
    print('PASS_SHARED_NATIVE_DUAL_AUDIT')

if __name__=='__main__': main()

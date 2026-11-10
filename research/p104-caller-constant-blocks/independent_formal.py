#!/usr/bin/env python3
"""Separate lead implementation: exact whole-caller reverse polynomial identity.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
No author or predecessor scientific module is imported.
"""
from fractions import Fraction as Q
from pathlib import Path
from collections import Counter
import copy, gzip, hashlib, json
ZERO=(Q(0),Q(0)); ONE=(Q(1),Q(0))
def read(path):
    raw=Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)

def need(ok,why):
    if not ok: raise ValueError(why)

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
    n,L=c['roles'],c['stages']; rows=[{(i,0,0):ONE} for i in range(n)]; peak=0
    occurrences=Counter()
    for e in c['events']:
        if e[0]=='HOST2': occurrences[e[1]]+=1
        elif e[0]=='IDLE_ONE': occurrences.update(e[2])
    need(all(1 <= s <= L and count < 64 for s,count in occurrences.items()),
         'stage exponents exceed the proven six-bit packing bound')
    for idx,e in reversed(list(enumerate(c['events']))):
        op,*a=e
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
    expected=[]
    for i,(q,z,*mask) in enumerate(c['diagonal']):
        need(z==0 and len(mask)==L,'diagonal schema')
        expected.append({(i,q%4,sum(v<<(6*j) for j,v in enumerate(mask))):ONE})
    bad=[i for i in range(n) if rows[i]!=expected[i]]
    need(not bad,'formal caller transpose mismatch '+str(bad))
    return dict(roles=n,stage_variables=L,events=len(c['events']),matrix_coefficients=n*n,sampled_peak_monomials=peak,ring='Q(i)[q,D1,...,DL]/(q^4-1)',exact_transpose=True)

def fails(fn):
    try: fn()
    except ValueError: return True
    return False

def main():
    here=Path(__file__).resolve().parent
    pins={'caller-before.json':'c403bb58f732de8356ed7fef3717649b209ba9d37eb4b8000eec9d876dc7142f',
          'caller-after.json':'e83221e5de1cd75b92bbbc40057f07e406af9551bd511bae659fa7173d6d5332'}
    for name,sha in pins.items():
        p=here/'data'/name
        need(hashlib.sha256(p.read_bytes()).hexdigest()==sha,'frozen caller bytes')
        c=read(p)
        print(name,json.dumps(caller_dual(c),sort_keys=True))
    c=read(here/'data/caller-after.json')
    controls={}
    for op in ('QUERY','IDLE_ONE','LAMBDA','HOST2'):
        m=copy.deepcopy(c)
        del m['events'][next(i for i,e in enumerate(m['events']) if e[0]==op)]
        controls['delete_'+op]=fails(lambda:caller_dual(m))
    m=copy.deepcopy(c);i=next(i for i,e in enumerate(m['events']) if e[0]=='LAMBDA');m['events'][i][2]*=-1
    controls['flip_lambda']=fails(lambda:caller_dual(m))
    m=copy.deepcopy(c);m['diagonal'][0][2]^=1
    controls['wrong_target_mask']=fails(lambda:caller_dual(m))
    m=copy.deepcopy(c);m['events']=[['IDLE_ONE',0,[1]]]*64+m['events']
    controls['stage_exponent_packing_guard']=fails(lambda:caller_dual(m))
    need(all(controls.values()),'nonrejecting mutation control')
    print(json.dumps(controls,sort_keys=True))
    print('PASS_INDEPENDENT_FORMAL_CALLER')

if __name__=='__main__':main()

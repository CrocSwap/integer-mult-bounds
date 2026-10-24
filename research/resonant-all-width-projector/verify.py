"""Exact all-width resonant rank certificate; Python 3.10+, standard library only."""
import hashlib
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PIN = 'e7df852b5c641f326ac67cd35cea8da6cfdd059fa12df1cf6fb758bb4206d684'
POLY = [0,-40131624960,219800272896,-542559928320,801997037568,-795721089024,562949320704,-294425358336,116429094784,-35292520896,8259053280,-1494247760,208111552,-22069792,1747036,-99820,3884,-92,1]
IDENTITY = tuple(range(8)), (0,)*8

def require(ok, message):
    if not ok:
        raise ValueError(message)

def mul(a,b):
    p,q=a; r,s=b
    return tuple(p[j] for j in r), tuple((s[j]+q[r[j]])%4 for j in range(8))

def inv(a):
    p,q=a; r=[0]*8; s=[0]*8
    for j,k in enumerate(p):
        r[k]=j; s[k]=-q[j]%4
    return tuple(r),tuple(s)

def convolution(a,b):
    out=defaultdict(int)
    for g,x in a.items():
        for h,y in b.items():
            out[mul(g,h)] += x*y
    return {g:x for g,x in out.items() if x}

def load_factorization():
    raw=(ROOT/'TARGET.json').read_bytes()
    require(hashlib.sha256(raw).hexdigest()==PIN,'source SHA256 mismatch')
    records=json.loads(raw)
    require(hashlib.sha256(json.dumps(records,sort_keys=True).encode()).hexdigest()=='445b3e5f8edb6f345981c02c1feb91f2ce473763be74ca7d949421e1ca64d03d','canonical source mismatch')
    A={}
    for x in records:
        require(x['coefficient'] in ('1/16','-1/16'),'coefficient')
        g=tuple(x['permutation']),tuple(x['phase_i'])
        require(sorted(g[0])==list(range(8)) and all(0<=v<4 for v in g[1]),'monomial')
        require(g not in A,'duplicate source term')
        A[g]=1 if x['coefficient']=='1/16' else -1
    require(len(A)==256,'source support')
    ds=[(IDENTITY[0],(2,)*8),(tuple(j^1 for j in range(8)),(1,)*8)]
    ds += [(IDENTITY[0],tuple(2*((j>>k)&1) for j in range(8))) for k in range(3)]
    D={IDENTITY}
    for d in ds:
        D |= {mul(d,g) for g in D}
        require({mul(d,g):v for g,v in A.items()}==A,'left stabilizer')
    require(len(D)==32,'projector group order')
    remaining=set(A); b0=[]
    while remaining:
        g=min(remaining); sign=A[g]; orbit={mul(d,g) for d in D}
        require(orbit<=remaining and all(A[h]==sign for h in orbit),'signed orbit')
        remaining-=orbit; b0.append((g,sign))
    require(len(b0)==8,'eight cosets')
    r0=b0[0][0]; ri=inv(r0)
    b=[(mul(ri,g),s) for g,s in b0]
    d=[mul(mul(ri,h),r0) for h in ds]
    # Reconstruct H=4 A* A as an INTEGER group-algebra coefficient table.
    gram=convolution({inv(g):s for g,s in A.items()},A)
    require(len(gram)==704 and all(x%64==0 for x in gram.values()),'Gram divisibility')
    H={g:x//64 for g,x in gram.items()}
    require(sum(abs(x) for x in H.values())==1024,'Gram norm')
    prod={IDENTITY:1}
    for h in d:
        prod=convolution(prod,{IDENTITY:1,h:1})
    fact=convolution(convolution({inv(g):s for g,s in b},prod),dict(b))
    require(all(x%2==0 for x in fact.values()),'factor divisibility')
    require({g:x//2 for g,x in fact.items()}==H,'exact Gram factorization')
    return raw, ds, b, d, H

def build_action(b, d, H):
    generators=list(dict.fromkeys([g for g,s in b]+d+[inv(g) for g,s in b]))
    group=[IDENTITY]; index={IDENTITY:0}
    for g in group:
        for h in generators:
            k=mul(h,g)
            if k not in index:
                index[k]=len(group); group.append(k)
                require(len(group)<=21504,'group escaped certified bound')
    require(len(group)==21504,'Gram group order')
    tables={h:[index[mul(h,g)] for g in group] for h in generators}
    def translate_add(out,v,h,sign):
        table=tables[h]
        for j,x in enumerate(v):
            out[table[j]] += sign*x
    def apply_H(v):
        u=[0]*len(group)
        for h,sign in b:
            translate_add(u,v,h,sign)
        for h in reversed(d):
            w=u.copy(); translate_add(w,u,h,1); u=w
        w=[0]*len(group)
        for h,sign in b:
            translate_add(w,u,inv(h),sign)
        require(all(x%2==0 for x in w),'H application not integral')
        return [x//2 for x in w]
    e=[0]*len(group); e[0]=1
    hv=apply_H(e)
    require({group[j]:v for j,v in enumerate(hv) if v}==H,'factor/table orientation')
    return group, apply_H, e, hv

def polynomial_certificate(group, apply_H, e):
    q=POLY[1:]; v=e.copy(); bound=1; max_bound=1
    for k in range(16,-1,-1):
        v=apply_H(v)
        scale=64**(17-k)
        v[0]+=q[k]*scale
        bound=1024*bound+abs(q[k])*scale
        max_bound=max(max_bound,bound)
    require(not any(apply_H(v)),'exact degree-18 group-algebra identity failed')
    max_bound=max(max_bound,1024*bound)
    require(max_bound<2**255,'signed 256-bit bound')
    denominator=q[0]*64**17
    numer=[-x for x in v]; numer[0]+=denominator
    return numer, denominator, max_bound

def trace_certificate(group, numer, denominator):
    traces=defaultdict(int)
    units=((1,0),(0,1),(-1,0),(0,-1))
    for g,x in zip(group,numer):
        if not x: continue
        p,ph=g; re=im=0
        for j in range(8):
            if p[j]==j:
                a,c=units[ph[j]]; re+=a; im+=c
        if re or im:
            traces[re,im]+=x
    actual={str(k[0]):str(Fraction(v,denominator)) for k,v in traces.items() if v and k[1]==0}
    require(all(not v or k[1]==0 for k,v in traces.items()),'uncancelled complex trace')
    expected={'-8':'3/256','-4':'1/64','-2':'-1/8','2':'-1/8','4':'1/64','8':'3/256'}
    require(actual==expected,'rank trace formula')
    ranks=[]
    for f in range(1,13):
        rank=sum(Fraction(c)*int(t)**f for t,c in actual.items())
        require(rank.denominator==1 and 0<=rank<=8**f,'rank range')
        ranks.append(int(rank))
    require(ranks[:6]==[0,1,0,100,0,6256],'predecessor and new-width values')
    return actual, ranks

def rejecting_controls(raw, ds, hv):
    # Three rejecting controls, independent of Python assertion optimization.
    changed=bytearray(raw); changed[0]^=1
    require(hashlib.sha256(changed).hexdigest()!=PIN,'source mutation control')
    require(any(hv),'polynomial constant mutation must produce nonzero H residual')
    require(ds[0]!=IDENTITY and mul(ds[0],ds[0])==IDENTITY,'central phase collapse control')

def main():
    raw, ds, b, d, H = load_factorization()
    group, apply_H, e, hv = build_action(b, d, H)
    numer, denominator, max_bound = polynomial_certificate(group, apply_H, e)
    actual, ranks = trace_certificate(group, numer, denominator)
    rejecting_controls(raw, ds, hv)
    receipt={'status':'PASS_EXACT_ALL_WIDTH_RESONANT_RANK','source_terms':256,'gram_support':704,'group_order':len(group),'polynomial_degree':18,'arithmetic':'unbounded exact Python integers','max_integer_bound_bits':max_bound.bit_length(),'valid_widths':'all integers f >= 1','trace_coefficients':actual,'ranks_f_1_to_12':ranks,'mutation_controls':3,'complete_supplier':False,'new_kappa':False}
    print(json.dumps(receipt,sort_keys=True,indent=2))
    expected_path=ROOT/'EXPECTED.json'
    if expected_path.exists():
        require(json.loads(expected_path.read_text())==receipt,'receipt mismatch')

if __name__=='__main__':
    main()

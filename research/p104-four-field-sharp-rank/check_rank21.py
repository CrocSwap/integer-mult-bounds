#!/usr/bin/env python3
"""Independent exact q=2,n=4 four-stage root construction, seed 78.

Original construction in this file; no predecessor executable imported.
All arithmetic uses fractions. Prepared with OpenAI Codex assistance.
"""
from fractions import Fraction as F
import argparse
import copy
import hashlib
import json
from pathlib import Path


def mat(a): return [[F(x) for x in row] for row in a]
def zero(n, m=None): return [[F(0) for _ in range(n if m is None else m)] for _ in range(n)]
def eye(n): return [[F(i == j) for j in range(n)] for i in range(n)]
def add(a, b): return [[x+y for x,y in zip(ar,br)] for ar,br in zip(a,b)]
def scale(c,a): return [[c*x for x in row] for row in a]
def sub(a,b): return add(a,scale(-1,b))
def mul(a,b): return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]
def stack(*a): return [row[:] for m in a for row in m]
def beside(*a): return [sum((list(m[i]) for m in a),[]) for i in range(len(a[0]))]
def diag(*aa):
    n=sum(len(a) for a in aa); out=zero(n); k=0
    for a in aa:
        for i,row in enumerate(a):
            for j,x in enumerate(row): out[k+i][k+j]=x
        k+=len(a)
    return out
def rank(a):
    a=[r[:] for r in a]; i=0
    for j in range(len(a[0])):
        k=next((k for k in range(i,len(a)) if a[k][j]),None)
        if k is None: continue
        a[i],a[k]=a[k],a[i]; c=a[i][j]; a[i]=[x/c for x in a[i]]
        for k in range(len(a)):
            if k!=i:
                c=a[k][j]; a[k]=[x-c*y for x,y in zip(a[k],a[i])]
        i+=1
        if i==len(a): break
    return i
def inverse(a):
    n=len(a); a=beside(a,eye(n))
    for j in range(n):
        k=next(k for k in range(j,n) if a[k][j]); a[j],a[k]=a[k],a[j]
        c=a[j][j]; a[j]=[x/c for x in a[j]]
        for k in range(n):
            if k!=j:
                c=a[k][j]; a[k]=[x-c*y for x,y in zip(a[k],a[j])]
    return [row[n:] for row in a]
def determinant(a):
    a=[r[:] for r in a]; out=F(1)
    for j in range(len(a)):
        k=next((k for k in range(j,len(a)) if a[k][j]),None)
        if k is None: return F(0)
        if k!=j: a[j],a[k]=a[k],a[j]; out=-out
        c=a[j][j]; out*=c
        for k in range(j+1,len(a)):
            t=a[k][j]/c; a[k]=[x-t*y for x,y in zip(a[k],a[j])]
    return out
def require(ok, message):
    if not ok: raise AssertionError(message)
def same(a,b): return a==b


def fixture():
    i=eye(2); z=zero(2); e=mat([[1,0],[0,0]]); f=sub(i,e)
    u0=stack(i,i,z,z); v0=beside(scale(-1,i),i,z,z)
    u1=stack(add(i,e),e,e,scale(-1,e))
    v1=beside(scale(-1,e),add(i,e),scale(-1,f),scale(-1,f))
    u3=stack(i,z,z,i); v3=beside(i,z,scale(-2,i),scale(-1,i))
    u4=stack(i,z,i,z); v4=beside(i,z,scale(-1,i),z)
    u2=sub(add(sub(u1,u0),u3),u4)
    v2=sub(add(sub(v1,v0),v3),v4)
    uu=[u0,u1,u2,u3,u4]; vv=[v0,v1,v2,v3,v4]
    rr=[mul(u,v) for u,v in zip(uu,vv)]
    t=mat([[0,1,-1,1],[0,0,0,0],[0,0,1,0],[0,1,0,1]])
    d=mat([[1,0,0,0],[0,1,0,0],[0,0,0,0],[0,0,-1,1]])
    pp=[diag(i,i,z,z),diag(i,i,t),None,diag(i,z,i,i),diag(i,z,d)]
    hz=mat([[1,0,1,-1],[0,0,0,1],[0,1,0,0],[1,1,0,-1]])
    h=diag(i,i,hz)
    masks=[15,15,3,3,14,6,12,12]
    return uu,vv,rr,pp,h,masks


def poly_mul_stage(poly,p,bit):
    out={}
    for mask,a in poly.items():
        for b,c in [(0,sub(eye(8),p)),(bit,p)]:
            key=mask|b; term=mul(c,a)
            out[key]=add(out.get(key,zero(8)),term)
    return out


def full_word(rr,pp,s,omit_query=None,omit_stage=None):
    out={0:eye(8)}; bit=1
    for site in range(5):
        query=eye(8) if site==omit_query else add(eye(8),scale(s-1,rr[site]))
        out={mask:mul(query,a) for mask,a in out.items()}
        if pp[site] is not None:
            if site!=omit_stage: out=poly_mul_stage(out,pp[site],bit)
            bit*=2
    return out


def integral_formal_word(rr,pp):
    """Direct multiplication with S exponents reduced modulo two over Z."""
    out={(0,0):eye(8)}; stage_bit=1
    for site in range(5):
        new={}
        for (mask,sbit),a in out.items():
            for qbit,qmatrix in [(0,sub(eye(8),rr[site])),(1,rr[site])]:
                key=(mask,sbit^qbit)
                new[key]=add(new.get(key,zero(8)),mul(qmatrix,a))
        out=new
        if pp[site] is None: continue
        new={}
        for (mask,sbit),a in out.items():
            for bit,pmatrix in [(0,sub(eye(8),pp[site])),(stage_bit,pp[site])]:
                key=(mask|bit,sbit)
                new[key]=add(new.get(key,zero(8)),mul(pmatrix,a))
        out=new; stage_bit*=2
    return out


def run():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture",type=Path,default=Path(__file__).with_name("ROOT-RANK21.json"))
    parser.add_argument("--emit",type=Path,help="Explicitly generate a new fixture at this path; default is read-only verification")
    args=parser.parse_args()
    uu,vv,rr,pp,h,masks=fixture(); ident=eye(8); zz=zero(8)
    require(rank(h)==8,"independent arbitrary-input basis")
    hinv=inverse(h)
    require(determinant(h)==-1,"unimodular H determinant")
    require(all(x.denominator==1 for row in hinv for x in row),"integral H inverse")
    gram_count=0
    for a in range(5):
        require(rank(uu[a])==rank(vv[a])==rank(rr[a])==2,f"query rank {a}")
        require(mul(rr[a],rr[a])==zz,f"square zero {a}")
        for b in range(5):
            require(mul(vv[a],uu[b])==scale((a>b)-(a<b),eye(2)),f"Gram {a},{b}")
            gram_count+=1
    prefix=ident
    ranks=[]; bit=1
    for site in range(5):
        prefix=mul(sub(ident,scale(2,rr[site])),prefix)
        p=pp[site]
        if p is None: continue
        require(mul(p,p)==p,f"idempotence {site}")
        require(mul(p,rr[site])==mul(rr[site],p)==rr[site],f"support {site}")
        require(mul(p,prefix)==mul(prefix,p),f"actual prefix {site}")
        maskdiag=[[F(i==j and masks[i]&bit!=0) for j in range(8)] for i in range(8)]
        require(mul(p,h)==mul(h,maskdiag),f"joint mask {site}")
        ranks.append(rank(p)); bit*=2
    require(prefix==scale(-1,ident),"full -I query endpoint")
    require(ranks==[4,6,6,5] and sum(ranks)==21,"stage ranks")
    for i,p in enumerate(pp):
        if p is None: continue
        for j,q in enumerate(pp):
            if q is not None: require(mul(p,q)==mul(q,p),f"commutation {i},{j}")
    coefficients=0
    for s in [1,-1]:
        word=full_word(rr,pp,s)
        for mask in range(16):
            want=scale(s,[[F(i==j and masks[i]==mask) for j in range(8)] for i in range(8)])
            require(mul(word.get(mask,zz),h)==mul(h,want),f"literal formal coefficient S={s}, mask={mask}")
            coefficients+=1
    controls=[]
    for site in range(5):
        bad=full_word(rr,pp,-1,omit_query=site)
        controls.append(any(mul(bad.get(mask,zz),h)!=mul(h,scale(-1,[[F(i==j and masks[i]==mask) for j in range(8)] for i in range(8)])) for mask in range(16)))
    require(all(controls),"omitted query controls")
    stage_controls=[]
    for site in [0,1,3,4]:
        bad=full_word(rr,pp,1,omit_stage=site)
        stage_controls.append(any(
            mul(bad.get(mask,zz),h)!=mul(h,[[F(i==j and masks[i]==mask) for j in range(8)] for i in range(8)])
            for mask in range(16)))
    require(all(stage_controls),"omitted stage controls")
    formal=integral_formal_word(rr,pp)
    for mask in range(16):
        for sbit in range(2):
            want=[[F(sbit==1 and i==j and masks[i]==mask) for j in range(8)] for i in range(8)]
            require(mul(formal.get((mask,sbit),zz),h)==mul(h,want),f"integral formal coefficient mask={mask},S^{sbit}")
    def integers(a): return [[int(x) if x.denominator==1 else str(x) for x in row] for row in a]
    artifact={
        "schema":"independent-exact-four-stage-root-v1", "seed":78,"n":4,"q":2,
        "stage_sites":[0,1,3,4],"stage_ranks":ranks,"total_stage_rank":21,
        "input_dimension":8,"U":[integers(u) for u in uu],"V":[integers(v) for v in vv],
        "R":[integers(r) for r in rr],"P":{str(j):integers(p) for j,p in enumerate(pp) if p is not None},
        "H":integers(h),"output_stage_masks":masks,
        "output_monomials":["ABCD","ABCD","AB","AB","BCD","BC","CD","CD"],
        "identity":"H^-1 L(S,A,B,C,D) H = S diag(ABCD,ABCD,AB,AB,BCD,BC,CD,CD)",
        "source_context":{"canonical_base":"7c49fe32c55de02c2c873655c804b16e4c3fef0a","predecessor_pr":6773,"predecessor_head":"10ecaad298e6a6af7416fbd2baca15674fcadf5b"},
        "checks":{"gram_blocks":gram_count,"full_formal_coefficients":coefficients,"query_omission_controls":controls,"stage_omission_controls":stage_controls},
        "scope":"Coefficient-space identity only. No paid supplier, native phase, ownership, physical port, cost or all-size discharge."
    }
    expected_bytes=(json.dumps(artifact,indent=2)+"\n").encode()
    def verify_fixture(payload):
        require(payload==expected_bytes,"fixture bytes differ from independent exact regeneration")
    corruption_controls=[]
    for field in ["U","R","P","H","output_stage_masks"]:
        bad=copy.deepcopy(artifact)
        if field=="P": bad[field]["0"][0][0]+=1
        elif field=="output_stage_masks": bad[field][0]^=1
        elif field=="H": bad[field][0][0]+=1
        else: bad[field][0][0][0]+=1
        try: verify_fixture((json.dumps(bad,indent=2)+"\n").encode())
        except AssertionError: corruption_controls.append(field)
    require(len(corruption_controls)==5,"fixture corruption controls")
    if args.emit is not None:
        args.emit.write_bytes(expected_bytes)
        fixture_bytes=expected_bytes
    else:
        fixture_bytes=args.fixture.read_bytes()
        verify_fixture(fixture_bytes)
    maxima={name:max(abs(x) for matrix in matrices for row in matrix for x in row) for name,matrices in [("U",uu),("V",vv),("R",rr),("P",[p for p in pp if p is not None]),("H",[h]),("H_inverse",[hinv])]}
    print(json.dumps({"status":"PASS_EXACT_RANK21_ROOT","read_only":args.emit is None,"stage_ranks":ranks,"inventory":artifact["output_monomials"],"gram_blocks":gram_count,"character_coefficients":coefficients,"direct_integral_formal_coefficients":32,"word_omission_controls":len(controls)+len(stage_controls),"fixture_corruption_controls":corruption_controls,"determinant_H":-1,"max_abs_integer_coefficients":{key:int(value) for key,value in maxima.items()},"artifact_sha256":hashlib.sha256(fixture_bytes).hexdigest()},indent=2))


if __name__=="__main__": run()

"""Compare the closed count with literal GL actions and a kernel-lattice oracle.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from hashlib import sha1, sha256
from functools import lru_cache
from math import prod
from random import Random
import json
import runpy
import sys

P=Path(__file__).resolve().parent
C=runpy.run_path(str(P/'count.py'));L=runpy.run_path(str(P/'literal.py'));need=C['need']


def authenticate(raw,pin):
    need(sha256(raw).hexdigest()==pin['sha256'],'Frozen SHA256')
    need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==pin['git_blob'],'Frozen Git blob')


def reject(f):
    try:f()
    except ValueError:return
    raise ValueError('Invalid input accepted')


def run():
    pins=json.loads((P/'SOURCES.json').read_text())['retained_predecessors']
    for pin in pins:
        raw=(P/pin['local']).read_bytes();authenticate(raw,pin)
        reject(lambda raw=raw,pin=pin:authenticate(raw+b'changed',pin))
    R=runpy.run_path(str(P/'inputs/pr6533-completion.py'))
    @lru_cache(maxsize=None)
    def formula(q,values):return C['count_profile'](q,*values)
    census=[];total=0;positive=0;profile_controls=set()
    for n,q in [(0,2),(1,2),(2,2),(3,2),(2,3),(2,4),(2,5)]:
        sp=L['universe'](n,q);S=sp['S']
        for u in range(n+1):
            literal,matrices=L['counts'](sp,u);digest=sha256();pos=0;mass=0
            for a in range(S):
                for b in range(S):
                    for c in range(S):
                        for d in range(S):
                            values,ok=L['normalized_profile'](sp,u,a,b,c,d)
                            value=formula(q,tuple(values)) if ok else 0
                            index=((a*S+b)*S+c)*S+d
                            need(value==literal[index],'Complete literal GL count')
                            pos+=bool(value);mass+=value;digest.update(str(value).encode()+b',')
                            if ok and value:
                                swapped=list(values);swapped[2],swapped[3]=swapped[3],swapped[2];swapped[5],swapped[6]=swapped[6],swapped[5];swapped[10],swapped[11]=swapped[11],swapped[10]
                                need(value==formula(q,tuple(swapped)),'Symmetric capacity count')
                                profile_controls.add((q,*values))
            total+=S**4;positive+=pos
            census.append(dict(n=n,q=q,fixed_rank=u,contracts=S**4,positive=pos,gl_maps=matrices,count_sum=mass,sha256=digest.hexdigest()))
    random=Random(4006535);kernel_checks=0;arbitrary_maps=0
    for n,p,rounds in [(2,2,18),(2,3,18),(3,2,20),(3,3,12),(4,2,10)]:
        spaces=R['subspaces'](n,p)
        for _ in range(rounds):
            U=random.choice(spaces);u=len(U)
            while True:
                E=tuple(tuple(random.randrange(p) for _ in range(n)) for _ in range(u))
                if R['rank'](E,p,n)==u:break
            fixed=tuple(zip(U,E));caps=tuple((random.choice(spaces),random.choice(spaces)) for _ in range(2))
            got,profile=C['contract'](n,p,fixed,caps,R)
            exact=R['fixed_rank_counts'](n,p,fixed,caps)
            need(got==exact['rank_counts'][n],'Independent affine kernel-lattice count')
            kernel_checks+=1;arbitrary_maps+=bool(u)
    # The named oblique and nonzero-delta controls use literal vector data.
    e=lambda n,i:tuple(int(j==i) for j in range(n))
    def sumv(x,y,p):return tuple((a+b)%p for a,b in zip(x,y))
    named=[]
    for p in (2,3,5):
        e1,e2,e3=[e(3,i) for i in range(3)]
        fixed=((e1,e1),(e2,e2));caps=(((sumv(e1,e3,p),),(e1,e3)),((e3,),(e1,sumv(e2,e3,p))))
        value,profile=C['contract'](3,p,fixed,caps,R);need(value==0,'Coupled oblique zero count');named.append(dict(field=p,name='oblique',count=value,profile=profile))
        e1,e2=[e(2,i) for i in range(2)];u=tuple((a-b)%p for a,b in zip(e1,e2))
        value,profile=C['contract'](2,p,((u,u),),(((e1,),(e1,)),((e2,),(e2,))),R)
        need(value==1,'Nonzero delta has one completion');named.append(dict(field=p,name='nonzero-delta',count=value,profile=profile))
    # Independent elementary product counts in dimensions far above enumeration.
    large=[]
    for q in (2,3,4,9):
        n,u=120,20
        for name,values,want in [
            ('free',[n,u,0,0,0,0,0,0,0,0,0,0,0],prod(q**n-q**i for i in range(u,n))),
            ('unrestricted-capacities',[n,u,40,40,60,100,100,100,20,100,20,20,20],prod(q**n-q**i for i in range(u,n))),
            ('two-block',[n,u,50,50,100,50,50,100,0,0,20,20,20],q**2000*C['injections'](50,50,q)**2),
            ('nonzero-delta',[n,u,20,20,20,20,20,20,0,0,0,0,0],prod(q**n-q**i for i in range(40,n)))]:
            got=C['count_profile'](q,*values);need(got==want,'Large independent product formula')
            large.append(dict(field=q,name=name,profile=values,count_hex=hex(got),bits=got.bit_length()))
    # Check actual large vector contracts, including an independent fixed injection.
    large_vectors=[]
    for p in (2,3):
        n=48;u=8;E=[e(n,i) for i in range(n)]
        fixed=tuple((E[i],E[i]) for i in range(u))
        caps=((tuple(E[8:28]),tuple(E[:28])),(tuple(E[28:48]),tuple(E[:8]+E[28:48])))
        got,profile=C['contract'](n,p,fixed,caps,R)
        want=p**(8*40)*C['injections'](20,20,p)**2
        need(got==want,'Large actual two-block input')
        large_vectors.append(dict(field=p,dimension=n,profile=profile,count_hex=hex(got)))
    # Each omitted multiplicative factor has an actual positive finite counterexample.
    factor_witnesses={}
    for vals in sorted(profile_controls):
        q,n,u,a,b,s,c,d,t,k,ell,ec,ed,ecd=vals;j=a+b-s;alpha=a-j;beta=b-j
        factors={'common_lift':q**(ell*(j-k)), 'quotient_lift':q**(j*(alpha+beta)),
                 'fixed_image_lift':q**(ecd*j+ec*alpha+ed*beta),
                 'ambient_extension':prod(q**n-q**i for i in range(u+s,n))}
        for name,factor in factors.items():
            if factor>1 and name not in factor_witnesses:
                value=C['count_profile'](*vals);need(value%factor==0 and value//factor!=value,'Omitted factor changes exact count')
                factor_witnesses[name]=dict(profile=list(vals),count=value,mutant=value//factor)
    need(len(factor_witnesses)==4,'All lift and extension omission controls')
    bad=[lambda:C['count_profile'](6,1,0,0,0,0,0,0,0,0,0,0,0,0),
         lambda:C['count_profile'](2,-1,0,0,0,0,0,0,0,0,0,0,0,0),
         lambda:C['count_profile'](2,1,0,1,1,0,1,1,1,0,0,0,0,0),
         lambda:C['contract'](2,4,(),(((),()),((),())),R),
         lambda:C['contract'](2,2,(((1,0),(0,0)),),(((),()),((),())),R),
         lambda:C['contract'](2,2,(),(((),()),),R),
         lambda:C['contract'](2,2,(),((((2,0),),()),((),())),R)]
    for f in bad:reject(f)
    return dict(status='PASS_TWO_CAPACITY_COMPLETION_COUNT',census=census,contracts=total,positive=positive,
                distinct_positive_profiles=len(profile_controls),kernel_oracle_checks=kernel_checks,nonzero_fixed_maps=arbitrary_maps,
                named_controls=named,large_formulas=large,large_vector_contracts=large_vectors,
                omitted_factor_controls=factor_witnesses,invalid_controls=len(bad),source_corruptions=len(pins),
                scope='All-finite-field two-capacity count; executable prime-field extraction and literal F4 corroboration. No native or kappa claim.')


if __name__=='__main__':
    value=run()
    if '--write-result' in sys.argv:(P/'RESULT.json').write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')
    else:need(value==json.loads((P/'RESULT.json').read_text()),'Exact result receipt')
    print(json.dumps({k:value[k] for k in ('status','contracts','positive','distinct_positive_profiles','kernel_oracle_checks','invalid_controls')},sort_keys=True))

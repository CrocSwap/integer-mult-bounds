"""Compare incidence inversion with complete matrix and factor domains.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
import argparse
import hashlib
from itertools import product
import json
from pathlib import Path
import sys
import types

P=Path(__file__).resolve().parent
ROOT=P.parents[1]


def need(ok,message):
    if not ok:raise ValueError(message)


def load(name,path):
    m=types.ModuleType(name);m.__file__=str(path);sys.modules[name]=m
    exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__)
    return m


class Field:
    def __init__(self,q):
        self.q=q
        self.poly={4:0b111,8:0b1011}.get(q)
        self.add=lambda a,b:(a^b) if self.poly else (a+b)%q
        self.neg=lambda a:a if self.poly else (-a)%q
        self.inv={a:next(b for b in range(1,q) if self.mul(a,b)==1) for a in range(1,q)}
    def mul(self,a,b):
        if not self.poly:return a*b%self.q
        out=0
        while b:
            if b&1:out^=a
            b>>=1;a<<=1
            if a&self.q:a^=self.poly
        return out
    def rank(self,a):
        a=[row[:] for row in a]
        if not a:return 0
        rank=0
        for j in range(len(a[0])):
            k=next((i for i in range(rank,len(a)) if a[i][j]),None)
            if k is None:continue
            a[k],a[rank]=a[rank],a[k]
            inv=self.inv[a[rank][j]];a[rank]=[self.mul(inv,v) for v in a[rank]]
            for i in range(rank+1,len(a)):
                c=a[i][j]
                a[i]=[self.add(x,self.neg(self.mul(c,y))) for x,y in zip(a[i],a[rank])]
            rank+=1
            if rank==len(a):break
        return rank
    def mm(self,x,y,d):
        out=[]
        for row in x:
            result=[]
            for j in range(d):
                value=0
                for k,a in enumerate(row):value=self.add(value,self.mul(a,y[k][j]))
                result.append(value)
            out.append(result)
        return out


def matrices(r,c,q):
    for v in product(range(q),repeat=r*c):yield [list(v[i*c:(i+1)*c]) for i in range(r)]


def fingerprint(value):
    raw=value.to_bytes(max(1,(value.bit_length()+7)//8),'big')
    return dict(bits=value.bit_length(),sha256=hashlib.sha256(raw).hexdigest())


def inverse(field, a):
    n=len(a);a=[row[:] + [int(i==j) for j in range(n)] for i,row in enumerate(a)]
    for j in range(n):
        k=next(i for i in range(j,n) if a[i][j])
        a[k],a[j]=a[j],a[k];scale=field.inv[a[j][j]]
        a[j]=[field.mul(scale,v) for v in a[j]]
        for i in range(n):
            if i!=j:
                c=a[i][j]
                a[i]=[field.add(x,field.neg(field.mul(c,y))) for x,y in zip(a[i],a[j])]
    return [row[n:] for row in a]


def literal_f4_splits(c):
    f=Field(4);counts=Counter();checked=0
    for inclusion in product(range(4),repeat=3):
        if not any(inclusion):continue
        for projection in product(range(4),repeat=3):
            checked+=1
            def compress(mask):
                value=0
                for x,y,m in zip(projection,inclusion,mask):
                    if m:value=f.add(value,f.mul(x,y))
                return value
            if (compress((1,1,1)),compress((1,0,1)),compress((0,1,1)))!=(1,2,2):continue
            pivot=next(j for j in range(3) if projection[j])
            kernel=[]
            for j in range(3):
                if j!=pivot:
                    v=[0]*3;v[j]=1;v[pivot]=f.neg(f.mul(projection[j],f.inv[projection[pivot]]));kernel.append(v)
            header=[list(row) for row in zip(inclusion,*kernel)];inv=inverse(f,header)
            def schur(mask):
                p=f.mm(inv,[[f.mul(mask[i],v) for v in header[i]] for i in range(3)],3)
                need(p[0][0]==2,'literal scalar pivot')
                return [[f.add(p[i][j],f.neg(f.mul(f.mul(p[i][0],f.inv[2]),p[0][j]))) for j in (1,2)] for i in (1,2)]
            s=schur((1,0,1));t=schur((0,1,1));st=f.mm(s,t,2);ts=f.mm(t,s,2)
            counts[f.rank([[f.add(st[i][j],f.neg(ts[i][j])) for j in range(2)] for i in range(2)])]+=1
    got=c.headers(4,1,(0,1,1,1),'generic')
    need(checked==4032 and dict(counts)=={2:27},'all F4 literal scalar splits')
    need(got['sharp']==got['common']==4860 and str(got['sharp_probability'])=='3/112','F4 complete header count')
    return dict(split_pairs=checked,admissible_splits=27,sharp_headers=4860,total_headers=got['total'],probability='3/112')


def scalar_censuses(c):
    rows=[]
    for q,d,lam,kind,profile in ((3,2,2,'half',(2,3,3,2)),(5,2,2,'generic',(1,2,2,2)),
        (5,2,3,'half',(1,2,2,2)),(4,2,2,'generic',(1,2,2,2)),(8,2,2,'generic',(1,2,2,2))):
        f=Field(q);shift=f.add(f.add(lam,lam),f.neg(1));distinct=[0,lam]
        if shift not in distinct:distinct.append(shift)
        observed=Counter();common=sharp=0
        for h in matrices(d,d,q):
            ranks=[]
            for scalar in distinct:
                ranks.append(f.rank([[f.add(h[i][j],f.neg(scalar if i==j else 0)) for j in range(d)] for i in range(d)]))
            observed[tuple(d-r for r in ranks)]+=1
            all_splits,good_splits=c.fixed_product(q,d,profile,(ranks[distinct.index(shift)],ranks[1],ranks[1],ranks[0]))
            common+=all_splits;sharp+=good_splits
        need(dict(observed)=={k:v for k,v in c.joint_nullities(q,d,len(distinct)).items() if v},'scalar three-shift census')
        got=c.headers(q,d,profile,kind);completion=c.gl(q,sum(profile)-d)
        need((got['common'],got['sharp'])==(common*completion,sharp*completion),'scalar header weights')
        rows.append(dict(q=q,d=d,scalar=lam,pivot_class=kind,matrices=q**(d*d),common_splits=common,sharp_splits=sharp,sharp_probability=str(got['sharp_probability']),conditional_probability=str(got['conditional_probability'])))
    fixed=c.fixed_product(5,2,(1,2,2,2),(1,2,2,2))
    need(fixed==(442368000,442368000),'named F5 Jordan split count')
    named=c.headers(5,2,(1,2,2,2),'generic')
    need(named['sharp']==385*480**3*c.gl(5,5),'named F5 full profile count')
    return rows,dict(fixed_H_sharp_splits=fixed[1],fixed_H_sharp_headers=fixed[1]*c.gl(5,5),full_profile_sharp_splits=385*480**3,full_profile_sharp_headers=named['sharp'],full_profile_common_headers=named['common'],total_headers=named['total'],probability=str(named['sharp_probability']),conditional_probability=str(named['conditional_probability']))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write-result',action='store_true');args=ap.parse_args()
    for row in json.loads((P/'SOURCES.json').read_text())['files']:
        if row['usage']=='input':need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'source hash')
    c=load('counts',P/'counts.py')
    old=load('binary_source',ROOT/'research/schur-header-count/verify.py')
    domains=[];total=0
    for q,d in ((2,1),(2,2),(2,3),(3,1),(3,2),(3,3),(5,1),(5,2),(4,1),(4,2),(8,1),(8,2)):
        field=Field(q);observed=Counter()
        for h in matrices(d,d,q):
            w=[[field.add(int(i==j),field.neg(h[i][j])) for j in range(d)] for i in range(d)]
            observed[d-field.rank(h),d-field.rank(w)]+=1
        predicted=c.joint_nullities(q,d)
        need(dict(observed)=={k:v for k,v in predicted.items() if v},'complete joint-nullity census')
        domains.append(dict(q=q,d=d,matrices=sum(observed.values()),nonempty_strata=len(observed)))
        total+=sum(observed.values())
    factor_pairs=0;factor_targets=0
    for q,d,r in ((2,1,0),(2,1,1),(2,1,2),(2,2,2),(2,2,3),(3,1,2),(3,2,2),(4,1,2),(4,2,1)):
        field=Field(q);all_counts=Counter();full_counts=Counter()
        for x in matrices(d,r,q):
            for y in matrices(r,d,q):
                a=field.mm(x,y,d);key=tuple(map(tuple,a));all_counts[key]+=1;factor_pairs+=1
                if field.rank(x)==d and field.rank(y)==d:full_counts[key]+=1
        for a in matrices(d,d,q):
            key=tuple(map(tuple,a));rho=field.rank(a)
            need(all_counts[key]==c.unrestricted(q,r,d,rho),'unrestricted factor count')
            need(full_counts[key]==c.full_rank(q,r,d,rho),'full factor count')
            factor_targets+=1
    comparisons=[]
    for d,profile in ((1,(1,1,1,2)),(1,(0,2,2,1)),(2,(2,2,2,2)),(2,(1,3,3,2)),(3,(3,3,3,4))):
        got=c.headers(2,d,profile);want=old.predict(profile,d)
        need((got['sharp'],got['common'],got['total'])==(want['sharp_headers'],want['identity_headers'],want['total_headers']),'retained binary header law')
        comparisons.append(dict(d=d,profile=list(profile),sharp_probability=str(got['sharp_probability']),conditional_probability=str(got['conditional_probability'])))
    # Literal full headers use the predecessor's independent bit-matrix oracle.
    profile=(1,1,1,1);common=sharp=0
    for h in old.gl_headers(4):
        rank=old.inspect_header(h,profile,1)
        common+=rank is not None;sharp+=rank==2
    got=c.headers(2,1,profile)
    need((common,sharp)==(got['common'],got['sharp']),'all GL4 literal headers')
    large=[]
    for q,d in ((2,32),(4,16)):
        law=c.joint_nullities(q,d)
        need(law[d,0]==law[0,d]==1 and all(law[a,b]==law[b,a] for a,b in law),'large symmetry and unique endpoints')
        result=c.headers(q,d,(d,d,d,d))
        need(0<=result['sharp']<=result['common']<=result['total'],'large containment')
        large.append(dict(q=q,d=d,strata=len(law),matrix_space_bits=(q**(d*d)).bit_length(),sharp=fingerprint(result['sharp']),common=fingerprint(result['common']),total=fingerprint(result['total'])))
    need(c.joint_nullities(2,1).get((1,1),0)==0,'zero and one eigenspaces disjoint')
    need(c.headers(2,1,(1,0,0,0))['conditional_probability'] is None,'empty event has no conditional probability')
    need(c.headers(3,1,(1,1,1,1))['sharp']==16*c.gl(3,3),'odd-field scalar H2 count')
    need(c.headers(2,1,(0,2,2,1))['sharp']==181440,'unrestricted00 boundary')
    scalar_rows,named=scalar_censuses(c)
    literal_scalar=literal_f4_splits(c)
    generic=c.headers(4,12,(12,12,12,12),'generic')
    need(0<generic['sharp']<=generic['common']<=generic['total'],'large generic containment')
    generic_large=dict(q=4,d=12,strata=len(c.joint_nullities(4,12,3)),sharp=fingerprint(generic['sharp']),common=fingerprint(generic['common']),total=fingerprint(generic['total']))
    result=dict(status='PASS_SCALAR_PIVOT_HEADER_COUNTS',scalar_censuses=scalar_rows,named_F5=named,literal_F4=literal_scalar,generic_large=generic_large,domains=domains,matrices=total,factor_pairs=factor_pairs,factor_targets=factor_targets,binary_comparisons=comparisons,literal_headers=c.gl(2,4),large=large,controls=4,counts_sha256=hashlib.sha256((P/'counts.py').read_bytes()).hexdigest())
    if args.write_result:(P/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(json.dumps(result,sort_keys=True)==json.dumps(json.loads((P/'RESULT.json').read_text()),sort_keys=True),'typed complete receipt')
    print(json.dumps({k:result[k] for k in ('status','matrices','factor_pairs','factor_targets','literal_headers','controls')}))


if __name__=='__main__':main()

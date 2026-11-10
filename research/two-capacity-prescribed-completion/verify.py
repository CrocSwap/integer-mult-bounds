#!/usr/bin/env python3
"""Exact RREF criterion for two nonnested prescribed-map capacities.

The finite census normalizes h to identity on the first r basis vectors.
Independent domain/codomain basis changes justify this normalization in PROOF.
No predecessor or independent-oracle executable is imported or executed.
New work: ToikY with OpenAI Codex assistance; predecessor credit retained.
"""
import argparse
import hashlib
from itertools import product
import json
import math
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
MANIFEST_SHA='1d8841030f20e596c24aa8aace249e7ef744d14ba60e745a6b7668c8166df3c0'
PINS={
 'inputs/README-6489.md':(8094,'87b6addb51d5d521e2e098e5ae41d76001541cc7b16858038e41bef700ff15ce','9baf5b33e7362565cee3e7a5c38ba9d9116b9645'),
 'inputs/PROOF-6489.md':(6107,'35534ff37cbc97ae182baf5972a7a9d1ddb79a5dab38bea4ddf88b7e15ebc6ad','5416883d22271b525674ed8e4458acff4139117a'),
}
OBLIGATIONS=('source_A_compatibility','source_B_compatibility','source_sum_compatibility',
             'quotient_A_capacity','quotient_B_capacity','quotient_sum_capacity','coupled_kernel_capacity')


def require(ok,message):
    if not ok:raise ValueError(message)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)


def decode(raw):
    def unique(items):
        out={}
        for key,value in items:
            require(key not in out,'duplicate JSON key');out[key]=value
        return out
    def bad(value):raise ValueError('nonfinite JSON: '+value)
    def floating(value):
        out=float(value);require(math.isfinite(out),'nonfinite JSON number');return out
    return json.loads(raw,object_pairs_hook=unique,parse_constant=bad,parse_float=floating)


def read(path):
    with path.open('rb') as handle:raw=handle.read(1024*1024+1)
    require(len(raw)<=1024*1024,'one-MiB input capacity');return raw


def authenticate():
    manifest=read(ROOT/'SOURCE-PINS.json')
    require(hashlib.sha256(manifest).hexdigest()==MANIFEST_SHA,'source manifest SHA256')
    hashes={}
    for path,(size,sha,blob) in PINS.items():
        raw=read(ROOT/path);require(len(raw)==size,'source length: '+path)
        require(hashlib.sha256(raw).hexdigest()==sha,'source SHA256: '+path)
        framed=b'blob '+str(size).encode()+b'\0'+raw
        require(hashlib.sha1(framed).hexdigest()==blob,'source Git blob: '+path)
        raw.decode('utf-8');hashes[path]=sha
    return hashes


def vector(code,q,n):
    return tuple((code//q**i)%q for i in range(n))


def rref(rows,q,n):
    require(type(q) is int and q in (2,3,5),'supported prime field')
    require(type(n) is int and 0<=n<=4 and q**n<=27,'bounded ambient dimension')
    require(all(len(row)==n and all(type(x) is int and 0<=x<q for x in row) for row in rows),'canonical field coordinates')
    work=[list(row) for row in rows];pivot=0
    for column in range(n):
        choice=next((j for j in range(pivot,len(work)) if work[j][column]),None)
        if choice is None:continue
        work[pivot],work[choice]=work[choice],work[pivot]
        inverse=pow(work[pivot][column],q-2,q)
        work[pivot]=[x*inverse%q for x in work[pivot]]
        for j in range(len(work)):
            if j!=pivot:
                coefficient=work[j][column]
                work[j]=[(x-coefficient*y)%q for x,y in zip(work[j],work[pivot])]
        pivot+=1
        if pivot==len(work):break
    return tuple(tuple(row) for row in work[:pivot])


def orthogonal(basis,q,n):
    pivots=[next(i for i,x in enumerate(row) if x) for row in basis]
    out=[]
    for free in range(n):
        if free in pivots:continue
        row=[0]*n;row[free]=1
        for p,b in zip(pivots,basis):row[p]=-b[free]%q
        out.append(tuple(row))
    return rref(out,q,n)


def space_mask(basis,q,n):
    mask=0
    for coefficients in product(range(q),repeat=len(basis)):
        value=[sum(c*row[j] for c,row in zip(coefficients,basis))%q for j in range(n)]
        code=sum(x*q**i for i,x in enumerate(value));mask|=1<<code
    return mask


def prepare(q,n):
    rref((),q,n)
    all_vectors=[vector(code,q,n) for code in range(q**n)]
    seen={()};frontier={()}
    for _ in range(n):
        following=set()
        for basis in frontier:
            for v in all_vectors:
                child=rref(basis+(v,),q,n)
                if child not in seen:seen.add(child);following.add(child)
        frontier=following
    require(len(seen)<=80,'subspace capacity')
    bases=sorted(seen,key=lambda basis:space_mask(basis,q,n));index={basis:i for i,basis in enumerate(bases)}
    join=[[index[rref(a+b,q,n)] for b in bases] for a in bases]
    dual=[index[orthogonal(basis,q,n)] for basis in bases]
    meet=[[dual[join[dual[i]][dual[j]]] for j in range(len(bases))] for i in range(len(bases))]
    standard=[index[tuple(tuple(int(i==j) for j in range(n)) for i in range(rank))] for rank in range(n+1)]
    return {'q':q,'n':n,'bases':bases,'index':index,'join':join,'meet':meet,
            'dim':list(map(len,bases)),'masks':[space_mask(b,q,n) for b in bases],'standard':standard}


def flags(table,U,A,B,C,D):
    join,meet,dim=table['join'],table['meet'],table['dim']
    UA,UB=meet[U][A],meet[U][B];S=join[A][B];U0=meet[U][S]
    EC,ED=meet[U][C],meet[U][D];CD=join[C][D];I=meet[A][B];CI=meet[C][D]
    Z=join[EC][ED];X=meet[U0][Z]
    a,b,s=dim[A]-dim[UA],dim[B]-dim[UB],dim[S]-dim[U0]
    c,d,t=dim[C]-dim[EC],dim[D]-dim[ED],dim[CD]-dim[meet[U][CD]]
    k=dim[I]+dim[X]-dim[UA]-dim[UB]
    w=dim[CI]-dim[meet[U][CI]]
    conditions=(meet[UA][C]==UA,meet[UB][D]==UB,meet[U0][CD]==U0,a<=c,b<=d,s<=t,k<=w)
    return conditions,{'a':a,'b':b,'s':s,'c':c,'d':d,'t':t,'j':a+b-s,
                       'T':c+d-t,'k':k,'H':w,'ordinary_intersection_quotient':dim[I]-dim[meet[U][I]]}


def census(table,controls):
    q,n=table['q'],table['n'];m=len(table['bases']);ranks=[];whole=hashlib.sha256();total=0;feasible=0
    for rank,U in enumerate(table['standard']):
        transcript=bytearray();passing=0
        for A,B,C,D in product(range(m),repeat=4):
            conditions,_=flags(table,U,A,B,C,D)
            accepted=all(conditions);transcript.append(int(accepted));passing+=accepted
            if not accepted and conditions.count(False)==1:
                which=conditions.index(False)
                if which not in controls:
                    controls[which]={'q':q,'n':n,'rank':rank,'indices':[U,A,B,C,D],
                                     'masks':[table['masks'][x] for x in (U,A,B,C,D)]}
        count=len(transcript);whole.update(transcript);total+=count;feasible+=passing
        ranks.append({'rank':rank,'cases':count,'feasible':passing,'feasibility_sha256':hashlib.sha256(transcript).hexdigest()})
    return {'q':q,'n':n,'subspace_masks':table['masks'],'ranks':ranks,
            'cases':total,'feasible':feasible,'feasibility_sha256':whole.hexdigest()}


def all_gl(q,n):
    vectors=[vector(code,q,n) for code in range(q**n)]
    matrices=[]
    for columns in product(vectors,repeat=n):
        if len(rref(columns,q,n))==n:matrices.append(columns)
    return matrices


def apply(columns,v,q):
    return tuple(sum(v[j]*columns[j][i] for j in range(len(v)))%q for i in range(len(v)))


def included_image(columns,basis,target,q,n):
    return all(rref(target+(apply(columns,v,q),),q,n)==target for v in basis)


def gl_counts(table,indices,matrices):
    q,n=table['q'],table['n'];U,A,B,C,D=[table['bases'][i] for i in indices]
    total=one=two=both=0;witness=None
    for columns in matrices:
        if not all(apply(columns,v,q)==v for v in U):continue
        total+=1
        first=included_image(columns,A,C,q,n);second=included_image(columns,B,D,q,n)
        one+=first;two+=second;both+=first and second
        if first and second and witness is None:witness=[list(v) for v in columns]
    return {'prescribed_extensions':total,'individual_A':one,'individual_B':two,'joint':both,'witness_columns':witness}


def named_fixtures(tables,groups):
    out=[]
    for q in (2,3):
        table=tables.setdefault((q,3),prepare(q,3));basis=lambda codes:rref(tuple(vector(x,q,3) for x in codes),q,3)
        specs=[[1,q],[1+q*q],[q*q],[1,q*q],[1,q+q*q]]
        indices=[table['index'][basis(codes)] for codes in specs]
        conditions,data=flags(table,*indices)
        group=groups.setdefault((q,3),all_gl(q,3));counts=gl_counts(table,indices,group)
        require(conditions[:-1]==(True,)*6 and not conditions[-1] and data['j']<=data['T'] and data['ordinary_intersection_quotient']<=data['H'],'genuine oblique coupled obstruction')
        require(counts['joint']==0 and counts['individual_A']>0 and counts['individual_B']>0,'direct GL obstruction counts')
        out.append({'name':'oblique-three-dimensional','q':q,'n':3,'masks':[table['masks'][x] for x in indices],'flags':list(conditions),'invariants':data,'counts':counts})
        table=tables[(q,2)];basis2=lambda codes:rref(tuple(vector(x,q,2) for x in codes),q,2)
        specs=[[1+(q-1)*q],[1],[q],[1],[q]]
        indices=[table['index'][basis2(codes)] for codes in specs]
        conditions,data=flags(table,*indices);counts=gl_counts(table,indices,groups.setdefault((q,2),all_gl(q,2)))
        require(all(conditions) and data['j']>data['H'] and data['k']==0 and counts['joint']>0,'nonzero-delta feasible control')
        out.append({'name':'nonzero-delta-two-dimensional','q':q,'n':2,'masks':[table['masks'][x] for x in indices],'flags':list(conditions),'invariants':data,'counts':counts})
    return out


def omission_controls(found,tables,groups):
    require(set(found)==set(range(7)),'all seven omission controls found')
    out=[]
    for which,record in sorted(found.items()):
        key=(record['q'],record['n']);table=tables[key]
        conditions,data=flags(table,*record['indices'])
        require(not conditions[which] and all(value for j,value in enumerate(conditions) if j!=which),'actual one-condition omission false positive')
        counts=gl_counts(table,record['indices'],groups.setdefault(key,all_gl(*key)))
        require(counts['joint']==0,'GL rejects omitted-condition false positive')
        out.append({'omitted':OBLIGATIONS[which],**record,'flags':list(conditions),'invariants':data,'GL_counts':counts})
    return out


def invalid_controls():
    out={}
    for name,callback in [('boolean_dimension',lambda:prepare(2,True)),('nonprime_field',lambda:prepare(4,2)),
                          ('invalid_coordinate',lambda:rref(((True,0),),2,2)),
                          ('duplicate_JSON',lambda:decode('{"x":1,"x":2}')),('nonfinite_JSON',lambda:decode('{"x":1e999}'))]:
        try:callback()
        except ValueError as error:out[name]=str(error)
        else:raise ValueError('invalid input accepted: '+name)
    return out


def compute():
    source_hashes=authenticate();tables={};groups={};found={};domains=[]
    for q,n in [(2,0),(2,1),(2,2),(2,3),(3,2),(5,2)]:
        table=prepare(q,n);tables[q,n]=table;domains.append(census(table,found))
    controls=omission_controls(found,tables,groups)
    fixtures=named_fixtures(tables,groups)
    return {'schema_version':1,'source_manifest_sha256':MANIFEST_SHA,'source_sha256':source_hashes,
            'method':'RREF joins,orthogonal-nullspace meets and seven exact rank/compatibility tests; normalized prescribed injection',
            'domains':domains,'total_cases':sum(row['cases'] for row in domains),
            'total_feasible':sum(row['feasible'] for row in domains),
            'omission_controls':controls,'named_fixtures':fixtures,'invalid_controls':invalid_controls(),
            'software_scope':'Prime fields2,3,5; n<=4 and q^n<=27; census domains explicitly listed. h identity on standard rank-r subspace in census; independent basis normalization covers all prescribed injections up to coordinates.',
            'limits':['All-field feasibility relies on the written exact-sequence/lift/gluing proof,not finite extrapolation.',
                      'No universal constructor software or general finite-field completion-count formula claimed.',
                      'Unrestricted GL interface only; no native/symplectic/phase/causal/cost/physical admission,kappa or selected-frontier change.']}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--emit',action='store_true');args=parser.parse_args()
    result=compute()
    if args.emit:print(canonical(result))
    else:
        require(canonical(decode(read(ROOT/'RESULT.json')))==canonical(result),'strict complete RESULT receipt drift')
        print('PASS_TWO_NONNESTED_PRESCRIBED_CAPACITY_CRITERION')


if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,TypeError,OSError) as error:
        print('FAIL: '+str(error),file=sys.stderr);sys.exit(1)

#!/usr/bin/env python3
"""Finite controls for PROOF.md; @CubeJerry with substantial OpenAI assistance.
Apache-2.0. Standard library only. All-width quantifiers use the written proof.
"""
from collections import Counter, defaultdict
from itertools import combinations
import argparse, hashlib, json
from pathlib import Path
class VerificationError(Exception): pass
def need(ok, message):
    if not ok: raise VerificationError(message)
def span(vectors):
    values={0}
    for v in vectors: values|={w^v for w in tuple(values)}
    return values
def rank(vectors):
    basis={}
    for v in vectors:
        while v:
            p=v.bit_length()-1
            if p not in basis:
                basis[p]=v; break
            v^=basis[p]
    return len(basis)
def matrix(x,y,n): return tuple(y if x>>i&1 else 0 for i in range(n))
def packed(rows): return sum(row<<(len(rows)*i) for i,row in enumerate(rows))
def pattern(x,y,n): return packed(matrix(x,y,n))&~sum(1<<(n*i+i) for i in range(n))
def multiply(a,b):
    out=[]
    for row in a:
        v=0
        for j,other in enumerate(b):
            if row>>j&1: v^=other
        out.append(v)
    return tuple(out)
def catalogue(n):
    out=defaultdict(list); count=0
    for x in range(1,1<<n):
        for y in range(1,1<<n):
            if (x&y).bit_count()%2:
                count+=1; p=pattern(x,y,n)
                if p: out[p].append((x,y))
    need(count==((1<<n)-1)*(1<<(n-1)), 'catalogue count')
    need(all(len(v)==(2 if p.bit_count()==1 else 1) for p,v in out.items()), 'fiber control')
    return dict(out),count
def pool(ps,by): return sorted(pair for p in ps if p for pair in by.get(p,[]))
def invariant(vectors,ps):
    vs=set(vectors)
    return all((x if (y&v).bit_count()%2 else 0) in vs for x,y in ps for v in vs)
def cyclic(start,ps):
    vs={0,start}
    while True:
        added={x for x,y in ps if any((y&v).bit_count()%2 for v in vs)}
        new=span(list(vs)+list(added))
        if new==vs: return vs
        vs=new
def irreducible(n,ps): return all(len(cyclic(v,ps))==1<<n for v in range(1,1<<n))
def reject(fn,name):
    try: fn()
    except VerificationError: return name
    raise VerificationError('negative control accepted: '+name)
def validate(doc):
    need(type(doc.get('width')) is int and doc['width']==5,'width')
    ps=doc.get('projectors'); need(type(ps) is list and len(ps)==5,'pool size')
    for pair in ps:
        need(type(pair) is list and len(pair)==2,'pair encoding')
        x,y=pair
        need(type(x) is type(y) is int and 0<x<32 and 0<y<32,'mask')
        need((x&y).bit_count()%2,'idempotence')
    ps=sorted(map(tuple,ps)); need(len(set(ps))==5,'duplicate')
    plane=span(pattern(x,y,5) for x,y in ps)
    need(len(plane)==8,'pattern dimension')
    need(sum(p.bit_count()==1 for p in plane)==2,'two edges')
    by,count=catalogue(5); need(pool(plane,by)==ps,'complete pool')
    need(rank(x for x,y in ps)==5 and rank(y for x,y in ps)==5,'image/covector dimension')
    need(irreducible(5,ps),'cyclic-space irreducibility')
    return ps,count
def witness_controls(doc):
    ps,count=validate(doc); s=(3,2,12,8,16); identity=tuple(1<<i for i in range(5))
    need(multiply(s,s)==identity,'shear involution')
    actual={multiply(multiply(s,matrix(x,y,5)),s) for x,y in ps}
    expected={matrix(1<<i,1<<i,5) for i in range(4)}|{(31,)*5}
    need(actual==expected,'exact normal form')
    spaces=set()
    for d in range(1,5):
        for basis in combinations(range(1,32),d):
            vs=span(basis)
            if len(vs)==1<<d: spaces.add(tuple(sorted(vs)))
    need(len(spaces)==372,'proper-subspace coverage')
    need(not any(invariant(vs,ps) for vs in spaces),'all-subspace irreducibility')
    controls=[]
    bad=dict(doc,projectors=doc['projectors'][:-1])
    controls.append(reject(lambda:validate(bad),'omitted bridge'))
    badps=[v[:] for v in doc['projectors']]; badps[-1][0]^=1
    controls.append(reject(lambda:validate(dict(doc,projectors=badps)),'nonidempotent bridge'))
    badps=[v[:] for v in doc['projectors']]; badps[-1][1]=20
    controls.append(reject(lambda:validate(dict(doc,projectors=badps)),'legal reducible bridge'))
    controls.append(reject(lambda:need(rank(x for x,y in ps)<=4,'false cap'),'false four-dimensional cap'))
    without=[v for v in ps if v!=(26,21)]
    need(rank(x for x,y in without)==4 and not irreducible(5,without),'bridge matters')
    by6,_=catalogue(6); six=pool(span([1<<1,1<<15,1<<29]),by6)
    need(len(six)==6 and rank(x for x,y in six)==6,'three-edge global image six')
    need(all(any((x|y)&b==(x|y) for b in (3,12,48)) for x,y in six),'separate two-dimensional blocks')
    controls.append(reject(lambda:need(rank(x for x,y in six)<=5,'false e3 cap'),'wrong total bound at three edges'))
    coord=[(127,127)]+[(1<<i,1<<i) for i in range(7)]
    need(irreducible(7,coord),'coordinate-call scope control')
    need(len(span(pattern(x,y,7) for x,y in coord))==2,'one-dimensional pattern control')
    return {'catalogue':count,'pool':[list(v) for v in ps],'proper_subspaces':372,'joint_image':5,
            'normal_form':True,'rejections':controls,'three_edge_image':6,'coordinate_scope_width':7}
def quotient_controls():
    reports=[]
    for n,inside in ((4,3),(5,3),(6,15)):
        by,_=catalogue(n)
        block=sum(1<<(n*i+j) for i in range(n) for j in range(n) if inside>>i&1 and inside>>j&1)
        groups=defaultdict(list)
        for p,vs in by.items():
            for x,y in vs: groups[p&~block].append((p,x,y))
        checked=exceptions=0
        for vs in groups.values():
            for (p,x,y),(q,u,v) in combinations(vs,2):
                checked+=1; xx=x&~inside; uu=u&~inside
                if not(xx and uu and xx!=uu): continue
                exceptions+=1; need(p==q and p.bit_count()==1,'exception is an edge')
                a,b=divmod(p.bit_length()-1,n)
                need(not(inside>>a&1) and not(inside>>b&1),'edge endpoints outside')
        need(exceptions>0,'nonvacuous exception')
        reports.append({'width':n,'inside':inside,'pairs':checked,'edge_exceptions':exceptions})
    return reports
def plane_controls():
    types={'opposite':((0,1),(1,0)),'same_source':((0,1),(0,2)),
           'same_target':((1,0),(2,0)),'path':((0,1),(1,2)),'disjoint':((0,1),(2,3))}
    reports=[]; irreducibles=[]
    for n in (4,5,6,7):
        by,_=catalogue(n)
        for kind,edges in types.items():
            p,q=[1<<(n*a+b) for a,b in edges]; p0={0,p,q,p^q}
            planes={tuple(sorted(p0|{r^v for v in p0})) for r in by if r not in p0}
            hist=Counter()
            for plane in planes:
                if sum(v.bit_count()==1 for v in plane)!=2: continue
                ps=pool(plane,by); dim=rank(x for x,y in ps)
                need(dim<=len({v for e in edges for v in e})+1,'joint-image theorem')
                hist[dim]+=1
                if n==5 and kind=='disjoint' and dim==5 and irreducible(n,ps): irreducibles.append(ps)
            reports.append({'width':n,'edge_type':kind,'generated_planes':len(planes),
                            'two_edge_image_histogram':sorted(hist.items())})
    need(irreducibles==[[(1,3),(3,2),(4,12),(12,8),(26,21)]],'unique irreducible fixed-edge width-five pool')
    return reports
def poly_mul(a,b):
    out=set()
    for x in a:
        for y in b: out.symmetric_difference_update((tuple(i+j for i,j in zip(x,y)),))
    return out
def word(calls):
    zero=(0,0,0); n=5
    out=[[{zero} if i==j else set() for j in range(n)] for i in range(n)]
    for a,x,y in calls:
        need(a!=zero and (x&y).bit_count()%2,'legal call')
        new=[[p.copy() for p in row] for row in out]
        for i in range(n):
            p=set()
            for k in range(n):
                if x>>k&1: p.symmetric_difference_update(out[i][k])
            delta=poly_mul(p,{zero,a})
            for j in range(n):
                if y>>j&1: new[i][j].symmetric_difference_update(delta)
        out=new
    return out
def formal_control():
    a,b,c=(1,0,0),(0,1,0),(0,0,1)
    calls=[(a,1,3),(a,3,2),(b,4,12),(b,12,8),(c,26,21),((0,0,-1),26,21)]
    targets=[a,a,b,b,(0,0,0)]
    expected=[[{targets[i]} if i==j else set() for j in range(5)] for i in range(5)]
    need(word(calls)==expected,'whole formal endpoint')
    need({a,b,c}<={v[0] for v in calls},'three free exponent generators')
    bad=word(calls[:-1]); need(any(bad[i][j] for i in range(5) for j in range(5) if i!=j),'cleanup omission')
    return {'calls':6,'exponent_span':3,'relation_rank':3,'endpoint':True,'cleanup_omission':True,
            'limitation':'No saving: the two bridge calls cancel.'}
def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--output',type=Path)
    args=parser.parse_args(); here=Path(__file__).resolve().parent
    origins=json.loads((here/'ORIGINS.json').read_text())
    for source in origins['files']:
        need(hashlib.sha256((here/source['path']).read_bytes()).hexdigest()==source['sha256'],'retained predecessor source hash')
    doc=json.loads((here/'WITNESS.json').read_text())
    result={'schema_version':1,'witness':witness_controls(doc),'quotient':quotient_controls(),
            'planes':plane_controls(),'formal':formal_control()}
    encoded=json.dumps(result,sort_keys=True,separators=(',',':')).encode()
    print('PASS_THREE_RELATION_TWO_EDGE_CORE',hashlib.sha256(encoded).hexdigest())
    print(json.dumps(result,sort_keys=True))
    if args.output: args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
if __name__=='__main__': main()

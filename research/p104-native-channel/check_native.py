"""Read-only native boundary proof: no compiler or producer imports.

Each literal transport is verified as a complete Clifford operator, including
its scalar phase. A separate frame-invariant scalar replay composes the full
channel, including source query formation. The side correction is outside it.
"""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations,product
from collections import Counter
import argparse,copy,gzip,hashlib,importlib.util,json
H=Path(__file__).resolve().parent
P=H/'inputs'
NP=H/'vendor/native_verify.py'
sp=importlib.util.spec_from_file_location('independent_gaussian',NP);N=importlib.util.module_from_spec(sp);sp.loader.exec_module(N)

def need(ok,why):
    if not ok:raise ValueError(why)

def roots():
    lines=set()
    for i,j in combinations(range(8),2):
        for sign in (-1,1):
            v=[0]*8;v[i]=2;v[j]=2*sign;lines.add(tuple(v))
    for signs in product((-1,1),repeat=7):
        if signs.count(-1)%2==0:lines.add((1,*signs))
    need(len(lines)==120,'independent E8 roots');return sorted(lines)

def span(vs):
    out={0}
    for v in vs:out|={x^v for x in tuple(out)}
    return tuple(sorted(out))

def validate(c,w,fixture,full_gaussian=False):
    rr=roots();inner=lambda a,b:sum(x*y for x,y in zip(a,b))//4
    binary=[sum(((inner(a,b)+1)&1)<<j for j,b in enumerate(rr))for a in rr]
    iso=c['label_isometry'];ix=iso['pivot_root_indices'];need(len(ix)==len(set(ix))==9,'nine distinct coordinate pivots')
    compressed=[sum(((row>>j)&1)<<k for k,j in enumerate(ix))for row in binary];gram=[compressed[i]for i in ix]
    need(list(gram)==iso['compressed_gram'],'compressed Gram binding');dual=list(N.inverse(tuple(gram)));need(dual==iso['compressed_dual_gram'],'dual Gram inverse')
    mv=lambda rows,x:sum(((row&x).bit_count()&1)<<i for i,row in enumerate(rows))
    dot=lambda a,b:(a&mv(dual,b)).bit_count()&1
    orth=iso['orthonormal_basis_compressed'];need(len(orth)==9 and all(dot(a,b)==int(i==j)for i,a in enumerate(orth)for j,b in enumerate(orth)),'orthonormal isometry')
    convert=lambda x:sum(dot(x,v)<<j for j,v in enumerate(orth));q=[convert(x)for x in compressed]
    need(q==iso['physical_root_labels']and len(set(q))==120,'physical label image')
    for i,a in enumerate(q):
        for j,b in enumerate(q):need(((a&b).bit_count()&1)==((binary[i]>>j)&1),'all 14400 physical binary pairings')
    labels=dict(zip(rr,q));pairs=[(tuple(a),tuple(b))for a,b in fixture['pairs_doubled_coordinates']];removed={tuple(r)for r in fixture['F0']+fixture['C']};ports=[r for r in rr if r not in removed]
    need(len(pairs)==8 and len(ports)==104,'P104 fixture binding')
    key=lambda f:span(convert(v)for v in f)
    charts={};edges={};covered={};paid=Counter();gaussian_columns=0
    def chart(f):
        k=span(f);need(len(k)==1<<len(f),'independent frame basis')
        if k in charts:need(charts[k]==tuple(f),'consistent chart basis per frame')
        else:charts[k]=tuple(f)
        return k
    for rec in c['transports']:
        a,b=tuple(rec['old']),tuple(rec['new']);ka,kb=chart(a),chart(b);need((ka,kb)not in edges,'unique transport edge');edges[ka,kb]=rec
        need(set(ka)<=set(kb)or set(kb)<=set(ka),'nested actual physical frames')
        rank=abs(len(a)-len(b));need(rank==rec['rank']==rec['recipe']['rank']and rank>0,'exact native jump rank')
        expected=N.adjoint(N.frame(a,9))+N.frame(b,9);N.equal(N.recipe(rec['recipe']),expected,'independent native boundary edge')
        if full_gaussian and len(a)==8 and len(b)==1:
            for j in range(512):need(N.state(N.recipe(rec['recipe']),j)==N.state(expected,j),'all private-copy basis columns');gaussian_columns+=1
        for i in rec['events']:
            need(i not in covered and 0<=i<len(w['program']),'transport occurrence coverage');e=w['program'][i]
            need(e[0]=='transport'and key(e[2])==ka and key(e[3])==kb and e[4]==rank,'literal transport binding');covered[i]=rec;paid[rank]+=1
    need(set(covered)=={i for i,e in enumerate(w['program'])if e[0]=='transport'},'every literal transport compiled')
    need(dict(sorted(paid.items()))=={int(k):v for k,v in c['paid_profile'].items()},'complete paid profile')
    adapters={}
    for rec in c['endpoint_adapters']:
        reg=rec['register'];f=tuple(rec['frame']);kf=chart(f);where=rec['position'];need((where,reg)not in adapters,'unique endpoint adapter');adapters[where,reg]=rec
        need(rec['recipe']['rank']==0,'monomial endpoint')
        if where=='entry':
            k=int(reg[1:]);normal=labels[ports[k]];need(reg=='X'+str(k)and key(w['initial_frames'][reg])==kf and f==(normal,),'source entry singleton')
            expected=N.adjoint((('C',normal,1),))+N.frame(f,9)
        else:
            need(where=='exit'and reg.startswith('Y'),'target exit kind');normal=labels[ports[int(reg[1:])]];need(key(w['final_frames'][reg])==kf,'target exit frame')
            expected=N.adjoint(N.frame(f,9))+(('C',normal,-1),)+N.fourier(9)
        need(normal==rec['normal'],'physical root binding')
        if where=='exit':need(all(not((v&normal).bit_count()&1)for v in f),'physical root hyperplane')
        N.equal(N.recipe(rec['recipe']),expected,'independent intrinsic endpoint')
    need(set(adapters)=={('entry','X'+str(k))for k in range(104)}|{('exit','Y'+str(t))for t in range(104)},'208 intrinsic endpoints')
    # Canonical row replay is the induction invariant: physical value of r
    # equals chart(current frame) applied to this exact linear combination.
    names=list(w['initial_frames']);state={name:{name:Q(1)}for name in names};frames={name:key(f)for name,f in w['initial_frames'].items()};scalar=Counter()
    for i,e in enumerate(w['program']):
        op=e[0]
        if op=='transport':
            _,reg,old,new,rank=e;need(frames[reg]==key(old),'native entry invariant');frames[reg]=key(new)
        elif op=='zero':
            _,reg,f=e;need(reg=='C'and reg not in frames,'owned private initialization');state[reg]={};frames[reg]=key(f);scalar[op]+=1
        elif op=='erase':
            _,reg,f=e;need(reg=='C'and frames[reg]==key(f),'owned private erasure');state.pop(reg);frames.pop(reg);scalar[op]+=1
        elif op=='copy':
            _,reg,src,f=e;need(not state[reg]and frames[reg]==frames[src]==key(f),'common-chart copy');state[reg]=dict(state[src]);scalar[op]+=1
        else:
            need(op=='add','literal scalar type');_,reg,src,a,f=e;need(reg!=src and frames[reg]==frames[src]==key(f),'common-chart scalar induction')
            for name,v in list(state[src].items()):
                z=state[reg].get(name,Q(0))+Q(a)*v
                if z:state[reg][name]=z
                else:state[reg].pop(name,None)
            scalar[op]+=1
    need(set(state)==set(frames)==set(names),'all private storage closed')
    for name in names:
        expected={name:Q(1)}
        if name.startswith('Y'):
            t=int(name[1:]);expected.update({'X'+str(k):Q(inner(ports[t],a),2)for k,a in enumerate(ports)if inner(ports[t],a)})
        need(state[name]==expected and frames[name]==key(w['final_frames'][name]),'full physical boundary endpoint '+name)
    return dict(transports=len(edges),intrinsic_endpoint_adapters=len(adapters),formal_boundary_columns=len(names),paid_profile=dict(sorted(paid.items())),rank_mass=sum(k*v for k,v in paid.items()),scalar_events=dict(scalar),all_private_copy_gaussian_columns=gaussian_columns,all_physical_pairings=14400)

def replay(full_gaussian=True):
    packed=(H/'NATIVE-RECIPES.json.gz').read_bytes();raw=gzip.decompress(packed);c=json.loads(raw);wr=(P/'LOWRANK-WITNESS.json').read_bytes();need(hashlib.sha256(wr).hexdigest()==c['source_witness_sha256'],'frozen witness hash');need(hashlib.sha256(NP.read_bytes()).hexdigest()==c['source_native_checker_sha256'],'independent native checker pin')
    w=json.loads(wr);fixture=json.loads((P/'P104-FIXTURE.json').read_text())['section4_explicit_P104'];r=validate(c,w,fixture,full_gaussian)
    controls={}
    bad=copy.deepcopy(c);bad['transports'][0]['recipe']['left']['phase']=(bad['transports'][0]['recipe']['left']['phase']+1)%4
    try:validate(bad,w,fixture)
    except ValueError:controls['global_phase']=True
    else:raise ValueError('accepted wrong native global phase')
    bad=copy.deepcopy(c);bad['transports'].pop()
    try:validate(bad,w,fixture)
    except ValueError:controls['missing_transport']=True
    else:raise ValueError('accepted missing native edge')
    bad=copy.deepcopy(c);bad['label_isometry']['physical_root_labels'][0]^=1
    try:validate(bad,w,fixture)
    except ValueError:controls['physical_label']=True
    else:raise ValueError('accepted wrong physical label')
    for name,i in [('missing_initial_query_compensation',0),('missing_final_query_cleanup',len(w['program'])-1)]:
        bad=copy.deepcopy(w);need(bad['program'][i][0]=='add','semantic control is scalar addition');bad['program'][i][3]='0'
        try:validate(c,bad,fixture)
        except ValueError:controls[name]=True
        else:raise ValueError('accepted '+name)
    r.update(status='PASS_CONCRETE_NATIVE_P104_LOW_RANK_CHANNEL',recipes_raw_sha256=hashlib.sha256(raw).hexdigest(),source_witness_sha256=hashlib.sha256(wr).hexdigest(),controls=controls,scope='Concrete finite Clifford primitives plus a complete framed induction over all 280 arbitrary channel inputs, source gathering and 72 dirty helper restorations. No I-G/2 side correction, global helper assignment, precision, all-size admission or new kappa.')
    return r

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path);ap.add_argument('--all-copy-columns',action='store_true');args=ap.parse_args()
    out=json.dumps(replay(args.all_copy_columns),sort_keys=True,indent=2)+'\n'
    if args.out:
        with args.out.open('x')as f:f.write(out)
    print(out,end='')

if __name__=='__main__':main()

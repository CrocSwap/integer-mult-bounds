"""Independent source/energy/flow audit for the scalar-combined least-frame fusion, with an explicit boundary mode.

No imports from the proposal builder, source graph, interval engine, or search.
Reconstructs chronological nodes using 9-bit point sets, computes each cost as
subspace symmetric-difference dimension, and verifies the supplied residual as
a feasible flow. Capacity signs use separate exact rational Taylor bounds.
"""
from pathlib import Path
from collections import Counter, defaultdict
from functools import lru_cache
from fractions import Fraction as Q
import argparse, copy, gzip, hashlib, json, time

SOURCE_SHA256='aa4a8241da76abd2c06e6576a3ac09e77781321deaac3ad7d3ce4519342a36e6'
ZERO=(0,)*10

def need(ok,msg):
    if not ok: raise ValueError(msg)

def sha(b): return hashlib.sha256(b).hexdigest()
def add(a,b):return tuple(x+y for x,y in zip(a,b))
def scale(a,k):return tuple(x*k for x in a)
def sub(a,b):return add(a,scale(b,-1))
def atom(r,k=1):return tuple(k if i==r and r else 0 for i in range(10))

def span(vectors):
    s={0}
    for v in vectors:s|={x^v for x in tuple(s)}
    return frozenset(s)

def dim(s):
    need(len(s)>0 and not len(s)&(len(s)-1),'binary subspace cardinality')
    return len(s).bit_length()-1

@lru_cache(None)
def base(s):
    b=[];covered=frozenset({0})
    for v in sorted(s):
        if v not in covered:b.append(v);covered=span(b)
    need(covered==s,'binary subspace closure')
    return tuple(b)

@lru_cache(None)
def join(a,b):return span(base(a)+base(b))

def mv(g,x):
    result=0
    for i,col in enumerate(g):
        if x>>i&1:result^=col
    return result

@lru_cache(None)
def image(g,s):return frozenset(mv(g,x) for x in s)

def inverse(g):
    lookup={mv(g,x):x for x in range(512)}
    need(len(lookup)==512,'native map invertible')
    return tuple(lookup[1<<i] for i in range(9))

def distance(a,b):return dim(a)+dim(b)-2*dim(a&b)

def helper_lower(payload):
    """Independent exact carried DAG with physical adapter pin pullbacks.

    Demand nodes are not the uncontracted cost nodes. A current demand carries
    its complete native map, so a frozen adapter pins G^{-1}(its actual frame),
    rather than assuming no warp occurred since the demand was introduced.
    """
    c=payload['canonical'];frames=list(map(span,c['frames']))
    eye=tuple(1<<i for i in range(9))
    maps={w['op']:tuple(w['G_columns']) for w in c['warps']}
    maps.update({-op:inverse(g) for op,g in list(maps.items())})
    original=[];parents=[];fixed={};contacts={};adapter_nodes=set();mapped_adapters=0
    def node(value,pin=False):
        i=len(original);original.append(value);parents.append([])
        if pin:fixed[i]=value
        return i
    current=[(node(frames[f],r<224),eye) for r,f in enumerate(c['start'])]
    physical=[frames[f] for f in c['start']]
    for index,e in enumerate(payload['programs']['forward']):
        kind=e[0]
        if kind=='climb':physical[e[2]]=frames[e[4]]
        elif kind=='warp':
            r,op=e[1][1],e[2];i,g=current[r]
            current[r]=(i,tuple(mv(maps[op],v) for v in g));physical[r]=frames[e[4]]
        elif kind=='scalar':
            gate,f=e[1:];refs=gate[1:3] if gate[0] in ('add','copy') else gate[1:2]
            live=[r for typ,r in refs if typ=='L']
            if not live or gate[0]=='scale':continue
            i=node(frames[f],len(live)<len(refs));contacts[index]=i
            for r in live:
                parents[i].append(current[r]);current[r]=(i,eye)
                need(physical[r]==frames[f],'actual source scalar frame')
        elif kind=='adapter':
            r=e[2];i,g=current[r];required=image(inverse(g),physical[r])
            if g!=eye:mapped_adapters+=1
            need(required==original[i],'adapter demand pullback agrees with actual source node')
            need(i not in fixed or fixed[i]==required,'consistent adapter pin')
            fixed[i]=required;adapter_nodes.add(i)
    final=[]
    for r,f in enumerate(c['final']):
        i=node(frames[f],r<224);parents[i].append(current[r]);final.append(i)
    def lower():
        result=[]
        for i,incoming in enumerate(parents):
            value=frozenset({0})
            for a,g in incoming:value=join(value,image(g,result[a]))
            if i in fixed:
                need(value<=fixed[i],'fixed demand lower containment');value=fixed[i]
            result.append(value)
        return result
    values=lower();repins=[]
    for r in range(224,632):
        if distance(values[r],values[final[r]])==0:
            repins.append(r);fixed[final[r]]=original[final[r]]
    values=lower()
    return {'start':values[:632],'final':[values[i] for i in final],
            'contacts':{index:values[i] for index,i in contacts.items()},
            'adapter_demand_nodes_pinned':len(adapter_nodes),'adapter_pins_after_nonidentity_map':mapped_adapters,
            'retained_helper_exit_pins':repins,'demand_nodes':len(values)}

def source_graph(payload,proof_mode):
    target=helper_lower(payload) if proof_mode=='joint-helper' else None
    c=payload['canonical'];frames=list(map(span,c['frames']))
    maps={w['op']:tuple(w['G_columns']) for w in c['warps']}
    maps.update({-op:inverse(g) for op,g in list(maps.items())})
    old=[];low=[];edges=[];fixed=set()
    def node(a,b,freeze=False):
        i=len(old);old.append(a);low.append(b)
        if freeze:fixed.add(i)
        return i
    current=[node(frames[f],target['start'][r] if target else frames[f],r<224) for r,f in enumerate(c['start'])]
    initial=current[:]
    centers=Counter();climbs=Counter()
    for event_index,e in enumerate(payload['programs']['forward']):
        kind=e[0]
        if kind=='scalar':
            gate,f=e[1:];refs=gate[1:3] if gate[0] in ('add','copy') else gate[1:2]
            lives=[r for typ,r in refs if typ=='L'];owned=len(lives)<len(refs)
            least=frames[f] if owned else frozenset({0})
            if not owned:
                for r in lives:least=join(least,low[current[r]])
            if target and lives and gate[0]!='scale':least=target['contacts'][event_index]
            n=node(frames[f],least,owned)
            for r in lives:
                need(old[current[r]]<=frames[f],'source scalar climb nesting')
                edges.append((current[r],n,0,1));current[r]=n
        elif kind=='warp':
            _,role,op,a,b=e;need(role[0]=='L','persistent warp')
            r=role[1];before=current[r]
            need(old[before]<=frames[a],'source pre-warp nesting')
            n=node(frames[a],low[before]);edges.append((before,n,0,1))
            after=node(frames[b],image(maps[op],low[before]))
            need(image(maps[op],frames[a])==frames[b],'native source frame image')
            edges.append((n,after,op,1));current[r]=after
        elif kind=='adapter':fixed.add(current[e[2]])
        elif kind=='climb':climbs[e[5]]+=1
        elif kind=='center':centers[e[4]]+=1
        else:need(kind=='phase','known event type')
    final=[]
    for r,f in enumerate(c['final']):
        n=node(frames[f],target['final'][r] if target else frames[f],r<224);final.append(n)
        need(old[current[r]]<=frames[f] and low[current[r]]<=low[n],'final nesting')
        edges.append((current[r],n,0,1))
    for r in range(224,632):edges.append((initial[r],final[r],0,-1))
    # Adapter nodes are restored to original charts after least-frame generation.
    if target:need(all(old[i]==low[i] for i in fixed),'every physical frozen chart unchanged')
    return old,low,edges,fixed,maps,centers,climbs,initial,final,target

def chart_is_canonical(chart,s):
    need(len(chart)==9 and all(type(v)is int and 0<v<262144 for v in chart),'full chart rows')
    need(len(span(chart))==512,'full chart rank')
    need(span(v&511 for v in chart)==s,'chart projected space')
    for v in chart:
        x,z=v&511,v>>9
        need(x in s and all(((x^z)&u).bit_count()%2==0 for u in base(s)),'canonical zero-phase chart')

def reconstruct_energy(witness,payload,proof_mode):
    old,low,edges,fixed,maps,centers,climbs,initial,final,target=source_graph(payload,proof_mode)
    proposals={int(i):chart for i,chart in witness['proposals'].items()}
    expected={i for i in range(len(old)) if old[i]!=low[i] and i not in fixed}
    need(set(proposals)==expected,'all and only distinct eligible least-frame proposals')
    need(len(expected)==(1079 if target else 896),'declared variable inventory')
    for i,chart in proposals.items():chart_is_canonical(chart,low[i])
    if not target:need(not expected.intersection(initial+final),'all helper and main endpoints fixed')
    else:
        need(witness['binding']['combined_word_payload_sha256']==SOURCE_SHA256,'helper witness source binding')
        need(witness['retained_helper_exit_pins']==target['retained_helper_exit_pins'],'independent helper exit repins')
        need(witness['adapter_demand_nodes_pinned']==target['adapter_demand_nodes_pinned'],'independent adapter pin inventory')
    tables=[];paid=Counter(centers);lower_paid=Counter(centers);helpers=Counter();new_helpers=Counter()
    linear=defaultdict(lambda:ZERO);pair=defaultdict(lambda:ZERO)
    zero_changed=0;warps_changed=0
    for a,b,op,sign in edges:
        if a==b and not op:continue
        left=[old[a],low[a] if a in expected else old[a]]
        right=[old[b],low[b] if b in expected else old[b]]
        if op:left=[image(maps[op],s) for s in left]
        ranks=[distance(left[i],right[j]) for i,j in [(0,0),(1,0),(0,1),(1,1)]]
        need(min(ranks)>=0 and max(ranks)<=9,'physical rank range')
        if sign<0:
            need(min(ranks)>0,'all helper states strictly productive');helpers[ranks[0]]+=1;new_helpers[ranks[3]]+=1
        else:
            if ranks[0]:paid[ranks[0]]+=1
            if ranks[3]:lower_paid[ranks[3]]+=1
        if a not in expected and b not in expected:continue
        tables.append([a,b,op,sign,ranks])
        if sign>0 and not ranks[0]:zero_changed+=1
        if op:warps_changed+=1
        v00,v10,v01,v11=[atom(r,sign) for r in ranks]
        if a==b:
            linear[a]=add(linear[a],sub(v11,v00))
        else:
            if a in expected:linear[a]=add(linear[a],sub(v10,v00))
            if b in expected:linear[b]=add(linear[b],sub(v01,v00))
            if a in expected and b in expected:
                key=tuple(sorted((a,b)));pair[key]=add(pair[key],sub(sub(v11,v10),sub(v01,v00)))
    need(tables==witness['tables'],'every ordered four-state rank table from raw events')
    need(paid==climbs+centers,'entire source paid multiset')
    need(paid==Counter({int(k):v for k,v in witness['baseline_paid'].items()}),'witness baseline invoice')
    need(lower_paid==Counter({int(k):v for k,v in witness['proposal_paid' if target else 'lower_paid'].items()}),'witness least invoice')
    need(helpers==Counter({4:28,7:7,8:47,9:326}),'all 408 helper rewards')
    if target:
        need(helpers==Counter({int(k):v for k,v in witness['baseline_helpers'].items()}),'witness baseline helper invoice')
        need(new_helpers==Counter({int(k):v for k,v in witness['proposal_helpers'].items()}),'witness proposal helper invoice')
        need(witness['zero_productivity_combinations']==[] and witness['all_binary_combinations_strictly_productive'],'declared strict productivity')
    return linear,{k:v for k,v in pair.items() if v!=ZERO},{'source_nodes':len(old),'all_edges':len(edges),'orientation':'forward','proposals':len(expected),'affected_edges':len(tables),'old_zero_edges_affected_including_warps':zero_changed,'old_zero_paid_edges_affected':zero_changed-warps_changed,'native_warps_affected':warps_changed,'helper_endpoints_changed':len(expected.intersection(initial+final)),'proposal_helper_rewards':dict(new_helpers),'boundary_mode':proof_mode,'adapter_pins_after_nonidentity_map':target['adapter_pins_after_nonidentity_map'] if target else None,'retained_helper_exit_pins':target['retained_helper_exit_pins'] if target else None,'restored_frozen_least_differences':sum(old[i]!=low[i] for i in fixed),'helper_rewards':dict(helpers),'baseline_paid':dict(paid)}

def graph_energy(d,linear,pair):
    ids=d['ids'];need(ids==sorted(linear),'ordered graph variable IDs')
    n=len(ids);S=n;T=n+1;sw={int(k):v for k,v in d['switch'].items()}
    need(set(sw)==set(ids) and set(sw.values())<={0,1},'binary switch')
    need(d['groups']==len(ids) and d['pair_terms']==len(pair),'reported graph inventory')
    reachable=set(d['terminal_reachable'])
    selected=[i for j,i in enumerate(ids) if sw[i]^(j not in reachable)]
    need(selected==d['selected_groups'],'reported minimizing assignment')
    # Expand cut arcs as a quadratic in original x, independently of the
    # author's switched-submodular graph construction.
    coeff=defaultdict(lambda:ZERO);coeff[()]=tuple(d['graph_constant'])
    def multiply(a,b):
        out=defaultdict(int)
        for ma,ca in a.items():
            for mb,cb in b.items():out[tuple(sorted(set(ma+mb)))]+=ca*cb
        return out
    def y(i):return {():sw[ids[i]],(ids[i],):1-2*sw[ids[i]]}
    def one_minus(p):return {k:(1 if k==() else 0)-v for k,v in {():0,**p}.items()}
    for a,b,cap in d['source_arcs']:
        need(0<=a<n+2 and 0<=b<n+2 and a!=b and len(cap)==10 and cap[0]==0,'graph arc shape')
        ya={():0} if a==S else {():1} if a==T else y(a)
        yb={():0} if b==S else {():1} if b==T else y(b)
        for monomial,k in multiply(one_minus(ya),yb).items():coeff[monomial]=add(coeff[monomial],scale(cap,k))
    expected={():ZERO,**{(i,):scale(c,2) for i,c in linear.items()},**{k:scale(c,2) for k,c in pair.items()}}
    need({k:v for k,v in coeff.items() if v!=ZERO}=={k:v for k,v in expected.items() if v!=ZERO},'cut graph equals twice source energy for every assignment')

@lru_cache(None)
def log_interval(r):
    # Independent rational atanh series with 30 terms and argument reduction.
    def unit(q):
        z=(q-1)/(q+1)
        lo=2*sum((z**(2*k+1)/Q(2*k+1) for k in range(30)),Q(0))
        return lo,lo+2*z**61/(61*(1-z*z))
    k=r.bit_length()-1;a,b=unit(Q(2));c,d=unit(Q(r,1<<k))
    return k*a+c,k*b+d

@lru_cache(None)
def power_interval(r,c):
    a,b=log_interval(r);lo,hi=c*a,c*b
    need(0<=lo<=hi<Q(1,2),'exponential series range')
    def partial(x,n):
        total=term=Q(1)
        for j in range(1,n+1):term*=-x/Q(j);total+=term
        return total
    # Alternating terms decrease: odd truncation is below, even above.
    return r*partial(hi,19),r*partial(lo,18)

def certify(poly):
    need(len(poly)==10 and all(type(v)is int for v in poly) and poly[0]==0,'rank polynomial shape')
    # Representation of any increasing concave rank tariff by min(r,k).
    if all(sum(poly[r]*min(r,k) for r in range(1,10))>=0 for k in range(1,10)):return 'concave'
    mass=sum(r*poly[r] for r in range(1,10));need(mass>=0,'nonnegative at C=0')
    for j in range(16):
        l=Q(j,3200);h=Q(j+1,3200);bound=Q(0)
        for r in range(1,10):
            a=power_interval(r,h)[0];b=power_interval(r,l)[1]
            coefficient=poly[r]
            if not mass:
                la,lb=log_interval(r);a*=la;b*=lb;coefficient=-coefficient
            bound+=coefficient*(a if coefficient>=0 else b)
        need(bound>0,'rational interval positivity')
    return 'derivative' if not mass else 'value'

def verify_flow(d):
    n=len(d['ids'])+2;S=n-2;T=n-1;initial=[[] for _ in range(n)];arcs=[]
    for a,b,c in d['source_arcs']:
        ai,bi=len(initial[a]),len(initial[b]);c=tuple(c)
        initial[a].append((b,c,bi));initial[b].append((a,ZERO,ai));arcs.append((a,ai,b,bi,c))
    final=d['final_residual'];need(len(final)==n,'residual node count')
    for old,row in zip(initial,final):
        need(len(old)==len(row),'residual adjacency shape')
        for (ob,oc,oi),(b,c,i) in zip(old,row):need((ob,oi)==(b,i),'residual incidence and reverse pairing')
    divergence=[ZERO]*n;polynomials=set();reachable=set(d['terminal_reachable']);need(S in reachable and T not in reachable,'separating cut')
    cut=ZERO
    for a,ai,b,bi,c in arcs:
        residual=tuple(final[a][ai][1]);flow=tuple(final[b][bi][1])
        need(add(residual,flow)==c,'individual arc capacity conservation')
        divergence[a]=add(divergence[a],flow);divergence[b]=sub(divergence[b],flow)
        polynomials.update([c,residual,flow])
        if a in reachable and b not in reachable:cut=add(cut,c)
    for a,row in enumerate(final):
        for b,c,r in row:
            if a in reachable and b not in reachable:need(tuple(c)==ZERO,'cut saturated identically')
    need(all(v==ZERO for i,v in enumerate(divergence) if i not in (S,T)),'flow conservation at every variable')
    need(add(divergence[S],divergence[T])==ZERO and divergence[S]==cut,'exact max-flow/min-cut equality')
    need(add(cut,tuple(d['graph_constant']))==tuple(d['minimum_polynomial'])==ZERO,'identically zero energy minimum')
    need(all(type(i)is int and 0<=i<n for i in reachable),'cut vertex range')
    signs=Counter(certify(p) for p in sorted(polynomials) if p!=ZERO)
    return {'arcs':len(arcs),'nonzero_capacity_polynomials':len(polynomials-{ZERO}),'interval_C':['0','1/200'],'independent_exact_signs':dict(signs),'cut_polynomial':list(cut),'minimum_polynomial':[0]*10}

def source_bytes(raw):
    need(sha(raw)==SOURCE_SHA256,'frozen combined word hash')
    return json.loads(raw)

def rejection_controls(raw,witness,d,proof_mode):
    controls=[]
    def reject(name,action,reason):
        try:action()
        except ValueError as exc:
            need(reason in str(exc),'unexpected corruption rejection: '+str(exc))
            controls.append(name)
        else:raise ValueError('corruption accepted: '+name)
    reject('source hash mismatch',lambda:source_bytes(raw+b' '),'frozen combined word hash')
    bad=copy.deepcopy(witness);bad['tables'][0][4][1]+=1
    reject('rank table corruption',lambda:reconstruct_energy(bad,json.loads(raw),proof_mode),'every ordered four-state rank table')
    bad=copy.deepcopy(witness);first=next(iter(bad['proposals']));bad['proposals'][first][0]=0
    reject('proposal chart corruption',lambda:reconstruct_energy(bad,json.loads(raw),proof_mode),'full chart rows')
    bad=copy.deepcopy(d);bad['graph_constant'][1]+=1
    reject('energy constant corruption',lambda:verify_flow(bad),'identically zero energy minimum')
    # Subtract a large circulation from antiparallel internal arcs whose
    # endpoints lie on the same cut side. This preserves all arc sums,
    # vertex conservation, cut capacity, saturation and the claimed minimum;
    # only the negative-flow capacity certificate can reject the forgery.
    adjacency=[[] for _ in d['final_residual']];arcs={}
    for a,b,c in d['source_arcs']:
        ai,bi=len(adjacency[a]),len(adjacency[b]);adjacency[a].append(b);adjacency[b].append(a)
        arcs[a,b]=(a,ai,b,bi)
    cut=set(d['terminal_reachable']);n=len(d['ids'])
    pair=next((edge for edge in arcs if edge[::-1] in arcs and max(edge)<n and ((edge[0] in cut)==(edge[1] in cut))),None)
    need(pair is not None,'internal antiparallel control arcs')
    bad=copy.deepcopy(d)
    for key in (pair,pair[::-1]):
        a,ai,b,bi=arcs[key]
        bad['final_residual'][a][ai][1][1]+=1000000
        bad['final_residual'][b][bi][1][1]-=1000000
    reject('negative circulation with conservation and cut preserved',lambda:verify_flow(bad),'nonnegative at C=0')
    return controls

def run(args):
    started=time.monotonic();compressed=args.word.read_bytes()
    raw=gzip.decompress(compressed) if compressed[:2]==b'\x1f\x8b' else compressed
    payload=source_bytes(raw)
    wr=args.witness.read_bytes();dr=args.certificate.read_bytes()
    witness=json.loads(wr);d=json.loads(dr);need(sha(wr)==d['proposal_source_sha256'],'witness hash bound by certificate')
    linear,pair,source=reconstruct_energy(witness,payload,args.proof_mode)
    graph_energy(d,linear,pair);flow=verify_flow(d)
    controls=rejection_controls(raw,witness,d,args.proof_mode) if args.self_test else []
    result={'status':'PASS_INDEPENDENT_SOURCE_AND_FLOW_AUDIT','source_sha256':sha(raw),'witness_sha256':sha(wr),'certificate_sha256':sha(dr),'source':source,'flow':flow,'negative_controls':controls,'scope':'Forward original-versus-source-derived least canonical chart at all declared unfrozen uncontracted nodes of the fixed 98-event-combined source word. Fixed native G maps; boundary mode '+args.proof_mode+'. No new kappa, physical phase admission, or global optimum claim.','seconds':round(time.monotonic()-started,3)}
    if args.output:args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proof-mode',choices=['fixed-helper','joint-helper'],required=True)
    parser.add_argument('--word',type=Path,required=True)
    parser.add_argument('--witness',type=Path,required=True)
    parser.add_argument('--certificate',type=Path,required=True)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--self-test',action='store_true')
    run(parser.parse_args())

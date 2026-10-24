#!/usr/bin/env python3
"""Exact restricted frame-domain min-sum; no physical emitter or large search."""
import argparse
import hashlib
import importlib.util
import itertools
import json
import time
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT = HERE.parents[2] / 'outputs/mathematics-paper-research-20261023/frame-optimization'
C = Q(15108879, 5000000000)
ZERO = (0,) * 10
PENALTY = (0, 5328) + (0,) * 8

def need(x, message):
    if not x: raise ValueError(message)

def add(a,b): return tuple(x+y for x,y in zip(a,b))
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def singleton(r): return tuple(int(i==r and r>0) for i in range(10))

def log_bounds(r, n):
    # ln(r)=k ln(2)+ln(r/2^k); each atanh argument is in [0,1/3].
    def series(x):
        z=(x-1)/(x+1)
        total=sum((z**(2*j+1)/Q(2*j+1) for j in range(n)), Q(0))*2
        tail=2*z**(2*n+1)/(Q(2*n+1)*(1-z*z))
        return total,total+tail
    k=r.bit_length()-1
    a,b=series(Q(2));d,e=series(Q(r,2**k))
    return k*a+d,k*b+e

def exp_bounds(x,n):
    # Positive x<1. Tail ratios after n are bounded by x/(n+2).
    term=Q(1);total=term
    for j in range(1,n+1):
        term*=x/j;total+=term
    first=term*x/(n+1)
    return total,total+first/(1-x/Q(n+2))

class Price:
    def __init__(self):
        self.n=24;self.cache={};self.bounds={};self.refinements=0;self.comparisons=0;self.certificates=[]
    def prepare(self):
        self.bounds={0:(Q(0),Q(0)),1:(Q(1),Q(1))}
        for r in range(2,10):
            lo,hi=log_bounds(r,self.n)
            elo,_=exp_bounds(C*lo,self.n)
            _,ehi=exp_bounds(C*hi,self.n)
            self.bounds[r]=(Q(r)/ehi,Q(r)/elo)
    def interval(self,h):
        lo=hi=Q(0)
        for r,a in enumerate(h):
            l,u=self.bounds[r]
            lo+=a*(l if a>=0 else u);hi+=a*(u if a>=0 else l)
        return lo,hi
    def compare(self,a,b):
        if a==b:return 0
        d=sub(a,b)
        if d in self.cache:return self.cache[d]
        self.comparisons+=1
        while True:
            lo,hi=self.interval(d)
            if hi<0: sign=-1;break
            if lo>0: sign=1;break
            self.n*=2;self.refinements+=1
            need(self.n<=384,'STOP_UNRESOLVED_DISTINCT_HISTOGRAM')
            self.prepare()
        self.cache[d]=sign;self.cache[tuple(-x for x in d)]=-sign
        self.certificates.append({'difference_histogram':list(d),'sign':sign,
                                  'series_terms':self.n,'interval_decimal':decimal_bounds((lo,hi))})
        return sign

def decimal_bounds(pair,digits=30):
    scale=10**digits
    lo,hi=pair
    def show(n):
        sign='-' if n<0 else '';n=abs(n)
        return sign+str(n//scale)+'.'+str(n%scale).zfill(digits)
    return [show(lo.numerator*scale//lo.denominator),
            show(-((-hi.numerator*scale)//hi.denominator))]

def domain(frame,lo,hi):
    # Select an independent complement of lo inside hi. Enumerate the ENTIRE
    # quotient subspace lattice by repeated adjoining of each quotient vector.
    comp=[];span=lo
    for v in frame.basis(hi):
        if not (span>>v)&1:
            comp.append(v);span=frame.join(span,frame.space([v]))
    need(span==hi,'Complement spans upper')
    qspace=frame.space(comp)
    vectors=[v for v in range(1,512) if (qspace>>v)&1]
    vals={lo}
    for v in vectors:
        vals|={frame.join(s,frame.space([v])) for s in tuple(vals)}
    result=sorted(vals)
    need(all(s&lo==lo and s&hi==s for s in result),'Domain interval')
    need(all(frame.space(frame.basis(s))==s for s in result),'Actual subspace closure')
    expect={0:1,1:2,2:5,3:16}[len(comp)]
    need(len(result)==expect,'Complete quotient cardinality')
    return result

def histogram(frame,graph,values):
    graph.check(values)
    h=list(ZERO);h[8]=8
    for b,parents in enumerate(graph.parents):
        for a,g in parents:
            need(frame.image(g,values[a])&values[b]==frame.image(g,values[a]),'Mapped containment')
            r=frame.dimension(values[b])-frame.dimension(values[a])
            need(r>=0,'Ascending rank')
            if r:h[r]+=1
    return tuple(h)

def solve_component(order,domains,factors,price):
    factors=list(factors);records=[];states=0;largest=0
    for v in order:
        bucket=[f for f in factors if v in f[0]]
        factors=[f for f in factors if v not in f[0]]
        need(bucket,'Nonempty variable bucket')
        scope=tuple(sorted({w for s,t in bucket for w in s}));sep=tuple(w for w in scope if w!=v)
        table={};choice={}
        for indices in itertools.product(*(range(len(domains[w])) for w in sep)):
            env=dict(zip(sep,indices));best=None;arg=None
            for j in range(len(domains[v])):
                env[v]=j;value=ZERO;states+=1
                for s,t in bucket:value=add(value,t[tuple(env[w] for w in s)])
                if best is None or price.compare(value,best)<0:best,arg=value,j
            table[indices]=best;choice[indices]=arg
        largest=max(largest,len(table)*len(domains[v]))
        factors.append((sep,table));records.append((v,sep,choice))
    need(all(not s for s,t in factors),'Elimination complete')
    optimum=ZERO
    for s,t in factors:optimum=add(optimum,t[()])
    assignment={}
    for v,sep,choices in reversed(records):assignment[v]=choices[tuple(assignment[w]for w in sep)]
    return optimum,assignment,states,largest,records

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source-root',type=Path,default=DEFAULT)
    parser.add_argument('--output',type=Path,default=HERE/'RESULT.json');args=parser.parse_args()
    start=time.monotonic();src=args.source_root.resolve()
    spec=importlib.util.spec_from_file_location('authenticated_frame_probe',src/'inspect_graph.py')
    probe=importlib.util.module_from_spec(spec);spec.loader.exec_module(probe)
    data,construct,frame=probe.load()
    frozen=json.loads((src/'GRAPH-STRUCTURE.json').read_text())
    published=json.loads((probe.FROZEN/'research/carried-warp-frame-intervals/RESULT.json').read_text())
    price=Price();price.prepare();result={'status':'PASS_EXACT_RESTRICTED_OPTIMUM','C':str(C),'directions':{},'physical_emitter':False,'new_kappa':None}
    for direction,source in data['programs'].items():
        tick=time.monotonic();program,swaps,unequal=construct(source)
        need((swaps,unequal)==(534,43),'Frozen constructor census')
        schedule=frame.NativeSchedule(data['canonical'],program);graph=schedule.graph
        lower,upper=graph.bounds();original=schedule.original_values
        need(len(graph.fixed)==15935 and sum(map(len,graph.parents))==29790,'Complete graph census')
        need(Counter(e[-1]for e in program if e[0]=='center')=={8:8},'Owned centres constant')
        variable={v for v in range(len(lower))if lower[v]!=upper[v]}
        adjacency={v:set()for v in variable}
        for b in variable:
            for a,g in graph.parents[b]:
                if a in variable:adjacency[a].add(b);adjacency[b].add(a)
        comps=probe.components(adjacency);need(len(comps)==19 and len(comps[0])==1271,'Components')
        small=set.union(*comps[1:]);need(len(small)==68,'Small variable scope')
        domains={v:domain(frame,lower[v],upper[v])for v in sorted(small)}
        need(Counter(map(len,domains.values()))=={2:53,5:12,16:3},'Domain census')
        need(all(original[v]in domains[v]for v in small),'Source fallback inclusion')
        controls={}
        for name,values in [('original_contacts',original),('least',lower),('greatest',upper)]:
            h=histogram(frame,graph,values)
            expected={int(k):v for k,v in published['directions'][direction]['schedules'][name]['paid'].items()}
            need({r:n for r,n in enumerate(h)if n}==expected,'Known profile '+name)
            controls[name]=list(h)
        values=list(original);comp_results=[];total_states=0
        for ci,comp in enumerate(comps[1:],1):
            order=frozen['directions'][direction]['elimination_components'][ci]['ordering']
            need(set(order)==comp,'Frozen order exact component')
            factors=[];edge_ids=[]
            for b,parents in enumerate(graph.parents):
                for ei,(a,g)in enumerate(parents):
                    if a not in comp and b not in comp:continue
                    scope=tuple(sorted(v for v in (a,b)if v in comp))
                    need(not ((a in variable and a not in comp)or(b in variable and b not in comp)),'No omitted variable neighbor')
                    table={}
                    for ix in itertools.product(*(range(len(domains[v]))for v in scope)):
                        env={v:domains[v][j]for v,j in zip(scope,ix)}
                        av=env.get(a,original[a]);bv=env.get(b,original[b])
                        moved=frame.image(g,av)
                        table[ix]=singleton(frame.dimension(bv)-frame.dimension(av))if moved&bv==moved else PENALTY
                    factors.append((scope,table));edge_ids.append([a,b,ei,list(g)])
            optimum,assignment,states,largest,trace=solve_component(order,domains,factors,price)
            direct=ZERO
            for scope,table in factors:direct=add(direct,table[tuple(assignment[v]for v in scope)])
            need(direct==optimum,'Traceback original factor objective')
            source_h=ZERO
            for scope,table in factors:source_h=add(source_h,table[tuple(domains[v].index(original[v])for v in scope)])
            need(price.compare(optimum,source_h)<=0,'Source fallback cost')
            for v,j in assignment.items():values[v]=domains[v][j]
            total_states+=states
            comp_results.append({'nodes':sorted(comp),'order':order,'factor_multiedges':len(factors),'edge_sha256':hashlib.sha256(json.dumps(edge_ids,separators=(',',':')).encode()).hexdigest(),'bucket_states':states,'largest_bucket_states':largest,'histogram':list(optimum),'source_histogram':list(source_h),'domain_sizes':{str(v):len(domains[v])for v in sorted(comp)},'assignment_indices':assignment,'traceback':[[v,list(sep),[[list(k),j]for k,j in sorted(ch.items())]]for v,sep,ch in trace]})
        need(total_states==1095,'Measured bucket states match declared domain')
        need(all(values[v]==original[v]for v in range(len(values))if v not in small),'Large and determined contacts untouched')
        full=histogram(frame,graph,values);old=histogram(frame,graph,original)
        delta=sub(full,old);cmp=price.compare(full,old)
        # Three source-bound semantic rejection controls.
        bad=list(values);v=next(v for v in small if upper[v]!=graph.full);bad[v]=graph.full
        try:graph.check(bad)
        except ValueError:bad_rejected=True
        else:bad_rejected=False
        need(bad_rejected,'Out-of-interval/fixed-neighbor mutation rejected')
        positive_edge=next((a,b,g)for b,ps in enumerate(graph.parents)for a,g in ps if frame.dimension(original[b])>frame.dimension(original[a]))
        a,b,g=positive_edge;dropped=list(old);dropped[frame.dimension(original[b])-frame.dimension(original[a])]-=1
        need(tuple(dropped)!=old,'Dropped multiplicity changes full invoice')
        map_witness=None
        for b,ps in enumerate(graph.parents):
            for a,g in ps:
                if g!=graph.identity and original[a]&original[b]!=original[a]:map_witness=[a,b];break
            if map_witness:break
        need(map_witness is not None,'Actual map-to-identity containment failure control')
        result['directions'][direction]={'small_variables':68,'large_variables_held_source':1271,'mapped_edges_checked':29790,'components':comp_results,'all_domains':{str(v):list(map(str,domains[v]))for v in sorted(small)},'assignment':{str(v):str(values[v])for v in sorted(small)},'changed_nodes':[v for v in sorted(small)if values[v]!=original[v]],'original_histogram':list(old),'optimal_full_histogram':list(full),'delta_histogram':list(delta),'delta_interval_rational':list(map(str,price.interval(delta))),'delta_interval_decimal':decimal_bounds(price.interval(delta)),'strict_improvement':cmp<0,'six_profile_controls_this_direction':controls,'semantic_controls':{'bad_assignment_rejected':bad_rejected,'dropped_edge_histogram_rejected':True,'map_to_identity_containment_rejected_at':map_witness},'bucket_states':total_states,'runtime_seconds':round(time.monotonic()-tick,6)}
        print(json.dumps({'direction':direction,'bucket_states':total_states,'changed':len(result['directions'][direction]['changed_nodes']),'histogram':full,'delta':result['directions'][direction]['delta_interval_decimal'],'seconds':result['directions'][direction]['runtime_seconds']}),flush=True)
    result['comparison']={'log_and_exp_terms':price.n,'refinements':price.refinements,'distinct_comparisons':price.comparisons,'method':'exact rational atanh log and positive exp Taylor bounds; signed histogram coefficients enclosed outward',
                         'final_weight_bounds_rational':{str(r):list(map(str,b))for r,b in price.bounds.items()},
                         'certificates':price.certificates}
    result['source_manifest']=json.loads((src/'SOURCE-MANIFEST.json').read_text())
    result['loader_sha256']=hashlib.sha256((src/'inspect_graph.py').read_bytes()).hexdigest()
    result['script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result['total_runtime_seconds']=round(time.monotonic()-start,6)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'total_seconds':result['total_runtime_seconds'],'comparisons':price.comparisons,'refinements':price.refinements}))

if __name__=='__main__':main()

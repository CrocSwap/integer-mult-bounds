"""Credited PR4610 helper_line_milp adapted to an explicitly supplied changed word.
Discovery only, no exact optimality claim. Apache-2.0; OpenAI assistance.
"""
from collections import Counter,defaultdict
from copy import deepcopy
from itertools import product
from pathlib import Path
import argparse,gzip,json,sys,time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE/'.deps'))
import numpy as np
import scipy
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import csc_array
sys.path.insert(0,str(ROOT/'research/kappa-round3-warp-20261022'))
sys.path.insert(0,str(ROOT/'research/warp-interface-20261022'))
from warp_merge import J,F,roles,synthesize
from constrained_map import line_matching_map
from free_warp_contacts import matching_map
sys.path.insert(0,str(ROOT/'research/scalar-reorder-20261022'))
from intervals import complete_interval


def main(op,time_limit):
    started=time.monotonic();payload=json.loads(gzip.decompress((Path(INPUT_WORD)).read_bytes()));c=payload['canonical'];programs=payload['programs'];p=[deepcopy(e) for e in programs['forward'] if e[0]!='climb']
    spans=[F.span(b) for b in c['frames']];dims=[len(b) for b in c['frames']];labels={s:i for i,s in enumerate(spans)}
    def label(s):
        s=frozenset(s)
        if s not in labels:
            b=[];v={0}
            for x in sorted(s):
                if x not in v:b.append(x);v|={y^x for y in tuple(v)}
            labels[s]=len(spans);spans.append(s);dims.append(len(b));c['frames'].append(b)
        return labels[s]
    jc={};mc={}
    def join(a,b):
        key=min(a,b),max(a,b)
        if key not in jc:
            if spans[a]<=spans[b]:jc[key]=b
            elif spans[b]<=spans[a]:jc[key]=a
            else:
                v=set(spans[a])
                for x in c['frames'][b]:
                    if x not in v:v|={y^x for y in tuple(v)}
                jc[key]=label(v)
        return jc[key]
    def meet(a,b):
        key=min(a,b),max(a,b)
        if key not in mc:mc[key]=label(spans[a]&spans[b])
        return mc[key]
    const=lambda f:-f-1
    fixed=lambda n:-n-1
    ops=list(range(1,73)) if op=='all' else [op]
    line_constraints={}
    selected_ops={}
    for operator in ops:
        occurrence=[i for i,e in enumerate(p) if e[0]=='warp' and abs(e[2])==operator]
        candidates=[i for i in occurrence if dims[p[i][3]] not in (0,9) or dims[p[i][4]] not in (0,9)]
        chosen=max(candidates,key=lambda i:dims[p[i][3]])
        F.need(p[chosen][2]>0,'Positive selected late warp')
        selected_ops[chosen]=operator
        if len(candidates)>1:
            pairs={(p[i][3],p[i][4]) if p[i][2]>0 else (p[i][4],p[i][3]) for i in candidates if i!=chosen}
            F.need(len(pairs)==1,'One preserved prelude line pair')
            a,b=next(iter(pairs));F.need(dims[a]==dims[b]==1,'Fixed line constraint');line_constraints[operator]=(c['frames'][a][0],c['frames'][b][0])
    helper_nodes={len(p)+r:r for r in range(224,632)}
    current=[len(p)+r if r>=224 else const(f) for r,f in enumerate(c['start'])];edges=[];original={n:c['start'][r] for n,r in helper_nodes.items()};variables=list(helper_nodes);free_records={}
    def edge(a,b):
        if isinstance(a,tuple):
            edges.append((a[0],b,a[1]));free_records[a[1]]=(a[0],b)
        else:edges.append((a,b,'normal'))
    for i,e in enumerate(p):
        rs=roles(e)
        if e[0]=='scalar' and rs:
            g=e[1];allL=all(r[0]=='L' for r in (g[1:3] if g[0] in ('add','copy') else g[1:2]))
            node=i if allL else const(e[2])
            if allL:variables.append(i);original[i]=e[2]
            for r in rs:edge(current[r],node);current[r]=node
        elif e[0]=='warp':
            r=e[1][1]
            if i in selected_ops:current[r]=(current[r],selected_ops[i])
            else:edge(current[r],const(e[3]));current[r]=const(e[4])
    for r,f in enumerate(c['final']):edge(current[r],const(f))
    for n,r in helper_nodes.items():edges.append((n,const(c['final'][r]),'helper'))
    incoming=defaultdict(list);outgoing=defaultdict(list)
    for a,b,k in edges:
        if k=='normal':incoming[b].append(a);outgoing[a].append(b)
    lower={};upper={}
    for n in variables:
        z=0
        for a in incoming[n]:z=join(z,lower[a] if a>=0 else fixed(a))
        lower[n]=z
    for n in reversed(variables):
        z=1
        for b in outgoing[n]:z=meet(z,upper[b] if b>=0 else fixed(b))
        upper[n]=z
    domain={};cache={};counts=Counter()
    for n in variables:
        lo,hi=lower[n],upper[n];key=lo,hi
        F.need(spans[lo]<=spans[original[n]]<=spans[hi],'Original scalar in relaxed interval')
        if key not in cache:
            qs={};choices=complete_interval(spans,dims,c['frames'],(lo,),(hi,),qs,max_gap=5)
            counts.update(qs)
            # Wide intervals use a bounded, explicitly incomplete catalogue.
            if qs.get('skipped_large_interval') and len(choices)>128:
                choices=sorted(choices,key=lambda f:(dims[f],f));step=max(1,len(choices)//120);choices=choices[::step][:120]+[lo,hi]
                counts['catalogue_truncated']+=1
            cache[key]=choices
        domain[n]=list(dict.fromkeys(cache[key]+[original[n]]))
    aliases={n:const(v[0]) for n,v in domain.items() if len(v)==1}
    E=Counter((aliases.get(a,a),aliases.get(b,b),k) for a,b,k in edges)
    active={n:v for n,v in domain.items() if len(v)>1}
    print('MODEL_DOMAINS',op,len(active),sum(map(len,active.values())),dict(counts),flush=True)
    costs=[];integrality=[];nodevars={};rows=[];cols=[];data=[];lb=[];ub=[]
    def newvar(cost,integer=False):
        i=len(costs);costs.append(cost);integrality.append(int(integer));return i
    def constraint(coefs,target):
        r=len(lb);lb.append(target);ub.append(target)
        for v,a in coefs.items():
            if a:rows.append(r);cols.append(v);data.append(a)
    for n,choices in active.items():
        nodevars[n]={f:newvar(0.,True) for f in choices};constraint({v:1 for v in nodevars[n].values()},1)
    t=1-.00302157135;weight=[0.]+[r**t-r for r in range(1,10)];constant=0.;old_objective=0.
    def oldframe(n):return original[n] if n>=0 else fixed(n)
    for (a,b,kind),multiplicity in E.items():
        A=active[a] if a>=0 else [fixed(a)];B=active[b] if b>=0 else [fixed(b)]
        # The retained native grammar has no zero-rank frame-retag event.
        # Keep identical frame IDs on zero-rank ordinary edges; a same-span
        # different-gauge monomial is outside this bounded discovery model.
        def valid(f,g):
            if kind=='helper':return spans[f]<spans[g]
            if kind=='normal':return f==g or spans[f]<spans[g]
            if dims[f]>dims[g]:return False
            if kind not in line_constraints:return True
            a,b=line_constraints[kind]
            return (b in spans[g]) if a in spans[f] else (dims[f]<dims[g] or b not in spans[g])
        of,og=oldframe(a),oldframe(b);F.need(valid(of,og),'Original edge feasible')
        sign=-1 if kind=='helper' else 1
        old_objective+=sign*multiplicity*weight[dims[og]-dims[of]]
        if a<0 and b<0:constant+=sign*multiplicity*weight[dims[B[0]]-dims[A[0]]];continue
        if a<0 or b<0:
            n=b if a<0 else a
            for f in active[n]:
                x,y=(A[0],f) if a<0 else (f,B[0]);v=nodevars[n][f]
                if not valid(x,y):constraint({v:1},0)
                else:costs[v]+=sign*multiplicity*weight[dims[y]-dims[x]]
            continue
        margA=defaultdict(dict);margB=defaultdict(dict)
        for f,g in product(A,B):
            if not valid(f,g):continue
            v=newvar(sign*multiplicity*weight[dims[g]-dims[f]])
            margA[f][v]=1;margB[g][v]=1
        for f,x in nodevars[a].items():constraint({**margA[f],x:-1},0)
        for g,x in nodevars[b].items():constraint({**margB[g],x:-1},0)
    print('MODEL_READY',op,len(costs),len(lb),'old',old_objective,'seconds',time.monotonic()-started,flush=True)
    matrix=csc_array((np.asarray(data,float),(np.asarray(rows,np.int32),np.asarray(cols,np.int32))),shape=(len(lb),len(costs)))
    result=milp(np.asarray(costs),integrality=np.asarray(integrality),bounds=Bounds(0,1),constraints=LinearConstraint(matrix,np.asarray(lb),np.asarray(ub)),options={'time_limit':time_limit,'mip_rel_gap':1e-10})
    row={'status':'DISCOVERY_ONLY','operator':op,'scipy':scipy.__version__,'numpy':np.__version__,'solver_status':int(result.status),'message':result.message,'variables':len(costs),'constraints':len(lb),'old_objective':old_objective,'constant':constant,'objective':None if result.fun is None else float(result.fun)+constant,'counts':dict(counts),'seconds':time.monotonic()-started}
    if result.x is not None:
        chosen={n:max(nodevars[n],key=lambda f:result.x[nodevars[n][f]]) if n in active else domain[n][0] for n in variables}
        for n in active:F.need(result.x[nodevars[n][chosen[n]]]>.999,'Integral proposed frame')
        recipes={}
        for operator,(A,B) in free_records.items():
            fa=chosen[A] if A>=0 else fixed(A);fb=chosen[B] if B>=0 else fixed(B)
            F.need(dims[fa]<=dims[fb],'Actual free-warp rank compatibility')
            if operator in line_constraints:
                G,outbasis=line_matching_map(c['frames'][fa],c['frames'][fb],*line_constraints[operator])
                fo=label(F.span(outbasis))
            else:
                fo=fb if dims[fa]==dims[fb] else label(F.span(c['frames'][fb][:dims[fa]]));G=matching_map(c['frames'][fa],c['frames'][fo])
            recipes[operator]={'input':fa,'output':fo,'G_columns':G}
        altered={}
        for direction,word in programs.items():
            raw=[deepcopy(e) for e in word if e[0]!='climb']
            for i,f in chosen.items():
                if i<len(p):raw[i][2]=f
                else:c['start'][helper_nodes[i]]=f
            for selected,operator in selected_ops.items():raw[selected][3:5]=[recipes[operator]['input'],recipes[operator]['output']]
            altered[direction]=synthesize(c,raw)
        for w in c['warps']:
            if w['op'] in recipes:w['G_columns']=recipes[w['op']]['G_columns']
        prof={d:Counter(e[5] for e in word if e[0]=='climb') for d,word in altered.items()}
        for d,word in altered.items():prof[d].update(e[4] for e in word if e[0]=='center')
        F.need(prof['forward']==prof['backward'],'Equal complete dual tariffs')
        oldpaid=Counter({1:2201,2:412,3:510,4:127,5:40,8:8});newhelpers=Counter(len(c['frames'][c['final'][r]])-len(c['frames'][c['start'][r]]) for r in range(224,632))
        oldhelpers=Counter({4:28,7:7,8:47,9:326})
        actual_gain=sum(oldpaid[r]*weight[r] for r in oldpaid)-sum(n*weight[r] for r,n in prof['forward'].items())+sum(n*weight[r] for r,n in newhelpers.items())-sum(n*weight[r] for r,n in oldhelpers.items())
        row['helpers']=dict(newhelpers);row['changed_helpers']=[(r,original[n],chosen[n]) for n,r in helper_nodes.items() if chosen[n]!=original[n]]
        row.update(paid=dict(prof['forward']),actual_moment_reduction=actual_gain,changed_scalar_contacts=sum(chosen[n]!=original[n] for n in chosen),warp_recipes=recipes)
        if actual_gain>1e-9:
            row['status']='POSITIVE_UNVERIFIED_NATIVE_CANDIDATE'
            (HERE/'DISCOVERY-CANDIDATE.json').write_text(json.dumps(row,indent=2,sort_keys=True)+'\n')
            (HERE/'DISCOVERY-CANDIDATE-WORD.json.gz').write_bytes(gzip.compress(json.dumps({'canonical':c,'programs':altered},sort_keys=True,separators=(',',':')).encode(),mtime=0))
    (HERE/f'DISCOVERY-OP{op}.json').write_text(json.dumps(row,indent=2,sort_keys=True)+'\n');print(json.dumps(row,sort_keys=True));return row


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--word',required=True);ap.add_argument('--operator',default='all');ap.add_argument('--seconds',type=float,default=20);args=ap.parse_args();INPUT_WORD=args.word;main(args.operator if args.operator=='all' else int(args.operator),args.seconds)

"""Exact binary F/Phi costs on actual scalar-contact components.
Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
Optimization is a finite rank screen, not physical supplier admission.
"""
from collections import Counter,defaultdict,deque
from hashlib import sha256
import gzip
import json
from pathlib import Path
import sys
import time
import realification_census as R

HERE=Path(__file__).resolve().parent


class Union:
    def __init__(self):self.parent=[]
    def new(self):
        i=len(self.parent);self.parent.append(i);return i
    def find(self,i):
        while self.parent[i]!=i:
            self.parent[i]=self.parent[self.parent[i]];i=self.parent[i]
        return i
    def join(self,a,b):
        a,b=self.find(a),self.find(b)
        if a!=b:self.parent[b]=a


def graph(payload):
    c=payload['canonical'];word=payload['programs']['forward'];u=Union()
    frames=[];owned=[]
    def node(frame,is_owned=False):
        i=u.new();frames.append(frame)
        if is_owned:owned.append(i)
        return i
    current={('L',i):node(frame) for i,frame in enumerate(c['start'])}
    starts=dict(current);edges=[];scalar_contacts=0
    for index,event in enumerate(word):
        kind=event[0]
        if kind in ('climb','warp'):
            role=('L',event[2]) if kind=='climb' else tuple(event[1])
            a,b=event[3:5]
            R.need(frames[current[role]]==a,'Actual residence source')
            target=node(b)
            edges.append(dict(kind=kind,event=index,source=current[role],target=target,
                              operator=event[2] if kind=='warp' else 0,old_rank=event[5] if kind=='climb' else 0))
            current[role]=target
        elif kind=='center':
            role=('C',event[1]);a,b=event[2:4]
            R.need(frames[current[role]]==a,'Actual owned center source')
            target=node(b,True)
            edges.append(dict(kind='center',event=index,source=current[role],target=target,operator=0,old_rank=event[4]))
            current[role]=target
        elif kind=='scalar':
            gate,frame=event[1:];op=gate[0];dst=tuple(gate[1])
            if op=='clear':
                R.need(dst[0]=='C','Only explicitly owned fields may clear')
                current[dst]=node(frame,True)
            else:
                R.need(frames[current[dst]]==frame,'Actual scalar destination')
                if op in ('add','copy'):
                    src=tuple(gate[2]);R.need(frames[current[src]]==frame,'Actual scalar source')
                    u.join(current[dst],current[src]);scalar_contacts+=1
                else:R.need(op=='scale','Closed scalar alphabet')
        elif kind=='adapter':
            # Deferred boundary descriptor, inert at its textual position;
            # exit markers precede the subsequent full-frame cleanup word.
            pass
        elif kind=='residual_adapter':
            # Current selected word has no suspended-helper residual adapters.
            raise ValueError('Derive literal residual-adapter endpoints before adding this word')
        else:R.need(kind=='phase','Closed word alphabet')
    ends={('L',i):current['L',i] for i in range(632)}
    for role,at in ends.items():R.need(frames[at]==c['final'][role[1]],'Exact invocation final reference')
    roots=sorted({u.find(i) for i in range(len(frames))});number={r:i for i,r in enumerate(roots)}
    comp=[number[u.find(i)] for i in range(len(frames))]
    compframe={}
    for i,frame in enumerate(frames):
        R.need(compframe.setdefault(comp[i],frame)==frame,'Scalar component has one exact reference frame')
    for edge in edges:
        edge['source_frame']=frames[edge['source']];edge['target_frame']=frames[edge['target']]
        edge['source']=comp[edge['source']];edge['target']=comp[edge['target']]
    helpers=[dict(role=i,source=comp[starts['L',i]],target=comp[ends['L',i]],
                  source_frame=frames[starts['L',i]],target_frame=frames[ends['L',i]]) for i in range(224,632)]
    basefixed={comp[i] for i in owned}
    basefixed|={comp[starts['L',i]] for i in range(224)}|{comp[ends['L',i]] for i in range(224)}
    basefixed|={component for component,frame in compframe.items() if frame==0}
    strictfixed=basefixed|{comp[starts['L',i]] for i in range(224,632)}|{comp[ends['L',i]] for i in range(224,632)}
    return dict(canonical=c,edges=edges,helpers=helpers,components=len(roots),component_frames=compframe,
                original_residences=len(frames),scalar_contacts=scalar_contacts,
                base_fixed=sorted(basefixed),strict_fixed=sorted(strictfixed))


def tables(ce,g,ell,framecache):
    c=g['canonical'];ops={}
    for frame in sorted(set(g['component_frames'].values())):
        basis=tuple(c['frames'][frame])
        if basis not in framecache:framecache[basis]=R.frame_data(ce,basis)
        F,(x,z,p),K=framecache[basis]
        regular=R.tensor_columns(R.tabcols(F),ell)
        ops[frame]=(regular,R.transvection(regular,R.tensor_pauli(x,z,9,ell)))
    native={w['op']:R.Kop(ce,w['G_columns']) for w in c['warps']}
    kt={}
    def body(op):
        if op not in kt:
            actual=native[abs(op)] if op>0 else native[abs(op)].adjoint()
            kt[op]=R.tensor_columns(R.tabcols(actual),ell)
        return kt[op]
    cache={};terms=[]
    for item in g['edges']+g['helpers']:
        helper='role' in item
        a,b=item['source_frame'],item['target_frame'];op=item.get('operator',0)
        key=a,b,op
        if key not in cache:
            cost=[]
            for x in (0,1):
                row=[]
                for y in (0,1):
                    left=ops[a][x];right=ops[b][y]
                    product=R.compose(right,R.compose(body(op),left)) if op else R.compose(right,left)
                    row.append(R.f_rank(ce,product))
                cost.append(row)
            cache[key]=cost
        costs=cache[key]
        if not helper:R.need(costs[0][0]==item['old_rank']*ell,'All-old cost matches original invoice')
        else:R.need(costs[0][0]==ell*(len(c['frames'][b])-len(c['frames'][a])),'Original helper credit')
        terms.append({**item,'kind':'helper' if helper else item['kind'],'costs':costs})
    return terms


def value(terms,modes):
    return sum((-1 if e['kind']=='helper' else 1)*e['costs'][modes[e['source']]][modes[e['target']]] for e in terms)


def signed_structure(terms,n):
    adjacency=defaultdict(list);nonzero=0
    for e in terms:
        a,b=e['source'],e['target'];c=e['costs'];sgn=-1 if e['kind']=='helper' else 1
        interaction=sgn*(c[0][0]+c[1][1]-c[0][1]-c[1][0])
        if interaction and a!=b:
            adjacency[a].append((b,int(interaction>0)))
            adjacency[b].append((a,int(interaction>0)));nonzero+=1
    colors={};conflicts=[]
    for start in range(n):
        if start in colors:continue
        colors[start]=0;queue=deque([start])
        while queue:
            a=queue.popleft()
            for b,parity in adjacency[a]:
                wanted=colors[a]^parity
                if b not in colors:colors[b]=wanted;queue.append(b)
                elif colors[b]!=wanted:conflicts.append((a,b))
    return dict(nonzero_interactions=nonzero,sign_frustrated_edges=len(set(tuple(sorted(e)) for e in conflicts)),colors=colors)


def solve_mincut(terms,n,fixed,colors):
    import networkx as nx
    unary=[[0,0] for _ in range(n)];pairs=[];constant=0
    for e in terms:
        a,b=e['source'],e['target'];sgn=-1 if e['kind']=='helper' else 1
        cost=[[sgn*e['costs'][x^colors[a]][y^colors[b]] for y in (0,1)] for x in (0,1)]
        if a==b:unary[a][0]+=cost[0][0];unary[a][1]+=cost[1][1];continue
        v00,v01,v10,v11=cost[0][0],cost[0][1],cost[1][0],cost[1][1]
        weight=v01+v10-v00-v11
        R.need(weight>=0,'Switched energy is submodular')
        constant+=v00;unary[a][1]+=v10-v00;unary[b][1]+=v11-v10
        if weight:pairs.append((a,b,weight))
    graph=nx.DiGraph();source=n;sink=n+1;graph.add_nodes_from(range(n+2))
    def edge(a,b,c):
        if c:graph.add_edge(a,b,capacity=graph.get_edge_data(a,b,{}).get('capacity',0)+c)
    for i,(a,b) in enumerate(unary):
        low=min(a,b);constant+=low;a-=low;b-=low
        edge(source,i,b);edge(i,sink,a)
    for a,b,w in pairs:edge(a,b,w)
    infinity=1+sum(d['capacity'] for _,_,d in graph.edges(data=True))
    for i in fixed:
        if colors[i]:edge(i,sink,infinity)
        else:edge(source,i,infinity)
    optimum,(left,right)=nx.minimum_cut(graph,source,sink)
    modes=[int(i in right)^colors[i] for i in range(n)]
    R.need(all(modes[i]==0 for i in fixed),'Fixed old gauges')
    R.need(value(terms,modes)==optimum+constant,'Exact mincut energy replay')
    return modes,int(optimum+constant)


def main():
    began=time.monotonic();pins=R.read(HERE/'SOURCES.json')
    for row in pins['files']:R.need(sha256((HERE/row['copy']).read_bytes()).hexdigest()==row['sha256'],'Source pin')
    ce=R.load(HERE/'sources'/R.CE,'mixed_actual_clifford')
    payload=R.read(HERE/'sources/research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz')
    g=graph(payload);framecache={};results=[]
    for ell in (1,3):
        terms=tables(ce,g,ell,framecache)
        structure=signed_structure(terms,g['components'])
        cases=[]
        for boundary,fixed in [('strict',g['strict_fixed']),('helper_free_optimistic',g['base_fixed'])]:
            row=dict(boundary=boundary,fixed_components=len(fixed),all_old_energy=value(terms,[0]*g['components']))
            if structure['sign_frustrated_edges']==0:
                modes,energy=solve_mincut(terms,g['components'],fixed,structure['colors'])
                row.update(solver='exact integer mincut',energy=energy,modes=modes,
                           changed_components=sum(modes),local_deficit=energy-1792*ell)
            else:row.update(solver='requires non-submodular optimizer',energy=None)
            cases.append(row)
        results.append(dict(ell=ell,terms=terms,structure={k:v for k,v in structure.items() if k!='colors'},cases=cases))
        print('PASS_MIXED_GAUGE_GRAPH',ell,'components',g['components'],'frustrated',structure['sign_frustrated_edges'],
              'cases',[{k:v for k,v in row.items() if k!='modes'} for row in cases],'elapsed',round(time.monotonic()-began,2),flush=True)
    output=dict(status='PASS_EXACT_MIXED_GAUGE_CONTACT_GRAPH',original_residences=g['original_residences'],
                components=g['components'],scalar_contacts=g['scalar_contacts'],component_frames=g['component_frames'],
                base_fixed=g['base_fixed'],strict_fixed=g['strict_fixed'],results=results,
                source_manifest_sha256=sha256((HERE/'SOURCES.json').read_bytes()).hexdigest(),
                script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),helper_sha256=sha256((HERE/'realification_census.py').read_bytes()).hexdigest(),
                helper_free_scope='Optimistic new independent helper frame endpoints. Existing external helper-adapter/full-job semantics and exact absolute phases must be bound separately before admission.',
                new_kappa=False)
    (HERE/'MIXED-GAUGE.json.gz').write_bytes(gzip.compress(json.dumps(output,sort_keys=True,separators=(',',':')).encode(),mtime=0))


if __name__=='__main__':main()

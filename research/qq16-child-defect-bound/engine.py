"""Signed chronological sensitivities, independent of the retained interpreter.

All maps act on logical fields; native frame changes are unitary isometries.
No symbolic-child result, matrix rank or sensitivity is cached as an answer.
Apache-2.0; ywz65 with OpenAI Codex assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import hashlib,json
from sources import need

IDENTITY=tuple(1<<j for j in range(73))
FAULT_OPS={'add','line','stage','current_map'}

def act(g,x):
    y=0
    for j in range(73):
        if x>>j&1:y^=g[j]
    return y

@lru_cache(None)
def compose(g,h):return tuple(act(g,x) for x in h)

def plus(a,b,c=Q(1)):
    out=dict(a)
    for key,value in b.items():
        z=out.get(key,Q(0))+c*value
        if z:out[key]=z
        else:out.pop(key,None)
    return out

def route(g,row):
    out={(v,compose(g,h)):c for (v,h),c in row.items()}
    need(len(out)==len(row),'route is injective on group elements')
    return out

def canon(row):
    return [[v,list(g),str(c)] for (v,g),c in sorted(row.items())]

def digest(value):return hashlib.sha256(json.dumps(value,separators=(',',':'),sort_keys=True).encode()).hexdigest()

def weights(word):
    return {f'd{i}':(e['op'],1+abs(Q(e['coefficient'])) if e['op']=='add' else Q(1))
            for i,e in enumerate(word) if e['op'] in FAULT_OPS}

def norms(row,sites):
    p,a,k,n,c=Q(0),Q(0),Q(0),Q(0),Q(0)
    for (v,_),x in row.items():
        x=abs(x)
        if v.startswith('i:'):p+=x
        else:
            op,w=sites[v];a+=x;k+=x*w
            if op in ('line','stage'):n+=x
            if op=='current_map':c+=x
    return dict(P=p,A=a,K=k,native=n,cover=c)

def forward(old,word,records):
    V=old.V
    rows={f'X{p}':{('i:E'+str(p),IDENTITY):Q(1)} for p in V}
    sites=weights(word); trace=[]; peaks={}; peakrows={}; final={}; clears=[]
    private=set(); boundary=False
    def observe(i,name):
        values=norms(rows[name],sites)
        trace.append([i,name,*[str(values[k]) for k in ('P','A','K','native','cover')]])
        for kind,value in values.items():
            if kind not in peaks or value>Q(peaks[kind]['value']):
                peaks[kind]={'event':i,'field':name,'value':str(value)}
                peakrows[kind]=dict(rows[name])
    for i,e in enumerate(word):
        op=e['op']; changed=[]
        if op=='history_boundary':
            need(not boundary,'unique history boundary');boundary=True
            for side in ('X','Y'):
                for p in range(112):
                    name=f'{side}{p}';rows[name]={('i:'+name,IDENTITY):Q(1)};changed.append(name)
        elif op=='private_begin':
            need(not private,'private lifetime overlap');private=set(e['fields'])
            need(all(x not in rows for x in private),'private reuse without retirement')
        elif op=='private_end':
            need(private==set(e['fields']) and all(not rows[x] for x in private),'exact owned clear before retirement')
            for x in private:del rows[x]
            private=set()
        elif op=='clear':
            name=e['field']
            if name in rows:clears.append([i,name,*[str(v) for v in norms(rows[name],sites).values()]])
            rows[name]={};changed=[name]
        elif op=='add':
            dst,src=e['dst'],e['src'];need(dst in rows and src in rows,'no uninitialized read')
            rows[dst]=plus(rows[dst],rows[src],Q(e['coefficient']));changed=[dst]
        elif op in ('line','stage'):
            need(e['field'] in rows,'initialized native input');changed=[e['field']]
        elif op=='current_map':
            name=e['field'];g=records[e['port']]['g'];need(compose(g,g)==IDENTITY,'actual map involution')
            rows[name]=route(g,rows[name]);changed=[name]
        else:need(op=='checkpoint','supported actual opcode')
        if op in FAULT_OPS:
            name=e['dst'] if op=='add' else e['field']
            rows[name]=plus(rows[name],{(f'd{i}',IDENTITY):Q(1)})
        for name in changed:observe(i,name)
    for name,row in rows.items():final[name]={k:str(v) for k,v in norms(row,sites).items()}
    for kind,row in peakrows.items():
        peaks[kind].update(terms=len(row),row_sha256=digest(canon(row)))
    return {'events':len(word),'fault_sites':len(sites),'fault_ops':dict(Counter(op for op,w in sites.values())),
            'changed_field_boundaries':len(trace),'trace_sha256':digest(trace),'peaks':peaks,
            'final':final,'pre_clear_sha256':digest(clears),'pre_clear_count':len(clears)},peakrows,rows

def reverse(word,records,event,field):
    """Separate backward covector traversal; does not call forward or route/plus."""
    adj={field:{IDENTITY:Q(1)}}; result={}
    def accumulate(target,key,c):
        z=target.get(key,Q(0))+c
        if z:target[key]=z
        else:target.pop(key,None)
    for i in range(event,-1,-1):
        e=word[i];op=e['op']
        target=e.get('dst') if op=='add' else e.get('field')
        if op in FAULT_OPS:
            for g,c in adj.get(target,{}).items():accumulate(result,(f'd{i}',g),c)
        if op=='add':
            out=adj.setdefault(e['src'],{})
            for g,c in list(adj.get(e['dst'],{}).items()):accumulate(out,g,Q(e['coefficient'])*c)
        elif op=='current_map':
            out={};h=records[e['port']]['g']
            for g,c in adj.get(target,{}).items():
                # Right composition, independently expressed with binary columns.
                columns=[]
                for x in h:
                    y=0
                    for j,col in enumerate(g):
                        if (x>>j)&1:y^=col
                    columns.append(y)
                accumulate(out,tuple(columns),c)
            adj[target]=out
        elif op=='clear':adj.pop(target,None)
        elif op=='history_boundary':
            for side in ('X','Y'):
                for p in range(112):
                    name=f'{side}{p}'
                    for g,c in adj.pop(name,{}).items():accumulate(result,('i:'+name,g),c)
        elif op in ('private_begin','private_end'):
            for name in e['fields']:need(not adj.get(name),'no dependence on uncleared/discarded dirt')
        else:need(op in ('line','stage','checkpoint'),'reverse opcode coverage')
    for name,row in adj.items():
        need(not row or name.startswith('X'),'only early X inputs survive reverse traversal')
        for g,c in row.items():accumulate(result,('i:E'+name[1:],g),c)
    return result

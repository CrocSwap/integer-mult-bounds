"""Union graph for arbitrary interleaving of the fixed P104 frame paths.

Default: discard every original ADD/COPY and all scalar-access dependencies.
Retain each role's transport/lifetime chain, granting arbitrary linear scalar
resynthesis between equal frames. The larger union may contain incompatible
choices and cycles; disconnection is a conservative certificate.
Jeremy Diviney with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import defaultdict
import hashlib,json,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'p104-native-channel'

def need(ok,why):
    if not ok:raise ValueError(why)

def key(vs):
    out={0}
    for v in vs:out|={x^v for x in tuple(out)}
    return tuple(sorted(out))

def build(remove_descents=True,force_overlap=False,transport_only=True):
    raw=(BASE/'inputs/LOWRANK-WITNESS.json').read_bytes()
    need(hashlib.sha256(raw).hexdigest()=='0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e','pin')
    w=json.loads(raw)
    retained=[i for i,e in enumerate(w['program']) if not transport_only or e[0] not in ('add','copy')]
    program=[w['program'][i] for i in retained];N=len(program)
    last={};anc=[]
    for at,e in enumerate(program):
        regs=e[1:3] if e[0] in ('add','copy') else e[1:2];a=0
        for r in regs:
            if r in last:a |= anc[last[r]]|(1<<last[r])
        anc.append(a)
        for r in regs:last[r]=at
    # node=(role,start_event,end_event,frame); final graph never identifies
    # separate private C lifetimes.
    nodes=[];active={};inputs={};outputs={};edges=[];removed=[]
    def new(r,start,f):
        n=len(nodes);nodes.append([r,start,N,f]);active[r]=n;return n
    for r,f in w['initial_frames'].items():inputs[r]=new(r,-1,key(f))
    for at,e in enumerate(program):
        op=e[0];r=e[1]
        if op=='zero':
            need(r not in active,'private lifetime');new(r,at,key(e[2]));continue
        old=active[r];nodes[old][2]=at;oldframe=nodes[old][3]
        if op=='erase':del active[r];continue
        f=key(e[3]) if op=='transport' else oldframe
        if op=='transport':need(oldframe==key(e[2]),'source frame')
        src=active[e[2]] if op in ('add','copy') else None
        dst=new(r,at,f)
        if op=='transport' and r=='C' and len(f)<len(oldframe):
            removed.append([at,old,dst,e[4]])
            if not remove_descents:edges.append((old,dst))
        else:edges.append((old,dst))
        if src is not None:edges.append((src,dst))
    outputs=dict(active)
    adjacency=[0]*len(nodes)
    for a,b in edges:adjacency[a]|=1<<b
    def before(a,b):
        if a==-1 or b==N:return True
        if a==N or b==-1:return False
        return a==b or bool(anc[b]&(1<<a))
    groups=defaultdict(list)
    for i,(_,_,_,f) in enumerate(nodes):groups[f].append(i)
    extra=0
    for ids in groups.values():
        for uindex,u in enumerate(ids):
            _,us,ue,_=nodes[u]
            for v in ids[uindex+1:]:
                if nodes[u][0]==nodes[v][0]:continue
                _,vs,ve,_=nodes[v]
                if not force_overlap and (before(ue,vs) or before(ve,us)):continue
                adjacency[u]|=1<<v;adjacency[v]|=1<<u;extra+=2
    starts=sum(1<<n for r,n in inputs.items() if r.startswith('X'))
    seen=starts;pending=starts
    while pending:
        bit=pending&-pending;pending^=bit;u=bit.bit_length()-1
        added=adjacency[u]&~seen;seen|=added;pending|=added
    reached=[r for r,n in outputs.items() if r.startswith('Y') and seen&(1<<n)]
    return {'nodes':nodes,'input_nodes':inputs,'output_nodes':outputs,'removed_edges':removed,
            'causal_edges':len(edges),'potential_common_frame_edges':extra,
            'reachable_mask_hex':hex(seen),'reached_targets':reached,
            'source_witness_sha256':hashlib.sha256(raw).hexdigest(), 'adjacency':adjacency,
            'retained_event_indices':retained,'transport_only':transport_only}

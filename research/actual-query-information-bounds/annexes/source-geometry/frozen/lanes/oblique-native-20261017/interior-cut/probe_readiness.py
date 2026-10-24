#!/usr/bin/env python3
"""Check row readiness inside each pinned clean native word."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
CORE = LANES / 'new-core-transfer-20261017'
PIN = 'a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa'
A = [0, 7, 20, 27, 36, 46, 57, 111]

def need(test, label):
    if not test:
        raise ValueError(label)

spec = importlib.util.spec_from_file_location('raw_transfer', CORE / 'emit_raw_selected.py')
e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)
payload = gzip.decompress((CORE / 'CLEAN-J-PROGRAMS.json.gz').read_bytes())
need(sha256(payload).hexdigest() == PIN, 'Pinned clean core')
core = json.loads(payload)
r = [{int(p): F(c) for p, c in row.items()} for row in core['R']]
D = {p: {a: sum(row.get(p, 0)*row.get(a, 0) for row in r)/4 for a in A} for p in range(112) if p not in A}
D = {p: {a: c for a,c in row.items() if c} for p,row in D.items()}
B = {a: {p: D[p][a] for p in D if a in D[p]} for a in A}


def replay(program, state, word, backward=False, observer=None):
    state = deepcopy(state)
    n = len(word['start'])
    frames = {p: f for p,f in enumerate(word['start'])}
    frames.update({n+p:0 for p in range(8)})
    zero = set()
    def slot(x):
        if x[0] == 'L': return x[1]
        if x[0] == 'C': return n+x[1]
        need(x[0] == 'Z', 'Slot token')
        return ('Z',x[1])
    if observer: observer(-1, None, state, frames)
    for pos,event in enumerate(program):
        tag = event[0]
        if tag == 'scalar':
            gate,f = event[1:]
            t,op = slot(gate[1]),gate[0]
            if op == 'clear':
                state[t],frames[t] = {},f
            else:
                need(frames[t] == f, ('Scalar target frame',pos))
                if op == 'scale':
                    c=F(*gate[2:4]); state[t]={k:c*v for k,v in state[t].items() if c*v}
                else:
                    s=slot(gate[2]); need(t!=s and frames[s]==f, ('Scalar source frame',pos))
                    if op=='copy': state[t]=dict(state[s])
                    else:
                        need(op=='add','Scalar operation'); e.add(state[t],state[s],F(*gate[3:5]))
        elif tag=='climb':
            t,old,new,rank=event[2:6]
            need(frames[t]==old and len(word['frames'][new])-len(word['frames'][old])==rank,('Climb',pos))
            frames[t]=new
        elif tag=='warp':
            t,op,old,new=slot(event[1]),event[2],event[3],event[4]
            need(frames[t]==old,('Warp frame',pos));frames[t]=new
            state[t]=e.operator(state[t],('dual_K' if backward else 'K',abs(op)),1 if op>0 else -1)
        elif tag=='zero_buffer':
            t=('Z',event[2])
            if event[1]=='alloc':
                need(t not in zero,'Private allocation');state[t],frames[t]={},1;zero.add(t)
            else:
                need(t in zero and not state[t],'Private return');zero.remove(t)
        else: need(tag in ('phase','adapter','residual_adapter'),'Event tag')
        if observer: observer(pos,event,state,frames)
    need(not zero,'No live private buffer')
    need([frames[p] for p in range(n)]==word['final'],'Final live frames')
    need(all(frames[n+p]==0 for p in range(8)),'Final owned frames')
    return state


def setup(word, backward):
    n=len(word['start']);identity={p:{(p,()):F(1)} for p in range(n+8)}
    physical=deepcopy(identity)
    for p in range(112):physical[p]=e.line(physical[p],p,1)
    if backward:
        for a in A:
            for p,c in B[a].items():e.add(physical[a],physical[112+p],-c)
    else:
        for p in D:
            for a,c in D[p].items():e.add(physical[112+p],physical[a],c)
    for a in A:physical[a],physical[112+a]=physical[112+a],physical[a]
    for p in range(112):physical[p]=e.line(physical[p],p,-1)
    return physical


def run(provider, item, direction):
    backward=direction=='backward';word=item['canonical'];program=item['programs'][direction]
    start=setup(word,backward);final=replay(program,start,word,backward)
    watched=A+[112+a for a in A]
    periods={p:[] for p in watched};active={}
    phases=[];last_climbs={p:None for p in range(112,224)}
    exact_rows=[]
    def observe(pos,event,state,frames):
        if event and event[0]=='climb' and 112<=event[2]<224:last_climbs[event[2]]=pos
        for p in watched:
            good=state[p]==final[p]
            if good and p not in active:
                active[p]=[pos,frames[p],sum(frames[112+u]==0 for u in range(112) if u not in A),sum(frames[112+u]==word['final'][112+u] for u in range(112) if u not in A)]
            elif not good and p in active:
                periods[p].append(active.pop(p)+[pos-1])
        if event and event[0]=='phase':
            phases.append({'position':pos,'name':event[1],'selected_X_frames':[frames[a] for a in A],'selected_Y_frames':[frames[112+a] for a in A],'Y_frame_counts':dict(Counter(frames[p] for p in range(112,224))), 'ready_fields':[p for p in watched if state[p]==final[p]]})
        if event and event[0]=='climb' and 112<=event[2]<224:
            t=event[2]
            exact_rows.append({'position':pos,'target':t,'rank':event[5],'from':event[3],'to':event[4], 'ready_selected_X':[a for a in A if state[a]==final[a]],'ready_selected_Y':[a for a in A if state[112+a]==final[112+a]]})
    actual=replay(program,start,word,backward,observe)
    need(actual==final,'Repeat replay')
    for p,v in active.items():periods[p].append(v+[len(program)-1])
    result={'phases':phases,'selected_final_value_intervals':periods,'last_Y_climbs':last_climbs,'Y_climb_readiness':exact_rows,'all_input_columns':len(word['start'])+8}
    print(provider,direction,'stable',[(p,periods[p][-1][0],periods[p][-1][1:4]) for p in watched],flush=True)
    return result

if __name__=='__main__':
    out={'schema':'native-interior-row-readiness-v1','source_payload_sha256':PIN,'providers':{}}
    for provider,item in core['providers'].items():
        out['providers'][provider]={direction:run(provider,item,direction) for direction in ('forward','backward')}
    out['checker_sha256']=sha256(Path(__file__).read_bytes()).hexdigest()
    (HERE/'READINESS.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')

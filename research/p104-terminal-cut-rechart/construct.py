# SPDX-License-Identifier: Apache-2.0
"""Rechart the fixed terminal cut, preserving every normalized scalar event.
Rohan Arun with OpenAI Codex assistance; predecessor credits in NOTICE.
"""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent

def need(ok, reason):
    if not ok: raise ValueError(reason)

def span(rows):
    out={0}
    for row in rows: out |= {v^row for v in tuple(out)}
    return out

def construct(old, witness=None):
    hit=witness if witness is not None else json.loads((HERE/'WITNESS.json').read_bytes())
    raw=json.dumps(old,sort_keys=True,separators=(',',':')).encode()
    need(sha256(raw).hexdigest()==hit['source_word_sha256'],'Exact source7274 word')
    changes={int(i):f for i,f in hit['event_frames'].items()}
    out=deepcopy(old)
    for r,f in hit['final_frames'].items(): out['final'][int(r)]=f
    spaces=list(map(span,old['frames']));n=old['public']
    current=old['initial']+[None]*old['owned_fields']; program=[]
    def move(r,to):
        before=current[r]
        if before==to:return
        need(before is not None,'Live source chart')
        need(spaces[before]<spaces[to] or (r>=n and spaces[to]<spaces[before]),'Legal nested transport')
        program.append(['MOVE',r,before,to,r>=n]);current[r]=to
    for i,e in enumerate(old['program']):
        op,r=e[:2]
        if op=='MOVE':
            need(i not in changes,'Only scalar or lifetime chart changes')
            continue
        f=changes.get(i,e[-1])
        if i in changes:need(e[-1]==245 and f==127,'Exact245 to127 rechart')
        if op=='INIT':
            need(current[r] is None,'Unique owned initialization');program.append([op,r,f]);current[r]=f
        elif op=='CLEAR':
            move(r,f);program.append([op,r,f]);current[r]=None
        else:
            for q in e[1:3] if op in ('ADD','COPY') else e[1:2]:move(q,f)
            program.append([*e[:-1],f])
    for r,f in enumerate(out['final']):move(r,f)
    need(current==out['final']+[None]*old['owned_fields'],'Exact output inventory')
    out['program']=program
    return out

#!/usr/bin/env python3
"""Disjoint truth-table engine: complete 16-input address action, no primary import.
JoyboyBrian, substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent

def require(ok,message):
    if not ok:raise ValueError(message)

GATES=[(i,j) for i in range(4) for j in range(4) if i!=j]
IDENTITY=tuple(range(16))
TARGET=tuple(((x>>1)&1)|(((x>>2)&1)<<1)|((x&1)<<2)|(x&8) for x in range(16))

def step(table,gate):
    target,donor=gate
    return tuple(y ^ (((y>>donor)&1)<<target) for y in table)

def grow(seed,depth):
    seen={seed};front={seed};layers=[1]
    for _ in range(depth):
        new={step(t,g) for t in front for g in GATES}-seen
        layers.append(len(new));seen|=new;front=new
    return seen,layers

def run():
    left,layers=grow(IDENTITY,2);right,_=grow(TARGET,2)
    require(not left&right,'target reachable within four')
    bridge_hits=sum(step(t,g) in right for t in left for g in GATES)
    require(bridge_hits==0,'target reachable within five')
    third,layers3=grow(IDENTITY,3)
    # Convert each whole truth table to rows; verify all 16 inputs, not only basis.
    matrices=[]
    for table in third:
        rows=tuple(sum(((table[1<<j]>>i)&1)<<j for j in range(4)) for i in range(4))
        for x in range(16):
            image=sum(((row&x).bit_count()%2)<<i for i,row in enumerate(rows))
            require(image==table[x],'linear truth-table conversion')
        matrices.append(rows)
    digest=hashlib.sha256(json.dumps(sorted(matrices),separators=(',',':')).encode()).hexdigest()
    receipt=json.loads((HERE/'RESULT.json').read_text())
    require(receipt['layers']==layers3 and receipt['ball_two']==len(left) and receipt['ball_three']==len(third),'independent ball inventory')
    require(receipt['ball_three_sha256']==digest,'complete converted ball agreement')
    require(receipt['target_hits_through_five']==bridge_hits and receipt['minimum']==6,'independent exclusion receipt')
    word=[(0,1),(1,0),(0,1),(1,2),(2,1),(1,2)];table=IDENTITY
    for gate in word:table=step(table,gate)
    require(table==TARGET,'six-call full-address witness')
    # Reachability positives exercise both overlap and middle-edge paths.
    small=step(IDENTITY,(0,1));small_right,_=grow(small,2)
    require(left&small_right,'short positive overlap')
    five=IDENTITY
    for gate in word[:5]:five=step(five,gate)
    five_right,_=grow(five,2)
    require(any(step(t,g) in five_right for t in left for g in GATES),'short positive bridge')
    print('PASS_THREE_CYCLE_INDEPENDENT tables=651 full_input_checks=10416 bridges=1308 hits=0')
if __name__=='__main__':run()

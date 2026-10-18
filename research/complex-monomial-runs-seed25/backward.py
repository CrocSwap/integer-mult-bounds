"""Independent reverse-label enumeration and literal matrix witness replay.
No finite.py or joint.py imports. Apache-2.0, Codex assistance for @woklerx.
"""
from itertools import product
from collections import Counter

def need(ok,msg):
    if not ok:raise ValueError(msg)

def solve(permutation,clean=False):
    n=len(permutation);width=n+1;needed=set(range(1,n+1))
    states={s for s in product(range(n+2),repeat=width)if needed.issubset(s)}
    target=tuple(permutation)+(0,);distance={target:0};front={target};levels=[1]
    while front:
        next_front=set()
        for state in front:
            for d in range(width):
                # A previous COPY into d requires the current label in some
                # other coordinate; a previous CLEAR needs output zero.
                new=state[d]
                if new and not any(state[s]==new for s in range(width)if s!=d):continue
                for old in range(n+2):
                    if old==new:continue
                    prior=state[:d]+(old,)+state[d+1:]
                    if prior in states and prior not in distance:next_front.add(prior)
        if not next_front:break
        for state in next_front:distance[state]=len(levels)
        levels.append(len(next_front));front=next_front
    initial=tuple(range(1,n+1))+(0 if clean else n+1,)
    return {'admissible_states':len(states),'states_reaching_goal':len(distance),
       'backward_layers':levels,'minimum':distance[initial]}

def replay(permutation,word,clean=False):
    n=len(permutation);width=n+1
    values=[[int(i==j)for j in range(width)]for i in range(width)]
    if clean:values[-1]=[0]*width
    for instruction in word:
        tag,d=instruction[:2]
        need(type(d)is int and 0<=d<width,'target')
        if tag in('copy','add','subtract'):
            s=instruction[2];need(type(s)is int and 0<=s<width and s!=d,'distinct source')
        if tag=='clear':values[d]=[0]*width
        elif tag=='copy':values[d]=values[instruction[2]][:]
        elif tag=='negate':values[d]=[-v for v in values[d]]
        elif tag in('double','halve'):
            need(not any(values[d]),'nonunit monomial coefficient');values[d]=[0]*width
        elif tag in('add','subtract'):
            c=1 if tag=='add'else-1;values[d]=[a+c*b for a,b in zip(values[d],values[instruction[2]])]
        else:raise ValueError('primitive')
        need(sum(v!=0 for v in values[d])<=1 and all(abs(v)<=1 for v in values[d]),'prefix monomial restriction')
    expected=[[int(j==source-1)for j in range(width)]for source in permutation]+[[0]*width]
    need(values==expected,'signed arbitrary-input endpoint')
    return True

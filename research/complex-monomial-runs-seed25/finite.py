"""Finite absolute-label quotient and exact forward shortest paths.
Apache-2.0; substantial OpenAI Codex assistance for @woklerx.
"""
from collections import deque,Counter

def solve(permutation,clean=False):
    n=len(permutation);start=tuple(range(1,n+1))+(0 if clean else n+1,)
    goal=tuple(permutation)+(0,);critical=set(range(1,n+1))
    distance={start:0};parent={};queue=deque([start]);edges=0
    while queue:
        state=queue.popleft()
        for d in range(n+1):
            for s in range(-1,n+1):
                if s==d:continue
                value=0 if s<0 else state[s]
                if state[d]==value:continue
                nxt=state[:d]+(value,)+state[d+1:]
                if not critical.issubset(nxt):continue
                edges+=1
                if nxt not in distance:
                    distance[nxt]=distance[state]+1;parent[nxt]=(state,['clear',d]if s<0 else['copy',d,s]);queue.append(nxt)
    word=[];cursor=goal
    while cursor!=start:cursor,op=parent[cursor];word.append(op)
    word.reverse()
    return {'data':n,'permutation':list(permutation),'clean_work_on_entry':clean,'minimum':distance[goal],
       'reachable_states':len(distance),'primitive_edges':edges,
       'distance_histogram':{str(k):v for k,v in sorted(Counter(distance.values()).items())},'witness':word}

#!/usr/bin/env python3
"""New deterministic exact frame endpoints and legal late handoff discovery.

Chafik Boukhalfa with OpenAI Codex assistance. Apache-2.0.
Builds on PR144 binary frame/word contract and PR157 physical reuse theorem.
Numerical excess weights only select witnesses; exact containment, histogram
and scalar checks must be independently replayed on the selected candidate.
"""
from collections import defaultdict,deque,Counter
from functools import lru_cache
import math
from paired_cube.frames import basis,perp,contained

@lru_cache(maxsize=300000)
def join(A,B):
    if contained(A,B):return B
    if contained(B,A):return A
    return basis(A+B)
@lru_cache(maxsize=300000)
def meet(A,B,h):
    if contained(A,B):return A
    if contained(B,A):return B
    return perp(join(perp(A,h),perp(B,h)),h)

class Physical:
    def __init__(self,g,w,word,row):
        self.g,self.w,self.word,self.row=g,w,word,row;self.h=g['h'];self.R=row['R'];self.v=g['v'];h=self.h
        self.full=basis(1<<i for i in range(h));self.ops=[tuple(op) for op in word['ops']]
        args=[None]+[None if a is None else [x+1 for x in a] for a in g['args']];self.spans=[()]*len(args)
        for x in range(1,len(args)):
            self.spans[x]=(g['inputs'][x-1],) if args[x] is None else join(self.spans[args[x][0]],self.spans[args[x][1]])
        self.frames=[perp(tuple(w['annihilators'][x]),h) for _,_,x in self.ops];self.original=self.frames[:]
        self.start=[()]*self.R;self.end=[self.full]*self.R
        self.sources={int(x):s for x,s in word['sources'].items()}
        for x,s in self.sources.items():self.start[s]=(g['inputs'][x-1],)
        self.gauge={z['role']:perp(tuple(z['annihilator']),h) for z in word['selected']}
        for s,F in self.gauge.items():self.start[s]=F
        self.roots=set(word['rootroles'])
        for r,s in zip(g['roots'],word['rootroles']):
            self.end[s]=self.spans[r['node']+1] if r['kind']=='center' else perp(basis(g['inputs'][t] for t in r['targets']),h)
        self.role_ops=[[] for _ in range(self.R)]
        self.prev=[];last=[None]*self.R
        for i,(a,b,x) in enumerate(self.ops):
            self.prev.append([last[a],last[b]])
            for s in (a,b):last[s]=i;self.role_ops[s].append(i)
        self.next=[None]*len(self.ops);nxt=[None]*self.R
        for i in range(len(self.ops)-1,-1,-1):
            a,b,x=self.ops[i];self.next[i]=[nxt[a],nxt[b]];nxt[a]=nxt[b]=i
        phase=set(word['phase1']);self.order=list(word['phase1'])+[i for i in range(len(self.ops)) if i not in phase]
        self.order.sort(key=lambda i:(i not in phase,i));self.position={i:j for j,i in enumerate(self.order)};self.phase=phase
        import os
        _a=float(os.environ.get('PHI_ALPHA','0.00057'));self.rng=__import__('random').Random(int(os.environ.get('DESCENT_SEED','0')))
        self.phi=[0.]+[t*math.expm1(_a*math.log(3*h/t))/_a for t in range(1,3*h+1)]

    def neighbors(self,i):
        a,b,_=self.ops[i]
        P=[self.frames[j] if j is not None else self.start[s] for s,j in zip((a,b),self.prev[i])]
        N=[self.frames[j] if j is not None else self.end[s] for s,j in zip((a,b),self.next[i])]
        return P,N

    def descend(self,rounds=4,lower_only=False):
        changes=[]
        for rnd in range(rounds):
            changed=0;gain=0.
            order=list(range(len(self.ops))) if rnd%2==0 else list(range(len(self.ops)-1,-1,-1))
            if __import__('os').environ.get('DESCENT_SEED'):self.rng.shuffle(order)
            for i in order:
                P,N=self.neighbors(i);old=self.frames[i];x=self.ops[i][2]
                L=join(join(P[0],P[1]),self.spans[x]);assert contained(L,old)
                U=meet(N[0],N[1],self.h);assert contained(old,U)
                def cost(r):return sum(self.phi[r-len(F)] for F in P)+sum(self.phi[len(F)-r] for F in N)
                choices=[L] if lower_only else [L,U]
                best=min(choices,key=lambda F:(cost(len(F)),len(F),F))
                delta=cost(len(old))-cost(len(best))
                if best!=old and (lower_only or delta>1e-10 or abs(delta)<=1e-10 and len(best)<len(old)):
                    self.frames[i]=best;changed+=1;gain+=delta
            changes.append(dict(round=rnd,changed=changed,numerical_excess_gain=gain));print('descent',changes[-1],flush=True)
            if not changed:break
        for i in range(len(self.ops)):
            P,N=self.neighbors(i);assert contained(self.spans[self.ops[i][2]],self.frames[i]);assert all(contained(F,self.frames[i]) for F in P);assert all(contained(self.frames[i],F) for F in N)
        return changes

    def pairs(self):
        donors=[s for s in range(self.R) if s not in self.gauge and s not in self.roots and self.role_ops[s]]
        byframe=defaultdict(list)
        for s in donors:byframe[self.frames[self.role_ops[s][-1]]].append(s)
        recipients=sorted(self.gauge,key=lambda b:(self.position[self.role_ops[b][0]],b))
        groups={};adj=[];gains={}
        for b in recipients:
            F=self.gauge[b]
            if F not in groups:
                groups[F]=[s for D,ss in byframe.items() if contained(D,F) for s in ss]
            time=self.position[self.role_ops[b][0]]
            row=[s for s in groups[F] if self.position[self.role_ops[s][-1]]<time]
            def gain(s):
                dd=len(self.frames[self.role_ops[s][-1]]);f=len(F)
                return 3*self.phi[self.h-dd]+self.phi[3*f]-3*self.phi[f-dd]
            row.sort(key=lambda s:(-gain(s),self.position[self.role_ops[s][-1]],s));adj.append(row)
        L=len(recipients);ml=[-1]*L;mr={};dist=[0]*L
        def bfs():
            q=deque();found=False
            for u in range(L):
                dist[u]=0 if ml[u]<0 else -1
                if ml[u]<0:q.append(u)
            while q:
                u=q.popleft()
                for d in adj[u]:
                    z=mr.get(d,-1)
                    if z<0:found=True
                    elif dist[z]<0:dist[z]=dist[u]+1;q.append(z)
            return found
        def dfs(u):
            for d in adj[u]:
                z=mr.get(d,-1)
                if z<0 or dist[z]==dist[u]+1 and dfs(z):ml[u]=d;mr[d]=u;return True
            dist[u]=-1;return False
        while bfs():
            for u in range(L):
                if ml[u]<0:dfs(u)
        result=[]
        for j,d in enumerate(ml):
            if d>=0:
                b=recipients[j];first=self.role_ops[b][0]
                result.append([d,b,None if self.role_ops[d][-1] in self.phase else first])
        return result,dict(donors=len(donors),recipients=L,edges=sum(map(len,adj)),matched=len(result),gauge_frames=len(groups),donor_frames=len(byframe))

    def changed(self):return [[i,F] for i,F in enumerate(self.frames) if F!=self.original[i]]

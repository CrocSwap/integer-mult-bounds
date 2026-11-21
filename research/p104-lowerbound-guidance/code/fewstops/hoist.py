# FEWSTOPS hoist scheduler: execute any ready (block-DAG) event whose participants already share a chart (zero move);
# otherwise run the earliest pending event e* at its ORIGINAL chart (eager raise). Invariant cur[r] <= orig chart of
# r's earliest pending event => no deadlock, and every register visits a SUBSET of its original charts (never worse).
from ls import *
from sched import build_blocks, regs_of
import heapq, sys, pickle
def hoist(Win):
    setup(Win)
    P0=[e for e in Win['program'] if not (e[0]=='MOVE' and e[1]<n)]
    # original chart of each event for public participants
    cur=list(Win['initial']); G0=[None]*len(P0); j=0
    for e in Win['program']:
        if e[0]=='MOVE' and e[1]<n: cur[e[1]]=e[3]; continue
        rs=[r for r in regs_of(e) if r<n]
        if rs: G0[j]=cur[rs[0]]
        j+=1
    blocks,bidx=build_blocks(P0)
    curb={r:0 for r in blocks}; rem={r:len(B[0]) for r,B in blocks.items()}
    cid=list(Win['initial']); cm=[SM_[x] for x in cid]
    done=[False]*len(P0)
    def ready(i): return all(bidx[(i,r)]==curb[r] for r in regs_of(P0[i]))
    def zero(i):
        e=P0[i]; rs=[r for r in regs_of(e) if r<n]
        if e[0]=='ADD':
            if e[1]>=n or e[2]>=n: return all(cid[r]==e[4] for r in rs)
            return cid[e[1]]==cid[e[2]]
        return True
    rdy=set(i for i in range(len(P0)) if ready(i))
    heap=[i for i in rdy if zero(i)]; heapq.heapify(heap)
    out=[]; estar=0; ndone=0; hoisted=0
    def emit(i):
        e=P0[i]; op=e[0]
        if op=='SCALE' and e[1]<n: out.append(['SCALE',e[1],e[2],cid[e[1]]])
        elif op=='ADD' and e[1]<n and e[2]<n: out.append(['ADD',e[1],e[2],e[3],cid[e[1]]])
        else: out.append(e)
    def finish(i):
        nonlocal ndone
        done[i]=True; rdy.discard(i); ndone+=1
        newr=[]
        for r in regs_of(P0[i]):
            rem[r]-=1
            if rem[r]==0 and curb[r]+1<len(blocks[r]):
                curb[r]+=1; rem[r]=len(blocks[r][curb[r]])
                for k in blocks[r][curb[r]]:
                    if ready(k): rdy.add(k); newr.append(k)
        for k in newr:
            if zero(k): heapq.heappush(heap,k)
    while ndone<len(P0):
        moved=False
        while heap:
            i=heapq.heappop(heap)
            if done[i] or not zero(i): continue
            if i!=estar: hoisted+=1
            emit(i); finish(i)
        if ndone==len(P0): break
        while done[estar]: estar+=1
        i=estar; e=P0[i]
        assert i in rdy, 'e* not ready?!'
        g=G0[i]; changed=[]
        for r in regs_of(e):
            if r<n and cid[r]!=g:
                assert cm[r]&SM_[g]==cm[r], 'invariant broken'
                out.append(['MOVE',r,cid[r],g,False]); cid[r]=g; cm[r]=SM_[g]; changed.append(r)
        emit(i); finish(i)
        for r in changed:
            for k in blocks[r][curb[r]]:
                if not done[k] and k in rdy and zero(k): heapq.heappush(heap,k)
            # partners' ready events involving r
        # registers' ready events where partner == changed register are covered since k in blocks[r]
    for r in range(n):
        if cid[r]!=Win['final'][r]: out.append(['MOVE',r,cid[r],Win['final'][r],False])
    W2=dict(Win); W2['program']=out
    print('hoisted events',hoisted)
    return W2
if __name__=='__main__':
    from check import check
    W2=hoist(W); pickle.dump(W2,open('W_H.pkl','wb'))
    print(check(W2,'hoist'))

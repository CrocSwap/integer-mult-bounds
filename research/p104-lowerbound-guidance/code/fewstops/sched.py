# FEWSTOPS: dependency-respecting re-scheduler. Events commute when they share a register only as two intakes
# (ADD r+=..) or two outputs (reads of r). Any linear extension of the block DAG gives identical rows [P].
# Public charts are re-chosen: gate chart = join of participants' current charts (lazy ascent); owned events pinned.
from ls import *
from lub import join
from collections import defaultdict
import heapq, sys
def build_blocks(P2):
    N=n+W['owned_fields']
    role=defaultdict(list)  # r -> list of (event, role)
    for i,e in enumerate(P2):
        op=e[0]
        if op in ('ADD','COPY'):
            role[e[1]].append((i,'in')); role[e[2]].append((i,'out'))
        else:
            role[e[1]].append((i,'bar'))
    blocks={}; bidx={}
    for r,L in role.items():
        B=[]; prev=None
        for i,ro in L:
            if ro=='bar' or ro!=prev: B.append([]); 
            B[-1].append(i); bidx[(i,r)]=len(B)-1; prev=ro
        blocks[r]=B
    return blocks,bidx
def regs_of(e):
    return [e[1],e[2]] if e[0] in ('ADD','COPY') else [e[1]]
def schedule(Win, Uup, prio='climb'):
    P2=Win['program']; setup(Win)
    blocks,bidx=build_blocks(P2)
    left={r:[len(B[0]) if B else 0] for r,B in blocks.items()}
    curb={r:0 for r in blocks}; rem={r:len(blocks[r][0]) for r in blocks}
    cur=[SM_[x] for x in Win['initial']]
    # Uup[i] = static upper bound for public participants of event i (from DAG); per-register remaining-U counters
    remU=defaultdict(lambda: defaultdict(int))
    for i,e in enumerate(P2):
        for r in regs_of(e):
            if r<n and Uup[i] is not None: remU[r][Uup[i]]+=1
    fin=[SM_[x] for x in Win['final']]
    def ubound(r):
        m=fin[r]
        for k,v in remU[r].items():
            if v: m&=k
        return m
    def ready(i):
        return all(bidx[(i,r)]==curb[r] for r in regs_of(P2[i]))
    def need(i):
        e=P2[i]; op=e[0]
        if op in ('ADD','COPY'):
            d,s_=e[1],e[2]
            if d<n and s_<n: return join(cur[d],cur[s_])
            if d<n or s_<n: return SM_[e[4]]
        return None
    done=[False]*len(P2); out=[]; frames=[list(b) for b in Win['frames']]; m2i={}
    for k,m in enumerate(SM_): m2i.setdefault(m,k)
    def fid(m):
        if m not in m2i: m2i[m]=len(frames); frames.append(basis_of(m)); SM_.append(m)
        return m2i[m]
    curid=list(Win['initial'])
    readyset=set(i for i in range(len(P2)) if ready(i))
    ndone=0
    while ndone<len(P2):
        best=None; bk=None
        zero=[]
        for i in readyset:
            g=need(i); e=P2[i]
            pubs=[r for r in regs_of(e) if r<n]
            if g is None or all(cur[r]==g for r in pubs):
                zero.append(i)
        if zero:
            pick=sorted(zero)
        else:
            cands=[]
            for i in readyset:
                g=need(i); e=P2[i]; pubs=[r for r in regs_of(e) if r<n]
                if any(cur[r]&g!=cur[r] or g&ubound(r)!=g for r in pubs): continue
                climb=sum(dm(g)-dm(cur[r]) for r in pubs)
                cands.append((climb if prio=='climb' else 0, i))
            if not cands: raise RuntimeError('deadlock at %d done'%ndone)
            pick=[min(cands)[1]]
        newready=[]
        for i in pick:
            if i not in readyset: continue
            e=P2[i]; g=need(i)
            pubs=[r for r in regs_of(e) if r<n]
            if g is not None and not all(cur[r]==g for r in pubs):
                if not all(cur[r]==g for r in pubs) and pick is not None and len(pick)>1: continue
                for r in pubs:
                    if cur[r]!=g:
                        nid=fid(g); out.append(['MOVE',r,curid[r],nid,False]); cur[r]=g; curid[r]=nid
            # emit
            op=e[0]
            if op=='MOVE':
                out.append(e)
            elif op in('INIT','CLEAR'): out.append(e)
            elif op=='SCALE': out.append(['SCALE',e[1],e[2],curid[e[1]] if e[1]<n else e[3]])
            else:
                fr=e[4] if (e[1]>=n or e[2]>=n) else curid[e[1]]
                out.append([op,e[1],e[2],e[3],fr])
            readyset.discard(i); done[i]=True; ndone+=1
            for r in regs_of(e):
                if r<n and Uup[i] is not None: remU[r][Uup[i]]-=1
                rem[r]-=1
                if rem[r]==0 and curb[r]+1<len(blocks[r]):
                    curb[r]+=1; rem[r]=len(blocks[r][curb[r]])
                    for j in blocks[r][curb[r]]:
                        if ready(j): readyset.add(j)
        if ndone%20000<len(pick): print('done',ndone,'ready',len(readyset)); sys.stdout.flush()
    for r in range(n):
        if curid[r]!=Win['final'][r]:
            out.append(['MOVE',r,curid[r],Win['final'][r],False])
    W3=dict(Win); W3['program']=out; W3['frames']=frames
    return W3
def upper_bounds(P2):
    # static DAG upper bound for each event's public participants: meet of final charts and pinned charts of DAG successors
    setup(W)
    blocks,bidx=build_blocks(P2)
    U=[None]*len(P2)
    fin=[SM_[x] for x in W['final']]
    # blockU[r][b] = meet of U of events in blocks >= b of r  (computed in reverse event order)
    bu={r:[None]*len(B) for r,B in blocks.items()}
    for i in range(len(P2)-1,-1,-1):
        e=P2[i]; op=e[0]; rs=regs_of(e)
        def after(r):
            b=bidx[(i,r)]+1
            if r>=n: return None
            m=fin[r]
            if b<len(blocks[r]) and bu[r][b] is not None: m&=bu[r][b]
            return m
        if op in('ADD','COPY'):
            d,s_=e[1],e[2]
            if d<n and s_<n: u=after(d)&after(s_)
            elif d<n or s_<n: u=SM_[e[4]]
            else: u=None
        elif op=='SCALE' and e[1]<n: u=after(e[1])
        else: u=None
        U[i]=u
        for r in rs:
            if r<n:
                b=bidx[(i,r)]; cu=bu[r][b]
                x=u if u is not None else after(r)
                # block meet includes this event's own bound and later blocks
                bu[r][b]= x if cu is None else (cu & x)
                if b+1<len(blocks[r]) and bu[r][b+1] is not None: bu[r][b]&=bu[r][b+1]
    return U
if __name__=='__main__':
    from check import check
    import pickle
    W0=dict(W); W0['program']=[e for e in P if not (e[0]=='MOVE' and e[1]<n)]
    U=upper_bounds(W0['program'])
    W2=schedule(W0,U)
    pickle.dump(W2,open('W_S.pkl','wb'))
    print(check(W2,'sched-climb'))

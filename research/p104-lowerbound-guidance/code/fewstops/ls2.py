# pair-meeting moves: set two adjacent meetings (sharing a register as consecutive stays) to one chart G.
from meet import *
from lub import join
from ls import rebuild
import pickle, sys
def run(W2, rounds=10):
    for rd in range(rounds):
        st,members,pinev=meetings(W2)
        mid={}
        for m,Lm in members.items():
            for x in Lm: mid[x]=m
        init=[SM_[x] for x in W2['initial']]; fin=[SM_[x] for x in W2['final']]
        chart={x:st[x[0]][x[1]][0] for x in mid}
        mch={m:chart[Lm[0]] for m,Lm in members.items()}
        fixed=set(pinev)
        for m,Lm in members.items():
            # meetings containing a first stay at init chart or last stay at final are not fixed (move inserts a jump)
            pass
        def pq(r,k):
            p=mch[mid[(r,k-1)]] if k>0 else init[r]; q=mch[mid[(r,k+1)]] if k+1<len(st[r]) else fin[r]; return p,q
        def cost_set(ms, assign):
            # cost of all members of meetings in ms under assign (dict meeting->chart), counting jumps p->G and G->q per member,
            # but avoid double counting the jump between two meetings in ms on the same register
            regs={}
            for m in ms:
                for (r,k) in members[m]: regs.setdefault(r,set()).add(k)
            tot=0.0
            for r,ks in regs.items():
                lo=min(ks); hi=max(ks)
                seq=[]
                for k in range(lo-1,hi+2):
                    if k<0: seq.append(init[r])
                    elif k>=len(st[r]): seq.append(fin[r])
                    else:
                        mm=mid[(r,k)]; seq.append(assign.get(mm,mch[mm]))
                for a,b in zip(seq,seq[1:]):
                    if a&b!=a: return None
                    tot+=f(dm(b)-dm(a))
            return tot
        gain=0; nchg=0; touched=set()
        adj=set()
        for r in range(n):
            for k in range(len(st[r])-1):
                a,b=mid[(r,k)],mid[(r,k+1)]
                if a!=b: adj.add((a,b))
        for a,b in sorted(adj, key=lambda t:-(len(members[t[0]])+len(members[t[1]]))):
            if a in touched or b in touched: continue
            if a in fixed and b in fixed: continue
            ms=[a,b]
            base=cost_set(ms,{})
            cands=set()
            for m in ms:
                for (r,k) in members[m]:
                    p,q=pq(r,k); cands.add(p); cands.add(q)
            cands.add(mch[a]); cands.add(mch[b])
            best=(1e-12,None)
            for G in cands:
                if a in fixed and G!=mch[a]: continue
                if b in fixed and G!=mch[b]: continue
                c=cost_set(ms,{a:G,b:G})
                if c is not None and base-c>best[0]: best=(base-c,G)
            # also single moves
            for m in ms:
                if m in fixed: continue
                for G in cands:
                    c=cost_set(ms,{m:G})
                    if c is not None and base-c>best[0]: best=(base-c,('one',m,G))
            if best[1] is not None:
                if isinstance(best[1],tuple): mch[best[1][1]]=best[1][2]
                else: mch[a]=best[1]; mch[b]=best[1]
                gain+=best[0]; nchg+=1
                # lock neighbours
                for m in ms:
                    touched.add(m)
                    for (r,k) in members[m]:
                        for kk in (k-1,k+1):
                            if 0<=kk<len(st[r]): touched.add(mid[(r,kk)])
        print('round',rd,'changes',nchg,'gain@kf',round(gain,4)); sys.stdout.flush()
        if nchg==0: break
        ch2={x:mch[mid[x]] for x in mid}
        W2=rebuild(W2,st,ch2)
    return W2
if __name__=='__main__':
    from check import check
    W2=run(W)
    print(check(W2,'pairLS')); pickle.dump(W2,open('W_pair.pkl','wb'))

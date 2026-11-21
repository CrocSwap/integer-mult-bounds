from ls import *
from lub import bounds
from check import check
import pickle
setup(W); st=stays_of(W)
L,U=bounds(P)
def word_from_gatecharts(Gc):
    # Gc: event index -> mask for public participants (pub-pub gates and public scales); owned gates pinned
    frames=[list(b) for b in W['frames']]; m2i={}
    for k,m in enumerate(SM_): m2i.setdefault(m,k)
    def fid(m):
        if m not in m2i: m2i[m]=len(frames); frames.append(basis_of(m)); SM_.append(m)
        return m2i[m]
    cur=[SM_[x] for x in W['initial']]; curid=list(W['initial']); prog=[]
    for i,e in enumerate(P):
        op=e[0]
        if op=='MOVE':
            if e[1]>=n: prog.append(e)
            continue
        if op in('INIT','CLEAR'): prog.append(e); continue
        rs=[e[1]] if op=='SCALE' else [e[1],e[2]]
        pubs=[r for r in rs if r<n]
        if not pubs: prog.append(e); continue
        if op=='ADD' and (e[1]>=n or e[2]>=n): g=SM_[e[4]]; gid=e[4]
        else: g=Gc[i]; gid=None
        for r in pubs:
            if cur[r]!=g:
                nid=gid if gid is not None else fid(g)
                prog.append(['MOVE',r,curid[r],nid,False]); cur[r]=g; curid[r]=nid
        if op=='SCALE': prog.append(['SCALE',e[1],e[2],curid[e[1]]])
        else: prog.append([op,e[1],e[2],e[3],e[4] if (e[1]>=n or e[2]>=n) else curid[e[1]]])
    for r in range(n):
        if curid[r]!=W['final'][r]: prog.append(['MOVE',r,curid[r],W['final'][r],False])
    W2=dict(W); W2['program']=prog; W2['frames']=frames; return W2
if __name__=='__main__':
    W2=word_from_gatecharts(L); print(check(W2,'L-assign'))

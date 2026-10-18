from vr import *
import sys
def seqof(w): return [('A',i,e) for i,e in enumerate(w['A'])]+[('B',i,e) for i,e in enumerate(w['B'])]  # cut skipped for frames (cut ops have None frames); value ops handled separately
class Model:
    def __init__(self,w):
        self.w=w;self.P=w['ports'];R=w['report']['R'];n=2*V+R
        self.seq=seqof(w)   # global index g over A then B
        self.n=n
        self.writes={}   # reg-> list of g (writes: dst of add/scale)
        for g,(p,i,e) in enumerate(self.seq):
            self.writes.setdefault(e[1],[]).append(g)
        # cur frame after each op per register: record drag time wrt perp sets lazily
        cur={r:((self.P[r],) if r<V else ((G.basis(w['start_extra'][str(r)]) if str(r) in w.get('start_extra',{}) else ()) if r>=2*V else ())) for r in range(n)}
        self.hist={r:[(-1,cur[r])] for r in range(n)}
        for g,(p,i,e) in enumerate(self.seq):
            F=G.basis(e[-1])
            for r in [e[1]]+([e[2]] if e[0]=='add' else []):
                nf=G.basis(list(cur[r])+list(F))
                if nf!=cur[r]: self.hist[r].append((g,nf))
                cur[r]=nf
    def tdrag(self,u,ts):
        """first global idx at which u's frame is not inside perp(P_t) for all t in ts (None=never) ; -1 means from start"""
        for g,F in self.hist[u]:
            if not all(inperp(F,t,self.P) for t in ts): return g
        return None
    def frame_at(self,u,g):
        F=()
        for gg,FF in self.hist[u]:
            if gg<g: F=FF
        return F

def expand(M,u,g,ts,depth=0,memo=None,path=()):
    """value of reg u just before global op g, as list of (reg, insertpos_lo, insertpos_hi, coeff) reads each safe; or ('FLOOR',u,g,...)"""
    ws=[x for x in M.writes.get(u,[]) if x<g]
    last=ws[-1] if ws else -1
    td=M.tdrag(u,ts)
    hi=g if td is None else min(g,td)   # insert before op index <=hi
    lo=last+1
    if lo<=hi and (td is None or lo<=td):
        return [(u,lo,hi,Q(1))]
    if not ws: return [('FLOOR',u,g,td,'initial value, dragged before use')]
    p,i,e=M.seq[last]
    if e[0]=='scale':
        c=Q(e[2],e[3]); sub=expand(M,u,last,ts,depth+1,memo,path+((u,g),))
        return [(x if x[0]=='FLOOR' else (x[0],x[1],x[2],x[3]*c)) for x in sub]  # scale: new=c*old
    c=Q(e[3],e[4]); s=e[2]
    a=expand(M,u,last,ts,depth+1,memo,path+((u,g),))
    b=expand(M,s,last,ts,depth+1,memo,path+((u,g),))
    return a+[(x if x[0]=='FLOOR' else (x[0],x[1],x[2],x[3]*c)) for x in b]
if __name__=='__main__':
    w=load(__import__('os').environ['EO_ROOT']+'/work/o_cf0/FULL-WORD.json.gz');M=Model(w)
    g585=len(w['A'])+585
    for ts in ([58],[58,63]):
        r=expand(M,283,g585,ts)
        print(ts,len(r),[x for x in r if x[0]=='FLOOR'][:10]); print([x for x in r if x[0]!='FLOOR'][:30])

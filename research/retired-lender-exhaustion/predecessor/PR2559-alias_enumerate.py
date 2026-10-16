"""alias_enumerate.py WORD OUT.json: enumerate every (helper h, retired lender L) dirty-borrow alias on a BORROW-WORD and count the failing necessary frame conditions (h first used in B, L not used from h's first use on, dim(L frame at retirement) <= dim(h first frame), end frame of L contains the end of h)."""
import json,gzip,sys
from collections import Counter,defaultdict
from pathlib import Path as _P;sys.path.insert(0,str(_P(__file__).resolve().parent))
from audit_local import basis,contained,registers
def load(p):return json.loads(gzip.decompress(open(p,'rb').read()))
def analyze(w):
    v=112;n=2*v+w['report']['R'];h=9;full=basis([1<<i for i in range(h)])
    removed=set(w['removed']);live=[r for r in range(n) if r not in removed];istarget=lambda r:v<=r<2*v
    end=[full]*v+[basis([x for x in range(1,1<<h) if (x&p).bit_count()%2==0]) for p in w['ports']]+[full]*w['report']['R']
    for q,U in w['helper_final'].items():end[int(q)]=basis(U)
    start=[(p,) for p in w['ports']]+[()]*(v+w['report']['R'])
    for q,U in w['start_extra'].items():start[int(q)]=basis(U)
    npre=w['prelude_events'];A=w['A'];B=w['B'];nA=len(A);nB=len(B)
    uses=defaultdict(list)   # r -> list of (time, frame)  ; time: A i -> i, B p -> nA+p, restore j-> nA+nB+j
    early=set()
    for sec in ('precondition','compensation','cut'):
        for e in w[sec]:
            for r in registers(e):early.add(r)
    for i,e in enumerate(A):
        if e[0]=='warp':uses[e[1]].append((i,'warp'));continue
        for r in registers(e):uses[r].append((i,basis(e[-1])))
    byp=defaultdict(list)
    for op,rec in enumerate(w['warps'],1):byp[rec[0]].append(op)
    for p in range(nB+1):
        for op in byp.get(p,[]):uses[w['warps'][op-1][1]].append((nA+p-0.5,'warp'))
        if p<nB:
            for r in registers(B[p]):uses[r].append((nA+p,basis(B[p][-1])))
    for j,e in enumerate(w['restore']):
        for r in registers(e):uses[r].append((nA+nB+j,basis(e[-1])))
    # frame at retirement: simulate chain (warps set frame)
    cur=list(start);retire={}
    # simple: walk events in time order per register
    for r in live:
        c=start[r]
        for t,f in uses[r]:
            if f=='warp':
                # find the warp's to-frame
                pass
        retire[r]=None
    # full simulation (copy of audit order)
    cur=list(start)
    for e in A[:npre]:
        if e[0]=='warp':
            _,r_,op_,fr_,to_=e;cur[r_]=basis(to_)
        else:
            for q in registers(e):cur[q]=basis(e[-1]) if contained(cur[q],basis(e[-1])) else None
    lastframe={}
    for e in A[npre:]:
        for q in registers(e):cur[q]=basis(e[-1])
    snap_after_A=list(cur)
    frame_before_B=[None]*(nB+1)
    # record per register the frame at its last event
    curB=list(cur);hist=defaultdict(list)
    for p in range(nB+1):
        for op in byp.get(p,[]):
            rec=w['warps'][op-1];curB[rec[1]]=basis(rec[4])
        if p<nB:
            for q in registers(B[p]):curB[q]=basis(B[p][-1])
    return dict(v=v,n=n,full=full,live=live,end=end,start=start,uses=uses,early=early,nA=nA,nB=nB,removed=removed)
def frame_at(w,G,r,T):
    """frame of register r just before time T (B-index time) given uses"""
    c=G['start'][r]
    for t,f in G['uses'][r]:
        if t>=T:break
        if f=='warp':
            # locate warp record
            p=t-G['nA']+0.5
            for op,rec in enumerate(w['warps'],1):
                if rec[1]==r and rec[0]==p:c=basis(rec[4])
            # prelude warps
            if t<G['nA']:
                e=w['A'][int(t)];c=basis(e[4])
        else:c=f
    return c
def main(path):
    w=load(path);G=analyze(w);v=G['v'];nA=G['nA'];full=G['full']
    centers=set(w['centers']);lenders_now={rec[1] for rec in w['warps']}
    H=[r for r in G['live'] if r>=2*v and r not in centers]
    out=[];stats=Counter()
    Lcand=[r for r in G['live'] if not(v<=r<2*v) and r not in centers]
    lastuse={r:(G['uses'][r][-1][0] if G['uses'][r] else -1) for r in Lcand}
    for h in H:
        us=G['uses'][h]
        if not us:stats['h_unused']+=1;continue
        if h in G['early'] or us[0][0]<nA:stats['h_used_in_A_or_early']+=1;continue
        if any(f=='warp' for t,f in us):stats['h_is_lender']+=1;continue
        p1=us[0][0];F1=us[0][1];S=G['start'][h];hlast=us[-1][1]
        cold=str(h) in w['helper_final']
        for L in Lcand:
            if L==h:continue
            if lastuse[L]>=p1:stats['lender_not_retired']+=1;continue
            U=frame_at(w,G,L,p1);d=len(U)
            if d>len(F1):stats['dim_too_big']+=1;continue
            endL=G['end'][L]
            if not contained(hlast,endL) and not contained(G['end'][h],endL):stats['endL']+=1;continue
            # profile delta
            dp=Counter()
            if U!=endL:dp[len(endL)-len(U)]-=1     # L's terminal climb removed (approx: L climbs from U to its end)
            if S!=F1:dp[len(F1)-len(S)]-=1
            if d==len(S) and contained(S,F1):E='S'
            else:E='sub'
            if d!=len(F1):dp[len(F1)-d]+=1
            # end climbs: h last -> end[h]  vs  h last -> end[L]
            eh=G['end'][h]
            if hlast!=eh:dp[len(eh)-len(hlast)]-=1
            if hlast!=endL:dp[len(endL)-len(hlast)]+=1
            width=len(G['end'][h])-len(S)
            out.append(dict(h=h,L=L,p1=p1-nA,Lret=lastuse[L]-nA,d=d,s=len(S),f1=len(F1),E=E,cold=cold,width=width,dprof={k:x for k,x in dp.items() if x},Lsrc=L<v,Lwarped=L in lenders_now))
            stats['pair']+=1
    return out,stats
if __name__=='__main__':
    out,stats=main(sys.argv[1]);print(stats)
    json.dump(out,open(sys.argv[2],'w'))
    c=Counter((x['h'],x['width'],x['cold']) for x in out);print('helpers with any lender',len(c))
    print(Counter((x['E'],x['cold']) for x in out))

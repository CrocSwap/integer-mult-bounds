"""Any-refit test for pre-life hosting of borrower L on retired cold lender h (warp at L's first gate).
After the warp L sits at a frame E of dim d=|cold end of h| (warps keep dim). Every frame refit of the fixed
gate list needs lo'(g) <= hi(g) where lo' is propbound's forward lo propagation with the extra pin E on L.
Necessary: some dim-d E <= hi(L first gate) with all lo' <= hi.  usage: prelo.py WORD gapb.json"""
import sys,json,itertools
import os as _os,sys as _sys;_H=_os.path.dirname(_os.path.abspath(__file__));_sys.path[:0]=[_H,_os.path.join(_H,'..','..')]   # this directory and new/borrow (audit_local, word_patch, alias_build)
import os as _os,sys as _sys;_H=_os.path.dirname(_os.path.abspath(__file__));_sys.path[:0]=[_H,_os.path.join(_H,'..','..')]   # this directory and new/borrow (audit_local, word_patch, alias_build)
from wordmodel import Word,basis,contained,regs
from propbound import span
from gapbound import lohi
from collections import Counter
Wd=Word(sys.argv[1]);v=Wd.v;w=Wd.w;lo,hi=lohi(Wd)
ports=w['ports'];ev=Wd.events
lev={int(t):basis(U) for t,U in w.get('target_levels',{}).items()}
cU={q:basis(U) for q,U in zip(w['centers'],w['center_frames'])}
bnd=min(t for t,(s,e) in enumerate(ev) if s=='cut')
def lo_with(pin_t,pin_r,E):
    def stat_lo(q,warped):
        if warped:return ()
        return span(Wd.start[q],(ports[q],)) if q<v else Wd.start[q]
    lo_reg={};warped=set();crossed=False;bad=0
    for t,(s,e) in enumerate(ev):
        if not crossed and t>=bnd:
            crossed=True
            for q,U in cU.items():lo_reg[q]=span(lo_reg.get(q,stat_lo(q,q in warped)),U)
            for tt,U in lev.items():lo_reg[v+tt]=span(lo_reg.get(v+tt,()),U)
        if t==pin_t:lo_reg[pin_r]=E
        if e[0]=='warp':warped.add(e[1]);lo_reg[e[1]]=();continue
        if t not in Wd.gateframe:continue
        rs=regs(e);L_=span(*[lo_reg.get(q,stat_lo(q,q in warped)) for q in rs])
        if not contained(L_,hi[t]):return t
        for q in rs:lo_reg[q]=L_
    return None
pairs=[(x['h'],x['L']) for x in json.load(open(sys.argv[2])) if x['loose']]
cold={int(q):basis(U) for q,U in w['helper_final'].items()}
res=Counter();ok=[]
for h,L in sorted(set(pairs)):
    if h not in cold:res['h not cold']+=1;continue
    d=len(cold[h])
    G=[t for t,s in Wd.touches[L] if t in Wd.gateframe and s not in('precondition','compensation')]
    t0=G[0];H=hi[t0]
    if len(H)<d:res['hi dim']+=1;continue
    subs=set()
    vec=[x for x in range(1,512) if len(basis(list(H)+[x]))==len(H)]
    for vs in itertools.combinations(vec,d):
        B_=basis(list(vs))
        if len(B_)==d:subs.add(B_)
        if len(subs)>400:break
    good=None
    for E in sorted(subs):
        r=lo_with(t0,L,E)
        if r is None:good=E;break
    if good:ok.append((h,L,list(good)));print("FEASIBLE",h,L,good,flush=True)
    else:res['all E infeasible (lo>hi)']+=1
print(res,"feasible",len(ok));json.dump(ok,open(sys.argv[3],"w")) if len(sys.argv)>3 else None

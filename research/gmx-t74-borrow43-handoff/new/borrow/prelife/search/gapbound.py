"""Refit-necessary frame test for gap hosting (helper h nested in an idle gap of a live non-target L).
lo/hi = propbound.py's static-pin propagation (valid for EVERY frame refit of the fixed gate list).
Loosest model: warps allowed at both gap ends (barriers), so only dims must fit:
   dim frame(L at gap start) >= dim lo_L_in ;  need some dim F1 of h's first gate >= that, <= dim hi(h_first)
   dim Fl >= dim lo(h_last) ; need <= dim hi(L_next)
Strict model (no warps): span(lo_L_in, lo(h gates)) must sit below hi(h gates) & hi(L_next) (containment).
usage: gapbound.py WORD.json.gz out.json"""
import sys,json
import os as _os,sys as _sys;_H=_os.path.dirname(_os.path.abspath(__file__));_sys.path[:0]=[_H,_os.path.join(_H,'..','..')]   # this directory and new/borrow (audit_local, word_patch, alias_build)
from collections import Counter
from wordmodel import Word,basis,contained,regs
from propbound import meet,span
def lohi(Wd):
    w=Wd.w;v=Wd.v;FULL=Wd.full;ports=w['ports']
    lev={int(t):basis(U) for t,U in w.get('target_levels',{}).items()}
    cU={q:basis(U) for q,U in zip(w['centers'],w['center_frames'])}
    ev=Wd.events;bnd=min(t for t,(s,e) in enumerate(ev) if s=='cut')
    def stat_lo(q,warped):
        if warped:return ()
        return span(Wd.start[q],(ports[q],)) if q<v else Wd.start[q]
    lo_reg={};warped=set();lo={};crossed=False
    for t,(s,e) in enumerate(ev):
        if not crossed and t>=bnd:
            crossed=True
            for q,U in cU.items():lo_reg[q]=span(lo_reg.get(q,stat_lo(q,q in warped)),U)
            for tt,U in lev.items():lo_reg[v+tt]=span(lo_reg.get(v+tt,()),U)
        if e[0]=='warp':warped.add(e[1]);lo_reg[e[1]]=();continue
        if t not in Wd.gateframe:continue
        rs=regs(e);L=span(*[lo_reg.get(q,stat_lo(q,q in warped)) for q in rs]);lo[t]=L
        for q in rs:lo_reg[q]=L
    hi_reg={};hi={};crossed=False;lastwarp={}
    for t in range(len(ev)-1,-1,-1):
        s,e=ev[t]
        if not crossed and t<bnd:
            crossed=True
            for q,U in cU.items():hi_reg[q]=meet(hi_reg.get(q,Wd.end[q]),U)
            for tt in range(v):hi_reg[v+tt]=meet(hi_reg.get(v+tt,Wd.end[v+tt]),lev.get(tt,()))
        if e[0]=='warp':hi_reg[e[1]]=FULL;lastwarp[e[1]]=t;continue
        if t not in Wd.gateframe:continue
        rs=regs(e);H=FULL
        for q in rs:H=meet(H,hi_reg.get(q,Wd.end[q] if q not in lastwarp else FULL))
        hi[t]=H
        for q in rs:hi_reg[q]=H
    return lo,hi
if __name__=='__main__':
    Wd=Word(sys.argv[1]);v=Wd.v;lo,hi=lohi(Wd)
    WRAP=('precondition','compensation')
    T={r:[t for t,s in Wd.touches.get(r,[]) if s not in WRAP] for r in Wd.live}
    G={r:[t for t in T[r] if t in Wd.gateframe] for r in Wd.live}
    res=[];loose=[];strict=[]
    for hq in Wd.helpers:
        if not T[hq] or not G[hq]:continue
        a,b=T[hq][0],T[hq][-1];hf,hl=G[hq][0],G[hq][-1]
        for L in Wd.live:
            if L==hq or v<=L<2*v:continue
            if any(a<=t<=b for t in T[L]):continue
            nxt=[t for t in G[L] if t>b]
            if not nxt:continue
            prv=[t for t in G[L] if t<a]
            loin=span(Wd.start[L],(Wd.w['ports'][L],)) if L<v else Wd.start[L]
            if prv:loin=span(loin,lo[prv[-1]])
            hin=hi[nxt[0]]
            okl=len(loin)<=len(hi[hf]) and len(lo[hl])<=len(hin)
            # strict: one chain, no warps: everything h needs must fit between
            X=span(loin,*[lo[t] for t in G[hq]])
            oks=contained(X,hin) and all(contained(X,hi[t]) for t in G[hq])
            r=dict(h=hq,L=L,w=len(Wd.end[hq])-len(Wd.start[hq]),loin=len(loin),hif=len(hi[hf]),lol=len(lo[hl]),hin=len(hin),
                   din=max(0,len(loin)-len(hi[hf])),dout=max(0,len(lo[hl])-len(hin)),loose=okl,strict=oks)
            res.append(r)
    print('gap pairs',len(res),'helpers',len({r['h'] for r in res}))
    print('loose(warp-barrier, any refit) feasible',sum(r['loose'] for r in res),'helpers',sorted({r['h'] for r in res if r['loose']}))
    print('strict(no-warp, any refit) feasible',sum(r['strict'] for r in res))
    print('deficit hist (din,dout)',Counter((r['din'],r['dout']) for r in res).most_common(20))
    print('min total deficit by width',{wd:min(r['din']+r['dout'] for r in res if r['w']==wd) for wd in sorted({r['w'] for r in res})})
    json.dump(res,open(sys.argv[2],'w'))

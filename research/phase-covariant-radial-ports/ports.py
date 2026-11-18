"""Use an explicit numerical backend in the retained complete port.

Port source: JoyboyBrian / PR5485 and the credited PR4743 lineage.
Interface: Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from kernel import need

def port(x,y,f,kind,reverse,width,backend,source,capture=False):
    monomial,mix=source.monomial,source.mix
    need(x is not y, 'Distinct dirty banks')
    need(kind in (2,3),'two or three calls')
    if capture:x=list(x);y=list(y)
    trace={};cuts=[]
    def paid(v,axis,adj=False):
        before=list(v) if capture else None
        backend(v,f,axis,width,adj,trace)
        if capture:cuts.append((axis,adj,before,list(v)))
    if reverse:
        if kind==3:
            monomial(y,'M',f,width,True);paid(y,2,True);monomial(y,'W',f,width,True)
        paid(y,0,True);mix(x,y,f,width,-1);paid(x,0,True)
    else:
        paid(x,0);mix(x,y,f,width,1);paid(y,0)
        if kind==3:monomial(y,'W',f,width);paid(y,2);monomial(y,'M',f,width)
    return x,y,trace,cuts


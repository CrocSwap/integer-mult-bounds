from vr import *
import itertools,sys
W0=load(__import__('os').environ['EO_ROOT']+'/work/o_cf0/FULL-WORD.json.gz')
def build(Q,hoist,terms,dst=591,delidx=585):
    """Q: B index where hoisted reads+absorption go; hoist: list of B indices to hoist (original indices); terms: regs absorbed into dst in order"""
    w=copy.deepcopy(W0); B=w['B']
    assert B[delidx][:3]==['add',dst,283]
    moved=[B[i][:-1]+[None] for i in hoist]
    dead=set(hoist)|{delidx}
    newB=[]
    for i,e in enumerate(B):
        if i==Q: newB+= [copy.deepcopy(m) for m in moved]; newB+=[['add',dst,u,1,1,None] for u in terms]
        if i in dead: continue
        newB.append(e)
    w['B']=newB
    return w
def evaluate(w,seeds=(591,),verbose=True):
    ok=same_value(W0,w)
    r,ch,cone=lazy(w,list(seeds)); b,fr=caps(r)
    return ok,ch,b,fr,prof(r),r
if __name__=='__main__':
    for Q in (0,100,200,239):
        w=build(Q,[245,246,271,272],(283,281,299,297))
        ok,ch,b,fr,pr,r=evaluate(w)
        print(Q,'value',ok,'changed',ch,'caps',b,pr if not isinstance(pr,dict) else 'PROFILE OK')

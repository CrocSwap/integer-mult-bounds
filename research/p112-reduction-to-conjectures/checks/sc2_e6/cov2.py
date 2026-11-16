import sys,time,itertools
from cov import *
import os; HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE); sys.path.insert(0,os.path.join(HERE,'..','g777'))
from cov import g
import cov as C
from importlib import import_module
# CARRIER's cov.py is shadowed; load as module under other name
import importlib.util
spec=importlib.util.spec_from_file_location('carcov',os.path.join(HERE,'carrier_cov.py'))
carcov=importlib.util.module_from_spec(spec); spec.loader.exec_module(carcov)
def cover_set(T,ws,verbose=False):
    """True if lines T (indices) can be covered by flats of weights ws"""
    T=list(T); ws=sorted(ws,reverse=True)
    capall=sum(g[w] for w in ws)
    if len(T)>capall: return False
    big=[w for w in ws if w>=5]; small=[w for w in ws if w<5]
    tg=Tgt(T)
    capsmall=sum(g[w] for w in small)
    slack=capall-len(T)
    arr={}
    for w in set(big):
        L=max(1,g[w]-slack)
        arr[w]=(tg.level(w,L))
        if verbose: print(' level',w,'L',L,len(arr[w]),flush=True)
    npar={}
    for w,lst in arr.items():
        lo=np.array([m&((1<<64)-1) for m in lst],dtype=np.uint64); hi=np.array([m>>64 for m in lst],dtype=np.uint64)
        npar[w]=(lo,hi,lst)
    labs_of=lambda unc:tuple(lab[tg.T[i]] for i in bits(unc))
    smallds=tuple(sorted(small,reverse=True))
    nodes=[0]
    def rec(idx,unc,prev):
        # idx: next big piece
        nodes[0]+=1
        left=bin(unc).count('1')
        if idx==len(big):
            if left==0: return True
            if left>capsmall: return False
            return carcov.can_cover(labs_of(unc),smallds,0,{})
        capleft=sum(g[w] for w in big[idx+1:])+capsmall
        need=left-capleft
        ul=np.uint64(unc&((1<<64)-1)); uh=np.uint64(unc>>64)
        bestw={}
        for w2 in set(big[idx:]):
            lo2,hi2,_=npar[w2]
            bestw[w2]=(int((pc(lo2&ul)+pc(hi2&uh)).max()) if len(lo2) else 0) if len(lo2)<=5000 else g[w2]
        if sum(bestw[w2] for w2 in big[idx:])+capsmall<left: return False
        need=left-sum(bestw[w2] for w2 in big[idx+1:])-capsmall
        w=big[idx]
        lo,hi,lst=npar[w]
        ul=np.uint64(unc&((1<<64)-1)); uh=np.uint64(unc>>64)
        cnt=pc(lo&ul)+pc(hi&uh)
        start=prev[1] if idx>0 and big[idx-1]==w else 0
        ids=np.nonzero(cnt>=max(need,0))[0]
        ids=ids[ids>=start] if start else ids
        ids=ids[np.argsort(-cnt[ids],kind='stable')] if not (idx>0 and big[idx-1]==w) else ids
        for k in ids:
            if rec(idx+1,unc&~lst[k],(w,int(k))): return True
        return False
    r=rec(0,tg.full,(0,0))
    if verbose: print(' nodes',nodes[0])
    return r

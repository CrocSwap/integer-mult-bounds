# SYN-18 probe: plane-stopper planes per S1 block: parallel classes, rows, pairing on a common plane.
exec(open((__import__('os').environ['HM_ROOT']+'/cards/B167/blockscan.py')).read().split("for r in rep: print(r)")[0].replace("rep.append((bn,len(cols)","INFO[bn]=(cols,vec,planes,H,B,S,wide,pairs,scr);rep.append((bn,len(cols)") .replace("rep=[]","rep=[];INFO={}"))
from collections import Counter
for bn,(cols,vec,planes,H,B,S,wide,pairs,scr) in INFO.items():
    # plane -> its direction (functional): plane through 4 points; parallel class = linear part
    def lin(P):
        ps=sorted(P); v0=vec[ps[0]]; return frozenset(vec[p]^v0 for p in ps)
    cls=Counter(lin(H[z]) for z in planes)
    hz=Counter(H[z] for z in planes)
    print(bn,'stoppers',len(planes),'distinct planes',len(hz),'parallel classes used',len(cls),'class sizes',sorted(cls.values()),
          '| B-bound sizes', Counter(len(B[r]) for r in cols+scr))
    if bn==list(INFO)[3]:
        for z in planes: print('  z',z,'H',sorted(H[z]),'row',{k:str(v) for k,v in rows0[z].items()})
        for u in wide: print('  courier',u,'row',{k:str(v) for k,v in rows0[u].items()})

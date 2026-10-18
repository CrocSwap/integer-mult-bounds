import sys,os
sys.dont_write_bytecode=True
SY=(__import__('os').environ['HM_ROOT']+'/cards/SYN-18')
os.chdir(SY)
src=open('planes.py').read().split("from collections import Counter")[0]
exec(src)
from collections import Counter
def kn(dd):
    if not dd: return None
    it=sorted(dd.items()); s=it[0][1]; return tuple((a,b/s) for a,b in it)
phases=['A','cut','B','tail','compensation','cleanup']
TW=[]
for bn,(cols,vec,planes,H,B,S,wide,pairs,scr) in INFO.items():
    for u in wide:
        if u not in scr: continue
        ku=kn(rows0[u]); tw=[r for r in cols+scr if r!=u and kn(rows0[r])==ku]
        if len(tw)==1 and len(S[u])==2: TW.append((bn,u,tw[0],planes,H,B,cols,scr))

"""T74 aggregated window-class model pieces (classes = (cap,lo,hi) windows; one item per bin per call)."""
import sys,collections,math;sys.path.insert(0,__import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from fillbase import *
WID=[4,5,7,8,9]
prov=read(P/'new/BORROW-PROVIDERS.json');wd=prov['gauge44']['widths'];assert all(d['widths']==wd for d in prov.values())
DW=collections.Counter(wd)                 # per-call width demand
win={}
for key,(cap,times) in windows.items():
    r,ch=map(int,key.split(','));ts=sorted(times);assert ts==list(range(ts[0],ts[-1]+1));win[r,ch]=(cap,ts[0],ts[-1])
cls=collections.defaultdict(list)
for (r,ch),(cap,lo,hi) in sorted(win.items()):
    for p in range(112):cls[cap,lo,hi].append((r,ch,p))
CL=sorted(cls)
K=0.0017037
def h(f):return 0.0 if f<=0 else f*((73/f)**K-1)
def pats(cap):
    out=[]
    def rec(i,rem,cur):
        if i==len(WID):out.append(tuple(cur));return
        for c in range(rem//WID[i]+1):rec(i+1,rem-c*WID[i],cur+[c])
    rec(0,cap,[]);return out
PATS={c:pats(c) for c in (8,16,32,48)}
def idle(cap,p):return cap-sum(a*w for a,w in zip(p,WID))

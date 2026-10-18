# Exact optimum over square (9-term) decoders of ONE fixed A2-family member (duality branch-and-bound over the catalogue of deficiency directions, opt3u.py).
# Every deficiency space of these members is 1-dim (asserted), so the candidate directions are exactly the catalogue directions and the search is complete for that member (HUNT-A2 notes, section 1);
# pairwise duality (x_i . y_j = 0 unpaired, != 0 paired) and independence of the chosen row / column directions are enforced exactly at the point.
# usage: UNIT=P112|P104|E8 python exact_opt.py gen|tie THRESHOLD      gen: first random member with the exact iff pattern; tie: the member of data/tie_<UNIT>.json.
import os, sys, json, random, io, contextlib
os.environ['NDIM']='9'; os.environ['NT']='9'
from a2lib import *
import opt3u
mode=sys.argv[1]; thr=int(sys.argv[2])
if mode=='tie':
    D=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','data','tie_%s.json'%UNIT))); th=tuple(Fr(x) for x in D['theta']); zX=tuple(Fr(x) for x in D['zX'])
else:
    rnd=random.Random(1)
    while True:
        th=tuple(Fr(rnd.randint(-9,9)) for _ in range(4)); zX=tuple(Fr(rnd.randint(-50,50),rnd.randint(1,7)) for _ in range(3))
        if pattern_ok(Mof(*build(th,zX)))==0: break
A,B=build(th,zX); assert pattern_ok(Mof(A,B))==0
out=catalogue(A,B); assert all(len(x[1])<=1 and len(x[2])<=1 for x in out.values())
buf=io.StringIO()
with contextlib.redirect_stdout(buf):
    r=opt3u.run(list(X),[],[0]*v,[0]*v,out,thr,verbose=False,PH=(A,B))
print('RESULT',UNIT,mode,'theta',[str(x) for x in th],'zX',[str(x) for x in zX],'exact square optimum',r)

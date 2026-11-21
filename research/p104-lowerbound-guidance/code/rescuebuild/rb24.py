"""rb24: follow rb22 log; for each SURVIVES design: fixed generic walks, then joint walk+frame LM (jbuild). usage: rb24.py log k"""
import sys,os,time,ast;sys.path.insert(0,'.')
from rb15 import *
log,k=sys.argv[1],int(sys.argv[2]);done=0
while True:
    L=[l for l in open(log) if 'SURVIVES' in l]
    for l in L[done:]:
        d=ast.literal_eval(l[l.index('((('):].strip());R=roles_of(d);v=l.split('val ')[1].split()[0]
        b,res=builds(k,R,nw=4,tr=8)
        if b:print('BUILT-FIXED',v,d,flush=True)
        else:
            ok,info,S,z,Q=jbuild(k,R,starts=3)
            print('BUILT-JOINT' if ok else 'stall',v,'fixed %.1e'%res,info if ok else '',d if ok else '',flush=True)
        done+=1
    if any('STATUS' in l for l in open(log)) and done>=len([l for l in open(log) if 'SURVIVES' in l]):break
    time.sleep(20)
print('END',done)

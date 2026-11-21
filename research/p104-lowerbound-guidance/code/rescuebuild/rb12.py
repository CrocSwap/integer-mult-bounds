"""rb12: follow an rb7 log, numerically test each new design (fixed generic walks).  usage: rb12.py log k pid_of_enum [walks] [tries]"""
import sys,os,time,ast;sys.path.insert(0,'.')
from rb1 import *
from rb10 import roles_of
log,k,pid=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]);nw=int(sys.argv[4]) if len(sys.argv)>4 else 3;tr=int(sys.argv[5]) if len(sys.argv)>5 else 8
done=0
def alive(p):
    try: os.kill(p,0);return True
    except OSError: return False
while True:
    L=[l for l in open(log) if l.startswith('#')]
    for l in L[done:]:
        num,v,t,rest=l.split(' ',3);d=ast.literal_eval(rest.strip());R=roles_of(d);best=9;hit=None
        for w in range(nw):
            S=FSys(k,R,anywalk(k,w));nr,z=S.solve(w,tries=tr);best=min(best,nr)
            if nr<1e-9:
                P,W=to_real(*S.unpack(z)[:3],k);hit=(w,np.abs(P+np.eye(S.n)).max());break
        print(num,v,'BUILT walk %d prod+I %.1e'%hit if hit else 'stall best %.2e'%best,flush=True)
        done+=1
    if not alive(pid) and done>=len([l for l in open(log) if l.startswith('#')]):break
    time.sleep(10)
print('END',done)

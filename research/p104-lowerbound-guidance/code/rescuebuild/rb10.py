"""rb10: numeric frame build attempts (fixed generic walks) on enumerated designs.  usage: rb10.py pickle k [walks] [tries] [maxdesigns]"""
import sys,pickle,time;sys.path.insert(0,'.')
from rb1 import *
def roles_of(des):return [(F(M),[F(p) for p in P]) for M,P,mn in des]
if __name__=='__main__':
    fn=sys.argv[1];k=int(sys.argv[2]);nw=int(sys.argv[3]) if len(sys.argv)>3 else 3;tr=int(sys.argv[4]) if len(sys.argv)>4 else 6
    mx=int(sys.argv[5]) if len(sys.argv)>5 else 10**9
    seen=pickle.load(open(fn,'rb'));items=sorted(seen.items(),key=lambda x:-x[1])[:mx];hits=[]
    print('designs',len(items),flush=True)
    for j,(d,v) in enumerate(items):
        R=roles_of(d);best=9
        for w in range(nw):
            S=FSys(k,R,rwalk(k,500+w));nr,z=S.solve(w,tries=tr);best=min(best,nr)
            if nr<1e-9:
                P,W=to_real(*S.unpack(z)[:3],k);hits.append((v,d,w));print('BUILT',round(v,3),d,'walk',w,'prod+I %.1e'%np.abs(P+np.eye(S.n)).max(),flush=True);break
        print(j,round(v,3),'best res %.2e'%best,flush=True)
    pickle.dump(hits,open(fn.replace('.pkl','_hits.pkl'),'wb'));print('hits',len(hits))

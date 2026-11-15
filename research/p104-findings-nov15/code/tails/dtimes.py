import os,sys,json
os.environ['SUP_BASE']='inputs/ATTACK/COURIER226/hit_c226_1.json.gz'
sys.path.insert(0,'.')
from census import *
from layer2 import delta_times
import tails
for st in [(680,1049,39784,43434),(592,1053,40278,42506),(681,1049,36664,43436),(664,1051,39828,43374),(117,1066,42259,43682),(627,117,33141,43993)]:
    m=mapst(st,nbo); r=test([m],frames_mode='down',K=4000,owned=False,want=True)
    ed,W2,org,seeds,sv=make([m]); r['org']=org; W3m,org2=corrected(r)
    dt,Xn,Xb=delta_times(W3m,org2,B0)
    # map W3 time -> base time approx via org2
    def bt(j):
        while j<len(org2) and org2[j] is None: j+=1
        return org2[j] if j<len(org2) else len(B0['program'])
    out=[]
    for rr,j in sorted(dt.items(),key=lambda x:x[1]):
        if B0['final'][rr]!=127 and ((Xn[rr,:n]-Xb[rr,:n])%P).any():
            G=B0['final'][rr]; t=bt(j); path=[(x['c'],x['mv']) for x in tails.M.nodes[rr]]
            cur=[c for c,mv in path if (mv or 0)<=t][-1]
            out.append((rr,G,'junk@',t,'main at chart',cur,'dim',tails.M.dim[cur],'arrG',tails.arrive(rr,G)))
    print(st,out,flush=True)

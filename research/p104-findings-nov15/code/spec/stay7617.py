# R2: run the BIG/TAILS stay-drop engine on #7617 (SUP_BASE=best7616) for given w7608 stays; save corrected word + dirty rows.
import os,sys,json,gzip,threading,resource,time,pickle
os.environ['SUP_BASE']='inputs/ATTACK/STACK7616/best7616.json.gz'
def _w():
    while True:
        if resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1e9>3.8: print('RSS bail',flush=True); os._exit(3)
        time.sleep(1)
threading.Thread(target=_w,daemon=True).start()
OUT=os.path.abspath(sys.argv[2]);todo=json.load(open(os.path.abspath(sys.argv[1])));lim=int(sys.argv[3])
os.chdir('inputs/BIG/TAILS/code');sys.path.insert(0,'.')
from k3 import *
import circ
W8=json.load(gzip.open('inputs/ATTACK/PAIR/code/w7608.json.gz','rt')); nb8=circ.Base(W8)
def mapst(st,old):
    h,F,a,d=st; L=old.stays[h]; i=[x[1] for x in L].index(a)
    pf=L[i-1][0]; nf=L[i+1][0]; N=nb.stays[h]
    c=[j for j,x in enumerate(N) if 0<j<len(N)-1 and x[0]==F and N[j-1][0]==pf and N[j+1][0]==nf]
    if not c: return None
    j=min(c,key=lambda j:abs(N[j][1]-a)); x=N[j]; return (h,x[0],x[1],x[2])
print('base public',n,'events',len(B0['program']),flush=True)
for st,mode in todo[:lim]:
    t0=time.time();m=mapst(tuple(st),nb8)
    if m is None:print(st,'unmapped',flush=True);continue
    K=300 if mode=='all' else 4000
    r=test([m],frames_mode=mode,K=K,owned=False,want=True)
    if not r.get('cands'):print(st,m,'nocands',flush=True);continue
    ed,W2,org,seeds,sv=make([m]);r['org']=org
    W3m,org2=corrected(r);Xn,Xb,kind=obs_rows(W3m,org2,None)
    D=(Xn-Xb)%P;dirty=[]
    for i in range(len(kind)):
        if D[i].any():
            k=kind[i];cols=np.nonzero(D[i])[0].tolist()
            dirty.append(dict(kind=k[0],r=int(k[1]),G=B0['final'][k[1]] if k[0]=='pub' else None,cols=cols,coef=[int(D[i,c]) for c in cols]))
    tag='_'.join(map(str,m))
    with gzip.open(os.path.join(OUT,'w3m_%s.json.gz'%tag),'wt') as f:json.dump(W3m,f)
    open(os.path.join(OUT,'dirty7617.jsonl'),'a').write(json.dumps(dict(st=st,m=m,sv=sv,ok=bool(r.get('ok')),dirty=dirty,tag=tag))+'\n')
    print(st,m,'sv',round(sv,3),'ok',r.get('ok'),'dirty',[(d['kind'],d['r'],d['G'],len(d['cols'])) for d in dirty][:6],len(dirty),round(time.time()-t0,1),flush=True)

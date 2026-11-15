import os,sys,threading,resource,time,json,gzip,collections
os.environ['SUP_BASE']='inputs/ATTACK/COURIER226/hit_c226_1.json.gz'
def _w():
    while True:
        if resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1e9>3.8: print('RSS>3.8GB bail',flush=True); os._exit(3)
        time.sleep(1)
threading.Thread(target=_w,daemon=True).start()
sys.path.insert(0,'.')
from k3 import *
import circ
W8=json.load(gzip.open('inputs/ATTACK/PAIR/code/w7608.json.gz','rt')); nb8=circ.Base(W8)
def mapst(st,old):
    h,F,a,d=st; L=old.stays[h]; i=[x[1] for x in L].index(a)
    pf=L[i-1][0]; nf=L[i+1][0]; N=nb.stays[h]
    c=[j for j,x in enumerate(N) if 0<j<len(N)-1 and x[0]==F and N[j-1][0]==pf and N[j+1][0]==nf]
    if not c: return None
    j=min(c,key=lambda j:abs(N[j][1]-a)); x=N[j]; return (h,x[0],x[1],x[2])
fg=collections.defaultdict(list)
for q in range(n): fg[B0['final'][q]].append(q)
def run(m,mode,K):
    t0=time.time()
    r=test([m],frames_mode=mode,K=K,owned=False,want=True)
    out=dict(m=m,ok=bool(r.get('ok')),K=r.get('K'),nv=r.get('nviol'))
    if not r.get('cands'): out['err']='nocands'; return out
    ed,W2,org,seeds,sv=make([m]); r['org']=org
    W3m,org2=corrected(r); Xn,Xb,kind=obs_rows(W3m,org2,None)
    D=(Xn-Xb)%P; dirty=[]
    for i in range(len(kind)):
        if D[i].any():
            k=kind[i]; cols=np.nonzero(D[i])[0].tolist()
            fin=B0['final'][k[1]] if k[0]=='pub' else None
            dirty.append(dict(kind=k[0],r=int(k[1]),G=fin,cols=cols[:400],ncols=len(cols),coef=[int(D[i,c]) for c in cols[:400]]))
    out['dirty']=dirty; out['sv']=sv; out['sec']=round(time.time()-t0,1)
    return out
if __name__=='__main__':
    which=sys.argv[1]; outf=sys.argv[2]
    S=json.load(open('inputs/BIG/VPHASE/singles.json'))
    done=set()
    if os.path.exists(outf):
        for l in open(outf): done.add(tuple(json.loads(l)['st']))
    todo=[]
    if which=='strict':
        for st in [(117,1066,42259,43682),(625,117,33138,33283),(624,117,33139,43889),(627,117,33141,43993),(680,1049,39784,43434),(592,1053,40278,42506),(664,1051,39828,43374),(681,1049,36664,43436),(67,1066,42260,42509),(1144,24,34341,35522),(1191,246,39072,46777),(1164,37,29797,29900),(691,1050,36094,44033)]:
            todo.append((st,'down',4000,'stack'))
    else:
        seen=set()
        for s in sorted(S,key=lambda s:-s['m']):
            t=tuple(s['st'])
            if t in seen: continue
            seen.add(t); todo.append((t,s['mode'],300 if s['mode']=='all' else 4000,'w7608'))
        if which!='all': todo=todo[:int(which)]
    for st,mode,K,src in todo:
        if st in done: continue
        try:
            m=mapst(st,nbo if src=='stack' else nb8)
            if m is None: o=dict(err='unmapped')
            else: o=run(m,mode,K)
        except Exception as e: o=dict(err=repr(e)[:200])
        o['st']=st; o['mode']=mode
        open(outf,'a').write(json.dumps(o)+'\n')
        print(st,o.get('m'),o.get('ok'),o.get('err'),[(d['r'],d['G'],d['ncols']) for d in o.get('dirty',[])][:6],o.get('sec'),flush=True)

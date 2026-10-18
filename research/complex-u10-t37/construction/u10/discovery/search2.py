import sys,json,gzip,itertools,time;sys.path.insert(0,'/tmp/don');from slot import *
b=0.001665;m=73
f=lambda r:r*((m/r)**b-1)
fee=lambda P:sum(f(int(k))*v for k,v in P.items())
base_path,part,nparts,OUTD=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]
w=L(base_path);base=fee(profile(w))
B=w['B'];se=set(map(int,w['start_extra']))
copies=[i for i,g in enumerate(B) if g[0]=='add' and g[1]>=224 and g[2]>=224 and g[3]==1 and g[4]==1]
copies=[c for k,c in enumerate(copies) if k%nparts==part]
def evaluate(ci,a,dons):
    w2=build(w,ci,a,dons)
    if w2 is None: return None
    w3,info=optimise(w2)
    if w3 is None: return None
    P=profile(w3)
    return (fee(P)-base)/b,P,w3
for ci in copies:
    E,X,reads,pre=slot_info(w,ci)
    if not reads or len(reads)>5: continue
    if any(j>ci and B[j][1] in (X,E) for j in range(len(B))): continue
    if E not in se and any(j<ci and B[j][1]==E for j in range(len(B))) and False: continue
    orig={i:s for (i,t,s,c) in reads}
    H={i:holders(w,ci,i,{E,X}) for (i,t,s,c) in reads}
    ks=[i for (i,t,s,c) in reads]
    assigns=[dict(zip(ks,ss)) for ss in itertools.product((E,X),repeat=len(ks))] if len(ks)<=4 else [orig]
    donopts=[[]]
    singles=[(i,h,j) for i in ks for (h,j) in H[i]]
    donopts+= [[s] for s in singles]
    donopts+= [[s1,s2] for s1,s2 in itertools.combinations(singles,2) if s1[0]!=s2[0] and s1[1]!=s2[1]]
    best=None;n=0;t0=time.time()
    for dons in donopts:
        for a in assigns:
            if not dons and a==orig: continue
            try: r=evaluate(ci,a,dons)
            except Exception as ex: r=None
            n+=1
            if r is None: continue
            if best is None or r[0]<best[0]:
                best=(r[0],a,dons,r[1])
                if r[0]<-1e-9:
                    fn=OUTD+'/imp_%d_%d.gz'%(ci,n)
                    w3=r[2];w3['report']['local_profile']={str(k):v for k,v in r[1].items()}
                    open(fn,'wb').write(gzip.compress(json.dumps(w3,separators=(',',':')).encode(),mtime=0))
                    import subprocess
                    rr=subprocess.run(['python3','-B','/tmp/bar/audit_local.py','--word',fn,'--output',fn+'.audit.json'],capture_output=True,text=True)
                    ok='PASS_INDEPENDENT' in rr.stdout
                    print('IMPROVE' if ok else 'improve-FAIL','ci',ci,'E',E,'X',X,'%.5f'%r[0],a,dons,r[1],'' if ok else (rr.stdout+rr.stderr).strip().splitlines()[-1][:120],flush=True)
                    if not ok: best=None
    print('slot ci',ci,'E',E,'X',X,'reads',len(reads),'evals',n,'best',None if best is None else '%.5f'%best[0],best[3] if best else '', '%.0fs'%(time.time()-t0),flush=True)

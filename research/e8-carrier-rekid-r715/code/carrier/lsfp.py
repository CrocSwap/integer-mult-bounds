# local search over producer knobs for the FP word, objective = R after #443 reuse (tuning check only)
import os,sys,json,ast,random,time
os.environ['E8COORD']='ham'
import runfp as RF, ham2fp as H
Pd={ast.literal_eval(k):v for k,v in json.load(open('params-r740.json'))}
keys=list(Pd.keys())
mods={'pair':3,'fold':2,'l5':2,'fc0':7,'fn':3,'ls':3}
random.seed(int(sys.argv[1])); T=float(sys.argv[2]); t0=time.time()
def ev(P):
    H.P.clear(); H.P.update(P); return RF.run(True,1,0,True)['Rreuse']
cur=dict(Pd); best=ev(cur); print('start',best,flush=True)
while time.time()-t0<T:
    k=random.choice(keys); n=mods.get(k[0],2)
    P=dict(cur); P[k]=(P.get(k,0)+random.randint(1,n-1))%n
    r=ev(P)
    if r<=best:
        if r<best: print('improve',r,k,P[k],'%.0fs'%(time.time()-t0),flush=True)
        best=r; cur=P
json.dump([[repr(k),v] for k,v in cur.items()],open('params-fp-ls%s.json'%sys.argv[1],'w'))
print('final',best,flush=True)

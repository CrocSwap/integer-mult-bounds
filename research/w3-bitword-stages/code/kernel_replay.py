"""replay.py OLD_DIR NEW_DIR OUT_JSON [trials]
(1) GF(2) replay (the word's semantics: bit side, ADD acts iff coefficient odd) with 64 parallel random dirty inputs per
    trial: all sources/targets/helpers random. PASS requires: sources unchanged, target_final = target ^ source,
    every helper restored, and every register's final value identical between old (#310) and new word.
    Omitted-gate controls: removing the cat-28 (Q) or cat-29 (Q^-1) gates must break the new word.
(2) Integer replay mod 2^61-1 of both words with identical random inputs, for the record: #310's own word is NOT a
    Z-identity (targets depend on helper dirt over Z), so Z-equality is not a correctness criterion for this F2 word."""
import sys,json,random
import numpy as np
P=(1<<61)-1
def load(d): return np.fromfile(d+'/COHORT249-RECORDS.bin',dtype='<i4').reshape(-1,6).tolist()
def runF2(rec,x0,n,omit=None):
    x=list(x0)+[0]
    for k,a,b,c,f,z in rec:
        if k==1:
            if z==omit or not (c&1): continue
            x[a]^=x[b]
        elif k==2: x[n]=x[a]
        elif k==3:
            if x[n]!=x[a]: raise RuntimeError('erase mismatch')
    return x[:n]
def runZ(rec,x0,n):
    x=list(x0)+[0]
    for k,a,b,c,f,z in rec:
        if k==1: x[a]=(x[a]+c*x[b])%P
        elif k==2: x[n]=x[a]
        elif k==3 and x[n]!=x[a]: raise RuntimeError('erase mismatch')
    return x[:n]
if __name__=='__main__':
    old,new=load(sys.argv[1]),load(sys.argv[2])
    st=json.load(open(sys.argv[2]+'/249-states.json')); n,v=st['n'],st['v']
    T=int(sys.argv[4]) if len(sys.argv)>4 else 4
    res=dict(trials=T,bits_per_trial=64,registers=n)
    bad=dict(old_target=0,new_target=0,old_helper=0,new_helper=0,source=0,old_vs_new=0)
    for t in range(T):
        rnd=random.Random(1000+t); x0=[rnd.getrandbits(64) for _ in range(n)]
        yo=runF2(old,x0,n); yn=runF2(new,x0,n)
        for y,tag in ((yo,'old'),(yn,'new')):
            bad[tag+'_target']+=sum(1 for i in range(v) if y[v+i]!=x0[v+i]^x0[i])
            bad[tag+'_helper']+=sum(1 for s in range(2*v,n) if y[s]!=x0[s])
            bad['source']+=sum(1 for i in range(v) if y[i]!=x0[i])
        bad['old_vs_new']+=sum(1 for s in range(n) if yo[s]!=yn[s])
        if t==0:
            for cat in (28,29):
                yc=runF2(new,x0,n,omit=cat); res[f'control_omit_cat{cat}_wrong_registers']=sum(1 for s in range(n) if yc[s]!=yo[s])
    res['F2_failures']=bad
    rnd=random.Random(7); x0=[rnd.randrange(P) for _ in range(n)]; zo=runZ(old,x0,n); zn=runZ(new,x0,n)
    x1=list(x0)
    for s in range(2*v,n): x1[s]=0
    zo1=runZ(old,x1,n)
    res['Z_mod_2^61-1']=dict(old_targets_depending_on_helper_dirt=sum(1 for s in range(v,2*v) if zo[s]!=zo1[s]),
        helpers_restored_old=sum(1 for s in range(2*v,n) if zo[s]==x0[s]),helpers_restored_new=sum(1 for s in range(2*v,n) if zn[s]==x0[s]),
        nonhelper_equal_old_vs_new=sum(1 for s in range(2*v) if zo[s]==zn[s]),note='#310 word itself is not a Z-identity; F2 is the semantics')
    res['status']='PASS' if not any(bad.values()) and res['control_omit_cat28_wrong_registers']>0 and res['control_omit_cat29_wrong_registers']>0 else 'FAIL'
    json.dump(res,open(sys.argv[3],'w'),indent=1); print(json.dumps(res))

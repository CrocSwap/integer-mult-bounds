"""Does there exist d in {0..8}^(16\\I) x {9}^I (inactive set exactly I) that is lexmax in its Aut-orbit
(d >=lex d o p for all 384 p, position 0 most significant)?  For every non-orbit-lexmax mask I the answer must be NO
for the cube partition (orbit-lexmax I only) to be complete.  Incremental DFS with alive-permutation pruning."""
import pickle, sys, time
T55='code/tight55/'
PERMS=[tuple(p) for p in pickle.load(open(T55+'perms.pkl','rb'))]
ident=tuple(range(16)); PNF=[p for p in PERMS if p!=ident]
nonrep, lexmax_masks = pickle.load(open('partition_masks.pkl','rb'))
def feasible(I):
    d=[0]*16
    def dfs(k, alive):
        # alive: list of (p, j) undecided perms with pointer j (all positions <j equal)
        if k==16: return True
        vals=[9] if I>>k&1 else range(8,-1,-1)
        for v in vals:
            d[k]=v; na=[]; ok=True
            for (p,j) in alive:
                while j<=k and p[j]<=k:
                    a=d[j]; b=d[p[j]]
                    if a>b: j=-1; break
                    if a<b: ok=False; break
                    j+=1
                if not ok: break
                if j!=-1: na.append((p,j))
            if ok and dfs(k+1,na): return True
        return False
    return dfs(0,[(p,0) for p in PNF])
if __name__=='__main__':
    which=sys.argv[1]
    masks = nonrep if which=='nonrep' else lexmax_masks
    t0=time.time(); feas=[]
    for n,I in enumerate(masks):
        if feasible(I): feas.append(I)
        if n%200==0: print(n,len(masks),len(feas),round(time.time()-t0),flush=True)
    print(which,'masks',len(masks),'feasible',len(feas),'time',round(time.time()-t0))
    print('feasible masks:', feas[:50])
    pickle.dump(feas,open(f'dfs_{which}.pkl','wb'))

# usage: solve_types.py TYPES.json.gz WRITER(A|B) RANK SELECT [KEEPDIR]
#  SELECT: sample (fixed 32-type sample) | all | chunk:i/n (types i, i+n, ... of the |D|-sorted nonorth list)
# For each selected non-orthogonal type: CNF "fitting rank <= RANK on the orthogonality graph of D" must be UNSAT with a drat-trim VERIFIED proof.
import sys, json, gzip, time
sys.path.insert(0,__import__('os').path.dirname(__file__))
tp,w,r,sel=sys.argv[1],sys.argv[2],int(sys.argv[3]),sys.argv[4]; keep=sys.argv[5] if len(sys.argv)>5 else None
T=[t for t in json.load(gzip.open(tp,'rt')) if t['nonorth']]
T.sort(key=lambda t:(len(t['D']),t['j'],t['k']))
if sel=='sample': T=T[:14]+T[14::(len(T)-14)//18][:18]
elif sel.startswith('chunk:'): i,n=map(int,sel[6:].split('/')); T=T[i::n]
def Gof(t):
    m=len(t['D']); return [[0 if (t['orth'][a]>>b&1) and a!=b else 1 for b in range(m)] for a in range(m)]
if w=='A':
    import satA; run=lambda G,D,r,tag: satA.run(G,D,r,None,tag=tag,keep=keep)[:2]
else:
    import satB, lib
    def run(G,D,r,tag):
        S=lib.nonorth_clique(G,list(reversed(D)),r)
        return satB.solve(G,D,r,S)
bad=0; t0=time.time()
for t in T:
    D=list(range(len(t['D']))); res=run(Gof(t),D,r,f"t{t['j']}_{t['k']}")
    ok=(res[0]=='UNSAT' and res[1] is True); bad+=not ok
    print('type j',t['j'],'k',t['k'],'|D|',len(D),'rank<=%d'%r,res,'OK' if ok else 'BAD',flush=True)
print('writer',w,'types',len(T),'bad',bad,'seconds',int(time.time()-t0))
print('PASS' if bad==0 and T else 'FAIL', 'all selected types UNSAT at rank <= %d with VERIFIED DRAT (writer %s)'%(r,w))
sys.exit(1 if bad or not T else 0)

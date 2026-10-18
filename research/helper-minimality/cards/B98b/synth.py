"""Re-synthesise a block's A program with fewer scratch registers. Exact Fractions.
Registers: lines (8, rows = cols identity) + kept scratch. Target = shipped end-of-A rows (rows of canonical replay).
Backward elimination from target to [I;0], invert."""
import gzip,json,pickle,csv,math,sys
from fractions import Fraction as Q
exec(open('iface.py').read().split("reads=defaultdict")[0])
for e in d['A']: ap(e)
blocks,_=pickle.load(open('iface.pkl','rb'))
def src(k,S_): return {e[2] for e in d[k] if e[0]=='add' and e[2] in S_}
H=list(csv.DictReader(open((__import__('os').environ['HM_ROOT']+'/inputs/ledger_helpers.csv'))))
psi={int(h['reg']):float(h['psi']) for h in H}
def synth(names,rowsv):
    n=len(rowsv);cols=sorted({j for r in rowsv for j in r});M=[[r.get(j,Q(0)) for j in cols] for r in rowsv]
    ops=[]  # backward ops transforming M -> [I;0]
    k=len(cols)
    for c in range(k):
        # pivot row among rows >=c ... target pivot row is line index c (rows 0..k-1 are lines)
        cand=[i for i in range(n) if M[i][c]!=0 and (i>=c or i<k) and all(M[i][cc]==0 for cc in range(c)) or (i==c and M[i][c]!=0)]
        cand=[i for i in range(c,n) if M[i][c]!=0]
        if not cand: return None
        p=min(cand,key=lambda i:(M[i][c].denominator, abs(M[i][c].numerator),i))
        if p!=c:  # swap via adds: row_c += row_p ; ensures nonzero pivot at c
            ops.append(('add',c,p,Q(1)));M[c]=[a+b for a,b in zip(M[c],M[p])]
        if M[c][c]!=1:
            q=M[c][c];ops.append(('scale',c,1/q));M[c]=[x/q for x in M[c]]
        for i in range(n):
            if i!=c and M[i][c]!=0:
                f=M[i][c];ops.append(('add',i,c,-f));M[i]=[a-f*b for a,b in zip(M[i],M[c])]
    for i in range(n):
        for j in range(k):
            assert M[i][j]==(1 if i==j else 0),(i,j)
    # invert: reversed order, add(t,s,q)->add(t,s,-q), scale(c,s)->scale(c,1/s)
    fw=[]
    for o in reversed(ops):
        fw.append(('add',o[1],o[2],-o[3]) if o[0]=='add' else ('scale',o[1],1/o[2]))
    return fw,cols
def verify(fw,cols,rowsv):
    n=len(rowsv);k=len(cols);R=[[Q(1) if i==j else Q(0) for j in range(k)] if i<k else [Q(0)]*k for i in range(n)]
    for o in fw:
        if o[0]=='add':R[o[1]]=[a+o[3]*b for a,b in zip(R[o[1]],R[o[2]])]
        else:R[o[1]]=[o[2]*a for a in R[o[1]]]
    return all(R[i]==[r.get(j,Q(0)) for j in cols] for i,r in enumerate(rowsv))
tot_save=0;res=[]
for bn,regs in blocks.items():
    S_=set(regs)
    keep=src('B',S_)|src('tail',S_)|src('cut',S_)|src('compensation',S_)|src('cleanup',S_)
    cols=sorted({j for r in regs for j in rows[r]})
    if len(cols)!=8: res.append((bn,'skip cols',len(cols)));continue
    lines=cols
    # lines rows at end of A (shipped T); order: lines first, in cols order => identity start index i<->col
    names=lines+sorted(keep)
    rv=[rows[r] for r in names]
    out=synth(names,rv)
    if out is None: res.append((bn,'rank-deficient',len(keep)));continue
    fw,cc=out
    ok=verify(fw,cc,rv)
    dens=sorted({o[3].denominator if o[0]=='add' else o[2].denominator for o in fw}|{1})
    drop=sorted(S_-keep);sv=sum(psi[r] for r in drop)
    res.append((bn,'ok' if ok else 'FAIL',len(keep),'ops',len(fw),'dens',dens[:8],'drop',len(drop),'psi_saved',round(sv,1)))
    tot_save+=sv if ok else 0
for r in res:print(r)
print('total psi of dropped regs (verified blocks)',round(tot_save,1))

# Bridge own generator: #7761 final graph -> Lean data (Bridge7761D*.lean). Data only; verifies everything in exact Fractions.
import os as _os
_HERE=_os.path.dirname(_os.path.abspath(__file__))
# BRIDGE_OUT: a COPY of ../../Nov15 (read for inputs, overwritten with outputs); BRIDGE_GRAPH: final7761.json.gz from apply.py
OUTD=_os.environ['BRIDGE_OUT'].rstrip('/')+'/'
BG=_HERE+'/'
import gzip, json, collections, sys
EMIT123='--d123' in sys.argv
from fractions import Fraction
g=json.loads(gzip.decompress(open(_os.environ['BRIDGE_GRAPH'],'rb').read())); lay=json.load(open(_os.environ['BRIDGE_IFACE']))
fr,I,F,first=g['frames'],g['initial'],g['final'],g['first_output']
forms={k:{d:Fraction(c) for d,c in f} for k,f in g['forms']}
moves={k:(a,b) for k,a,b in g['moves']}
n=len(I)
sched=[k for k in g['schedule'] if k<first]; assert len(sched)==len(moves)==5746
pos={k:i for i,k in enumerate(sched)}
# ---- RREF charts
def rref(vs):
    rows=[]
    for v in vs:
        for b in rows:
            if v & (1<<(b.bit_length()-1)): v^=b
        if v:
            rows.append(v)
    # reduce fully
    rows.sort(key=lambda x:-x)
    for i,b in enumerate(rows):
        p=1<<(b.bit_length()-1)
        for j in range(len(rows)):
            if j!=i and rows[j]&p: rows[j]^=b
    rows.sort(key=lambda x:-x)
    return rows
CB=[rref(f) for f in fr]; CP=[[b.bit_length()-1 for b in r] for r in CB]
for r,p in zip(CB,CP):
    assert all(b<512 for b in r)
    for i in range(len(r)):
        for j in range(len(r)): assert ((r[j]>>p[i])&1)==(1 if i==j else 0)
rk=lambda c:len(CB[c])
def inspan(c,x): # x in span of chart c
    v=0
    for b,p in zip(CB[c],CP[c]):
        if (x>>p)&1: v^=b
    return v==x
def le(c,d): return all(inspan(d,b) for b in CB[c])
# ---- evaluation
val={}
for k in g['schedule']:
    row={}
    for d,c in forms[k].items():
        src={~d:Fraction(1)} if d<0 else val[d]
        for i,v in src.items():
            x=row.get(i,0)+c*v
            if x: row[i]=x
            else: row.pop(i,None)
    val[k]=row
# ---- locality at chart-id level (evidence for P-FORMS)
for k in g['schedule']:
    ch = moves[k][0] if k<first else F[k-first]
    for d in forms[k]:
        if d<0: assert I[~d]==ch
        else: assert moves[d][1]==ch and (k>=first or pos[d]<pos[k])
# ---- roles / pi / O
role={}
for x in lay['live']: role[x]='X'; role[x+112]='Y'
for x in lay['hosted']['X2']: role[x]='X2'
for y in lay['hosted']['Y2']: role[y]='Y2'
mains=sorted(m for m in role if m<n); assert len(mains)==400
part={m:[i for i in val[first+m] if i!=m] for m in range(n)}
assert all(len(p)<=1 for p in part.values()) and all(m in val[first+m] for m in range(n))
pi=list(range(n))
for m in range(n):
    if part[m]:
        p=part[m][0]; assert m in role and p in role
        pi[m]=p; 
for m in range(n):
    if part[m]:
        p=part[m][0]
        if pi[p]==p: pi[p]=m
assert all(pi[pi[m]]==m for m in range(n)), 'pi not involution'
assert all((pi[m]!=m)==(m in role) for m in range(n))
for m in range(n): assert set(val[first+m])<= {m,pi[m]}
Od=[val[first+m][m] for m in range(n)]
Op=[val[first+m].get(pi[m],Fraction(0)) if pi[m]!=m else Fraction(0) for m in range(n)]
assert all(Od)
for m in range(n):
    if pi[m]!=m: assert Od[m]*Od[pi[m]]-Op[m]*Op[pi[m]]!=0
print('pairs full',sum(1 for m in mains if Op[m] and Op[pi[m]]),'rows w partner',sum(1 for m in range(n) if Op[m]))
cl=[rk(F[m])-rk(I[m]) for m in range(n)]
assert all(rk(I[m])<=rk(F[m]) and le(I[m],F[m]) for m in range(n))
assert all(cl[m]==8 for m in mains)
print('mains cl8; nonmains cl hist',collections.Counter(cl[m] for m in range(n) if m not in role))
pairs=sorted(set((moves[k][0],moves[k][1]) for k in sched)); print('distinct bank chart pairs',len(pairs))
assert all(le(a,b) or le(b,a) for a,b in pairs)
# ---- rows
src=open(OUTD+'BankFlagB.lean').read()
def lst(name):
    s=src.split('def %s : List (ℕ × ℕ) := '%name)[1].split('\n')[0]; return [tuple(map(int,t.split(', '))) for t in s.strip('[]()').split('), (')]
def nl(name): return [int(x) for x in src.split('def %s : List ℕ := '%name)[1].split('\n')[0].strip('[]').split(', ')]
par=lambda a,b: bin(a&b).count('1')%2
def is_ker(c,a): return rk(c)==8 and all(par(a,x)==0 for x in CB[c])
rows={}
for nm,cn,kind in (('OUT','cntOUT','O'),('IN','cntIN','I')):
    P=lst(nm); used=set(); rl=[0]*len(P); cands={}
    for i in nl(cn):
        v,a=P[i]
        if kind=='O': cs=[f for f in mains if CB[I[f]]==[v] and rk(F[f])==9 and rk(I[pi[f]])==0 and is_ker(F[pi[f]],a) and Op[f]]
        else: cs=[f for f in mains if rk(I[f])==0 and is_ker(F[f],a) and CB[I[pi[f]]]==[v] and rk(F[pi[f]])==9 and Op[f]]
        cands[i]=cs
    for i in sorted(cands,key=lambda i:len(cands[i])):
        c=[f for f in cands[i] if f not in used]; assert c,(nm,i); used.add(c[0]); rl[i]=c[0]
    rows[nm]=rl; print(nm,'cands',[len(cands[i]) for i in sorted(cands)])
ehi=[f for f in range(n) if rk(I[f])==1 and rk(F[f])==9 and rk(I[pi[f]])==0 and rk(F[pi[f]])==8 and Op[f]]
elo=[f for f in range(n) if rk(I[f])==0 and rk(F[f])==8 and rk(I[pi[f]])==1 and rk(F[pi[f]])==9 and Op[f]]
print('Ehi',len(ehi),'Elo',len(elo)); assert len(ehi)==104 and len(elo)==104
# ---- emit
def L(name,ty,xs,per=60,chunk=1500):
    out=[]
    parts=[xs[i:i+chunk] for i in range(0,len(xs),chunk)] or [[]]
    for pi_,pt in enumerate(parts):
        out.append('def %s%d : List %s := [%s]\n'%(name,pi_,ty,', '.join(pt)))
    out.append('def %s : List %s := %s\n'%(name,ty,' ++ '.join('%s%d'%(name,i) for i in range(len(parts)))))
    return ''.join(out)
def q(x): return '(%d/%d : ℚ)'%(x.numerator,x.denominator) if x.denominator!=1 else '(%d : ℚ)'%x.numerator
hdr='import Mathlib.Data.Rat.Defs\nnamespace Bridge7761\n'
if EMIT123:
    open(OUTD+'Bridge7761D1.lean','w').write('-- generated by bridgegen/gen.py chart reduced-echelon bases/pivots for the 1099 frames of #7761 final graph\n'+hdr+
      'def chBasis : List (List ℕ) := [%s]\n'%', '.join('[%s]'%', '.join(map(str,r)) for r in CB)+
      'def chPiv : List (List ℕ) := [%s]\n'%', '.join('[%s]'%', '.join(map(str,r)) for r in CP)+'end Bridge7761\n')
    open(OUTD+'Bridge7761D2.lean','w').write('-- generated: field data (A/B chart ids, pi, main flags, O diag/partner entries)\n'+hdr+
      L('fA','ℕ',list(map(str,I)))+L('fB','ℕ',list(map(str,F)))+L('piL','ℕ',list(map(str,pi)))+
      L('mainL','Bool',['true' if m in role else 'false' for m in range(n)])+
      L('odL','ℚ',[q(x) for x in Od])+L('opL','ℚ',[q(x) for x in Op])+'end Bridge7761\n')
    open(OUTD+'Bridge7761D3.lean','w').write('-- generated: bank data in schedule order (src/dst chart ids), distinct chart pairs, flag rows, HS rows\n'+hdr+
      L('bS','ℕ',[str(moves[k][0]) for k in sched],chunk=1500)+L('bT','ℕ',[str(moves[k][1]) for k in sched],chunk=1500)+
      L('bPairs','(ℕ × ℕ)',['(%d, %d)'%p for p in pairs],chunk=300)+
      'def rowOL : List ℕ := [%s]\n'%', '.join(map(str,rows['OUT']))+'def rowIL : List ℕ := [%s]\n'%', '.join(map(str,rows['IN']))+'end Bridge7761\n')


# ================= D4/D5: HS rows, chains =================
EMIT45='--d45' in sys.argv
if EMIT45:
    import re
    dw=open(OUTD+'DecoderWall4Data.lean').read()
    labsL=[int(x) for x in re.search(r'def labs : List ℕ := \[([^\]]*)\]',dw).group(1).split(',')]
    assert len(labsL)==104
    live=lay['live']; labx={}
    for x in live:
        assert len(CB[I[x]])==1; labx[x]=CB[I[x]][0]
    assert sorted(labx.values())==sorted(labsL)
    Xof=[next(x for x in live if labx[x]==l) for l in labsL]   # Lean index p -> field
    dotp=lambda a,b: bin(a&b).count('1')&1
    # symbolic values
    desc=[k for k in sched if not le(moves[k][0],moves[k][1])]
    for k in desc: assert le(moves[k][1],moves[k][0])
    dset=set(desc)
    sym={}
    for k in g['schedule']:
        row={}
        for d,c in forms[k].items():
            ss={('x',~d):Fraction(1)} if d<0 else sym[d]
            for i,v in ss.items(): row[i]=row.get(i,0)+c*v
        row={i:v for i,v in row.items() if v}
        sym[k]=row
        if k in dset: pass
    # NOTE sym of a descent k used by later banks must be the symbol D_k: recompute with substitution
    sym={}; symraw={}
    for k in g['schedule']:
        row={}
        for d,c in forms[k].items():
            ss={('x',~d):Fraction(1)} if d<0 else sym[d]
            for i,v in ss.items(): row[i]=row.get(i,0)+c*v
        row={i:v for i,v in row.items() if v}
        symraw[k]=row
        sym[k]={('D',k):Fraction(1)} if k in dset else row
    beta={k:{j:v for (t,j),v in symraw[k].items() if t=='D' and v} for k in desc}
    succ={}
    for k in desc:
        assert len(beta[k])<=1
        for j in beta[k]: succ.setdefault(j,[]).append(k)
    assert all(len(v)==1 for v in succ.values())
    chains=[]
    for h in [k for k in desc if not beta[k]]:
        ch=[h]
        while ch[-1] in succ: ch.append(succ[ch[-1]][0])
        chains.append(ch)
    assert len(chains)==8 and sum(map(len,chains))==23==len(desc)
    for ch in chains:
        for t in range(len(ch)-1): assert moves[ch[t]][1]==moves[ch[t+1]][0]
    cdiag={x:[v for i,v in val[first+x+112].items() if i!=x+112] for x in live}
    # U[s][k]: coefficient of D_k in output Y_s over its partner... recompute exactly as ca1: Y_s row = diag*Y_s + c X_s, divide by cdiag
    cd={}
    for x in live:
        r=val[first+x+112]; others={i:v for i,v in r.items() if i!=x+112}
        assert list(others)==[x]; cd[x]=others[x]
    Xi=[Xof[p] for p in range(104)]
    def q(x): return '(%d/%d : ℚ)'%(x.numerator,x.denominator) if x.denominator!=1 else '(%d : ℚ)'%x.numerator
    Z=Fraction(0)
    chdata=[]
    for ch in chains:
        ids=[moves[ch[0]][0]]+[moves[k][1] for k in ch]
        fresh=[[symraw[k].get(('x',Xi[p]),Z) for p in range(104)] for k in ch]
        gath=[[symraw[first+Xi[s]+112].get(('D',k),Z)/cd[Xi[s]] for s in range(104)] for k in ch]
        bet=[Fraction(1)]+[beta[k][ch[t-1]] for t,k in enumerate(ch) if t>0]
        chdata.append((ch,ids,fresh,gath,bet))
        # carried check vs true values
    # check Realises in exact arithmetic
    bad=0
    for p in range(104):
        for s in range(104):
            if dotp(labsL[p],labsL[s]):
                tot=Z
                for ch,ids,fresh,gath,bet in chdata:
                    car=[Z]*104; 
                    for kk in range(len(ch)):
                        car=[ (bet[kk]*car[pp] if kk>0 else Z)+fresh[kk][pp] for pp in range(104)]
                        tot+=car[p]*gath[kk][s]
                if tot!=(1 if p==s else 0): bad+=1
    print('Realises failures (python)',bad)
    # supports
    for ch,ids,fresh,gath,bet in chdata:
        for j,k in enumerate(ch):
            for p in range(104):
                if fresh[j][p]: assert inspan(ids[j],labsL[p]),('fresh',j,p)
            for sI in range(104):
                if gath[j][sI]: assert all(dotp(labsL[sI],b)==0 for b in CB[ids[j+1]]),('gath',j,sI)
    print('chain supports OK; chain lens',[len(c[0]) for c in chdata])
    # F2 factorisation certificate for row price: per chain, dep/gat from phi,cv
    out45=[]
    out45.append('def hsEhi : List ℕ := [%s]\ndef hsElo : List ℕ := [%s]\n'%(', '.join(map(str,ehi)),', '.join(map(str,elo))))
    out45.append('def xField : List ℕ := [%s]\n'%', '.join(map(str,Xi)))
    open(OUTD+'Bridge7761D4.lean','w').write('-- generated: HS partner rows (104+104) and live label->field map\nimport Mathlib.Data.Rat.Defs\nnamespace Bridge7761\n'+''.join(out45)+'end Bridge7761\n')
    o5=['-- generated: #7761 relay chains (23 descents in 8 chains) as ChainRow data; index p = DW4.lab p\nimport Mathlib.Data.Rat.Defs\nnamespace Bridge7761\n']
    o5.append('def chPos : List (List ℕ) := [%s]\n'%', '.join('[%s]'%', '.join(str(pos[k]) for k in c[0]) for c in chdata))
    o5.append('def chIds : List (List ℕ) := [%s]\n'%', '.join('[%s]'%', '.join(map(str,c[1])) for c in chdata))
    for ci,c in enumerate(chdata):
        o5.append('def chFresh%d : List (List ℚ) := [%s]\n'%(ci,', '.join('[%s]'%', '.join(q(x) for x in r) for r in c[2])))
        o5.append('def chGath%d : List (List ℚ) := [%s]\n'%(ci,', '.join('[%s]'%', '.join(q(x) for x in r) for r in c[3])))
        o5.append('def chBeta%d : List ℚ := [%s]\n'%(ci,', '.join(q(x) for x in c[4])))
    o5.append('def chFresh : List (List (List ℚ)) := [%s]\n'%', '.join('chFresh%d'%i for i in range(8)))
    o5.append('def chGath : List (List (List ℚ)) := [%s]\n'%', '.join('chGath%d'%i for i in range(8)))
    o5.append('def chBeta : List (List ℚ) := [%s]\n'%', '.join('chBeta%d'%i for i in range(8)))
    o5.append('end Bridge7761\n')
    open(OUTD+'Bridge7761D5.lean','w').write(''.join(o5))

json.dump(dict(pairs=len(pairs)),open('gen.out.json','w'))

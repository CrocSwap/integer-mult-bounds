# Row-puncture floors P_k and the Case I / Case II arithmetic (A2COST sections 2-4), UNIT env: P112 | P104 | E8.
# P_k := minimum cost of an 8-term (square, dimension 8) decoder of the Gram matrix with the rows of Z (subset of the triangle X, |Z| = k) deleted (zeroed).
#   P112, P104: exact duality branch-and-bound over the catalogue of deficiency directions (opt3u.py; complete because every candidate space is 1-dim).
#   E8: no column-deficient classes; the row-deficient classes of the punctured Gram are exactly |Z| classes with 1-dim nullspace and normal r_i (i in Z), and r_1, r_2, r_3 span only 2 dimensions
#       (the E8 near-miss, README remark); then each term costs >= 9 except at most rank{r_i : i in Z} terms with row normal parallel to some r_i (cost >= 8): P_k >= 72 - rank{r_i : i in Z}.
# Then the case arithmetic (README section 5): Case I (some x_j parallel to e_9) and Case II (no x_j parallel to e_9).
import os, io, contextlib, itertools
os.environ['NDIM']='8'; os.environ['NT']='8'
from a2lib import *
Xt=list(X); print(UNIT,'lines',v,'triangle X',Xt)
P={}
def punctured(Z):
    ph=[([0]*8 if u in Z else list(L[u])) for u in range(v)]; qh=[list(L[u]) for u in range(v)]
    out={}
    for co,w in cls.items():
        Oc=bits(w); nr=nullspace([ph[u] for u in Oc],8); nc=nullspace([qh[u] for u in Oc],8)
        if nr or nc: out[co]=(len(Oc),nr,nc)
    return ph,qh,out
for k in range(4):
    vals=[]
    for Z in itertools.combinations(Xt,k):
        ph,qh,out=punctured(Z)
        if UNIT in ('P112','P104'):
            import opt3u
            buf=io.StringIO()
            with contextlib.redirect_stdout(buf):
                r=opt3u.run(list(Z),[],[0]*v,[0]*v,out,80,verbose=False,PH=(ph,qh))
            assert r is not None and all(len(x[1])<=1 and len(x[2])<=1 for x in out.values())
            vals.append(r)
        else:
            rowdef=[(co,x) for co,x in out.items() if x[1]]; coldef=[x for x in out.values() if x[2]]
            assert not coldef and len(rowdef)==k and all(len(x[1])==1 for _,x in rowdef)
            def norm(x):
                i=next(a for a in range(8) if x[a]!=0); return tuple(c/x[i] for c in x)
            normals=sorted(norm(x[1][0]) for _,x in rowdef)
            assert normals==sorted(norm(R[u]) for u in Z)          # the normals are the roots r_i, i in Z
            vals.append(8*9-rank([R[u] for u in Z],8))          # the bound P_k >= 72 - rank{r_i : i in Z}
    P[k]=min(vals)
    print('P_%d = %d   (over the %d subsets Z of X of size %d: %s)'%(k,P[k],len(vals),k,sorted(set(vals))))
if UNIT=='E8':
    assert rank([R[u] for u in Xt],8)==2
    print('PASS E8: r_1, r_2, r_3 span only 2 dimensions')
EXP_P={'P112':{0:64,1:63,2:62,3:62},'P104':{0:56,1:56,2:56,3:56},'E8':{0:72,1:71,2:70,3:70}}[UNIT]
assert P==EXP_P, (P,EXP_P)
print('PASS floors',UNIT,P)
# B[X,s] for s in O_{u_i} \ (E6 u X) is the unit vector e_i (convention B[t,s] = 1 iff t = s or t orthogonal to s); this is what makes cost_0 >= |T| (Case I) and cost_0 >= |Z| (Case II(a)).
E6=[s for s in range(v) if all(Gm[x][s]==0 for x in Xt)]
for i in range(3):
    Sset=[s for s in O[i] if s not in E6 and s not in Xt]
    assert {tuple((Brows[x]>>s)&1 for x in Xt) for s in Sset}=={tuple(int(a==i) for a in range(3))}
print('PASS B[X,s] = e_i for every s in O_{u_i} minus (E6 and X)')
# ---- Case I (some x_j parallel to e9): T = {i : w_i not in <r_i>}; cost_0 >= rank{e_i : i in T} = |T|; the other eight terms decode a Gram with the rows Z (T <= Z, |Z| <= 3) deleted or enlarged.
#      |T| <= 1: the rows outside T are honest (pattern), so |Z| = |T|; |T| = 2: |Z| in {2,3}; |T| = 3: |Z| = 3.
caseI={0:P[0],1:1+P[1],2:2+min(P[2],P[3]),3:3+P[3]}
# ---- Case II (a): some y_j has A_j inside X (cocycle frame y_j = e_9): cost_0 >= |Z| and the other eight terms are a Gram decoder with the columns Z punctured/enlarged: total >= min_k (k + P_k)
caseIIa=min(k+P[k] for k in range(4))
# ---- Case II (b): exact class-level min-cost relaxation (iib.py), no e9 row, each catalogue direction used at most once per side.  Off the B-locus (gamma2 != gamma3) at most ONE merged class is column-killable
#      (mergedkill.py, CHECKED); on the B-locus none.  II(b) = min(off, on) = the off-locus value (65 / 62 / 74 vs 66 / 63 / 75 on the locus).
from iib import relaxations
_r = relaxations([9])
caseIIb = min(_r['off'][9], _r['on'][9])
print('Case II(b) relaxation: off B-locus', _r['off'][9], ' on B-locus', _r['on'][9])
assert caseIIb == {'P112': 65, 'P104': 62, 'E8': 74}[UNIT]
caseII=min(caseIIa,caseIIb)
FLOOR={'P112':64,'P104':56,'E8':72}[UNIT]
print('Case I totals by |T|:',caseI,'-> Case I floor',min(caseI.values()))
print('Case II: (a)',caseIIa,' (b)',caseIIb,'-> Case II floor',caseII)
assert min(caseI.values())==FLOOR and caseII>=FLOOR
overall=min(min(caseI.values()),caseII)
print('PASS case arithmetic %s: every square decoder of every A2-family member costs >= %d (Case I %d, Case II >= %d)'%(UNIT,overall,min(caseI.values()),caseII))
assert overall==FLOOR

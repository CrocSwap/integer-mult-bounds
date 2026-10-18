from enum9 import *
import itertools
AMS=sorted({Fr(p,q) for p in range(-8,9) for q in range(1,9) if p!=0})
cnt=dict(us=0,nonorth=0,sol=0,vl=0)
fail_i={}
for J in itertools.combinations(range(8),5):
    Jc=[c for c in range(8) if c not in J]
    for m in J:
        cand={}
        for j in J:
            allowed=set(Jc)|{m,j}
            cand[j]=[t for t in range(v) if FCl[t][j]!=0 and all(FCl[t][c]==0 for c in range(8) if c not in allowed)]
        if any(len(cand[j])==0 for j in J): 
            fail_i['nocand']=fail_i.get('nocand',0)+1; continue
        for prod in itertools.product(*[cand[j] for j in J]):
            cnt['us']+=1
            if len(set(prod))<5 or not all(nonorth(a_,b_) for a_,b_ in itertools.combinations(prod,2)): continue
            cnt['nonorth']+=1
            us=dict(zip(J,prod))
            a={c:Fr(1,FCl[us[c]][c]) for c in J if c!=m}
            I=Jc+[m]
            for am in AMS:
                a2=dict(a);a2[m]=am
                A=[[Fr(0)]*8 for _ in range(8)]
                for c in J:
                    for i in range(8): A[i][c]=a2[c]*FCl[us[c]][i]
                if any(A[r][c]!=Fr(int(r==c)) for r in range(8) if r not in I for c in range(8)):
                    fail_i['Irows']=fail_i.get('Irows',0)+1; break
                ok=0
                for i in I:
                    w=[Fr(int(i==c))-A[i][c] for c in range(8)]
                    k=key(w)
                    if k is not None and k in RK: ok+=1
                fail_i[ok]=fail_i.get(ok,0)+1
print(cnt,fail_i)

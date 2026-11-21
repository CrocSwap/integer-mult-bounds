import json, itertools, sys
exec(open('explore.py').read().split("print(lab==L1")[0])
E8=json.load(open(D+'e8base.json')); b=E8['basis'];Gb=E8['Gb'];C=E8['C']
# standard roots, doubled coords
roots=[]
for i,j in itertools.combinations(range(8),2):
    for si in(2,-2):
        for sj in(2,-2):
            v=[0]*8; v[i]=si; v[j]=sj; roots.append(tuple(v))
for s in itertools.product((1,-1),repeat=8):
    if s.count(-1)%2==0: roots.append(s)
assert len(roots)==240
ip=lambda x,y: sum(a*c for a,c in zip(x,y))//4
assert all(sum(a*c for a,c in zip(x,y))%4==0 for x in roots for y in roots)
# backtrack basis with Gram Gb
sol=None
def bt(k,ch):
    global sol
    if sol: return
    if k==8: sol=list(ch); return
    for r in roots:
        if all(ip(r,ch[j])==Gb[k][j] for j in range(k)) and ip(r,r)==2:
            bt(k+1,ch+[r])
            if sol: return
# restrict first root to a fixed one (transitivity)
ch0=[roots[0]]
bt(1,ch0)
beta=sol
print(beta)
R=[tuple(sum(C[t][j]*beta[j][a] for j in range(8)) for a in range(8)) for t in range(120)]
rs=set(roots)
print(all(r in rs for r in R), len(set(R)), len(set(R)|set(tuple(-a for a in r) for r in R)))
print(all(ip(R[t],R[s])==sum(C[t][a]*Gb[a][c]*C[s][c] for a in range(8) for c in range(8)) for t in range(120) for s in range(120)))
json.dump({'beta':beta,'R':[list(r) for r in R]},open('embed.json','w'))
# omitted 16
om=list(range(104,120))
print([[ip(R[a],R[c]) for c in om] for a in om])

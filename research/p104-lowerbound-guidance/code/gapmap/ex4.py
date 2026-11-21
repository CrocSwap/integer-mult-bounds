import sys; sys.path.insert(0,'<word-rung-package>/tools')
import pricekit as pk
W=pk.load('<word-rung-package>/data/t7669.json.gz')
dot=lambda a,b: bin(a&b).count('1')&1
def span(B):
    S={0}
    for b in B: S|={x^b for x in S}
    return frozenset(S)
F=W['frames']; ports=W['ports']; H=W['hosted']; ini=W['initial']; fin=W['final']; live=W['live']
X2=H['X2']; Y2=H['Y2']; Dp=H['Dports']
print(X2[:8],Y2[:8],Dp[:12], live[:8], sorted(set(range(104))-set(Dp)))
# try X2[j] <-> port Dp[j]
a=sum(ports[p] in span(F[ini[x]]) for x,p in zip(X2,Dp)); b=sum(all(dot(v,ports[p])==0 for v in F[fin[y]]) for y,p in zip(Y2,Dp))
print('idx map',a,b)
# alt: X2 reg = 772+live[p]
m={}
for p in Dp:
    x=772+live[p]; y=882+live[p]
    m[p]=(x in X2, y in Y2)
print(sum(v[0] and v[1] for v in m.values()))
print(H['alpha2'] if not isinstance(H['alpha2'],list) else H['alpha2'][:3], H['beta2'] if not isinstance(H['beta2'],list) else H['beta2'][:3])
# partner perm hint: Y2 finals/x2 initial
import itertools
# brute: for each X2 reg find ports whose q in initial chart
for j in range(4):
    x=X2[j]; S=span(F[ini[x]]); print(j,x,F[ini[x]], [p for p in range(104) if ports[p] in S][:5])
for j in range(4):
    y=Y2[j]; print(j,y,F[fin[y]], [p for p in range(104) if all(dot(v,ports[p])==0 for v in F[fin[y]])][:5])

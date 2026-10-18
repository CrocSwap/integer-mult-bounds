from an1 import *
def dot(a,b): return bin(a&b).count('1')&1
w=load(__import__('os').environ['EO_ROOT']+'/work/o_base/FULL-WORD.json.gz');P=w['ports'];cur,rd=frames(w)
# readers by register: y targets that add from s directly
ry=collections.defaultdict(set)
for y in range(V,2*V):
    for s in rd[y]: ry[s].add(y-V)
res=collections.Counter();rows=[]
for s,T in ry.items():
    blks={t//8 for t in T}
    if len(blks)<2: continue
    I={x for x in range(512) if all(dot(x,P[t])==0 for t in T)}
    F=sp(cur[s]) if cur[s] else {0}
    inter=len([x for x in F if x in I]).bit_length()-1
    dF=len(cur[s]);dI=len(I).bit_length()-1
    rows.append((s,len(T),len(blks),dF,dI,dF-inter))
    res[(len(blks),dF-inter)]+=1
print('regs read directly by y of >=2 blocks:',len(rows))
print('(nblocks, excess of final frame over ∩perp):count',sorted(res.items()))
print('dim ∩ distribution',collections.Counter(r[4] for r in rows))
print('final dim dist',collections.Counter(r[3] for r in rows))
print(rows[:10])
print('s=283',[r for r in rows if r[0]==283])

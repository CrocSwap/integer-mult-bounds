from an1 import *
def dot(a,b): return bin(a&b).count('1')&1
w=load(__import__('os').environ['EO_ROOT']+'/work/o_base/FULL-WORD.json.gz');P=w['ports'];cur,rd=frames(w)
ry=collections.defaultdict(set)
for y in range(V,2*V):
    for s in rd[y]: ry[s].add(y-V)
ops=collections.defaultdict(list)
for part in 'AB':
    for e in w[part]:
        F=G.basis(e[-1])
        for r in [e[1]]+([e[2]] if e[0]=='add' else []): ops[r].append(F)
tot=[];cnt=collections.Counter()
for s,T in ry.items():
    if len({t//8 for t in T})<2: continue
    I={x for x in range(512) if all(dot(x,P[t])==0 for t in T)}
    ex=0;nb=0
    for F in ops[s]:
        S=sp(F) if F else {0}
        i=(len([x for x in S if x in I])).bit_length()-1
        if i<len(F): ex+=len(F)-i;nb+=1
    tot.append((ex,nb,len(ops[s])));
import statistics
print('n',len(tot),'sum excess per reg: min/median/max',min(t[0] for t in tot),statistics.median(t[0] for t in tot),max(t[0] for t in tot))
print('bad ops per reg median',statistics.median(t[1] for t in tot),'ops per reg median',statistics.median(t[2] for t in tot))
print(collections.Counter(t[0] for t in tot).most_common(8))
# fraction of regs with all ops fitting
print('regs with 0 excess',sum(1 for t in tot if t[0]==0))
# same for pairs only (T size 2)

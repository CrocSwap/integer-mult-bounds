from an1 import *
def dot(a,b): return bin(a&b).count('1')&1
wb=load(__import__('os').environ['EO_ROOT']+'/work/o_base/FULL-WORD.json.gz');wc=load(__import__('os').environ['EO_ROOT']+'/work/o_cf0/FULL-WORD.json.gz')
cb,rb=frames(wb);cc,rc=frames(wc);P=wb['ports']
diff=[r for r in cb if r in cc and len(cb[r])!=len(cc[r])]
print('regs whose final frame dim differs base->cf0:',[(r,len(cb[r]),len(cc[r])) for r in diff])
ry=collections.defaultdict(set)
for y in range(V,2*V):
    for s in rc[y]: ry[s].add(y-V)
ops=collections.defaultdict(list)
for e in wc['A']+wc['B']:
    F=G.basis(e[-1])
    for r in [e[1]]+([e[2]] if e[0]=='add' else []): ops[r].append(F)
for s in diff:
    T=ry.get(s,set())
    if not T: print(s,'no direct y reader');continue
    I={x for x in range(512) if all(dot(x,P[t])==0 for t in T)}
    ex=0
    for F in ops[s]:
        S=sp(F) if F else {0}
        i=len([x for x in S if x in I]).bit_length()-1
        ex+=len(F)-i
    print(s,'T',sorted(T),'blocks',sorted({t//8 for t in T}),'dimI',len(I).bit_length()-1,'final',len(cc[s]),'op-excess',ex)

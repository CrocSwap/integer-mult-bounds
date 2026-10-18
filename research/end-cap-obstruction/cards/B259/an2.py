from an1 import *
import random
w=load(__import__('os').environ['EO_ROOT']+'/work/o_cf0/FULL-WORD.json.gz');P=w['ports'];cur,rd=frames(w)
bad=[58,59,62,63]
Iv=[P[t] for t in bad]
Ispace=G.basis([x for x in sp(G.perp(Iv[0]))]) if False else None
# I = intersection of perps: vectors x with x.u=0 for all u
def dot(a,b): return bin(a&b).count('1')&1
Iset=[x for x in range(512) if all(dot(x,u)==0 for u in Iv)]
print('|I|',len(Iset),'dim',len(Iset).bit_length()-1)
Is=set(Iset)
for t in bad:
    y=V+t;print('y',y,'final dim',len(cur[y]),'readers',sorted(rd[y]))
    for s in sorted(rd[y]):
        S=sp(cur[s]) if cur[s] else {0}
        inter=len([x for x in S if x in Is])
        print('   src',s,'final frame dim',len(cur[s]),'|S∩I|',inter,'dim excess over I',len(cur[s])-(inter.bit_length()-1))

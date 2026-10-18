import gzip,json,itertools,collections
w=json.loads(gzip.decompress(open(__import__('os').environ['EO_ROOT']+'/inputs/words/w1018.json.gz','rb').read()))
P=w['ports'];V=112
def dot(a,b): return bin(a&b).count('1')&1
def rank(vs):
    b=[];
    for v in vs:
        for x in b: v=min(v,v^x)
        if v: b.append(v)
    return len(b)
S=set(P); assert len(S)==112
print('self-dot all 1:',all(dot(p,p)==1 for p in P))
print('cap (no 3 xor 0):', not any((a^b) in S for a,b in itertools.combinations(P,2)))
# zero-sum quads
quads=[q for q in itertools.combinations(range(V),3) if (P[q[0]]^P[q[1]]^P[q[2]]) in S and P.index(P[q[0]]^P[q[1]]^P[q[2]])>q[2]]
print('zero-sum 4-sets (span dim3 with 4 ports):',len(quads))
blk=lambda i:i//8
print('block spans:',[rank(P[8*b:8*b+8]) for b in range(14)])
c=collections.Counter(tuple(sorted(collections.Counter(blk(i) for i in q).values())) for q in quads)
print('quad block patterns:',c)
# orthogonality graph
O=[[dot(P[i],P[j]) for j in range(V)] for i in range(V)]
deg0=[sum(1 for j in range(V) if j!=i and O[i][j]==0) for i in range(V)]
print('orth degree (excluding self):',collections.Counter(deg0))
# within block orthogonality
for b in range(2):
    print('block',b,[[O[i][j] for j in range(8*b,8*b+8)] for i in range(8*b,8*b+8)])
# common-orth source counts for groups
def corth(T): return [s for s in range(V) if all(O[s][t]==0 for t in T)]
pc=collections.Counter(len(corth(p)) for p in itertools.combinations(range(V),2))
print('pairs: #ports in perp(u_a)∩perp(u_b):',sorted(pc.items()))
qc=collections.Counter(len(corth(q)) for q in quads)
print('quads: #ports in common perp (dim6):',sorted(qc.items()))
tc=collections.Counter(len(corth(q)) for q in itertools.combinations(range(V),3))
print('triples: #ports in common perp:',sorted(tc.items()))
# within/cross block pairs
pcb=collections.Counter((blk(a)==blk(b),O[a][b]) for a,b in itertools.combinations(range(V),2))
print('pairs (sameblock, dot):',pcb)

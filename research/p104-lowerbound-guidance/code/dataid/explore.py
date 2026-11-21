import json, itertools, re, ast
W='<research-tree>/cards/WILD/'
D=W+'LUNCH/exchange/d56dir/mod4/'
def npy(path):
    import struct
    b=open(path,'rb').read()
    hl=struct.unpack('<H',b[8:10])[0]
    hdr=ast.literal_eval(b[10:10+hl].decode())
    data=b[10+hl:]
    sh=hdr['shape']; dt=hdr['descr']
    n=sh[0]*sh[1]
    sz={'<i8':8,'<i4':4,'<f8':8}[dt]
    f={'<i8':'q','<i4':'i','<f8':'d'}[dt]
    v=struct.unpack('<%d%s'%(n,f),data[:n*sz])
    return [list(map(int,v[i*sh[1]:(i+1)*sh[1]])) for i in range(sh[0])]
G=npy(W+'REBASET1/G104.npy')
lab=list(map(int,open(D+'labels.txt').read().split()))
L1=json.load(open(W+'REBASET1/lines104.json'))
print(lab==L1, len(lab))
E8=json.load(open(D+'e8base.json'))
b=E8['basis'];Gb=E8['Gb'];C=E8['C']
print(b, len(C))
print(all(G[i][j]==sum(C[i][a]*Gb[a][c]*C[j][c] for a in range(8) for c in range(8)) for i in range(104) for j in range(104)))
# xMasks
src=open('<research-tree>/lean/decoder-duality/Nov15/LinP104Base.lean').read()
def getlist(name):
    m=re.search(r'def '+name+r' : List Nat := \[([^\]]*)\]',src); return list(map(int,m.group(1).split(',')))
X=getlist('xMasks'); BM=getlist('bmMasks'); BI=getlist('binvMasks'); LM=getlist('labMasks')
print(LM==lab)
print(X==[sum((C[t][i]%2)<<i for i in range(8)) for t in range(104)])
print(BM==[sum((Gb[i][j]%2)<<j for j in range(8)) for i in range(8)])
dot=lambda a,c: bin(a&c).count('1')&1
print(all(dot(lab[t],lab[s])==(G[t][s]+1)%2 for t in range(104) for s in range(104)))
print(sorted(set(v for r in G for v in r)))
fr=[list(map(int,l.split())) for l in open(D+'frames.txt').read().strip().split('\n')[1:]]
print(len(fr), fr[:2])
# 8-cliques
adj=[[G[i][j]==0 for j in range(104)] for i in range(104)]
cl=[]
def rec(cur,cand):
    if len(cur)==8: cl.append(tuple(cur));return
    for k,v in enumerate(cand):
        rec(cur+[v],[w for w in cand[k+1:] if adj[v][w]])
rec([],list(range(104)))
print(len(cl), set(map(tuple,fr))==set(cl), fr==[list(c) for c in cl])

import sys; sys.path.insert(0,'<word-rung-package>/tools')
import pricekit as pk
W=pk.load('<word-rung-package>/data/t7669.json.gz')
print(W['ports'][:6], W['live'][:6], W['frames'][:4], W['hosted']['Dports'][:6], W['hosted']['X2'][:4], W['hosted']['Y2'][:4], W['hosted']['mode'], W['hosted']['alpha'] if not isinstance(W['hosted']['alpha'],list) else W['hosted']['alpha'][:3])
dot=lambda a,b: bin(a&b).count('1')&1
def inspan(B,v):
    S={0}
    for b in B:
        S|={x^b for x in S}
    return v in S
F=W['frames']; ports=W['ports']; ini=W['initial']; fin=W['final']
ok=0
for p,r in enumerate(W['live']):
    q=ports[p]
    X=r; Y=r+112
    a=inspan(F[ini[X]],q); b=all(dot(x,q)==0 for x in F[fin[Y]])
    ok+= a and b
print('live ok',ok)
# test alternative: ports indexed by position vs by register id
print(len(set(map(tuple,map(lambda x:[x],ports)))))

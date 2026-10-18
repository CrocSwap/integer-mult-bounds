import sys,gzip,json
sys.path.insert(0,(__import__('os').environ['HM_ROOT']+'/cards/B99/work'))
import lib
d=lib.load()
w=json.load(gzip.open((__import__('os').environ['HM_ROOT']+'/inputs/words/656-layers-FULL-WORD.json.gz')))
def basis(vs):
    piv={}
    for a in vs:
        while a:
            bit=a.bit_length()-1
            if bit in piv:a^=piv[bit]
            else:piv[bit]=a;break
    for k in sorted(piv):
        for j in piv:
            if j>k and piv[j]>>k&1:piv[j]^=piv[k]
    return tuple(piv[k] for k in sorted(piv,reverse=True))
pi={}
for p in 'AB':
  for a,b in zip(d[p],w[p]):
    rs=[1,2] if a[0]=='add' else [1]
    for j in rs: pi[b[j]]=a[j]
# solve T: columns. gaussian: find T with T(x_i)=y_i for pairs (full port -> canon port)
pairs=[(w['ports'][r],d['ports'][pi[r]]) for r in range(112)]
def solve(pairs):
    # find 9x9 matrix M (as list of images of basis e_k) s.t. M(x)=y for all pairs; linear system over GF(2)
    # unknown images of e_0..e_8; use elimination on (x,y) pairs
    piv={}
    for x,y in pairs:
        for b,(px,py) in list(piv.items()):
            pass
    # reduce: maintain basis of x with tracked y
    rows=[]
    for x,y in pairs:
        for (px,py) in rows:
            if x&(px&-px) and False:pass
        rows.append((x,y))
    B={}
    for x,y in pairs:
        while x:
            bit=x.bit_length()-1
            if bit in B: x^=B[bit][0]; y^=B[bit][1]
            else: B[bit]=(x,y);break
        else:
            if y: return None
    return B
B=solve(pairs)
print('consistent' if B else 'inconsistent', len(B) if B else '')
def apply(B,x):
    y=0
    while x:
        bit=x.bit_length()-1
        if bit not in B:return None
        x^=B[bit][0];y^=B[bit][1]
    return y
if B and len(B)==9:
    bad=0;tot=0
    for p in 'AB':
      for a,b in zip(d[p],w[p]):
        tot+=1
        if basis([apply(B,x) for x in b[-1]])!=basis(d['frames'][a[-1]]): bad+=1
    print('frame map bad',bad,tot)

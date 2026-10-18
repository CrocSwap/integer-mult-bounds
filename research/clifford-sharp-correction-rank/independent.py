"""Code-separated Gaussian-rational audit of the full 32-dimensional witness.

Does not import the builder, its spectrum formula, FWHT, or native interpreter.
"""
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ZERO, ONE, I = (Q(0),Q(0)),(Q(1),Q(0)),(Q(0),Q(1))

def require(ok,why):
    if not ok: raise ValueError(why)

def plus(a,b): return a[0]+b[0],a[1]+b[1]
def minus(a,b): return a[0]-b[0],a[1]-b[1]
def times(a,b): return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]
def divide(a,b):
    d=b[0]*b[0]+b[1]*b[1]
    return (a[0]*b[0]+a[1]*b[1])/d,(a[1]*b[0]-a[0]*b[1])/d

def matrix_product(a,b):
    out=[[ZERO for _ in b[0]] for _ in a]
    for i,row in enumerate(a):
        for k,x in enumerate(row):
            if x!=ZERO:
                for j,y in enumerate(b[k]):
                    if y!=ZERO: out[i][j]=plus(out[i][j],times(x,y))
    return out

def difference(a,b): return [[minus(x,y) for x,y in zip(ar,br)] for ar,br in zip(a,b)]
def unit(n): return [[ONE if i==j else ZERO for j in range(n)] for i in range(n)]
def transpose(a): return [list(row) for row in zip(*a)]

def rank(a):
    a=[list(row) for row in a]
    count=0
    for j in range(len(a[0])):
        p=next((p for p in range(count,len(a)) if a[p][j]!=ZERO),None)
        if p is None: continue
        a[p],a[count]=a[count],a[p]
        z=a[count][j]
        a[count]=[divide(x,z) for x in a[count]]
        for k in range(count+1,len(a)):
            z=a[k][j]
            if z!=ZERO: a[k]=[minus(x,times(z,y)) for x,y in zip(a[k],a[count])]
        count+=1
    return count

def kernel(h):
    n=2**h
    out=[]
    for x in range(n):
        row=[]
        for y in range(n):
            z=ONE
            for j in range(h):
                z=times(z,(Q(1,2),Q(-1 if (x^y)>>j&1 else 1,2)))
            row.append(z)
        out.append(row)
    return out

def deserialize(cols,den):
    require(type(den) is int and den>0,'integer positive denominator')
    require(len(cols)==32 and all(len(c)==32 for c in cols),'full matrix extent')
    for col in cols:
        for entry in col:
            require(type(entry) is list and len(entry)==2 and all(type(x) is int for x in entry),'Gaussian integer field')
    return transpose([[(Q(a,den),Q(b,den)) for a,b in col] for col in cols])

def run():
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row.get('usage')=='input':
            data=(ROOT/row['path']).read_bytes()
            require(hashlib.sha256(data).hexdigest()==row['sha256'],'independent source hash')
            require(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob'],'independent Git blob')
    w=json.loads((HERE/'WITNESS.json').read_text())
    require(w['s']==4 and w['h']==5 and w['direction']==1 and w['phase']==2,'literal witness contract')
    e=deserialize(w['encoding_columns'],w['encoding_denominator'])
    f=deserialize(w['correction_columns'],w['correction_denominator'])
    h=[[(-a,-b) for a,b in row] for row in kernel(5)]
    t=[[ZERO for _ in range(32)] for _ in range(32)]
    c=kernel(1)
    for lane in range(16):
        for a in range(2):
            for b in range(2): t[2*lane+a][2*lane+b]=c[a][b]
    left=matrix_product(matrix_product(f,h),e)
    right=matrix_product(e,t)
    require(left==right,'complete native-coordinate F H E = E T')
    delta=difference(f,unit(32))
    require(rank(e)==32 and rank(f)==32,'rational encoding/correction invertibility')
    require(rank(delta)==6,'exact Gaussian correction rank six')
    require(matrix_product(delta,delta)==[[ZERO]*32 for _ in range(32)],'nilpotent correction')
    # Reconstruct six outer products using direct Walsh entries, without the builder's transform.
    u,v=[],[]
    for a,b in w['pairs']:
        wa=[-1 if (x&a).bit_count()%2 else 1 for x in range(32)]
        wb=[-1 if (x&b).bit_count()%2 else 1 for x in range(32)]
        u.append([(Q(x+y),Q(0)) for x,y in zip(wa,wb)])
        v.append([(Q(0),Q(y-x,16)) for x,y in zip(wa,wb)])
    require(len(u)==6 and not w['signs'],'six actual shear factors')
    require(matrix_product(transpose(u),v)==delta,'rank-six U V-transpose decomposition')
    require(matrix_product(v,transpose(u))==[[ZERO]*6 for _ in range(6)],'mutually annihilating shears')
    require(rank(u)==rank(v)==6,'independent update and read directions')
    # All four phases have lower bounds [10,10,6,10], reconstructed by actual eigenvector signs.
    bounds=[]
    for phase in range(4):
        counts=[sum((phase+x.bit_count())%4==j for x in range(32)) for j in range(4)]
        bounds.append(max(abs(16-counts[0]),abs(16-counts[1]),counts[2],counts[3]))
    require(bounds==[10,10,6,10],'phase-specific minimum cannot be five')
    controls=[]
    changed=[row[:] for row in f]
    changed[0][0]=plus(changed[0][0],ONE)
    require(matrix_product(matrix_product(changed,h),e)!=right,'changed full correction rejected')
    controls.append('wrong correction coefficient')
    require(matrix_product(matrix_product(f,[[(-a,-b) for a,b in row] for row in h]),e)!=right,'wrong phase rejected')
    controls.append('wrong global phase')
    require(matrix_product(transpose(u[:-1]),v[:-1])!=delta,'five-shear truncation rejected')
    controls.append('missing sixth shear')
    changed=[row[:] for row in e]
    changed[0][0]=plus(changed[0][0],ONE)
    require(matrix_product(matrix_product(f,h),changed)!=matrix_product(changed,t),'wrong encoder rejected')
    controls.append('wrong encoder')
    # Sharing an unchanged spectator multiplies algebraic rank, not host width.
    lifted=[[delta[i//2][j//2] if i%2==j%2 else ZERO for j in range(64)] for i in range(64)]
    require(rank(lifted)==12,'spectator rank is multiplied')
    return len(controls)

if __name__=='__main__':
    print('PASS_INDEPENDENT_SHARP_CORRECTION full_dimension=32 rank=6 controls='+str(run()))

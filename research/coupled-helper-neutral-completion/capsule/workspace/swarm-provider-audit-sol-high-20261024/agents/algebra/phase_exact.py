"""Independent nine-bit signed-Pauli and exact anchor circuit evaluator.

No submitted or source evaluator import. Equality is the complete 18-generator
Pauli action plus the full image of |0>, which fixes the scalar phase.
"""
from functools import lru_cache

N=9

def parity(x): return x.bit_count()%2

def mv(rows,x): return sum(parity(r&x)<<j for j,r in enumerate(rows))

def transpose(rows): return tuple(sum(((rows[i]>>j)&1)<<i for i in range(N)) for j in range(N))

def invert(rows):
    a=[row | (1<<(N+j)) for j,row in enumerate(rows)]
    for j in range(N):
        k=next(i for i in range(j,N) if a[i]>>j&1)
        a[j],a[k]=a[k],a[j]
        for i in range(N):
            if i!=j and a[i]>>j&1:a[i]^=a[j]
    if [x&511 for x in a]!=[1<<j for j in range(N)]:raise ValueError('singular map')
    return tuple(x>>N for x in a)

def rank(rows):
    basis={}
    for x in rows:
        while x:
            k=x.bit_length()-1
            if k not in basis:basis[k]=x;break
            x^=basis[k]
    return len(basis)

def freeze(word):return tuple(tuple(tuple(x) if isinstance(x,list) else x for x in e) for e in word)

def adjoint(word):
    result=[]
    for e in reversed(word):
        if e[0]=='P':result.append(('P',invert(e[1])))
        elif e[0]=='D':result.append(('D',e[1],tuple(-v%4 for v in e[2])))
        elif e[0]=='C':result.append(('C',e[1],-e[2]))
        elif e[0]=='phase':result.append(('phase',-e[1]%4))
        else:result.append(e)
    return tuple(result)

def conjugate(word):
    return tuple(('D',e[1],tuple(-v%4 for v in e[2])) if e[0]=='D' else
                 ('C',e[1],-e[2]) if e[0]=='C' else
                 ('phase',-e[1]%4) if e[0]=='phase' else e for e in word)

def polynomial(e,x):
    Q,alpha=e[1:]
    return (sum(alpha[j] for j in range(N) if x>>j&1)+
            2*sum(parity(Q[j]&x&~((1<<(j+1))-1)) for j in range(N) if x>>j&1))%4

def pauli(word,x,z,p=0):
    for e in word:
        if e[0]=='P':x,z=mv(e[1],x),mv(transpose(invert(e[1])),z)
        elif e[0]=='X':p+=2*parity(z&e[1])
        elif e[0]=='D':
            q=polynomial(e,x)
            z^=sum((((polynomial(e,x^(1<<j))-polynomial(e,1<<j)-q)%4)//2)<<j for j in range(N))
            p+=q
        elif e[0]=='C':
            if parity(z&e[1]):x^=e[1];p-=e[2]
        elif e[0]!='phase':raise ValueError('unsupported gate')
    return x,z,p%4

def rot(v,p):
    a,b=v
    return ((a,b),(-b,a),(-a,-b),(b,-a))[p%4]

@lru_cache(None)
def signature(word):
    tab=tuple(pauli(word,1<<j,0) for j in range(N))+tuple(pauli(word,0,1<<j) for j in range(N))
    values=[(0,0)]*512;values[0]=(1,0);den=0
    for e in word:
        if e[0]=='P':
            out=[(0,0)]*512
            for x,v in enumerate(values):out[mv(e[1],x)]=v
            values=out
        elif e[0]=='X':values=[values[x^e[1]] for x in range(512)]
        elif e[0]=='D':values=[rot(v,polynomial(e,x)) for x,v in enumerate(values)]
        elif e[0]=='phase':values=[rot(v,e[1]) for v in values]
        elif e[0]=='C':
            out=[]
            for x,v in enumerate(values):
                # ((1+s*i)*a+(1-s*i)*b)/2
                u=values[x^e[1]];s=e[2]
                out.append((v[0]-s*v[1]+u[0]+s*u[1],v[1]+s*v[0]+u[1]-s*u[0]))
            values=out;den+=1
        else:raise ValueError('unsupported gate')
        while den and all(not (a%2 or b%2) for a,b in values):
            values=[(a//2,b//2) for a,b in values];den-=1
    return tab,tuple(values),den

def frame(U):
    r=len(U)
    if not r:return ()
    if r==N:return tuple(('C',1<<j,1) for j in range(N))
    basis=[]
    for q in list(U)+[1<<j for j in range(N)]:
        if rank(basis+[q])>len(basis):basis.append(q)
    G=transpose(basis);gi=invert(G);cols=transpose(gi)
    Q=tuple((1<<j)^sum(parity(cols[j]&cols[k])<<k for k in range(N)) for j in range(N))
    K=(('P',G),('D',Q,tuple((Q[j]>>j)&1 for j in range(N))))
    return adjoint(K)+tuple(('C',1<<j,1) for j in range(r))+K

def equal(a,b):return signature(tuple(a))==signature(tuple(b))

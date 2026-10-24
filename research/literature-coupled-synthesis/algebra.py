"""Small exact engines for paper-to-interface experiments. Apache-2.0.
New code by zxv with OpenAI Codex assistance; source Clifford engine is attributed separately.
"""
from fractions import Fraction as F
from collections import deque

def need(ok, message):
    if not ok:
        raise ValueError(message)

def eye(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]

def transpose(a):
    return list(map(list, zip(*a)))

def mm(a, b):
    bt = transpose(b)
    return [[sum((x*y for x,y in zip(r,c) if x and y), F()) for c in bt] for r in a]

def add(a,b,c=1):
    return [[x+c*y for x,y in zip(r,s)] for r,s in zip(a,b)]

def rank(a):
    a = [[F(x) for x in r] for r in a]
    if not a:
        return 0
    k = 0
    for j in range(len(a[0])):
        p = next((i for i in range(k,len(a)) if a[i][j]), None)
        if p is None:
            continue
        a[k],a[p] = a[p],a[k]
        v = a[k][j]; a[k] = [x/v for x in a[k]]
        for i in range(k+1,len(a)):
            v = a[i][j]
            if v:
                a[i] = [x-v*y for x,y in zip(a[i],a[k])]
        k += 1
        if k == len(a):
            break
    return k

def gf_basis(rows):
    b = {}
    for x in rows:
        while x:
            j = x.bit_length()-1
            if j not in b:
                b[j] = x
                break
            x ^= b[j]
    for j in sorted(b):
        for k in b:
            if k > j and b[k] >> j & 1:
                b[k] ^= b[j]
    return tuple(b[j] for j in sorted(b))

def inverse(a):
    n = len(a); r = [list(map(F,row))+tail for row,tail in zip(a,eye(n))]
    for j in range(n):
        p = next((i for i in range(j,n) if r[i][j]),None)
        need(p is not None,'invertible matrix')
        r[j],r[p] = r[p],r[j]
        v = r[j][j]; r[j] = [x/v for x in r[j]]
        for i in range(n):
            if i != j:
                v = r[i][j]
                if v:
                    r[i] = [x-v*y for x,y in zip(r[i],r[j])]
    return [row[n:] for row in r]

def reversible_path(length, pebbles):
    """Exact BFS reversible pebble game. Node 0 is permanent and uncharged.
    Toggle i only while predecessor i-1 is present. End with only node length.
    Measures graph moves, not physical Gaussian work.
    """
    start=0; target=1 << (length-1); todo=deque([start]); prev={start:None}
    while todo:
        s=todo.popleft()
        if s == target:
            path=[]
            while prev[s] is not None:
                old,i=prev[s];path.append(i);s=old
            return list(reversed(path))
        for i in range(length):
            if i and not s >> (i-1) & 1:
                continue
            t=s^(1<<i)
            if t.bit_count() <= pebbles and t not in prev:
                prev[t]=(s,i+1);todo.append(t)
    return None

def binary_elimination(rows, block=1):
    """Patel-style duplicate panel elimination, then Gauss-Jordan cleanup.
    Restricted small-matrix adaptation, not the paper's asymptotic algorithm.
    Every XOR/swap is recorded and replayed exactly.
    """
    n=len(rows); a=list(rows); ops=[]
    def xor(i,j):
        a[i]^=a[j];ops.append(['xor',i,j])
    for lo in range(0,n,block):
        seen={}; mask=((1 << min(block,n-lo))-1) << lo
        for i in range(lo,n):
            p=a[i]&mask
            if p and p in seen:
                xor(i,seen[p])
            elif p:
                seen[p]=i
        for j in range(lo,min(lo+block,n)):
            p=next(i for i in range(j,n) if a[i]>>j&1)
            if p != j:
                # Three CNOTs implement one row swap.
                xor(p,j);xor(j,p);xor(p,j)
            for i in range(j+1,n):
                if a[i]>>j&1:xor(i,j)
    for j in reversed(range(n)):
        for i in range(j):
            if a[i]>>j&1:xor(i,j)
    need(a==[1<<i for i in range(n)],'binary elimination endpoint')
    b=list(rows)
    for _,i,j in ops:b[i]^=b[j]
    need(a==b,'CNOT replay')
    return ops

def coupled_program(m,a):
    """In normalized K frames: H(a,-12/a) = [[I-WZ,aW],[-12Z/a,13I]].
    W=M/2, Z=M^T/2, ZW=14I. All 120 inputs arbitrary. No scratch.
    Physical Kp/Km boundary maps are counted separately in the caller.
    """
    ops=[]
    for k in range(8):ops.append(['scale',112+k,str(a)])
    for k in range(8):
        for i in range(112):
            if m[k][i]:ops.append(['add',112+k,i,str(-F(m[k][i],2))])
    for i in range(112):
        for k in range(8):
            if m[k][i]:ops.append(['add',i,112+k,str(F(m[k][i],2))])
    for k in range(8):ops.append(['scale',112+k,str(-1/a)])
    for k in range(8):
        for i in range(112):
            if m[k][i]:ops.append(['add',112+k,i,str(F(m[k][i],2)/a)])
    return ops

def replay(program, rows):
    a=[r[:] for r in rows]
    for e in program:
        if e[0]=='scale':a[e[1]]=[F(e[2])*v for v in a[e[1]]]
        elif e[0]=='add':
            _,i,j,c=e;need(i!=j,'distinct ADD fields')
            a[i]=[x+F(c)*y for x,y in zip(a[i],a[j])]
        else:raise ValueError(e)
    return a

def lagrange_weights(xs, at=0):
    out=[]
    for i,x in enumerate(xs):
        w=F(1)
        for j,y in enumerate(xs):
            if i!=j:w*=F(at-y,x-y)
        out.append(w)
    return out

def coupled_program_dual(m,a):
    """Transpose the normalized scalar H(b,a) program, where b=-12/a.
    Swap ADD source/destination and reverse chronology. This can avoid odd
    divisions when b, rather than a, is a dyadic unit. No-op scales are omitted.
    Physical K boundary maps are wrapped afterward, not transposed.
    """
    out=[]
    for e in reversed(coupled_program(m,-12/a)):
        if e[0]=='add':out.append(['add',e[2],e[1],e[3]])
        elif F(e[2])!=1:out.append(e[:])
    return out

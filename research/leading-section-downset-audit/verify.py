"""Independent exact LDU/downset oracle; no predecessor verifier imported."""
import ast
import copy
import importlib.util
import json
from fractions import Fraction as Q
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
SOURCE = "research/capped-phase-fusion/evidence/inplace_algebra_ultra/check_circuits.py"
spec = importlib.util.spec_from_file_location("scalar", ROOT/"research/rational-unitary-fft/exact.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
C = module.C


def need(ok, message):
    if not ok:
        raise ValueError(message)


class Matrix(list):
    def __init__(self, rows):
        super().__init__([[x if isinstance(x,C) else C(x) for x in row] for row in rows])
    @property
    def T(self):
        return Matrix(zip(*self))
    def __getitem__(self, key):
        if not isinstance(key,tuple):return super().__getitem__(key)
        i,j = key
        if isinstance(i,int) and isinstance(j,int):return super().__getitem__(i)[j]
        return Matrix([row[j] for row in super().__getitem__(i)])
    def __matmul__(self, other):return mul(self,other)
    def __sub__(self, other):return Matrix([[x-y for x,y in zip(a,b)] for a,b in zip(self,other)])


def eye(n):return Matrix([[int(i==j) for j in range(n)] for i in range(n)])


def mul(a,b):
    return Matrix([[sum((a[i][k]*b[k][j] for k in range(len(b))),C())
                    for j in range(len(b[0]))] for i in range(len(a))])


def inv(a):
    n=len(a); rows=[list(x)+list(y) for x,y in zip(a,eye(n))]
    for k in range(n):
        pivot=next((i for i in range(k,n) if rows[i][k]!=0),None)
        need(pivot is not None,"singular leading section")
        rows[k],rows[pivot]=rows[pivot],rows[k]
        q=rows[k][k];rows[k]=[x/q for x in rows[k]]
        for i in range(n):
            if i!=k:
                q=rows[i][k];rows[i]=[x-q*y for x,y in zip(rows[i],rows[k])]
    return Matrix([row[n:] for row in rows])


def ldu(t):
    n=len(t);a=Matrix(t);lo,di,up=eye(n),eye(n),eye(n)
    for k in range(n):
        pivot=a[k][k];need(pivot!=0,"singular leading section");di[k][k]=pivot
        for j in range(k+1,n):up[k][j]=a[k][j]/pivot
        for i in range(k+1,n):
            lo[i][k]=a[i][k]/pivot
            for j in range(k+1,n):a[i][j]=a[i][j]-lo[i][k]*a[k][j]
    need(mul(mul(lo,di),up)==t,"independent LDU endpoint")
    return lo,di,up


def block(a,lo,hi):return Matrix([row[lo:hi] for row in a[lo:hi]])


def embed(a,lo,n):
    out=eye(n)
    for i,row in enumerate(a):
        for j,x in enumerate(row):out[lo+i][lo+j]=x
    return out


def envelope(a):
    def mass(row):return sum((abs(x.re)+abs(x.im) for x in row),Q(0))
    return max(max(map(mass,a)),max(map(mass,zip(*a))))


def schur(t,a,b):
    if a==0:return block(t,0,b)
    return block(t,a,b)-mul(mul(Matrix([row[:a] for row in t[a:b]]),inv(block(t,0,a))),
                            Matrix([row[a:b] for row in t[:a]]))


def trees(a,b):
    if b-a==1:return [(a,b,None,None)]
    return [(a,b,l,r) for c in range(a+1,b) for l in trees(a,c) for r in trees(c,b)]


def build(t,tree,atoms):
    a,b,left,right=tree;n=len(t);m=schur(t,a,b)
    lo,di,up=ldu(m)
    node=dict(a=a,b=b,lo=lo,di=di,up=up)
    if left is None:
        token=("D",a,b);atoms.append((token,embed(m,a,n)))
        node.update(ids={token},token=token,left=None,right=None)
    else:
        c=left[1];split=c-a
        aa=block(m,0,split);bb=Matrix([row[split:] for row in m[:split]])
        cc=Matrix([row[:split] for row in m[split:]])
        k,h=mul(inv(aa),bb),mul(cc,inv(aa))
        upper,lower=eye(n),eye(n)
        for i in range(split):
            for j in range(b-c):upper[a+i][c+j]=k[i][j]
        for i in range(b-c):
            for j in range(split):lower[c+i][a+j]=h[i][j]
        rt,lt=("R",a,b),("L",a,b);atoms.append((rt,upper))
        ln,rn=build(t,left,atoms),build(t,right,atoms)
        atoms.append((lt,lower))
        node.update(ids=ln['ids']|rn['ids']|{rt,lt},token=rt,left=ln,right=rn)
        # Independently check the block endpoint quotient.
        children=mul(embed(schur(t,a,c),a,n),embed(schur(t,c,b),c,n))
        need(mul(mul(lower,children),upper)==embed(m,a,n),"ancestor Schur split endpoint")
    return node


def states(node):
    if node['left'] is None:return [set(),set(node['ids'])]
    return [set()]+[{node['token']}|a|b for a in states(node['left']) for b in states(node['right'])]+[set(node['ids'])]


def collected(node,state,n,kind):
    if kind=='lower' and node['ids']<=state:return embed(node['lo'],node['a'],n)
    if kind=='upper' and (node['left'] is None or node['token'] not in state):
        return embed(node['up'],node['a'],n)
    if node['left'] is None:return eye(n)
    return mul(collected(node['left'],state,n,kind),collected(node['right'],state,n,kind))


def audit(t,selected_trees):
    n=len(t);lo,di,up=ldu(t);li,ui=inv(lo),inv(up)
    lam=max(Q(1),envelope(t));q=max(Q(1),*(envelope(inv(block(t,0,k))) for k in range(1,n+1)))
    chi=lam*q;u0=lam+lam*lam*q
    need(mul(mul(di,up),inv(t))==li and mul(mul(inv(t),lo),di)==ui,"global inverse factor order")
    for k in range(1,n):
        right=mul(inv(block(t,0,k)),Matrix([row[k:] for row in t[:k]]))
        lower=mul(Matrix([row[:k] for row in t[k:]]),inv(block(t,0,k)))
        need(right[-1]==up[k-1][k:],"original last-row solve")
        need([row[-1] for row in lower]==[row[k-1] for row in lo[k:]],"original last-column solve")
        need(sum((x.norm2() for x in right[-1]),Q(0))<=chi*chi,"upper tail Euclidean budget")
        need(sum((row[-1].norm2() for row in lower),Q(0))<=chi*chi,"lower tail Euclidean budget")
    count=mixed=0;noncommuting=False
    for tree in selected_trees:
        atoms=[];node=build(t,tree,atoms)
        def restrictions(v):
            a,b=v['a'],v['b']
            need((v['lo'],v['di'],v['up'])==(block(lo,a,b),block(di,a,b),block(up,a,b)),"global factor restriction")
            need(inv(v['lo'])==block(li,a,b) and inv(v['up'])==block(ui,a,b),"contiguous inverse restriction")
            if v['left'] is not None:restrictions(v['left']);restrictions(v['right'])
        restrictions(node)
        for state in states(node):
            endpoint=eye(n)
            for token,a in atoms:
                if token in state:endpoint=mul(a,endpoint)
            lc,uf=collected(node,state,n,'lower'),collected(node,state,n,'upper')
            dpart=eye(n)
            for k in range(n):
                if ('D',k,k+1) in state:dpart[k][k]=di[k][k]
            rhs=mul(mul(mul(lc,dpart),inv(uf)),up)
            need(endpoint==rhs,"noncommuting frontier order")
            need(inv(endpoint)==mul(mul(mul(ui,uf),inv(dpart)),inv(lc)),"downset inverse order")
            # Spectral norm squared <= norm_1 * norm_inf <= envelope^2.
            # The exact radical-free common theorem bound squared is 1024 N^3 chi^16.
            need(max(envelope(endpoint)**2,envelope(inv(endpoint))**2)<=1024*n**3*chi**16,
                 "completed downset common norm budget")
            noncommuting |= endpoint!=mul(mul(mul(lc,dpart),up),inv(uf))
            mixed += int(lc!=eye(n) and uf!=eye(n))
            count+=1
    return dict(n=n,trees=len(selected_trees),downsets=count,mixed_lower_frontier=mixed),noncommuting


def source_binding(t):
    n=len(t);tree=ast.parse((ROOT/SOURCE).read_bytes())
    defs=[copy.deepcopy(x) for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in {'full_plan','parallel'}]
    need(len(defs)==2,"retained structural function selection")
    def diagonal(ids,values):
        a=eye(n)
        for i,v in zip(ids,values):a[i][i]=v
        return [[a]]
    def shear(target,source,k):
        a=eye(n)
        for i,x in enumerate(target):
            for j,y in enumerate(source):a[x][y]=k[i][j]
        return [[a]]
    env=dict(STATS={'full_nodes':0},diag=diagonal,lowdisp_shear=shear,
             np=SimpleNamespace(linalg=SimpleNamespace(solve=lambda a,b:mul(inv(a),b))))
    mod=ast.Module(body=defs,type_ignores=[]);ast.fix_missing_locations(mod)
    exec(compile(mod,'<retained full_plan algebra only>','exec',optimize=0),env)
    plan=env['full_plan'](list(range(n)),t);endpoint=eye(n)
    for layer in plan:
        for a in layer:endpoint=mul(a,endpoint)
    need(endpoint==t,"retained compiler algebra binding")
    return sum(map(len,plan))


def reject(call,text):
    try:call()
    except ValueError as exc:need(text in str(exc),'unexpected control failure')
    else:raise ValueError('missed control: '+text)


def main():
    results=[];wrong_order=False
    for n in (1,3,4,5):
        t=Matrix([[C(2+Q(i,5),Q(i+1,17)) if i==j else C(Q(i+2*j+1,41),Q(i-j,37))
                   for j in range(n)] for i in range(n)])
        choices=trees(0,n)
        if n==5:choices=[choices[0],choices[len(choices)//2],choices[-1]]
        result,wrong=audit(t,choices);results.append(result);wrong_order|=wrong
        if n==4:source_atoms=source_binding(t)
    need(wrong_order,"wrong frontier order discriminated")
    bad=Matrix([[0,1],[1,0]]);need(mul(bad,inv(bad))==eye(2),'full endpoint invertible control')
    reject(lambda:ldu(bad),'singular leading section')
    u=Matrix([[1,1,0],[0,1,1],[0,0,1]])
    sub=lambda a:Matrix([[a[i][j] for j in (0,2)] for i in (0,2)])
    need(inv(sub(u))!=sub(inv(u)),"noncontiguous inverse restriction rejected")
    t=Matrix([[Q(1,64),1],[1,0]])
    need(max(envelope(t),envelope(inv(t)))<=2 and envelope(ldu(t)[2])>32,
         "full inverse alone cannot bound shear")
    a=Matrix([[C(1,1),1],[2,C(3,-1)]])
    row=Matrix([[C(1,2),C(2,-1)]])
    correct=mul(row,inv(a))
    adjoint=Matrix([[x.conjugate() for x in r] for r in a.T])
    wrong=mul(inv(adjoint),row.T).T  # Unmatched adjoint in the source's ordinary right solve.
    need(correct!=wrong,"wrong complex adjoint discriminated")
    need(any(r['mixed_lower_frontier'] for r in results),'mixed completed/frontier states covered')
    print(json.dumps(dict(cases=results,source_algebra_atoms=source_atoms,controls=5),sort_keys=True))
    print('PASS_LEADING_SECTION_DOWNSET_AUDIT arbitrary_interval_tree scoped_proof no_new_kappa')


if __name__=='__main__':main()

"""Adaptive affine transcripts and exact binary certificates. Apache-2.0."""
from functools import lru_cache
from pathlib import Path
import hashlib
import importlib.util
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FRAMES = ((0,28,29,39),(1,22,23,38),(2,16,17,37),(9,10,11,36),
          (3,15,26,32),(5,12,24,35),(7,14,21,34),(4,18,25,31),
          (6,19,20,33),(8,13,27,30))


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    for record in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if record['usage'] != 'input':
            continue
        raw = (ROOT/record['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == record['sha256'], 'source SHA '+record['path'])
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
             == record['git_blob'], 'source blob '+record['path'])


def load():
    authenticate()
    modules=[]
    for name,path in [('floor','research/eisenstein-reduction-copy-floor/verify.py'),
                      ('geometry','research/eisenstein-clique-copy-bound/geometry.py')]:
        spec=importlib.util.spec_from_file_location('r036_'+name,ROOT/path)
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        modules.append(module)
    return modules


def parity(x):
    return x.bit_count() & 1


def affine_system(equations, n):
    """A particular point and full kernel basis, or None for an empty fiber."""
    pivots={}
    for row,rhs in equations:
        need(type(row) is int and 0 <= row < 1 << n and rhs in (0,1), 'binary equation')
        while row:
            p=row.bit_length()-1
            if p not in pivots:
                pivots[p]=(row,rhs)
                break
            r,b=pivots[p];row^=r;rhs^=b
        if not row and rhs:
            return None
    def complete(seed, homogeneous):
        out=seed
        for p,(row,rhs) in sorted(pivots.items()):
            if parity(row & out) ^ (0 if homogeneous else rhs):
                out ^= 1 << p
        return out
    point=complete(0,False)
    kernel=[complete(1 << j,True) for j in range(n) if j not in pivots]
    return point,kernel,len(pivots)


def combination(rows, target):
    pivots={}
    for index,row in enumerate(rows):
        mask=1 << index
        while row:
            p=row.bit_length()-1
            if p not in pivots:
                pivots[p]=(row,mask);break
            r,m=pivots[p];row^=r;mask^=m
    result=0
    while target:
        p=target.bit_length()-1
        if p not in pivots:
            return None
        row,mask=pivots[p];target^=row;result^=mask
    return result


def xor_rows(rows, coefficients):
    result=0
    for i,row in enumerate(rows):
        if coefficients >> i & 1:
            result ^= row
    return result


class Protocol:
    """The public controller receives only paid answers, never the input x."""
    def __init__(self, kind, demands):
        self.kind=kind
        self.demands=tuple(demands)
        need(len(demands)==40 and all(type(b) is int and b>=0 for b in demands), 'demands')
        self.owners=tuple(t for t,b in enumerate(demands) for _ in range(b))
        self.n=len(self.owners)
        self.frame_rows=[]
        self.groups=[]
        offset={}
        for bit,owner in enumerate(self.owners):
            offset.setdefault(owner,[]).append(bit)
        for frame in FRAMES:
            group=[]
            for level in range(max(demands[t] for t in frame)):
                row=sum(1 << offset[t][level] for t in frame if demands[t]>level)
                group.append(row)
                self.frame_rows.append(row)
            if group:
                self.groups.append(tuple(group))

    def query(self, history):
        k=len(history)
        if self.kind in ('adaptive','variable','affine','dropped'):
            repeat=int(self.kind=='variable' and bool(history) and history[0]==1)
            if repeat and k==1:
                rows=(self.frame_rows[0],)
            else:
                stage=k-int(repeat and k>=2)
                stop=len(self.frame_rows)-int(self.kind=='dropped')
                if stage>=stop:
                    return None
                row=self.frame_rows[stage]
                if stage==1 and history[0]:
                    row ^= self.frame_rows[2]
                rows=(row,)
        elif self.kind=='block':
            if k>=len(self.groups):
                return None
            rows=self.groups[k]
            if k==1 and history[0]&1:
                rows=tuple(row ^ self.groups[2][i] for i,row in enumerate(rows))
        elif self.kind=='unequal':
            if k>=len(self.frame_rows):
                return None
            rows=(self.frame_rows[k],)
        else:
            raise ValueError('unknown protocol')
        sources=tuple(sorted({self.owners[bit] for row in rows
                              for bit in range(self.n) if row >> bit & 1}))
        constant=(k+1)%2 if self.kind=='affine' else 0
        return dict(rows=tuple(rows),sources=sources,constant=constant)

    def answer(self, query, x):
        return sum(parity(row & x) << i for i,row in enumerate(query['rows'])) ^ query['constant']

    def walk(self, x):
        history=[]
        while True:
            need(len(history)<=30, 'finite fixture guard')
            query=self.query(history)
            if query is None:
                return tuple(history)
            history.append(self.answer(query,x))

    def leaves(self):
        def visit(history,equations,path):
            solved=affine_system(equations,self.n)
            if solved is None:
                return
            query=self.query(history)
            if query is None:
                yield tuple(history),tuple(equations),tuple(path),solved
                return
            need(len(history)<=30, 'finite fixture guard')
            for y in range(1 << len(query['rows'])):
                rhs=y ^ query['constant']
                additions=[(row,(rhs >> i)&1) for i,row in enumerate(query['rows'])]
                yield from visit(history+[y],equations+additions,path+[query])
        yield from visit([],[],[])


class Geometry:
    def __init__(self, floor, source):
        self.floor,self.source=floor,source
        self.reps,self.images,self.adjacent,_,_=source.geometry()
        self.h=[[floor.gram(x,y,jy) for y,jy in zip(self.reps,self.images)] for x in self.reps]
        self.hbar=[[floor.reduce_mod2(z) for z in row] for row in self.h]
        need(len(self.reps)==40 and len(source.echelon(self.reps))==8, 'full rational span')
        need(sorted(t for frame in FRAMES for t in frame)==list(range(40)), 'partition')
        for frame in FRAMES:
            need(all(self.h[i][j]==floor.ZERO for i in frame for j in frame if i!=j), 'orthogonal frame')
            need(self.price(frame)==4, 'actual frame price')

    @lru_cache(None)
    def price(self, sources):
        # All spans R^8, hence its pairing rank with A is dim_Q X_A.
        rows=[r for i in sources for r in (self.reps[i],self.images[i])]
        rank=len(self.source.echelon(rows))
        need(rank%2==0, 'even rational source rank')
        cost=rank//2
        matrix=[[self.h[i][j] for j in sources] for i in range(40)]
        need(self.floor.rank(matrix)==cost, 'actual K/rational price comparison')
        need(self.floor.rank([[self.hbar[i][j] for j in sources] for i in range(40)],'F4')<=cost,
             'source specialization rank')
        return cost

    @lru_cache(None)
    def recover(self, rows, owners):
        n=len(owners);q=len(rows);decoder=[];fitting=[]
        for k,t in enumerate(owners):
            side=[1 << j for j,u in enumerate(owners) if u!=t and not (self.adjacent[t] >> u & 1)]
            coefficients=combination(list(rows)+side,1 << k)
            need(coefficients is not None, 'undecodable leaf kernel')
            d=coefficients & ((1 << q)-1)
            b=xor_rows(rows,d)
            for j,u in enumerate(owners):
                if u==t or self.adjacent[t] >> u & 1:
                    need(((b >> j)&1)==int(j==k), 'fitting block mask')
                value=self.hbar[t][u] if b >> j & 1 else 0
                need(value==int(j==k), 'lifted Hadamard identity')
            decoder.append(d);fitting.append(b)
        return tuple(decoder),tuple(fitting)

    def certify(self, protocol, equations, path):
        rows=tuple(row for row,_ in equations)
        cost=0
        for query in path:
            actual={protocol.owners[j] for row in query['rows'] for j in range(protocol.n) if row >> j & 1}
            need(actual <= set(query['sources']), 'undeclared query source')
            q=len(query['rows'])
            need(0<=query['constant']<1 << q, 'affine constant width')
            cost += q*self.price(tuple(query['sources']))
        decoder,fitting=self.recover(rows,protocol.owners)
        need(cost>=protocol.n, 'pathwise pairing floor')
        return cost,decoder,fitting

#!/usr/bin/env python3
"""Independent left-product Tseitin CNF over a permutation group algebra.
No Z3 dependency. Cinna Davis with OpenAI Codex assistance. Apache-2.0.
"""
import itertools

GROUP=tuple(itertools.permutations(range(3)))
INDEX={g:i for i,g in enumerate(GROUP)}
IDENT=INDEX[(0,1,2)];A=INDEX[(0,2,1)];B=INDEX[(2,1,0)];SWAP=INDEX[(1,0,2)]
MUL=[[INDEX[tuple(p[q[i]] for i in range(3))] for q in GROUP] for p in GROUP]

class Formula:
    def __init__(self):self.variables=1;self.clauses=[[1]];self.projectors=[];self.operations=[]
    def variable(self):self.variables+=1;return self.variables
    def clause(self,*lits):self.clauses.append(list(lits))
    def both(self,a,b):
        if a==1:return b
        if b==1:return a
        if a==-1 or b==-1 or a==-b:return -1
        if a==b:return a
        t=self.variable();self.operations.append((t,"and",a,b));self.clause(-t,a);self.clause(-t,b);self.clause(t,-a,-b);return t
    def xor(self,a,b):
        if a==-1:return b
        if b==-1:return a
        if a==1:return -b
        if b==1:return -a
        if a==b:return -1
        if a==-b:return 1
        t=self.variable();self.operations.append((t,"xor",a,b))
        for clause in [(-a,-b,-t),(a,b,-t),(a,-b,t),(-a,b,t)]:self.clause(*clause)
        return t
    def parity(self,values):
        out=-1
        for value in values:out=self.xor(out,value)
        return out

def patterns():return [''.join('a' if j in positions else 'b' for j in range(7)) for positions in itertools.combinations(range(7),3)]

def encode(labels,pinned=None):
    f=Formula();r=4;ordinal=0
    state=[[[1 if h==IDENT and i==j else -1 for j in range(r)] for i in range(r)] for h in range(6)]
    for step,label in enumerate(labels):
        if label=='a':u=[1 if i==ordinal else -1 for i in range(r)];ordinal+=1
        else:u=[f.variable() for _ in range(r)]
        v=[f.variable() for _ in range(r)];f.projectors.append((u,v))
        f.clause(f.parity(f.both(u[i],v[i]) for i in range(r)))
        if pinned is not None:
            for name,values in [('u',u),('v',v)]:
                for i,value in enumerate(values):f.clause(value if (pinned[step][name]>>i)&1 else -value)
        g=A if label=='a' else B
        # Left multiplication, with a row contraction and left group translation.
        contracted=[[f.parity(f.both(v[k],state[h][k][j]) for k in range(r)) for j in range(r)] for h in range(6)]
        new=[[[0]*r for _ in range(r)] for _ in range(6)]
        for h in range(6):
            previous=MUL[g][h] # g is an involution
            for j in range(r):
                change=f.xor(contracted[h][j],contracted[previous][j])
                for i in range(r):new[h][i][j]=f.xor(state[h][i][j],f.both(u[i],change))
        state=new
    for h in range(6):
        for i in range(r):
            for j in range(r):
                required=i==j and h==(SWAP if i<3 else IDENT)
                f.clause(state[h][i][j] if required else -state[h][i][j])
    return f

def concrete(word,r=4):
    state=[[[int(h==IDENT and i==j) for j in range(r)] for i in range(r)] for h in range(6)]
    for gate in word:
        u,v,g=gate['u'],gate['v'],A if gate['label']=='a' else B
        if not (u and v and (u&v).bit_count()%2):raise ValueError('illegal projector')
        previous=state
        state=[[row[:] for row in block] for block in previous]
        for h in range(6):
            for j in range(r):
                delta=0
                for k in range(r):
                    if v>>k&1:delta^=previous[h][k][j]^previous[MUL[g][h]][k][j]
                for i in range(r):
                    if u>>i&1:state[h][i][j]^=delta
    return state

"""Slow independent arithmetic oracles, never a claimed physical backend.

Fresh coefficient products deliberately cost g products per record. The
physical backend must implement and charge its own cached delivery protocol.
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q

from compiler import Hadamard
from sources import need

ZERO=(Q(0),Q(0))
ONE=(Q(1),Q(0))


def add(a,b):
    return a[0]+b[0],a[1]+b[1]


def neg(a):
    return -a[0],-a[1]


def mul(a,b):
    return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]


def divide(a,b):
    d=b[0]*b[0]+b[1]*b[1]
    need(d>0,'nonzero independent complex divisor')
    r=mul(a,(b[0],-b[1]))
    return r[0]/d,r[1]/d


def decode(z,bits):
    return Q(z[0],1 << bits),Q(z[1],1 << bits)


def rounded(z,bits):
    return int(z[0]*(1 << bits)),int(z[1]*(1 << bits))


def energy(values):
    return sum((a*a+b*b for a,b in values),Q(0))


def distance_squared(a,b):
    return energy([add(x,neg(y)) for x,y in zip(a,b,strict=True)])


def raw_h(state,positions):
    for bit in positions:
        step=1 << bit
        for block in range(0,len(state),2*step):
            for low in range(step):
                i,j=block+low,block+low+step
                x,y=state[i],state[j]
                state[i],state[j]=add(x,y),add(x,neg(y))
    return state


class FreshSemanticService:
    """Fraction oracle for the declared protocol; no cache or tape claims."""
    def __init__(self):
        self.stats=dict(global_H_calls=0,global_diagonals=0,fresh_factor_products=0,
                        data_products=0,nonzero_roundings=0,maximum_numerator_bits=0)

    def apply_h(self,state,event):
        event.validate()
        need(len(state) == 1 << event.array_bits,'oracle complete global H field')
        self.stats['global_H_calls']+=1
        return raw_h(state,event.positions)

    def apply_diagonal(self,state,event):
        event.validate()
        need(len(state) == 1 << event.array_bits,'oracle complete global diagonal field')
        F,m,g=event.fractional_bits,event.axis_bits,event.axes
        mask=(1 << m)-1
        for address,z in enumerate(state):
            coarse=address >> (m*g)
            coefficient=ONE
            for axis in range(g-1,-1,-1):
                factor=decode(event.pages[coarse][axis][(address >> (axis*m)) & mask],F)
                exact=mul(factor,coefficient)
                stored=rounded(exact,F)
                coefficient=decode(stored,F)
                self.stats['fresh_factor_products']+=1
                self.stats['nonzero_roundings']+=int(coefficient != exact)
            exact=mul(decode(z,F),coefficient)
            state[address]=rounded(exact,F)
            self.stats['nonzero_roundings']+=int(decode(state[address],F) != exact)
            self.stats['data_products']+=1
            self.stats['maximum_numerator_bits']=max(self.stats['maximum_numerator_bits'],
                                                     *(abs(x).bit_length()+1 for x in state[address]))
        self.stats['global_diagonals']+=1
        return state


def emitted_exact(program,values):
    """Exact unrounded global primitive word, independent of event encoding."""
    state=list(values)
    N,g,m=program.size,program.axes,program.axis_bits
    for step in range(program.stages):
        kind,bit=program.layer_signature[step % program.layer_stages]
        if kind == 'H':
            raw_h(state,[a*m+bit for a in range(g)])
        else:
            for address,z in enumerate(state):
                c=address >> (g*m)
                coefficient=ONE
                for a in range(g):
                    coefficient=mul(coefficient,program.reference_stage(c,a,step)[1][(address >> (a*m)) & (N-1)])
                state[address]=mul(coefficient,z)
    return state


def source_plan_exact(program,values):
    """Apply original stored logical gates, not the compiled primitive word."""
    state=list(values)
    N=program.size
    local=N**program.axes
    for c,block in enumerate(program.programs):
        for axis,p in enumerate(block):
            stride=N**axis
            for layer in p.plan:
                for ids,gate in layer:
                    matrix=[[(z.re,z.im) for z in row] for row in gate]
                    for high in range(0,local,N*stride):
                        for low in range(stride):
                            places=[c*local+high+low+j*stride for j in ids]
                            old=[state[k] for k in places]
                            for i,address in enumerate(places):
                                total=ZERO
                                for j,z in enumerate(old):
                                    total=add(total,mul(matrix[i][j],z))
                                state[address]=total
    return state


def inverse(matrix):
    """Separate exact complex Gauss-Jordan, without retained source routines."""
    n=len(matrix)
    rows=[list(row)+[ONE if i==j else ZERO for j in range(n)] for i,row in enumerate(matrix)]
    for column in range(n):
        pivot=next((i for i in range(column,n) if rows[i][column] != ZERO),None)
        need(pivot is not None,'independent nonsingular root')
        rows[column],rows[pivot]=rows[pivot],rows[column]
        divisor=rows[column][column]
        rows[column]=[divide(z,divisor) for z in rows[column]]
        for i in range(n):
            if i==column:
                continue
            coefficient=rows[i][column]
            rows[i]=[add(a,neg(mul(coefficient,b))) for a,b in zip(rows[i],rows[column],strict=True)]
    return [row[n:] for row in rows]


def root_exact(program,values):
    state=list(values)
    N=program.size
    local=N**program.axes
    for c,block in enumerate(program.roots):
        for axis,root in enumerate(block):
            matrix=[[(z.re,z.im) for z in row] for row in root.matrix]
            if program.directions[c][axis]:
                matrix=inverse(matrix)
            physical=[[ZERO]*N for _ in range(N)]
            for i in range(N):
                for j in range(N):
                    physical[root.indices[i]][root.indices[j]]=matrix[i][j]
            stride=N**axis
            for high in range(0,local,N*stride):
                for low in range(stride):
                    places=[c*local+high+low+j*stride for j in range(N)]
                    old=[state[k] for k in places]
                    for i,address in enumerate(places):
                        total=ZERO
                        for j,z in enumerate(old):
                            total=add(total,mul(physical[i][j],z))
                        state[address]=total
    return state

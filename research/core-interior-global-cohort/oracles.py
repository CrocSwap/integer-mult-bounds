"""Independent finite arithmetic checks; never a production arithmetic owner.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from core_layout import address
from cohort_sources import need


def truncate(value,bits):
    return (abs(value) >> bits)*(-1 if value < 0 else 1)


def product(a,b,bits):
    return (truncate(a[0]*b[0]-a[1]*b[1],bits),
            truncate(a[0]*b[1]+a[1]*b[0],bits))


class IntegerOracle:
    """Fresh products for every record; deliberately no physical suffix cache."""
    def __init__(self):
        self.roundings = 0

    def apply_h(self,state,event):
        for bit in event.positions:
            stride = 1 << bit
            for base in range(0,len(state),2*stride):
                for low in range(stride):
                    i,j = base+low,base+low+stride
                    a,b = state[i],state[j]
                    state[i],state[j] = ((a[0]+b[0],a[1]+b[1]),(a[0]-b[0],a[1]-b[1]))
        return state

    def apply_diagonal(self,state,event):
        F,m,g = event.fractional_bits,event.axis_bits,event.axes
        unit,mask = 1 << F,(1 << m)-1
        for index,value in enumerate(state):
            label = index >> (g*m)
            factor = (unit,0)
            for axis in reversed(range(g)):
                z = event.pages[label][axis][(index >> (axis*m)) & mask]
                exact = (z[0]*factor[0]-z[1]*factor[1],z[0]*factor[1]+z[1]*factor[0])
                factor = tuple(truncate(x,F) for x in exact)
                self.roundings += int(any(x % unit for x in exact))
            exact = (factor[0]*value[0]-factor[1]*value[1],
                     factor[0]*value[1]+factor[1]*value[0])
            state[index] = tuple(truncate(x,F) for x in exact)
            self.roundings += int(any(x % unit for x in exact))
        return state


def permute(values,mapping):
    result = [None]*len(values)
    for old,value in enumerate(values):
        result[address(old,mapping)] = value
    need(all(x is not None for x in result),'complete independent permutation image')
    return result


def source_reference(program,values):
    """Direct-sum exact reference matrices, independently of logical/primitive gates."""
    r = program.roots[0][0].runtime
    E,N,g = r.exact,program.size,program.axes
    state = [E.C(Q(a,1 << program.incoming),Q(b,1 << program.incoming)) for a,b in values]
    local = N**g
    for label,block in enumerate(program.roots):
        for axis,root in enumerate(block):
            stride = N**axis
            matrices = root.partition.inverses if program.directions[label][axis] else root.partition.matrices
            for indices,matrix in zip(root.partition.indices,matrices):
                for high in range(0,local,N*stride):
                    for low in range(stride):
                        places = [label*local+high+low+j*stride for j in indices]
                        old = [state[i] for i in places]
                        for row,i in zip(matrix,places):
                            state[i] = sum((a*x for a,x in zip(row,old)),E.C())
    return state


def check_complete(program,original):
    packed = permute(original,program.layout.gather)
    service = IntegerOracle()
    result,counts = program.execute(packed,service)
    expected = source_reference(program,packed)
    r = program.roots[0][0].runtime
    E,scale = r.exact,1 << program.bits
    error = sum(((E.C(Q(a,scale),Q(b,scale))-z).norm2()
                 for (a,b),z in zip(result,expected)),Q(0))
    need(error <= program.total_error**2 and error < program.tau**2,
         'complete source-reference global numerical endpoint')
    return permute(result,program.layout.inverse),counts,service.roundings,error

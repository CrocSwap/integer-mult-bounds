"""Clean nearest-neighbour readout of a width-13 complex canonical coefficient."""
import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE/'retained')]
from divider import Layout, program as divide
from physical import Meter, TRACKS, loc, lower
from producer import ODD, SHIFT, producer


def shape_mono(m):
    if len(m['rows'])!=4 or len(m['linear'])!=4:
        raise ValueError("Expected four binary rows and four phase coefficients")
    images = {0}
    for row in m['rows']:
        images |= {v^row for v in images}
    if len(images)!=16:
        raise ValueError("The four affine-map rows must be independent")


def bind(registers,value,state):
    if type(value) is not int or not 0<=value<1<<len(registers):
        raise ValueError("Input does not fit its declared binary width")
    for i,w in enumerate(registers):
        state[loc(w)] = value>>i & 1


def encode(I,request,state):
    for key in ('phase','mask','x','z'):
        bind(I[key],request[key],state)
    for key in ('left','right'):
        m=request[key]
        shape_mono(m)
        for field in ('shift','cross'):
            bind(I[key][field],m[field],state)
        for field in ('rows','linear'):
            for regs,val in zip(I[key][field],m[field],strict=True):
                bind(regs,val,state)
    for registers,values in zip(I['terms'],request['terms'],strict=True):
        for regs,val in zip(registers,values,strict=True):
            bind(regs,val,state)


def mapped(gates):
    return [tuple(map(loc,g)) for g in gates]


class Plan:
    def __init__(self,m,precision):
        net,self.input,mags,signs=producer(m,precision)
        self.prepare=mapped(net.gates)
        magbits=len(mags[0])
        padded=max(magbits,SHIFT-precision+1)
        div=Layout(padded,ODD.bit_length(),SHIFT,precision)
        self.result=[(net.wires(div.m),net.wires(1)[0]) for _ in range(2)]
        self.sign_ops=[]
        for (digits,sign_out),negative in zip(self.result,signs,strict=True):
            start=len(net.gates)
            nz=net.complement(net.every([net.complement(d) for d in digits]))
            flag=net.both(nz,negative)
            gates=mapped(net.gates[start:])
            self.sign_ops.append(gates+[(loc(flag),loc(sign_out))]+gates[::-1])
        self.base=(net.size+7)//8
        self.sites=self.base+div.sites
        def dw(site,track=0):
            return TRACKS*(self.base+site)+track
        self.modulus=[(dw(div.k-i,1),) for i in range(div.k) if ODD>>i&1]
        self.division=[tuple(dw(v//8,v%8) for v in g) for g in divide(div)]
        self.loads=[[(loc(w),dw(div.k+div.bits-i)) for i,w in enumerate(mag)] for mag in mags]
        self.copies=[[(dw(div.m-1-i),loc(w)) for i,w in enumerate(regs)] for regs,_ in self.result]
        self.numerator=mags,signs
        self.precision=precision

    def operations(self):
        yield from self.prepare
        yield from self.modulus
        for load,copy,sign in zip(self.loads,self.copies,self.sign_ops,strict=True):
            yield from load
            yield from self.division
            yield from copy
            yield from reversed(self.division)
            yield from reversed(load)
            yield from sign
        yield from reversed(self.modulus)
        yield from reversed(self.prepare)


def toggle(g,state):
    value=1
    for w in g[:-1]:
        value &= state[w]
    state[g[-1]] ^= value


def raw_read(bits,state):
    return sum(state[loc(b)]<<i for i,b in enumerate(bits))


def evaluate(request,literal=False):
    plan=Plan(len(request['terms']),request['precision'])
    state=bytearray(TRACKS*plan.sites)
    encode(plan.input,request,state)
    start=state.copy()
    meter=Meter()
    for g in plan.operations():
        if literal:
            for primitive in lower(g):
                toggle(primitive,state)
                meter.local(primitive)
        else:
            toggle(g,state)
            meter.logical(g)
    meter.visit(0,0)
    outputs=[]
    for regs,sgn in plan.result:
        magnitude=raw_read(regs,state)
        negative=state[loc(sgn)]
        if negative and not magnitude:
            raise ValueError("Negative zero")
        outputs.append(-magnitude if negative else magnitude)
        for w in [*regs,sgn]:
            state[loc(w)]=0
    if state!=start:
        raise ValueError("Input or clean workspace was not restored")
    return dict(grid_integers=outputs,precision=request['precision'],sites=plan.sites,
                not_gates=meter.gates[1],cnot_gates=meter.gates[2],toffoli_gates=meter.gates[3],
                head_moves=meter.moves)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('request',type=Path)
    parser.add_argument('--literal',action='store_true')
    args=parser.parse_args()
    print(json.dumps(evaluate(json.loads(args.request.read_bytes()),args.literal),indent=2))

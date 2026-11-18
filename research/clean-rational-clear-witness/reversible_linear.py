"""Finite reversible Boolean compiler for constant-denominator linear witnesses.
No gate erases information. Inputs remain unchanged; every ancillary bit starts
and ends at zero. This is a gate-network model, NOT a project tape compiler.
"""
from itertools import product
from collections import Counter
class Circuit:
    def __init__(self,n): self.inputs=n; self.next=n; self.gates=[]
    def fresh(self): r=self.next; self.next+=1; return r
    def const(self,v):
        r=self.fresh()
        if v: self.gates.append(('X',r))
        return r
    def xor(self,a,b):
        r=self.fresh(); self.gates.extend([('CX',a,r),('CX',b,r)]); return r
    def inv(self,a):
        r=self.fresh(); self.gates.extend([('CX',a,r),('X',r)]); return r
    def land(self,a,b):
        r=self.fresh(); self.gates.append(('CX',a,r) if a==b else ('CCX',a,b,r)); return r
    def choose(self,s,a,b): return self.xor(b,self.land(s,self.xor(a,b)))
    def vector(self,k,n): return [self.const((k>>i)&1) for i in range(n)]
    def add(self,a,b,carry=None):
        carry=self.const(0) if carry is None else carry; out=[]
        for x,y in zip(a,b):
            t=self.xor(x,y); out.append(self.xor(t,carry))
            carry=self.xor(self.land(x,y),self.land(t,carry))
        return out,carry
    def subtract(self,a,b): return self.add(a,[self.inv(v) for v in b],self.const(1))
    def multiply_constant(self,a,k):
        n=len(a)
        if k==1: return a
        if k<0:
            positive=self.multiply_constant(a,-k)
            return self.add([self.inv(v) for v in positive],self.vector(0,n),self.const(1))[0]
        out=self.vector(0,n)
        for shift in range(min(n,k.bit_length())):
            if k>>shift&1:
                out,_=self.add(out,self.vector(0,shift)+a[:n-shift])
        return out
    def divide_unsigned(self,a,d):
        # remainder < d at each iteration; temporary doubled remainder <2*d.
        width=d.bit_length()+1; rem=self.vector(0,width); divisor=self.vector(d,width); q=[None]*len(a)
        for i in range(len(a)-1,-1,-1):
            rem=[a[i]]+rem[:-1]
            delta,ge=self.subtract(rem,divisor)
            rem=[self.choose(ge,x,y) for x,y in zip(delta,rem)]
            q[i]=ge
        return q,rem

def compile_linear(coefficients,denominator,width):
    if type(denominator) is not int or denominator <= 0 or type(width) is not int or width <= 0:
        raise ValueError("positive integer denominator and width required")
    if not isinstance(coefficients,(list,tuple)) or any(type(a) is not int for a in coefficients):
        raise ValueError("integer coefficient list required")
    count=len(coefficients); c=Circuit(count*width)
    # Covers ALL signed width-bit input strings, not sampled trajectories.
    bound=sum(abs(a) for a in coefficients)*(1<<(width-1))
    offset=((bound+denominator-1)//denominator)*denominator
    n=max(width,(2*bound+denominator).bit_length()+1)
    accum=c.vector(offset,n)
    for j,k in enumerate(coefficients):
        bits=list(range(j*width,(j+1)*width)); extended=bits+[bits[-1]]*(n-width)
        term=c.multiply_constant(extended,abs(k))
        accum,_=c.subtract(accum,term) if k<0 else c.add(accum,term)
    quotient,remainder=c.divide_unsigned(accum,denominator)
    result,_=c.subtract(quotient,c.vector(offset//denominator,n))
    invalid=c.const(0)
    for bit in remainder+[c.xor(bit,result[width-1]) for bit in result[width:]]:
        invalid=c.xor(c.xor(invalid,bit),c.land(invalid,bit))
    c.invalid=invalid
    return c,result[:width],{'numerator_abs_bound':bound,'offset':offset,'arithmetic_bits':n,'input_bits':count*width,'ancilla_bits':c.next-c.inputs,'forward_gates':dict(Counter(g[0] for g in c.gates)),'clean_CLEAR_gates':2*len(c.gates)+width+1,'output_bits':width}

def apply(state,gates):
    for gate in gates:
        if gate[0]=='X': state[gate[1]]^=1
        elif gate[0]=='CX': state[gate[2]]^=state[gate[1]]
        elif gate[0]=='CCX': state[gate[3]]^=state[gate[1]]&state[gate[2]]
        else: raise ValueError('unknown gate')

def clear(c,out,inputs,target,width):
    bits=[(x>>i)&1 for x in inputs for i in range(width)]
    state=bits+[0]*(c.next-c.inputs)+[(target>>i)&1 for i in range(width)]+[0]
    apply(state,c.gates)
    reconstructed=sum(state[b]<<i for i,b in enumerate(out))
    output_gates=[('CX',b,c.next+i) for i,b in enumerate(out)]+[('CX',c.invalid,c.next+width)]
    apply(state,output_gates)
    apply(state,reversed(c.gates))
    assert state[:c.inputs]==bits and not any(state[c.inputs:c.next])
    target_after=sum(state[c.next+i]<<i for i in range(width))
    return target_after,reconstructed,state[-1]

def selftest():
    import random
    rng=random.Random(7671); cases=0
    for coeff,d,w in [([1,-1],1,3),([1,2],3,3),([-3,1],8,3),([0],2,4),([7,-5,2],6,4)]:
        c,out,stats=compile_linear(coeff,d,w)
        entries=product(range(-(1<<(w-1)),1<<(w-1)),repeat=len(coeff)) if len(coeff)<3 else (tuple(rng.randrange(-(1<<(w-1)),1<<(w-1)) for _ in coeff) for _ in range(100))
        for xs in entries:
            numerator=sum(k*x for k,x in zip(coeff,xs)); expected=numerator//d
            after,got,invalid=clear(c,out,xs,expected,w)
            assert got==expected%(1<<w) and after==0
            assert invalid==int(numerator%d!=0 or not -(1<<(w-1))<=expected<(1<<(w-1)))
            bad,_,_=clear(c,out,xs,expected^1,w); assert bad==1
            cases+=1
    return {'cases':cases,'all_signed_inputs_exhaustive_for_first_four_contracts':True,'last_contract_deterministic_random_cases':100,'all_sources_preserved_all_ancillas_zero':True,'nonzero_target_mismatch_preserved':True,'invalid_fraction_or_signed_overflow_flag_exact':True}
if __name__=='__main__':
    import json
    print(json.dumps(selftest()))

"""Width-13 canonical numerator producer. Programs depend only on public sizes."""
from itertools import combinations

SCALE = (71470953728,3372907072,299589952,-12441328,-14688133)
ODD = 7852360022325
SHIFT = 19
PAIRS = tuple(combinations(range(4),2))


class Network:
    """Straight-line XOR/AND construction, retaining enough work to reverse every gate."""
    def __init__(self):
        self.size = 2
        self.gates = [(1,)]  # wire zero stays zero, wire one is initialized reversibly

    def wires(self,n):
        start = self.size
        self.size += n
        return list(range(start,self.size))

    def xor(self,*inputs):
        remaining = set()
        for v in inputs:
            if v:
                remaining.symmetric_difference_update([v])
        if not remaining:
            return 0
        if len(remaining)==1:
            return remaining.pop()
        out, = self.wires(1)
        self.gates.extend((v,out) for v in sorted(remaining))
        return out

    def both(self,a,b):
        if a==0 or b==0:
            return 0
        if a==1 or a==b:
            return b
        if b==1:
            return a
        out, = self.wires(1)
        self.gates.append((a,b,out))
        return out

    def complement(self,a):
        return self.xor(a,1)

    def every(self,entries):
        result = 1
        for v in entries:
            result = self.both(result,v)
        return result

    def equals(self,bits,value):
        return self.every(b if value>>j&1 else self.complement(b) for j,b in enumerate(bits))

    def add(self,a,b,carry=0):
        answer = []
        for left,right in zip(a,b,strict=True):
            pair = self.xor(left,right)
            answer.append(self.xor(pair,carry))
            if len(answer)<len(a):
                carry = self.xor(self.both(left,right),self.both(pair,carry))
        return answer

    def negative(self,a):
        return self.add([self.complement(v) for v in a],[0]*len(a),1)

    def dot(self,a,b):
        return self.xor(*(self.both(x,y) for x,y in zip(a,b,strict=True)))


def mono_wires(net):
    return dict(rows=[net.wires(4) for _ in range(4)],shift=net.wires(4),
                linear=[net.wires(2) for _ in range(4)],cross=net.wires(6))


def mono(net,data,v):
    addr = [net.xor(net.dot(row,v),off) for row,off in zip(data['rows'],data['shift'],strict=True)]
    phase = [0,0]
    for x,lin in zip(v,data['linear'],strict=True):
        phase = net.add(phase,[net.both(x,b) for b in lin])
    phase[1] = net.xor(phase[1],*(net.every([v[i],v[j],coef])
                                 for (i,j),coef in zip(PAIRS,data['cross'],strict=True)))
    return addr,phase


def term_flags(net,target,record,jbits,shell):
    r,c,t = record
    rprime = [net.xor(a,b) for a,b in zip(r,target['x'],strict=True)]
    left,lp = mono(net,target['left'],rprime)
    right,rp = mono(net,target['right'],c)
    b = target['mask']
    ok = net.every(net.complement(net.every([net.complement(mask),net.xor(x,y)]))
                   for mask,x,y in zip(b,left,right,strict=True))
    pauli_sign = net.dot(rprime,target['z'])
    had_sign = net.xor(*(net.every([x,y,mask]) for x,y,mask in zip(left,right,b,strict=True)))
    phase = net.add(net.add(t,lp),net.negative(net.add(rp,target['phase'])))
    phase[1] = net.xor(phase[1],pauli_sign,had_sign,shell[3],shell[4])
    angle = net.add([0,*phase],net.negative(jbits))
    eighths = [net.both(ok,net.equals(angle,k)) for k in range(8)]
    return [(net.xor(*(eighths[i] for i in pos)),net.xor(*(eighths[i] for i in neg)))
            for pos,neg in [((0,1,7),(3,4,5)),((1,2,3),(5,6,7))]]


def producer(m,precision):
    if type(m) is not int or m<1 or type(precision) is not int or precision<0:
        raise ValueError("Expected a positive number of records and a nonnegative precision")
    n = Network()
    I = dict(left=mono_wires(n),right=mono_wires(n),mask=n.wires(4),
             phase=n.wires(2),x=n.wires(4),z=n.wires(4))
    I['terms'] = [(n.wires(4),n.wires(4),n.wires(2)) for _ in range(m)]
    bits = (m*max(map(abs,SCALE))).bit_length()
    numer = [[0]*(bits+1) for _ in range(2)]
    jbits = [0,0,0]
    for b in I['mask']:
        jbits = n.add(jbits,[b,0,0])
    shell = [n.equals(jbits,j) for j in range(5)]
    scale = [n.xor(*(shell[j] for j,v in enumerate(SCALE) if abs(v)>>i&1))
             for i in range(bits+1)]
    for record in I['terms']:
        flags = term_flags(n,I,record,jbits,shell)
        for lane,(pos,neg) in enumerate(flags):
            live = n.xor(pos,neg)
            operand = [n.xor(n.both(v,live),neg) for v in scale]
            numer[lane] = n.add(numer[lane],operand,neg)
    signs = [v[-1] for v in numer]
    magnitudes = [n.add([n.xor(s,v) for v in vector[:-1]],[0]*bits,s)
                  for s,vector in zip(signs,numer,strict=True)]
    return n,I,magnitudes,signs

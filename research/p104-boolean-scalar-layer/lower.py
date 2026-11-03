"""Lower the selected scalar alphabet to NOT, CNOT and Toffoli gates.

ADD circuits are unchanged PR3080 code. The SCALE lowering specializes its
constant increment and uses in-place rotations. Ali Romman with substantial
OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q


def need(ok,message):
    if not ok:raise ValueError(message)


def rotate(width,offset):
    gates = [];seen = set()
    for start in range(width):
        if start in seen:continue
        cycle = [];i = start
        while i not in seen:
            cycle.append(i);seen.add(i);i = (i+offset)%width
        a = ('t',start)
        for i in cycle[1:]:
            b = ('t',i);gates.extend([('cx',a,b),('cx',b,a),('cx',a,b)])
    return gates


def increment(width,adder):
    gates = []
    for gate in adder.adder(width,0):
        controls = [];zero = False
        for bank,i in gate[1:-1]:
            if bank == 's':zero |= i != 0
            else:controls.append((bank,i))
        if not zero:gates.append((('x','cx','ccx')[len(controls)],*controls,gate[-1]))
    return gates


def circuit(width,op,q,adder,signed=True):
    need(type(width) is int and 26 <= width <= 256,'supported word width')
    q = Q(q)
    if op == 'ADD':return adder.circuit(width,q.numerator,q.denominator,signed=signed)
    if op == 'COPY':
        need(q == 1,'selected COPY coefficient')
        return [('cx',('s',i),('t',i)) for i in range(width)]
    need(op == 'SCALE' and q and abs(q.numerator).bit_count() == q.denominator.bit_count() == 1,'dyadic unit SCALE')
    shift = abs(q.numerator).bit_length()-q.denominator.bit_length()
    need(abs(shift) < width,'scalar shift width')
    fill = [('cx',('t',width-1),('t',i)) for i in range(abs(shift))]
    gates = rotate(width,shift)+fill if shift >= 0 else fill+rotate(width,shift)
    if q < 0:gates += [('x',('t',i)) for i in range(width)]+increment(width,adder)
    return gates


def apply(gates,source,target,width,carry=0):
    """Execute each literal Boolean gate on fixed-width bit banks."""
    banks = {'s':source,'t':target,'c':carry}
    for gate in gates:
        control = 1
        for bank,i in gate[1:-1]:control &= (banks[bank]>>i)&1
        bank,i = gate[-1]
        need(bank != 's' and 0 <= i < (width-1 if bank == 'c' else width),'gate ownership')
        if control:banks[bank] ^= 1 << i
    need(banks['s'] == source,'source preserved')
    return banks['t'],banks['c']

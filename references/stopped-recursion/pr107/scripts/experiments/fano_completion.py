"""Two arbitrary-scratch completions of the q=2 Fano XOR code.

The register realizations are our constructions; they are not claimed to
preserve the capacity graph of the source network-coding instance.
"""
from hashlib import sha256
import json

from certify import require
from finite_bit_contract import xor_gate, scalar_permutation


FANO_EDGES = (
    ('a','u1'),('a','tc'),('b','u1'),('b','u2'),('c','u2'),('c','u6'),
    ('u1','u3'),('u2','u4'),('u3','u5'),('u3','u6'),('u4','u5'),('u4','ta'),
    ('u5','u7'),('u6','u8'),('u7','u9'),('u7','tc'),('u8','u9'),('u8','ta'),
    ('u9','u10'),('u10','tb'))


def code(compact=True, edge_explicit=False):
    if edge_explicit:
        incoming = {}; nodes = []
        for i,(u,v) in enumerate(FANO_EDGES):
            nodes.append((('a','b','c').index(u),) if u in ('a','b','c') else tuple(incoming[u]))
            incoming.setdefault(v,[]).append(3+i)
        return dict(nodes=nodes,outputs=[tuple(incoming[t]) for t in ('ta','tb','tc')])
    # Input IDs 0,1,2 are a,b,c. Each subsequent ID is one computed node.
    nodes = [(0,1),(1,2),(3,4),(3,2),(5,6)]  # p,q,r,s,t
    if compact:
        outputs = [(6,4),(7,),(5,0)]         # s+q, t, r+a
    else:
        nodes += [(6,4),(5,0)]              # decoded a,c registers
        outputs = [(8,),(7,),(9,)]
    return dict(nodes=nodes,outputs=outputs)


def addition(source, target, auxiliary, compact=True, signal_first=False, dirty=True, edge_explicit=False):
    spec = code(compact,edge_explicit)
    require(len(source) == len(target) == 3 and len(auxiliary) == len(spec['nodes']), 'Wrong bank size')
    require(len(set(source+target+auxiliary)) == len(source+target+auxiliary), 'Banks overlap')
    role = lambda x: source[x] if x < 3 else auxiliary[x-3]
    def compute(with_sources):
        return [xor_gate(auxiliary[i],role(child)) for i,args in enumerate(spec['nodes'])
                for child in args if with_sources or child >= 3]
    C, C0 = compute(True),compute(False)
    J = [xor_gate(target[t],role(child)) for t,args in enumerate(spec['outputs']) for child in args if child >= 3]
    K = [xor_gate(target[t],role(child)) for t,args in enumerate(spec['outputs']) for child in args if child < 3]
    signal = C+J+list(reversed(C))
    cancel = C0+J+list(reversed(C0))
    body = signal if not dirty else signal+cancel if signal_first else cancel+signal
    return body+K


def completed_swap(compact=True, shared=True, signal_first=False, dirty=True, edge_explicit=False):
    width = len(code(compact,edge_explicit)['nodes']); W = 6+width*(1 if shared else 3)
    X,Y = list(range(3)),list(range(3,6)); gates = []
    for stage,(source,target) in enumerate(((X,Y),(Y,X),(X,Y))):
        start = 6+(0 if shared else stage*width)
        gates += addition(source,target,list(range(start,start+width)),compact,signal_first,dirty,edge_explicit)
    return dict(W=W,gates=gates)


def case_name(compact, shared, signal_first):
    return '-'.join(('compact' if compact else 'decoded','shared' if shared else 'separate',
                     'signal-first' if signal_first else 'cancel-first'))


def cases():
    for compact in (True,False):
        for shared in (True,False):
            for signal_first in (False,True):
                yield case_name(compact,shared,signal_first),completed_swap(compact,shared,signal_first)
    for shared in (True,False):
        for signal_first in (False,True):
            name = case_name(True,shared,signal_first).replace('compact','edge')
            yield name,completed_swap(shared=shared,signal_first=signal_first,edge_explicit=True)
    # Individual shears have the same additive dirty-scratch offset. With a
    # shared bank it cancels across the three-stage exchange, so C0 is optional
    # globally even though it is necessary for a clean individual addition.
    for layout,compact,edge in (('compact',True,False),('decoded',False,False),('edge',True,True)):
        yield layout+'-shared-global-cancel',completed_swap(compact=compact,shared=True,dirty=False,edge_explicit=edge)


def program_hash(program):
    return sha256(json.dumps(program,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def clean_prefix(compact=True,edge_explicit=False):
    spec = code(compact,edge_explicit); W = 6+len(spec['nodes'])
    role = lambda x:x if x < 3 else 6+x-3
    gates = [xor_gate(6+i,role(child)) for i,args in enumerate(spec['nodes']) for child in args]
    gates += [xor_gate(3+i,role(child)) for i,args in enumerate(spec['outputs']) for child in args]
    return dict(W=W,gates=gates)


def scalar_check(program):
    W,gates = program['W'],program['gates']
    rho = scalar_permutation(W,gates)
    require(rho == tuple(list(range(3,6))+list(range(3))+list(range(6,W))),
            'Incorrect exchange or dirty scratch restoration')
    values = [1 << w for w in range(W)]
    for gate in gates:
        for t,s in gate['xors']: values[t] ^= values[s]
    for gate in reversed(gates):
        for t,s in reversed(gate['xors']): values[t] ^= values[s]
    require(values == [1 << w for w in range(W)], 'Inverse failed')
    return dict(W=W,primitive_xors=len(gates),rho=list(rho),all_inputs_independent=True,
                arbitrary_auxiliary_inputs_restored=True,inverse_exact=True,program_sha256=program_hash(program))

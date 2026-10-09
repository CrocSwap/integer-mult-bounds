"""Exact finite XOR-circuit/rational-frame contract, without fixed stage cuts.

All roles carry arbitrary inputs. A gate is a sequence of XOR updates on its
listed ports, with one common rational matrix for every incidence. rho maps
INPUT roles to OUTPUT roles. No geometric or projection ansatz is imposed.
"""
from fractions import Fraction
from itertools import permutations

from audit_joint_frames import eye, rank, sub
from certify import require


def validate_circuit(W, gates):
    require(type(W) is int and W >= 2, 'Need at least two roles')
    require(isinstance(gates,(tuple,list)), 'Gate sequence must be explicit')
    for gate in gates:
        require(isinstance(gate,dict) and set(gate) <= {'roles','xors','frame'}, 'Unsupported gate fields')
        require(isinstance(gate['roles'],(tuple,list)) and isinstance(gate['xors'],(tuple,list)),
                'Ports and XOR updates must be explicit sequences')
        roles = tuple(gate['roles'])
        require(roles and len(set(roles)) == len(roles), 'Gate ports must be distinct and nonempty')
        require(all(type(r) is int and 0 <= r < W for r in roles), 'Invalid gate port')
        for update in gate['xors']:
            require(len(update) == 2, 'XOR needs target and control')
            t, s = update
            require(type(t) is int and type(s) is int and t in roles and s in roles and t != s,
                    'XOR must use distinct listed ports')


def scalar_permutation(W, gates):
    """Return rho(input)=output; reject every nonpermutation linear map."""
    validate_circuit(W, gates)
    values = [1 << w for w in range(W)]
    for gate in gates:
        for t, s in gate['xors']:
            values[t] ^= values[s]
    require(set(values) == {1 << w for w in range(W)}, 'Scalar map is not an all-role permutation')
    rho = [None]*W
    for output, value in enumerate(values):
        rho[value.bit_length()-1] = output
    return tuple(rho)


def physical_graph(W, gates):
    """Every physical segment, including untouched roles and terminal edges."""
    validate_circuit(W, gates)
    last = list(range(W)); edges = []
    for index, gate in enumerate(gates):
        node = W+index
        for role in gate['roles']:
            edges.append((last[role], node, role))
            last[role] = node
    for role in range(W):
        edges.append((last[role], W+len(gates)+role, role))
    return edges


def rational_matrix(value, m):
    require(isinstance(value, (tuple,list)) and len(value) == m, 'Wrong matrix height')
    result = []
    for row in value:
        require(isinstance(row, (tuple,list)) and len(row) == m, 'Wrong matrix width')
        out = []
        for x in row:
            require(type(x) is int or isinstance(x, (Fraction,str)), 'Use exact rational entries, never floats')
            out.append(Fraction(x))
        result.append(tuple(out))
    return tuple(result)


def inspect_candidate(candidate, require_deficit=True):
    """Verify an explicit candidate; strict transfer eligibility is the default.

    Set require_deficit=False only to score nonimproving controls. The result
    then explicitly says whether the full strict transfer contract is met.
    """
    W, m, gates = candidate['W'], candidate['m'], candidate['gates']
    require(type(m) is int and m >= 2, 'Need matrix dimension at least two')
    rho = scalar_permutation(W, gates)
    require(isinstance(candidate['rho'],(tuple,list)) and
            all(type(r) is int for r in candidate['rho']), 'Declare an integer role permutation')
    require(tuple(candidate['rho']) == rho, 'Wrong input-to-output permutation')
    require(len(candidate['source_frames']) == len(candidate['sink_frames']) == W,
            'Every role needs both terminal frames')
    sources = tuple(rational_matrix(M,m) for M in candidate['source_frames'])
    sinks = tuple(rational_matrix(M,m) for M in candidate['sink_frames'])
    internal = tuple(rational_matrix(g['frame'],m) for g in gates)
    I = eye(m)
    require(all(sub(sinks[rho[w]],sources[w]) == I for w in range(W)),
            'An all-role endpoint identity fails')
    frames = sources+internal+sinks
    edges = physical_graph(W,gates)
    costs = tuple(rank(sub(frames[v],frames[u])) for u,v,_ in edges)
    s = sum(costs); delta = W*m-s
    require(not require_deficit or delta > 0, 'No strict rank deficit')
    return dict(W=W,m=m,rho=list(rho),gates=len(gates),physical_edges=len(edges),
                edge_ranks=list(costs),s=s,baseline=W*m,deficit=delta,
                rank_ratio=str(Fraction(s,W*m)),scalar_and_endpoints_verified=True,
                strict_transfer_contract=delta > 0)


def find_routing(W, gates, max_states=5040, max_gate_arity=7):
    """Exact bounded routing search, independent of frames and scalar updates.

    At each common-frame gate, route its incoming tokens bijectively to its
    outgoing ports. A budget failure raises; it never reports nonroutability.
    """
    rho = scalar_permutation(W,gates)
    want = [None]*W
    for w,out in enumerate(rho): want[out] = w
    states = {tuple(range(W)): ()}
    for gate in gates:
        roles = tuple(gate['roles'])
        require(len(roles) <= max_gate_arity, 'Routing gate-arity budget exceeded')
        nxt = {}
        for state, choices in states.items():
            for input_ports in permutations(roles):
                new = list(state)
                for out,source in zip(roles,input_ports): new[out] = state[source]
                nxt.setdefault(tuple(new), choices+(input_ports,))
                require(len(nxt) <= max_states, 'Routing state budget exceeded')
        states = nxt
    choices = states.get(tuple(want))
    if choices is None:
        return dict(routable=False, exhaustive=True, reachable_permutations=len(states))
    paths = [[] for _ in range(W)]; tokens = list(range(W)); edge_index = 0
    for gate, input_ports in zip(gates, choices):
        roles = tuple(gate['roles'])
        for role in roles:
            paths[tokens[role]].append(edge_index); edge_index += 1
        old = list(tokens)
        for out,source in zip(roles,input_ports): tokens[out] = old[source]
    for role in range(W):
        paths[tokens[role]].append(edge_index); edge_index += 1
    check = check_routing_paths(W,gates,paths)
    return dict(routable=True, exhaustive=True, reachable_permutations=len(states),
                gate_input_ports=[list(p) for p in choices], paths=paths,check=check)


def check_routing_paths(W, gates, paths):
    """Check explicit edge-disjoint routes for the ACTUAL scalar permutation.

    A successful certificate proves s>=W*m for every rational frame assignment
    obeying the endpoint identities, in every dimension m.
    """
    rho = scalar_permutation(W,gates); edges = physical_graph(W,gates)
    require(len(paths) == W, 'One path is required for every input role')
    used = set()
    for w,path in enumerate(paths):
        current = w
        for index in path:
            require(type(index) is int and 0 <= index < len(edges), 'Invalid path edge')
            require(index not in used, 'Routing paths share a physical edge')
            u,v,_ = edges[index]
            require(u == current, 'Disconnected routing path')
            used.add(index); current = v
        require(current == W+len(gates)+rho[w], 'Path has wrong routed endpoint')
    return dict(paths=W,used_edges=len(used),total_edges=len(edges),
                edge_disjoint=True,actual_scalar_permutation=True,
                rank_lower_bound='W*m',scope='All rational frames satisfying the endpoint identities, all m>=2.')


def xor_gate(target, source):
    return dict(roles=[target,source],xors=[[target,source]])


def zero_frame_candidate(W, gates, m=2):
    """Universal equality control: zero sources/gates, identity sinks."""
    Z = tuple((0,)*m for _ in range(m)); I = eye(m)
    return dict(W=W,m=m,rho=list(scalar_permutation(W,gates)),
                source_frames=[Z]*W,sink_frames=[I]*W,
                gates=[dict(g,frame=Z) for g in gates])


if __name__ == '__main__':
    import argparse
    import json
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('candidate',type=Path,help='JSON circuit and complete rational frame assignment')
    parser.add_argument('--score-only',action='store_true',help='Permit controls without a strict rank deficit')
    args = parser.parse_args()
    try:
        result = inspect_candidate(json.loads(args.candidate.read_text()),require_deficit=not args.score_only)
    except (ValueError,KeyError,TypeError,ZeroDivisionError) as error:
        parser.error(str(error))
    print(json.dumps(result,indent=2,sort_keys=True))

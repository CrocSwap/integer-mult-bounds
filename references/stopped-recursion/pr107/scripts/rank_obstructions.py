"""Exact positive witnesses for stronger finite-rank rejection screens.

Failed discovery is never a rejection certificate. These routines check
supplied fractional paths or characteristic-zero gate realizations.
"""
from fractions import Fraction as Q

from audit_joint_frames import eye, zero, matrix, add, sub, rank, product
from audit_stage_pair import kron
from certify import require
from finite_bit_contract import scalar_permutation, rational_matrix


def check_fractional_paths(edges, demands, flows, required_rates=None):
    require(len(flows) == len(demands), 'One path collection per demand required')
    required_rates = list(required_rates) if required_rates is not None else [Q(1)]*len(demands)
    require(len(required_rates) == len(demands), 'Wrong rate count')
    require(all(type(x) is int or isinstance(x, (Q, str)) for x in required_rates), 'Use exact rates')
    required_rates = [Q(x) for x in required_rates]
    require(all(x >= 0 for x in required_rates), 'Rates must be nonnegative')
    require(all(u != v for u, v in edges), 'Self-loop edges are not supported')
    loads = [Q(0)]*len(edges); rates = []; backwards = 0
    for (source, target), paths, required in zip(demands, flows, required_rates):
        require(source != target, 'Demand endpoints must differ')
        rate = Q(0)
        for item in paths:
            value = item['weight']
            require(type(value) is int or isinstance(value, (Q, str)), 'Use exact rational weights')
            weight = Q(value)
            require(weight > 0, 'Only positive path weights are accepted')
            at = source; seen = {at}
            for e in item['edges']:
                require(type(e) is int and 0 <= e < len(edges), 'Invalid edge index')
                u, v = edges[e]
                require(at in (u, v), 'Disconnected path')
                reverse = at == v
                at = u if reverse else v
                require(at not in seen, 'Path is not simple')
                seen.add(at); loads[e] += weight; backwards += int(reverse)
            require(at == target, 'Wrong demand endpoint')
            rate += weight
        require(rate >= required, 'Demand rate is insufficient')
        rates.append(rate)
    require(all(load <= 1 for load in loads), 'A shared undirected edge exceeds capacity')
    return dict(rates=rates, total_rate=sum(rates), loads=loads,
                backward_traversals=backwards, exact_shared_capacity_check=True)


def scalar_lift(W, gates, local_matrices):
    require(len(local_matrices) == len(gates), 'One local matrix per gate required')
    rho = scalar_permutation(W, gates)
    full = eye(W); operators = []
    for gate, local in zip(gates, local_matrices):
        ports = gate['roles']; local = rational_matrix(local, len(ports))
        T = [list(row) for row in eye(W)]
        for i, r in enumerate(ports):
            T[r] = [Q(0)]*W
            for j, s in enumerate(ports): T[r][s] = local[i][j]
        T = matrix(T); operators.append(T); full = product(T, full)
    coefficients = []
    for w, out in enumerate(rho):
        require(full[out][w] != 0 and all(not full[out][j] for j in range(W) if j != w),
                'Characteristic-zero action is not monomial with the required permutation')
        coefficients.append(full[out][w])
    return dict(rho=rho, coefficients=coefficients, transfer=full, operators=operators,
                all_rational_frames_excluded=True, rank_lower_bound='W*m')


def block_diagonal(blocks):
    m = len(blocks[0]); W = len(blocks)
    return matrix([[blocks[i//m][i%m][j%m] if i//m == j//m else 0
                    for j in range(W*m)] for i in range(W*m)])


def check_telescope(W, gates, local_matrices, sources, internal, sinks):
    """Check the rank-telescoping identity on a supplied finite control.

    The accompanying written proof establishes the general obstruction.
    """
    lifted = scalar_lift(W, gates, local_matrices)
    require(len(sources) == len(sinks) == W and len(internal) == len(gates), 'Missing frame')
    m = len(sources[0]); I = eye(m)
    sources = [rational_matrix(M, m) for M in sources]
    internal = [rational_matrix(M, m) for M in internal]
    sinks = [rational_matrix(M, m) for M in sinks]
    require(all(sub(sinks[lifted['rho'][w]], sources[w]) == I for w in range(W)), 'Wrong endpoint identities')
    operators = lifted['operators']; prefix = [eye(W)]
    for T in operators: prefix.append(product(T, prefix[-1]))
    suffix = [None]*len(operators)+[eye(W)]
    for j in range(len(operators)-1, -1, -1): suffix[j] = product(suffix[j+1], operators[j])
    total = zero(W*m); last = list(sources); costs = []
    for j, gate in enumerate(gates):
        for role in gate['roles']:
            delta = sub(internal[j], last[role]); costs.append(rank(delta))
            outer = matrix([[suffix[j][out][role]*prefix[j][role][inp]
                             for inp in range(W)] for out in range(W)])
            total = add(total, kron(outer, delta)); last[role] = internal[j]
    for role in range(W):
        delta = sub(sinks[role], last[role]); costs.append(rank(delta))
        outer = matrix([[lifted['transfer'][role][inp] if out == role else 0
                         for inp in range(W)] for out in range(W)])
        total = add(total, kron(outer, delta))
    transfer = kron(lifted['transfer'], I)
    discrepancy = sub(product(block_diagonal(sinks), transfer), product(transfer, block_diagonal(sources)))
    require(total == discrepancy, 'Edge discrepancy does not telescope')
    require(rank(discrepancy) == W*m <= sum(costs), 'Rank obstruction failed')
    return dict(W=W, m=m, discrepancy_rank=rank(discrepancy), edge_ranks=costs,
                rank_sum=sum(costs), exact_telescope=True,
                monomial_coefficients=lifted['coefficients'])

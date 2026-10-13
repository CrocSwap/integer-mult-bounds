"""Actual pinned rounded leaves, exact dense oracles and restoration checks.

Gareth Davidson (@bitplane), substantial OpenAI Codex assistance; Apache-2.0.
"""
import hashlib
import json
from fractions import Fraction as Q


def run_case(core, vendor, factors, beta, radix, length, direction, dirt, target, prepared=None):
    n = len(factors)
    scratch, calls, exponent = core.resources(n)
    arrays = [[(Q(dirt+2*i+j, 4), Q(dirt-3*i-j, 8)) for i in range(length)]
              for j in range(scratch+2)]
    original = [a[:] for a in arrays]
    D = max(abs(x)+abs(y) for arr in arrays for x, y in arr)
    K, a = Q(radix)/beta, 13*(radix+1)/beta**3
    bits = max(core.working_bits(n, K, a, D, target+1, 3), core.ceil_log2(2/beta**2))
    bound = core.execution_parameters(n, K, a, D, bits)
    core.need(Q(1, 2**bits) <= beta**2/2, "rounded leaf closure")
    phases = [vendor.c.ONE, (Q(0), Q(1)), (Q(3, 5), Q(4, 5))][:length]
    core.need(not any(phases is arr for arr in arrays), "phase alias outside contract")
    # The predecessor's oracle expands the prepared polynomial and uses dense
    # Gauss-Jordan elimination, rather than the lifting/commutator recurrence.
    if prepared:
        exact = vendor.w.solve(vendor.w.matrix(prepared['q'], phases, direction), original[0])
        perturbation = Q(prepared['certificate']['factorization_inverse_error_bound'])*D
        core.need(perturbation <= Q(1, 2**(target+1)), "unchanged factor certificate insufficient for source scale")
    else:
        exact = vendor.exact_operator(original[0], factors, phases, direction)
        perturbation = Q(0)
    observed = {'leaves': 0, 'maximum_squared': max(vendor.c.norm2(z) for arr in arrays for z in arr)}
    leaf = vendor.leaf

    def monitored(x, y, factor, ps, b, w, d, sign, stats):
        before = x[:]
        leaf(x, y, factor, ps, b, w, d, sign, stats)
        core.need(x == before, "leaf failed exact source restoration")
        observed['leaves'] += 1
        observed['maximum_squared'] = max(observed['maximum_squared'], max(map(vendor.c.norm2, y)))

    try:
        vendor.leaf = monitored
        stats = dict(leaves=0, scalar_steps=0)
        vendor.compose(*arrays[:2], factors, arrays[2:], phases, beta, bits, direction, stats=stats)
    finally:
        vendor.leaf = leaf
    core.need(stats['leaves'] == calls == observed['leaves'], "full leaf count")
    core.need(stats['scalar_steps'] == 3*length*calls, "paid three-pass accounting")
    core.need(arrays[0] == original[0] and arrays[2:] == original[2:], "exact dirty restoration")
    core.need(observed['maximum_squared'] <= bound['magnitude_bound']**2, "actual boundary magnitude")
    net = [vendor.c.sub(x, y) for x, y in zip(arrays[1], original[1])]
    error2 = max(vendor.c.norm2(vendor.c.sub(x, y)) for x, y in zip(net, exact))
    core.need(error2 <= bound['error_bound']**2, "new execution error bound")
    core.need(bound['error_bound']+perturbation <= Q(1, 2**target), "combined preparation/execution budget")
    # Same grid and same deterministic leaf; negative whole word cancels exactly.
    vendor.compose(*arrays[:2], factors, arrays[2:], phases, beta, bits, direction, -1)
    core.need(arrays == original, "whole-word exact inverse")
    evidence = json.dumps([net, exact, error2, bound['error_bound'], perturbation], default=str, separators=(',', ':'))
    return dict(factors=n, radix=radix, length=length, direction=direction, dirt=dirt,
                target_bits=target, working_bits=bits, leaf_calls=calls, prefix_exponent=exponent,
                boundary_checks=observed['leaves'], scalar_steps=stats['scalar_steps'],
                error_squared_log2_upper=core.ceil_log2(error2) if error2 else None,
                execution_bound_log2_upper=core.ceil_log2(bound['error_bound']),
                exact_evidence_sha256=hashlib.sha256(evidence.encode()).hexdigest(),
                source_and_dirty_restored=True, inverse_cancels=True,
                coefficient_perturbation_checked=prepared is not None)


def generic(core, vendor):
    result = []
    for n in (1, 2, 3, 5, 8, 17):
        factors = [(i%2 == 0, (Q(1, 4), Q((-1)**i, 8)), Q(3 if i == 0 else 1)) for i in range(n)]
        for length in (1, 3):
            for direction in (-1, 1):
                for dirt in (-7, 11):
                    result.append(run_case(core, vendor, factors, Q(1, 2), 3, length, direction, dirt, 32))
    return result


def kernels(core, vendor, data):
    result = []
    for row in data:
        state = vendor.w.k.certify(row)
        factors = [(inside, b, Q(state['radix'] if i == 0 else 1)) for i, (inside, b) in enumerate(state['factors'])]
        for length in (1, 3):
            for direction in (-1, 1):
                # Both signs of initial dirt across both cycle orientations.
                result.append({**run_case(core, vendor, factors, state['beta'], state['radix'],
                                          length, direction, -7 if direction == -1 else 11, 128, state),
                               'embedding': state['embedding']})
    return result

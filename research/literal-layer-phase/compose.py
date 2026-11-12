"""Finite wrapper join: literal S, exact test oracle C, literal egress, literal S.

This supplies no executable C consumer. The oracle and its common-grid source
preparation are explicit outside services, not part of a physical time claim.
"""
from pathlib import Path
import hashlib
import json
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import phase as P
import oracles as O
from verify import need, run_case, extents


def egress_table():
    reference = HERE/'reference/literal-egress-patterns.py'
    source = reference.read_bytes()
    need(hashlib.sha256(source).hexdigest() ==
         '5875981b27bbb131a1e13ffca7f7eb920aa85b90699e6d40a85bd3902ff073e7', 'pinned egress source')
    # Relocate only the compile-time package directory to the shared exact
    # machine export. The unchanged source must emit its exact pinned table.
    namespace = {'__file__': str(HERE/'phase.py'), '__name__': 'pinned_egress_reference'}
    exec(compile(source, str(reference), 'exec'), namespace)
    code, _ = namespace['compile_egress']()
    digest = hashlib.sha256(json.dumps(code, separators=(',', ':'), sort_keys=True).encode()).hexdigest()
    need(digest == 'd3021bc0d7b378741e64ae768171f5aec1f289b15265f4463e7b91b887f11243', 'pinned egress graph')
    return code


def gaussian_multiply(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def exact_tensor(values, parameters, kind):
    """Direct small Cartesian sum, unrelated to the literal odometer."""
    _, global_d, r, dimension, outer, spectator, block, rho1, _ = parameters
    Q = 1 << (dimension*block)
    positions = [j*block+rho1-1 for j in range(dimension)]
    active_mask = sum(1 << j for j in positions)
    out = []
    for a in range(outer):
        for destination in range(Q):
            base = destination & ~active_mask
            for s in range(spectator):
                for coefficient in range(r):
                    total_real = total_imag = 0
                    for source in range(1 << dimension):
                        address = base
                        kernel = (1, 0)
                        sign = 1
                        for j, position in enumerate(positions):
                            x, y = (source >> j) & 1, (destination >> position) & 1
                            address |= x << position
                            kernel = gaussian_multiply(kernel, (1, 1 if x == y else -1))
                            sign *= -1 if x and y else 1
                        index = ((a*Q+address)*spectator+s)*r+coefficient
                        real, imag = values[index]
                        if kind == 'C':
                            real, imag = gaussian_multiply(kernel, (real, imag))
                        else:
                            real, imag = sign*real, sign*imag
                        total_real += real
                        total_imag += imag
                    if kind == 'C':
                        factor = 1 << (global_d-dimension)
                        out.append((factor*total_real, factor*total_imag))
                    else:
                        def toward_zero(value):
                            q = abs(value)//(1 << dimension)
                            return -q if value < 0 else q
                        out.append((toward_zero(total_real), toward_zero(total_imag)))
    return out


def run_join(parameters, source, phase_code, egress_code):
    p, d, _, _, _, _, _, _, w = parameters
    H = p+2*d+4
    N = O.cardinality(parameters)
    V, guarded = 2*N*w, 2*N*H
    first, tapes = run_case(phase_code, parameters, source, public_reserve=guarded)
    starts = [t.head for t in tapes]
    initial_private = [dict(t.cells) for t in tapes[2:]]
    header_before = dict(tapes[P.HEADER].cells)
    data = tapes[P.DATA]
    actual_first = O.decode(''.join(data.cells[data.origin+j] for j in range(V)), w)
    supplied_C = exact_tensor(actual_first, parameters, 'C')
    need(O.fits(supplied_C, H), 'common-grid producer range')
    # Explicit supplied C plus format pass, in the pre-reserved same-owner
    # window. This host computation is NOT claimed as a literal C implementation.
    data.cells = {k: v for k, v in data.cells.items()
                  if k < data.origin or k > data.origin+guarded}
    data.cells.update({data.origin+j: b for j, b in enumerate(O.encode(supplied_C, H))})
    data.begin(data.origin, guarded, public=True)
    tapes[P.HEADER].begin(starts[P.HEADER], len(O.header(parameters)), public=True)
    egress_tapes = [tapes[P.HEADER], data]
    for i in range(16):
        origin = 370+13*i
        egress_tapes.append(P.Tape({origin-2: '1'}, origin))
    egress_heads = [t.head for t in egress_tapes]
    egress_private = [dict(t.cells) for t in egress_tapes[2:]]
    need(len({id(t) for t in tapes+egress_tapes[2:]}) == 36, 'distinct fixed inventories')
    machine = P.Machine(egress_code, egress_tapes)
    machine.run(65536*(len(O.header(parameters))+p+d+parameters[3]+w+N*(H+w+1)+1))
    need(all(t.head == h for t, h in zip(egress_tapes, egress_heads)), 'egress head return')
    need([dict(t.cells) for t in egress_tapes[2:]] == egress_private, 'egress private return')
    need(all(data.cells.get(data.origin+j, P.BLANK) == P.BLANK for j in range(V, guarded+1)),
         'egress old common-grid tail cleanup')
    for i, t in enumerate(tapes):
        t.begin(starts[i], extents(parameters)[i], public=i<2)
    final = P.Machine(phase_code, tapes)
    final.run(65536*(len(O.header(parameters))+p+d+parameters[3]*parameters[6]+N*w+1))
    actual = O.decode(''.join(data.cells[data.origin+j] for j in range(V)), w)
    expected = exact_tensor(source, parameters, 'H0')
    need(actual == expected, 'literal wrappers versus direct normalized Walsh tensor')
    need(tapes[P.HEADER].cells == header_before, 'composition header preservation')
    need(all(t.head == h for t, h in zip(tapes, starts)), 'final phase head return')
    need([dict(t.cells) for t in tapes[2:]] == initial_private, 'same phase inventory retired twice')
    need(data.cells.get(data.origin+guarded+1) == '1' and
         data.cells.get(data.origin+guarded+2) == '|', 'parent-reservation exterior')
    return dict(parameters=parameters, coefficients=N,
                initial_phase_steps=first['steps'], egress_steps=machine.steps,
                final_phase_steps=final.steps, physical_tapes=36)


def main():
    phase_code, _ = P.compile_phase()
    egress_code = egress_table()
    rng = random.Random(0x7350)
    rows = []
    parameters_list = [(p, D+p % 2, 1, D, 1, 1, 1, 1, p+2)
                       for p in (1, 2) for D in range(1, 5)]
    parameters_list += [(2, 3, 2, 2, 2, 2, 2, rho+1, 4) for rho in (0, 1)]
    for parameters in parameters_list:
        radius = 1 << parameters[0]
        disk = [(a, c) for a in range(-radius, radius+1) for c in range(-radius, radius+1)
                if a*a+c*c <= radius*radius]
        source = [rng.choice(disk) for _ in range(O.cardinality(parameters))]
        rows.append(run_join(parameters, source, phase_code, egress_code))
    receipt = dict(status='PASS_LITERAL_PHASE_EGRESS_JOIN', cases=len(rows),
                   coefficients=sum(r['coefficients'] for r in rows), rows=rows,
                   limitations=['Exact C and its common-grid format preparation are test oracles, not implementations.',
                                'Only the two phase tables and pinned egress execute as literal programs.'])
    if '--write' in sys.argv:
        (HERE/'JOIN-RESULT.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print(json.dumps(receipt, sort_keys=True))


if __name__ == '__main__':
    main()

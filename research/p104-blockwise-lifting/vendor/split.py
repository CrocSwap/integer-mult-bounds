"""Exact residue split; ordinary owned-buffer reference. Tekalign/Codex, Apache-2.0.

The Walsh backend is direct, not an admitted fast recursive supplier.
Scratch reset is explicitly paid; it is not reversible uncomputation.
"""


def need(ok, message):
    if not ok:
        raise ValueError(message)


def rot(z, phase):
    a, b = z
    return ((a, b), (-b, a), (-a, -b), (b, -a))[phase % 4]


def wrap_inplace(value, plan):
    """Cycle permutation using one Gaussian scratch, zero after each cycle."""
    seen = set()
    for start in range(len(value)):
        if start in seen:
            continue
        scratch, value[start] = value[start], (0, 0)
        x = start
        while x not in seen:
            seen.add(x)
            y, phase = plan[x]
            scratch = rot(scratch, phase)
            scratch, value[y] = value[y], scratch
            x = y
        need(x == start and scratch == (0, 0), 'wrapper scratch')


def invert_plan(plan):
    result = [None] * len(plan)
    for x, (y, phase) in enumerate(plan):
        result[y] = (x, -phase % 4)
    return result


def linear(value, rank, left, right, inverse=False):
    """In-place exact 2**g U(value), g=floor(rank/2)+1.

    D H D factorization is independent of the floor-lifting implementation.
    All arithmetic is integer, including the final Gaussian factor.
    """
    if inverse:
        left, right = invert_plan(right), invert_plan(left)
    wrap_inplace(value, right)
    mask = (1 << rank) - 1
    direction = 1 if inverse else -1
    for x, z in enumerate(value):
        value[x] = rot(z, direction * (x & mask).bit_count())
    for bit in range(rank):
        step = 1 << bit
        for start in range(0, len(value), 2*step):
            for x in range(start, start+step):
                a, b = value[x]
                c, d = value[x+step]
                value[x], value[x+step] = (a+c, b+d), (a-c, b-d)
    for x, z in enumerate(value):
        a, b = rot(z, direction * (x & mask).bit_count() - direction * (rank//2))
        if rank % 2:
            value[x] = (a+b, b-a) if inverse else (a-b, a+b)
        else:
            value[x] = (2*a, 2*b)
    wrap_inplace(value, left)
    return value


def kernel(value, rank, left, right, lift, inverse=False, backend=linear,
           observer=None):
    """Overwrite value by the identical lifting map; clear owned q/s buffers.

    backend is a trusted exact-integer interface, not an arbitrary approximate
    native call. Tests independently check it. Observer is instrumentation only.
    """
    n = len(value)
    need(n > 1 and n & (n-1) == 0 and 1 <= rank < n.bit_length(), 'kernel domain')
    g = rank//2 + 1
    quotient = [(a >> g, b >> g) for a, b in value]
    mask = (1 << g)-1
    residue = [(a & mask, b & mask) for a, b in value]
    backend(quotient, rank, left, right, inverse)
    lift.kernel(residue, rank, left, right, inverse=inverse)
    for x, ((a, b), (c, d)) in enumerate(zip(quotient, residue)):
        value[x] = (a+c, b+d)
    for x in range(n):
        quotient[x] = residue[x] = (0, 0)
    if observer:
        observer(quotient, residue)
    return value


def invoice(n, rank, wrapper_cycles):
    """Per transport, excluding the backend internals and caller collector."""
    return dict(backend_calls=1, residue_pairs=n*rank//2,
                residue_real_adds=4*n*rank, residue_floor_halves=2*n*rank, residue_quarter_turns=n*rank//2,
                residue_pair_component_reads=2*n*rank,
                residue_pair_component_writes=2*n*rank,
                residue_wrapper_cycles=wrapper_cycles,
                residue_wrapper_swaps=2*n+wrapper_cycles,
                residue_wrapper_component_reads=4*(2*n+wrapper_cycles),
                residue_wrapper_component_writes=4*(2*n+wrapper_cycles),
                quotient_shift_components=2*n, residue_mask_components=2*n,
                split_component_reads=4*n, quotient_components_written=2*n,
                residue_components_written=2*n, combine_component_reads=4*n,
                combine_real_adds=2*n, combine_component_writes=2*n,
                clear_component_writes=4*n, residue_wrapper_values=2*n,
                residue_wrapper_count=2, owned_gaussian_buffers=2,
                guard_bits=rank//2+1)

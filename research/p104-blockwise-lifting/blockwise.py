"""Blocked P104 lifting and clean reversible macro words. Apache-2.0.

Ross Richardson with substantial OpenAI Codex assistance. The literal lifting
and scaled Walsh identity are Tekalign's PR3025/3033, not new primitives.
The direct backend here is a reference, NOT a fast recursive implementation.
"""
def need(ok, why):
    if not ok:
        raise ValueError(why)


def rotate(z, phase):
    a, b = z
    return ((a, b), (-b, a), (-a, -b), (b, -a))[phase % 4]


def literal(value, axes, inverse=False):
    out = list(value)
    for bit in reversed(axes) if inverse else axes:
        for x in range(len(out)):
            if x & (1 << bit):
                continue
            y = x | (1 << bit)
            a, b = out[x], out[y]
            d = (a[0]-b[0], a[1]-b[1])
            s = (b[0]+d[0]//2, b[1]+d[1]//2)
            d = rotate(d, -1 if inverse else 1)
            b = (s[0]-d[0]//2, s[1]-d[1]//2)
            out[x], out[y] = (b[0]+d[0], b[1]+d[1]), b
    return out


def scaled_backend(value, inverse=False):
    """Exact 2**g U_k, using PR3033's direct Walsh factorization."""
    n = len(value)
    need(n >= 2 and n & (n-1) == 0, 'backend cube')
    k, direction = n.bit_length()-1, 1 if inverse else -1
    out = [rotate(z, direction*x.bit_count()) for x, z in enumerate(value)]
    for bit in range(k):
        for x in range(n):
            if x & (1 << bit):
                continue
            y = x | (1 << bit)
            a, b = out[x], out[y]
            out[x], out[y] = (a[0]+b[0], a[1]+b[1]), (a[0]-b[0], a[1]-b[1])
    for x, z in enumerate(out):
        a, b = rotate(z, direction*(x.bit_count()-k//2))
        out[x] = ((a+b, b-a) if inverse else (a-b, a+b)) if k % 2 else (2*a, 2*b)
    return out


def signed_xor(x, y, width):
    modulus = 1 << width
    z = (x % modulus) ^ (y % modulus)
    return z-modulus if z >= modulus//2 else z


def add_mod(x, y, width):
    modulus = 1 << width
    z = (x+y) % modulus
    return z-modulus if z >= modulus//2 else z


def clean_oracle(source, target, width, inverse=False, work=None, meter=None,
                 backend=scaled_backend, clean_return=True):
    """(x,y,0)->(x,y XOR L_k(x),0), clean macro-level reference.

    Backend calls are exact source-preserving XOR oracles by contract. Their
    implementation, clean work and complete cost are an explicit theorem premise.
    All other work below is reversed literally; no data reset is used.
    """
    n = len(source)
    need(n >= 2 and n & (n-1) == 0 and len(target) == n, 'oracle shape')
    need(type(width) is int and width >= 4, 'word width')
    need(source is not target, 'source/target alias')
    need(all(type(t) is int and -(1 << (width-1)) <= t < (1 << (width-1))
             for v in (source, target) for z in v for t in z), 'signed word range')
    k, g = n.bit_length()-1, (n.bit_length()-1)//2+1
    need(width >= g+k+3, 'narrow signed headroom')
    if work is None:
        work = [[(0, 0)]*n for _ in range(3)]
    need(len(work) == 3 and all(len(v) == n for v in work), 'work shape')
    need(len({id(source), id(target), *(id(v) for v in work)}) == 5, 'work aliases')
    need(all(z == (0, 0) for v in work for z in v), 'clean work required')
    q, low, z = work
    def xor_array(a, b):
        for j in range(n):
            a[j] = tuple(signed_xor(x, y, width) for x, y in zip(a[j], b[j]))
    high = [(a >> g, b >> g) for a, b in source]
    residues = [(a % (1 << g), b % (1 << g)) for a, b in source]
    xor_array(q, high)
    xor_array(low, residues)
    exact = backend(q, inverse)
    need(all(-(1 << (width-1)) <= t < (1 << (width-1)) for v in exact for t in v),
         'backend output headroom')
    xor_array(z, exact)
    low[:] = literal(low, tuple(range(k)), inverse)
    need(all(abs(t) < (1 << (g+k+1)) for v in low for t in v), 'narrow headroom')
    for j in range(n):
        need(all(-(1 << (width-1)) <= x+y < (1 << (width-1))
                 for x, y in zip(z[j], low[j])), 'combined output headroom')
        z[j] = tuple(add_mod(x, y, width) for x, y in zip(z[j], low[j]))
    xor_array(target, z)
    if clean_return:
        for j in range(n):
            z[j] = tuple(add_mod(x, -y, width) for x, y in zip(z[j], low[j]))
        low[:] = literal(low, tuple(range(k)), not inverse)
        xor_array(z, backend(q, inverse))
        xor_array(low, residues)
        xor_array(q, high)
        need(all(v == (0, 0) for a in work for v in a), 'literal cleanup')
    if meter is not None:
        meter['backend_xor_calls'] += 2
        meter['narrow_pair_lifts'] += k*n
        meter['wide_modular_adds'] += 4*n
        meter['wide_target_xors'] += 2*n
    return target


def clean_permutation(value, width, inverse=False, meter=None):
    """Compute, swap, inverse-XOR: an in-place permutation with clean work."""
    target = [(0, 0)]*len(value)
    clean_oracle(value, target, width, inverse, meter=meter)
    value[:], target[:] = target[:], value[:]
    clean_oracle(value, target, width, not inverse, meter=meter)
    need(all(z == (0, 0) for z in target), 'inverse-XOR failed to erase old input')
    return value


def partition(rank, cap):
    need(type(rank) is type(cap) is int and 1 <= cap <= rank, 'partition domain')
    return (cap,)*(rank//cap) + ((rank % cap,) if rank % cap else ())


def cube_indices(n, start, size):
    """One r-bit address per word, then k-bit local addressing."""
    for upper in range(1 << (n-start-size)):
        for lower in range(1 << start):
            base = lower | (upper << (start+size))
            yield [base | (local << start) for local in range(1 << size)]


def blocked(value, parts, inverse=False, width=None, meter=None, inplace=False):
    """Paid dispatcher; inplace=True avoids a full ambient input snapshot.

    The default read-only convenience wrapper copies the input. That copy is
    not used by the in-place construction or its peak local-stock statement.
    """
    n = len(value).bit_length()-1
    need(1 << n == len(value) and parts and all(type(k) is int and k > 0 for k in parts)
         and sum(parts) <= n, 'blocked shape')
    out, schedule, start = value if inplace else list(value), [], 0
    for k in parts:
        schedule.append((start, k))
        start += k
    if inverse:
        schedule.reverse()
    for start, k in schedule:
        for indices in cube_indices(n, start, k):
            local = [(0, 0)]*len(indices)
            for j, i in enumerate(indices):
                local[j], out[i] = out[i], local[j]
            if width is None:
                g = k//2+1
                low = [(a % (1 << g), b % (1 << g)) for a, b in local]
                q = [(a >> g, b >> g) for a, b in local]
                wide = scaled_backend(q, inverse)
                narrow = literal(low, tuple(range(k)), inverse)
                local = [(a+c, b+d) for (a, b), (c, d) in zip(wide, narrow)]
            else:
                clean_permutation(local, width, inverse, meter)
            for j, i in enumerate(indices):
                local[j], out[i] = out[i], local[j]
            need(all(z == (0, 0) for z in local), 'local cube bank restoration')
            if meter is not None:
                meter['global_gaussian_swaps'] += 2*len(indices)
                meter['cube_transactions'] += 1
    return out


def invoice(n, parts):
    N = 1 << n
    return dict(cube_transactions=sum(N >> k for k in parts),
                backend_xor_calls=4*sum(N >> k for k in parts),
                narrow_pair_lifts=2*N*sum(parts),
                wide_modular_adds=8*N*len(parts),
                wide_target_xors=4*N*len(parts),
                global_gaussian_swaps=2*N*len(parts))


def gray_plan(rows, offset, linear, quadratic, phase):
    """O(N n) addressed-bit-work compiler for affine/quadratic-Z4 wrappers.

    Maintain every first derivative and one binary output label. This emits
    public program data; its table/schedule storage and access remain charged.
    """
    n = len(rows)
    need(n > 0 and len(linear) == len(quadratic) == n, 'wrapper dimension')
    need(all(type(t) is int and 0 <= t < (1 << n) for t in rows+quadratic),
         'wrapper rows')
    need(all(type(t) is int and 0 <= t < 4 for t in linear), 'wrapper linear phase')
    need(type(offset) is type(phase) is int and 0 <= offset < (1 << n), 'wrapper constants')
    columns = [sum(((rows[i] >> j) & 1) << i for i in range(n)) for j in range(n)]
    neighbors = [[k for k in range(n) if k != j and
                  ((quadratic[min(j, k)] >> max(j, k)) & 1)] for j in range(n)]
    result, x, y, f, deriv = [None]*(1 << n), 0, offset, phase % 4, list(linear)
    result[0] = (y, f)
    for step in range(1, 1 << n):
        bit = (step & -step).bit_length()-1
        f = (f + (1-2*((x >> bit) & 1))*deriv[bit]) % 4
        for k in neighbors[bit]:
            deriv[k] = (deriv[k]+2) % 4
        x ^= 1 << bit
        y ^= columns[bit]
        result[x] = (y, f)
    seen = bytearray(1 << n)
    for y, _ in result:
        need(not seen[y], 'wrapper not bijective')
        seen[y] = 1
    return result

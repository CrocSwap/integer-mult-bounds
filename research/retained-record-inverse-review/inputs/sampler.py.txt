"""Run the integer caller and retain every value required by its inverse.

The pair map and route formula extend Ali Romman's PR6532 implementation.
"""

from fractions import Fraction as Q
from hashlib import sha256


def need(ok, label):
    if not ok:
        raise ValueError(label)


def phase(z, p):
    a, b = z
    p %= 4
    if p == 0:
        return a, b
    if p == 1:
        return -b, a
    if p == 2:
        return -a, -b
    return b, -a


def pair(x, y, seed, inverse=False):
    need(type(seed) is int and seed in (-1, 1), "pair seed")
    a, b = x
    c, d = y
    sr, si, dr, di = a+c, b+d, a-c, b-d
    cr = ci = 0
    if (sr+si) % 2:
        if sr % 2:
            cr = seed if sr > 0 else -seed
        else:
            ci = seed if si > 0 else -seed
    dr, di = dr-cr, di-ci
    dr, di = (di, -dr) if inverse else (-di, dr)
    dr, di = dr+cr, di+ci
    nums = sr+dr, si+di, sr-dr, si-di
    need(all(v % 2 == 0 for v in nums), "integer pair output")
    a, b, c, d = (v//2 for v in nums)
    return (a, b), (c, d)


def route(rec):
    dest, phases = [], []
    n = len(rec["matrix_rows"])
    for x in range(1 << n):
        dest.append(sum(((row & x).bit_count() % 2) << j
                        for j, row in enumerate(rec["matrix_rows"])) ^ rec["offset"])
        p = rec["phase"]
        for j in range(n):
            if x >> j & 1:
                p += rec["linear_Z4"][j]
                p += 2 * (((rec["quadratic_rows"][j] >> (j+1)) & (x >> (j+1))).bit_count() % 2)
        phases.append(p % 4)
    need(sorted(dest) == list(range(1 << n)), "monomial permutation")
    return dest, phases


def monomial(values, routing, f, inverse=False):
    dest, phases = routing
    out = [None] * len(values)
    for src in range(len(values)):
        dst, p = 0, 0
        for axis in range(f):
            digit = (src >> (9*axis)) & 511
            dst |= dest[digit] << (9*axis)
            p += phases[digit]
        if inverse:
            out[src] = phase(values[dst], -p)
        else:
            out[dst] = phase(values[src], p)
    return out


def native(values, routes, rank, seeds, f=1, inverse=False):
    need(type(f) is int and f >= 1 and len(values) == 512**f, "native shape")
    axes = [9*j+k for j in range(f) for k in range(rank)]
    need(len(seeds) == len(axes), "native seed count")
    left, right = routes
    out = monomial(values, left if inverse else right, f, inverse)
    order = reversed(range(len(axes))) if inverse else range(len(axes))
    for j in order:
        stride = 1 << axes[j]
        for start in range(0, len(out), 2*stride):
            for low in range(stride):
                a, b = start+low, start+low+stride
                out[a], out[b] = pair(out[a], out[b], seeds[j], inverse)
    return monomial(out, right if inverse else left, f, inverse)


def quantized(values, q, seed):
    d = q.denominator
    need(type(seed) is int and 0 <= seed < d, "scalar seed")
    return [((q.numerator*a+seed)//d, (q.numerator*b+seed)//d) for a, b in values]


def pack_remainders(values, q, seed):
    d = q.denominator
    bits = d.bit_length()-1
    need(abs(q.numerator) == 1 and bits > 0, "division residue contract")
    out = bytearray((2*len(values)*bits+7)//8)
    pos = 0
    for z in values:
        for v in z:
            residue = (q.numerator*v+seed) % d
            for k in range(bits):
                out[pos//8] |= ((residue >> k) & 1) << (pos % 8)
                pos += 1
    return bytes(out)


def restore_division(values, q, seed, packed):
    d = q.denominator
    bits = d.bit_length()-1
    need(abs(q.numerator) == 1 and bits > 0, "division residue contract")
    size = 2*len(values)*bits
    need(len(packed) == (size+7)//8, "residue byte length")
    need(not size % 8 or packed[-1] >> (size % 8) == 0, "residue padding")
    out, pos = [], 0
    for z in values:
        value = []
        for v in z:
            rem = 0
            for k in range(bits):
                rem |= ((packed[pos//8] >> (pos % 8)) & 1) << k
                pos += 1
            value.append(q.numerator * (d*v+rem-seed))
        out.append(tuple(value))
    return out


def digest(fields):
    h = sha256()
    for r, values in sorted(fields.items()):
        h.update(f"{r}:".encode())
        for a, b in values:
            h.update(f"{a},{b};".encode())
    return h.hexdigest()


def execute(word, recipes, initial, seed_value, f=1):
    """Use supplied seeds; a deterministic test stream is not a randomness proof."""
    fields = {r: list(v) for r, v in initial.items()}
    tape, routes = [], {}
    peak_fields = len(fields)
    retained_fields = scalar_seed_bits = native_seed_bits = residue_bits = 0
    max_abs = max(abs(t) for v in fields.values() for z in v for t in z)
    for j, e in enumerate(word["program"]):
        op, r = e[:2]
        if op == "INIT":
            need(r not in fields, "allocate unused field")
            fields[r] = [(0, 0)] * (512**f)
            record = None
        elif op == "CLEAR":
            record = fields.pop(r)
            retained_fields += 1
        elif op == "COPY":
            need(Q(e[3]) == 1, "selected exact COPY coefficient")
            record = fields[r]
            fields[r] = list(fields[e[2]])
            retained_fields += 1
        elif op == "MOVE":
            key = f"{e[2]},{e[3]}"
            rec = recipes[key]
            if key not in routes:
                routes[key] = (route(rec['left']), route(rec['right']))
            raw = [seed_value(j, k, 2) for k in range(rec['rank']*f)]
            need(all(type(v) is int and v in (0,1) for v in raw), 'fresh bit range')
            record = [1 if v else -1 for v in raw]
            native_seed_bits += len(record)
            fields[r] = native(fields[r], routes[key], rec['rank'], record, f)
        else:
            need(op in {'ADD', 'SCALE'}, "known scalar instruction")
            q = Q(e[-2])
            seed = seed_value(j, 0, q.denominator) if q.denominator > 1 else 0
            scalar_seed_bits += q.denominator.bit_length()-1
            record = (seed, None)
            if op == 'ADD':
                inc = quantized(fields[e[2]], q, seed)
                fields[r] = [(a+c, b+d) for (a,b),(c,d) in zip(fields[r],inc)]
            else:
                if q.denominator > 1:
                    packed = pack_remainders(fields[r], q, seed)
                    residue_bits += 2*len(fields[r])*(q.denominator.bit_length()-1)
                    record = (seed, packed)
                fields[r] = quantized(fields[r], q, seed)
        tape.append(record)
        peak_fields = max(peak_fields, len(fields)+retained_fields)
        if r in fields:
            max_abs = max(max_abs, max(abs(t) for z in fields[r] for t in z))
    output = {r: list(v) for r, v in fields.items()}
    for j in reversed(range(len(tape))):
        e, record = word['program'][j], tape[j]
        tape[j] = None
        op, r = e[:2]
        if op == 'INIT':
            need(all(z == (0,0) for z in fields.pop(r)), "reverse allocation is zero")
        elif op == 'CLEAR':
            need(r not in fields, "restore cleared field")
            fields[r] = record
        elif op == 'COPY':
            need(fields[r] == fields[e[2]], "reverse COPY value")
            fields[r] = record
        elif op == 'MOVE':
            key = f"{e[2]},{e[3]}"
            fields[r] = native(fields[r], routes[key], recipes[key]['rank'], record, f, True)
        else:
            q, (seed, packed) = Q(e[-2]), record
            if op == 'ADD':
                inc = quantized(fields[e[2]], q, seed)
                fields[r] = [(a-c, b-d) for (a,b),(c,d) in zip(fields[r],inc)]
            elif q.denominator > 1:
                fields[r] = restore_division(fields[r], q, seed, packed)
            else:
                need(all(t % q.numerator == 0 for z in fields[r] for t in z), "reverse integer scale")
                fields[r] = [(a//q.numerator,b//q.numerator) for a,b in fields[r]]
    need(fields == initial, "literal complete inverse")
    return output, {'initial_sha256':digest(initial),'output_sha256':digest(output),
                    'retained_field_values':retained_fields,'peak_live_and_retained_fields':peak_fields,
                    'native_seed_bits':native_seed_bits,'scalar_seed_bits':scalar_seed_bits,
                    'division_residue_bits':residue_bits,'max_absolute_payload':max_abs,
                    'all_events_forward_and_reverse':len(tape)}

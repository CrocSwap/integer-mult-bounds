"""Finite sequential execution of the cached chirp and synthetic ring convolution.

The input list and the result list are the external serialization only. Every
field between them has one current head. A trace counts reads, writes and
head travel in bits. The tape interpreter compresses consecutive movements.
Loop control uses the public geometry. Scalar arithmetic is a word primitive.
"""
from dataclasses import dataclass
from math import isqrt, prod
from word_multiply import product as mul


@dataclass
class Trace:
    reads: int = 0
    writes: int = 0
    travel: int = 0
    resets: int = 0
    erased: int = 0
    high_water: int = 0
    live: int = 0
    rings: int = 0
    stages: int = 0
    h_bits: int = 0
    scalar_products: int = 0
    max_scalar_operand: int = 0
    fast_words: int = 0
    root_enclosures: int = 0
    phase_updates: int = 0
    grouped_requests: int = 0
    native_requests: int = 0
    max_support: int = 0
    bit_swaps: int = 0


class Tape:
    """One sequential tape of fixed-width two-component sign-magnitude records."""

    def __init__(self, width, trace):
        self.width = width
        self.trace = trace
        self.cells = []
        self.head = 0
        self.released = False

    def seek(self, index):
        if self.released or not 0 <= index <= len(self.cells):
            raise ValueError("invalid tape address")
        self.trace.travel += abs(self.head - index) * (2 * self.width)
        self.head = index

    def home(self):
        self.seek(0)
        self.trace.resets += 1

    def append(self, z):
        if self.released or self.head != len(self.cells):
            raise ValueError("tail write requires a live head at the end")
        if any(abs(x).bit_length() >= self.width for x in z):
            raise ArithmeticError("signed field overflow")
        self.cells.append(z)
        self.head += 1
        charge = 2 * self.width
        self.trace.writes += charge
        self.trace.travel += charge
        self.trace.live += charge
        self.trace.high_water = max(self.trace.live, self.trace.high_water)

    def read(self):
        if self.released or self.head == len(self.cells):
            raise ValueError("unexpected tape end")
        z = self.cells[self.head]
        self.head += 1
        self.trace.reads += 2 * self.width
        self.trace.travel += 2 * self.width
        return z

    def read_back(self):
        if self.released or self.head==0:
            raise ValueError("unexpected start of backward tape scan")
        self.head-=1
        self.trace.reads+=2*self.width
        self.trace.travel+=2*self.width
        return self.cells[self.head]

    def pop(self):
        if self.head!=len(self.cells):
            raise ValueError("stack pop requires its end head")
        z=self.read_back()
        self.cells.pop()
        self.trace.writes+=2*self.width
        self.trace.erased+=2*self.width
        self.trace.live-=2*self.width
        return z

    def replace(self, index, z):
        self.seek(index)
        if any(abs(x).bit_length() >= self.width for x in z):
            raise ArithmeticError("signed field overflow")
        self.cells[index] = z
        self.head += 1
        self.trace.writes += 2 * self.width
        self.trace.travel += 2 * self.width

    def release(self):
        if self.released:
            raise ValueError("double release")
        self.home()
        charge = len(self.cells) * 2 * self.width
        self.trace.writes += charge
        self.trace.erased += charge
        self.trace.travel += 2 * charge
        self.trace.live -= charge
        self.cells.clear()
        self.released = True


def tz(x, scale):
    if scale & (scale-1) == 0 and scale > 0:
        value = abs(x) >> (scale.bit_length()-1)
    else:
        value = abs(x) // scale
    return -value if x < 0 else value


def times(a, b, scale, trace):
    x, y = a
    u, v = b
    return (tz(mul(x, u, trace) - mul(y, v, trace), scale),
            tz(mul(x, v, trace) + mul(y, u, trace), scale))


def conj(z):
    return z[0], -z[1]


def neg(z):
    return -z[0], -z[1]


def quarter_root(j, n, bits):
    """Return outward integer enclosures of exp(2*pi*i*j/n) times 2^bits."""
    one = 1 << bits
    if n <= 0 or n & (n-1):
        raise ValueError("power-of-two root order required")
    def root_interval(a, b):
        r = isqrt(a)
        t = isqrt(b)
        return r, t + (t*t < b)
    def negative(pair):
        return -pair[1], -pair[0]
    quarters=[]
    j%=n
    c,s=(one,one),(0,0)
    while j:
        if n==2:
            c=(-one,-one)
            break
        quadrant, k=divmod(j,n//4)
        if not k:
            for _ in range(quadrant):
                c,s=negative(s),c
            break
        quarters.append(quadrant)
        j,n=k,n//2
    for quadrant in reversed(quarters):
        lo,hi=c
        c=root_interval(one*(one+lo)//2,one*(one+hi)//2)
        s=root_interval(one*(one-hi)//2,one*(one-lo)//2)
        for _ in range(quadrant):
            c,s=negative(s),c
    return c, s


def root_word(j, n, f, trace):
    bits = 2*f + 2*n.bit_length() + 16
    while True:
        intervals = quarter_root(j, n, bits)
        unit = 1 << (bits-f)
        result = []
        for lo, hi in intervals:
            x = lo // unit if lo > 0 else -((-hi) // unit) if hi < 0 else 0
            if max(abs(x*unit-lo), abs(hi-x*unit)) > 2*unit:
                break
            result.append(x)
        if len(result) == 2:
            trace.root_enclosures += 1
            return tuple(result)
        bits *= 2


def map_tape(tape, volume, fn, width=None):
    tape.home()
    out = Tape(tape.width if width is None else width, tape.trace)
    for k in range(volume):
        out.append(fn(k, tape.read()))
    tape.release()
    return out


def join(x, y, volume, fn):
    x.home()
    y.home()
    out = Tape(x.width, x.trace)
    for _ in range(volume):
        out.append(fn(x.read(), y.read()))
    x.release()
    y.release()
    return out


def scalar_diagonal(tape, diag, volume, scale, conjugate=False):
    diag.home()
    def apply(_, x):
        z = diag.read()
        return times(x, conj(z) if conjugate else z, scale, tape.trace)
    return map_tape(tape, volume, apply)


def split_add(tape, width, volume, span, divisor):
    """Apply one butterfly between span-separated records; stream every bank."""
    trace = tape.trace
    if span <= 0 or span & (span-1):
        raise ValueError("dyadic butterfly span")
    select = span.bit_length()-1
    pos, minus = Tape(width, trace), Tape(width, trace)
    upper, lower = Tape(width, trace), Tape(width, trace)
    tape.home()
    for i in range(volume):
        (lower if (i>>select)&1 else upper).append(tape.read())
    tape.release()
    upper.home()
    lower.home()
    for _ in range(volume//2):
        a, b = upper.read()
        c, d = lower.read()
        pos.append((tz(a+c, divisor), tz(b+d, divisor)))
        minus.append((tz(a-c, divisor), tz(b-d, divisor)))
    upper.release()
    lower.release()
    out = Tape(width, trace)
    pos.home()
    minus.home()
    for i in range(volume):
        out.append((minus if (i>>select)&1 else pos).read())
    pos.release()
    minus.release()
    trace.h_bits += 1
    return out


def rotate_rings(tape, r, outer, active, local_sizes, sign):
    """Multiply a ring word by Y^e. Every wrapped coefficient changes sign."""
    volume = prod(outer) * r
    out = Tape(tape.width, tape.trace)
    for m in range(volume//r):
        e = 0
        index = m
        for dim, radix in enumerate(outer):
            j, index = index % radix, index // radix
            extent = local_sizes[dim]
            if dim in active and j & (extent//2):
                e += (2*r//extent) * (j % (extent//2))
        e = (sign * e) % (2*r)
        for k in range(r):
            source = (k-e) % r
            tape.seek(m*r + source)
            z = tape.read()
            out.append(neg(z) if ((source+e)//r)%2 else z)
    tape.release()
    return out


def grouped_h(tape, volume, bits, *, backend=None, fractional_bits=None,
              elementary_cap=8):
    """One H0 tensor request on real bit positions in the complete address field."""
    bits = tuple(sorted(bits))
    if not bits:
        return tape
    if (volume <= 0 or volume & (volume-1) or len(tape.cells) != volume
            or len(bits)!=len(set(bits))
            or min(bits)<0 or max(bits)>=volume.bit_length()-1):
        raise ValueError("invalid full-grid Hadamard support or field extent")
    tr=tape.trace
    tr.grouped_requests+=1
    tr.max_support=max(tr.max_support,len(bits))
    if len(bits)>elementary_cap:
        if backend is None:
            from c_dispatch import uniform_h
            backend=uniform_h
        tr.native_requests+=1
        return backend(tape, volume, bits, fractional_bits)
    # At most the fixed number of passes claimed by the elementary branch.
    # Before its final drop there are len(bits) extra possible integer bits.
    last=tape.width
    tape=map_tape(tape,volume,lambda _,z:z,last+len(bits))
    for axis in bits:
        divisor=1<<len(bits) if axis==bits[-1] else 1
        tape=split_add(tape,tape.width,volume,1<<axis,divisor)
    return map_tape(tape,volume,lambda _,z:z,last)


def synthetic_fft(tape, r, outer, inverse=False, *, backend=None,
                  fractional_bits=None, elementary_cap=8):
    """DIF forwards and matched DIT inverse; polynomial spectra stay permuted."""
    volume = r * prod(outer)
    guard = prod(outer).bit_length()-1
    initial_width = tape.width
    tape = map_tape(tape, volume, lambda k,z:(z[0]<<guard,z[1]<<guard),
                    initial_width+guard)
    top = max((n.bit_length()-1 for n in outer), default=0)
    stages = list(range(top))
    if inverse:
        stages.reverse()
    for stage in stages:
        sizes = tuple(t >> stage for t in outer)
        active = tuple(i for i, extent in enumerate(sizes) if extent >= 2)
        if inverse:
            tape = rotate_rings(tape, r, outer, active, sizes, +1)
        positions=tuple((r*prod(outer[:axis])*(sizes[axis]//2)).bit_length()-1
                        for axis in active)
        tape=grouped_h(tape,volume,positions,backend=backend,
                       fractional_bits=None if fractional_bits is None else fractional_bits+guard,
                       elementary_cap=elementary_cap)
        if not inverse:
            tape = rotate_rings(tape, r, outer, active, sizes, -1)
        tape.trace.stages += 1
    return map_tape(tape, volume,
                    lambda k,z:(tz(z[0],1<<guard),tz(z[1],1<<guard)),initial_width)


def pack_ring(tape, start, r, digit):
    """Scan signed coefficients and emit fixed-width limbs with a signed carry."""
    stride = digit//8
    mask = (1 << digit) - 1
    packed = bytearray(), bytearray()
    carries = [0, 0]
    tape.seek(start)
    for _ in range(r):
        for i, component in enumerate(tape.read()):
            total = component + carries[i]
            packed[i].extend((total & mask).to_bytes(stride, "little"))
            carries[i] = total >> digit
    for stream, carry in zip(packed, carries):
        stream.append(carry & 255)
    return tuple(int.from_bytes(value, "little", signed=True) for value in packed)


def signed_limbs(value, count, digit):
    stride = digit//8
    base = 1 << digit
    half = base >> 1
    carry = 0
    data = value.to_bytes(count*stride+1, "little", signed=True)
    for at in range(0, count*stride, stride):
        centered = int.from_bytes(data[at:at+stride], "little") + carry
        carry = int(centered >= half)
        yield centered-base if carry else centered
    if (data[-1] == 255 and carry != 1) or (data[-1] == 0 and carry != 0) or data[-1] not in (0, 255):
        raise ArithmeticError("signed Kronecker unpack overflow")


def ring_products(x, y, r, outer, f):
    """One bounded Kronecker word product for each real product of two rows."""
    M = prod(outer)
    trace = x.trace
    out = Tape(x.width, trace)
    # |c_j| <= 2r*(2^f)^2 for complex inputs in the unit disk.
    digit = 8*((2*f + r.bit_length() + 12)//8)
    divisor = r << f
    for m in range(M):
        a, b = pack_ring(x, m*r, r, digit)
        c, d = pack_ring(y, m*r, r, digit)
        real = mul(a, c, trace) - mul(b, d, trace)
        imag = mul(a, d, trace) + mul(b, c, trace)
        low = Tape(digit+2, trace)
        components = (signed_limbs(value, 2*r, digit) for value in (real, imag))
        for j, (u, v) in enumerate(zip(*components, strict=True)):
            if j < r:
                low.append((u,v))
                if j+1 == r:
                    low.home()
            else:
                u0, v0 = low.read()
                out.append((tz(u0-u,divisor),tz(v0-v,divisor)))
        low.release()
        trace.rings += 1
    x.release()
    y.release()
    return out


def make_diagonals(sources, radices, width, f, trace):
    volume = prod(radices)
    scale = 1 << f
    r = radices[0]
    row = Tape(width, trace)
    starts = []
    for s,t in zip(sources, radices):
        starts.append(len(row.cells))
        for k in range(t):
            row.append(root_word(-s*k*k, 2*t, f, trace))
    # Immutable per-axis phase tables and cached lexicographic prefixes.
    cache = Tape(width,trace)
    for _ in range(len(radices)+1):
        cache.append((scale,0))
    coords = [0]*len(radices)
    a, twists = Tape(width, trace), Tape(width, trace)
    twist_row = Tape(width, trace)
    for k in range(r):
        twist_row.append(root_word(k,2*r,f,trace))
    changed = len(radices)-1
    for m in range(volume):
        for k in reversed(range(changed+1)):
            row.seek(starts[k] + coords[k])
            cache.seek(k+1)
            cache.replace(k,times(cache.read(),row.read(),scale,trace))
            trace.phase_updates += 1
        cache.home()
        a.append(cache.read())
        twist_row.seek(coords[0])
        twists.append(twist_row.read())
        if m+1 < volume:
            changed = 0
            while coords[changed]+1 == radices[changed]:
                coords[changed] = 0
                changed += 1
            coords[changed] += 1
    twist_row.release()
    row.release()
    cache.release()
    return a, twists


def chirp_middle(values, sources, radices, q, *, inverse=False, f=None, trace=None,
                 h_backend=None, elementary_cap=8):
    """Normalized P_t F_t on the q grid; invert the sign by conjugating."""
    sources, radices = tuple(sources), tuple(radices)
    if len(radices)<2 or len(sources)!=len(radices):
        raise ValueError("expected at least two original axes")
    r, outer = radices[0], radices[1:]
    if r<4 or r&(r-1) or any(t not in (r//2,r) for t in outer):
        raise ValueError("dyadic two-scale polynomial geometry required")
    if any(not 0<s<t or not s%2 for s,t in zip(sources,radices)):
        raise ValueError("odd source slope required")
    volume, M = prod(radices), prod(outer)
    if type(q) is not int or q < 2:
        raise ValueError("positive q grid")
    f = max(16, q+M.bit_length()+10) if f is None else f
    if f<max(q,16,M.bit_length()+12):
        raise ValueError("insufficient internal grid")
    trace = Trace() if trace is None else trace
    if trace.live:
        raise ValueError("trace contains live input banks")
    scale = 1<<f
    # Includes temporary exact sums in the elementary simultaneous H interpreter.
    width = f + len(outer) + 4
    source = Tape(width, trace)
    half_sq = 1 << (2*q-2)
    for pair in values:
        a,b=pair
        if mul(a,a,trace)+mul(b,b,trace)>half_sq:
            raise ValueError("half-disk entrance")
        source.append((a<<(f-q), (-b if inverse else b)<<(f-q)))
    if len(source.cells)!=volume:
        raise ValueError("incomplete original-coordinate field")
    phase, twist = make_diagonals(sources,radices,width,f,trace)
    source = scalar_diagonal(source,phase,volume,scale,True)
    phase.home()
    kernel = Tape(width,trace)
    for _ in range(volume):
        kernel.append(phase.read())
    root_args=dict(backend=h_backend,fractional_bits=f,elementary_cap=elementary_cap)
    source = synthetic_fft(scalar_diagonal(source,twist,volume,scale),r,outer,**root_args)
    kernel = synthetic_fft(scalar_diagonal(kernel,twist,volume,scale),r,outer,**root_args)
    product = ring_products(kernel,source,r,outer,f)
    opposite = synthetic_fft(product,r,outer,True,**root_args)
    shift = M.bit_length()-1
    scaled = map_tape(opposite,volume,lambda k,z:(z[0]<<shift,z[1]<<shift))
    cyclic = scalar_diagonal(scaled,twist,volume,scale,True)
    end = scalar_diagonal(cyclic,phase,volume,scale,True)
    end.home()
    output=[]
    for _ in range(volume):
        a,b=end.read()
        output.append((tz(a,1<<(f-q)),tz(-b if inverse else b,1<<(f-q))))
    end.release()
    phase.release()
    twist.release()
    if trace.live:
        raise ArithmeticError("unretired tape")
    return output

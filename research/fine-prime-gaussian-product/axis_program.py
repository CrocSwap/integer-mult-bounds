"""Compile and execute the Gaussian factor on one physical tensor coordinate."""

from contextlib import closing
from dataclasses import dataclass
from fractions import Fraction
from math import prod

from condensed import CyclicBand
from crt_route import Banks, export_field, import_field
from sparse_tapes import correct_field
from fine_ring import Tape, Trace, root_word, split_add, times, tz
from gaussian_pages import admit, build_raw_axis, dyadic_shift, inverse_rational
from gauged_circulants import build_circulant


def require(ok, message):
    if not ok:
        raise ValueError(message)


def grid(x, bits):
    x = Fraction(x)
    return tz(x.numerator << bits, x.denominator)


def row_norm(matrix):
    return max(sum(abs(x) for x in row) for row in matrix)


def bit_reverse(k, width):
    a = 0
    for _ in range(width):
        a = 2*a + k%2
        k //= 2
    return a


@dataclass
class Carve:
    target: int
    flags: tuple

    def boundary(self, i):
        return self.flags[i]

    def boundary_size(self):
        return sum(self.flags)


def convert(values, input_width, output_width, trace, operation):
    with closing(Banks(trace)) as owner:
        source = import_field(values,len(values),input_width,owner)
        out = owner.make(output_width)
        source.home()
        for _ in range(len(values)):
            out.append(operation(source.read()))
        return export_field(out)


def diagonal(values, row, stride, bits, width, trace):
    """Read each diagonal slot once per slower prefix and retain the inner field."""
    unit = 1 << bits
    with closing(Banks(trace)) as owner:
        source = import_field(values,len(values),width,owner)
        page = import_field(row,len(row),width,owner)
        out = owner.make(width)
        source.home()
        for _ in range(len(values) // (len(row)*stride)):
            page.home()
            for _ in range(len(row)):
                coefficient = page.read()
                for _ in range(stride):
                    out.append(times(source.read(),coefficient,unit,trace))
        return export_field(out)


def spectral_table(kernel, bits, trace):
    n = len(kernel)
    levels = n.bit_length()-1
    roots = [root_word(k, n, bits, trace) for k in range(n)]
    out = []
    for j in range(n):
        k = bit_reverse(j, levels)
        out.append(tuple(int(sum(c*roots[(k*h) % n][side] for h,c in enumerate(kernel)))
                         for side in range(2)))
    return out


def local_fft(values, size, stride, bits, component_width, trace, inverse):
    """Perform the short transform directly on the chosen low bits of the axis."""
    n = len(values)
    bank = Tape(component_width, trace)
    for z in values:
        bank.append(z)
    levels = range(size.bit_length()-1)
    if not inverse:
        levels = reversed(levels)
    for level in levels:
        span = 1 << level
        period = 2*span
        factors = [((1 << bits),0)]*span + [
            root_word((1 if inverse else -1)*k, period, bits, trace) for k in range(span)]
        def phase(data):
            out = Tape(component_width, trace)
            data.home()
            page = Tape(component_width,trace)
            for a in factors:
                page.append(a)
            for _ in range(n//(stride*period)):
                page.home()
                for _ in range(period):
                    a = page.read()
                    for _ in range(stride):
                        out.append(times(data.read(),a,1 << bits,trace))
            page.release()
            data.release()
            return out
        if inverse:
            bank = phase(bank)
        bank = split_add(bank, component_width, n, span*stride, 2)
        if not inverse:
            bank = phase(bank)
    bank.home()
    result = [bank.read() for _ in range(n)]
    bank.release()
    return result


@dataclass
class CirclePass:
    side: int
    before: tuple
    eigenvalues: tuple
    after: tuple

    def run(self, data, stride, bits, component_width, trace):
        out = diagonal(data, self.before, stride, bits, component_width, trace)
        out = local_fft(out, self.side, stride, bits, component_width, trace, False)
        out = diagonal(out, self.eigenvalues, stride, bits, component_width, trace)
        out = local_fft(out, self.side, stride, bits, component_width, trace, True)
        # Both FFTs divided by their length. Restore one full local length.
        return diagonal(out, self.after, stride, bits, component_width, trace)


@dataclass
class Factor:
    carve: Carve
    phase: CirclePass
    phase_inverse: CirclePass | None
    residual: object
    condensed: object
    diagonal_scale: tuple
    output_shift: int
    defect: Fraction
    work_bits: int
    component_width: int
    condition_guard: int

    def run(self, data, shape, axis, q, trace):
        """Use axis zero fastest in the outer field."""
        w = self.work_bits
        stride = prod(shape[:axis])
        up = w-q
        values = convert(data,q+3,self.component_width,trace,
                         lambda z:(z[0] << up,z[1] << up))
        if self.phase_inverse is not None:
            values = self.phase_inverse.run(values,stride,w,self.component_width,trace)
        base = self.phase.run(values,stride,w,self.component_width,trace)
        sums, receipt = correct_field(values,base,shape,axis,self.carve,self.residual,
                                      self.condensed,self.component_width,trace)
        if self.phase_inverse is not None:
            sums = self.phase_inverse.run(sums,stride,w,self.component_width,trace)
            sums = diagonal(sums,self.diagonal_scale,stride,w,self.component_width,trace)
        divisor = 1 << (up+self.output_shift)
        return convert(sums,self.component_width,q+3,trace,
                       lambda z:(tz(z[0],divisor),tz(z[1],divisor))), receipt


def assemble_factor(raw, kind, block, coefficient_bits, q, max_defect):
    n, s = raw.t, raw.s
    require(n%block==0, "incomplete dyadic cell")
    w_band = raw.width
    is_inverse = kind == "narrow"
    true_reference = raw.narrow if is_inverse else raw.broad
    error = raw.narrow_error if is_inverse else raw.broad_error
    d_error = raw.diagonal_error if is_inverse else 0
    real_d = raw.diagonal if is_inverse else (Fraction(1),)*n
    chosen = set(raw.positions)
    flags = []
    J = [[Fraction(0)]*n for _ in range(n)]
    parts = []
    for start in range(0,n,block):
        pure = all(i in chosen for i in range(start,start+block))
        flags.extend(not pure or i<w_band or block-1-i<w_band for i in range(block))
        if pure:
            page = build_circulant(s,n,raw.alpha,start,block,w_band,
                                   coefficient_bits,kind)
            z = 1 << coefficient_bits
            u = tuple(Fraction(x,z) for x in page.row)
            v = tuple(Fraction(x,z) for x in page.column)
            kernel = tuple(Fraction(x,z) for x in page.weights)
            kernel_inv = page.inverse_weights if is_inverse else ()
        else:
            u = v = (Fraction(1),)*block
            kernel = (Fraction(1),)+(Fraction(0),)*(block-1)
            kernel_inv = kernel if is_inverse else ()
        parts.append((u,kernel,v,kernel_inv))
        for i in range(block):
            for j in range(block):
                J[start+i][start+j] = u[i]*kernel[(j-i)%block]*v[j]
    E = [i for i in range(n) if flags[i]]
    Q = [[true_reference[i][j] if flags[i] and flags[j] else J[i][j]
          for j in range(n)] for i in range(n)]
    q_err = error + max(sum(abs(x-y) for x,y in zip(a,b))
                        for a,b in zip(Q,true_reference))
    carve = Carve(n, tuple(flags))
    residual = [[Q[i][j]-J[i][j] for j in E] for i in E]
    # The cyclic band is measured after the nonboundary coordinates are removed.
    width = min(4*w_band+2, len(E)//2)
    band = CyclicBand.from_rows((enumerate(row) for row in residual),width)
    f_band = None
    if is_inverse:
        q_inv = inverse_rational(Q)
        q_inv_norm = row_norm(q_inv)
        admit(q_err*q_inv_norm < 1, "inverse perturbation fails")
        inverse_true = q_inv_norm/(1-q_err*q_inv_norm)
        defect = d_error*inverse_true + max(abs(x) for x in real_d)*q_inv_norm*q_err*inverse_true
        effective_norm = max(abs(d)*sum(abs(x) for x in row)
                             for d,row in zip(real_d,q_inv))
        conditional = [[q_inv[i][j] for j in E] for i in E]
        f = inverse_rational(conditional)
        f_band = CyclicBand.from_rows((enumerate(row) for row in f),width)
        gap = min(abs(row[i])-sum(abs(x) for j,x in enumerate(row) if i!=j)
                  for i,row in enumerate(Q))
        admit(gap>0, "narrow reference loses strict row dominance")
        solver_norm = max(row_norm(f), q_inv_norm, 1/gap)
    else:
        defect = q_err
        effective_norm = row_norm(Q)
        solver_norm = Fraction(1)
    out_shift = dyadic_shift(max(Fraction(1),effective_norm+defect))
    normalized_defect = defect/(1 << out_shift)
    admit(normalized_defect < max_defect, "Gaussian page error exceeds its budget")
    # All factors other than the two normalized short FFTs are real. Bound their
    # norms before choosing the common grid, including the true inverse kernel.
    max_gain = max(Fraction(2),n,solver_norm,row_norm(residual),max(real_d))
    for u,k,v,ki in parts:
        max_gain = max(max_gain,max(u),max(v),sum(map(abs,k)))
        if is_inverse:
            max_gain = max(max_gain,1/min(u),1/min(v),sum(map(abs,ki)))
    guard = dyadic_shift(max_gain+2)
    work_bits = q+80*guard+32
    trace = Trace()
    def circle(inv):
        pre, spec, post = [], [], []
        for u,k,v,ki in parts:
            before = [1/x for x in u] if inv else v
            after = [1/x for x in v] if inv else u
            pre.extend((grid(x,work_bits),0) for x in before)
            spec.extend(spectral_table(ki if inv else k,work_bits,trace))
            post.extend((grid(block*x,work_bits),0) for x in after)
        return CirclePass(block,tuple(pre),tuple(spec),tuple(post))
    return Factor(carve,circle(False),circle(True) if is_inverse else None,
                  band.apply_page(work_bits),f_band.factor(work_bits) if is_inverse else None,
                  tuple((grid(d,work_bits),0) for d in real_d),out_shift,normalized_defect,
                  work_bits,work_bits+40*guard+16,guard)


def make_axis(s,t,alpha,block,width,q,*,max_defect=None):
    if max_defect is None:
        max_defect = Fraction(1,1 << (q+3))
    precision = 2*q + 128 + 4*t.bit_length()
    raw = build_raw_axis(s,t,alpha,width,precision)
    broad = assemble_factor(raw,"broad",block,precision,q,max_defect)
    narrow = assemble_factor(raw,"narrow",block,precision,q,max_defect)
    return raw.positions,broad,narrow

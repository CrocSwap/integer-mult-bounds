"""Check the dirty stride construction with exact arithmetic."""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
from fractions import Fraction as F

HERE = Path(__file__).resolve().parent
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


d = load(HERE/'dirty_stride.py', 'dirty_stride')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def pins():
    source = json.loads((HERE/'SOURCE.json').read_text())
    for row in source['sources']:
        data = (HERE/row['local']).read_bytes()
        d.need(hashlib.sha256(data).hexdigest() == row['sha256'], 'source SHA256: '+row['local'])
        blob = b'blob '+str(len(data)).encode()+b'\0'+data
        d.need(hashlib.sha1(blob).hexdigest() == row['blob'], 'source Git blob: '+row['local'])
    return len(source['sources'])


class Bank:
    """Allow indexed reads and writes. Refuse iteration and array copies."""
    def __init__(self, values):
        self.values = list(values)
        self.peak_l1 = max(abs(a)+abs(b) for a, b in self.values)

    def __len__(self):
        return len(self.values)

    def __getitem__(self, index):
        if type(index) is not int:
            raise ValueError('data slice is not allowed')
        return self.values[index]

    def __setitem__(self, index, value):
        if type(index) is not int:
            raise ValueError('data slice is not allowed')
        self.values[index] = value
        self.peak_l1 = max(self.peak_l1, abs(value[0])+abs(value[1]))

    def __iter__(self):
        raise ValueError('data iteration is not allowed')


def values(length, bits, salt):
    scale = 1 << bits
    return [(F(2*((5*i+salt) % 13)-11, 8)+F(1, scale),
             F(2*((7*i+salt) % 11)-9, 16)+F(1, scale)) for i in range(length)]


def magnitude(arrays):
    return max(abs(a)+abs(b) for array in arrays for a, b in array)


def digest_arrays(arrays):
    data = [[[str(a), str(b)] for a, b in array] for array in arrays]
    return hashlib.sha256(canonical(data).encode()).hexdigest()


def cycle_oracle(source, coefficient, stride):
    """Sum the finite geometric inverse. Do not use the recursive solver."""
    n = len(source)
    count = n//math.gcd(n, stride)
    ar, ai = coefficient
    result = []
    for i in range(n):
        sr = si = F(0)
        wr, wi = F(1), F(0)
        for k in range(count):
            xr, xi = source[(i-k*stride) % n]
            sr, si = sr+wr*xr-wi*xi, si+wr*xi+wi*xr
            wr, wi = wr*ar-wi*ai, wr*ai+wi*ar
        rr, ri = 1-wr, -wi
        den = rr*rr+ri*ri
        result.append(((sr*rr+si*ri)/den, (si*rr-sr*ri)/den))
    return result


def geometry_check(limit=128):
    cases = levels = 0
    for length in range(1, limit+1):
        for stride in range(length):
            divisor = math.gcd(length, stride)
            cycle = length//divisor
            inv = pow(stride//divisor, -1, cycle) if cycle > 1 else 0
            geo = d.Geometry(d.ZERO, divisor, cycle, inv, 64, d.Meter())
            weights = [1]*length
            w, orientation = stride, 1
            while True:
                n = len(weights)
                w %= n
                if 2*w > n:
                    weights.reverse()
                    w, orientation = n-w, -orientation
                a, b = geo.exponents(n, w, orientation)
                d.need(weights == [b if i < w else a for i in range(n)], 'return-time geometry')
                levels += 1
                if w == 0:
                    break
                weights = [sum(weights[j] for j in range(i % w, i+1, w))
                           for i in range(n-w, n)]
                w = (-n) % w
            cases += 1
    return dict(lengths=[1, limit], cases=cases, levels=levels)


def power_check():
    cases = nonzero = 0
    for beta in (F(1, 2), F(1, 16), F(1, 4096)):
        for phase in (d.ONE, (F(3, 5), F(4, 5)), (F(-5, 13), F(12, 13))):
            root = tuple((1-beta)*v for v in phase)
            for bits in (16, 64):
                exact = d.ONE
                for exponent in range(1, 130):
                    exact = d.mul(exact, root)
                    result = d.power(root, exponent, bits, d.Meter())
                    d.need(d.norm2(result) <= d.norm2(exact), 'power does not increase the norm')
                    error = d.norm2(d.sub(result, exact))
                    d.need(error <= (8*F(1, 1 << bits)/beta)**2, 'uniform power error')
                    nonzero += error != 0
                    cases += 1
    return dict(cases=cases, nonzero_errors=nonzero, maximum_exponent=129)


def generic_check(limit=24):
    cases = nonzero = 0
    receipt = hashlib.sha256()
    worst = F(0)
    for beta in (F(1, 2), F(1, 16), F(1, 4096)):
        bits = 32+6*d.ceil_log2(1/beta)
        b = ((1-beta)*F(3, 5), (1-beta)*F(4, 5))
        for length in range(1, limit+1):
            for stride in range(-length, length):
                x0, y0 = values(length, bits, 36), values(length, bits, 71)
                exact = cycle_oracle(x0, b, stride)
                for shift in sorted({0, stride % length}):
                    x, y = Bank(x0), Bank(y0)
                    meter = d.lift(x, y, b, beta, bits, stride, shift=shift)
                    d.need(x.values == x0, 'source restoration')
                    error = max(d.norm2(d.sub(d.sub(y.values[i], y0[i]), exact[(i-shift) % length]))
                                for i in range(length))
                    bound = d.leaf_bound(magnitude([x0]), beta, bits)
                    d.need(error <= bound*bound, 'leaf error')
                    worst = max(worst, error/(bound*bound))
                    nonzero += error != 0
                    receipt.update(digest_arrays([y.values]).encode())
                    d.lift(x, y, b, beta, bits, stride, -1, shift=shift)
                    d.need(x.values == x0 and y.values == y0, 'leaf inverse')
                    d.need(meter.max_depth == d.depth(length, stride), 'observed recursion depth')
                    d.need(meter.tape_moves <= 4096*length, 'shifted leaf tape bound')
                    cases += 1
    return dict(lengths=[1, limit], strides='every integer in [-L,L)', cases=cases,
                output_shifts='zero and stride modulo L; duplicates removed',
                nonzero_errors=nonzero, max_squared_error_ratio_log2_upper=d.ceil_log2(worst),
                output_digest=receipt.hexdigest())


def cost_check():
    rows = []
    for length in (1, 2, 5, 12, 29, 70, 169, 408, 985, 2378):
        for stride in sorted({0, 1 % length, length//3, length//2, (length*36)//100,
                              math.isqrt(2*length*length)-length,
                              min(length-1, math.isqrt(2*length*length)-length+1)}):
            n, w, weight, mass, nodes = length, stride, 1, 0, 0
            while True:
                w %= n
                w = min(w, n-w)
                mass += weight*n
                nodes += weight
                if w == 0:
                    break
                n, w, weight = w, (-n) % w, weight*2
            d.need(mass <= 6*length, 'Euclidean recurrence mass')
            x, y = Bank([d.ZERO]*length), Bank([d.ONE]*length)
            meter = d.lift(x, y, d.ZERO, F(1, 2), 64, stride)
            calls = meter.products+meter.power_products+meter.divisions
            bound = 9*mass+32*nodes*(length//math.gcd(length, stride)).bit_length()+3*length
            d.need(meter.nodes == nodes and calls <= bound, 'complete arithmetic bill')
            d.need(calls <= 1280*length and meter.reads+meter.writes <= 512*length,
                   'linear arithmetic and indexed access bound')
            d.need(meter.tape_moves <= 4096*length and set(meter.heads) == {0, 1}
                   and all(v == 0 for v in meter.heads.values()), 'linear two-tape bound and head returns')
            d.need(x.values == [d.ZERO]*length and y.values == [d.ONE]*length, 'count fixture restoration')
            rows.append(dict(length=length, stride=stride, nodes=nodes, weighted_length=mass,
                             scalar_products=meter.products, power_products=meter.power_products,
                             divisions=meter.divisions, reads=meter.reads, writes=meter.writes,
                             two_tape_record_moves=meter.tape_moves, arithmetic_bound=bound))
    return rows


def kernel_check():
    c = load(HERE/'vendor/pr628/check.py', 'source628_check')
    fixtures = json.loads((HERE/'vendor/pr628/FACTORS.json').read_text())
    rows = []
    for fixture in fixtures:
        state = c.certify(fixture)
        factors = [(inside, b, F(state['radix']) if i == 0 else F(1))
                   for i, (inside, b) in enumerate(state['factors'])]
        beta, r = state['beta'], state['radix']
        perturbation = F(state['certificate']['factorization_inverse_error_bound'])
        for length, stride in ((1, 0), (3, 1), (5, 2), (5, -2)):
            for tau in (d.ONE, (F(3, 5), F(4, 5))):
                bits = d.working_bits(len(factors), r, beta, 4, 128, 16, length, stride)
                originals = [values(length, bits, 36+7*j)
                             for j in range(2+(len(factors)-1).bit_length())]
                bound0 = magnitude(originals)
                d.need(bound0 <= 4, 'initial magnitude')
                d.need(all((a*(1 << bits)).numerator % 2 and (b*(1 << bits)).numerator % 2
                           for array in originals for a, b in array), 'odd lowest input bits')
                banks = [Bank(v) for v in originals]
                meter = d.compose(banks[0], banks[1], factors, banks[2:], tau, beta, bits, stride)
                d.need(banks[0].values == originals[0] and
                       [a.values for a in banks[2:]] == originals[2:], 'kernel dirty restoration')
                net = [d.sub(a, old) for a, old in zip(banks[1].values, originals[1])]
                exact = c.matrix_solve(originals[0], c.phased_polynomial(state['q'], tau), stride)
                error = max(d.norm2(d.sub(a, b)) for a, b in zip(net, exact))
                execution = d.execution_bound(len(factors), r, beta, bound0, bits)
                d.need(error <= execution**2, 'independent dense kernel error')
                d.need(execution+perturbation*magnitude([originals[0]]) <= F(1, 1 << 128), 'true kernel target')
                d.need(meter.leaves == d.leaf_calls(len(factors)), 'paid leaf count')
                tape_bound = 8192*(meter.leaves+1)*len(banks)*length
                d.need(meter.tape_moves <= tape_bound and set(meter.heads) == {0, 1}
                       and all(v == 0 for v in meter.heads.values()), 'kernel two-tape routing')
                space_bound = 512*(r+1)*(bound0+1)*(2+F(r)/beta)**meter.leaves/beta**7
                peak = max(bank.peak_l1 for bank in banks)
                d.need(peak <= space_bound, 'complete integer magnitude allowance')
                output_digest = digest_arrays([b.values for b in banks])
                d.compose(banks[0], banks[1], factors, banks[2:], tau, beta, bits, stride, -1)
                d.need([b.values for b in banks] == originals, 'full word inverse')
                rows.append(dict(radix=r, embedding=state['embedding'], length=length,
                                 stride=stride, gauge=[str(v) for v in tau], bits=bits,
                                 leaf_calls=meter.leaves, borrowed_arrays=len(banks)-2,
                                 two_tape_record_moves=meter.tape_moves, tape_bound=tape_bound,
                                 peak_l1_log2_upper=d.ceil_log2(peak),
                                 nonzero_error=error != 0, error_squared_log2_upper=d.ceil_log2(error) if error else None,
                                 execution_bound=str(execution), output_digest=output_digest))
        print('checked kernel', r, fixture['embedding'], flush=True)
    return rows


def controls():
    rows = []
    def reject(name, fn):
        try:
            fn()
        except ValueError as exc:
            rows.append(dict(name=name, reason=str(exc)))
        else:
            raise ValueError('control accepted: '+name)
    x, y = Bank([d.ONE, d.ZERO]), Bank([d.ZERO, d.ONE])
    reject('source_target_alias', lambda: d.lift(x, x, d.ZERO, F(1, 2), 64, 1))
    reject('insufficient_precision', lambda: d.lift(x, y, d.ZERO, F(1, 16), 8, 1))
    reject('unit_coefficient', lambda: d.lift(x, y, d.ONE, F(1, 2), 64, 1))
    reject('off_grid_source', lambda: d.lift(Bank([(F(1, 3), F(0)), d.ZERO]), y,
                                            d.ZERO, F(1, 2), 64, 1))
    factors = [(True, (F(1, 4), F(0)), F(1))]*2
    reject('ancestor_target_as_scratch', lambda: d.compose(x, y, factors, [y], d.ONE, F(1, 2), 64, 1))
    reject('missing_dirty_level', lambda: d.compose(x, y, factors, [], d.ONE, F(1, 2), 64, 1))
    reject('nonunit_gauge', lambda: d.compose(x, y, factors, [Bank([d.ONE]*2)],
                                             (F(2), F(0)), F(1, 2), 64, 1))
    scratch = Bank([d.ONE]*2)
    before = [x.values[:], y.values[:], scratch.values[:]]
    reject('late_unstable_factor', lambda: d.compose(x, y, [factors[0], (True, d.ONE, F(1))],
                                                      [scratch], d.ONE, F(1, 2), 64, 1))
    d.need([x.values, y.values, scratch.values] == before, 'preflight must precede mutation')
    reject('fractional_stride', lambda: d.lift(x, y, d.ZERO, F(1, 2), 64, F(1, 2)))
    bad_meter = d.Meter(layout={id(x): (0, 0), id(y): (0, 2)})
    reject('same_tape_operands', lambda: d.lift(x, y, d.ZERO, F(1, 2), 64, 1, meter=bad_meter))
    reject('unsupported_shift', lambda: d.lift(Bank([d.ZERO]*3), Bank([d.ONE]*3),
                                              d.ZERO, F(1, 2), 64, 1, shift=2))
    increments = []
    for salt in (1, 2):
        x0, y0 = values(3, 48, 36), values(3, 48, salt)
        src, dst = Bank(x0), Bank(y0)
        d.lift(src, dst, (F(3, 10), F(2, 5)), F(1, 2), 48, 1)
        increments.append([d.sub(a, b) for a, b in zip(dst.values, y0)])
    d.need(increments[0] != increments[1], 'target dependence witness')
    rows.append(dict(name='target_dependence', reason='L=3, stride=1, W=48',
                     changed_entries=sum(a != b for a, b in zip(*increments))))
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', type=Path, help='Write a new exact receipt to this absent path.')
    args = parser.parse_args()
    if args.write:
        d.need(not args.write.exists(), 'output already exists')
    result = dict(status='passed', pins=pins(), geometry=geometry_check(), power=power_check(),
                  generic=generic_check(), costs=cost_check(), kernels=kernel_check(), controls=controls())
    text = json.dumps(result, indent=2, sort_keys=True)+'\n'
    if args.write:
        with args.write.open('x') as out:
            out.write(text)
    else:
        expected = json.loads((HERE/'EXPECTED.json').read_text())
        d.need(canonical(result) == canonical(expected), 'exact receipt mismatch')
    print('PASS_DIRTY_STRIDE_SOURCE_REUSE geometry=%d generic=%d kernels=%d controls=%d' %
          (result['geometry']['cases'], result['generic']['cases'], len(result['kernels']), len(result['controls'])))


if __name__ == '__main__':
    main()

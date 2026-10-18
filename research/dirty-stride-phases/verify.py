"""Check the phased dirty operator against independent rational intervals."""
import argparse
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


c = load(HERE/'chirp.py', 'checked_chirp')
o = load(HERE/'oracle.py', 'phase_oracle')


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


class Bus:
    def __init__(self):
        self.heads = {0: 0, 1: 0}
        self.minimum_moves = 0
        self.reads = self.writes = 0

    def access(self, tape, position, write):
        self.minimum_moves += abs(position-self.heads[tape])+1
        self.heads[tape] = position
        if write:
            self.writes += 1
        else:
            self.reads += 1


class Bank:
    """Refuse data copies and slices. Measure the largest stored value."""
    def __init__(self, values, bus=None, tape=0, offset=0):
        self.bus, self.tape, self.offset = bus, tape, offset
        self.values = list(values)
        self.peak = max(abs(a)+abs(b) for a, b in self.values)

    def __len__(self):
        return len(self.values)

    def __getitem__(self, index):
        need(type(index) is int, 'array slices are not allowed')
        if self.bus is not None:
            self.bus.access(self.tape, self.offset+index, False)
        return self.values[index]

    def __setitem__(self, index, value):
        need(type(index) is int, 'array slices are not allowed')
        if self.bus is not None:
            self.bus.access(self.tape, self.offset+index, True)
        self.values[index] = value
        self.peak = max(self.peak, abs(value[0])+abs(value[1]))

    def __iter__(self):
        raise ValueError('array copies are not allowed')


def data(length, bits, salt=0, dirt=0):
    unit = F(1, 1 << bits)
    return [(F((7*i+salt) % 19-9, 8)+dirt+unit,
             F((11*i+salt) % 17-8, 16)-dirt+3*unit) for i in range(length)]


def digest(arrays):
    return hashlib.sha256(canonical([[[str(a), str(b)] for a, b in array] for array in arrays]).encode()).hexdigest()


def pins():
    sources = json.loads((HERE/'SOURCE.json').read_text())
    for row in sources['sources']:
        value = (HERE/row['local']).read_bytes()
        need(hashlib.sha256(value).hexdigest() == row['sha256'], 'source SHA256: '+row['local'])
        need(hashlib.sha1(b'blob '+str(len(value)).encode()+b'\0'+value).hexdigest()
             == row['blob'], 'source Git blob: '+row['local'])
    return len(sources['sources'])


def check_phase_case(module, modulus, residue, bits, value):
    meter = module.Meter()
    plan = module.Phase.prepare(1, modulus, bits, meter)
    coefficients = plan.coefficients(residue)
    quadrant, tangent, sine = coefficients
    ideal = o.phase(residue, modulus, 1, bits+96)
    real, imag = ideal
    reduced = ((real, imag), (imag, o.neg(real)),
               (o.neg(real), o.neg(imag)), (o.neg(imag), real))[quadrant]
    need(reduced[0][0] >= F(1, 2), 'phase quadrant')
    denominator = o.plus(o.point(1), reduced[0], bits+96)
    ratio = [v/w for v in reduced[1] for w in denominator]
    tangent_error = max(abs(tangent-min(ratio)), abs(tangent-max(ratio)))
    sine_error = max(abs(sine-reduced[1][0]), abs(sine-reduced[1][1]))
    need(tangent_error <= F(1, 1 << (bits+8)) and sine_error <= F(1, 1 << (bits+8)),
         'phase coefficient accuracy')
    rotated = module.rotate(value, coefficients, bits)
    exact = o.complex_mul(ideal, o.complex_point(value), bits+96)
    bound = 4*(abs(value[0])+abs(value[1])+1)*F(1, 1 << bits)
    need(o.squared_distance_bound(rotated, exact) <= bound*bound, 'rotation accuracy')
    need(module.rotate(rotated, coefficients, bits, True) == value, 'rotation exact inverse')
    inverse_rotated = module.rotate(value, coefficients, bits, True)
    exact_inverse = o.complex_mul((ideal[0], o.neg(ideal[1])), o.complex_point(value), bits+96)
    need(o.squared_distance_bound(inverse_rotated, exact_inverse) <= bound*bound, 'inverse rotation accuracy')
    need(module.rotate(inverse_rotated, coefficients, bits) == value, 'rotation reverse cancellation')
    return digest([[rotated, inverse_rotated]])


def phase_check(module=c):
    cases = 0
    result = hashlib.sha256()
    for bits in (2, 17, 64):
        unit = F(1, 1 << bits)
        for modulus in range(1, 25):
            for residue in range(modulus):
                value = (F(17, 4)+unit, -F(33, 8)+3*unit)
                if residue % 3 == 1:
                    value = (2**60+unit, -2**48+3*unit)
                result.update(check_phase_case(module, modulus, residue, bits, value).encode())
                cases += 1
    for modulus in (2**80, 2**80+7):
        for residue in (1, modulus//8, modulus//4-1, modulus//2+1, modulus-1):
            result.update(check_phase_case(module, modulus, residue, 96, (F(1, 8), F(-11, 16))).encode())
            cases += 1
    return dict(cases=cases, small_moduli=[1, 24], coefficient_bits=[10, 25, 72, 104],
                wide_modulus_bits=81, output_digest=result.hexdigest())


def check_leaf_case(module, length, stride, numerator, modulus, dirt=0, shift=0,
                    sign=1, beta=F(1, 4), target_bits=32):
    multiplier = (F(3, 5), F(-4, 5))
    bits = module.working_bits(target_bits, 4, 2*abs(dirt)+8, beta, length, stride,
                               multiplier_bound=F(7, 5))
    x0 = data(length, bits, 2)
    y0 = data(length, bits, 9, dirt)
    bus = Bus()
    x, y = Bank(x0, bus, 0), Bank(y0, bus, 1)
    result = module.lift(x, y, (F(3, 10), F(2, 5)), beta, bits, stride, numerator, modulus,
                         sign, multiplier, shift)
    need(x.values == x0, 'leaf source restoration')
    need(result.reads == bus.reads and result.writes == bus.writes, 'paid data accesses')
    need(result.tape_moves >= bus.minimum_moves, 'minimum physical tape movement')
    need(result.phase_passes == 4 and result.phase_evaluations == 4*length
         and result.phase_recurrence_steps == 4*length, 'four complete phase passes')
    need(result.input_reads == 2*length, 'paid input scan')
    need(result.tape_moves <= 4160*length and result.phase_record_moves <= 16*length,
         'phased leaf tape bill')
    need(all(position == 0 for position in result.heads.values())
         and set(result.heads) == {0, 1}, 'two returned data heads')
    need(result.phase_terms <= 2*result.internal_bits*(4*length+1)
         and result.phase_products <= 4*result.internal_bits*(4*length+1)
         and result.phase_divisions <= 2*result.internal_bits*(4*length+1), 'phase arithmetic bill')
    need(result.error_bound <= F(1, 1 << (target_bits+1)), 'leaf precision choice')
    ideal = o.leaf(x0, (F(3, 10), F(2, 5)), stride, numerator, modulus, bits+96,
                   multiplier, shift)
    error = F(0)
    nonzero = False
    for i in range(length):
        increment = (sign*(y.values[i][0]-y0[i][0]), sign*(y.values[i][1]-y0[i][1]))
        error = max(error, o.squared_distance_bound(increment, ideal[i]))
        nonzero |= not (ideal[i][0][0] <= increment[0] <= ideal[i][0][1]
                        and ideal[i][1][0] <= increment[1] <= ideal[i][1][1])
    need(error <= result.error_bound**2, 'phased leaf accuracy')
    integer_bound = 16384*(F(7, 5)+1)*(result.initial_bound+1)/beta**7
    need(max(x.peak, y.peak, result.phase_peak_l1) <= 2*integer_bound, 'leaf integer reserve')
    output = digest([y.values])
    module.lift(x, y, (F(3, 10), F(2, 5)), beta, bits, stride, numerator, modulus,
                -sign, multiplier, shift)
    need(x.values == x0 and y.values == y0, 'leaf complete-word inverse')
    return dict(output=output, nonzero=nonzero, ratio=error/result.error_bound**2,
                bits=bits, phase_terms=result.phase_terms, tape_moves=result.tape_moves)


def leaf_check(module=c):
    count = nonzero = 0
    worst = F(0)
    width = 0
    output = hashlib.sha256()
    for length in range(1, 13):
        for stride in sorted({0, 1, length//2, length-1, -1, -length//2}):
            for numerator, modulus in ((-3, 2*length), (5, 2*length+1)):
                for dirt in (0, 2**40):
                    shift = stride if dirt else 0
                    result = check_leaf_case(module, length, stride, numerator, modulus,
                                              dirt, shift, -1 if stride < 0 else 1)
                    count += 1
                    nonzero += result['nonzero']
                    worst = max(worst, result['ratio'])
                    width = max(width, result['bits'])
                    output.update(result['output'].encode())
    for length, stride, numerator, modulus in ((17, 7, -3, 34), (29, 12, -5, 58),
                                                (11, -7, 2**96+9, 2**80+7)):
        result = check_leaf_case(module, length, stride, numerator, modulus, 2**80, stride,
                                 beta=F(1, 32), target_bits=64)
        count += 1
        nonzero += result['nonzero']
        worst = max(worst, result['ratio'])
        width = max(width, result['bits'])
        output.update(result['output'].encode())
    need(nonzero == count, 'nonzero rounded leaf errors')
    return dict(cases=count, nonzero_errors=nonzero, maximum_bits=width,
                max_squared_error_ratio_log2_upper=c.d.ceil_log2(worst), output_digest=output.hexdigest())


def check_kernel_case(module, count, length, stride, dirt=0):
    beta = F(1, 4)
    factors = [(i % 2 == 0, (F(1, 4), F((-1)**i, 8)), F(3 if i == 0 else 1)) for i in range(count)]
    numerator, modulus = -3, 2*length
    tau = F(3, 5), F(4, 5)
    bits = module.working_bits(48, 4, 2*abs(dirt)+16, beta, length, stride, count=count, scale_bound=3)
    x0, y0 = data(length, bits, 2), data(length, bits, 8, dirt)
    scratch0 = [data(length, bits, 15+j, (-1)**j*dirt) for j in range((count-1).bit_length())]
    bus = Bus()
    originals = [x0, y0]+scratch0
    banks = [Bank(a, bus, 1 if i == len(originals)-1 else 0,
                  0 if i == len(originals)-1 else i*length) for i, a in enumerate(originals)]
    x, y, scratch = banks[0], banks[1], banks[2:]
    result = module.compose(x, y, factors, scratch, tau, beta, bits, stride, numerator, modulus)
    need(x.values == x0 and [a.values for a in scratch] == scratch0, 'kernel source and scratch restoration')
    need(result.reads == bus.reads and result.writes == bus.writes, 'kernel paid data accesses')
    need(result.tape_moves >= bus.minimum_moves, 'kernel minimum physical tape movement')
    calls = c.d.leaf_calls(count)
    need(result.leaves == calls, 'complete factor word')
    need(result.phase_passes == 4 and result.phase_evaluations == 4*length,
         'four phase passes around the complete kernel')
    need(set(result.heads) == {0, 1} and all(p == 0 for p in result.heads.values()), 'kernel data heads')
    need(result.tape_moves <= 8256*(calls+1)*(len(scratch)+2)*length, 'kernel tape bill')
    need(result.phase_terms <= 2*result.internal_bits*(4*length+1), 'kernel phase generation bill')
    need(result.error_bound <= F(1, 1 << 49), 'kernel precision choice')
    integer_bound = 16384*4*(result.initial_bound+1)*14**calls/beta**7
    need(max(result.phase_peak_l1, *(bank.peak for bank in banks)) <= 2*integer_bound,
         'kernel integer reserve including phase transients')
    exact = o.kernel(x0, factors, tau, stride, numerator, modulus, bits+96)
    error = max(o.squared_distance_bound((y.values[i][0]-y0[i][0], y.values[i][1]-y0[i][1]), exact[i])
                for i in range(length))
    need(error <= result.error_bound**2, 'phased kernel accuracy')
    output = digest([y.values])
    module.compose(x, y, factors, scratch, tau, beta, bits, stride, numerator, modulus, -1)
    need(x.values == x0 and y.values == y0 and [a.values for a in scratch] == scratch0,
         'kernel complete-word inverse')
    return dict(count=count, length=length, stride=stride, dirt=str(dirt), bits=bits,
                calls=calls, tape_moves=result.tape_moves, phase_terms=result.phase_terms,
                output_digest=output)


def kernel_check(module=c):
    return [check_kernel_case(module, count, length, stride, dirt)
            for count in (1, 2, 3, 5, 8)
            for length, stride, dirt in ((1, 0, 7), (5, 2, -13), (8, -3, 2**40), (17, 7, 2**80))]


def cost_check(module=c):
    rows = []
    for length, stride in ((70, 29), (169, 70), (408, 169), (985, 408)):
        bits = 48
        x0, y0 = data(length, bits, 4), data(length, bits, 15)
        bus = Bus()
        x, y = Bank(x0, bus, 0), Bank(y0, bus, 1)
        result = module.lift(x, y, (F(0), F(0)), F(1, 2), bits, stride, -3, 2*length)
        need(x.values == x0, 'large leaf source restoration')
        need(result.reads == bus.reads and result.writes == bus.writes, 'large paid data accesses')
        need(result.tape_moves >= bus.minimum_moves, 'large minimum physical tape movement')
        need(result.tape_moves <= 4160*length, 'large leaf tape bound')
        need(result.phase_evaluations == 4*length and result.phase_passes == 4, 'large leaf phase access')
        module.lift(x, y, (F(0), F(0)), F(1, 2), bits, stride, -3, 2*length, -1)
        need(x.values == x0 and y.values == y0, 'large leaf exact inverse')
        rows.append(dict(length=length, stride=stride, tape_moves=result.tape_moves,
                         phase_terms=result.phase_terms, phase_peak_l1_log2_upper=c.d.ceil_log2(result.phase_peak_l1),
                         products=result.phase_products,
                         divisions=result.phase_divisions, recursion_depth=result.max_depth))
    return rows


def controls(module=c):
    cases = []
    def rejected(name, call, arrays, original):
        try:
            call()
        except ValueError as error:
            expected = dict(zero_modulus='integer phase descriptor', boolean_numerator='integer phase descriptor',
                            aliased_arrays='distinct arrays', insufficient_precision='conjugation precision admission',
                            unstable_coefficient='stable coefficient', unsupported_shift='supported output shift',
                            invalid_sign='integer stride and sign', float_coefficient='stable coefficient')
            need(str(error) == expected[name], 'wrong rejection: '+name+'; '+str(error))
            need(arrays == original, 'rejection changed data: '+name)
            cases.append(name)
        else:
            raise ValueError('accepted invalid input: '+name)
    x, y = data(5, 80), data(5, 80, 7)
    original = [x[:], y[:]]
    defaults = dict(x=x, y=y, b=(F(1, 4), F(0)), beta=F(1, 4), bits=80, stride=2,
                    numerator=-3, modulus=10)
    for name, patch in (('zero_modulus', {'modulus':0}), ('boolean_numerator', {'numerator':True}),
                         ('aliased_arrays', {'y':x}),
                         ('unstable_coefficient', {'b':(F(1), F(0))}), ('unsupported_shift', {'shift':1}),
                         ('invalid_sign', {'sign':0}), ('float_coefficient', {'b':(0.25,0.0)})):
        args = defaults | patch
        rejected(name, lambda args=args: module.lift(**args), [x, y], original)
    coarse_x = [(F(1), F(0))]*5
    coarse_y = [(F(2), F(0))]*5
    rejected('insufficient_precision', lambda: module.lift(coarse_x, coarse_y, (F(1, 4), F(0)),
             F(1, 4), 14, 2, -3, 10), [coarse_x, coarse_y], [coarse_x[:], coarse_y[:]])
    # A unit source has a nonconstant response under the retained length-eight chirp.
    source = [(F(i == 0), F(0)) for i in range(8)]
    phased = o.leaf(source, (F(1, 2), F(0)), 3, -3, 16, 160)
    plain = o.leaf(source, (F(1, 2), F(0)), 3, 0, 16, 160)
    separation = max(max(F(0), phased[i][0][0]-plain[i][0][1],
                         plain[i][0][0]-phased[i][0][1]) for i in range(8))
    need(separation > F(1, 8), 'nonconstant phase witness')
    return dict(rejections=cases, nonconstant_witness=dict(length=8, stride=3, numerator=-3, modulus=16,
                                                          real_separation_lower='1/8'))


def retained_kernel_check(module=c):
    fixture = next(row for row in json.loads((HERE/'vendor/pr628/FACTORS.json').read_text())
                   if row['radix'] == 4 and row['embedding'] == 1)
    beta = F(fixture['beta'])
    roots = [tuple(F(v) for v in z) for z in fixture['roots']]
    factors = []
    approximate = [(F(1), F(0))]
    for i, root in enumerate(roots):
        inside = root[0]**2+root[1]**2 < 1
        b = root if inside else o.inverse(root)
        need(b[0]**2+b[1]**2 <= (1-beta)**2, 'retained stable factor')
        factors.append((inside, b, F(4 if i == 0 else 1)))
        following = [(F(0), F(0)) for _ in range(len(approximate)+1)]
        for j, value in enumerate(approximate):
            v = o.rational_mul(root, value)
            following[j] = following[j][0]-v[0], following[j][1]-v[1]
            following[j+1] = following[j+1][0]+value[0], following[j+1][1]+value[1]
        approximate = following
    approximate = [(a/4, b/4) for a, b in approximate]
    exact = [(F(1), F(0)), (F(1, 2), F(1, 2)), (F(1, 4), F(1, 4)), (F(1, 4), F(0))]
    residual = sum(abs(a-c)+abs(b-d) for (a, b), (c, d) in zip(approximate, exact))
    inverse_bound = 4/beta**3
    need(inverse_bound*residual < 1, 'retained factor residual')
    perturbation = inverse_bound**2*residual/(1-inverse_bound*residual)
    rows = []
    for length, stride, dirt in ((5, 2, 7), (8, -3, 2**40)):
        bits = module.working_bits(128, 4, 2*dirt+8, beta, length, stride, count=3, scale_bound=4)
        initial = [data(length, bits, 3+7*j, dirt if j else 0) for j in range(4)]
        banks = [Bank(a) for a in initial]
        tau = F(3, 5), F(4, 5)
        result = module.compose(banks[0], banks[1], factors, banks[2:], tau, beta, bits, stride, -3, 2*length)
        need(banks[0].values == initial[0] and [a.values for a in banks[2:]] == initial[2:],
             'retained kernel restoration')
        source_bound = max(abs(a)+abs(b) for a, b in initial[0])
        total = result.error_bound+perturbation*source_bound
        need(total <= F(1, 1 << 128), 'retained kernel 128-bit budget')
        ideal = o.polynomial(initial[0], exact, stride, -3, 2*length, bits+96, tau)
        error = max(o.squared_distance_bound((banks[1].values[i][0]-initial[1][i][0],
                                               banks[1].values[i][1]-initial[1][i][1]), ideal[i])
                    for i in range(length))
        need(error <= total**2, 'retained dense polynomial accuracy')
        output = digest([a.values for a in banks])
        module.compose(banks[0], banks[1], factors, banks[2:], tau, beta, bits, stride, -3, 2*length, -1)
        need([a.values for a in banks] == initial, 'retained complete-word inverse')
        rows.append(dict(radix=4, embedding=1, length=length, stride=stride, dirt=str(dirt), bits=bits,
                         total_bound_log2_upper=c.d.ceil_log2(total), output_digest=output))
    return dict(factor_residual_log2_upper=c.d.ceil_log2(residual),
                inverse_perturbation_log2_upper=c.d.ceil_log2(perturbation), cases=rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', type=Path)
    args = parser.parse_args()
    result = dict(schema=1, source_pins=pins(), phases=phase_check(), leaves=leaf_check(),
                  kernels=kernel_check(), retained_kernel=retained_kernel_check(), costs=cost_check(), controls=controls())
    encoded = json.dumps(result, indent=2, sort_keys=True)+'\n'
    if args.write:
        with args.write.open('x') as output:
            output.write(encoded)
    else:
        need(canonical(result) == canonical(json.loads((HERE/'EXPECTED.json').read_text())), 'full typed receipt')
    print('PASS_DIRTY_STRIDE_PHASES phases='+str(result['phases']['cases'])
          +' leaves='+str(result['leaves']['cases'])+' kernels='+str(len(result['kernels']))
          +' retained='+str(len(result['retained_kernel']['cases']))+' costs='+str(len(result['costs']))+' input_controls='+str(len(result['controls']['rejections'])))


if __name__ == '__main__':
    main()

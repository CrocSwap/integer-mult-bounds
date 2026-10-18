"""Check phase accuracy, exact cleanup, dirty calls, and the paid work."""
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


c = load(HERE/'chirp.py', 'checked_fast_chirp')
s = c.stream
o = load(HERE/'vendor/pr1038/oracle.py', 'fast_phase_oracle')


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def digest(values):
    return hashlib.sha256(canonical([[str(a), str(b)] for a, b in values]).encode()).hexdigest()


def pins():
    source = json.loads((HERE/'SOURCE.json').read_text())
    for path, row in source['files'].items():
        value = (HERE/path).read_bytes()
        need(hashlib.sha256(value).hexdigest() == row['sha256'], 'source SHA256: '+path)
        blob = hashlib.sha1(b'blob '+str(len(value)).encode()+b'\0'+value).hexdigest()
        need(blob == row['git_blob'], 'source Git blob: '+path)
    return len(source['files'])


def coefficient_check(value, coefficients, ideal, bits):
    quadrant, tangent, sine = coefficients
    real, imag = ideal
    reduced = ((real, imag), (imag, o.neg(real)),
               (o.neg(real), o.neg(imag)), (o.neg(imag), real))[quadrant]
    need(reduced[0][0] >= F(3, 5), 'phase quadrant')
    denominator = o.plus(o.point(1), reduced[0], bits+96)
    quotients = [v/w for v in reduced[1] for w in denominator]
    error_t = max(abs(tangent-min(quotients)), abs(tangent-max(quotients)))
    error_s = max(abs(sine-reduced[1][0]), abs(sine-reduced[1][1]))
    need(max(error_t, error_s) <= F(1, 1 << (bits+8)), 'phase coefficient accuracy')
    bound = 4*(abs(value[0])+abs(value[1])+1)*F(1, 1 << bits)
    outputs = []
    for inverse in (False, True):
        result = s.rotate(value, coefficients, bits, inverse)
        phase = (ideal[0], o.neg(ideal[1])) if inverse else ideal
        expected = o.complex_mul(phase, o.complex_point(value), bits+96)
        need(o.squared_distance_bound(result, expected) <= bound**2, 'grid rotation accuracy')
        need(s.rotate(result, coefficients, bits, not inverse) == value, 'grid rotation inverse')
        outputs.append(result)
    return digest(outputs)


def phase_case(numerator, modulus, bits, length, sample_stride=1):
    meter = s.Meter()
    plan = s.Phase.prepare(numerator, modulus, bits, meter, length)
    state = plan.start()
    unit = F(1, 1 << plan.state_bits)
    value = F(2**80)+F(1, 1 << bits), -F(2**61)+F(3, 1 << bits)
    result = hashlib.sha256()
    samples = 0
    maximum_ratio = F(0)
    for j in range(length):
        if j % sample_stride == 0 or j == length-1:
            ideal = o.phase(numerator, modulus, j, plan.state_bits+96)
            ratio = o.phase(numerator*(2*j+1), modulus, 1, plan.state_bits+96)
            phase_bound = 256*(j+1)**2*unit
            ratio_bound = 12*(j+1)*unit
            actual_error = o.squared_distance_bound(state.value, ideal)
            need(actual_error <= phase_bound**2, 'phase state drift')
            need(o.squared_distance_bound(state.ratio, ratio) <= ratio_bound**2, 'ratio state drift')
            maximum_ratio = max(maximum_ratio, actual_error/phase_bound**2)
            coefficients = state.coefficients()
            result.update(coefficient_check(value, coefficients, ideal, bits).encode())
            need(state.erase_coefficients(coefficients) == (0, 0, 0), 'emitted coefficient zero')
            samples += 1
        state.step()
    state.clear()
    need(state.value == state.ratio == c.d.ZERO, 'phase state zero')
    plan.clear()
    need(plan.seed == c.d.ZERO and plan.omega == (0, 0, 0), 'phase seed zero')
    need(meter.stream_steps == meter.stream_reverse_steps == length, 'paid reverse reconstruction')
    need(meter.stream_charts == 4*length+2*samples, 'paid coefficient reconstruction')
    need(meter.phase_products == 12*length+6, 'paid phase state rotations')
    need(meter.seed_cleanups == 6 and meter.stream_cleanups == meter.preparation_cleanups == 1,
         'complete phase cleanup')
    return dict(numerator=str(numerator), modulus=str(modulus), bits=bits, length=length,
                sample_stride=sample_stride, samples=samples, state_bits=meter.state_bits,
                max_squared_drift_ratio_log2=c.d.ceil_log2(maximum_ratio) if maximum_ratio else None,
                seed_peak_bits=meter.seed_peak_bits, output_digest=result.hexdigest())


def phases():
    rows = []
    for bits in (2, 24):
        for modulus in range(1, 10):
            for numerator in range(modulus):
                rows.append(phase_case(numerator, modulus, bits, 2*modulus+1))
    for bits, numerator, modulus, length in (
            (64, -3, 16, 33), (64, 5, 17, 41), (128, -17, 31, 65),
            (96, 1, 2**160+7, 9), (96, 2**180+9, 2**160+7, 9),
            (96, 2**157-1, 2**160, 11), (96, 2**157+1, 2**160, 11)):
        rows.append(phase_case(numerator, modulus, bits, length))
    rows.append(phase_case(12345, 65537, 24, 16384, 257))
    return rows


class Bus:
    def __init__(self):
        self.heads = {0: 0, 1: 0}
        self.minimum_moves = self.reads = self.writes = 0

    def access(self, tape, position, write):
        self.minimum_moves += abs(position-self.heads[tape])+1
        self.heads[tape] = position
        if write:
            self.writes += 1
        else:
            self.reads += 1


class Bank:
    def __init__(self, values, bus, tape, offset=0):
        self.values = list(values)
        self.bus, self.tape, self.offset = bus, tape, offset

    def __len__(self):
        return len(self.values)

    def __iter__(self):
        raise ValueError('array copies are not allowed')

    def __getitem__(self, index):
        need(type(index) is int, 'array slices are not allowed')
        self.bus.access(self.tape, self.offset+index, False)
        return self.values[index]

    def __setitem__(self, index, value):
        need(type(index) is int, 'array slices are not allowed')
        self.bus.access(self.tape, self.offset+index, True)
        self.values[index] = value


def data(length, bits, salt, dirt=0):
    unit = F(1, 1 << bits)
    return [(dirt+F((7*j+salt) % 19-9, 8)+unit,
             -dirt+F((11*j+salt) % 17-8, 16)+3*unit) for j in range(length)]


def word_case(length, stride, numerator, modulus, dirt, count=1, sign=1):
    beta = F(1, 4)
    factors = [(j % 2 == 0, (F(1, 4), F((-1)**j, 8)), F(1)) for j in range(count)]
    tau = F(3, 5), F(4, 5)
    bits = c.working_bits(24, 4, 2*abs(dirt)+16, beta, length, stride,
                          count=count, scale_bound=1 if count > 1 else None)
    height = (count-1).bit_length()
    initial = [data(length, bits, 3+7*j, dirt if j else 0) for j in range(height+2)]
    bus = Bus()
    banks = [Bank(a, bus, 1 if j == len(initial)-1 else 0,
                  0 if j == len(initial)-1 else j*length) for j, a in enumerate(initial)]
    x, y, scratch = banks[0], banks[1], banks[2:]
    def call(direction):
        if count == 1:
            return c.lift(x, y, (F(3, 10), F(2, 5)), beta, bits, stride,
                          numerator, modulus, direction)
        return c.compose(x, y, factors, scratch, tau, beta, bits, stride,
                         numerator, modulus, direction)
    meter = call(sign)
    need(x.values == initial[0] and [a.values for a in scratch] == initial[2:], 'dirty source restoration')
    need(meter.reads == bus.reads and meter.writes == bus.writes, 'literal data access bill')
    need(meter.tape_moves >= bus.minimum_moves, 'physical data movement bill')
    need(set(meter.heads) == {0, 1} and all(v == 0 for v in meter.heads.values()), 'returned data heads')
    calls = c.d.leaf_calls(count)
    bill = 4160*length if count == 1 else 8256*(calls+1)*(height+2)*length
    need(meter.tape_moves <= bill, 'complete two-tape bound')
    need(meter.phase_evaluations == meter.stream_steps == meter.stream_reverse_steps == 4*length,
         'four phase streams')
    need(meter.stream_cleanups == 4 and meter.preparation_cleanups == 1, 'word phase cleanup')
    need(meter.phase_products == 60*length+6 and meter.phase_divisions == 24*length,
         'linear phase arithmetic')
    need(meter.error_bound <= F(1, 1 << 25), 'complete dirty precision')
    if count == 1:
        exact = o.leaf(initial[0], (F(3, 10), F(2, 5)), stride, numerator, modulus, bits+96)
    else:
        exact = o.kernel(initial[0], factors, tau, stride, numerator, modulus, bits+96)
    error = F(0)
    nonzero = False
    for j in range(length):
        increment = tuple(sign*(v-w) for v, w in zip(y.values[j], initial[1][j]))
        error = max(error, o.squared_distance_bound(increment, exact[j]))
        nonzero |= any(not lo <= v <= hi for v, (lo, hi) in zip(increment, exact[j]))
    need(error <= meter.error_bound**2, 'dirty operator accuracy')
    need(nonzero, 'nonzero rounded execution error')
    output = digest(y.values)
    call(-sign)
    need([a.values for a in banks] == initial, 'complete dirty inverse')
    return dict(length=length, stride=stride, count=count, sign=sign, dirt=str(dirt), bits=bits,
                borrowed_arrays=height, calls=calls, tape_moves=meter.tape_moves,
                seed_terms=meter.seed_terms, products=meter.phase_products,
                divisions=meter.phase_divisions, output_digest=output)


def words():
    rows = []
    for length, stride, dirt in ((1, 0, 7), (5, 2, -13), (8, -3, 2**40), (17, 7, 2**80)):
        for count in (1, 3):
            for sign in (-1, 1):
                rows.append(word_case(length, stride, -3, 2*length, dirt, count, sign))
    return rows


def costs():
    rows = []
    for length, bits in ((32, 16), (257, 48), (2048, 96)):
        before = data(length, bits, 3)
        a, b = list(before), list(before)
        old_meter, new_meter = s.old.Meter(), s.Meter()
        old_meter.layout = {id(a): (0, 0)}
        new_meter.layout = {id(b): (0, 0)}
        old_plan = s.old.Phase.prepare(-3, 2*length+1, bits, old_meter)
        new_plan = s.Phase.prepare(-3, 2*length+1, bits, new_meter, length)
        for inverse in (False, True):
            s.old.phase_pass(a, old_plan, inverse)
            s.phase_pass(b, new_plan, inverse)
        new_plan.clear()
        need(a == b == before, 'same-input baseline restoration')
        need(old_meter.reads == new_meter.reads and old_meter.writes == new_meter.writes
             and old_meter.tape_moves == new_meter.tape_moves, 'same-input tape equality')
        need(new_meter.phase_products == 30*length+6 and new_meter.phase_divisions == 12*length,
             'linear stream work')
        need(new_meter.seed_terms <= 48*new_meter.internal_bits,
             'seed work independent of stream length')
        rows.append(dict(length=length, bits=bits, old_terms=old_meter.phase_terms,
                         old_products=old_meter.phase_products, old_divisions=old_meter.phase_divisions,
                         new_seed_terms=new_meter.seed_terms, new_seed_products=new_meter.seed_products,
                         new_seed_divisions=new_meter.seed_divisions, new_stream_products=new_meter.phase_products,
                         new_stream_divisions=new_meter.phase_divisions, new_seed_peak_bits=new_meter.seed_peak_bits,
                         new_state_bits=new_meter.state_bits, tape_moves=new_meter.tape_moves))
    return rows


def controls():
    rows = []
    def reject(label, call, expected):
        try:
            call()
        except ValueError as error:
            need(str(error) == expected, 'wrong rejection: '+label)
            rows.append(label)
        else:
            raise ValueError('accepted invalid input: '+label)
    for label, args, expected in (
            ('zero_modulus', (1, 0, 12, 8), 'integer phase descriptor'),
            ('boolean_numerator', (True, 7, 12, 8), 'integer phase descriptor'),
            ('zero_length', (1, 7, 12, 0), 'phase stream domain'),
            ('boolean_precision', (1, 7, True, 8), 'phase stream domain')):
        a, m, w, length = args
        reject(label, lambda a=a, m=m, w=w, length=length:
               s.Phase.prepare(a, m, w, s.Meter(), length), expected)
    p = s.Phase.prepare(1, 8, 12, s.Meter(), 3)
    state = p.start()
    reject('second_stream', p.start, 'one open phase stream')
    reject('early_seed_clear', p.clear, 'phase stream must be clear')
    state.step()
    state.clear()
    p.clear()
    reject('cleared_seed', p.start, 'active phase preparation')
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', type=Path)
    args = parser.parse_args()
    result = dict(schema=1, source_pins=pins(), phases=phases(), words=words(), costs=costs(), controls=controls())
    encoded = json.dumps(result, indent=2, sort_keys=True)+'\n'
    if args.write:
        with args.write.open('x') as output:
            output.write(encoded)
    else:
        need(canonical(result) == canonical(json.loads((HERE/'EXPECTED.json').read_text())), 'full typed receipt')
    print('PASS_DIRTY_STRIDE_FAST_PHASES phases='+str(len(result['phases']))
          +' samples='+str(sum(row['samples'] for row in result['phases']))
          +' words='+str(len(result['words']))+' costs='+str(len(result['costs']))
          +' input_controls='+str(len(result['controls'])))


if __name__ == '__main__':
    main()

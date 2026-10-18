"""Check the new precision contract with exact arithmetic."""
import argparse
import ast
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from math import gcd
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.set_int_max_str_digits(0)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


d = load(HERE/'dirty_stride.py', 'stride_precision_solver')
b = load(HERE/'budget.py', 'stride_precision_budget')
v = load(HERE/'vendor/pr985/verify.py', 'stride_precision_reference')
c = load(HERE/'vendor/pr985/vendor/pr628/check.py', 'stride_precision_kernel')


class Bank(v.Bank):
    """Count each actual indexed access, apart from the solver's meter."""
    def __init__(self, values):
        super().__init__(values)
        self.reads = self.writes = 0

    def __getitem__(self, index):
        self.reads += 1
        return super().__getitem__(index)

    def __setitem__(self, index, value):
        self.writes += 1
        super().__setitem__(index, value)


def run_counted(fn, arrays):
    before = (sum(a.reads for a in arrays), sum(a.writes for a in arrays))
    meter = fn()
    after = (sum(a.reads for a in arrays), sum(a.writes for a in arrays))
    d.need(after[0]-before[0] == meter.reads and after[1]-before[1] == meter.writes,
           'literal indexed access charge')
    return meter


def digest(value):
    return hashlib.sha256(json.dumps(value, default=str, sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


def pins():
    records = json.loads((HERE/'SOURCES.json').read_text())['sources']
    for row in records:
        data = (HERE/row['local']).read_bytes()
        d.need(hashlib.sha256(data).hexdigest() == row['sha256'], 'source SHA256')
        header = b'blob '+str(len(data)).encode()+b'\0'
        d.need(hashlib.sha1(header+data).hexdigest() == row['blob'], 'source Git blob')
    def word(text):
        nodes = ast.parse(text).body
        return [ast.dump(node) for node in nodes
                if not isinstance(node, ast.Expr)
                and getattr(node, 'name', '') not in ('admitted', 'effective_depth')]
    reference = (HERE/'vendor/pr985/dirty_stride.py').read_text()
    old = "            need(rnd(data[i], bits) == data[i], 'fixed grid data')"
    new = ("            datum = data[i]\n"
           "            need(rnd(datum, bits) == datum, 'fixed grid data')\n"
           "            del datum")
    d.need(reference.count(old) == 2, 'two retained validation sites')
    d.need(word((HERE/'dirty_stride.py').read_text()) == word(reference.replace(old, new)),
           'unchanged rounded word and tape operations')
    return len(records)


def budget_checks():
    def calls(n):
        return 1 if n == 1 else 2*(calls(n//2)+calls(n-n//2))
    rows = []
    for r in range(3, 513):
        if not b.prime_power(r):
            continue
        ell, h = (r-1).bit_length(), (r-2).bit_length()
        prime = next((j for j in range(2, r+1) if r % j == 0))
        phi = r-r//prime
        delta = 1+2*ell+r*(r-1)*phi
        inverse, gap = 2*delta+r+2, delta+ell+2*r+2
        prefix = inverse+2*r+ell+1+2*h
        count = calls(r-1)
        for p in (0, 1, 16, 128, 1024):
            for m in (0, 20, 128):
                for incoming in (0, 64, 4096):
                    row = b.uniform(r, p, m, incoming)
                    b.check_uniform(row)
                    d.need((row['phi'], row['leaf_calls'], row['prefix_exponent'])
                           == (phi, count, prefix), 'independent prefix budget')
                    local = row['local_error_exponent']
                    d.need(local >= 5*gap and 68*(r+1) <= 1 << (local-5*gap),
                           'independent local bound')
                    w = row['working_bits']
                    e = w-p-m-3*prefix-local-3
                    d.need(e >= 0 and count <= 1 << e, 'independent execution budget')
                    d.need(w >= max(incoming, 4*gap+16), 'independent admission budget')
                    d.need(row['integer_bits'] >= prefix+m+8*gap+2*ell+15,
                           'inverse preimage integer guard')
                    d.need(row['preparation_error_exponent'] >= p+2*inverse+m+4,
                           'independent coefficient error')
                    d.need(w <= max(p, incoming)+m+18*r**3
                           and row['integer_bits'] <= m+15*r**3,
                           'independent cubic bounds')
                    rows.append(row)
    comparison = b.uniform(64, 128, 20, 0)
    g, calls64 = comparison['margin_exponent'], comparison['leaf_calls']
    old = (129+(calls64*68*65*((1 << 20)+1)-1).bit_length()+5*g
           +(calls64-1)*(g+7))
    return dict(cases=len(rows), sha256=digest(rows), radix64=comparison,
                radix64_old_fractional_bits=old)


def admission_checks():
    checked = 0
    for g in range(1, 65):
        beta = F(1, 1 << g)
        for bits in range(4*g+16, 4*g+33):
            depth = d.effective_depth(beta, bits)
            d.need(depth == g+bits.bit_length(), 'effective depth formula')
            d.need(48*(depth+1) <= 1 << (bits-3*g), 'all-length admission inequality')
            d.need(d.admitted(beta, bits, 1 << 100), 'large structural depth admission')
            checked += 1
    decay = []
    for beta in (F(1, 2), F(1, 3), F(1, 16), F(2, 129), F(1, 4096)):
        for bits in (12, 24, 64, 128):
            depth = d.effective_depth(beta, bits)
            for phase in (d.ONE, (F(3, 5), F(4, 5)), (F(-5, 13), F(12, 13))):
                coefficient = tuple((1-beta)*z for z in phase)
                for exponent in (1 << depth, (1 << depth)+1, 3 << depth):
                    d.need(d.power(coefficient, exponent, bits, d.Meter()) == d.ZERO,
                           'exact coefficient extinction')
                    decay.append((str(beta), bits, depth, exponent, phase))
    geometries = 0
    for length in range(1, 129):
        for stride in range(length):
            divisor = gcd(length, stride)
            cycle = length//divisor
            inverse = pow(stride//divisor, -1, cycle) if cycle > 1 else 0
            geo = d.Geometry(d.ONE, divisor, cycle, inverse, 64, d.Meter())
            n, w, orientation, level = length, stride, 1, 0
            while True:
                w %= n
                if 2*w > n:
                    w, orientation = n-w, -orientation
                exponents = geo.exponents(n, w, orientation)
                d.need(min(exponents) >= 1 << level and max(exponents) <= cycle,
                       'return exponent growth and cycle maximum')
                if w == 0:
                    break
                n, w, level = w, (-n) % w, level+1
            geometries += 1
    return dict(thresholds=checked, extinction_cases=len(decay),
                extinction_sha256=digest(decay), geometries=geometries)


def zero_subtrees():
    rows = []
    for root in ((F(1, 2), F(0)), (F(3, 10), F(2, 5))):
        length, stride, bits, beta = 5741, 2378, 12, F(1, 2)
        cutoff = d.effective_depth(beta, bits)
        n, w, orientation = length, stride, 1
        for _ in range(cutoff):
            w %= n
            if 2*w > n:
                w, orientation = n-w, -orientation
            n, w = w, (-n) % w
        if 2*w > n:
            w, orientation = n-w, -orientation
        for sign in (-1, 1):
            originals = [v.values(n, bits, 36), v.values(n, bits, 71)]
            arrays = [v.Bank(z) for z in originals]
            meter = d.Meter(layout={id(arrays[0]): (0, 0), id(arrays[1]): (1, 0)})
            geo = d.Geometry(root, 1, length, pow(stride, -1, length), bits, meter)
            d.need(geo.coefficients(n, w, orientation) == (d.ZERO, d.ZERO),
                   'zero subtree coefficients')
            start = 0 if orientation == 1 else n-1
            views = [d.View(a, start, orientation, n, meter) for a in arrays]
            d.solve(*views, w, geo, sign=sign, level=cutoff)
            expected = [d.add(y, tuple(sign*z for z in x))
                        for x, y in zip(*originals)]
            d.need(arrays[0].values == originals[0] and arrays[1].values == expected,
                   'zero subtree exact addition')
            bound = 2*v.magnitude(originals)
            d.need(max(a.peak_l1 for a in arrays) <= bound,
                   'zero subtree depth-independent magnitude')
            rows.append(dict(root=list(map(str, root)), length=n, stride=w, sign=sign,
                             effective_depth=cutoff, remaining_depth=d.depth(n, w),
                             peak_l1=str(max(a.peak_l1 for a in arrays))))
    return rows


def leaf_checks(limit=12):
    rows, target_increments = [], []
    for beta in (F(1, 2), F(1, 16), F(1, 4096)):
        bits = 32+6*b.ceil_log2(1/beta)
        coefficient = ((1-beta)*F(3, 5), (1-beta)*F(4, 5))
        for length in range(1, limit+1):
            for stride in range(-length, length):
                originals = [v.values(length, bits, 36), v.values(length, bits, 71)]
                exact = v.cycle_oracle(originals[0], coefficient, stride)
                sign = -1 if stride < 0 else 1
                shift = stride % length
                multiplier = (F(6, 5), F(8, 5))
                arrays = [Bank(a) for a in originals]
                reference = [v.Bank(a) for a in originals]
                meter = run_counted(lambda: d.lift(*arrays, coefficient, beta, bits, stride,
                                                  sign, multiplier, shift), arrays)
                old_meter = v.d.lift(*reference, coefficient, beta, bits, stride, sign, multiplier, shift)
                d.need([a.values for a in arrays] == [a.values for a in reference],
                       'same rounded output as PR985')
                d.need(meter.tape_moves == old_meter.tape_moves, 'same complete tape movement')
                d.need(arrays[0].values == originals[0], 'source restoration')
                bound = d.leaf_bound(v.magnitude([originals[0]]), beta, bits, 2)
                error = max(d.norm2(d.sub(d.sub(arrays[1].values[i], originals[1][i]),
                              tuple(sign*z for z in d.mul(multiplier, exact[(i-shift) % length]))))
                            for i in range(length))
                d.need(error <= bound**2, 'signed source-only leaf error')
                run_counted(lambda: d.lift(*arrays, coefficient, beta, bits, stride,
                                          -sign, multiplier, shift), arrays)
                d.need([a.values for a in arrays] == originals, 'signed leaf inverse')
                rows.append((str(beta), length, stride, sign, error != 0))
    for salt in (1, 2):
        x, y = v.values(3, 48, 36), v.values(3, 48, salt)
        source, target = v.Bank(x), v.Bank(y)
        d.lift(source, target, (F(3, 10), F(2, 5)), F(1, 2), 48, 1)
        target_increments.append([d.sub(a, z) for a, z in zip(target.values, y)])
    d.need(target_increments[0] != target_increments[1], 'actual target dependence')
    return dict(cases=len(rows), nonzero_errors=sum(row[-1] for row in rows),
                sha256=digest(rows), target_dependence=True)


def deep_admission():
    length, stride, bits, beta = 5741, 2378, 12, F(1, 2)
    originals = [v.values(length, bits, 36), v.values(length, bits, 71)]
    d.need(not v.d.admitted(beta, bits, d.depth(length, stride)), 'old length gate fixture')
    d.need(d.admitted(beta, bits, d.depth(length, stride)), 'new length gate fixture')
    arrays = [Bank(z) for z in originals]
    coefficient = (F(3, 10), F(2, 5))
    meter = run_counted(lambda: d.lift(*arrays, coefficient, beta, bits, stride), arrays)
    net = [d.sub(a, z) for a, z in zip(arrays[1].values, originals[1])]
    residual = max(d.norm2(d.sub(d.sub(net[i], d.mul(coefficient, net[(i-stride) % length])),
                               originals[0][i])) for i in range(length))
    bound = d.leaf_bound(v.magnitude([originals[0]]), beta, bits)
    d.need(0 < residual <= (beta*bound)**2, 'newly admitted inverse residual')
    d.need(arrays[0].values == originals[0], 'deep source restoration')
    d.need(meter.tape_moves <= 4096*length and all(x == 0 for x in meter.heads.values()),
           'full deep tape bill')
    run_counted(lambda: d.lift(*arrays, coefficient, beta, bits, stride, -1), arrays)
    d.need([a.values for a in arrays] == originals, 'deep inverse cancellation')
    return dict(length=length, stride=stride, bits=bits, structural_depth=d.depth(length, stride),
                effective_depth=d.effective_depth(beta, bits), old_admitted=False,
                tape_moves=meter.tape_moves, residual_squared=str(residual))


def kernel_cases():
    rows = []
    fixtures = json.loads((HERE/'vendor/pr985/vendor/pr628/FACTORS.json').read_text())
    for fixture in fixtures:
        state = c.certify(fixture)
        r, beta = state['radix'], state['beta']
        factors = [(inside, z, F(r if j == 0 else 1))
                   for j, (inside, z) in enumerate(state['factors'])]
        qnorm = sum(abs(re)+abs(im) for re, im in state['q'])
        inverse = F(state['certificate']['inverse_norm_bound'])
        subset = max(F(1), r*(1 << (r-1))*qnorm*inverse)
        budget = b.choose(r-1, r, beta, subset, 4, 128, 16)
        for length, stride in ((1, 0), (3, 1), (5, 2), (5, -2)):
            for tau in (d.ONE, (F(3, 5), F(4, 5))):
                row = execute_kernel(state, factors, beta, budget, length, stride, tau)
                row['old_working_bits'] = v.d.working_bits(r-1, r, beta, 4, 128, 16, length, stride)
                rows.append(row)
        print('checked kernel', r, fixture['embedding'], flush=True)
    return rows


def uniform_kernel_cases():
    rows = []
    fixtures = json.loads((HERE/'vendor/pr985/vendor/pr628/FACTORS.json').read_text())
    for fixture in fixtures[:3]:
        r, embedding = fixture['radix'], fixture['embedding']
        row = b.uniform(r, 128, 2, 16)
        beta = F(1, 1 << row['margin_exponent'])
        roots = [d.rnd(tuple(map(F, z)), row['factor_bits']) for z in fixture['roots']]
        q, factors = [d.ONE], []
        for j, root in enumerate(roots):
            inside = d.norm2(root) < 1
            coefficient = root if inside else d.div(d.ONE, root)
            d.need(d.norm2(coefficient) <= (1-beta)**2, 'uniform prepared margin')
            factors.append((inside, coefficient, F(r if j == 0 else 1)))
            new = [d.ZERO]*(len(q)+1)
            for i, value in enumerate(q):
                new[i] = d.sub(new[i], d.mul(root, value))
                new[i+1] = d.add(new[i+1], value)
            q = new
        q = [tuple(z/r for z in value) for value in q]
        boxes = c.ik.kernel(r, embedding)
        epsilon = sum(max(abs(endpoint-value) for endpoint in interval)
                      for box, coefficient in zip(boxes, q)
                      for interval, value in zip(box, coefficient))
        d.need(epsilon <= F(1, 1 << row['preparation_error_exponent']),
               'uniform prepared coefficient error')
        d.need(sum(abs(re)+abs(im) for re, im in q) <= 1 << r, 'uniform coefficient norm')
        inverse = 1 << row['inverse_exponent']
        d.need(inverse*epsilon <= F(1, 2), 'uniform Neumann admission')
        perturbation = 2*inverse**2*epsilon
        subset = 1 << (row['inverse_exponent']+2*r+(r-1).bit_length())
        budget = b.execution(r-1, r, beta, subset, 4, row['working_bits'])
        budget.update(working_bits=row['working_bits'], integer_bits=row['integer_bits'])
        state = dict(radix=r, embedding=embedding, q=q,
                     certificate=dict(factorization_inverse_error_bound=str(perturbation)))
        for length, stride in ((1, 0), (5, 2), (12, 5)):
            for tau in (d.ONE, (F(3, 5), F(4, 5))):
                result = execute_kernel(state, factors, beta, budget, length, stride, tau)
                result['factor_bits'] = row['factor_bits']
                result['coefficient_error_log2_upper'] = b.ceil_log2(epsilon)
                rows.append(result)
        print('checked uniform kernel', r, embedding, flush=True)
    return rows


def execute_kernel(state, factors, beta, budget, length, stride, tau):
    r, bits = state['radix'], budget['working_bits']
    originals = [v.values(length, bits, 36+7*j) for j in range(2+budget['dirty_arrays'])]
    d.need(v.magnitude(originals) <= 4, 'initial magnitude')
    d.need(all((component*(1 << bits)).numerator % 2
               for a in originals for pair in a for component in pair), 'odd lowest input bits')
    arrays = [Bank(z) for z in originals]
    def execute(sign):
        return run_counted(lambda: d.compose(*arrays[:2], factors, arrays[2:], tau,
                                            beta, bits, stride, sign), arrays)
    meter = execute(1)
    d.need(arrays[0].values == originals[0] and [a.values for a in arrays[2:]] == originals[2:],
           'kernel source and scratch restoration')
    net = [d.sub(a, z) for a, z in zip(arrays[1].values, originals[1])]
    exact = c.matrix_solve(originals[0], c.phased_polynomial(state['q'], tau), stride)
    error = max(d.norm2(d.sub(a, z)) for a, z in zip(net, exact))
    d.need(0 < error <= budget['error']**2, 'new kernel execution error')
    perturbation = F(state['certificate']['factorization_inverse_error_bound'])*4
    d.need(budget['error']+perturbation <= F(1, 1 << 128), 'true kernel target')
    d.need(meter.leaves == budget['leaf_calls'], 'complete paid leaf count')
    tape = 8192*(meter.leaves+1)*len(arrays)*length
    d.need(meter.tape_moves <= tape and set(meter.heads) == {0, 1}
           and all(x == 0 for x in meter.heads.values()), 'complete two-tape bill')
    peak = max(a.peak_l1 for a in arrays)
    d.need(peak <= budget['internal_magnitude'], 'forward integer guard')
    execute(-1)
    d.need([a.values for a in arrays] == originals, 'complete word inverse')
    execute(-1)
    negative = [d.sub(a, z) for a, z in zip(arrays[1].values, originals[1])]
    negative_error = max(d.norm2(d.add(a, z)) for a, z in zip(negative, exact))
    d.need(0 < negative_error <= budget['error']**2, 'standalone inverse error at preimage')
    d.need(arrays[0].values == originals[0] and [a.values for a in arrays[2:]] == originals[2:],
           'standalone inverse restoration')
    d.need(max(a.peak_l1 for a in arrays) <= budget['internal_magnitude'], 'inverse integer guard')
    execute(1)
    d.need([a.values for a in arrays] == originals, 'positive word cancels inverse')
    return dict(radix=r, embedding=state['embedding'], length=length, stride=stride,
                gauge=list(map(str, tau)), working_bits=bits, integer_bits=budget['integer_bits'],
                leaf_calls=meter.leaves, tape_moves=meter.tape_moves, tape_bound=tape,
                nonzero_error=True, error_squared_log2_upper=b.ceil_log2(error),
                negative_error_squared_log2_upper=b.ceil_log2(negative_error),
                peak_l1_log2_upper=b.ceil_log2(peak), sha256=digest(net))


def controls():
    rows = []
    def reject(name, fn, reason):
        try:
            fn()
        except ValueError as exc:
            d.need(str(exc) == reason, 'wrong rejection for '+name)
            rows.append(dict(name=name, reason=reason))
        else:
            raise ValueError('control accepted: '+name)
    row = b.uniform(5, 128, 2, 16)
    changed = dict(row, working_bits=row['working_bits']-1)
    reject('reduced_precision_certificate', lambda: b.check_uniform(changed), 'certificate fields')
    changed = dict(row, magnitude_bits=True)
    reject('boolean_certificate', lambda: b.check_uniform(changed), 'integer certificate')
    reject('feedback_violation', lambda: b.execution(63, 64, F(1, 2), 1 << 100, 4, 32),
           'feedback smallness')
    reject('underprecision', lambda: d.lift([d.ONE]*3, [d.ZERO]*3, d.ZERO, F(1, 2), 8, 1),
           'precision admission')
    reject('old_length_gate', lambda: v.d.lift([d.ONE]*5741, [d.ZERO]*5741,
                                             d.ZERO, F(1, 2), 12, 2378), 'precision admission')
    reject('off_grid', lambda: d.lift([(F(1, 3), F(0))], [d.ZERO], d.ZERO, F(1, 2), 64, 0),
           'fixed grid data')
    x, y = [d.ONE]*3, [d.ZERO]*3
    fs = [(True, (F(1, 4), F(0)), F(1))]*2
    reject('borrowed_target', lambda: d.compose(x, y, fs, [y], d.ONE, F(1, 2), 64, 1),
           'all arrays distinct')
    reject('nonunit_gauge', lambda: d.compose(x, y, fs, [[d.ZERO]*3],
                                             (F(2), F(0)), F(1, 2), 64, 1), 'immutable unit gauge')
    reject('mixed_unstable_factor', lambda: d.compose(x, y, [fs[0], (True, d.ONE, F(1))],
                                                    [[d.ZERO]*3], d.ONE, F(1, 2), 64, 1),
           'stable factor descriptor')
    d.need(x == [d.ONE]*3 and y == [d.ZERO]*3, 'preflight before mutation')
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', type=Path, help='Write a receipt to a new path.')
    args = parser.parse_args()
    if args.write:
        d.need(not args.write.exists(), 'output already exists')
    result = dict(status='passed', source_pins=pins(), budgets=budget_checks(),
                  admission=admission_checks(), zero_subtrees=zero_subtrees(),
                  inherited_powers=v.power_check(), leaves=leaf_checks(),
                  deep=deep_admission(), kernels=kernel_cases(),
                  uniform_kernels=uniform_kernel_cases(), controls=controls())
    text = json.dumps(result, indent=2, sort_keys=True)+'\n'
    if args.write:
        with args.write.open('x') as out:
            out.write(text)
    else:
        d.need(digest(result) == digest(json.loads((HERE/'EXPECTED.json').read_text())),
               'exact receipt mismatch')
    print('PASS_DIRTY_STRIDE_PRECISION budgets=%d leaves=%d kernels=%d uniform=%d controls=%d' %
          (result['budgets']['cases'], result['leaves']['cases'],
           len(result['kernels']), len(result['uniform_kernels']), len(result['controls'])))


if __name__ == '__main__':
    main()

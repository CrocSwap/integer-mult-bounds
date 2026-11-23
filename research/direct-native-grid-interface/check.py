"""Bounded exact evidence for the native requested-grid adapter.

Prepared for Jerry Chen / @CubeJerry with OpenAI assistance. Apache-2.0.
The C/S/b oracle is mathematical evidence, not a physical native backend.
"""
import argparse
import ast
from fractions import Fraction as F
from hashlib import sha256, sha1
from itertools import product, combinations
import json
from pathlib import Path
import random
from adapter import Format, adapt_raw_h, finish_c_endpoint, validate_domain, validate_strides

ROOT = Path(__file__).resolve().parent


def need(value, message):
    if not value:
        raise ValueError(message)


def authenticate(overrides=None):
    pins = json.loads((ROOT/'SOURCE-BYTES.json').read_text())
    out = {}
    for row in pins['sources']:
        name = row['retained']
        data = (overrides or {}).get(name, (ROOT/name).read_bytes())
        need(sha256(data).hexdigest() == row['sha256'], 'Source SHA256 differs: '+name)
        blob = b'blob '+str(len(data)).encode()+b'\0'+data
        need(sha1(blob).hexdigest() == row['git_blob'], 'Git blob differs: '+name)
        out[name] = data
    return out


def literal_functions(raw):
    tree = ast.parse(raw)
    names = {'hadamard', 'axis_packs'}
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    need({n.name for n in nodes} == names, 'Literal source functions missing')
    env = {}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), 'frozen-tensor-word', 'exec'), env)
    return env['hadamard'], env['axis_packs']


def add(x, y):
    return x[0]+y[0], x[1]+y[1]


def mul(x, y):
    return x[0]*y[0]-x[1]*y[1], x[0]*y[1]+x[1]*y[0]


def trunc(x):
    return (-1 if x < 0 else 1)*(abs(x.numerator)//x.denominator)


def c_normalized_service(field, requested, strides, *, bad_phase=False,
                         omit_b=False, return_bits=None, observer=None):
    """Exact C/S/b endpoint and final toward-zero truncation."""
    unit = 1 << requested
    values = [(F(a, unit), F(b, unit)) for a, b in field]
    alpha, beta = (F(1, 2), F(1, 2)), (F(1, 2), F(-1, 2))
    if bad_phase:
        alpha, beta = beta, alpha
    phases = []
    for i in range(len(field)):
        k = sum(bool(i&s) for s in strides) % 4
        phases.append(((1, 0), (0, 1), (-1, 0), (0, -1))[k])
    values = [mul(z, phase) for z, phase in zip(values, phases)]
    if observer:
        observer(values)
    for stride in strides:
        for start in range(0, len(values), 2*stride):
            for lo in range(start, start+stride):
                hi = lo+stride
                u, v = values[lo], values[hi]
                values[lo] = add(mul(alpha, u), mul(beta, v))
                values[hi] = add(mul(beta, u), mul(alpha, v))
        if observer:
            observer(values)
    values = [mul(z, phase) for z, phase in zip(values, phases)]
    terminal_check = None
    if not omit_b and not bad_phase:
        f = requested+len(strides)
        raw = [(a*(1 << f), b*(1 << f)) for a, b in values]
        need(all(a.denominator == b.denominator == 1 for a, b in raw), 'C endpoint grid')
        terminal_check = finish_c_endpoint([(int(a), int(b)) for a, b in raw], len(strides))
        terminal_check = [(F(a, 1 << f), F(b, 1 << f)) for a, b in terminal_check]
    if not omit_b:
        for _ in range(len(strides)//2):
            values = [mul(z, (0, F(-1, 2))) for z in values]
            if observer:
                observer(values)
        if len(strides) % 2:
            values = [mul(z, (F(1, 2), F(-1, 2))) for z in values]
            if observer:
                observer(values)
    if terminal_check is not None:
        need(values == terminal_check, 'Exact integer terminal macro disagrees with rational b^h')
    qout = requested if return_bits is None else return_bits
    return [(trunc(a*(1 << qout)), trunc(b*(1 << qout))) for a, b in values]


def public_parameters(p, widths):
    d, L, m = len(widths), sum(widths), max(widths)
    E = (257*L+1)//2+1354*d
    A = 20*L+303*d
    J = 20000*(d+1)*(m+2)**6
    C = 4*J*(d+1)**2+d+1
    P = 4*p+A+2*E+C.bit_length()
    return P, E, A, C


def run():
    raw = authenticate()
    hadamard, axis_packs = literal_functions(raw['retained/tensor_word.py'])
    cases = components = observed = sharp_controls = 0
    actual_pack_checks = selector_checks = 0

    def compare(field, P, E, strides):
        nonlocal cases, components, observed
        original = list(field)
        expected = list(field)
        hadamard(expected, strides)
        fmt = Format(P, E, len(strides))
        def observe(values):
            nonlocal observed
            for value in values:
                for component in value:
                    n = component*(1 << fmt.conditional_private_fractional_bits)
                    need(n.denominator == 1, 'C/S/b macro leaves the conditional grid')
                    cap = 1 << (fmt.conditional_private_component_bits-1)
                    need(-cap <= n < cap, 'C/S/b macro component width')
                    observed += 1
        def native(z, q, ss):
            need(q == fmt.requested_bits and ss == strides, 'Wrong service parameters')
            need(all(a*a+b*b <= (1 << (2*q-2)) for a, b in z), 'Unit-disk normalization')
            cap = 1 << (fmt.entrance_component_bits-1)
            need(all(-cap <= a < cap and -cap <= b < cap for a, b in z), 'Entrance width')
            return c_normalized_service(z, q, ss, observer=observe)
        actual = adapt_raw_h(field, P, E, strides, native, check_domain=True)
        need(actual == expected, 'Native format adapter disagrees with literal raw H')
        need(list(field) == original, 'Original owner overwritten before complete return')
        cap = 1 << (fmt.returned_raw_component_bits-1)
        need(all(-cap <= a < cap and -cap <= b < cap for a, b in actual), 'Returned raw width')
        cases += 1
        components += 2*len(field)

    for v in product(range(-1, 2), repeat=4):
        compare([(v[0], v[1]), (v[2], v[3])], 1, 0, (1,))
    alphabet = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (-1, 1)]
    for field in product(alphabet, repeat=4):
        compare(field, 2, 0, (1, 2))
    for signs in product((-1, 1), repeat=8):
        compare([(a, 0) for a in signs], 1, 0, (1, 2, 4))
    rng = random.Random(80937849)
    for L in range(2, 7):
        for h in range(1, min(L, 4)+1):
            for positions in list(combinations(range(L), h))[:5]:
                strides = tuple(1 << k for k in positions)
                for P, E in [(1, 0), (3, 2), (17, 3)]:
                    cap = 1 << (P+E-1)
                    field = [(rng.randrange(-cap, cap+1), rng.randrange(-cap, cap+1))
                             for _ in range(1 << L)]
                    compare(field, P, E, strides)
    for P, E, L, strides in [(3438, 1483, 3, (1, 4)), (4097, 12, 2, (1, 2)),
                             (257, 1024, 4, (2, 8)), (1, 0, 2, (1, 2))]:
        cap = 1 << (P+E)
        compare([(cap if i % 2 else -cap, 0) for i in range(1 << L)], P, E, strides)

    for P in (1, 2, 17):
        for E in (0, 2, 7):
            for h in range(1, 6):
                fmt = Format(P, E, h)
                strides = tuple(1 << k for k in range(h))
                for basis in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    field = [basis]+[(0, 0)]*((1 << h)-1)
                    lifted = [(a << h, b << h) for a, b in field]
                    good = c_normalized_service(lifted, fmt.requested_bits, strides)
                    coarse_lifted = [(a << (h-1), b << (h-1)) for a, b in field]
                    bad = c_normalized_service(coarse_lifted, fmt.requested_bits-1, strides)
                    need(any(a or b for a, b in good) and not any(a or b for a, b in bad),
                         'One-bit-coarser final truncation not detected')
                    sharp_controls += 1

    for widths in [(2, 3, 2, 4), (3,)*16, (2,)*128, (2, 3, 4, 5, 2, 3, 4, 5)]:
        sides = tuple(1 << k for k in widths)
        starts, cursor = [], 0
        for ell in widths:
            starts.append(cursor)
            cursor += ell
        for p in (1, 7, 31):
            for active in axis_packs(sides, p):
                need(len({widths[i] for i in active}) == 1, 'Packing mixes widths')
                for bit in range(widths[active[0]]):
                    selected = tuple(1 << (starts[i]+bit) for i in active)
                    validate_strides(1 << sum(widths), selected)
                    actual_pack_checks += 1

    for p in (1, 2, 8, 30, 72, 256, 1024):
        for widths in [(1,), (1, 1), (2, 3), (4, 5), (1,)*16, (17, 1, 2), (200,)]:
            P, E, A, C = public_parameters(p, widths)
            L, d = sum(widths), len(widths)
            need(C < (1 << 29)*L**9, 'Universal C0 comparison')
            need(C.bit_length() <= 29*L and P <= 4*p+3318*L and E <= 1483*L,
                 'Parent selector comparison')
            for h in {1, d}:
                fmt = Format(P, E, h)
                need(fmt.requested_bits <= 4*p+4803*L, 'Requested-width comparison')
                need(fmt.conditional_private_temporary_bits <= 4*p+4835*L,
                     'Private-width comparison')
                if L <= p:
                    need(fmt.requested_bits < 8192*p and fmt.conditional_private_temporary_bits < 8192*p,
                         'Linear production width')
                    need((fmt.requested_bits+1).bit_length() <= (p+1).bit_length()+13,
                         'Native logarithmic parameter shift')
                selector_checks += 1
    P, E, _, _ = public_parameters(30, (1,))
    fmt = Format(P, E, 1)
    need((P, E, fmt.radius_shift, fmt.requested_bits,
          fmt.conditional_private_fractional_bits, fmt.conditional_private_temporary_bits)
         == (3438, 1483, 1484, 4923, 4924, 4955), 'Explicit constructor parameter binding')

    controls = []
    for name, action in [
        ('source_corruption', lambda: authenticate({'retained/tensor_word.py': raw['retained/tensor_word.py']+b'\n# corrupt'})),
        ('duplicate_stride', lambda: validate_strides(4, (1, 1))),
        ('partial_field', lambda: validate_strides(6, (1,))),
        ('non_binary_stride', lambda: validate_strides(8, (3,))),
        ('missing_address_bit', lambda: validate_strides(4, (4,))),
        ('understated_radius', lambda: validate_domain([(3, 0), (0, 0)], Format(1, 0, 1))),
        ('nonendpoint_odd_parity', lambda: finish_c_endpoint([(1, 0), (0, 0)], 1)),
        ('nonendpoint_even_divisor', lambda: finish_c_endpoint([(1, 0)]*4, 2)),
    ]:
        try:
            action()
        except ValueError:
            controls.append(name)
        else:
            raise ValueError('Control did not reject: '+name)
    field = [(1, -1), (2, 1), (-1, 2), (0, -1)]
    expected = list(field)
    hadamard(expected, (1,))
    for name, provider in [
        ('wrong_C_absolute_phase', lambda z, q, ss: c_normalized_service(z, q, ss, bad_phase=True)),
        ('omitted_b_normalization', lambda z, q, ss: c_normalized_service(z, q, ss, omit_b=True)),
        ('wrong_selected_stride', lambda z, q, ss: c_normalized_service(z, q, (2,))),
        ('post_return_second_shift', lambda z, q, ss: [(a << 3, b << 3) for a, b in c_normalized_service(z, q, ss)]),
    ]:
        need(adapt_raw_h(field, 3, 1, (1,), provider) != expected, 'Mutation not detected: '+name)
        controls.append(name)
    return dict(schema='direct-native-grid-evidence/1', status='PASS_DIRECT_NATIVE_GRID_INTERFACE',
                source_bindings=len(raw), exact_adapter_cases=cases, output_components=components,
                checked_macro_components=observed, sharp_coarser_grid_controls=sharp_controls,
                actual_pack_checks=actual_pack_checks, selector_checks=selector_checks,
                rejected_controls=controls,
                example=dict(P=3438,E=1483,R=1484,h=1,Q=4923,F_private=4924,W_temporary=4955),
                scope='Exact endpoint-format implication under supplied native contract; no native implementation, complete assumption removal or new kappa')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    payload = json.dumps(run(), indent=2, sort_keys=True)+'\n'
    if args.output:
        args.output.write_text(payload)
    print(payload, end='')

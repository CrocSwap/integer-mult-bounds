"""Integer and direct Gaussian oracles for the emitted egress program."""
import hashlib
import json
from pathlib import Path
import random
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import egress as E


def need(ok, message):
    if not ok:
        raise ValueError(message)


def gamma(n):
    need(type(n) is int and n >= 1, 'positive Gamma integer')
    s = format(n, 'b')
    return '0'*(len(s)-1)+s


def word(x, width):
    need(-(1 << (width-1)) <= x < (1 << (width-1)), 'signed fixture range')
    return format(x % (1 << width), '0'+str(width)+'b')


def trunc_fraction(n, denominator):
    return (1 if n >= 0 else -1)*(abs(n)//denominator)


def oracle(a, c, d, degree):
    # Repeated Gaussian multiplication, not the production parity decomposition.
    u, v = 1, 0
    for _ in range(degree):
        u, v = u+v, v-u
    den = 1 << (degree+d)
    return trunc_fraction(u*a-v*c, den), trunc_fraction(u*c+v*a, den)


def fixture(p, d, degree, w, values, *, skipped=(1, 1, 1, 1, 1), shift=0):
    h = p+2*d+4
    r, pre, suf, k, rho1 = skipped
    header = ''.join(gamma(v) for v in (p, d, r, degree, pre, suf, k, rho1, w))
    payload = ''.join(word(a, h)+word(c, h) for a, c in values)
    origins = [shift+7*t-60 for t in range(18)]
    tapes = []
    for i, origin in enumerate(origins):
        cells = {origin-2-j: v for j, v in enumerate('101|010')}
        if i == E.HEADER:
            cells.update({origin+j: v for j, v in enumerate(header)})
            cells[origin+len(header)+2] = '1'
        elif i == E.DATA:
            cells.update({origin+j: v for j, v in enumerate(payload)})
            cells[origin+max(len(payload), 2*w*len(values))+2] = '1'
        tapes.append(E.Tape(cells, origin))
    expected = [oracle(a, c, d, degree) for a, c in values]
    fits = all(-(1 << (w-1)) <= z < (1 << (w-1)) for pair in expected for z in pair)
    return tapes, origins, header, payload, expected, fits


def run_case(code, p, d, degree, w, values, *, skipped=(1, 1, 1, 1, 1), shift=0):
    tapes, origins, header, payload, expected, fits = fixture(p, d, degree, w, values, skipped=skipped, shift=shift)
    before = [dict(t.cells) for t in tapes]
    h, n = p+2*d+4, len(values)
    bound = 65536*(len(header)+p+d+degree+w+n*(h+w+1)+1)
    machine = E.Machine(code, tapes)
    try:
        machine.run(bound)
    except ValueError as error:
        need(not fits, 'unexpected rejection: '+str(error))
        need(machine.pc == len(code), 'must reject at explicit range sink')
        need(tapes[E.DATA].cells == before[E.DATA], 'data changed before validation')
        return {'steps': machine.steps, 'accepted': False, 'history': sum(t.high-t.low+1 for t in tapes[2:])}
    need(fits, 'unrepresentable result accepted')
    out = ''.join(word(a, w)+word(c, w) for a, c in expected)
    target, origin = before[E.DATA].copy(), origins[E.DATA]
    for j in range(max(len(payload), len(out))):
        target.pop(origin+j, None)
    target.update({origin+j: bit for j, bit in enumerate(out)})
    for i, tape in enumerate(tapes):
        need(tape.head == origins[i], 'head return '+str(i))
        need(tape.cells == (target if i == E.DATA else before[i]), 'complete tape contract '+str(i))
    history = sum(t.high-t.low+1 for t in tapes[2:])
    need(history <= 4*n*(h+w)+16*(h+w+len(header)+1), 'historical backing bound')
    need(machine.steps <= bound, 'literal time bound')
    return {'steps': machine.steps, 'accepted': True, 'history': history}


def add(x, y):
    return x[0]+y[0], x[1]+y[1]


def mul(x, y):
    return x[0]*y[0]-x[1]*y[1], x[0]*y[1]+x[1]*y[0]


def phase(z, k):
    for _ in range(k % 4):
        z = -z[1], z[0]
    return z


def layer_input(p, d, degree, original):
    values = [phase((a << d, c << d), x.bit_count()) for x, (a, c) in enumerate(original)]
    for axis in range(degree):
        for x in range(1 << degree):
            if x & (1 << axis):
                continue
            y = x | (1 << axis)
            u = add(mul((1, 1), values[x]), mul((1, -1), values[y]))
            v = add(mul((1, -1), values[x]), mul((1, 1), values[y]))
            need(all(z % 2 == 0 for z in (*u, *v)), 'exact common grid')
            values[x], values[y] = (u[0]//2, u[1]//2), (v[0]//2, v[1]//2)
    return values


def actual_layer_check(code):
    rng, cases, fields = random.Random(6201), 0, 0
    for degree in range(1, 7):
        for p in (2, 4):
            d, w, radius = degree+1, p+2, 1 << p
            original = []
            for _ in range(1 << degree):
                while True:
                    z = rng.randint(-radius, radius), rng.randint(-radius, radius)
                    if sum(v*v for v in z) <= radius*radius:
                        original.append(z)
                        break
            inner = layer_input(p, d, degree, original)
            run_case(code, p, d, degree, w, inner)
            for x, z in enumerate(inner):
                got = phase(oracle(*z, d, degree), x.bit_count())
                sums = [sum((1 if (x & y).bit_count() % 2 == 0 else -1)*original[y][part] for y in range(1 << degree)) for part in (0, 1)]
                want = tuple(trunc_fraction(t, 1 << degree) for t in sums)
                need(got == want, 'complete H0 tensor with final S')
                need(sum(v*v for v in got) <= radius*radius, 'disk return')
            cases, fields = cases+1, fields+len(inner)
    return {'cases': cases, 'fields': fields}


def mutant_code(old, new):
    path = Path(__file__).resolve().parent/'egress.py'
    source = path.read_text()
    need(source.count(old) == 1, 'unique mutation site')
    ns = {'__file__': str(path), '__name__': 'mutant_egress'}
    exec(compile(source.replace(old, new), '<semantic-mutant>', 'exec'), ns)
    return ns['compile_egress']()[0]


def main():
    pins = json.loads((Path(__file__).resolve().parent/'SOURCES.json').read_text())
    for pin in pins['files']:
        data = (Path(__file__).resolve().parent/pin['local']).read_bytes()
        need(len(data) == pin['bytes'], 'source byte length')
        need(hashlib.sha256(data).hexdigest() == pin['sha256'], 'source SHA256')
        need(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == pin['blob'], 'source Git blob')
    code, alphabet = E.compile_egress()
    need(len(code) == 17814, 'fixed program length')
    need(alphabet == ('_', '0', '1', '|'), 'fixed alphabet')
    for ins in code:
        need(ins[0] in ('read', 'write', 'move', 'goto', 'halt'), 'literal opcode')
        if ins[0] == 'move':
            need(ins[2] in (-1, 1), 'unit movement')
        if ins[0] == 'goto':
            need(0 <= ins[1] < len(code), 'jump target')
        if ins[0] == 'read':
            need(all(s in alphabet and 0 <= t < len(code) for s, t in ins[2].items()), 'read transitions')
    rng, runs = random.Random(7342), []
    for degree in range(1, 17):
        for p in (1, 3):
            d = degree+degree % 3
            h = p+2*d+4
            cap = 1 << (h-1)
            for w in (p+2, h+3):
                vals = [(0, 0), (-1, 0), (0, -1), (1, -1), (-cap, -cap), (cap-1, cap-1), (-cap, cap-1)]
                vals += [(rng.randrange(-cap, cap), rng.randrange(-cap, cap)) for _ in range(4)]
                for z in vals:
                    runs.append(run_case(code, p, d, degree, w, [z], shift=degree-12))
    runs.append(run_case(code, 2, 1, 1, 4, [(8, 0), (-1, 0), (-128, -128)]))
    runs.append(run_case(code, 4, 5, 4, 6, [(0, 0), (7, -3), (100, 220)]))
    endpoints = 0
    for degree in range(1, 9):
        p, d, w = 2, degree, 4
        u, v = 1, 0
        for _ in range(degree):
            u, v = u-v, u+v
        for q in (-9, -8, 7, 8):
            for z in ((q, 0), (0, q)):
                a, c = mul(z, (u, v))
                runs.append(run_case(code, p, d, degree, w, [(a << d, c << d)]))
                endpoints += 1
    huge = (2**120+19, 2**97+3, 2**101+7, 2**111+1, 2**109+2)
    # Local packet theorem only; the header's complete layout cardinality is a premise.
    runs.append(run_case(code, 3, 3, 2, 5, [(31, -27), (0, 1)], skipped=huge))
    layer = actual_layer_check(code)
    controls = [
        ('odd_shift', 'if mode % 2 == 0:', 'if mode % 2 == 1:', (2, 1, 1, 4, [(16, 0)])),
        ('negative_absolute', '    negate_magnitude(a)\n', '    pass\n', (2, 1, 1, 4, [(-3, 0)])),
        ('wrong_rotation', 'for _ in range(mode//2):', 'for _ in range((mode//2+1) % 4):', (2, 2, 2, 4, [(32, 0)])),
        ('header_return', '    trace_return(a, HEADER, HTRACE)\n', '    pass\n', (2, 1, 1, 4, [(0, 0)])),
        ('old_tail_cleanup', "    a.op('write', DATA, BLANK)\n", "    a.op('write', DATA, ONE)\n", (2, 1, 1, 4, [(8, 0)])),
        ('source_return_before_commit', '    trace_return(a, DATA, DTRACE)\n    a.rewind(OUTPUT, BITS)', '    a.rewind(OUTPUT, BITS)', (2, 1, 1, 4, [(8, 0)])),
    ]
    detected = []
    for name, old, new, args in controls:
        try:
            run_case(mutant_code(old, new), *args)
        except ValueError:
            detected.append(name)
        else:
            raise ValueError('undetected semantic mutant '+name)
    receipt = {
        'status': 'PASS_LITERAL_LAYER_EGRESS', 'program_instructions': len(code),
        'tapes': 18, 'symbols': list(alphabet),
        'program_sha256': hashlib.sha256(json.dumps(code, separators=(',', ':'), sort_keys=True).encode()).hexdigest(),
        'generic_cases': len(runs), 'accepted': sum(r['accepted'] for r in runs),
        'range_rejections': sum(not r['accepted'] for r in runs),
        'literal_steps_generic': sum(r['steps'] for r in runs),
        'max_private_backing_generic': max(r['history'] for r in runs),
        'actual_layer': layer, 'detected_semantic_mutants': detected,
        'signed_endpoint_cases': endpoints, 'authenticated_sources': len(pins['files']),
        'limits': ['All-size correctness rests on the written loop proof.', 'No recursive C, phase-sweep lowering, compiler or full multiplier.', 'Complete caller packet cardinality and header semantics are premises.'],
    }
    print(json.dumps(receipt, sort_keys=True))
    if '--write' in sys.argv:
        (Path(__file__).resolve().parent/'RESULT.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')


if __name__ == '__main__':
    main()

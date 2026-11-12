"""Author finite checks. Decoded arithmetic is confined to these oracles."""
from pathlib import Path
import hashlib
import json
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import leaf as m

CODE, ALPHABET = m.compile_leaf()


class ObservedTape(m.Tape):
    def begin_call(self):
        self.call_low = self.call_high = self.head

    def move(self, direction):
        super().move(direction)
        self.call_low = min(self.call_low, self.head)
        self.call_high = max(self.call_high, self.head)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def gamma(n):
    b = bin(n)[2:]
    return '0'*(len(b)-1)+b


def header(f, r, p, s, w, cutoff):
    return ''.join(gamma(n) for n in (f, r, p, s, w, cutoff))


def signed(n, width):
    require(-(1 << (width-1)) <= n < (1 << (width-1)), 'oracle signed fixture')
    return format(n % (1 << width), '0'+str(width)+'b')


def encode(values, w):
    return ''.join(signed(a, w)+signed(b, w) for a, b in values)


def multiply(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def weights(f):
    result = []
    for x in range(1 << f):
        c = (1, 0)
        for j in range(f):
            c = multiply(c, (1, -1 if x >> j & 1 else 1))
        result.append(c)
    return result


def oracle(values, f, r, p, s, w):
    """Direct tensor rows, not the executable butterfly or carry algorithm."""
    q, tail = 1 << f, (1 << (8*f))*s*r
    require(len(values) == p*q*tail, 'oracle complete array')
    coeffs, denominator = weights(f), 1 << f
    out = []
    for outer in range(p):
        for x in range(q):
            for z in range(tail):
                real = imag = 0
                for y in range(q):
                    a, b = multiply(coeffs[x ^ y], values[(outer*q+y)*tail+z])
                    real += a
                    imag += b
                require(real % denominator == imag % denominator == 0,
                        'nonintegral tensor oracle result')
                out.append((real//denominator, imag//denominator))
    return encode(out, w)


def caps(f, r, p, s, w, cutoff):
    e = len(header(f, r, p, s, w, cutoff))
    n = p*s*r*(1 << (9*f))
    v = 2*n*w
    up = s*r*(1 << (9*f-1))
    pre = p*(1 << (f-1))
    hi = max(pre, up, f, r, p, s, w)
    return [e, v, v, v, 1, e, e, hi, f, r, p, s, w,
            f.bit_length(), f.bit_length(), cutoff.bit_length(), cutoff.bit_length(),
            pre, up, 2*up*w, 2*up*w, 2*up*w, 2*up*w,
            w, w, w, w, w+2, v]


def packet(shape, word, origins=None, roomy=None):
    origins = origins or tuple(5*i-83 for i in range(29))
    limits = roomy or caps(*shape)
    tapes = []
    for i, (origin, limit) in enumerate(zip(origins, limits)):
        cell = {origin-3: '1', origin-2: '|', origin+limit+1: '0', origin+limit+2: '|'}
        if i < 2:
            cell[origin-1] = '1'
        tapes.append(ObservedTape(cell, origin))
        tapes[-1].begin_call()
    for i, text in enumerate((header(*shape), word)):
        tapes[i].cells.update({origins[i]+j: bit for j, bit in enumerate(text)})
    return tapes, origins


def run_case(shape, values, *, accept=True, code=CODE, change=None, tapes=None, origins=None):
    f, r, p, s, w, cutoff = shape
    word = encode(values, w)
    if tapes is None:
        tapes, origins = packet(shape, word)
    for tape in tapes:
        tape.begin_call()  # Observation only; primitive low/high histories persist.
    if change:
        change(tapes, origins)
    before = [dict(t.cells) for t in tapes]
    owners = tuple(map(id, tapes))
    k0 = sum(t.high-t.low+1 for t in tapes[2:])
    cpu = m.Machine(code, tapes)
    rejected = False
    try:
        cpu.run(1_000_000_000)
    except ValueError as exc:
        require(str(exc) == 'invalid scanned symbol', 'unexpected failure: '+str(exc))
        rejected = True
    require(rejected != accept, 'acceptance mismatch')
    require(tuple(map(id, tapes)) == owners, 'owner replaced')
    require(tapes[0].cells == before[0], 'header changed')
    if accept:
        expected = oracle(values, f, r, p, s, w)
        require(tapes[1].cells == before[1] | {origins[1]+j: bit for j, bit in enumerate(expected)},
                'complete tensor result or public exterior mismatch')
        require(all(t.head == u for t, u in zip(tapes, origins)), 'head not returned')
        require(all(t.cells == before[i] for i, t in enumerate(tapes) if i != 1),
                'private window/exterior not restored')
        e, v = len(header(*shape)), len(word)
        require(cpu.steps <= 65536*(f*v+e+1), 'complete tariff exceeded')
        for i, (tape, origin, cap) in enumerate(zip(tapes, origins, caps(*shape))):
            require(tape.call_low >= origin-(i >= 2) and tape.call_high <= origin+cap,
                    'proved frame cap exceeded')
        require(sum(t.high-t.low+1 for t in tapes[2:]) <= k0+64*(v+e+1),
                'private backing envelope exceeded')
    else:
        require(tapes[1].cells == before[1], 'rejected call changed public DATA')
    return cpu.steps


def authenticate():
    sources = json.loads((HERE/'SOURCES.json').read_text())['files']
    for pin in sources:
        raw = (HERE/pin['local']).read_bytes()
        require(len(raw) == pin['bytes'], 'source length')
        require(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'source hash')
        require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == pin['blob'],
                'source Git blob')
    for op, *args in CODE:
        require(op in ('read', 'write', 'move', 'goto', 'halt'), 'nonliteral opcode')
        if op in ('read', 'write', 'move'):
            require(type(args[0]) is int and 0 <= args[0] < 29, 'tape range')
        if op == 'move':
            require(args[1] in (-1, 1), 'nonlocal movement')
        if op == 'write':
            require(args[1] in ALPHABET, 'nonfixed symbol')
        if op == 'read':
            require(set(args[1]) <= set(ALPHABET), 'read alphabet')
            require(all(0 <= v < len(CODE) for v in args[1].values()), 'branch range')
        if op == 'goto':
            require(0 <= args[0] < len(CODE), 'fixed jump range')
    return len(sources)


def repeated_history():
    shapes = [(1,2,1,1,4,3), (1,1,1,1,2,1), (1,2,1,1,4,3)]
    roomy = [max(caps(*shape)[i] for shape in shapes) for i in range(29)]
    tapes, origins = packet(shapes[0], encode([(1,-1)]*1024,4), roomy=roomy)
    owners = tuple(map(id,tapes))
    prior = [t.high-t.low+1 for t in tapes]
    history, steps = [], []
    for shape in shapes:
        f,r,p,s,w,cutoff = shape
        values = [(-2,-2) if w==2 else (1,-1)]*(p*s*r*(1 << (9*f)))
        # Paid caller fixtures replace only public encodings. No private bank,
        # primitive head or historical low/high observer is reset/replaced.
        for i,text in enumerate((header(*shape),encode(values,w))):
            for j in range(roomy[i]+1):
                tapes[i].cells.pop(origins[i]+j,None)
            tapes[i].cells.update({origins[i]+j:bit for j,bit in enumerate(text)})
        steps.append(run_case(shape,values,tapes=tapes,origins=origins))
        require(tuple(map(id,tapes))==owners, 'repeat replaced owner')
        now = [t.high-t.low+1 for t in tapes]
        require(all(a<=b for a,b in zip(prior,now)), 'history shrank or reset')
        prior = now
        history.append(sum(now[2:]))
    require(history[0]==history[1]==history[2], 'reused bank incorrectly changed history')
    return {'calls':3,'private_history':history,'steps':steps,'owner_inventory':29}


def main():
    sources = authenticate()
    rng = random.Random(2026111204)
    cases, steps = [], 0
    for w, value in ((2, (-2, -2)), (3, (3, 3)), (3, (-4, -4))):
        shape = (1, 1, 1, 1, w, 1)
        count = run_case(shape, [value]*512)
        cases.append({'shape': list(shape), 'kind': 'constant signed endpoint', 'steps': count})
        steps += count
    for shape in ((1, 2, 1, 1, 4, 1), (1, 1, 2, 1, 5, 3), (1, 1, 1, 2, 4, 2)):
        f, r, p, s, w, cutoff = shape
        values = [(2*rng.randrange(-1, 2), 2*rng.randrange(-1, 2))
                  for _ in range(p*s*r*(1 << (9*f)))]
        count = run_case(shape, values)
        cases.append({'shape': list(shape), 'kind': 'dirty complete spectators and coefficients', 'steps': count})
        steps += count
    cutoff = (1 << 2048)+17
    count = run_case((1, 1, 1, 1, 3, cutoff), [(1, -1)]*512)
    cases.append({'shape': [1, 1, 1, 1, 3, '2049-bit threshold'], 'kind': 'binary cutoff', 'steps': count})
    steps += count
    rejected = []
    bad = [(0, 0)]*512
    bad[-1] = (1, 0)
    rejected.append(run_case((1, 1, 1, 1, 3, 1), bad, accept=False))
    bad = [(0, 0)]*512
    bad[255], bad[511] = (3, -3), (3, 3)
    rejected.append(run_case((1, 1, 1, 1, 3, 1), bad, accept=False))
    rejected.append(run_case((2, 1, 1, 1, 3, 1), [], accept=False))
    rejected.append(run_case((1, 1, 1, 1, 1, 1), [(0, 0)]*512, accept=False))
    rejected.append(run_case((1, 1, 1, 1, 3, 1), [(0, 0)]*512, accept=False,
                    change=lambda t,o: t[1].cells.pop(o[1]+3071)))
    rejected.append(run_case((1, 1, 1, 1, 3, 1), [(0, 0)]*512, accept=False,
                    change=lambda t,o: t[1].cells.__setitem__(o[1]+3072, '0')))
    reuse = repeated_history()
    print(json.dumps({'status':'PASS_LITERAL_C_AUTHOR_BASE','seed':2026111204,
          'sources':sources,'locations':len(CODE),'tapes':29,'successes':cases,
          'successful_steps':steps,'rejections':len(rejected),'rejected_steps':sum(rejected),
          'repeated_history':reuse,
          'source_sha256':hashlib.sha256((HERE/'leaf.py').read_bytes()).hexdigest(),
          'table_sha256':hashlib.sha256(json.dumps([CODE,ALPHABET],sort_keys=True,separators=(',',':')).encode()).hexdigest(),
          'scope':'Complete physical f=1 packets; f>1 covered separately, not inferred from rank1.'},indent=2,sort_keys=True))


if __name__ == '__main__':
    main()


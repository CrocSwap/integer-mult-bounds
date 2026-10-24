"""Independent complete-stream oracle, physical lifecycle and source controls."""
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import sys
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from machine import Tape, Machine, END, BLANK
from program import compile_program, caller


def check(ok, why):
    if not ok:
        raise RuntimeError(why)


def load_source():
    manifest = json.loads((HERE/'SOURCES.json').read_text())
    for row in manifest['files']:
        check(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'],
              'source drift '+row['path'])
    path = ROOT/'research/a5-eight-bit-carrier/verify.py'
    spec = importlib.util.spec_from_file_location('retained_a5', path)
    source = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(source)
    return source


def make(q, seed):
    rng = random.Random(seed)
    values = [[rng.randrange(2) for _ in range(256*q)] for _ in range(3)]
    data = [Tape(v) for v in values]
    width = Tape([int(b) for b in reversed(bin(q)[2:])]+[END])
    # Arbitrary retained blank tails are part of K0, not erased storage savings.
    for i, tape in enumerate((*data, width)):
        tape.cells.extend([BLANK]*(11+i))
    return values, data, width


def oracle(values, push, u, v, q):
    out = [row[:] for row in values]
    for origin, dest in enumerate(push):
        for lane in range(q):
            change = 0
            for r in range(3):
                if (v >> r) & 1:
                    change ^= values[r][origin*q+lane] ^ values[r][dest*q+lane]
            for r in range(3):
                if (u >> r) & 1:
                    out[r][dest*q+lane] ^= change
    return out


def boundary(m, expected, descriptor, k0, q, closed=False):
    check([t.cells[1:1+256*q] for t in m.data] == expected, 'complete endpoint')
    check(all(all(x == BLANK for x in t.cells[1+256*q:]) for t in m.data), 'data tails')
    check(m.width.cells == descriptor, 'borrowed width bytes')
    check(all(t.head == 1 for t in (*m.data, m.width, *m.private)), 'returned heads')
    check(all(x == BLANK for x in m.output.cells[1:]), 'erased output')
    check(all(x == BLANK for x in m.counter.cells[1:]), 'erased counter')
    if closed:
        check(all(all(x == BLANK for x in t.cells) for t in m.private), 'disposed private markers')
    else:
        check(m.guide.cells == [3]+[1]*q, 'reusable guide')
    total = sum(len(t.cells) for t in (*m.data, m.width, *m.private))
    check(total <= k0+257*q+q.bit_length()+4, 'retained backing bound')


def exercise(source, perms, bases, q, u, v, label, whole=False, seed=192):
    values, data, width = make(q, seed)
    descriptor = width.cells[:]
    k0 = sum(len(t.cells) for t in (*data, width))
    m = Machine(data, width)
    m.setup()
    if whole:
        caller(m, perms, bases)
        # Independent composition of predecessor push actions, not compiler inverse.
        xy = source.matrix_product(source.X, source.Y)
        yx = source.matrix_product(source.Y, source.X)
        expected = [row[:] for row in values]
        for r, matrix in enumerate((xy, yx)):
            for a in range(256):
                dest = source.address_action(matrix, a, 2)
                expected[r][dest*q:(dest+1)*q] = values[r][a*q:(a+1)*q]
    else:
        m.projector(bases[u, v][1], perms[label])
        matrix = source.X if label == 'x' else source.Y
        push = tuple(source.address_action(matrix, i, 2) for i in range(256))
        expected = oracle(values, push, u, v, q)
    boundary(m, expected, descriptor, k0, q)
    m.close()
    boundary(m, expected, descriptor, k0, q, True)
    traffic = sum(t.steps for t in (*data, width, *m.private))
    check(traffic+16*m.control <= (2**25 if whole else 2**23)*(q+1), 'complete loose invoice')
    return {'q': q, 'whole': whole, 'traffic': traffic, 'control': m.control,
            'digest': hashlib.sha256(bytes(sum(expected, []))).hexdigest()}


def rejects(fn):
    try:
        fn()
    except (RuntimeError, ValueError):
        return
    raise RuntimeError('negative control accepted')


def controls(source, perms, bases):
    q = 3
    values, data, width = make(q, 271)
    desc = width.cells[:]
    k0 = sum(len(t.cells) for t in (*data, width))
    expected = oracle(values, tuple(source.address_action(source.Y, i, 2) for i in range(256)), 3, 6, q)
    def mutant(kind):
        _, ds, w = make(q, 271)
        m = Machine(ds, w)
        m.setup()
        word = bases[3, 6][1]
        if kind == 'pull':
            wrong = tuple(source.address_action(source.Y, i, 2) for i in range(256))
            m.projector(word, wrong)
        elif kind == 'omit-mix':
            m.permute(0, perms['y'])
        elif kind == 'omit-inverse':
            m.mix(word)
            m.permute(0, perms['y'])
        else:
            m.projector(word, perms['y'])
            if kind == 'head':m.data[2].move(1)
            if kind == 'dirty-output':m.output.write(1)
            if kind == 'width':m.width.write(0)
        boundary(m, expected, desc, k0, q)
    names = ['pull', 'omit-mix', 'omit-inverse', 'head', 'dirty-output', 'width']
    for name in names:
        rejects(lambda: mutant(name))
    rejects(lambda: Machine([data[0]]*3, width))
    bad = Machine(data, Tape([0, END]))
    rejects(bad.setup)
    m = Machine(data, width)
    m.setup()
    m.close()
    rejects(m.close)
    return len(names)+3


def run():
    source = load_source()
    perms, bases = compile_program(source)
    check(len(bases) == 28, 'all three-role rank-one idempotents')
    results = []
    for u, v in sorted(bases):
        for label in ('x', 'y'):
            results.append(exercise(source, perms, bases, 1, u, v, label, seed=100*u+v))
    for q in (3, 5):
        results.append(exercise(source, perms, bases, q, 3, 6, 'y'))
    for q in (1, 3, 5, 9):
        results.append(exercise(source, perms, bases, q, 0, 0, 'x', whole=True))
    return {'schema_version':1, 'status':'PASS_PHYSICAL_A5_CALLER', 'physical_runs':len(results),
            'projectors':len(bases), 'whole_widths':[1,3,5,9], 'controls':controls(source, perms, bases),
            'traffic_sum':sum(r['traffic'] for r in results),
            'digest':hashlib.sha256(json.dumps(results,sort_keys=True).encode()).hexdigest()}


if __name__ == '__main__':
    result = run()
    if '--write-result' in sys.argv:
        (HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        expected = json.loads((HERE/'RESULT.json').read_text())
        check(json.dumps(expected,sort_keys=True) == json.dumps(result,sort_keys=True), 'typed complete receipt')
    print(json.dumps(result,sort_keys=True))

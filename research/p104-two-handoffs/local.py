"""Replay the credited P104 word and its complete native interfaces.

David Arias supplied the coalesced word. Cinna Davis supplied private reuse.
Gareth Davidson supplied their composition. Ali Romman prepared this caller
with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFIX = 'research/p104-coalesced-private-reuse/'
GEOMETRY = ('research/complex-block-rank-optimum/inputs/selected.json.gz',
            'research/frame-sa504/inputs/hamming/PROTOTYPE.json',
            'research/p104-native-channel/inputs/P104-FIXTURE.json')


def need(ok, why):
    if not ok:
        raise ValueError(why)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def add(dst, src, q):
    for k, v in tuple(src.items()):
        value = dst.get(k, 0) + q*v
        if value:
            dst[k] = value
        else:
            dst.pop(k, None)


def span(basis):
    out = {0}
    for v in basis:
        need(type(v) is int and 0 < v < 512 and v not in out, 'Independent binary basis')
        out |= {x ^ v for x in tuple(out)}
    return frozenset(out)


def construct():
    """Rebuild the published source without its obsolete owner-price engine."""
    manifest = read(ROOT / (PREFIX+'SOURCES.json'))
    archive, = manifest['archives']
    raw = (ROOT / (PREFIX+'predecessor2152.tar.gz')).read_bytes()
    need(sha256(raw).hexdigest() == archive['sha256'], 'Exact predecessor archive')
    pins = {x['path']: x for x in archive['members']}
    with tempfile.TemporaryDirectory(prefix='p104-source-') as tmp:
        root = Path(tmp)
        with tarfile.open(ROOT / (PREFIX+'predecessor2152.tar.gz')) as data:
            members = data.getmembers()
            need(len(members) == len(pins) == 11 and {m.name for m in members} == set(pins), 'Archive inventory')
            for m in members:
                need(m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts, 'Archive file')
                raw = data.extractfile(m).read()
                need(sha256(raw).hexdigest() == pins[m.name]['sha256'], 'Archive member pin')
                path = root/m.name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
        for path in GEOMETRY:
            target = root/path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT/path).read_bytes())
        C = load(root/'research/p104-interleaved-search/coalesced.py', 'productive_p104_coalesced')
        A = load(ROOT/(PREFIX+'compose.py'), 'productive_p104_composition')
        built = A.construct(C, C.construct())
        need(built['report'] == read(ROOT/(PREFIX+'RESULT.json'))['composition'], 'Published complete source report')
        frames, numbers = [], {}
        def frame(basis):
            key = tuple(basis)
            if key not in numbers:
                numbers[key] = len(frames)
                frames.append(list(key))
            return numbers[key]
        initial = [frame(C.F.basis(x)) for x in built['initial']]
        final = [frame(C.F.basis(x)) for x in built['final']]
        live = [r for r in range(112) if len(built['initial'][r]) == 2]
        edges = built['transport_edges']
        program = []
        for e in built['scalar_operations']:
            op = e['kind']
            if op == 'transport':
                edge = edges[e['occurrence']]
                program.append(['MOVE', edge['register'], frame(edge['source_frame']), frame(edge['target_frame']), edge['private']])
            elif op in ('private_init', 'private_discard'):
                program.append(['INIT' if op == 'private_init' else 'CLEAR', e['register'], frame(e['frame'])])
            else:
                program.append([{'add':'ADD', 'scale':'SCALE', 'private_copy':'COPY'}[op], *e['registers'], e['coefficient'], frame(e['frame'])])
        return {'schema':'p104-productive-source/1', 'public':737, 'live':live, 'ports':built['ports'],
                'frames':frames, 'initial':initial, 'final':final, 'program':program}


def replay(w):
    need(len(w['program']) < 26000, 'Fixed operation bound')
    frames = [span(x) for x in w['frames']]
    rows = [{r:Q(1)} for r in range(745)]
    current = list(w['initial']) + [None]*8
    paid, scalar, live_owned, peak = Counter(), 0, set(), 0
    for e in w['program']:
        op, r = e[:2]
        need(0 <= r < 745, 'Role index')
        if op == 'MOVE':
            _, r, a, b, private = e
            need(current[r] == a and (r in live_owned) == private, 'Transport source and ownership')
            need(frames[b] < frames[a] if private else frames[a] < frames[b], 'Nested chronological transport')
            paid[abs(len(w['frames'][b])-len(w['frames'][a]))] += 1
            current[r] = b
        elif op == 'INIT':
            need(r >= 737 and r not in live_owned, 'Owned initialization')
            live_owned.add(r)
            peak = max(peak, len(live_owned))
            rows[r] = {}
            current[r] = e[2]
            scalar += 2
        elif op == 'CLEAR':
            need(r in live_owned and current[r] == e[2], 'Owned erasure at declared frame')
            rows[r] = {}
            current[r] = None
            live_owned.remove(r)
            scalar += 2
        else:
            q, f = Q(e[-2]), e[-1]
            need(q and current[r] == f, 'Scalar destination and coefficient')
            n, d = abs(q.numerator), q.denominator
            need(d & (d-1) == 0, 'Dyadic scalar coefficient')
            need(abs(q)+1 < 2**16, 'Fixed scalar growth bound')
            if op == 'SCALE':
                need(n & (n-1) == 0, 'Dyadic unit SCALE')
                rows[r] = {k:q*x for k,x in rows[r].items()}
                scalar += 2*(abs(n.bit_length()-d.bit_length()) + int(q < 0))
            else:
                s = e[2]
                need(s != r and 0 <= s < 745 and current[s] == f, 'Common scalar chart')
                if op == 'COPY':
                    need(r in live_owned and not rows[r], 'COPY into cleared owned field')
                    rows[r] = {k:q*x for k,x in rows[s].items()}
                else:
                    need(op == 'ADD', 'Scalar opcode')
                    add(rows[r], rows[s], q)
                scalar += 2*(3+n.bit_length()-1+n.bit_count()+d.bit_length()-1)
    need(not live_owned and peak == 1 and current[:737] == w['final'], 'All public and owned exits')
    live = set(w['live'])
    for r,row in enumerate(rows):
        expected = {r:Q(1)} if r < 737 else {}
        if r-112 in live:
            expected[r-112] = Q(1)
        need(row == expected, 'All 745 public and owned rows')
    main = live | {r+112 for r in live}
    helpers = Counter(len(w['frames'][w['final'][r]])-len(w['frames'][w['initial'][r]]) for r in range(737) if r not in main)
    need(len(live) == len(w['ports']) == 104 and len(main) == 208 and min(helpers) > 0, 'Independent productive inputs')
    return {'paid':dict(paid), 'helpers':dict(helpers), 'public_inputs':737, 'owned_lifetimes':8,
            'peak_owned_fields':peak, 'real_scalar_allowance':scalar, 'endpoint_coefficients':745*745}


def reverse_columns(w):
    """Check the transpose with dense dyadic rows and the reverse chronology."""
    n = 745
    rows = [[int(i == j) for j in range(n)] for i in range(n)]
    exponents = [0]*n
    for e in reversed(w['program']):
        op,r = e[:2]
        if op == 'MOVE':
            continue
        if op in ('INIT','CLEAR'):
            rows[r] = [0]*n
            exponents[r] = 0
            continue
        q = Q(e[-2])
        qe = q.denominator.bit_length()-1
        if op == 'SCALE':
            rows[r] = [q.numerator*x for x in rows[r]]
            exponents[r] += qe
        else:
            s = e[2]
            level = max(exponents[s], exponents[r]+qe)
            a, b = 1 << (level-exponents[s]), q.numerator << (level-exponents[r]-qe)
            rows[s] = [a*x+b*y for x,y in zip(rows[s],rows[r])]
            exponents[s] = level
            if op == 'COPY':
                rows[r] = [0]*n
                exponents[r] = 0
            r = s
        while exponents[r] and not any(x & 1 for x in rows[r]):
            rows[r] = [x//2 for x in rows[r]]
            exponents[r] -= 1
    for r,row in enumerate(rows):
        expected = [0]*n
        if r < 737:
            expected[r] = 1 << exponents[r]
        if r in w['live']:
            expected[r+112] = 1 << exponents[r]
        need(row == expected, 'Independent dense transpose columns')
    return {'columns':n, 'coefficients':n*n, 'arithmetic':'Dense integer rows with binary denominators; reverse chronology'}


def native(w):
    C = load(ROOT/'research/p104-native-channel/vendor/clifford_exact.py', 'p104_productive_clifford')
    V = load(ROOT/'research/p104-native-channel/vendor/native_verify.py', 'p104_productive_gaussian')
    @lru_cache(None)
    def chart(i):
        return C.canonical_frame(9, tuple(w['frames'][i]))
    recipes = {}
    def check(a,b):
        if (a,b) not in recipes:
            recipe,_ = C.lower_child(chart(a).adjoint().then(chart(b)))
            expected = V.adjoint(V.frame(w['frames'][a],9)) + V.frame(w['frames'][b],9)
            V.equal(V.recipe(recipe),expected,'Native chart change and exact global phase')
            need(recipe['rank'] == abs(len(w['frames'][a])-len(w['frames'][b])), 'Native boundary rank')
            recipes[a,b] = recipe
        return recipes[a,b]
    for e in w['program']:
        if e[0] == 'MOVE':
            check(e[2],e[3])
    main = set(w['live']) | {r+112 for r in w['live']}
    helper_profile = Counter()
    for r in range(737):
        if r not in main:
            helper_profile[check(w['initial'][r],w['final'][r])['rank']] += 1
    adapters = []
    for r,q in zip(w['live'],w['ports']):
        need(w['frames'][w['initial'][r]] == [q], 'Literal central port')
        need(span(w['frames'][w['final'][r+112]]) == frozenset(x for x in range(512) if not (x&q).bit_count()%2), 'Literal output hyperplane')
        tests = [
            (C.cgate(9,q,1).adjoint().then(chart(w['initial'][r])), V.adjoint((('C',q,1),))+V.frame(w['frames'][w['initial'][r]],9)),
            (chart(w['final'][r+112]).adjoint().then(C.cgate(9,q,-1).then(C.fourier(9))), V.adjoint(V.frame(w['frames'][w['final'][r+112]],9))+(('C',q,-1),)+V.fourier(9))]
        for actual,expected in tests:
            recipe,_ = C.lower_child(actual)
            need(recipe['rank'] == 0, 'Free intrinsic main adapter')
            V.equal(V.recipe(recipe),expected,'Main endpoint phase')
            adapters.append(recipe)
    bad = json.loads(json.dumps(next(iter(recipes.values()))))
    bad['left']['phase'] = (bad['left']['phase']+1)%4
    a,b = next(iter(recipes))
    try:
        V.equal(V.recipe(bad),V.adjoint(V.frame(w['frames'][a],9))+V.frame(w['frames'][b],9),'Wrong phase control')
    except ValueError:
        pass
    else:
        raise ValueError('Wrong native phase accepted')
    payload = [[a,b,recipes[a,b]] for a,b in sorted(recipes)] + adapters
    return {'distinct_maps':len(recipes),'main_adapters':len(adapters),'helper_normalizers':2*sum(helper_profile.values()),
            'helpers':dict(helper_profile),'recipe_payload_sha256':sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            'wrong_phase_rejected':True, 'proof':'Every signed Pauli image and exact global phase; frame induction at every positive tensor width'}

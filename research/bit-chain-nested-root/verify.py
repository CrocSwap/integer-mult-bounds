#!/usr/bin/env python3
"""Exact checks for the chain-nested root caller on the retained BIT native word.  Python 3.12, standard library only.

Run:  python3 -B research/bit-chain-nested-root/verify.py        (add --write to regenerate the committed data files)
Expected marker: PASS_BIT_CHAIN_NESTED_ROOT

Checks (failures raise ValueError, so they stay active under -O):
  0. retained input bytes against retained/SOURCE-PINS.json (SHA-256 and Git blob ids)
  1. the complex caller is rebuilt and equals the committed word; its coefficients are integral (all SCALE +-1,
     ADD integers), forward-replayed over Z[i][q,D]/(q^4-1) with the ordinary normalisations (400 coefficients)
  2. the binary word is derived from it (drop normalisations, odd ADD -> XOR, even ADD -> nothing, SCALE +-1 -> identity)
     and equals the committed word
  3. three independent coefficient engines: forward over F2 with stage monomials; forward over Z[q,D]/(q^2-1)
     with the normalisations removed; the retained reverse audit (400 coefficients each)
  4. the retained BIT native word (SHA-256 51203e7f...) is audited by the retained source audit; complete invoice
  5. raw crossing: interval engine of the retained module and an independent Decimal engine; finite admission
     (retained compiler certificate, tail ratios, ordinary work, owned bank) at the tested saving
  6. the earlier caller cannot fund the new claim; controls
"""
import gzip, hashlib, importlib.util, json, sys
from collections import Counter
from decimal import Decimal as Dec, getcontext
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import chainroot  # noqa: E402

BIT = HERE / 'retained/pr6726/bit'
SOURCE_SHA = '51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78'
RAW = Q('.0038525'); GAP = Q(1, 10**10); ADMITTED = Q('.00385248')
LOW, HIGH = Q('.0038525393934'), Q('.0038525393935')
STEPS = (Q('.00385'), ADMITTED)
ATOM = Q('.004'); PREVIOUS = Q('.00374998')


def need(ok, msg):
    if not ok:
        raise ValueError(msg)


def load(path, name):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


def gz(path):
    return json.loads(gzip.decompress(Path(path).read_bytes()))


def dump(w):
    return gzip.compress(json.dumps(w, separators=(',', ':')).encode(), mtime=0)


# ---------------------------------------------------------------------------------------------- 0 pins
def check_pins():
    pins = json.loads((HERE / 'retained/SOURCE-PINS.json').read_text())
    for p in pins:
        data = (HERE / p['local']).read_bytes()
        need(len(data) == p['bytes'], ('size', p['local']))
        need(hashlib.sha256(data).hexdigest() == p['sha256'], ('sha256', p['local']))
        need(hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest() == p['git_blob'], ('git blob', p['local']))
    need(hashlib.sha256((BIT / 'inputs/BIT-NATIVE-WORD.json.gz').read_bytes()).hexdigest() == SOURCE_SHA, 'Exact native source')
    return len(pins)


# ------------------------------------------------------------------ 1 complex word, Z[i] engine with normalisations
def complex_forward(w):
    n, wd = w['roles'], w['stages'] + 2; zero = (0,) * wd
    Z0 = (Q(0), Q(0))

    def zmul(a, b): return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]

    def acc(dst, src, c=(Q(1), Q(0))):
        for k, v in src.items():
            t = zmul(c, v); o = dst.get(k, Z0); t = (o[0]+t[0], o[1]+t[1])
            if t != Z0: dst[k] = t
            else: dst.pop(k, None)

    def sh(row, term):
        out = []
        for cell in row:
            d = {}
            for k, v in cell.items():
                acc(d, {((k[0]+term[0]) % 4,)+tuple(a+b for a, b in zip(k[1:], term[1:])): v})
            out.append(d)
        return out
    rows = [[{zero: (Q(1), Q(0))} if i == j else {} for j in range(n)] for i in range(n)]; seen = []
    for e in w['events']:
        op = e[0]
        if op == 'ADD':
            for a, b in zip(rows[e[1]], rows[e[2]]): acc(a, b, (Q(e[3]), Q(0)))
        elif op == 'SCALE':
            c = (Q(e[2]), Q(0)); rows[e[1]] = [{k: zmul(c, v) for k, v in cell.items()} for cell in rows[e[1]]]
        elif op == 'SWAP': rows[e[1]], rows[e[2]] = rows[e[2]], rows[e[1]]
        elif op in ('LOCAL', 'QUERY'):
            if op == 'LOCAL': _, st, src, dst = e; ex = -1; seen.append(st)
            else: _, dst, src, ex = e
            for a, b in zip(rows[dst], sh(rows[src], (ex,)+(0,)*(wd-1))): acc(a, b)
            if op == 'LOCAL':
                term = (0,)+tuple(int(s == st) for s in range(wd-1))
                for r in (src, dst): rows[r] = sh(rows[r], term)
        elif op == 'LAMBDA':
            _, r, sign = e; need(sign in (-1, 1), 'normalisation sign')
            old = rows[r]; other = sh(old, (2,)+(0,)*(wd-1)); rows[r] = [{} for _ in range(n)]
            for dst, a, b in zip(rows[r], old, other):
                acc(dst, a, (Q(1, 2), Q(sign, 2))); acc(dst, b, (Q(1, 2), Q(-sign, 2)))
        elif op == 'IDLE_ONE':
            term = (0,)+tuple(int(s in e[2]) for s in range(wd-1)); rows[e[1]] = sh(rows[e[1]], term)
        else: raise ValueError('opcode ' + op)
    need(sorted(seen) == list(range(1, w['stages']+1)), 'every native stage once')
    for i, d in enumerate(w['diagonal']):
        key = (d[0] % 4,)+tuple(d[1:])
        for j in range(n):
            need(rows[i][j] == ({key: (Q(1), Q(0))} if i == j else {}), ('complex coefficient', i, j))
    return n*n


def integrality(w):
    for e in w['events']:
        if e[0] in ('SCALE', 'ADD'):
            v = Q(e[-1]); need(v.denominator == 1, 'integral coefficient')
            if e[0] == 'SCALE': need(abs(v) == 1, 'unimodular scaling')
        elif e[0] not in ('SWAP', 'LAMBDA', 'LOCAL', 'QUERY', 'IDLE_ONE'): raise ValueError('opcode ' + e[0])


def to_binary(c):
    integrality(c); ev = []
    for e in c['events']:
        op = e[0]
        if op == 'LAMBDA': continue
        if op == 'SCALE': continue
        if op == 'ADD':
            if int(Q(e[3])) % 2: ev.append(e[:3])
        elif op == 'QUERY': need(e[3] in (-1, 1), 'central involution query'); ev.append(e[:3])
        else: ev.append(e)
    return {'schema': 'binary-chain-nested-root/1', 'roles': c['roles'], 'stages': c['stages'], 'events': ev,
            'diagonal': [{'q': d[0] % 2, 'stages': [s for s, x in enumerate(d[2:], 1) if x]} for d in c['diagonal']]}


# ----------------------------------------------------------------------------------------- 3 engines
def f2_forward(w):
    n, wd = w['roles'], w['stages']+1; zero = (0,)*wd
    rows = [[{zero} if i == j else set() for j in range(n)] for i in range(n)]

    def shift(row, ss=(), q=0):
        out = []
        for cell in row:
            cc = set()
            for key in cell:
                k = list(key); k[0] ^= q
                for s in ss: k[s] += 1
                z = tuple(k)
                if z in cc: cc.remove(z)
                else: cc.add(z)
            out.append(cc)
        return out
    seen = []
    for e in w['events']:
        op = e[0]
        if op == 'ADD': rows[e[1]] = [x ^ y for x, y in zip(rows[e[1]], rows[e[2]])]
        elif op == 'SWAP': rows[e[1]], rows[e[2]] = rows[e[2]], rows[e[1]]
        elif op in ('LOCAL', 'QUERY'):
            if op == 'LOCAL': _, s, src, dst = e; seen.append(s)
            else: _, dst, src = e
            rows[dst] = [x ^ y for x, y in zip(rows[dst], shift(rows[src], q=1))]
            if op == 'LOCAL': rows[src] = shift(rows[src], [s]); rows[dst] = shift(rows[dst], [s])
        elif op == 'IDLE_ONE': rows[e[1]] = shift(rows[e[1]], e[2])
        else: raise ValueError(op)
    need(sorted(seen) == list(range(1, wd)), 'All native stages once')
    for i, d in enumerate(w['diagonal']):
        key = (d['q'],)+tuple(int(s in d['stages']) for s in range(1, wd))
        for j in range(n): need(rows[i][j] == ({key} if i == j else set()), ('F2 coefficient', i, j))
    return n*n


def z_forward(c):
    """Integer engine over Z[q,D1..D18]/(q^2-1): the complex word with normalisations removed (q^2=1 makes each one 1)."""
    n, wd = c['roles'], c['stages']+1; zero = (0,)*wd
    rows = [[{zero: 1} if i == j else {} for j in range(n)] for i in range(n)]

    def sh(row, ss=(), q=0):
        out = []
        for cell in row:
            d = {}
            for k, v in cell.items():
                k = list(k); k[0] ^= q
                for s in ss: k[s] += 1
                d[tuple(k)] = v
            out.append(d)
        return out

    def acc(a, b, m):
        for k, v in b.items():
            a[k] = a.get(k, 0)+m*v
            if a[k] == 0: del a[k]
    seen = []
    for e in c['events']:
        op = e[0]
        if op == 'ADD':
            for a, b in zip(rows[e[1]], rows[e[2]]): acc(a, b, int(Q(e[3])))
        elif op == 'SCALE':
            m = int(Q(e[2])); need(abs(m) == 1, 'unit scale'); rows[e[1]] = [{k: v*m for k, v in cell.items()} for cell in rows[e[1]]]
        elif op == 'SWAP': rows[e[1]], rows[e[2]] = rows[e[2]], rows[e[1]]
        elif op in ('LOCAL', 'QUERY'):
            if op == 'LOCAL': _, s, src, dst = e; seen.append(s)
            else: _, dst, src, _x = e
            for a, b in zip(rows[dst], sh(rows[src], q=1)): acc(a, b, 1)
            if op == 'LOCAL': rows[src] = sh(rows[src], [s]); rows[dst] = sh(rows[dst], [s])
        elif op == 'LAMBDA': pass
        elif op == 'IDLE_ONE': rows[e[1]] = sh(rows[e[1]], e[2])
    need(sorted(seen) == list(range(1, wd)), 'All native stages once')
    for i, d in enumerate(c['diagonal']):
        key = (d[0] % 2,)+tuple(d[1+s] for s in range(1, wd))
        for j in range(n): need(rows[i][j] == ({key: 1} if i == j else {}), ('Z coefficient', i, j))
    return n*n


# ---------------------------------------------------------------------------------------- main
def main():
    OUT = {}
    OUT['retained_inputs'] = check_pins()
    cw = chainroot.build([1]*9, [1]*9)
    stored = gz(HERE / 'CALLER-COMPLEX.json.gz')
    need(cw == stored, 'Rebuilt complex caller equals the committed caller')
    OUT['complex_events'] = len(cw['events'])
    OUT['complex_coefficients'] = complex_forward(cw)
    bw = to_binary(cw)
    need(bw == gz(HERE / 'CALLER-BINARY.json.gz'), 'Derived binary caller equals the committed caller')
    ops = Counter(e[0] for e in bw['events'])
    need((bw['roles'], bw['stages'], len(bw['events'])) == (20, 18, 670), 'census')
    OUT['binary_events'] = dict(ops)
    OUT['f2_forward_coefficients'] = f2_forward(bw)
    OUT['integer_forward_coefficients'] = z_forward(cw)
    audit = load(BIT / 'audit_binary_mixed.py', 'chain_audit')
    OUT['reverse_coefficients'] = audit.backward(bw)
    need(OUT['f2_forward_coefficients'] == OUT['integer_forward_coefficients'] == OUT['reverse_coefficients'] == 400, 'engines agree')
    p0, t0, source = audit.source_audit(gz(BIT / 'inputs/BIT-NATIVE-WORD.json.gz'))
    P = Counter({r: 18*c for r, c in p0.items()}); T = Counter({r: 18*c for r, c in t0.items()})
    for e in bw['events']:
        if e[0] == 'QUERY': P[1] += 111
        elif e[0] == 'IDLE_ONE': P[7*len(e[2])] += 111
    for d in bw['diagonal']: T[d['q']+7*len(d['stages'])] += 111
    mass = sum(r*v for r, v in T.items())-sum(r*v for r, v in P.items())
    OUT.update(productive_fields=sum(T.values()), paid_jobs=sum(P.values()), rank_mass_surplus=mass)
    need(mass > 0, 'No invented rank mass')
    # crossing, retained interval engine
    I = load(BIT / 'inputs/independent_interval.py', 'chain_interval')
    from functools import lru_cache

    @lru_cache(None)
    def power(r, t):
        lo, hi = I.power(r, t); s = 10**65
        return Q((lo*s).__floor__(), s), Q(-((-hi*s).__floor__()), s)

    def moment(h, t):
        lo = hi = Q(0)
        for r, n in h.items():
            x, y = power(r, t); lo += n*x; hi += n*y
        return lo, hi

    def margin(k, targets=T, paid=P):
        tt, pp = moment(targets, 1-k), moment(paid, 1-k); return tt[0]-pp[1], tt[1]-pp[0]
    need(margin(LOW)[0] > 0 and margin(HIGH)[1] < 0, 'Interval engine crossing bracket')
    # crossing, independent Decimal engine
    getcontext().prec = 60

    def f(k):
        k = Dec(k.numerator)/Dec(k.denominator)
        return sum((T.get(r, 0)-P.get(r, 0))*((1-k)*Dec(r).ln()).exp() for r in set(T)|set(P))
    need(f(LOW) > 0 and f(HIGH) < 0, 'Decimal engine crossing bracket')
    need(margin(RAW)[0] > 0 and f(RAW) > 0, 'Tested saving has strict margin')
    old = json.loads((BIT / 'RETIRED-BIT-ADMISSION.json').read_text())
    need(Q(old['ordinary_admitted']) == PREVIOUS, 'Previous qualified BIT ordinary result')
    need(margin(RAW, {int(k): v for k, v in old['targets'].items()}, {int(k): v for k, v in old['paid'].items()})[1] < 0, 'Earlier retired caller cannot fund the claim')
    prev = json.loads((BIT / 'FRAGMENT-BIT-ADMISSION.json').read_text())
    need(margin(RAW, {int(k): v for k, v in prev['targets'].items()}, {int(k): v for k, v in prev['paid'].items()})[1] < 0, 'Two-fragment caller cannot fund the claim')
    # finite admission
    C = load(BIT / 'inputs/credited_trim.py', 'chain_finite')
    cert = C.certificate(T, P, RAW, 768, 15, 16, Q(1, 5), Q(1, 5), uniform_gap=GAP, label='binary_chain_nested_root',
                         source_status='Literal 670-event integral-reduction caller; 400 forward and reverse coefficients; unchanged inherited all-width native theorem')
    t = 1-RAW; tt = moment(T, t); u = Q(1, 5)
    ratios = (I.div(moment(P, t), tt), I.div(moment(P, t+u), I.mul(power(15, u), tt)), I.div(I.mul(power(16, u), moment(T, t-u)), tt))
    limits = list(map(Q, cert['rational_upper_limits']))
    for r, b in zip(ratios, limits): need(0 < r[0] <= r[1] <= b < 1, 'Second engine finite tail bound')
    aa, gg, ll = limits; norm = 1/(1+768*(1-aa))+2*gg**768+ll**768
    need(norm < 1, 'Discarded targets and paid splits funded')
    comp = cert['uniform_compiler']; thr = comp['H']; p = comp['logarithm_power']; ex = comp['integer_test_exponent']
    need(thr == GAP.denominator*ex and (thr+1)**p < 2**ex, 'Uniform integer threshold')
    need(not (GAP.denominator*(ex-1)+1)**p < 2**(ex-1), 'Preceding compiler grid rejects')
    n = 111; m = bw['roles']; F = 18; thin = ops['QUERY']; idles = ops['IDLE_ONE']; h = 127
    basis = n*8*(ops['ADD']+3*ops['SWAP']); visible = F*10**7+basis+256*n*(F+thin+m)
    route_per = 8*(10*h*h+10*h); route_count = 4*(sum(P.values())+sum(T.values()))+8*n*F+8*n*idles; routes = route_per*route_count
    owned = F*source['owned_labels']+2*n*m*len(bw['events'])+16*n*(F+thin+m)
    need(visible+routes < 10**12 and owned < 10**7, 'Ordinary work and storage funded')
    prev_s = PREVIOUS; covered = RAW-2*GAP; boot = []
    for adm in STEPS:
        env = (1-ATOM)*covered+ATOM*prev_s
        need(ATOM > env > adm > prev_s and ATOM < 1-env, 'Ordinary wrapper envelope')
        boot.append(dict(previous=str(prev_s), covered=str(covered), atom=str(ATOM), envelope=str(env), admitted=str(adm), strict_debit=str(env-adm))); prev_s = adm
    OUT.update(visible_records=visible, route_records=routes, owned_bank_bound=owned, wrapper=boot)
    # controls
    neg = {}

    def reject(label, fn):
        try: fn()
        except ValueError as e: neg[label] = str(e)[:70]; return
        raise ValueError('control accepted: ' + label)
    for label, at in (('missing_input_basis', 0), ('missing_output_basis', len(bw['events'])-1)):
        bad = json.loads(json.dumps(bw)); del bad['events'][at]; reject(label, lambda b=bad: audit.backward(b))
    for op in ('LOCAL', 'QUERY', 'IDLE_ONE'):
        bad = json.loads(json.dumps(bw)); del bad['events'][next(i for i, e in enumerate(bad['events']) if e[0] == op)]
        reject('missing_' + op, lambda b=bad: audit.backward(b)); reject('missing_' + op + '_f2', lambda b=bad: f2_forward(b))
    bad = json.loads(json.dumps(bw)); i = next(i for i, e in enumerate(bad['events']) if e[0] == 'IDLE_ONE'); bad['events'][i][2] = bad['events'][i][2][:-1]
    reject('shrunk_idle', lambda: f2_forward(bad))
    i = next(i for i, e in enumerate(cw['events']) if e[0] == 'ADD' and int(Q(e[3])) % 2 == 0)
    bad = json.loads(json.dumps(bw)); bad['events'].insert(len(bad['events'])//2, ['ADD', 3, 5]); reject('stray_xor', lambda: f2_forward(bad))
    bad = json.loads(json.dumps(cw)); del bad['events'][next(i for i, e in enumerate(bad['events']) if e[0] == 'LAMBDA')]; reject('missing_LAMBDA', lambda: complex_forward(bad))
    bad = json.loads(json.dumps(cw)); del bad['events'][i]; reject('missing_even_ADD_integer_engine', lambda: z_forward(bad))
    dy = chainroot.build([1]*9, [1]*9, dyadic=True); complex_forward(dy); reject('dyadic_basis_not_integral', lambda: to_binary(dy))
    need(tt[0] > 0, 'positive productive moment')
    low_raw = Q('.00385254'); need(margin(low_raw)[1] < 0, 'A saving above the crossing is unfunded')
    reject('saving_above_crossing', lambda: need(margin(low_raw)[0] > 0, 'unfunded above crossing'))
    OUT['negative_controls'] = neg
    result = dict(status='PASS_BIT_CHAIN_NESTED_ROOT', ordinary_admitted=str(ADMITTED), previous_ordinary=str(PREVIOUS), raw_tested=str(RAW),
                  raw_crossing=[str(LOW), str(HIGH)], caller_complex_sha256=hashlib.sha256((HERE/'CALLER-COMPLEX.json.gz').read_bytes()).hexdigest(),
                  caller_binary_sha256=hashlib.sha256((HERE/'CALLER-BINARY.json.gz').read_bytes()).hexdigest(), native_source_sha256=SOURCE_SHA,
                  paid=dict(sorted(P.items())), targets=dict(sorted(T.items())), finite_admission=cert, details=OUT,
                  assumptions=['native_all_columns', 'owned_erasure', 'compiler', 'precision_tape', 'analytic_recovery'],
                  scope='BIT dependency bound only; no overall kappa claim.')
    text = json.dumps(result, indent=1, default=str, sort_keys=True)+'\n'
    target = HERE / 'BIT-CHAIN-ADMISSION.json'
    if '--write' in sys.argv: target.write_text(text)
    else: need(target.read_text() == text, 'Committed admission record reproduced exactly')
    print('PASS_BIT_CHAIN_NESTED_ROOT'); print(json.dumps({k: OUT[k] for k in OUT if k not in ('wrapper', 'negative_controls')}, default=str))


if __name__ == '__main__':
    main()

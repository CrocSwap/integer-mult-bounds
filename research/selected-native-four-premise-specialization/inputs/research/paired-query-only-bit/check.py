#!/usr/bin/env python3
"""Paired E-free BIT specialization and complete conditional accounting.
Only the E-free caller is emitted. Apache-2.0.
Source authors retained in NOTICE and SOURCES. OpenAI Codex assistance.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from functools import lru_cache
import gzip, hashlib, importlib.util, json, time, sys
H = Path(__file__).resolve().parent
RAW = Q('.00385253')
GAP = Q(1, 10 ** 10)

def need(ok, msg):
    if not ok:
        raise ValueError(msg)

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def encode(x):
    if isinstance(x, Q):
        return str(x)
    if isinstance(x, dict):
        return {str(k): encode(v) for k, v in x.items()}
    if isinstance(x, (tuple, list)):
        return [encode(v) for v in x]
    return x

def authenticate():
    manifest = json.loads((H / 'INPUT-PINS.json').read_text())
    for f in manifest['files']:
        if 'local' not in f:
            continue
        need(hashlib.sha256((H / f['local']).read_bytes()).hexdigest() == f['sha256'], 'source hash ' + f['local'])
    return manifest

def construct_efree(c=None):
    """Specialize #6980's type-A QUERY-only pair; instantiate111 pairs.
 Each of18 body stages executes TWO actual111-port native calls. First
 call handles the first shear in every pair, second the other shear.
 Their body axes agree, but inputs, helpers and owned lifetimes are distinct.
 """
    c = json.loads((H / 'data/query_only_6980.json').read_text()) if c is None else c
    events = []
    discarded = Counter()
    need((c['roles'], c['stages'], c['types']['A']['roles'], c['types']['A']['alpha2']) == (76, 18, 38, '-1'), 'exact #6980 paired interface')
    for e in c['events']:
        if e[0] == 'J':
            _, s, (src, dst, x2, y2), other = e
            need(len({src, dst, x2, y2}) == 4 and all((0 <= r < 38 for r in (src, dst, x2, y2))), 'two disjoint native shears')
            events += [['LOCAL', s, src, dst], ['LOCAL', s, y2, x2]]
            continue
        tag, op, *a = e
        roles = a[:2] if op in ('ADD', 'SWAP', 'QUERY') else a[:1]
        if tag == 'B':
            need(all((38 <= r < 76 for r in roles)), 'B support disjoint')
            discarded[op] += 1
            continue
        need(tag == 'A' and all((0 <= r < 38 for r in roles)), 'only A support')
        if op == 'LAMBDA':
            need(a[1] in (-1, 1), 'lambda becomes1 before mod2')
        elif op == 'SCALE':
            need(Q(a[1]) in (-1, 1), 'integral unit')
        elif op == 'ADD':
            v = Q(a[2])
            need(v.denominator == 1, 'integral A coefficient after lambda removal')
            if v.numerator % 2:
                events.append(['ADD', *a[:2]])
        elif op == 'QUERY':
            need(a[2] in (-1, 1), 'central involution')
            events.append(['QUERY', *a[:2]])
        elif op in ('SWAP', 'IDLE_ONE'):
            events.append([op, *a])
        else:
            raise ValueError('unimplemented A opcode ' + op)
    diagonal = [{'q': d[0] % 2, 'stages': [j + 1 for j, x in enumerate(d[2:]) if x]} for d in c['types']['A']['diagonal']]
    need(len(diagonal) == 38 and all((d['stages'] for d in diagonal)), 'all root targets have nonempty body masks')
    return (dict(schema='paired-efree-bit/1', roles=38, stages=18, ports=111, native_per_stage=2, body_rank=7, ambient_rank=127, events=events, diagonal=diagonal), dict(discarded))

def parity_certificate():
    """Finite algebra fixtures for the determinant argument in PROOF.md."""

    def mul(a, b):
        return (a & 1) * (b & 1) ^ (a >> 1 & 1) * (b >> 1 & 1) | ((a & 1) * (b >> 1 & 1) ^ (a >> 1 & 1) * (b & 1)) << 1

    def power(a, n):
        out = 1
        for _ in range(n):
            out = mul(out, a)
        return out

    def det2(a, b, c, d):
        return mul(a, d) ^ mul(b, c)
    need(mul(2, 2) == 1 and 2 != 1, 'formal q is an involution distinct from1')
    need(det2(1, 2, 0, 1) == det2(1, 1, 0, 1) == det2(0, 1, 1, 0) == 1, 'QUERY,ADD,SWAP determinants1')
    need(power(2, 19 * 111) == 2 and power(2, 19 * 222) == 1, 'odd root target determinant obstruction; doubled target passes')
    need(det2(2, 0, 0, 1) == 2, 'QSELF changes the excluded determinant')
    return {'ring': 'F2[q]/(q^2-1)', 'q_ne_1': True, 'single_layer_root_targets': 19 * 111, 'single_layer_target_determinant': 'q', 'allowed_D1_gate_determinants': '1', 'doubled_root_targets': 19 * 222, 'doubled_target_determinant': '1', 'scope': 'Fixed19q-targets per chain,111ports,existing scalar caller operations; no extra target or QSELF/owned operator. Not a general obstruction on BIT algorithms.'}

def forward(w, collapse_header=False):
    n = w['roles']
    width = w['stages'] + 1
    zero = (0,) * width
    rows = [[{zero} if i == j else set() for j in range(n)] for i in range(n)]

    def shift(row, ss=(), q=0):
        out = []
        for cell in row:
            cc = set()
            for key in cell:
                k = list(key)
                k[0] = 0 if collapse_header else k[0] ^ q
                for s in ss:
                    k[s] += 1
                z = tuple(k)
                if z in cc:
                    cc.remove(z)
                else:
                    cc.add(z)
            out.append(cc)
        return out
    seen = []
    for e in w['events']:
        op = e[0]
        if op == 'ADD':
            _, a, b = e
            rows[a] = [x ^ y for x, y in zip(rows[a], rows[b])]
        elif op == 'SWAP':
            _, a, b = e
            rows[a], rows[b] = (rows[b], rows[a])
        elif op in ('LOCAL', 'QUERY'):
            if op == 'LOCAL':
                _, s, src, dst = e
                seen.append(s)
            else:
                _, dst, src = e
            rows[dst] = [x ^ y for x, y in zip(rows[dst], shift(rows[src], q=1))]
            if op == 'LOCAL':
                rows[src] = shift(rows[src], [s])
                rows[dst] = shift(rows[dst], [s])
        elif op == 'IDLE_ONE':
            _, a, ss = e
            need(len(ss) == len(set(ss)), 'fresh idle axes')
            rows[a] = shift(rows[a], ss)
        else:
            raise ValueError(op)
    need(sorted(seen) == [s for s in range(1, width) for _ in range(w.get('native_per_stage', 1))], 'every real native occurrence counted')
    for i, d in enumerate(w['diagonal']):
        key = (0 if collapse_header else d['q'],) + tuple((int(s in d['stages']) for s in range(1, width)))
        for j in range(n):
            need(rows[i][j] == ({key} if i == j else set()), f'forward coefficient {i},{j}')
    return n * n

def main():
    started = time.monotonic()
    write_artifacts = '--write' in sys.argv
    manifest = authenticate()
    efree = True
    w, discarded = construct_efree()
    forward_count = forward(w)
    F = 36
    scale = 2
    root_thin = 4
    prior_chain = json.loads((H / 'data/6834_result.json').read_text())
    claim = Q(prior_chain['ordinary_admitted'])
    need(claim == Q('.00385248'), 'retain existing #6834 saving')
    audit = load(H / 'retained/audit_binary_mixed.py', 'retained_audit')
    reverse_count = audit.backward(w)
    sourceblob = (H / 'retained/inputs/BIT-NATIVE-WORD.json.gz').read_bytes()
    p0, t0, source = audit.source_audit(json.loads(gzip.decompress(sourceblob)))
    need(hashlib.sha256(sourceblob).hexdigest() == prior_chain['native_source_sha256'], 'same actual native as #6834')
    P = Counter({r: F * c for r, c in p0.items()})
    T = Counter({r: F * c for r, c in t0.items()})
    for e in w['events']:
        if e[0] == 'QUERY':
            P[1] += 111
        elif e[0] == 'IDLE_ONE':
            P[7 * len(e[2])] += 111
    for d in w['diagonal']:
        T[d['q'] + 7 * len(d['stages'])] += 111
    expectedP = Counter({r: F * c for r, c in p0.items()})
    expectedP[1] += root_thin * 111
    for size in range(1, 9):
        expectedP[7 * size] += scale * 222
    expectedT = Counter({r: F * c for r, c in t0.items()})
    expectedT[127] += scale * 111
    if not True:
        expectedT[1] += 111
    for size in range(1, 10):
        expectedT[1 + 7 * size] += scale * 222
    need(T == expectedT and P == expectedP, 'independent closed-form actual-source invoice')
    need(sum((r * v for r, v in T.items())) - sum((r * v for r, v in P.items())) == scale * 753, 'no invented rank mass')
    baseline = prior_chain
    for current, oldhist in ((T, baseline['targets']), (P, baseline['paid'])):
        scaled = Counter({int(r): 2 * v for r, v in oldhist.items()})
        scaled[1] -= 222
        scaled = Counter({r: v for r, v in scaled.items() if v})
        need(current == scaled, 'all-rank identity: twice original profile minus222 rank1 jobs')
    negative = {}
    for op in ('LOCAL', 'QUERY', 'IDLE_ONE', 'ADD', 'SWAP'):
        bad = json.loads(json.dumps(w))
        del bad['events'][next((i for i, e in enumerate(bad['events']) if e[0] == op))]
        try:
            audit.backward(bad)
        except ValueError as e:
            negative['missing_' + op] = str(e)
        else:
            raise ValueError('corruption accepted: ' + op)
    bad = json.loads(json.dumps(w))
    at = [i for i, e in enumerate(bad['events']) if e[0] == 'LOCAL'][1]
    del bad['events'][at]
    try:
        audit.backward(bad)
    except ValueError as e:
        negative['missing_second_native_in_pair'] = str(e)
    else:
        raise ValueError('free second native accepted')
    bad = json.loads((H / 'data/query_only_6980.json').read_text())
    at = next((i for i, e in enumerate(bad['events']) if e[:2] == ['A', 'ADD']))
    bad['events'][at][-1] = '1/2'
    try:
        construct_efree(bad)
    except ValueError as e:
        negative['division_by2_after_specialization'] = str(e)
    else:
        raise ValueError('illegal mod2 coefficient accepted')
    parity = parity_certificate()
    bad = json.loads(json.dumps(w))
    at = next((i for i, e in enumerate(bad['events']) if e[0] == 'QUERY'))
    bad['events'][at][0] = 'ADD'
    need(forward(bad, collapse_header=True) == w['roles'] ** 2, 'q=1 specialization is blind to QUERY replaced by ADD')
    try:
        audit.backward(bad)
    except ValueError as e:
        negative['QUERY_replaced_by_ADD_despite_q1_pass'] = str(e)
    else:
        raise ValueError('formal involution corruption accepted')
    bad = json.loads(json.dumps(w))
    bad['diagonal'][19]['q'] = 0
    try:
        audit.backward(bad)
    except ValueError as e:
        negative['root_header_target_declared_identity'] = str(e)
    else:
        raise ValueError('root header work silently dropped')
    need(all((d['stages'] for d in w['diagonal'])) and 1 not in T, 'no empty root and no productive rank1 credit')
    C = load(H / 'retained/inputs/credited_trim.py', 'finite_compiler')
    I = load(H / 'retained/inputs/independent_interval.py', 'independent_interval')
    cert = C.certificate(T, P, RAW, 768, 15, 16, Q(1, 5), Q(1, 5), uniform_gap=GAP, label='paired_efree_bit', source_status=f"Integral caller with{w['roles']}independent roles; unchanged #6726 BIT native111 ports per actual call; {F}actual calls; all{w['roles'] ** 2}forward and reverse coefficients")

    @lru_cache(None)
    def power(r, t):
        lo, hi = I.power(r, t)
        s = 10 ** 65
        return (Q((lo * s).__floor__(), s), Q(-(-hi * s).__floor__(), s))

    def moment(hist, t):
        lo = hi = Q(0)
        for r, n in hist.items():
            x, y = power(r, t)
            lo += n * x
            hi += n * y
        return (lo, hi)

    def margin(k, targets=T, paid=P):
        tt, pp = (moment(targets, 1 - k), moment(paid, 1 - k))
        return (tt[0] - pp[1], tt[1] - pp[0])
    low, high = (Q('.0038525393934'), Q('.0038525393935'))
    need(margin(low)[0] > 0 and margin(high)[1] < 0, 'independent crossing bracket')
    need(margin(RAW)[0] > 0, 'strict raw saving')
    t = 1 - RAW
    tt = moment(T, t)
    u = Q(1, 5)
    ratios = (I.div(moment(P, t), tt), I.div(moment(P, t + u), I.mul(power(15, u), tt)), I.div(I.mul(power(16, u), moment(T, t - u)), tt))
    limits = list(map(Q, cert['rational_upper_limits']))
    for r, bound in zip(ratios, limits):
        need(0 < r[0] <= r[1] <= bound < 1, 'independent finite tail bound')
    aa, gg, ll = limits
    norm = 1 / (1 + 768 * (1 - aa)) + 2 * gg ** 768 + ll ** 768
    need(norm < 1, 'all discarded targets and paid splits funded')
    compiler = cert['uniform_compiler']
    threshold = compiler['H']
    p = compiler['logarithm_power']
    e = compiler['integer_test_exponent']
    need(threshold == GAP.denominator * e and (threshold + 1) ** p < 2 ** e, 'independent uniform integer threshold')
    need(not (GAP.denominator * (e - 1) + 1) ** p < 2 ** (e - 1), 'previous compiler grid rejected')
    ops = Counter((e[0] for e in w['events']))
    n, m, h = (111, w['roles'], 127)
    thin = ops['QUERY']
    idles = ops['IDLE_ONE']
    basis = n * 8 * (ops['ADD'] + 3 * ops['SWAP'])
    visible = F * 10 ** 7 + basis + 256 * n * (F + thin + m)
    route_per = 8 * (10 * h * h + 10 * h)
    route_count = 4 * (sum(P.values()) + sum(T.values())) + 8 * n * F + 8 * n * idles
    routes = route_per * route_count
    owned = F * source['owned_labels'] + 2 * n * m * len(w['events']) + 16 * n * (F + thin + m)
    need(visible + routes < 10 ** 12 and owned < 10 ** 7, 'all ordinary work and storage funded')
    selected = json.loads((H / 'data/selected_claim.json').read_text())
    record = json.loads((H / 'data/selected_record.json').read_text())
    need(hashlib.sha256((H / 'data/selected_claim.json').read_bytes()).hexdigest() == record['certificate_sha256'], 'selected BIT bootstrap certificate binding')
    seed = Q(selected['admitted_BIT_saving'])
    need(seed == Q('17/5000'), 'source-backed ordinary bootstrap')
    previous = seed
    covered = RAW - 2 * GAP
    atom = Q('.004')
    stages = []
    for admitted in (Q('.0038507'), claim):
        envelope = (1 - atom) * covered + atom * previous
        need(atom > envelope > admitted > previous and atom < 1 - envelope, 'full wrapper envelope and stock')
        stages.append(dict(previous=previous, covered=covered, atom=atom, envelope=envelope, admitted=admitted, strict_debit=envelope - admitted))
        previous = admitted
    need(stages[0]['envelope'] < claim, 'one wrapper cannot justify final claimed saving')
    instances = []
    for index, event in enumerate((e for e in w['events'] if e[0] == 'LOCAL')):
        stage = event[1]
        copy = index % scale
        instances.append({'stage': stage, 'copy': copy, 'source_register': event[2], 'destination_register': event[3], 'ports': 111, 'fresh_helper_namespace': f'stage{stage}_copy{copy}', 'body_axes': list(range(1 + 7 * (stage - 1), 1 + 7 * stage))})
    need(len(instances) == F and len({(i['stage'], i['copy']) for i in instances}) == F, 'every distinct native call supplied')
    stem = 'EFREE-'
    blob = gzip.compress(json.dumps(w, separators=(',', ':')).encode(), mtime=0)
    caller_path = H / (stem + 'CALLER.json.gz')
    if write_artifacts:
        caller_path.write_bytes(blob)
    else:
        frozen_blob = caller_path.read_bytes()
        need(json.loads(gzip.decompress(frozen_blob)) == w, 'deterministic caller payload equals frozen artifact')
        blob = frozen_blob
    out = dict(status='PASS_PAIRED_EFREE_BIT_EXISTING_00385248', ordinary_admitted=claim, previous_ordinary=seed, ordinary_gain=None, existing_same_profile_ordinary=prior_chain['ordinary_admitted'], raw_tested=RAW, raw_crossing=[low, high], covered_saving=covered, caller_sha256=hashlib.sha256(blob).hexdigest(), native_source_sha256=hashlib.sha256(sourceblob).hexdigest(), source_pins=manifest['pins'], forward_coefficients=forward_count, reverse_coefficients=reverse_count, source=source, native_paid=dict(sorted(p0.items())), native_helpers=dict(sorted(t0.items())), paid=dict(sorted(P.items())), targets=dict(sorted(T.items())), paid_jobs=sum(P.values()), productive_fields=sum(T.values()), rank_surplus=scale * 753, native_calls=F, native_instances=instances, independent_moment_intervals={str(k): I.bounds_text(margin(k), 28) for k in (RAW, low, high)}, finite_admission=cert, independent_finite_ratios=[I.bounds_text(r, 28) for r in ratios], independent_normalized_upper=I.bounds_text((norm, norm), 28), event_counts=dict(ops), events=len(w['events']), discarded_source_stream=discarded, empty_body_targets={'count': 0, 'rank1_productive_credit': 0}, ordinary_basis_records=basis, ordinary_visible_records=visible, whole_job_route_count=route_count, whole_job_route_records=routes, ordinary_record_allowance=10 ** 12, owned_bank_bound=owned, compiler_constants={'U_raw': f'sum(i=0..767,{sum(T.values())}^(767-i)*{sum(P.values())}^i)', 'D': f'{sum(T.values())}^768-W', 'O': f'{owned}*U_raw+D', 'G': f'1000000000000*U_raw+8*R+2*{sum(T.values())}^768', 'E': '64*(Z+N+P+G+1)^3', 'B_constant': 'P+E', 'C0': '32*N*B_constant^2'}, ordinary_bootstrap=stages, negative_controls=negative, odd_port_determinant=parity, assumptions=['native_all_columns', 'owned_erasure', 'compiler', 'precision_tape', 'analytic_recovery'], scope='Paired E-free BIT specialization of#6980 with two actual native copies per stage; removes empty-body credit with unchanged complete signed moment crossing of#6834; inherited framework; no new kappa or native theorem reproof.', new_global_kappa_claim=False, seconds=time.monotonic() - started)
    result_path = H / (stem + 'RESULT.json')
    if write_artifacts:
        result_path.write_text(json.dumps(encode(out), indent=2) + '\n')
    else:
        frozen = json.loads(result_path.read_text())
        compared = {k: v for k, v in encode(out).items() if k != 'seconds'}
        need(compared == {k: v for k, v in frozen.items() if k != 'seconds'}, 'every proof-relevant receipt field equals frozen artifact')
    print(json.dumps(encode({k: out[k] for k in ('status', 'ordinary_admitted', 'ordinary_gain', 'raw_crossing', 'events', 'event_counts', 'productive_fields', 'paid_jobs', 'ordinary_visible_records', 'whole_job_route_records', 'owned_bank_bound', 'seconds')}), indent=2))
if __name__ == '__main__':
    main()

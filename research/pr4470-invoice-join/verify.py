#!/usr/bin/env python3
"""Independent join of the selected #4470 p16 invoice to its independently derived parts.

Separately written; imports no checker. It (A) rebuilds the complete p16 target/paid
histogram from the committed CONTROLLER.json event word and the per-orientation local
profile derived by the #4504 frame audit, with a closed-form third derivation from the
#4440 controller formula, and binds it to RESULT.json, NATIVE.json.gz, the embedded
controller invoice and #4478's hard-coded histogram; (B) encloses the raw moment surplus
and the three completion tails with decimal arithmetic under directed rounding (a
different method from the Fraction series used by #4470 and #4478); (C) runs semantic
rejection controls. JoyboyBrian with substantial Claude Code assistance. Apache-2.0.
"""
import ast
import copy
import decimal
import gzip
import hashlib
import json
import sys
from collections import Counter
from decimal import Decimal as D
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
JOINT = 'research/joint-helper-lattice/'

# Model constants of the #4440 complex controller (PROOF.md section 2), not read from code:
# 112 ports, fresh block rank 8, p = 16 pairs, prefix a = 7, 2p+1 = 33 local stages.
PORTS, BLOCK, PAIRS, PREFIX = 112, 8, 16, 7
STAGES = 2 * PAIRS + 1
THICK = frozenset({0, 2 * PAIRS, *range(1, 2 * PAIRS, 2)})
# THREE-base unit embedded in CONTROLLER.json's generic invoice (#4440 PROOF.md section 1).
THREE_HELPERS = {5: 28, 6: 18, 7: 56, 8: 93, 9: 213}
THREE_PAID = {1: 2487, 2: 713, 3: 224, 4: 102, 5: 20, 8: 8}
# Values stated in docs/research/pr-intake-evidence/pr4470/PROOF-REVIEW.md.
REVIEW = {'kappa': Q(60403, 20000000), 'tested': Q(3020155, 10 ** 9), 'cutoff': 20,
          'floor': 21, 'offset': Q(1, 5), 'root': (Q(30201659770, 10 ** 13), Q(30201659771, 10 ** 13)),
          'fields': 10928, 'paid_jobs': 64620, 'target_mass': 239886, 'paid_mass': 239134}
LIMITS = {'alpha': 1 - Q(1, 10 ** 9), 'gamma': Q(97, 100), 'delta': Q(97, 100)}

PREC = 60     # working digits
SLACK = 40    # every ln/exp value is widened by 10^-(PREC-SLACK) relative, far beyond 1 ulp


class Reject(Exception):
    pass


def need(ok, why):
    if not ok:
        raise Reject(why)


# ---------------------------------------------------------------- source binding

def blob(data):
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()


def load_inputs():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    data = {}
    for row in pins['files']:
        if row['usage'] != 'input':
            continue
        rel = Path(row['path'])
        need(not rel.is_absolute() and '..' not in rel.parts, 'canonical input path')
        raw = (ROOT / rel).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'sha256 pin: ' + row['path'])
        need(blob(raw) == row['git_blob'], 'git blob pin: ' + row['path'])
        data[row['path']] = raw
    return data


def as_json(raw, gz=False):
    return json.loads(gzip.decompress(raw) if gz else raw)


def hist(d):
    return {int(k): int(v) for k, v in d.items()}


def literal_dict(source, name):
    """Module-level `name = {...}` literal from a Python file, read as data (never executed)."""
    found = [n.value for n in ast.parse(source).body if isinstance(n, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == name for t in n.targets)]
    need(len(found) == 1, 'one literal ' + name)
    return hist(ast.literal_eval(found[0]))


# ---------------------------------------------------------------- A. invoice join

def controller_charges(ctrl):
    """Walk the emitted word once; return per-orientation full calls and the controller-only bill."""
    need((ctrl['kind'], ctrl['pairs'], ctrl['prefix_pairs'], ctrl['ambient_rank'])
         == ('complex', PAIRS, PREFIX, 1 + BLOCK * len(THICK)), 'controller parameters')
    full = {'forward': [], 'backward': []}
    thin, idle_paid, main = [], Counter(), Counter()
    for ev in ctrl['physical_events']:
        op = ev[0]
        if op == 'LOCAL':
            _, stage, pair, backward = ev
            need(stage in THICK and 0 <= pair < PAIRS and isinstance(backward, bool), 'full call at a thick stage')
            full['backward' if backward else 'forward'].append(stage)
        elif op == 'QUERY_SHEAR':
            _, stage, pair, backward = ev
            need(0 <= stage < STAGES and stage not in THICK and 0 <= pair < PAIRS, 'query shear at a thin stage')
            thin.append(stage)
        elif op == 'IDLE':
            _, pair, stages = ev
            need(0 <= pair < PAIRS and stages and len(set(stages)) == len(stages) and set(stages) <= THICK,
                 'idle multiplies only distinct thick stages')
            idle_paid[BLOCK * len(stages)] += 2 * PORTS   # both lines of the pair, every port
        elif op in ('ADD', 'SIGNED_SWAP', 'SWAP'):
            pass                                          # scalar bridge: no rank charge
        else:
            raise Reject('unknown event ' + str(op))
    calls = sorted(full['forward'] + full['backward'])
    need(calls == sorted(THICK), 'exactly one full native call per thick stage')
    need(sorted(thin) == sorted(set(range(STAGES)) - THICK), 'exactly one paid query shear per thin stage')
    need(len(ctrl['diagonal']) == 2 * PAIRS, 'one diagonal output per line')
    for term in ctrl['diagonal']:
        need(len(term) == 1 + STAGES and term[0] in (-1, 1), 'central Gaussian exponent is +-1')
        need(all(x in (0, 1) for x in term[1:]), 'stage exponents are 0/1')
        support = {s for s in range(STAGES) if term[1 + s]}
        need(support <= THICK, 'no main output is credited for a thin stage')
        main[1 + BLOCK * len(support)] += PORTS
    return full, len(thin), main, idle_paid


def join(ctrl, frame):
    """Complete p16 histogram: controller bill + one fresh local unit per full call."""
    full, thin, main, idle_paid = controller_charges(ctrl)
    new = frame['profiles']['new']
    helpers = hist(new['helpers'])
    targets, paid = Counter(main), Counter(idle_paid)
    paid[1] += PORTS * thin
    for orientation, stages in full.items():
        unit = hist(new[orientation]['paid'])
        need(new[orientation]['owned_center_jobs'] == unit.get(8, 0) == 8, 'eight rank-8 owned center jobs charged')
        for _ in stages:
            targets.update(helpers)
            paid.update(unit)
    return {'targets': dict(targets), 'paid': dict(paid), 'main': dict(main), 'idle': dict(idle_paid),
            'full_forward': len(full['forward']), 'full_backward': len(full['backward']), 'thin': thin,
            'helpers': helpers, 'unit_paid': {o: hist(new[o]['paid']) for o in full}}


def formula(helpers, unit):
    """#4440 PROOF.md section 2 closed form, with no reference to the event word."""
    p, a, d, v = PAIRS, PREFIX, BLOCK, PORTS
    targets, paid = Counter({1 + d * (p + 2): 2 * v}), Counter()
    for j in list(range(1, a + 1)) + list(range(1, p - a)):
        targets[1 + d * (j + 1)] += 2 * v
        paid[d * (j + 1)] += 2 * v
    for _ in range(p + 2):
        targets.update(helpers)
        paid.update(unit)
    paid[1] += v * (p - 1)
    return dict(targets), dict(paid)


def bind(inp):
    """All cross-bindings of the joined histogram against committed sources."""
    ctrl = as_json(inp[JOINT + 'CONTROLLER.json'])
    frame = as_json(inp['research/pr4470-frame-audit/RESULT.json'])
    result = as_json(inp[JOINT + 'RESULT.json'])
    native = as_json(inp[JOINT + 'NATIVE.json.gz'], gz=True)
    j = join(ctrl, frame)
    T, P = j['targets'], j['paid']
    need(j['unit_paid']['forward'] == j['unit_paid']['backward'], 'both orientations carry one local paid profile')
    unit = j['unit_paid']['forward']
    need(formula(j['helpers'], unit) == (T, P), 'event-word join equals the #4440 closed form')
    need(sum(T.values()) == REVIEW['fields'] and sum(P.values()) == REVIEW['paid_jobs'], 'field and job counts')
    need(sum(r * n for r, n in T.items()) == REVIEW['target_mass'], 'target rank mass')
    need(sum(r * n for r, n in P.items()) == REVIEW['paid_mass'], 'paid rank mass')
    need((hist(result['targets']), hist(result['paid'])) == (T, P), 'RESULT.json histogram')
    need((result['full_calls'], result['query_shears']) == (j['full_forward'] + j['full_backward'], j['thin']),
         'RESULT.json call counts')
    need((hist(result['local_helpers']), hist(result['local_paid'])) == (j['helpers'], unit), 'RESULT.json local unit')
    need((hist(native['helpers']), hist(native['paid'])) == (j['helpers'], unit), 'NATIVE.json.gz receipt')
    src = inp['research/pr4470-arithmetic-check/verify.py'].decode()
    need((literal_dict(src, 'T'), literal_dict(src, 'P')) == (T, P), '#4478 evaluated exactly this histogram')
    inv = ctrl['invoice']
    need(hist(inv['main']) == j['main'], 'embedded controller main targets')
    calls = j['full_forward'] + j['full_backward']
    embedded = Counter(hist(inv['paid']))
    embedded.subtract({r: calls * n for r, n in THREE_PAID.items()})
    embedded.update({r: calls * n for r, n in unit.items()})
    need(+embedded == Counter(P), 'embedded THREE-base invoice with the new unit substituted')
    need((inv['productive_fields'], inv['rank_surplus']) == (REVIEW['fields'], REVIEW['target_mass'] - REVIEW['paid_mass']),
         'embedded field count and surplus')
    old = Counter(hist(inv['paid']))
    need(sum(old.values()) == inv['paid_calls'], 'embedded THREE-base paid count')
    sel = as_json(inp['certificates/selected-result.json'])
    need(Q(sel['kappa']) == REVIEW['kappa'] == Q(result['kappa']), 'selected kappa')
    st = result['strictification']
    need((Q(st['tested']), st['cutoff'], st['floor'], Q(st['tail_offset']), st['power'])
         == (REVIEW['tested'], REVIEW['cutoff'], REVIEW['floor'], REVIEW['offset'], 1024), 'tail parameters')
    pred = as_json(inp['research/missing-join-frame/RESULT.json'])
    return j, (hist(pred['targets']), hist(pred['paid'])), frame


# ---------------------------------------------------------------- B. decimal enclosures

CTX = decimal.Context(prec=PREC, Emax=10 ** 6, Emin=-10 ** 6, traps=[decimal.InvalidOperation, decimal.DivisionByZero])
FLOOR = CTX.copy()
FLOOR.rounding = decimal.ROUND_FLOOR
CEIL = CTX.copy()
CEIL.rounding = decimal.ROUND_CEILING
REL = D(10) ** -(PREC - SLACK)


def dec(x):
    """Rational -> enclosing decimal interval."""
    x = Q(x)
    return FLOOR.divide(D(x.numerator), D(x.denominator)), CEIL.divide(D(x.numerator), D(x.denominator))


def widen(v):
    e = CEIL.multiply(abs(v), REL)
    return FLOOR.subtract(v, e), CEIL.add(v, e)


def ln_iv(k):
    return widen(CTX.ln(D(k))) if k != 1 else (D(0), D(0))


def mul_pos(a, b):
    need(a[0] >= 0 and b[0] >= 0, 'nonnegative interval product')
    return FLOOR.multiply(a[0], b[0]), CEIL.multiply(a[1], b[1])


def pow_iv(k, t):
    """k^t for integer k >= 1 and rational t >= 0: exp(t ln k), exp monotone."""
    x = mul_pos(dec(t), ln_iv(k))
    return widen(CTX.exp(x[0]))[0], widen(CTX.exp(x[1]))[1]


def moment(h, t):
    lo = hi = D(0)
    for k, n in h.items():
        p = pow_iv(k, t)
        lo, hi = FLOOR.add(lo, FLOOR.multiply(D(n), p[0])), CEIL.add(hi, CEIL.multiply(D(n), p[1]))
    return lo, hi


def surplus(T, P, saving):
    """Enclosure of T_t - P_t at t = 1 - saving."""
    t = 1 - Q(saving)
    a, b = moment(T, t), moment(P, t)
    return FLOOR.subtract(a[0], b[1]), CEIL.subtract(a[1], b[0])


def tails(T, P, tested, u, c, b):
    t = 1 - Q(tested)
    target = moment(T, t)
    alpha = CEIL.divide(moment(P, t)[1], target[0])
    gamma = CEIL.divide(moment(P, t + u)[1], FLOOR.multiply(pow_iv(c, u)[0], target[0]))
    delta = CEIL.divide(D(b * sum(T.values())), FLOOR.multiply(pow_iv(c, Q(tested))[0], target[0]))
    return {'alpha': alpha, 'gamma': gamma, 'delta': delta}


def moment_checks(T, P, kappa=REVIEW['kappa']):
    out = {'kappa': surplus(T, P, kappa), 'tested': surplus(T, P, REVIEW['tested']),
           'root_low': surplus(T, P, REVIEW['root'][0]), 'root_high': surplus(T, P, REVIEW['root'][1])}
    need(out['kappa'][0] > 0, 'positive raw surplus at the selected kappa')
    need(out['tested'][0] > 0, 'positive raw surplus at the tested saving')
    need(out['root_low'][0] > 0 and out['root_high'][1] < 0, 'raw root inside the stated bracket')
    tl = tails(T, P, REVIEW['tested'], REVIEW['offset'], REVIEW['cutoff'], REVIEW['floor'])
    for name, value in tl.items():
        need(value < dec(LIMITS[name])[0], name + ' below its stated limit')
    need(Q(97, 100) ** 128 < Q(1, 16), 'decay block (97/100)^128 < 1/16')
    need(1 / (1 + 1024 * Q(1, 10 ** 9)) + Q(4, 2 ** 32) < 1, 'normalized paid bound below one')
    return out, tl


# ---------------------------------------------------------------- C. controls

def rejects(fn):
    try:
        fn()
    except Reject as e:
        return str(e)
    raise Reject('control was not rejected')


def controls(inp, j, pred, frame):
    T, P = j['targets'], j['paid']
    ctrl = as_json(inp[JOINT + 'CONTROLLER.json'])
    out = {}

    def bumped(h, src, dst, n=1):
        h = Counter(h)
        h[src] -= n
        h[dst] += n
        return dict(+h)

    out['one_extra_rank1_paid_job'] = rejects(lambda: moment_checks(T, dict(Counter(P) + Counter({1: 1}))))
    out['one_paid_rank1_job_promoted_to_rank2'] = rejects(lambda: moment_checks(T, bumped(P, 1, 2)))
    out['one_productive_rank9_helper_demoted_to_rank8'] = rejects(lambda: moment_checks(bumped(T, 9, 8), P))
    out['kappa_at_root_upper_end'] = rejects(lambda: moment_checks(T, P, REVIEW['root'][1]))
    out['predecessor_p17_invoice_at_selected_kappa'] = rejects(lambda: need(surplus(*pred, REVIEW['kappa'])[0] > 0, 'predecessor surplus'))
    old = copy.deepcopy(frame)
    old['profiles']['new'] = old['profiles']['old']
    oj = join(ctrl, old)
    out['pr4447_local_unit_in_p16'] = rejects(lambda: moment_checks(oj['targets'], oj['paid']))

    def mutate(edit):
        bad = copy.deepcopy(inp)
        c = as_json(bad[JOINT + 'CONTROLLER.json'])
        edit(c)
        bad[JOINT + 'CONTROLLER.json'] = json.dumps(c).encode()
        return lambda: bind(bad)

    def first(c, op):
        return next(i for i, e in enumerate(c['physical_events']) if e[0] == op)

    out['query_shear_dropped'] = rejects(mutate(lambda c: c['physical_events'].pop(first(c, 'QUERY_SHEAR'))))
    out['query_shear_promoted_to_full_call'] = rejects(mutate(lambda c: c['physical_events'][first(c, 'QUERY_SHEAR')].__setitem__(0, 'LOCAL')))
    out['full_call_demoted_to_query'] = rejects(mutate(lambda c: c['physical_events'][first(c, 'LOCAL')].__setitem__(0, 'QUERY_SHEAR')))
    out['idle_stage_removed'] = rejects(mutate(lambda c: c['physical_events'][first(c, 'IDLE')][2].pop()))
    out['main_output_credited_thin_stage'] = rejects(mutate(lambda c: c['diagonal'][0].__setitem__(1 + 2, 1)))
    out['central_exponent_zero'] = rejects(mutate(lambda c: c['diagonal'][0].__setitem__(0, 0)))

    def frame_edit(edit):
        bad = copy.deepcopy(inp)
        f = as_json(bad['research/pr4470-frame-audit/RESULT.json'])
        edit(f['profiles']['new'])
        bad['research/pr4470-frame-audit/RESULT.json'] = json.dumps(f).encode()
        return lambda: bind(bad)

    def shift_backward(n):
        p = n['backward']['paid']
        p['1'] -= 1
        p['2'] += 1
    out['backward_unit_one_job_shifted'] = rejects(frame_edit(shift_backward))
    out['helper_unit_one_rank_lowered'] = rejects(frame_edit(lambda n: n['helpers'].update({'9': 325, '8': 48})))
    out['tampered_pinned_bytes'] = rejects(lambda: need(hashlib.sha256(inp[JOINT + 'CONTROLLER.json'] + b' ').hexdigest()
                                                     == hashlib.sha256(inp[JOINT + 'CONTROLLER.json']).hexdigest(), 'sha256 pin'))
    return out


def show(x, digits=15):
    return format(x, '.%dg' % digits)


def main():
    inp = load_inputs()
    j, pred, frame = bind(inp)
    T, P = j['targets'], j['paid']
    margins, tl = moment_checks(T, P)
    # Sharpness: the whole raw surplus at kappa and at the tested saving is below one rank-one job (1^t = 1).
    need(margins['kappa'][1] < 1 and margins['tested'][1] < 1, 'raw surplus below one rank-one paid job')
    ctl = controls(inp, j, pred, frame)
    print(json.dumps({
        'status': 'PASS_PR4470_INVOICE_JOIN',
        'join': {'full_calls': {'forward': j['full_forward'], 'backward': j['full_backward']},
                 'query_shears': j['thin'], 'targets': dict(sorted(T.items())), 'paid': dict(sorted(P.items())),
                 'productive_fields': sum(T.values()), 'paid_jobs': sum(P.values()),
                 'rank_masses': [sum(r * n for r, n in T.items()), sum(r * n for r, n in P.items())]},
        'bindings': ['CONTROLLER.json events and diagonal', '#4504 RESULT.json per-orientation unit',
                     '#4440 closed form', 'RESULT.json', 'NATIVE.json.gz', 'CONTROLLER.json embedded invoice',
                     '#4478 hard-coded T and P', 'selected kappa and tail parameters'],
        'raw_surplus_lower': {k: show(v[0]) for k, v in margins.items() if k != 'root_high'},
        'raw_surplus_upper_at_root_high': show(margins['root_high'][1]),
        'sharpness': 'raw surplus at kappa and at the tested saving is below 1 = the moment of one rank-one paid job',
        'tails_upper': {k: show(v) for k, v in tl.items()},
        'enclosure': 'decimal, %d digits, directed rounding, ln/exp widened by 10^-%d relative' % (PREC, PREC - SLACK),
        'rejected_controls': ctl,
        'new_kappa_claimed': False}, indent=1))


if __name__ == '__main__':
    try:
        main()
    except Reject as e:
        print('FAIL_PR4470_INVOICE_JOIN: ' + str(e))
        sys.exit(1)

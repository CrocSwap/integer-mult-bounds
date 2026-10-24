#!/usr/bin/env python3
"""Independent check of the #4630 -> #4635 native Word RAM kappa step.

Question: what exactly changes between Dugongue's #4630 (kappa 0.0030201655)
and #4635 (kappa 0.0030217754), and does the +0.0000016099 step come from the
paid profile / critical root or from the native transfer/absorption terms?

Stdlib only. No predecessor code is imported or executed; vendored PR-head files
are read as data (and two .py files as text, to bind the constants they state).
lm1909 with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from collections import Counter
from decimal import Decimal as D, getcontext
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
getcontext().prec = 60

H4630 = 'f4b974db1f651250a252721cf127d0491a802699'
H4635 = '898b0c8e2ca23897c312230988515c2553154f30'
H4610 = '1eb8da6cfb35512c0cc2533413e5ca42f48e13c6'
VENDOR = {  # vendored copy -> (pinned head, original path)
    'vendor/pr4630/raw-profile.json': (H4630, 'research/native-kappa-30201655/raw-profile.json'),
    'vendor/pr4630/native_ledger.py.txt': (H4630, 'research/native-kappa-30201655/native_ledger.py'),
    'vendor/pr4630/critical_check.py.txt': (H4630, 'research/native-kappa-30201655/critical_check.py'),
    'vendor/pr4635/ARITHMETIC.json': (H4635, 'research/native-provider-lift/ARITHMETIC.json'),
    'vendor/pr4635/PARAMETERS.json': (H4635, 'research/native-provider-lift/PARAMETERS.json'),
    'vendor/pr4635/critical_provider_check.py.txt': (H4635, 'research/native-provider-lift/critical_provider_check.py'),
    'vendor/pr4635/NATIVE-LIFT.md': (H4635, 'research/native-provider-lift/NATIVE-LIFT.md'),
    'vendor/pr4610/ARITHMETIC.json': (H4610, 'research/kappa-round3-warp-20261022/ARITHMETIC.json'),
}
MAIN = {
    'cjc': 'research/compact-joint-compiler/arithmetic/RESULT.json',
    'controller': 'research/joint-helper-lattice/CONTROLLER.json',
    'selected': 'certificates/selected-result.json',
}


def need(ok, why):
    if not ok:
        raise ValueError(why)


# ---------------------------------------------------------------- binding
def load_sources(sources=None, vendor_bytes=None):
    sources = sources if sources is not None else json.loads((HERE/'SOURCES.json').read_text())
    rows = {(r.get('pin') or 'base:'+r['path']): r for r in sources['files']}
    blobs = {}
    for rel, (head, path) in VENDOR.items():
        row = rows.get('head:%s:%s' % (head, path))
        need(row is not None and row['usage'] == 'provenance', 'missing head pin for '+path)
        raw = vendor_bytes[rel] if vendor_bytes and rel in vendor_bytes else (HERE/rel).read_bytes()
        need(sha256(raw).hexdigest() == row['sha256'], 'vendored bytes differ from pin: '+rel)
        blobs[rel] = raw
    for key, path in MAIN.items():
        row = rows['base:'+path]
        raw = (ROOT/path).read_bytes()
        need(row['usage'] == 'input' and sha256(raw).hexdigest() == row['sha256'], 'main input drift: '+path)
        blobs[key] = raw
    ctl4635 = rows['head:%s:research/native-provider-lift/CONTROLLER.json' % H4635]
    return blobs, ctl4635['sha256']


def hist(d):
    return {int(k): v for k, v in d.items()}


# ---------------------------------------------------------------- part A
def delta_ledger(blobs, ctl4635_sha):
    p30 = json.loads(blobs['vendor/pr4630/raw-profile.json'])
    p35 = json.loads(blobs['vendor/pr4635/ARITHMETIC.json'])
    main = json.loads(blobs['cjc'])
    need(blobs['vendor/pr4635/ARITHMETIC.json'] == blobs['vendor/pr4610/ARITHMETIC.json'],
         '#4635 ARITHMETIC.json is not byte-identical to #4610 round-three ARITHMETIC.json')
    need(ctl4635_sha == sha256(blobs['controller']).hexdigest(), '#4635 controller differs from main')
    ctl = json.loads(blobs['controller'])
    kinds = Counter(e[0] for e in ctl['physical_events'])
    need(kinds['LOCAL'] == 18, 'expected 18 LOCAL calls in the unchanged controller')
    for key in ('targets', 'paid', 'local_paid', 'local_helpers'):
        need(hist(p30[key]) == hist(main[key]), '#4630 profile is not main p16: '+key)
    need(hist(p30['targets']) == hist(p35['targets']), 'targets changed')
    need(hist(p30['local_helpers']) == hist(p35['local_helpers']), 'helper census changed')
    old, new = Counter(hist(p30['local_paid'])), Counter(hist(p35['local_paid']))
    dloc = {r: new[r]-old[r] for r in sorted(set(old) | set(new)) if new[r] != old[r]}
    need(dloc == {1: -36, 2: 24, 3: 16, 4: -20, 5: 4}, 'unexpected local paid delta %r' % dloc)
    need(sum(r*c for r, c in old.items()) == sum(r*c for r, c in new.items()) == 5327, 'local rank mass')
    P0, P1 = hist(p30['paid']), hist(p35['paid'])
    gdelta = {r: P1.get(r, 0)-P0.get(r, 0) for r in set(P0) | set(P1) if P1.get(r, 0) != P0.get(r, 0)}
    need(gdelta == {r: kinds['LOCAL']*c for r, c in dloc.items()}, 'global paid delta != 18 x local delta')
    T = hist(p30['targets'])
    need(sum(P1.values()) == 64404 and sum(T.values()) == 10928, '#4635 inventory counts')
    need(sum(P0.values()) == 64404 + 12*18, '#4630 paid count')
    need(sum(k*c for k, c in T.items()) - sum(r*c for r, c in P1.items()) == 752 ==
         sum(k*c for k, c in T.items()) - sum(r*c for r, c in P0.items()), 'rank-mass surplus 752 both')
    return dict(T=T, P0=P0, P1=P1, dloc=dloc, gdelta=gdelta, p35=p35, p30=p30)


# ---------------------------------------------------------------- part B
LN = {}


def ln(k):
    if k not in LN:
        LN[k] = D(k).ln()
    return LN[k]


def moment(h, t):
    return sum(c*(ln(k)*t).exp() for k, c in h.items())


def f(T, P, t):
    return moment(T, t) - moment(P, t)


TOL = D('1e-35')   # far above accumulated rounding of ~1e5 correctly rounded terms at 60 digits


def root(T, P, lo=D('0.99'), hi=D(1)):
    need(f(T, P, lo) < -TOL and f(T, P, hi) > TOL, 'no bracketed crossing')
    for _ in range(140):
        mid = (lo+hi)/2
        if f(T, P, mid) < 0:
            lo = mid
        else:
            hi = mid
    return lo, hi


def sign_at(T, P, t):
    v = f(T, P, D(t))
    need(abs(v) > TOL, 'sign not resolved at %s' % t)
    return v > 0


def mirror_max(T, P, t):
    pts = sorted({F(0), *(F(1, k) for k in T), *(F(1, r) for r in P)})
    worst = D(0)
    for a, b in zip(pts, pts[1:]):
        x = (a+b)/2
        src, ext = Counter(), Counter()
        for k, w in T.items():
            for r, c in P.items():
                if k > r and F(1, k) < x <= F(1, r):
                    src[k*r] += w*c
                if r > k and F(1, r) < x <= F(1, k):
                    ext[k*r] += w*c
        if ext:
            worst = max(worst, moment(ext, t)/moment(src, t))
    return worst


def roots(A):
    T, P0, P1 = A['T'], A['P0'], A['P1']
    out = {}
    for name, P, (blo, bhi) in (('4630', P0, ('.9969798340229', '.9969798340230')),
                                ('4635', P1, ('.9969782241', '.9969782242'))):
        lo, hi = root(T, P)
        need(not sign_at(T, P, blo) and sign_at(T, P, bhi), name+' stated root bracket rejected')
        # single crossing on a coarse grid of (0,1]: f<0 then f>0 exactly once
        signs = [sign_at(T, P, D(j)/100) for j in range(1, 101)]
        need(sum(1 for u, v in zip(signs, signs[1:]) if u != v) == 1, name+' grid sign changes')
        out[name] = dict(theta=lo, saving=1-hi, saving_hi=1-lo)
    return out


# ---------------------------------------------------------------- part C: finite absorption
LN2_LO, LN2_HI = F('0.6931471805'), F('0.6931471806')


def ln_upper(x):
    return F(D(x.numerator).ln() - D(x.denominator).ln() + D('1e-40'))


def absorption_margin(theta_lo, qC, H=10**12):
    """Lower bound on (1-theta-q_C)log N - log A - (2/5)log(133+log N) with
    N=2^H, n0=145*1024^650, A=n0^(1-theta)/(133+log n0)^(2/5) <= n0^(1-theta),
    and theta < theta_hi(=1-saving_lo). Uses the true root, not the rounded bracket."""
    one_minus_theta_hi = 1-F(theta_lo)          # upper bound for (1-theta)
    log_n0_hi = ln_upper(F(145)) + 6500*LN2_HI
    logA_hi = one_minus_theta_hi*log_n0_hi
    over_hi = F(2, 5)*ln_upper(133 + H*LN2_HI)
    return (1-F(theta_lo)-qC), logA_hi, over_hi


def absorption(R):
    res = {}
    for name, qC, kappa in (('4630', F('0.0030201656'), F('0.0030201655')),
                            ('4635', F('0.0030217755'), F('0.0030217754'))):
        r = R[name]
        th_hi = F(r['theta']) + F(1, 10**40)
        gap = 1 - th_hi - qC
        _, logA, over = absorption_margin(r['theta'], qC)
        margin = gap*10**12*LN2_LO - logA - over
        need(margin > 0, name+' finite absorption fails')
        need(F(r['saving']) > qC > kappa, name+' order raw saving > q_C > kappa')
        qmax = F(r['saving']) - (logA+over)/(10**12*LN2_LO)
        res[name] = dict(margin=margin, qC_max_at_this_N=qmax)
    return res


# ---------------------------------------------------------------- part D: native ledgers
C32 = F(3, 32)


def ledger(kappa, q, eps, beta, r, xi, provider, stop, strassen=2**45-7**16):
    sav = {
        'main': eps*q, 'standalone_routing': F(1), 'fused_gaussian': 1-eps+q*beta,
        'standalone_addressing': F(1), 'group_scans': 1-eps+beta, 'boundary': C32+xi-eps,
        'sparse_visits': F(1, 2)+xi-eps, 'record_products': eps, 'core_face_recovery': 79-eps-beta}
    guards = {
        'positive_kappa': kappa, 'stopped_provider': provider*(1-stop)-q, 'stop_positive': stop,
        'stop_below_one': 1-stop, 'epsilon_below_one': 1-eps, 'beta_positive': beta,
        'beta_below_epsilon': eps-beta, 'cap_above_band': xi-F(1, 2), 'cap_below_dimension': eps-xi,
        'global_gamma': 1-eps-r, 'group_chirp': 1-(beta+2*xi-2+r), 'group_key': 1-(beta+1-eps),
        'membership': 1-beta-2*(1-eps), 'spare_positive': r, 'strassen_integer_certificate': F(strassen)}
    excess = {k: v-kappa for k, v in sav.items()}
    failed = sorted([k for k, v in guards.items() if v <= 0] + [k+'_excess' for k, v in excess.items() if v <= 0])
    return sav, guards, excess, failed


def lift_params(kappa, qC):
    """NATIVE-LIFT.md 'Explicit universal parameter choice', re-implemented."""
    Q = min(qC, C32)
    need(0 < kappa < Q, 'kappa outside (0, min(q_C,3/32))')
    q = (kappa+Q)/2
    stop = (qC-q)/(2*qC)
    delta = min(F(1, 100), (q-kappa)/(4*(q+1)), (C32-q)/16)
    eps, beta = 1-delta, 1-3*delta
    r, layout = delta/10, delta/100
    xi = eps*(1+q)-C32+layout
    return dict(q=q, stop=stop, delta=delta, eps=eps, beta=beta, r=r, layout=layout, xi=xi)


def check_4635(blobs):
    P = json.loads(blobs['vendor/pr4635/PARAMETERS.json'])
    kappa, qC = F(P['target']), F(P['provider'])
    need(kappa == F('0.0030217754') and qC == F('0.0030217755'), 'stated #4635 target/provider')
    x = lift_params(kappa, qC)
    for k_mine, k_theirs in (('q', 'q'), ('stop', 'stop'), ('delta', 'delta'), ('r', 'spare'),
                             ('layout', 'layout'), ('xi', 'xi')):
        need(x[k_mine] == F(P[k_theirs]), 'parameter mismatch '+k_theirs)
    need(x['eps'] == F(P['epsilon']) and x['beta'] == F(P['beta']), 'epsilon/beta mismatch')
    sav, guards, excess, failed = ledger(kappa, x['q'], x['eps'], x['beta'], x['r'], x['xi'], qC, x['stop'])
    need(not failed, '#4635 ledger fails: %r' % failed)
    need(sav == {k: F(v) for k, v in P['savings'].items()}, 'nine savings differ from PARAMETERS.json')
    stored = {k: F(v) for k, v in P['guards'].items()}
    mine = dict(guards)
    for k, v in excess.items():
        mine[k+'_excess'] = v
    for k, v in stored.items():
        need(k in mine and mine[k] == v, 'guard differs from PARAMETERS.json: '+k)
    need(min(excess.values()) == F(P['minimum_excess']) == excess['main'], 'minimum excess')
    # rejecting controls, each must fail for the stated reason
    ctl = {}
    try:
        lift_params(qC, qC)
    except ValueError as e:
        ctl['kappa_equals_provider'] = str(e)
    try:
        lift_params(F(1, 10), F(1, 2))
    except ValueError as e:
        ctl['kappa_above_3_32'] = str(e)
    try:
        lift_params(kappa, F('0.0030201656'))
    except ValueError as e:
        ctl['4635_kappa_on_4630_provider'] = str(e)
    s2 = ledger(kappa, x['q'], x['eps'], x['beta'], x['r'], x['xi'], qC, x['stop'])[0]
    unfused = 1-x['eps']   # O(T d) Gaussian evaluation saves only 1-epsilon = delta
    ctl['unfused_gaussian_row'] = 'saving %s <= kappa' % float(unfused) if unfused <= kappa else None
    need(len([v for v in ctl.values() if v]) == 4 and s2 == sav, '#4635 controls')
    return dict(kappa=kappa, qC=qC, params=x, excess=excess, controls=ctl)


def check_4630(blobs):
    src = blobs['vendor/pr4630/native_ledger.py.txt'].decode()
    for lit in ("PROVIDER=F('0.0030201656')", "Q=F('0.00302016555')", "STOP=F(1,10**9)",
                "TARGET=F('0.0030201655')", "epsilon=1-F(1,10**8), beta=1-F(3,10**8)",
                "r=F(1,10**9)", "xi=epsilon*(1+q)-F(3,32)+F(1,10**10)"):
        need(lit in src, '#4630 ledger constant not found: '+lit)
    base = dict(kappa=F('0.0030201655'), q=F('0.00302016555'), eps=1-F(1, 10**8),
                beta=1-F(3, 10**8), r=F(1, 10**9), provider=F('0.0030201656'), stop=F(1, 10**9))

    def run(**kw):
        a = dict(base, **kw)
        xi = a['eps']*(1+a['q'])-C32+F(1, 10**10)
        return ledger(a['kappa'], a['q'], a['eps'], a['beta'], a['r'], xi, a['provider'], a['stop'])
    sav, guards, excess, failed = run()
    need(not failed, '#4630 ledger fails')
    need(min(excess.values()) == excess['main'] == F('0.0000000000197983445'), '#4630 minimum excess')
    ctl = {}
    for name, kw, expect in (
            ('epsilon_one', dict(eps=F(1)), {'epsilon_below_one'}),
            ('unfunded_outer_target', dict(kappa=F('0.00302016555')), {'main_excess'}),
            ('key_fills_whole_word_power', dict(beta=1-F(1, 10**8)), {'group_key'}),
            ('membership_at_edge', dict(beta=1-F(2, 10**8)), {'membership'}),
            ('normalization_at_edge', dict(r=F(1, 10**8)), {'global_gamma'})):
        failed = set(run(**kw)[3])
        need(expect <= failed, '#4630 control %s did not fail for its stated reason: %r' % (name, failed))
        ctl[name] = sorted(failed)
    return dict(excess=excess, controls=ctl)


# ---------------------------------------------------------------- main
def main():
    blobs, ctl_sha = load_sources()
    A = delta_ledger(blobs, ctl_sha)
    R = roots(A)
    ABS = absorption(R)
    L35 = check_4635(blobs)
    L30 = check_4630(blobs)
    sel = json.loads(blobs['selected'])
    kap_sel = F(sel['kappa'])
    need(kap_sel == F('0.00302015') and kap_sel < F(R['4630']['saving']), 'selected kappa vs p16 root')
    # bind stated brackets / q_C in the vendored provider checks (text only)
    need("lo,hi=F('.9969798340229'),F('.9969798340230')" in blobs['vendor/pr4630/critical_check.py.txt'].decode(),
         '#4630 stated root bracket not found')
    need("lo,hi=F('.9969782241'),F('.9969782242')" in blobs['vendor/pr4635/critical_provider_check.py.txt'].decode()
         and "qC=F('.0030217755')" in blobs['vendor/pr4635/critical_provider_check.py.txt'].decode(),
         '#4635 stated root bracket / q_C not found')
    T, P1 = A['T'], A['P1']
    th = R['4635']['theta']
    eta = th*(ln(145)*(th-1)).exp()
    mir = mirror_max(T, P1, th)
    need(mir < D('0.562811') < D('0.564') < D('0.982097') < eta, '#4635 stated mirror/capacity bounds')
    # local paid moment change g(t) = sum dloc_r r^t, negative at the new root
    g = sum(c*(ln(r)*th).exp() for r, c in A['dloc'].items())
    need(g < 0, 'local paid moment change must be negative at the root')
    dk = F('0.0030217754') - F('0.0030201655')
    need(dk == F('0.0000016099'), 'stated kappa step')
    ds = D(R['4635']['saving']) - D(R['4630']['saving'])
    slack30 = D(R['4630']['saving']) - D('0.0030201655')
    slack35 = D(R['4635']['saving']) - D('0.0030217754')
    need(abs((D(dk.numerator)/D(dk.denominator) - ds) - (slack30 - slack35)) < D('1e-30'), 'decomposition')
    # negative controls on the roots / absorption
    rej = {}
    try:  # old #4630 profile cannot support #4635's provider q_C
        need(F(R['4630']['saving_hi']) > F('0.0030217755'), 'old p16 root below #4635 q_C')
    except ValueError as e:
        rej['4630_profile_with_4635_qC'] = str(e)
    try:  # q_C above the true raw root is not absorbed
        gap, logA, over = absorption_margin(th, F('0.0030217759'))
        need(gap*10**12*LN2_HI - logA - over > 0, 'q_C above raw root not absorbed')
    except ValueError as e:
        rej['qC_above_root'] = str(e)
    try:  # a tampered vendored input is rejected by its head pin
        bad = dict(blobs)
        bad['vendor/pr4635/ARITHMETIC.json'] = blobs['vendor/pr4635/ARITHMETIC.json'].replace(b'"5": 40', b'"5": 41', 1)
        load_sources(vendor_bytes=bad)
    except ValueError as e:
        rej['tampered_vendored_profile'] = str(e)
    try:  # bracket from #4630 applied to the #4635 profile is rejected
        need(not sign_at(T, P1, '.9969798340229') and sign_at(T, P1, '.9969798340230'), 'wrong bracket')
    except ValueError as e:
        rej['4630_bracket_on_4635_profile'] = str(e)
    need(len(rej) == 4, 'a negative control was accepted: %r' % rej)

    s = lambda x, n=22: str(x)[:n]
    out = {
        'status': 'PASS_4635_DELTA_IS_PROFILE_ONLY',
        'changed_inputs': {
            'local_paid_delta_per_LOCAL_call': A['dloc'],
            'global_paid_delta': dict(sorted(A['gdelta'].items())),
            'LOCAL_calls': 18, 'targets_helpers_controller': 'unchanged (controller blob = main joint-helper-lattice/CONTROLLER.json)',
            'pr4635_ARITHMETIC_equals_pr4610_round3': True,
            'local_rank_mass': 5327, 'rank_mass_surplus_both': 752,
            'local_paid_moment_change_at_new_root': s(g),
        },
        'raw_saving_1_minus_theta': {k: s(v['saving'], 24) for k, v in R.items()},
        'raw_saving_step': s(ds, 24),
        'stated_kappa_step': str(dk),
        'transfer_slack_raw_minus_kappa': {'4630': '%.12e' % slack30, '4635': '%.12e' % slack35},
        'kappa_step_minus_raw_step': '%.12e' % (D(dk.numerator)/D(dk.denominator) - ds),
        'group_key_guard_equals_beta_below_epsilon': L35['params']['eps'] - L35['params']['beta'] == 2*L35['params']['delta'],
        'finite_absorption_log_margin_lower': {k: float(v['margin']) for k, v in ABS.items()},
        'largest_qC_this_N_supports': {k: float(v['qC_max_at_this_N']) for k, v in ABS.items()},
        'mirror_max_at_root_4635': s(mir, 10), 'capacity_eta_4635': s(eta, 10),
        'ledger_4635_min_excess': str(min(L35['excess'].values())),
        'ledger_4635_params': {k: str(v) for k, v in L35['params'].items()},
        'ledger_4635_controls': L35['controls'],
        'ledger_4630_min_excess': str(min(L30['excess'].values())),
        'ledger_4630_controls_fail_reasons': L30['controls'],
        'selected_kappa_below_p16_root': str(kap_sel),
        'negative_controls': rej,
        'scope': 'Profile delta, critical roots, finite-absorption and native-ledger arithmetic only. '
                 'Not covered: all-fiber algebraic identity of the #4610 word, retained analytic/compiler proofs, '
                 'the funded-majorant U/V/Q/d guards, the native algorithms themselves.',
    }
    print(json.dumps(out, indent=2, default=str))


if __name__ == '__main__':
    try:
        main()
    except ValueError as e:
        print('FAIL:', e)
        sys.exit(1)

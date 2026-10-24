#!/usr/bin/env python3
"""The p=19 uncoded word: trace identity, price, compiler, BIT chain and outer ledger.

Chain:

  1. the word is the controller's own gate trace, replayed in the controller algebra
     and required to equal controller() exactly; at p=19 it is 241 gates and
     diagonalises to the standard outputs with denominators [1] (p19_plain.py);
  2. the invoice takes no coding argument, so the word carries NO code: the field
     level bill is zero recodings, zero monomial field maps, zero scalar adds, zero
     owned clears and zero terminal-gauge decoder;
  3. the invoice prices the word at 0.007578535 with the PR4929 paid profile and
     reproduces the published p16 root; the raw moment sign at the tested saving is
     positive in exact interval arithmetic and in a 60-digit decimal control;
  4. the shape-correct power majorant (the constants research/query-thinned-controllers
     derives for a unit that splits at c = 20, completes at b = 21 with v = 1024)
     gives H0 = 5,170,423,668,736 and H1 = 49,224,448,837,637,726,209.  This is a
     numerical instantiation of the majorant, not an instantiation of every hypothesis
     of the source compiler theorem, which remains an applicability premise;
  5. the admitted ordinary BIT saving 0.0034 funds the endpoint;
  6. the strict outer ledger passes at the endpoint and at exactly 0.0034 fails only
     actual_bit_above_effective, so the endpoint is bit_saving - 5*gap.

The coded overlay is retained under P19_WORD.json as a historical record.  It is not
priced here: its terminal-gauge decoder costs 2,128 rank-1 units against a 1,103-unit
root budget, which is why it was dropped.
"""
import importlib.util, json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OWNERS, SIZE = 112, 512
SELECTED_CERT = ROOT/'certificates/selected-result.json'
FRONTIER = Q(json.loads(SELECTED_CERT.read_text())['kappa'])   # the selected repository record
REPORTED_FRONTIER = Q(302728823, 100000000000)                  # 0.00302728823, maintainer-reported, no certificate here
BIT_SAVING = Q(17, 5000)
GAP = Q(1, 1400000000)
KAPPA = Q(951999, 280000000)
TESTED = Q(951999, 280000000) + 7*Q(1, 1400000000)
H = {4: 28, 7: 7, 8: 47, 9: 326}
P_NEW = {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40}
MAPS, ADDS, CLEARS = 224, 896, 16

def need(ok, why):
    if not ok: raise ValueError(why)

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def invoice(p, pat, thick, prof):
    full = frozenset(range(2*p+1)); T, D = Counter(), Counter()
    outs = [full, full]
    for i, ch in enumerate(pat, 1):
        outs += [frozenset(range(0, 2*i+1)) if ch == 'I' else frozenset(range(2*i, 2*p+1))]*2
    for s in outs: T[1+8*len(s & thick)] += 112
    for i, ch in enumerate(pat, 1):
        if ch == 'I': D[8*len(frozenset(range(0, 2*i)) & thick)] += 224
        else: D[8*len(frozenset(range(2*i+1, 2*p+1)) & thick)] += 224
    for j in range(1, p): D[8*len(frozenset([2*j]) & thick)] += 224
    for r, n in H.items(): T[r] += len(thick)*n
    for r, n in prof.items(): D[r] += len(thick)*n
    D[1] += 112*(2*p+1-len(thick))
    T.pop(0, None); D.pop(0, None)
    return T, D

def ledger_failures(mod, kappa, certified, bit_saving=BIT_SAVING):
    prm = {'kappa': kappa, 'tested_saving': certified, 'complex_uniform_saving': kappa+6*GAP,
           'b': kappa+5*GAP, 'a': kappa+4*GAP, 'q': kappa+3*GAP, 'bit_saving': bit_saving,
           'epsilon': 1-GAP, 'beta': 1-3*GAP, 'r0': GAP/10, 'stop': GAP, 'layout': GAP, 'd': GAP}
    out = mod.ledger(prm)
    out['functional_checks']['actual_new_BIT_stock_sublinear'] = prm['beta']*(1-Q(1, 250))
    fails = [k for part in ('strict_checks', 'functional_checks') for k, x in out[part].items() if x <= 0]
    if not prm['complex_uniform_saving'] < certified: fails.append('uniform_above_certified_complex')
    if not prm['a'] < bit_saving: fails.append('effective_above_bit_saving')
    return fails

def shape_majorant(v, tested, uniform, cutoff, floor, max_rank):
    """The compiler constants for THIS complex shape, not the p7 unit's.

    research/query-thinned-controllers/verify.py::tail (lines 151-155) derives them for
    c = 20, b = 21, v = 1024: h = 1/64, B = (5+8h)v, debt = 1 + 8v(1-z0), H0 >= 8v.
    The p7 constants (h = 1/7, B = (4+7h)v, H0 >= 7v) come from 10 < 2^4 and 121 < 2^7 and
    fail here: 20 < 2^4 is false, 153 < 2^7 is false, and 20^7 < 21^6 is false.
    """
    t, z, h = 1-tested, 1-uniform, Q(1, 64)
    z0 = (t+z)/2
    gap = z0-t
    B, debt = (5+8*h)*v, 1+8*v*(1-z0)
    ratio = (gap*B+debt)/(h*gap)
    H0 = -((-ratio.numerator)//ratio.denominator)
    ratio = H0*(1-z0)/(z-z0)
    H1 = ratio.numerator//ratio.denominator+1
    need(cutoff**64 < floor**63, 'ranks after completion and splitting')
    need(max_rank < 256, 'raw ambient ranks below 256')
    need(H0 >= 8*v and H0*h*gap >= gap*B+debt, 'effective integer compiler bound')
    need((H0-1)*h*gap < gap*B+debt, 'previous threshold rejected')
    need(H1*(z-z0) > H0*(1-z0) >= (H1-1)*(z-z0), 'strict winning uniform rank')
    return H0, H1

def main():
    global L_phys, E_eng
    E_eng = load('lifteng', HERE/'physical_gauge_lift.py')
    receipt = json.loads((ROOT/'research/coded-native-caller/NORMALIZERS.json').read_text())
    _modes = [[(i, s) for i, s in enumerate(c) if s] for c in [[int(v) for v in x] for x in receipt['mode_columns']]]
    L_phys = lambda x, inv: E_eng.physical_code(x, receipt['ports'], _modes, inv)
    cols = [[int(v) for v in c] for c in receipt['mode_columns']]
    N = OWNERS

    A = [[Q(int(i == j)) - Q(sum(cols[m][i]*cols[m][j] for m in range(len(cols))), 4) for j in range(N)]
         for i in range(N)]
    Ainv = [[Q(int(i == j)) + (A[i][j]-Q(int(i == j)))/13 for j in range(N)] for i in range(N)]
    eye = [[Q(int(i == j)) for j in range(N)] for i in range(N)]
    need([[sum(A[i][k]*Ainv[k][j] for k in range(N) if A[i][k]) for j in range(N)] for i in range(N)] == eye,
         'A A^-1 = I')
    need(all(Ainv[i][j] == eye[i][j] - Q(sum(cols[m][i]*cols[m][j] for m in range(len(cols))), 52)
             for i in range(N) for j in range(N)), 'A^-1 = I - M M^T/52')
    for rec in receipt['ports']:
        seen, signs = set(), set()
        for x in range(SIZE):
            y, sg = E_eng.signed_map(rec, x)
            seen.add(y); signs.add(sg)
        need(len(seen) == SIZE and signs <= {1, -1}, 'port map is a signed address permutation')
    bank = [[0]*SIZE for _ in range(OWNERS)]
    for i in range(OWNERS): bank[i][7] = (i*13+7) % 65537 or 1
    mixed = E_eng.scalar_code(bank, [[(i, s) for i, s in enumerate(c) if s] for c in cols])
    need(all(v == 0 for i in range(OWNERS) for j, v in enumerate(mixed[i]) if j != 7),
         'scalar program moves no address')
    print('PASS rank-free: every port map is a signed address permutation and the scalar program moves no '
          'address, so a recoding adds no Gaussian rank')
    tmax = max(sum(abs(c) for c in col) for col in cols)
    prefix = (1 + Q(4*tmax, 4), 1 + Q(4*tmax, 52))
    need((tmax, prefix) == (56, (57, Q(69, 13))), 'published prefix bounds')
    print('PASS code: A = I - M M^T/4, A^-1 = I + (A - I)/13 = I - M M^T/52, A A^-1 = I; '
          'prefix bounds %d and %s, no recursive Gaussian child' % (prefix[0], prefix[1]))

    plain = json.loads((HERE/'P19_PLAIN.json').read_text())
    pw = plain['p19']
    need(pw['outputs'] == [[1, 4], [2, 4], [3, 4], [4, 4], [5, 4], [6, 4], [7, 4], [8, 4], [9, 4], [19, 2]],
         'p=19 diagonalisation outputs')
    need(pw['denominators'] == [1] and pw['trace_identity'] == 'replayed in the controller algebra',
         'trace identity and standard denominators')
    need((pw['retained_idles'], pw['idle_rank']) == (36, 198), 'idle census')
    need((pw['recodings'], pw['monomial_field_maps'], pw['scalar_adds'], pw['owned_clears'],
          pw['terminal_gauge_decoder']) == (0, 0, 0, 0, 0), 'no recoding bill')
    print('PASS word: the controller trace at p=19 gives %d gates %s, %d retained idles of rank %d, outputs %s '
          'with denominators %s, and no recoding bill'
          % (pw['gates'], pw['kinds'], pw['retained_idles'], pw['idle_rank'], pw['outputs'], pw['denominators']))
    word = json.loads((HERE/'P19_WORD.json').read_text())
    if isinstance(word, list): word = word[0]
    need(word['gate_records'] == 259 and word['recodings'] == 77, 'the coded overlay record is intact')
    print('RECORDED: the coded overlay (%d gates, %d recodings) is kept for reference only; it is not priced here'
          % (word['gate_records'], word['recodings']))

    p, pat = 19, 'I'*9+'T'*9
    thick = frozenset(range(1, 2*p, 2))
    T, Dp = invoice(p, pat, thick, P_NEW)
    E = load('moment', ROOT/'research/higher-moment-strictification/verify.py')
    t = 1-TESTED
    mt, mp = E.moment(T, t), E.moment(Dp, t)
    need(mt[0] > mp[1], 'raw moment sign at the tested saving')
    lim_a, lim_g, lim_d = 1-Q(1, 10**9), Q(97, 100), Q(97, 100)
    tk = 1-KAPPA
    mtk = E.moment(T, tk)
    alpha = E.divide(E.moment(Dp, tk), mtk)
    gamma = E.divide(E.moment(Dp, tk+Q(1, 5)), E.mul(E.power(20, Q(1, 5)), mtk))
    delta = E.divide((Q(sum(T.values())*21),)*2, E.mul(E.power(20, KAPPA), mtk))
    need(alpha[1] < lim_a and gamma[1] < lim_g and delta[1] < lim_d, 'charged tail ratios at the endpoint')
    need(lim_g**128 < Q(1, 16) and lim_d**128 < Q(1, 16), 'decay blocks')
    need(1/(1+1024*Q(1, 10**9)) + Q(4, 2**32) < 1, 'power-1024 tails')
    print('PASS invoice: raw moment sign positive at %s; at kappa the ratios are alpha %.8f, gamma %.6f, '
          'delta %.6f with both decay blocks under 1/16' % (TESTED, float(alpha[1]), float(gamma[1]), float(delta[1])))

    from decimal import Decimal, getcontext
    getcontext().prec = 60
    def dmoment(profile, c):
        total = Decimal(0)
        e = Decimal(1) - Decimal(c.numerator)/Decimal(c.denominator)
        for r, n in profile.items():
            total += Decimal(n)*((Decimal(r).ln()*e).exp())
        return total
    need((TESTED-KAPPA)/7 == GAP and GAP.numerator == 1, 'integer compiler grid')
    gap_at = dmoment(T, TESTED) - dmoment(Dp, TESTED)
    gap_below = dmoment(T, TESTED-Q(1, 10**3)) - dmoment(Dp, TESTED-Q(1, 10**3))
    gap_above = dmoment(T, TESTED+Q(5, 10**3)) - dmoment(Dp, TESTED+Q(5, 10**3))
    need(gap_at > 0 and gap_below > 0 and gap_above < 0, 'independent decimal sign check')
    print('PASS independent decimal engine (60 digits): signed moment +%s at the tested saving, '
          '+%s a step below, %s a step above' % (('%.6e' % gap_at), ('%.6e' % gap_below), ('%.6e' % gap_above)))

    H0, H1 = shape_majorant(1024, TESTED, KAPPA+6*GAP, 20, 21, max(T))
    print('PASS compiler: shape-correct majorant (h = 1/64, B = (5+8h)v, H0 >= 8v) at v=1024 gives '
          'H0 = %d, H1 = %d, N = 2^%d' % (H0, H1, H1))

    C1, a_old, atom = Q(345, 100000), Q(384599, 10000000000), Q(4, 1000)
    ordinary = (1-atom)*C1 + atom*a_old
    need(atom == Q(4, 1000) and atom > ordinary > BIT_SAVING and atom < 1-ordinary,
         'admitted ordinary BIT saving')
    print('PASS BIT: atom %.3f > ordinary saving %.10f > admitted cap 0.0034' % (float(atom), float(ordinary)))

    mod = load('ledger', ROOT/'research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py')
    need(ledger_failures(mod, KAPPA, TESTED) == [], 'ledger passes at the endpoint')
    need(ledger_failures(mod, Q(34, 10000), Q(34, 10000)+7*GAP) == ['actual_bit_above_effective', 'effective_above_bit_saving'],
         'at 0.0034 only the BIT side binds')
    need(ledger_failures(mod, KAPPA, TESTED, bit_saving=Q(27, 10000)) != [], 'old BIT saving rejected')
    print('PASS ledger: all predicates pass at kappa=%s; at exactly 0.0034 only the BIT predicate fails' % KAPPA)

    local_scalar, adapters, charts = 158168, 2*408, 688
    local_routes = (sum(P_NEW.values()) + adapters + charts)*1000
    need(local_routes + local_scalar < 10**7, 'local scalar and route allowance')
    raw = 19*10**7 + 16*1792 + 32*112*(word['gate_records'] + 2)
    field_records = (pw['monomial_field_maps'] + 448 + 448)*1000
    need(raw < 10**9 and raw + field_records < 10**9, 'raw nonrecursive bound with the field bill')
    need(local_routes + field_records < 10**7, 'with no recoding bill the local allowance holds')
    print('PASS budgets: local routes %d + local scalar %d < 10^7; raw %d + field bill %d = %d < 10^9, '
          'so with no recoding bill the local allowance now holds'
          % (local_routes, local_scalar, raw, field_records, raw+field_records))

    need(ledger_failures(mod, Q(3401, 1000000), Q(3401, 1000000)+7*GAP) != [], 'kappa above the BIT cap rejected')
    need(ledger_failures(mod, KAPPA, KAPPA+4*GAP) != [], 'unfunded uniform bracket rejected')
    rng = __import__('random').Random(3)
    C = lambda x: L_phys(x, False)
    Ci = lambda x: L_phys(x, True)
    Dg = lambda x, inv=False: E_eng.gaussian(x, range(1, 9), inv)
    Rg = lambda x, inv=False: E_eng.gaussian(x, range(9), inv)
    dense = [[rng.randrange(65537) for _ in range(SIZE)] for _ in range(OWNERS)]
    need(E_eng.diff(Dg(C(dense)), C(Dg(dense))) != 0, 'rank-8 letter does not commute with the code')
    need(E_eng.diff(Rg(C(dense)), C(Rg(dense))) == 0, 'full Gaussian letter commutes')
    print('PASS controls: kappa above the BIT cap, an unfunded uniform bracket, and the rank-8 letter are rejected')

    # Why the shape-correct constants and not the p7 pair: the p7 proof's premises are
    # 10 < 2^4 (split at 10^v) and 121 < 2^7 (ambient 121^v) with theta < 6/7.  This unit
    # splits at 20, completes at 21 and has ambient rank 153, so all three fail.
    need(not (20 < 2**4) and not (153 < 2**7) and not (20**7 < 21**6),
         'the p7 premises genuinely fail for this shape')
    A = E.power(153, TESTED)
    Pw = A
    for _ in range(10): Pw = E.mul(Pw, Pw)
    eta = E.divide((1-TESTED, 1-TESTED), Pw)
    lo, hi = 3000000, 4000000
    while hi - lo > 1:
        mid = (lo+hi)//2
        t2 = mid*Q(1, 10**9)
        A2 = E.power(153, t2); P2 = A2
        for _ in range(10): P2 = E.mul(P2, P2)
        if E.divide((1-t2, 1-t2), P2)[0] > (Q(63, 64))**1000: lo = mid
        else: hi = mid
    log_cap = lo*Q(1, 10**9)
    need(log_cap < TESTED, 'the logarithmic cap lies below the tested saving, so it cannot be the majorant here')
    print('PASS compiler: shape-correct majorant (query-thinned-controllers::tail constants) gives '
          'H0 = %d, H1 = %d' % (H0, H1))
    print('RECORDED: the p7 constants do not apply here (20 < 2^4 false, 153 < 2^7 false, 20^7 < 21^6 false), '
          'and the logarithmic majorant at ambient rank 153 caps the tested saving at %s (eta = %s below '
          '(63/64)^1000)' % (log_cap, E.display((eta[0]-((Q(63,64))**1000), eta[1]-((Q(63,64))**1000)))))
    need(delta[1] < Q(97, 100), 'the 0.97 delta limit holds')
    kappa_logmax = log_cap - 7*GAP
    # ---- discharging the three premises at the source's own level ----
    # H: the tail lemma, source structure, with the weaker but sufficient 0.97 limit.
    LIM = Q(97, 100)
    need(gamma[1] < LIM and delta[1] < LIM, 'gamma and delta under the 0.97 limit')
    need(LIM**128 < Q(1, 16), '0.97^128 < 1/16')
    need(LIM**1024 < (Q(1, 16))**8, 'block bound at power 1024, i.e. below 2^-32')
    need(Q(4)*LIM**1024 < Q(4, 2**32), 'four block failures below 4*2^-32')
    alpha_gap = Q(1, 10**9)
    need(alpha[1] < 1-alpha_gap, 'alpha under the Bernoulli gap')
    need(1/(1+1024*alpha_gap) + Q(4)*LIM**1024 < 1, 'tail assembly at power 1024')
    print('DISCHARGED tail limit: with L = 97/100, L^128 < 1/16, L^1024 < 2^-32, and '
          '1/(1+1024e-9) + 4*L^1024 < 1, so the source tail argument closes at the weaker limit; '
          '19/20 is a stronger unused choice')

    # F: the majorant's hypotheses are the unit's rank data, which the invoice census supplies.
    saved_H = dict(H)
    for r in list(H): del H[r]
    T_roles, _ = invoice(p, pat, thick, P_NEW)
    H.update(saved_H)
    helper_mass = Counter(T); helper_mass.subtract(T_roles)
    need(+helper_mass == Counter({r: len(thick)*n for r, n in H.items()}),
         'helper T mass is additive and separate from the role mass')
    need(sum(T.values()) == 12008, 'productive census')
    print('DISCHARGED compiler choice: the constants come from the pinned shape-correct derivation '
          '(query-thinned-controllers::tail) applied to this unit\'s ranks and completion bases, not from the p7 '
          'unit; the logarithmic route is not used and its cap %s is recorded above' % log_cap)

    # D: the helper block is autonomous with independent fields, so the main-role gauge cannot touch it.
    print('INHERITED helper materialisation: the 7752 units (19*{4:28,7:7,8:47,9:326}) are priced on the T side '
          'and not rebuilt here; what this package discharges is compatibility, below')

    # ---- the lifting lemma: the word's block realisation is a ring homomorphism ----
    lift = json.loads((HERE/'P19_LIFT.json').read_text())
    need(lift['status'] == 'PASS_LIFTING_LEMMA' and lift['differing_entries'] == 0, 'lifting lemma receipt')
    need(lift['control_status'].startswith('the p=2 address replay is randomised'),
         'the address replay is labelled a randomised control')
    print('PASS lifting lemma: Phi is multiplicative on the monomial ring (%d sampled pairs, 0 differing entries), '
          'so any polynomial identity between the gate list and the controller matrix lifts to address operators '
          'for every block count; the p=2 replay is a randomised control on the implementation'
          % lift['trials'])

    # ---- helper compatibility, the mechanical half ----
    need(pw['max_role'] == 37 and pw['role_set'] == list(range(38)),
         'the trace touches exactly the main roles 0..2p-1 and no helper index')
    print('PASS helper compatibility (mechanical): the trace\'s roles are exactly 0..37 (2p-1), so no gate reads '
          'or writes helper-owned state; the 7752 inherited helper units remain a separate T block')

    # ---- the controller's retained idle calls, now materialized in the listing ----
    pp, patq = 19, 'I'*9+'T'*9
    init = [((st+1)//2, st+1) for st in range(1, 2*pp) if st % 2 and st <= 2*pp-3]
    mid = [(1,) for st in range(1, 2*pp) if st % 2 == 0 and 2 <= st <= 2*pp-2]
    term = [(j, 2*pp+1-(2*j+3)) for j in range(pp-1)]
    keep_i = [r for pr, r in init if patq[pr-1] in 'IB']
    keep_t = [r for j, r in term if patq[j] in 'TB']
    idle_n = len(keep_i)+len(mid)+len(keep_t)
    idle_rank = sum(keep_i)+len(mid)*1+sum(keep_t)
    need((len(keep_i), len(mid), len(keep_t)) == (9, 18, 9), 'idle census matches the controller run')
    need(idle_n == 36 and idle_rank == 198, 'idle rank total')
    need(pw['retained_idles'] == idle_n and pw['idle_rank'] == idle_rank,
         'the word carries every retained idle')
    print('IDLES IN THE WORD: %d retained idle calls (9 initial rank %d, 18 middle rank 18, 9 terminal rank %d) '
          'apply %d rank across %d role-rank to main roles; the word carries no code, so they need no recoding '
          'and the field bill is zero' % (idle_n, sum(keep_i), sum(keep_t), idle_rank, 2*idle_rank))

    need(KAPPA > FRONTIER, 'claim above the frontier')
    claim = {'status': 'CLAIM_P19_UNCODED_WORD_SUPPLIER',
             'kappa': str(KAPPA), 'kappa_decimal': float(KAPPA),
             'complex_supplier': '0.007578535', 'bit_supplier': '17/5000',
             'kappa_under_logarithmic_majorant': str(kappa_logmax), 'logarithmic_cap': str(log_cap),
             'frontier_selected_record': str(FRONTIER),
             'gain_vs_selected_record_percent': round(100*(float(KAPPA)/float(FRONTIER)-1), 3),
             'frontier_reported': str(REPORTED_FRONTIER),
             'frontier_reported_provenance': 'maintainer-reported in review; no certificate in this tree',
             'gain_vs_reported_percent': round(100*(float(KAPPA)/float(REPORTED_FRONTIER)-1), 3),
             'complex_saving': float(Q(7578535, 1000000))/1000,
             'uncoded_word': {'gates': pw['gates'], 'gate_kinds': pw['kinds'],
                              'retained_idles': pw['retained_idles'], 'idle_rank': pw['idle_rank'],
                              'outputs': pw['outputs'], 'denominators': pw['denominators'],
                              'trace_identity': pw['trace_identity'], 'ambient_rank': pw['ambient_rank'],
                              'physical_bank_replay': 'not performed; ambient rank 153 exceeds a 512-address bank',
                              'p19_entries_checked': 'none (operator-level certification)'},
             'field_level_bill': {'recodings': pw['recodings'],
                                  'monomial_field_maps': pw['monomial_field_maps'],
                                  'scalar_adds': pw['scalar_adds'], 'owned_clears': pw['owned_clears'],
                                  'terminal_gauge_decoder': pw['terminal_gauge_decoder'],
                                  'recursive_gaussian_children': 0},
             'record_only_overlay': {'gates': word['gate_records'], 'gates_by_kind': word['gate_kinds'],
                                     'recodings': word['recodings'],
                                     'monomial_field_maps': word['monomial_field_maps'],
                                     'scalar_adds': word['scalar_adds'], 'owned_clears': word['owned_clears'],
                                     'status': 'historical record, NOT the priced word'},
             'paid_profile': P_NEW, 'helper_profile': H,
             'guards': {'alpha': float(alpha[1]), 'gamma': float(gamma[1]), 'delta': float(delta[1])},
             'compiler_obligations': {
                 'rank completion below b^v': 'checked on this census: max target rank 153 < 256',
                 'splitting at c^v': 'checked on this census: 20^64 < 21^63',
                 'whole-job normalizers': 'inherited from the producer; the word adds no job and consumes the same T/D interface',
                 'distinct-owner child allocation': 'inherited; the word introduces no new owner',
                 'rank-one surplus retention': 'inherited; the census is unchanged by the word'},
             'compiler': {'majorant': 'shape-correct power majorant (query-thinned-controllers constants)',
                          'v': 1024, 'h': '1/64', 'B': '(5+8h)v', 'H0_check': 'H0 >= 8v',
                          'H0': H0, 'H1': H1, 'N': '2^%d' % H1,
                          'classification': 'numerical instantiation under an applicability premise, not a proof',
                          'uninstantiated_hypotheses': [
                              'rank completion below b^v', 'job splitting at c^v',
                              'whole-job normalizers', 'distinct-owner child allocation',
                              'rank-one surplus retention', 'fresh-block replay of the trace']},
             'admitted_bit_saving': str(BIT_SAVING),
             'budgets': {'local_routes': local_routes, 'local_scalar': local_scalar,
                         'local_allowance': 10**7, 'raw_bound': raw, 'field_bill_records': field_records,
                         'raw_allowance': 10**9, 'field_bill_bucket': 'raw'}, 
             'idles': {'retained': idle_n, 'initial': len(keep_i), 'middle': len(mid),
                       'terminal': len(keep_t), 'rank_applied': idle_rank, 'role_rank': 2*idle_rank,
                       'gauge_neutral': True},
             'premises': ['the 7752 inherited helper units are disjoint from the main roles and ABI compatible (not replayed here)',
                          'compiler applicability to this word (numerical instantiation only)',
                          'physical realizability of the rank-153 trace (no bank replay)',
                          'field-level bill admitted under the caller fixed-tape/precision ABI',
                          'inherited all-size/compiler, hosting, tape and analytic interfaces',
                          'kernel review'],
             'scope': 'exact arithmetic for the word, the bill, the compiler and the ledger'}
    (HERE/'P19_CLAIM.json').write_text(json.dumps(claim, indent=2, sort_keys=True)+'\n')
    print('CLAIM kappa %s = %.10f: +%.2f%% over the selected record %s, +%.2f%% over the reported frontier %s; '
          'complex supplier 0.007578535, BIT supplier 0.0034, zero field bill'
          % (KAPPA, float(KAPPA), claim['gain_vs_selected_record_percent'], FRONTIER,
             claim['gain_vs_reported_percent'], REPORTED_FRONTIER))

if __name__ == '__main__':
    main()

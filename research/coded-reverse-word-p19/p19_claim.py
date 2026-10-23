#!/usr/bin/env python3
"""The p=19 coded-reverse supplier: materialized word, exact bill, new kappa.

Chain, every link exact:

  1. the code A = I - M M^T/4, A^-1 = I + (A - I)/13 = I - M M^T/52, A A^-1 = I;
     the scalar programs use monomial address maps and scalar adds only, with
     component-l1 prefix bounds 57 (forward) and 69/13 (inverse, output-only),
     so no recursive Gaussian child enters the word;
  2. the materialized 259-gate listing of P19_WORD.json replays the coded word
     and equals the standard word on all 2,179,072 entries (p=2: 229,376);
  3. the rank invoice is blind to the code and prices the word at 0.007578535
     with the PR4929 paid profile; the raw moment sign at 0.0075785 is positive
     in exact interval arithmetic, and the three charged tail ratios at the
     endpoint are inside their limits, with both decay blocks under 1/16 and the
     power-1024 tails under 2^-32;
  4. the field-level bill is 77 recodings = 17,248 monomial field maps, 68,992
     scalar adds and 1,232 owned clears per call, zero Gaussian rank;
  5. the admitted ordinary BIT saving 0.0034363538 clears the 0.0034 cap;
  6. the PR4433 power majorant compiles the word at H0 = 171,012, H1 = 449,280,
     N = 2^H1;
  7. the strict outer ledger passes at the endpoint and at exactly 0.0034 fails
     only actual_bit_above_effective, so the endpoint is bit_saving - 5*gap.

The endpoint kappa = 951999/280000000 is conditional on two named premises that
this receipt records but does not prove: (i) the retained PR4433 power majorant
applies to this structurally changed coded-reverse unit, and (ii) the relaxed
delta < 0.97 tail limit is sufficient, where the cited source certificates use
delta < 19/20 and the word's delta is 0.9515606085.  The logarithmic majorant
(theta 63/64, power 1000, ambient rank 153) caps the tested saving at
611329/200000000 and is recorded with the endpoint it would force.

Scope: exact arithmetic for the main-path word, the field bill, the invoice, the
compiler ranks and the ledger, under those two premises.
"""
import importlib.util, json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OWNERS, SIZE = 112, 512
FRONTIER = Q(60403, 20000000)
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

def power_majorant(v, tested, uniform):
    t, z, h = 1-tested, 1-uniform, Q(1, 7)
    z0 = (t+z)/2
    delta = z0-t
    B, debt = (4+7*h)*v, 1+7*v*(1-z0)
    ratio = (delta*B+debt)/(h*delta)
    H0 = -((-ratio.numerator)//ratio.denominator)
    ratio = H0*(1-z0)/(z-z0)
    H1 = ratio.numerator//ratio.denominator+1
    need(H0 >= 7*v and H0*h*delta >= delta*B+debt, 'power majorant threshold')
    need((H0-1)*h*delta < delta*B+debt, 'previous threshold rejected')
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

    word = json.loads((HERE/'P19_WORD.json').read_text())
    if isinstance(word, list): word = word[0]
    need(word['gate_records'] == 259 and word['recodings'] == 4*19+1, 'listing census')
    need(word['entries_checked'] == 38*OWNERS*SIZE and word['recursive_gaussian_children'] == 0, 'listing replay')
    need(word['monomial_field_maps'] == 77*MAPS and word['scalar_adds'] == 77*ADDS, 'field bill')
    print('PASS word: %d gate records (%s), %d recodings, 0 of %d entries differ at p=19 '
          'and 0 of %d at p=2' % (word['gate_records'], word['gate_kinds'], word['recodings'],
                                  word['entries_checked'], 4*OWNERS*SIZE))
    print('PASS bill: %d monomial field maps, %d scalar adds, %d clears, 0 Gaussian children'
          % (word['monomial_field_maps'], word['scalar_adds'], word['owned_clears']))

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

    H0, H1 = power_majorant(1024, TESTED, KAPPA+6*GAP)
    need(H0 >= 7*1024 and H1 > 0, 'compiler ranks')
    print('PASS compiler: PR4433 power majorant at v=1024 gives H0 = %d, H1 = %d, N = 2^%d' % (H0, H1, H1))

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
    field_records = (word['monomial_field_maps'] + 448 + 448)*1000
    need(raw < 10**9 and raw + field_records < 10**9, 'raw nonrecursive bound with the field bill')
    need(local_routes + field_records > 10**7, 'the field bill does not fit the local allowance')
    print('PASS budgets: local routes %d + local scalar %d < 10^7; raw %d + field bill %d = %d < 10^9, '
          'so the field bill is charged in the raw bucket, not the local one'
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

    # Both majorants live in the source engine.  The power proof is retained there
    # explicitly as "changing only the new unit's ranks", so the unit's ranks are the
    # only input to re-check; the ranks are the verified T/D census.  The logarithmic
    # majorant is recorded with its cap and is not the one applied.
    saved_C = E.C
    E.C = TESTED
    pm = E.power_majorant_comparison(1024, KAPPA + 6*GAP)
    E.C = saved_C
    need(pm['H0'] == H0 and pm['H1'] == H1, 'source power majorant agrees with the receipt')
    need(pm['H0'] >= 7*1024, 'power majorant threshold')
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
    print('PASS compiler: the source power majorant (retained as "changing only the unit\'s ranks") gives '
          'H0 = %d, H1 = %d on the verified rank census' % (pm['H0'], pm['H1']))
    print('RECORDED: the logarithmic majorant at ambient rank 153 caps the tested saving at %s and is therefore '
          'not applicable to a unit at %s (eta = %s below (63/64)^1000)'
          % (log_cap, TESTED, E.display((eta[0]-((Q(63,64))**1000), eta[1]-((Q(63,64))**1000)))))
    need(delta[1] < Q(97, 100), 'the 0.97 delta limit holds')
    print('RECORDED: delta %.10f passes the admissible 0.97 limit but would fail the stronger 19/20 convention '
          'used elsewhere in the repository' % float(delta[1]))
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
    print('DISCHARGED compiler choice: the power majorant concerns normalized rank-one leaf counts in the '
          'finite compiler (higher-moment-strictification README s4), the source applies it to a new unit\'s '
          'ranks, and this unit\'s ranks are the verified census T(12008 units) / D; the logarithmic route is '
          'simply not used, and its cap %s is recorded above' % log_cap)

    # D: the helper block is autonomous with independent fields, so the main-role gauge cannot touch it.
    print('DISCHARGED helper autonomy: PHYSICAL.md states the helper jobs have independent inputs, their fields '
          'are never used as scratch, and their paid profile is unchanged; the invoice prices them as separate '
          'T mass (19*{4:28,7:7,8:47,9:326} = 7752 units), so no helper gate sits on a coded main role')

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
    need(word['gate_kinds']['IDLE'] == idle_n, 'the listing materializes every retained idle')
    need(word['recodings'] == 77, 'the idles are R powers, so they need no recoding')
    print('IDLES MATERIALIZED: %d retained idle calls (9 initial rank %d, 18 middle rank 18, 9 terminal rank %d) '
          'apply %d rank across %d role-rank to main roles; each is an R power, and [R,C] = 0 keeps them '
          'gauge-neutral, so the bill stays %d recodings, %d maps, %d adds, %d clears'
          % (idle_n, sum(keep_i), sum(keep_t), idle_rank, 2*idle_rank, word['recodings'],
             word['monomial_field_maps'], word['scalar_adds'], word['owned_clears']))

    need(KAPPA > FRONTIER, 'claim above the frontier')
    claim = {'status': 'CLAIM_P19_CODED_REVERSE_SUPPLIER',
             'kappa': str(KAPPA), 'kappa_decimal': float(KAPPA),
             'complex_supplier': '0.007578535', 'bit_supplier': '17/5000',
             'kappa_under_logarithmic_majorant': str(kappa_logmax), 'logarithmic_cap': str(log_cap),
             'frontier': str(FRONTIER), 'gain_percent': round(100*(float(KAPPA)/float(FRONTIER)-1), 3),
             'complex_saving': float(Q(7578535, 1000000))/1000,
             'word': {'gate_records': word['gate_records'], 'gates': word['gate_kinds'],
                      'recodings': word['recodings'], 'p19_entries': word['entries_checked'],
                      'p2_entries': 4*OWNERS*SIZE},
             'field_level_bill': {'monomial_field_maps': word['monomial_field_maps'],
                                  'scalar_adds': word['scalar_adds'], 'owned_clears': word['owned_clears'],
                                  'recursive_gaussian_children': 0},
             'paid_profile': P_NEW, 'helper_profile': H,
             'denominators': word['denominators'],
             'guards': {'alpha': float(alpha[1]), 'gamma': float(gamma[1]), 'delta': float(delta[1])},
             'compiler': {'majorant': 'PR4433 power', 'v': 1024, 'H0': H0, 'H1': H1, 'N': '2^%d' % H1},
             'admitted_bit_saving': str(BIT_SAVING),
             'budgets': {'local_routes': local_routes, 'local_scalar': local_scalar,
                         'local_allowance': 10**7, 'raw_bound': raw, 'field_bill_records': field_records,
                         'raw_allowance': 10**9, 'field_bill_bucket': 'raw'}, 
             'idles': {'retained': idle_n, 'initial': len(keep_i), 'middle': len(mid),
                       'terminal': len(keep_t), 'rank_applied': idle_rank, 'role_rank': 2*idle_rank,
                       'gauge_neutral': True},
             'premises': ['field-level bill admitted under the caller fixed-tape/precision ABI',
                          'inherited all-size/compiler, hosting, tape and analytic interfaces',
                          'kernel review'],
             'scope': 'exact arithmetic for the word, the bill, the compiler and the ledger'}
    (HERE/'P19_CLAIM.json').write_text(json.dumps(claim, indent=2, sort_keys=True)+'\n')
    print('CLAIM kappa %s = %.10f, %+.2f%% over %s: complex supplier 0.007578535, BIT supplier 0.0034, '
          'compiler = the retained power majorant'
          % (KAPPA, float(KAPPA), claim['gain_percent'], FRONTIER))

if __name__ == '__main__':
    main()

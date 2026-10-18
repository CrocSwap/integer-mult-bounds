# SPDX-License-Identifier: Apache-2.0
"""Scope D: the complete T74 profile, physical stock, endpoint and kappa of PR #2751, and the comparison with
PR2733@2761b52b.

schedule(): the T74 template is PR2269's (research/gmx-t74-borrow43/GLOBAL-TEMPLATE.json.gz at b479fc55, with the T37
inputs template of the same commit), read from git objects, not from PR2751; check_fill.template_structure checks the
per-replica events, recipe and child ranks; check_fill.order_projection the inherited interleaving rule; the
block-level windows (check_fill.block_windows) must equal the event-position windows of the vendored
fill_check80.derive_schedule (check_fill.windows_agree).

price(): every row of a FILL.json.gz is checked against rules R-a..R-e and the R-c recount by two implementations,
check_fill.check_rows (own) and fill_check80.check_roles (vendored PR2387), with the local profiles and helper
widths taken from scope A's frame recounts (not from the words' reports); both must give the same idle and complete
profile (pricing.two_impl), and every priced fill must carry that comparison (pricing.two_impl_ran, checked in
verify.py for PR2751, PR2733, #2766 and #2767).  check_fill.check_rows reads its helper count from check_fill.CLAIM['helpers']; this
module sets it to the recounted helper count for the duration of the call (the file bytes are not modified).

pricing_checks() then checks (rule ids pricing.*): claim_files (CLAIM.json profile = PROFILE.json), profile_claim
(complete profile = CLAIM.json), mass (sum r*n_r = (m-1)W + 64N = 72W + 64N), idle_identical (PR2751's idle
remainders = PR2733's), delta (complete PR2751 - PR2733 = 2664(H8-H7-H1) = 666 x the per-word delta), physical (W + 8
+ helpers + private buffers + 2 from the words = README's 66801 = 66304+415+8+72+2), endpoint_format (C has 24
decimals, upper = C + 1e-24), endpoint_accept (the rigorous enclosure of M(C) has upper end < 1), endpoint_reject (the enclosure of
M(C + 1e-24) has lower end > 1), kappa (CLAIM kappa = C - 1e-46 - 1e-70 exactly) and improvement (PR2733's profile
is rejected at PR2751's C and PR2751's profile accepted at PR2733's C).  The enclosure is check_accounting.moment (exact atanh logs, 2^-640 fixed-point
directed-rounding exp); bisection to a point where the enclosure straddles 1 brackets the root.

head_comparison() compares PR2751 with PR2733's head refit a63c55ff (research/concentrated-prelife-refit/CLAIM.json):
that CLAIM compares against 2761b52b (pricing.head_claim), its complete profile is rejected at PR2751's C by the same
enclosure (pricing.head_rejected), its C is below PR2751's (pricing.head_gap), and PR2751 - head = 2664(H8-H7-H1) +
666(2H1-H2) exactly (pricing.head_delta); verify.py also runs endpoint_check on the head's own C (positive control).
"""
import re
from collections import Counter, defaultdict

import audit_lib as AL
import check_accounting as CA
import check_fill as CF
import fill_check80 as FC
from audit_common import need

V, M, T, STAGES = 112, 73, 74, 9
FPR = 2 * 4 * V
W = FPR * T
CALLS = STAGES * T
E24 = AL.Fraction(1, 10 ** 24)
KAPPA_TERMS = (AL.Fraction(1, 10 ** 46), AL.Fraction(1, 10 ** 70))
FILL_COLUMNS = ['time', 'helper', 'owner_replica', 'child', 'port', 'offset']
PROVIDER_OF = (('gauge44', 'base'), ('extra', 'extra'))


# --------------------------------------------------------------------------------------------- schedule ---
def schedule(tpl, t37, order):
    stage_pair, rank, info = CF.template_structure(tpl, t37)
    CF.order_projection(order)
    win, pair_of, side_of = CF.block_windows(tpl, order, stage_pair, rank)
    sched = FC.derive_schedule(T, tpl, order)
    wt = CF.windows_agree(win, sched)
    return dict(stage_pair=stage_pair, rank=rank, win=win, pair_of=pair_of, side_of=side_of, sched=sched,
                info=dict(calls=info['calls'], per_replica_events=info['per_replica_events'],
                          t37_events_recipe_ranks_equal=info['t37_events_recipe_ranks_equal'],
                          child_ranks=dict((str(k), v) for k, v in sorted(Counter(rank.values()).items())),
                          windows=len(win), windows_sha256=AL.sha(sorted([list(k), v] for k, v in wt.items()))))


def dispatch_map(dispatch_list, order):
    disp = dict(((s, r), p) for s, r, p in dispatch_list)
    need(len(disp) == len(dispatch_list) == len(order) == CALLS and sorted(disp) == sorted(order)
         and set(disp.values()) <= set(p for p, _ in PROVIDER_OF),
         'pricing.dispatch: dispatch does not cover the %d calls once with known providers' % CALLS)
    return disp


# ------------------------------------------------------------------------------------------------ fill ---
def own_rows(rows, order, disp, widths, local, sc, helpers, skip=()):
    saved = CF.CLAIM['helpers']
    CF.CLAIM['helpers'] = helpers
    try:
        return CF.check_rows(rows, order, disp, widths, local, sc['rank'], sc['win'], sc['pair_of'], sc['side_of'],
                             sc['stage_pair'], skip)
    finally:
        CF.CLAIM['helpers'] = saved


def fc_rows(rows, order, disp, widths, sc):
    return [CF.fc_row(z, order, disp, widths, sc['pair_of'], sc['side_of']) for z in rows]


def vendored_rows(drows, order, disp, widths, local, sc, helpers):
    ctx = dict(T=T, R=helpers, W=W, order=order, dispatch=disp, widths=widths, local_profiles=local)
    return FC.check_roles(ctx, sc['sched'], drows)


def compare_impl(own, fc):
    """pricing.two_impl; returns the comparison record that price() stores as 'two_impl' (check_two_impl_ran)."""
    need(fc['idle'] == AL.hist(own['idle']) and fc['profile'] == AL.hist(own['profile'])
         and fc['rank_mass'] == own['rank_mass'],
         'pricing.two_impl: fill_check80 idle/profile/mass != check_rows')
    return dict(idle_equal=True, profile_equal=True, rank_mass_equal=True, roles=own['roles'])


def check_two_impl_ran(priced):
    """pricing.two_impl_ran: every priced fill (name -> price() result) carries the two-implementation comparison."""
    bad = sorted(k for k, p in priced.items() if not (p.get('two_impl') and p['two_impl'].get('roles') ==
                                                       p['own']['roles']))
    need(sorted(priced) == ['pr2733', 'pr2751', 'pr2766', 'pr2767'], 'pricing.two_impl_ran: priced fills %r'
         % sorted(priced))
    need(not bad, 'pricing.two_impl_ran: no two-implementation comparison for %r' % bad)
    AL.ran('pricing.two_impl_ran')
    return dict((k, True) for k in sorted(priced))


def price(fill, order, disp, words, recounts, sc, keep_drows=False, fc_hook=None):
    """words: {'gauge44': base word, 'extra': extra word}; recounts: the same keys -> scope A frame recounts.
    fc_hook (negative controls only): applied to the vendored implementation's result before the comparison."""
    need(fill['columns'] == FILL_COLUMNS and fill['dispatch_overrides'] == [], 'pricing.fill_format: columns/overrides')
    widths, local, ended = {}, {}, {}
    for pid in words:
        widths[pid], ended[pid] = CF.word_widths(words[pid])
        need(widths[pid] == recounts[pid]['helper_widths'], 'pricing.widths: word widths != recount (%s)' % pid)
        local[pid] = Counter(recounts[pid]['paid'])
    helpers = len(widths['gauge44'])
    need(all(len(x) == helpers for x in widths.values()), 'pricing.widths: helper count differs between providers')
    rows = fill['rows']
    own = own_rows(rows, order, disp, widths, local, sc, helpers)
    drows = fc_rows(rows, order, disp, widths, sc)
    fc = vendored_rows(drows, order, disp, widths, local, sc, helpers)
    if fc_hook is not None:
        fc = fc_hook(fc)
    two = compare_impl(own, fc)
    return dict(own=own, fc=fc, two_impl=two, widths=widths, local=local, helpers=helpers, buffers=len(ended['gauge44']),
                buffers_by_provider=dict((p, len(e)) for p, e in ended.items()), drows=drows if keep_drows else None)


def summary(pr):
    own = pr['own']
    return dict(roles=own['roles'], idle=AL.hist(own['idle']), idle_remainders=own['idle_remainders'],
                profile=AL.hist(own['profile']), rank_mass=own['rank_mass'], deficit=own['deficit'],
                hosted_width=own['hosted_width'], capacity=own['capacity'],
                cross_replica_roles=own['cross_replica_roles'], occupied_bins=own['occupied_bins'], bins=own['bins'],
                helpers=pr['helpers'], private_buffers=pr['buffers'],
                vendored_fill_check80=dict(roles=pr['fc']['roles'], idle=pr['fc']['idle'], profile=pr['fc']['profile'],
                                           rank_mass=pr['fc']['rank_mass']))


# -------------------------------------------------------------------------------------------- endpoint ---
def endpoint_check(prof, C, upper):
    """C accepted (upper end of the enclosure of M(C) below 1) and upper = C + 1e-24 rejected (lower end of the
    enclosure of M(upper) above 1)."""
    need(upper - C == E24, 'pricing.endpoint_format: upper - C != 1e-24')
    lo, hi = CA.moment(prof, C)
    need(CA.accepts((lo, hi)), 'pricing.endpoint_accept: M(C) enclosure [%.3e, %.3e] - 1 does not lie below 0'
         % (float(lo - 1), float(hi - 1)))
    lo2, hi2 = CA.moment(prof, upper)
    need(CA.rejects((lo2, hi2)), 'pricing.endpoint_reject: M(C + 1e-24) enclosure [%.3e, %.3e] - 1 does not lie '
         'above 0' % (float(lo2 - 1), float(hi2 - 1)))
    return dict(C_moment_minus_1=['%.9e' % float(lo - 1), '%.9e' % float(hi - 1)],
                C_plus_1e24_moment_minus_1=['%.9e' % float(lo2 - 1), '%.9e' % float(hi2 - 1)],
                C_enclosure_width='%.2e' % float(hi - lo))


def straddle(prof, C):
    """Bisection on [C, C + 1e-24] until the enclosure of M straddles 1 (neither accepted nor rejected).  Returns
    (lo_a, hi_a, s): every point <= lo_a tested is accepted, hi_a rejected, s the straddle point."""
    lo_a, hi_a = C, C + E24
    for _ in range(2000):
        mid = (lo_a + hi_a) / 2
        e = CA.moment(prof, mid)
        if CA.accepts(e):
            lo_a = mid
        elif CA.rejects(e):
            hi_a = mid
        else:
            return lo_a, hi_a, mid
    raise AL.AuditFail('pricing.root_bracket: no straddle point found')


def kappa_check(kappa, C):
    need(kappa == C - KAPPA_TERMS[0] - KAPPA_TERMS[1], 'pricing.kappa: CLAIM kappa != C - 1e-46 - 1e-70')


def physical(words_widths_buffers, readme_text):
    """W + 8 + helpers + private buffers + 2 from the words, against README's 'physical<N> = <W>+<R>+8+<Z>+2'."""
    m = re.search(r'physical\s*(\d+)\s*=\s*(\d+)\+(\d+)\+(\d+)\+(\d+)\+(\d+)', readme_text)
    need(m is not None, 'pricing.physical: README stock statement not found')
    claim = [int(x) for x in m.groups()]
    helpers, buffers = words_widths_buffers
    terms = [W, helpers, 8, buffers, 2]
    got = sum(terms)
    need([got] + terms == claim, 'pricing.physical: own %d = %r != README %r' % (got, terms, claim))
    return dict(physical=got, terms=dict(live=W, helpers=helpers, centres=8, private_buffers=buffers, coefficient=2))


# ------------------------------------------------------------------------------------------------ checks ---
def check_claim_files(claim51, profile51):
    need(AL.intkeys(claim51['profile']) == AL.intkeys(profile51), 'pricing.claim_files: CLAIM.json profile != PROFILE.json')


def check_profile_claim(prof, claim):
    need(prof == AL.intkeys(claim['profile']), 'pricing.profile_claim: complete profile %r != CLAIM %r'
         % (prof, claim['profile']))


def check_mass(prof):
    mass = sum(r * n for r, n in prof.items())
    need(mass == (M - 1) * W + 64 * CALLS, 'pricing.mass: rank mass %d != 72W + 64N' % mass)
    return mass


def check_idle(own51, own33):
    need(own51['idle'] == own33['idle'], 'pricing.idle_identical: idle remainders differ')


def check_delta(prof51, prof33, local_delta):
    delta = AL.counter_delta(prof51, prof33)
    want = dict((k, CALLS * v) for k, v in local_delta.items())
    need(delta == want and want == {1: -2664, 7: -2664, 8: 2664}, 'pricing.delta: complete delta %r != 666 x %r'
         % (delta, local_delta))
    return delta


def check_improvement(prof33, prof51, C51, C33):
    need(CA.rejects(CA.moment(prof33, C51)) and CA.accepts(CA.moment(prof51, C33)),
         'pricing.improvement: PR2733 profile not rejected at PR2751 C (or PR2751 profile not accepted at PR2733 C)')


def pricing_checks(p51, p33, claim51, profile51, claim33, local_delta, readme51, phys_counts):
    """The checks of the module docstring, in this order."""
    prof51, prof33 = p51['own']['profile'], p33['own']['profile']
    check_claim_files(claim51, profile51)
    mass = check_mass(prof51)
    check_profile_claim(prof51, claim51)
    check_idle(p51['own'], p33['own'])
    delta = check_delta(prof51, prof33, local_delta)
    phys = physical(phys_counts, readme51)
    C, upper = AL.Fraction(claim51['complex_lower']), AL.Fraction(claim51['complex_upper'])
    need((C * 10 ** 24).denominator == 1, 'pricing.endpoint_format: C is not a 24-digit decimal')
    enc = endpoint_check(prof51, C, upper)
    kappa_check(AL.Fraction(claim51['kappa']), C)
    C33 = AL.Fraction(claim33['complex_lower'])
    check_improvement(prof33, prof51, C, C33)
    kappa = AL.Fraction(claim51['kappa'])
    return dict(complete_profile=AL.hist(prof51), complete_profile_equals_claim=prof51 == AL.intkeys(claim51['profile']),
                profile_json_equals_claim=AL.intkeys(profile51) == AL.intkeys(claim51['profile']),
                rank_mass=mass, rank_mass_equals_72W_plus_64N=mass == 72 * W + 64 * CALLS,
                idle_identical_to_pr2733=p51['own']['idle'] == p33['own']['idle'],
                complete_delta_vs_pr2733=AL.hist(delta), physical=phys, endpoint=enc, C=CA.dec(C, 24),
                C_minus_kappa_times_1e70=str((C - kappa) * 10 ** 70),
                kappa_equals_C_minus_1e46_minus_1e70=kappa == C - KAPPA_TERMS[0] - KAPPA_TERMS[1],
                pr2733_profile_rejected_at_C=CA.rejects(CA.moment(prof33, C)),
                pr2751_profile_accepted_at_C2733=CA.accepts(CA.moment(prof51, C33))), C


# ------------------------------------------------------------------------ PR2733 head (a63c55ff) comparison ---
def formula_delta():
    """2664(H8-H7-H1) + 666(2H1-H2) as {rank: change}."""
    d = {}
    for k, v in ((8, 2664), (7, -2664), (1, -2664), (1, 2 * 666), (2, -666)):
        d[k] = d.get(k, 0) + v
    return dict((k, v) for k, v in sorted(d.items()) if v)


def head_comparison(prof51, claim_head, C51, base_commit):
    """PR2733's head refit (a63c55ff, research/concentrated-prelife-refit/CLAIM.json) against PR2751 (rule ids
    pricing.head_*): the head CLAIM compares against base_commit (2761b52b, PR2751's comparison base); its complete
    profile is rejected at PR2751's C by the same enclosure (head_rejected); its C is below PR2751's (head_gap); and
    PR2751 - head = 2664(H8-H7-H1) + 666(2H1-H2) exactly (head_delta)."""
    prof_h = AL.intkeys(claim_head['global_profile'])
    Ch = AL.Fraction(claim_head['complex_lower'])
    need(claim_head['comparison']['head'] == base_commit, 'pricing.head_claim: the head compares against %s'
         % claim_head['comparison']['head'])
    lo, hi = CA.moment(prof_h, C51)
    need(CA.rejects((lo, hi)), 'pricing.head_rejected: the head profile is not rejected at PR2751 C (M-1 in '
         '[%.3e, %.3e])' % (float(lo - 1), float(hi - 1)))
    gap = C51 - Ch
    need(gap > 0, 'pricing.head_gap: PR2751 C - head C = %s is not positive' % gap)
    delta = AL.counter_delta(prof51, prof_h)
    want = formula_delta()
    need(delta == want, 'pricing.head_delta: PR2751 - head %r != 2664(H8-H7-H1)+666(2H1-H2) = %r' % (delta, want))
    AL.ran('pricing.head')
    return dict(head_profile=AL.hist(prof_h), head_C=CA.dec(Ch, 24), comparison_head=claim_head['comparison']['head'],
                pr2751_minus_head=AL.hist(delta), pr2751_minus_head_as='2664(H8-H7-H1) + 666(2H1-H2)',
                head_profile_rejected_at_pr2751_C=True,
                head_M_minus_1_at_pr2751_C=['%.9e' % float(lo - 1), '%.9e' % float(hi - 1)],
                C_gap=CA.dec(gap, 24), C_gap_approx='%.3e' % float(gap))


# ---------------------------------------------------------------------------------------- fill mutants ---
def fill_index(rows, order, disp, widths, sc):
    """Lookup tables for the fill mutants: (call, family) -> row, bin -> rows, top slice of each bin."""
    def fam(o, c, p):
        return o * FPR + (2 * sc['pair_of'][c] + sc['side_of'][c]) * V + p
    fam_at, bins = {}, defaultdict(list)
    for q, (t, h, o, c, p, off) in enumerate(rows):
        fam_at[t, fam(o, c, p)] = q
        bins[o, c, p].append(q)
    def wd(z):
        return widths[disp[order[z[0]]]][z[1]]
    top = {}
    for b, members in bins.items():
        q = max(members, key=lambda k: rows[k][5])
        top[b] = (q, rows[q][5] + wd(rows[q]))
    return fam, fam_at, bins, top, wd

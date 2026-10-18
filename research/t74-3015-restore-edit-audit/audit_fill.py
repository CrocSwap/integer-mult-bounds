# SPDX-License-Identifier: Apache-2.0
"""Scope C: PR #3015's literal T74 allocation (FILL/ORDER/DISPATCH byte-identical to PR #2979's) priced with the
recounted local profiles of the edited words, in two implementations (this contributor's own check_rows of PR2804
and the vendored fill_check80 of PR2387), and scope E's journal application for PR #3018.

schedule()      the T74 template (PR2269's GLOBAL-TEMPLATE, read at b479fc55) and the T37 inputs template (equal to
                PR2979's allocation/vendor/TEMPLATE.json.gz), the order's per-replica projection, the block-level
                windows against the event-position windows of the vendored derive_schedule.
price()         every fill row against rules R-a..R-e in both implementations, the R-c recount (idle remainders,
                complete profile), with the helper widths and local profiles taken from the frame recounts of the
                words given (not from the words' reports), and the two-implementation comparison (fill.two_impl).
check_*()       the complete profile against PROFILE.json and CLAIM.json (fill.profile_file, fill.profile_claim),
                the rank-mass identity (fill.mass), the complete delta against PR2979 = 666 x the local delta
                (fill.delta), the unchanged idle remainders (fill.idle), the physical stock W + helpers + 8 + buffers
                + 2 against CLAIM.json (fill.physical).
apply_journal() PR3018's EXCHANGE.json edits [row index, old row, new row] applied to PR2979's rows; every preimage
                must match (journal.preimage) and every index be distinct (journal.index).
Standard library only; Python 3.8-compatible syntax.
"""
import hashlib
from collections import Counter, defaultdict

import audit_lib as AL
import check_fill as CF
import fill_check80 as FC
from audit_common import need

V, M, T, STAGES = 112, 73, 74, 9
FPR = 2 * 4 * V
W = FPR * T
CALLS = STAGES * T
FILL_COLUMNS = ['time', 'helper', 'owner_replica', 'child', 'port', 'offset']
PROVIDER_OF = (('gauge44', 'base'), ('extra', 'extra'))


# ------------------------------------------------------------------------------------------------ schedule ---
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
         'fill.dispatch: dispatch does not cover the %d calls once with known providers' % CALLS)
    return disp


# ---------------------------------------------------------------------------------------------------- fill ---
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
    need(fc['idle'] == AL.hist(own['idle']) and fc['profile'] == AL.hist(own['profile'])
         and fc['rank_mass'] == own['rank_mass'],
         'fill.two_impl: fill_check80 idle/profile/mass != check_rows')
    return dict(idle_equal=True, profile_equal=True, rank_mass_equal=True, roles=own['roles'])


def price(fill, order, disp, words, recounts, sc, keep_drows=False, fc_hook=None):
    """words: {'gauge44': base word, 'extra': extra word}; recounts: the same keys -> frame recounts (scope B).
    fc_hook (negative controls only): applied to the vendored implementation's result before the comparison."""
    need(fill['columns'] == FILL_COLUMNS and fill['dispatch_overrides'] == [], 'fill.format: columns/overrides')
    widths, local, ended = {}, {}, {}
    for pid in words:
        widths[pid], ended[pid] = CF.word_widths(words[pid])
        need(widths[pid] == recounts[pid]['helper_widths'], 'fill.widths: word widths != recount (%s)' % pid)
        local[pid] = Counter(recounts[pid]['paid'])
    helpers = len(widths['gauge44'])
    need(all(len(x) == helpers for x in widths.values()), 'fill.widths: helper count differs between providers')
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
    return dict(roles=own['roles'], idle=AL.hist(own['idle']), profile=AL.hist(own['profile']),
                rank_mass=own['rank_mass'], deficit=own['deficit'], hosted_width=own['hosted_width'],
                capacity=own['capacity'], cross_replica_roles=own['cross_replica_roles'],
                occupied_bins=own['occupied_bins'], bins=own['bins'], helpers=pr['helpers'],
                private_buffers=pr['buffers'], two_impl=pr['two_impl'],
                vendored_fill_check80=dict(roles=pr['fc']['roles'], idle=pr['fc']['idle'], profile=pr['fc']['profile'],
                                           rank_mass=pr['fc']['rank_mass']))


# -------------------------------------------------------------------------------------------------- checks ---
def check_profile(prof, claimed, rule):
    need(prof == AL.intkeys(claimed), '%s: complete profile %r != %r' % (rule, AL.hist(prof), claimed))


def check_mass(prof):
    mass = sum(r * n for r, n in prof.items())
    need(mass == (M - 1) * W + 64 * CALLS, 'fill.mass: rank mass %d != 72W + 64N' % mass)
    return mass


def check_delta(prof_new, prof_old, local_delta):
    delta = AL.counter_delta(prof_new, prof_old)
    want = dict((k, CALLS * v) for k, v in local_delta.items())
    need(delta == want, 'fill.delta: complete delta %r != 666 x %r' % (delta, local_delta))
    return delta


def check_idle(own_new, own_old):
    need(own_new['idle'] == own_old['idle'], 'fill.idle: idle remainders differ')


def physical(helpers, buffers, claim):
    terms = dict(live=W, helpers=helpers, centres=8, private_buffers=buffers, coefficient=2)
    got = sum(terms.values())
    need(claim['live_families'] == W and claim['helpers'] == helpers and claim['zero_buffers'] == buffers
         and claim['physical_families'] == got,
         'fill.physical: own %d = %r != CLAIM %r' % (got, terms, dict((k, claim[k]) for k in
                                                                       ('live_families', 'helpers', 'zero_buffers',
                                                                        'physical_families'))))
    return dict(physical=got, terms=terms)


def fill_sha256(raw):
    return hashlib.sha256(raw).hexdigest()


# ------------------------------------------------------------------------------------------------ journal ---
def apply_journal(fill, edits):
    rows = list(fill['rows'])
    seen = set()
    for k, (idx, old, new) in enumerate(edits):
        need(isinstance(idx, int) and 0 <= idx < len(rows) and idx not in seen, 'journal.index: edit %d index %r' % (k, idx))
        seen.add(idx)
        need(rows[idx] == old, 'journal.preimage: edit %d: row %d is %r, not %r' % (k, idx, rows[idx], old))
        need(isinstance(new, list) and len(new) == 6 and new[:2] == old[:2], 'journal.row: edit %d keeps call and helper' % k)
        rows[idx] = list(new)
    return dict(fill, rows=rows), dict(edits=len(edits), rows_changed=len(seen),
                                         location_changes=sum(1 for _, o, n in edits if o[2:5] != n[2:5]),
                                         offset_only_changes=sum(1 for _, o, n in edits if o[2:5] == n[2:5]))


# --------------------------------------------------------------------------------------- control helpers ---
def fill_index(rows, order, disp, widths, sc):
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


def legal_move(rows, order, disp, widths, sc):
    """A fill that still satisfies R-a..R-e but has a different idle histogram."""
    fam, fam_at, bins, top, wd = fill_index(rows, order, disp, widths, sc)
    for b in sorted(bins):
        if len(bins[b]) < 2:
            continue
        q = top[b][0]
        t, h, o, c, p, off = rows[q]
        w = wd(rows[q])
        for p2 in range(V):
            if (o, c, p2) not in bins and (t, fam(o, c, p2)) not in fam_at and w <= sc['rank'][c]:
                rr = list(rows)
                rr[q] = [t, h, o, c, p2, 0]
                return rr, q, 'top slice of bin %r (width %d) moved to the empty bin %r' % (b, w, (o, c, p2))
    raise AL.AuditFail('control: no legal move found')

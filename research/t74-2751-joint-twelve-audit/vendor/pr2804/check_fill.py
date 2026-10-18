# SPDX-License-Identifier: Apache-2.0
"""Scope B: PR #2530's diagonal call order, windows, owner fill (evidence/eight-fill.json.gz) and physical stock.

What is proved (rules R-a..R-g of the PR858 / T16 hosting lineage, as restated in the vendored fill_check80.py
of PR2387; the T74 template is PR2269's, read at b479fc55 and equal to PR2462's copy):
  * order: eight-order.json = SPEC.call_order = PLAN.order = the 666 (stage, replica) calls sorted by
    (4*stage + replica, stage, replica); every replica runs stages 0..8 in increasing order (the per-replica
    projection, which is what the inherited interleaving rule requires); same call set as PR2462's ORDER;
  * template: 30 per-replica events plus the 2 global tail events; no per-replica event names another replica;
    every template call's first 224 owners are the caller's own active pair; the T37 inputs template has the same
    30 events, recipe and child ranks;
  * windows: a new block-level rule window(r,c) = (t_lo, t_hi] in call time equals the older event-position rule
    (fill_check80.derive_schedule; also under PR2462's order and a swapped order), PLAN.json.gz windows/pairs/sides
    and order-screen.json.gz windows (1332 windows, 2220 events, 666 bridges; windows_bound: same number of windows
    and every derived window's rank and call times); PLAN's schedule and template content hashes equal an own
    re-expansion; the derived order and windows are recorded by sha256;
    the event kind that sets each lower end t_lo is recorded; on these windows no call lies in a window of its own
    replica's active pair (its local sweep touches that pair), so R-e's active-pair rule is implied by R-d here;
  * widths: 422 live helpers per call, GF(2) widths = word report = eight-providers (ordered) = PLAN, 78 zero buffers;
    the local paid profiles are check_words' frame-chain recounts (equal to the words' report, eight-providers and
    the claim), so the global profile below rests on the recount, not on the report;
  * fill: every row of eight-fill.json.gz passes R-a (one role per call and helper), R-e (family identity,
    namespace, not on the caller's active pair, one helper per family per call), R-d (strictly inside its window),
    R-b (capacity, disjoint, prefix-contiguous bins) and the R-c recount (idle remainders, global profile = SPEC =
    PROFILE.json = PLAN, rank-mass identities, halving guard).  R-a..R-e are checked by two implementations (the
    own check_rows and the vendored fill_check80.check_roles); R-g (X2 pending axes, 7023 distinct 73-column
    charts = SPEC) only by the vendored fill_check80.pending_axes_and_charts; R-f (private namespace) is replaced
    by the physical stock and namespace-receipt check below;
  * physical stock 66814 = 66304 + 8 + 422 + 78 + 2, hosts inside the data namespace; in every call the 224
    active-pair families and the 422 host families are disjoint, so exactly 646 families are busy per call (asserted
    per call); against receipts/INDEPENDENT-GLOBAL.json: the own row coefficient 19545 (< 20161), stock bits and
    payload equal the receipt's, and the receipt's stock and five namespace intervals equal the own stock and its
    boundaries (namespace_receipt; the receipt values are recorded next to the own ones; the global prefix bits are
    checked in check_accounting);
  * order dependence (diagnostic): re-timed to PR2462's order, 60541 roles leave their windows.  Each of the 665
    adjacent swaps of two calls of different replicas is scored on R-d (the only call-time rule) through its two
    swapped calls: 238 keep every role in its window and 427 break at least one (the first at position 5; positions
    0-4 are legal).  The scan is cross-checked by a full re-timing at six positions;
  * negative controls, each asserting the rule that rejects it.  Order, windows and template (7): the diagonal
    formula applied to PR2462's order; the fill re-timed to PR2462's order; a per-replica stage inversion; the
    first breaking adjacent cross-replica swap; the block-rule windows compared with the event-rule windows of that
    swapped order; the active-pair lemma on one window widened to all calls; a template event given a cross-replica
    field.  Fill and stock (14): 11 fill mutants and the busy-family mutant must each be rejected first by its
    named rule id and, re-run with the rejecting ids skipped one at a time, break exactly its listed ids (R-a, R-b,
    R-c, R-d, R-e or the busy-family count, plus R-c.mass where that recount identity is the arithmetic
    consequence), and the vendored fill_check80 must reject each of the 11 fill mutants by the same rule id (the
    busy-family count has no counterpart there); they include roles placed exactly at both window ends (t = hi + 1,
    and t = lo of a window whose lower end is set by a bridge), and a host on the caller's active pair inside a
    window widened for that control (on the real windows R-d would reject it first).  Two R-g controls go through
    the vendored pending_axes_and_charts: an X2 pending-axis overlap (R-g.pending_axes) and a fill with one chart
    fewer than SPEC (R-g.charts).  Provenance (2): the INDEPENDENT-GLOBAL namespace with one interval shifted
    (physical.namespace_receipt) and a PLAN window with one call time dropped (windows.plan), each through the
    function the main check uses.
Scope limits: the window semantics and the free interleaving of independent replica controllers are inherited
modelling assumptions, not re-derived; the PR's emit/audit/invoice/native pipeline under the new order is not run.
"""
import gzip
import hashlib
import json
from collections import Counter, defaultdict

import fill_check80 as FC
from audit_common import AuditFail, attempt, need

V, H, M, T, STAGES, PAIRS = 112, 9, 73, 74, 9, 4
FPR = 2 * PAIRS * V                       # 896 data families per replica
W = FPR * T                               # 66304
CLAIM = dict(idle={1: 21976, 3: 6662, 5: 440, 8: 114, 16: 172, 32: 3, 48: 26488},
             profile={1: 1599730, 2: 420912, 3: 219782, 4: 78588, 5: 17756, 7: 5328, 8: 114, 16: 172, 32: 3, 48: 26488},
             local={1: 2369, 2: 632, 3: 320, 4: 118, 5: 26, 7: 8}, physical=66814, helpers=422, roles=281052)
# Rule ids of rejections ('rule: detail'); the R-* ids are fill_check80.check_roles's.
RULES = ('R-a.count', 'R-a.schema', 'R-a.call', 'R-a.helper_range', 'R-a.duplicate_helper', 'R-a.complete',
         'R-e.coords', 'R-e.namespace', 'R-e.active_pair', 'R-e.family_unique_per_call', 'R-d.window',
         'R-b.capacity', 'R-b.overlap', 'R-b.prefix', 'R-c.mass', 'order.inventory', 'order.projection',
         'physical.busy_families')


def intkeys(d):
    return dict((int(k), v) for k, v in d.items())


# ---------------------------------------------------------------------------------- template and order ---
def template_structure(tpl, t37):
    """Per-replica events touch only their own replica; the global tail comes last; template calls own their
    active pair; the T37 inputs template (used by the PR's search) has the same events, recipe and child ranks."""
    src = tpl['execution_schedule']
    need(len(src) == 32 and [e['kind'] for e in src[30:]] == ['bank_padding_cover_sweep', 'translate_every_live_family'],
         'template: global tail = last two events')
    stage_pair = dict((e['stage'], e['pair']) for e in tpl['recipe'] if e['kind'] == 'local')
    need(sorted(stage_pair) == list(range(STAGES)), 'template: recipe stages')
    fields = defaultdict(set)
    for e in src[:30]:
        fields[e['kind']].add(tuple(sorted(e)))
        need(e['kind'] in ('local_cover_sweep', 'idle_cover_sweep', 'bridge', 'terminal_Y_translations', 'terminal'),
             'template: event kind')
        need('replicas' not in e or e['replicas'] == list(range(T)), 'template: replicas field covers T74')
        need(not any(k in e for k in ('replica', 'src_replica', 'dst_replica', 'owner_replica')),
             'template.cross_replica_field: per-replica event %r names a replica' % e['kind'])
        need(e['kind'] != 'bridge' or (0 <= e['src'] < PAIRS and 0 <= e['dst'] < PAIRS), 'template: bridge pairs')
    rank = {}
    for c in tpl['idle_children']:
        need(c['replicas'] == T and rank.setdefault(c['child'], c['rank']) == c['rank'], 'template: idle child')
    need(len(tpl['idle_children']) == V * len(rank), 'template: idle child records')
    local_pair, owner_kinds = 0, Counter()
    for c in tpl['calls']:
        base = c['replica'] * FPR + 2 * stage_pair[c['stage']] * V
        fams = [f for f, _ in c['owners']]
        local_pair += sorted(fams[:2 * V]) == list(range(base, base + 2 * V))
        owner_kinds.update('data' if f < W else 'bank' for f in fams[2 * V:])
    need(local_pair == len(tpl['calls']) == STAGES * T, 'template: calls own their active pair')

    def strip(e):
        return dict((k, v) for k, v in e.items() if k != 'replicas')
    t37_equal = ([strip(e) for e in t37['execution_schedule'][:30]] == [strip(e) for e in src[:30]] and
                 t37['recipe'] == tpl['recipe'] and set((c['child'], c['port'], c['rank']) for c in t37['idle_children'])
                 == set((c['child'], c['port'], c['rank']) for c in tpl['idle_children']))
    need(t37_equal, 'template: T37 vs T74 events')
    return stage_pair, rank, dict(calls=len(tpl['calls']), calls_owning_active_pair=local_pair,
                                  helper_owner_kinds=dict(owner_kinds), per_replica_events=len(src) - 2,
                                  global_tail_events=sum(1 for e in src[30:]), t37_events_recipe_ranks_equal=t37_equal,
                                  event_fields=dict((k, sorted(map(list, v))) for k, v in sorted(fields.items())))


def diagonal_order():
    return sorted(((s, r) for s in range(STAGES) for r in range(T)), key=lambda x: (4 * x[0] + x[1], x[0], x[1]))


def check_diagonal(order):
    """The order is PR2530's stated formula: the 666 calls sorted by (4*stage + replica, stage, replica)."""
    need(order == diagonal_order(), 'order.diagonal: order != sorted by (4*stage+replica, stage, replica)')


def canon_sha(x):
    """sha256 of canonical JSON (sorted keys, no spaces)."""
    return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def order_projection(order, skip=()):
    """The inherited interleaving rule: any order is admissible if it contains every call once and each replica's
    projection runs its stages 0..8 in increasing order (windows are then recomputed for that order).  `skip`:
    controls only (see check_rows)."""
    need('order.inventory' in skip or sorted(order) == sorted((s, r) for s in range(STAGES) for r in range(T)),
         'order.inventory: call inventory')
    for r in range(T):
        need('order.projection' in skip or [s for s, rr in order if rr == r] == list(range(STAGES)),
             'order.projection: stage order of replica %d' % r)


def block_windows(tpl, order, stage_pair, rank, sources=None, defs=None):
    """New block-level window rule.  Per replica, walk its 30 source events; each event belongs to the block of
    the latest local sweep (stage s), which runs at call time at[(s,r)].  A touch of (r, pair) in block t (the local
    call, a later bridge or a terminal event) excludes calls <= t; an idle sweep in block t admits calls <= t.
    Hence window(r,c) = {t : t_lo < t <= t_hi}, t_lo = -1 if the pair was never touched.  If `sources` is a dict,
    sources[r, c] receives the kind of the event that set t_lo ('none' if untouched); if `defs` is a dict, defs[r, c]
    receives the calls (stage, r) whose times are t_lo (None if untouched) and t_hi."""
    at = dict((tuple(k), t) for t, k in enumerate(order))
    win, pair_of, side_of = {}, {}, {}
    for r in range(T):
        stage, last, kind, call = None, {}, {}, {}
        for e in tpl['execution_schedule'][:30]:
            k = e['kind']
            if k == 'local_cover_sweep':
                stage = e['stage']
                last[stage_pair[stage]] = at[stage, r]
                kind[stage_pair[stage]] = k
                call[stage_pair[stage]] = (stage, r)
            elif k == 'bridge':
                last[e['src']] = last[e['dst']] = at[stage, r]
                kind[e['src']] = kind[e['dst']] = k
                call[e['src']] = call[e['dst']] = (stage, r)
            elif k == 'idle_cover_sweep':
                for side, c in enumerate(e['child_indices']):
                    if c not in rank:
                        continue
                    need((r, c) not in win, 'windows: child swept twice')
                    need(pair_of.setdefault(c, e['pair']) == e['pair'] and side_of.setdefault(c, side) == side,
                         'windows: child pair/side')
                    win[r, c] = (last.get(e['pair'], -1), at[stage, r])
                    if sources is not None:
                        sources[r, c] = kind.get(e['pair'], 'none')
                    if defs is not None:
                        defs[r, c] = (call.get(e['pair']), (stage, r))
            else:   # terminal events touch every pair
                for p in range(PAIRS):
                    last[p] = at[stage, r]
                    kind[p] = k
                    call[p] = (stage, r)
    need(len(win) == T * len(rank), 'windows: inventory')
    return win, pair_of, side_of


def active_pair_outside_own_windows(order, win, pair_of, stage_pair):
    """No call lies in a window (r, c) of its own replica r whose child c is on the call's active pair (the call's
    local sweep touches that pair, which closes every earlier window of it and precedes every later one).  So on
    these windows R-e's active-pair rule is implied by R-d.  Returns the number of (window, call) pairs checked."""
    calls = defaultdict(list)
    for t, (s, r) in enumerate(order):
        calls[r].append((t, stage_pair[s]))
    checked = 0
    for (r, c), (lo, hi) in sorted(win.items()):
        for t, pair in calls[r]:
            if pair == pair_of[c]:
                need(not lo < t <= hi, 'windows.active_pair_lemma: call %d lies in window (%d,%d] of its own active '
                     'pair (child %d)' % (t, lo, hi, c))
                checked += 1
    return checked


def windows_agree(win, sched):
    """The own block rule and fill_check80's event-position rule (derive_schedule) give the same windows, as
    lists of call times.  Returns them."""
    wt = dict((k, list(range(lo + 1, hi + 1))) for k, (lo, hi) in win.items())
    need(sched['window_times'] == wt, 'windows.block_vs_event: block rule != fill_check80 event-position rule')
    return wt


def adjacent_swap_scan(order, defs, by_call):
    """Diagnostic: every adjacent pair of calls of different replicas is swapped in turn and the roles of PR2530's
    fill that leave their windows are counted.  Only R-d depends on call time (R-a, R-b, R-c and R-e depend on the
    call's (stage, replica), bins and families, which move with the call).  A swap at k only moves window ends
    between k and k + 1, so only the roles of the two swapped calls can change legality; they are checked against
    the windows recomputed from each window's defining calls (defs, from block_windows).  by_call[t] lists the
    (owner, child) of the roles of call t.  Returns {k: roles out of window} for the cross-replica swaps."""
    at = dict((x, t) for t, x in enumerate(order))
    out = {}
    for k in range(len(order) - 1):
        a, b = order[k], order[k + 1]
        if a[1] == b[1]:
            continue
        at2 = {a: k + 1, b: k}

        def time(x):
            return -1 if x is None else at2.get(x, at[x])
        bad = 0
        for t_old, t_new in ((k, k + 1), (k + 1, k)):
            for o, c in by_call[t_old]:
                lo, hi = defs[o, c]
                bad += not time(lo) < t_new <= time(hi)
        out[k] = bad
    return out


def out_of_window(rows, order, order_new, win_new):
    """Roles of the fill (given in `order`) outside their windows when the calls are re-timed to `order_new`."""
    at2 = dict((x, q) for q, x in enumerate(order_new))
    return sum(1 for t, h, o, c, p, off in rows if not win_new[o, c][0] < at2[order[t]] <= win_new[o, c][1])


def windows_bound(table, wt, rank, rule):
    """A pinned window table {'r,c': [rank of c, [call times]]} (PLAN.windows, order-screen.windows) must list exactly
    the derived windows: same number of windows and, for every derived window, the same rank and call times."""
    ok = len(table) == len(wt) and all(table.get('%d,%d' % k) == [rank[k[1]], v] for k, v in wt.items())
    need(ok, '%s: pinned windows != derived windows' % rule)
    return ok


def schedule_binding(tpl, order, plan):
    """Own re-expansion of the template in the given order (stage blocks copied with source_event, replica,
    replicas=[r], time; then the two tail events) and canonical-JSON hashes, against PLAN.replica_lift."""
    src = tpl['execution_schedule']
    blocks, stage = {}, None
    for i, e in enumerate(src[:30]):
        if e['kind'] == 'local_cover_sweep':
            stage = e['stage']
            blocks[stage] = []
        blocks[stage].append((i, e))
    sched = []
    for t, (s, r) in enumerate(order):
        for i, e in blocks[s]:
            sched.append(dict(e, source_event=i, replica=r, replicas=[r], time=t))
    sched += [dict(src[i], source_event=i) for i in (30, 31)]

    h_sched, h_tpl = canon_sha(sched), canon_sha(tpl)
    need(h_sched == plan['replica_lift']['schedule_content_sha256'], 'binding: schedule content hash')
    need(h_tpl == plan['replica_lift']['parent_template_content_sha256'], 'binding: template content hash')
    return dict(schedule_events=len(sched), schedule_content_sha256=h_sched, template_content_sha256=h_tpl)


# ---------------------------------------------------------------------------------------- words ---
def rank2(vs):
    piv = {}
    for x in vs:
        x = int(x)
        while x:
            b = x.bit_length() - 1
            if b in piv:
                x ^= piv[b]
            else:
                piv[b] = x
                break
    return len(piv)


def word_widths(w):
    """Live helpers 224..703 minus `removed`; width = rank(final) - rank(start) with nested frames; helpers with a
    helper_final hyperplane are the zero-buffer owners."""
    removed = set(w['removed'])
    widths, ended = [], []
    for r in range(2 * V, 2 * V + w['report']['R']):
        if r in removed:
            continue
        fin = w['helper_final'].get(str(r))
        if fin is None:
            fin = [1 << i for i in range(H)]
        else:
            ended.append(r)
        st = w['start_extra'].get(str(r), [])
        need(rank2(fin) == len(fin) and rank2(st) == len(st) and rank2(list(fin) + list(st)) == len(fin),
             'widths: frame nesting of helper %d' % r)
        widths.append(len(fin) - len(st))
    return widths, ended


# ------------------------------------------------------------------------------ fill (own implementation) ---
def check_rows(rows, order, dispatch, widths, local, rank, win, pair_of, side_of, stage_pair, skip=()):
    """R-a, R-e, R-d, R-b on the literal rows [time, helper, owner, child, port, offset] and the R-c recount.
    A rejection reads 'rule: detail' with fill_check80.check_roles's rule ids (RULES).  `skip` is for negative
    controls only: rules named in it are not enforced, which shows exactly which rules a mutant breaks."""
    def fail(rule, msg):
        if rule not in skip:
            raise AuditFail(rule + ': ' + msg)
    n, R = len(order), CLAIM['helpers']
    if len(rows) != n * R:
        fail('R-a.count', '%d roles != %d calls x %d helpers' % (len(rows), n, R))
    seen_h, seen_f, used = set(), set(), {}
    cross, hosted_width, per_call = 0, 0, Counter()
    for row in rows:
        if not (len(row) == 6 and all(type(x) is int for x in row)):
            fail('R-a.schema', 'row %r' % (row,))
        t, h, o, c, p, off = row
        if not 0 <= t < n:
            fail('R-a.call', 'call %d' % t)
        if not 0 <= h < R:
            fail('R-a.helper_range', 'helper %d' % h)
        if not (0 <= o < T and c in rank and 0 <= p < V):
            fail('R-e.coords', 'owner %d child %d port %d' % (o, c, p))
        s, r = order[t]
        wd = widths[dispatch[s, r]][h]
        if (t, h) in seen_h:
            fail('R-a.duplicate_helper', 'helper %d twice in call %d' % (h, t))
        seen_h.add((t, h))
        fam = o * FPR + (2 * pair_of[c] + side_of[c]) * V + p
        if not 0 <= fam < W:
            fail('R-e.namespace', 'family %d outside the data namespace [0,%d)' % (fam, W))
        if o == r and pair_of[c] == stage_pair[s]:
            fail('R-e.active_pair', 'helper %d of call %d hosted on the caller active pair (child %d)' % (h, t, c))
        if (t, fam) in seen_f:
            fail('R-e.family_unique_per_call', 'two helpers on family %d in call %d' % (fam, t))
        seen_f.add((t, fam))
        per_call[t] += 1
        lo, hi = win[o, c]
        if not lo < t <= hi:
            fail('R-d.window', 'role (t=%d,h=%d) outside window (%d,%d] of owner %d child %d' % (t, h, lo, hi, o, c))
        if not (off >= 0 and off + wd <= rank[c]):
            fail('R-b.capacity', 'slice [%d,%d) in bin %s of rank %d' % (off, off + wd, (o, c, p), rank[c]))
        cells = ((1 << wd) - 1) << off
        b = (o, c, p)
        if used.get(b, 0) & cells:
            fail('R-b.overlap', 'overlap in bin %s' % (b,))
        used[b] = used.get(b, 0) | cells
        cross += o != r
        hosted_width += wd
    if len(seen_h) != n * R:
        fail('R-a.complete', '%d distinct (call, helper) roles != %d' % (len(seen_h), n * R))
    for b, cells in used.items():
        if cells & (cells + 1):
            fail('R-b.prefix', 'occupied cells of bin %s are not a prefix' % (b,))
    idle = Counter()
    for (o, c) in win:
        for p in range(V):
            left = rank[c] - bin(used.get((o, c, p), 0)).count('1')
            if left:
                idle[left] += 1
    loc = Counter()
    for s, r in order:
        loc.update(local[dispatch[s, r]])
    prof = loc + idle
    mass = sum(k * v for k, v in prof.items())
    cap = T * V * sum(rank.values())
    if sum(k * v for k, v in idle.items()) != cap - hosted_width:
        fail('R-c.mass', 'idle mass != capacity - hosted width')
    if not (M * W - mass == 320 * T and mass == (M - 1) * W + 64 * n):
        fail('R-c.mass', 'rank-mass identities (mass %d)' % mass)
    if not M * M > 2 * max(prof) ** 2:
        fail('R-c.mass', 'halving guard')
    return dict(roles=len(rows), cross_replica_roles=cross, occupied_bins=len(used), bins=T * V * len(rank),
                idle=dict(sorted(idle.items())), idle_remainders=sum(idle.values()), profile=dict(sorted(prof.items())),
                rank_mass=mass, deficit=M * W - mass, hosted_width=hosted_width, capacity=cap,
                families_per_call=sorted(set(per_call.values())), max_family=max(f for _, f in seen_f),
                distinct_host_families=len(set(f for _, f in seen_f)))


def fc_row(row, order, dispatch, widths, pair_of, side_of):
    """A literal row as a fill_check80 role (same family/copy identity; width read from the given table)."""
    t, h, o, c, p, off = row
    s, r = order[t]
    return dict(child=c, copy=V * o + p, family=o * FPR + (2 * pair_of[c] + side_of[c]) * V + p, helper=h,
                offset=off, owner_replica=o, port=p, replica=r, stage=s, time=t, width=widths[dispatch[s, r]][h])


def busy_families(order, stage_pair, hosts, skip=()):
    """Physical occupancy per call: the caller's 224 active-pair families and its 422 host families (hosts[t], a
    set) are disjoint, so exactly 646 families are busy in every call.  Returns ({busy families: calls}, record)."""
    busy, sizes, shared = Counter(), Counter(), 0
    for t, (s, r) in enumerate(order):
        base = r * FPR + 2 * stage_pair[s] * V
        act = set(range(base, base + 2 * V))
        need('physical.busy_families' in skip or (len(hosts[t]) == CLAIM['helpers'] and not act & hosts[t]),
             'physical.busy_families: call %d has %d active-pair and %d host families, %d shared'
             % (t, len(act), len(hosts[t]), len(act & hosts[t])))
        busy[len(act | hosts[t])] += 1
        sizes[len(act), len(hosts[t])] += 1
        shared = max(shared, len(act & hosts[t]))
    need('physical.busy_families' in skip or busy == Counter({646: len(order)}),
         'physical.busy_families: busy families per call %r' % dict(busy))
    return busy, dict(active_pair_and_host_families=sorted(list(k) + [v] for k, v in sizes.items()),
                      max_shared=shared)


def rg_charts(rank, pair_of, side_of, phases, ports, rdicts, expected):
    """R-g by the vendored fill_check80.pending_axes_and_charts (X2: disjoint pending axes of the children sharing a
    family; one 73-column chart per role slice); the number of distinct charts must equal SPEC's."""
    xg = FC.pending_axes_and_charts(dict(rank=rank, child_pair=pair_of, child_side=side_of), phases,
                                    FC.owner_bases(ports), rdicts)
    need(xg['actual_73column_charts'] == expected, 'R-g.charts: %d charts != SPEC %d' % (xg['actual_73column_charts'], expected))
    return xg


def expect_fail(out, name, rule, fn, **extra):
    """Negative control of one check: fn() must raise, by `rule` (the 'rule:' prefix of an AuditFail message or a
    fill_check80 CheckFailure id)."""
    attempt(name)
    try:
        fn()
    except AuditFail as e:
        got, msg = str(e).split(':', 1)[0], str(e)
    except FC.CheckFailure as e:
        got, msg = e.check, str(e)
    else:
        raise AuditFail('negative control ACCEPTED: ' + name)
    need(got == rule, 'control %s: rejected by %s (%s), expected %s' % (name, got, msg[:80], rule))
    rec = dict(control=name, mutant=name, expected=rule, rejected_by=got, rejected=msg[:120])
    rec.update(extra)
    out.append(rec)


def violations(check):
    """[(rule, message)] of every rule a mutant breaks, in the order met: check(skip) is re-run with each rejecting
    rule added to skip until it passes."""
    skip, out = (), []
    while True:
        try:
            check(skip)
            return out
        except AuditFail as e:
            rule = str(e).split(':', 1)[0]
            need(rule in RULES and rule not in skip, 'control: unexpected rejection %r' % str(e)[:120])
            out.append((rule, str(e)))
            skip += (rule,)


def expect_reject(out, name, rules, check, fc=None, fc_rule=None):
    """Negative control.  check(skip) runs the own implementation on the mutant: it must reject, first by
    rules[0], and with the rejecting rules skipped one at a time it must break exactly `rules`, in that order.
    fc(), the vendored fill_check80 on the same mutant, must then reject by fc_rule (default: the same rule)."""
    attempt(name)
    got = violations(check)
    need(got, 'negative control ACCEPTED: ' + name)
    need([r for r, _ in got] == list(rules), 'control %s: breaks %r, expected %r' % (name, [r for r, _ in got], list(rules)))
    rec = dict(control=name, mutant=name, expected=rules[0], rejected_by=got[0][0], breaks=list(rules),
               rejected=got[0][1][:120])
    if fc is not None:
        try:
            fc()
        except FC.CheckFailure as e:
            need(e.check == (fc_rule or rules[0]), 'control %s: fill_check80 rejected by %s (%s)' % (name, e.check, e.detail))
            rec['fill_check80_rule'] = e.check
        else:
            raise AuditFail('negative control ACCEPTED by fill_check80: ' + name)
    out.append(rec)


# ---------------------------------------------------------------------------------------------- run ---
def namespace_receipt(ig, phys, helpers):
    """receipts/INDEPENDENT-GLOBAL.json: its physical stock and its five namespace intervals (data, centres, tableau,
    zero buffers, coefficient) must be the own stock phys = W + 8 + helpers + zero buffers + 2 cut at the own
    boundaries."""
    want = dict(data=[0, W], centres=[W, W + 8], tableau=[W + 8, W + 8 + helpers], zero_buffers=[W + 8 + helpers, phys - 2],
                coefficient=[phys - 2, phys])
    need(ig['physical'] == phys and ig['namespace'] == want, 'physical.namespace_receipt: receipt %r %r != own %d %r'
         % (ig['physical'], ig['namespace'], phys, want))
    return want


def run(inp, log, words_result):
    """words_result: check_words.run's result; the local paid profiles used here are its recounts (the words'
    report.local_profile and eight-providers.json must equal them)."""
    res = {}
    tpl = inp.json('tpl2269')
    need(inp.raw('tpl2269') == inp.raw('tpl2462'), 'template: PR2269 and PR2462 copies differ')
    t37 = inp.json('tpl_t37_2462')
    stage_pair, rank, res['template'] = template_structure(tpl, t37)
    log('fill: template = 30 per-replica events + 2 global tail; %d/%d calls own their active pair; T37 template '
        'events/recipe/ranks equal' % (res['template']['calls_owning_active_pair'], res['template']['calls']))

    order = [tuple(x) for x in inp.json('order2530')]
    spec, plan = inp.json('spec2530'), inp.json('plan2530')
    check_diagonal(order)
    spec_plan_equal = [tuple(x) for x in spec['call_order']] == order and [tuple(x) for x in plan['order']] == order
    need(spec_plan_equal, 'order: SPEC/PLAN')
    order_projection(order)
    old = [tuple(x) for x in inp.json('order2462')]
    order_projection(old)
    res['order'] = dict(calls=len(order), sha256=canon_sha(order), pr2462_sha256=canon_sha(old),
                        equals_diagonal_formula=order == diagonal_order(), equals_spec_and_plan_order=spec_plan_equal,
                        per_replica_projection_monotone=all([s for s, rr in order if rr == r] == list(range(STAGES))
                                                            for r in range(T)),
                        positions_changed_vs_pr2462=sum(x != y for x, y in zip(old, order)))

    lo_src, defs = {}, {}
    win, pair_of, side_of = block_windows(tpl, order, stage_pair, rank, lo_src, defs)
    sched = FC.derive_schedule(T, tpl, order)
    wt = windows_agree(win, sched)
    maps_equal = sched['child_pair'] == pair_of and sched['child_side'] == side_of
    need(maps_equal, 'windows: pair/side maps')
    need(sched['bridges'] == 9 * T and sched['events'] == 30 * T, 'windows: event/bridge counts')
    plan_equal = windows_bound(plan['windows'], wt, rank, 'windows.plan')
    plan_maps_equal = (dict((str(c), pair_of[c]) for c in pair_of) == plan['pairs'] and
                       dict((str(c), side_of[c]) for c in side_of) == plan['sides'])
    need(plan_maps_equal, 'windows: PLAN pairs/sides')
    scr = inp.json('screen2530')
    need([tuple(x) for x in scr['order']] == order, 'windows.order_screen: order')
    screen_equal = windows_bound(scr['windows'], wt, rank, 'windows.order_screen')
    win_old, _, _ = block_windows(tpl, old, stage_pair, rank)
    sched_old = FC.derive_schedule(T, tpl, old)
    wt_old = windows_agree(win_old, sched_old)          # the two window rules also agree under PR2462's order

    def wlen(ww):
        return sum(hi - lo for lo, hi in ww.values())
    res['windows'] = dict(count=len(win), expanded_events=sched['events'], bridges=sched['bridges'],
                          empty=sum(1 for lo, hi in win.values() if hi <= lo), total_length=wlen(win),
                          total_length_under_pr2462_order=wlen(win_old),
                          sha256=canon_sha(sorted([r, c, lo, hi] for (r, c), (lo, hi) in win.items())),
                          agreement=dict(fill_check80_event_rule=sched['window_times'] == wt, pair_side_maps=maps_equal,
                                         PLAN=plan_equal, PLAN_pairs_sides=plan_maps_equal, order_screen=screen_equal,
                                         event_rule_under_pr2462_order=sched_old['window_times'] == wt_old),
                          lower_end_set_by=dict(sorted(Counter(lo_src.values()).items())),
                          own_active_pair_calls_outside_window=active_pair_outside_own_windows(order, win, pair_of,
                                                                                               stage_pair))
    res['binding'] = schedule_binding(tpl, order, plan)
    log('fill: order = diagonal (4s+r, s, r), %d/666 positions moved vs PR2462; %d windows (block rule = event rule '
        '= PLAN = order-screen); schedule hash %s... matches PLAN' % (res['order']['positions_changed_vs_pr2462'],
                                                                       len(win), res['binding']['schedule_content_sha256'][:12]))

    words = dict((pid, inp.json('w2530_%s' % tag)) for pid, tag in (('gauge44', 'base'), ('extra', 'extra')))
    provs = inp.json('providers2530')
    recount = dict(gauge44=words_result['base']['pr2530']['profile'], extra=words_result['extra']['pr2530']['profile'])
    widths, local, ended = {}, {}, {}
    for pid, w in words.items():
        widths[pid], ended[pid] = word_widths(w)
        need(len(widths[pid]) == CLAIM['helpers'], 'widths: helpers per call')
        need(Counter(widths[pid]) == Counter(intkeys(w['report']['width_inventory'])), 'widths: report inventory')
        need(widths[pid] == provs[pid]['widths'], 'widths: ordered eight-providers widths')
        local[pid] = Counter(recount[pid])        # the frame-chain recount of check_words, not the report
        need(local[pid] == Counter(intkeys(w['report']['local_profile'])) == Counter(CLAIM['local'])
             == Counter(intkeys(provs[pid]['actual_paid_profile'])), 'widths: local profile recount != report/claim/providers')
        need(sum(k * v for k, v in local[pid].items()) == 2 * V * 8 + 8 * 8 + sum(widths[pid]), 'widths: local mass')
    need(widths['gauge44'] == widths['extra'] and ended['gauge44'] == ended['extra'], 'widths: providers differ')
    disp = dict(((s, r), p) for s, r, p in spec['dispatch'])
    need(disp == dict(((s, r), p) for s, r, p in inp.json('dispatch2462')), 'dispatch: SPEC != PR2462 DISPATCH')
    need(all(pc['provider'] == disp[pc['stage'], pc['replica']] and pc['time'] == t and (pc['stage'], pc['replica']) == order[t]
             for t, pc in enumerate(plan['provider_calls'])), 'dispatch: PLAN provider_calls')
    need(all(pw['widths'] == widths[disp[order[t]]] for t, pw in enumerate(plan['per_call_widths'])) and
         len(plan['per_call_widths']) == len(order), 'widths: PLAN per_call_widths')
    NZ = len(ended['gauge44'])
    res['words'] = dict(helpers=len(widths['gauge44']), inventory=dict(sorted(Counter(widths['gauge44']).items())),
                        zero_buffers=NZ, width_sum=sum(widths['gauge44']), dispatch=dict(Counter(disp.values())),
                        local_profile_source='check_words frame-chain recount (= report = eight-providers = claim)')

    fill = inp.json('fill2530')
    need(fill['columns'] == ['time', 'helper', 'owner_replica', 'child', 'port', 'offset'] and
         fill['dispatch_overrides'] == [], 'fill: schema')
    rows = fill['rows']
    exp = spec['expected']
    fr = check_rows(rows, order, disp, widths, local, rank, win, pair_of, side_of, stage_pair)
    need(fr['roles'] == CLAIM['roles'] == exp['hosted_residuals'], 'fill: roles')
    need(fr['idle'] == CLAIM['idle'] == intkeys(exp['idle_remainder_profile']), 'fill: idle %r' % fr['idle'])
    need(fr['profile'] == CLAIM['profile'] == intkeys(inp.json('profile2530')) == intkeys(exp['global_profile'])
         == intkeys(plan['profile']), 'fill: global profile')
    need(fr['rank_mass'] == exp['rank_mass'] == 4816512 and fr['deficit'] == 23680, 'fill: rank mass')
    need(fr['cross_replica_roles'] == exp['cross_replica_helper_roles'], 'fill: cross-replica roles')
    need(fr['idle_remainders'] == exp['idle_remainders'], 'fill: idle remainder count')
    res['fill'] = fr
    ctx = dict(T=T, R=CLAIM['helpers'], W=W, order=order, dispatch=disp, widths=widths, local_profiles=local)
    drows = [fc_row(z, order, disp, widths, pair_of, side_of) for z in rows]
    fc = FC.check_roles(ctx, sched, drows)
    second_equal = (fc['idle'] == dict((str(k), v) for k, v in fr['idle'].items()) and
                    fc['profile'] == dict((str(k), v) for k, v in fr['profile'].items()) and
                    fc['cross_replica_roles'] == fr['cross_replica_roles'] and fc['rank_mass'] == fr['rank_mass'])
    need(second_equal, 'fill: fill_check80.check_roles disagrees')
    res['fill_second_implementation'] = dict(hosted_families=fc['hosted_families'], occupied_bins=fc['occupied_bins'],
                                             idle_profile_cross_mass_equal=second_equal)
    log('fill: %d roles pass R-a, R-b, R-d, R-e and the R-c recount in both implementations (own check_rows and '
        'fill_check80.check_roles); idle %s; profile = PROFILE.json = SPEC = PLAN; cross-replica %d; mass %d'
        % (fr['roles'], fr['idle'], fr['cross_replica_roles'], fr['rank_mass']))

    # R-g (vendored fill_check80.pending_axes_and_charts only): DATA-PHASES bound to the template pin and the word
    # ports; X2 and 73-column charts.  R-f is replaced by the physical stock and namespace-receipt check below.
    phases = inp.json('phases2269')
    need(inp.used['phases2269']['sha256'] == tpl['exact_data_phase_recipe_sha256'], 'R-g: DATA-PHASES template pin')
    ports = [x['q'] for x in phases['recipes']]
    need(phases['ports'] == V and [x['port'] for x in phases['recipes']] == list(range(V)), 'R-g: port records')
    need(all(w['ports'] == ports for w in words.values()), 'R-g: DATA-PHASES ports != word ports')
    rdicts = [dict(port=p, child=c, offset=off, width=widths[disp[order[t]]][h]) for t, h, o, c, p, off in rows]
    xg = rg_charts(rank, pair_of, side_of, phases, ports, rdicts, exp['actual_73column_sigmas'])
    res['charts'] = xg

    # physical stock and occupancy
    phys = W + 8 + CLAIM['helpers'] + NZ + 2
    need(phys == CLAIM['physical'] == exp['physical'], 'physical %d' % phys)
    need(fr['max_family'] < W and fr['families_per_call'] == [CLAIM['helpers']], 'physical: hosting namespace')
    payload = 1 << (192 + (M + 1) // 2 + 2 * len(order) + 4).bit_length()
    stock_bits = (FC.stock_group() * phys).bit_length()
    row = 2 * stock_bits + 9909 + 252 + 2 * payload
    ig = inp.json('iglobal2530')
    need(row == ig['physical_row_coefficient'] and stock_bits == ig['physical_stock_bits'] and row < ig['row_limit'] == 20161
         and payload == ig['charged_prefix_bits'], 'physical.row_coefficient: own %d, receipt %r' % (row, ig['physical_row_coefficient']))
    namespace = namespace_receipt(ig, phys, CLAIM['helpers'])
    hosts = defaultdict(set)
    for t, h, o, c, p, off in rows:
        hosts[t].add(o * FPR + (2 * pair_of[c] + side_of[c]) * V + p)
    busy, busy_rec = busy_families(order, stage_pair, hosts)
    res['physical'] = dict(live=W, centres=8, tableau=CLAIM['helpers'], zero_buffers=NZ, coefficient=2, physical=phys,
                           stock_bits=stock_bits, row_coefficient=row, payload_bits=payload, namespace=namespace,
                           receipt_independent_global=dict(physical=ig['physical'], physical_stock_bits=ig['physical_stock_bits'],
                                                           physical_row_coefficient=ig['physical_row_coefficient'],
                                                           row_limit=ig['row_limit'],
                                                           charged_prefix_bits=ig['charged_prefix_bits'],
                                                           namespace=ig['namespace']),
                           busy_families_per_call=dict((str(k), v) for k, v in busy.items()), busy_families=busy_rec)
    log('fill: R-g (fill_check80 only) %d pending-axis checks, %d charts = SPEC; physical %d = %d + 8 + %d + %d + 2 = '
        'receipt (namespace intervals equal); busy families 224 + 422 = 646 (disjoint) in all %d calls; row %d = receipt '
        '< 20161; payload %d' % (xg['pending_axis_checks'], xg['actual_73column_charts'], phys, W, CLAIM['helpers'], NZ,
                                 busy[646], row, payload))

    # negative controls.  expect_reject: the own check_rows must reject the mutant first by the named rule and, re-run
    # with the rejecting rules skipped, break exactly the listed rules; fill_check80 must reject it by the same rule.
    # expect_fail: a single named check must reject the mutant.
    ctl_order, ctl_fill = [], []
    n = len(order)

    def own(rr, oo=order, ww=win, wd=widths, lp=local):
        return lambda skip: check_rows(rr, oo, disp, wd, lp, rank, ww, pair_of, side_of, stage_pair, skip)

    def vend(dr, cx=ctx, sc=sched):
        return lambda: FC.check_roles(cx, sc, dr)

    def fc_all(rr, oo=order, wd=widths):
        return [fc_row(z, oo, disp, wd, pair_of, side_of) for z in rr]

    def mut(changes):
        rr, dr = list(rows), list(drows)
        for q, z in changes.items():
            rr[q], dr[q] = z, fc_row(z, order, disp, widths, pair_of, side_of)
        return rr, dr

    def wd_of(z):
        return widths[disp[order[z[0]]]][z[1]]

    def fam_of(o, c, p):
        return o * FPR + (2 * pair_of[c] + side_of[c]) * V + p
    by_call, fam_at, helper_at, bins = defaultdict(list), {}, {}, defaultdict(list)
    for q, (t, h, o, c, p, off) in enumerate(rows):
        by_call[t].append(q)
        fam_at[t, fam_of(o, c, p)] = q
        helper_at[t, h] = q
        bins[o, c, p].append(q)
    top = {}                       # bin -> (row of its top slice, occupied end); bins are disjoint prefixes
    for b, members in bins.items():
        q = max(members, key=lambda k: rows[k][5])
        top[b] = (q, rows[q][5] + wd_of(rows[q]))
    tops = set(q for q, _ in top.values())

    def free_slot(t, o, c, w):
        """A port p whose family is unused in call t and whose bin (o, c, p) has room for width w on top."""
        return next(((p, top.get((o, c, p), (None, 0))[1]) for p in range(V) if (t, fam_of(o, c, p)) not in fam_at
                     and top.get((o, c, p), (None, 0))[1] + w <= rank[c]), None)

    # order, windows and template controls
    expect_fail(ctl_order, 'diagonal-formula check applied to PR2462\'s order', 'order.diagonal', lambda: check_diagonal(old))
    at_old = dict((k, i) for i, k in enumerate(old))
    rows_old = [[at_old[order[t]], h, o, c, p, off] for t, h, o, c, p, off in rows]
    out_old = out_of_window(rows, order, old, win_old)
    expect_reject(ctl_order, 'fill re-timed to PR2462 order (%d roles out of window)' % out_old, ['R-d.window'],
                  own(rows_old, old, win_old), vend(fc_all(rows_old, old), dict(ctx, order=old), sched_old))
    inv = list(order)
    i, j = inv.index((0, 5)), inv.index((1, 5))
    inv[i], inv[j] = inv[j], inv[i]
    expect_reject(ctl_order, 'per-replica stage inversion (replica 5)', ['order.projection'],
                  lambda skip: order_projection(inv, skip), lambda: FC.derive_schedule(T, tpl, inv), 'R-d.schedule')
    swapped = None
    for k in range(n - 1):
        o2 = list(order)
        o2[k], o2[k + 1] = o2[k + 1], o2[k]
        if o2[k][1] == o2[k + 1][1]:
            continue
        w2, _, _ = block_windows(tpl, o2, stage_pair, rank)
        at2 = dict((x, q) for q, x in enumerate(o2))
        r2 = [[at2[order[t]], h, o, c, p, off] for t, h, o, c, p, off in rows]
        try:
            own(r2, o2, w2)(())
        except AuditFail:
            swapped = (k, o2, w2, r2)
            break
    need(swapped is not None, 'controls: no breaking adjacent swap')
    k, o2, w2, r2 = swapped
    sched2 = FC.derive_schedule(T, tpl, o2)
    windows_agree(w2, sched2)                       # the two window rules agree under the swapped order too
    expect_reject(ctl_order, 'single adjacent cross-replica swap at position %d' % k, ['R-d.window'], own(r2, o2, w2),
                  vend(fc_all(r2, o2), dict(ctx, order=o2), sched2))
    expect_fail(ctl_order, 'block-rule windows of PR2530\'s order against the event-rule windows of the order swapped '
                'at position %d' % k, 'windows.block_vs_event', lambda: windows_agree(win, sched2))
    src = tpl['execution_schedule']
    q = next(q for q, e in enumerate(src[:30]) if e['kind'] == 'bridge')
    tpl_bad = dict(tpl, execution_schedule=src[:q] + [dict(src[q], dst_replica=1)] + src[q + 1:])
    expect_fail(ctl_order, 'template bridge event %d given a cross-replica field (dst_replica)' % q,
                'template.cross_replica_field', lambda: template_structure(tpl_bad, t37))

    # diagnostic: every adjacent cross-replica swap of the order, scored on R-d (the only call-time rule)
    by_call_oc = dict((t, [(rows[q_][2], rows[q_][3]) for q_ in qs]) for t, qs in by_call.items())
    scan = adjacent_swap_scan(order, defs, by_call_oc)
    breaking = [[k_, v] for k_, v in sorted(scan.items()) if v]
    legal = [k_ for k_, v in sorted(scan.items()) if not v]
    need(all(not scan[k_] for k_ in scan if k_ < k) and scan[k] > 0, 'diagnostic: swap scan != the control search')
    cross = sorted(set([k] + [b[0] for b in breaking[:3]] + [x for x in legal if x > k][:3]))
    for k_ in cross:
        o3 = list(order)
        o3[k_], o3[k_ + 1] = o3[k_ + 1], o3[k_]
        w3, _, _ = block_windows(tpl, o3, stage_pair, rank)
        need(out_of_window(rows, order, o3, w3) == scan[k_], 'diagnostic: swap scan at %d != full recount' % k_)
    res['order_dependence'] = dict(
        pr2462_order_roles_out_of_window=out_old,
        adjacent_cross_replica_swaps=dict(pairs=len(scan), same_replica_pairs=n - 1 - len(scan), legal=len(legal),
                                          breaking=len(breaking), first_breaking_position_roles=breaking[:10],
                                          first_legal_positions=legal[:10], positions_sha256=canon_sha(breaking),
                                          full_recount_cross_checked_at=cross))
    log('fill: diagnostic: %d adjacent cross-replica swaps keep every role of the fill in its window, %d break at least '
        'one (first breaking at %s; legal at %s...); PR2462 order: %d roles out of window'
        % (len(legal), len(breaking), [b[0] for b in breaking[:5]], legal[:6], out_old))

    # fill controls
    # R-d at the upper window end: helper h's roles of calls t and hi + 1 exchange their hosts; the moved-in role is
    # inside its window, both are off the callers' active pairs and on families unused in the new call
    moved = None
    for i, (t, h, o, c, p, off) in enumerate(rows):
        t2 = win[o, c][1] + 1
        if t2 >= n:
            continue
        j = helper_at[t2, h]
        _, _, oj, cj, pj, offj = rows[j]
        (s, r), (s2, r2_) = order[t], order[t2]
        lo_j, hi_j = win[oj, cj]
        if (widths[disp[s2, r2_]][h] == widths[disp[s, r]][h] and lo_j < t <= hi_j
                and not (o == r2_ and pair_of[c] == stage_pair[s2]) and not (oj == r and pair_of[cj] == stage_pair[s])
                and fam_at.get((t2, fam_of(o, c, p)), j) == j and fam_at.get((t, fam_of(oj, cj, pj)), i) == i):
            moved = (t2, mut({i: [t2, h, o, c, p, off], j: [t, h, oj, cj, pj, offj]}))
            break
    need(moved is not None, 'controls: no upper-end window control')
    expect_reject(ctl_fill, 'role moved to the call just after its window (t = hi + 1 = %d)' % moved[0], ['R-d.window'],
                  own(moved[1][0]), vend(moved[1][1]))

    # R-d at the lower window end: a role at t = lo of a window whose lower end is set by a bridge or a terminal
    # event in the owner's block lo (not by the local sweep, so the slot is off the caller's active pair)
    at_lo = None
    for (o, c) in sorted(x for x in win if lo_src[x] not in ('none', 'local_cover_sweep')):
        lo = win[o, c][0]
        s, r = order[lo]
        need(r == o, 'controls: window lower end outside the owner block')
        if pair_of[c] == stage_pair[s]:
            continue
        for j in by_call[lo]:
            slot = free_slot(lo, o, c, wd_of(rows[j])) if j in tops else None
            if slot is not None:
                at_lo = (lo, o, c, lo_src[o, c], mut({j: [lo, rows[j][1], o, c, slot[0], slot[1]]}))
                break
        if at_lo:
            break
    need(at_lo is not None, 'controls: no lower-end window control')
    expect_reject(ctl_fill, 'role at t = lo = %d of window (owner %d, child %d) whose lower end is a %s' % at_lo[:4],
                  ['R-d.window'], own(at_lo[4][0]), vend(at_lo[4][1]))

    # R-e: a second helper of call t stacked on top of another helper's bin (same family, in window, no overlap)
    stacked = None
    for t in range(n):
        for i in by_call[t]:
            b = tuple(rows[i][2:5])
            j = next((j for j in by_call[t] if j in tops and tuple(rows[j][2:5]) != b
                      and top[b][1] + wd_of(rows[j]) <= rank[b[1]]), None)
            if j is not None:
                stacked = mut({j: [t, rows[j][1]] + list(b) + [top[b][1]]})
                break
        if stacked:
            break
    need(stacked is not None, 'controls: no family control')
    expect_reject(ctl_fill, 'two helpers on one family (second stacked on the first one\'s bin)',
                  ['R-e.family_unique_per_call'], own(stacked[0]), vend(stacked[1]))

    # R-e: a host on the caller's active pair, in a free slot, with that one window widened to every call (on the
    # real windows R-d rejects such a host first: see own_active_pair_calls_outside_window)
    ap = None
    for t in range(n):
        s, r = order[t]
        for c in sorted(x for x in rank if pair_of[x] == stage_pair[s]):
            for j in by_call[t]:
                slot = free_slot(t, r, c, wd_of(rows[j])) if j in tops else None
                if slot is not None:
                    ap = (r, c, mut({j: [t, rows[j][1], r, c, slot[0], slot[1]]}))
                    break
            if ap:
                break
        if ap:
            break
    need(ap is not None, 'controls: no active-pair control')
    w_wide = dict(win)
    w_wide[ap[0], ap[1]] = (-1, n - 1)
    s_wide = dict(sched, windows=dict(sched['windows']))
    s_wide['windows'][ap[0], ap[1]] = (-1, sched['events'])
    expect_reject(ctl_fill, 'host on caller active pair (owner %d child %d; window widened to all calls)' % ap[:2],
                  ['R-e.active_pair'], own(ap[2][0], ww=w_wide), vend(ap[2][1], sc=s_wide))
    expect_fail(ctl_order, 'active-pair lemma on the windows with (owner %d, child %d) widened to all calls' % ap[:2],
                'windows.active_pair_lemma', lambda: active_pair_outside_own_windows(order, w_wide, pair_of, stage_pair))

    # R-a
    q = min(tops)
    expect_reject(ctl_fill, 'dropped role (top slice of its bin)', ['R-a.count', 'R-a.complete', 'R-c.mass'],
                  own(rows[:q] + rows[q + 1:]), vend(drows[:q] + drows[q + 1:]))
    a, b = next((a, b) for a in by_call[0] for b in by_call[0] if a < b and wd_of(rows[a]) == wd_of(rows[b]))
    rr, dr = mut({b: [rows[b][0], rows[a][1]] + rows[b][2:]})
    expect_reject(ctl_fill, 'helper hosted twice in one call (an equal-width helper left unhosted)',
                  ['R-a.duplicate_helper', 'R-a.complete'], own(rr), vend(dr))

    # R-b
    q = next(q for b, (q, e) in sorted(top.items()) if len(bins[b]) >= 2)
    rr, dr = mut({q: rows[q][:5] + [rows[q][5] - 1]})
    expect_reject(ctl_fill, 'overlap (top slice moved down one cell)', ['R-b.overlap', 'R-c.mass'], own(rr), vend(dr))
    q = next(q for b, (q, e) in sorted(top.items()) if e < rank[b[1]])
    rr, dr = mut({q: rows[q][:5] + [rows[q][5] + 1]})
    expect_reject(ctl_fill, 'prefix gap (top slice moved up one cell)', ['R-b.prefix'], own(rr), vend(dr))
    a, b = next((a, b) for a in sorted(tops) if top[tuple(rows[a][2:5])][1] == rank[rows[a][3]]
                for b in by_call[rows[a][0]] if b in tops and wd_of(rows[b]) > wd_of(rows[a]))
    rr, dr = mut({a: rows[a][:1] + rows[b][1:2] + rows[a][2:], b: rows[b][:1] + rows[a][1:2] + rows[b][2:]})
    expect_reject(ctl_fill, 'capacity (two helpers of one call exchange hosts; the wider tops a full bin)',
                  ['R-b.capacity'], own(rr), vend(dr))

    # width table and local profile (R-b / R-c)
    w_bad = dict((p_, list(v)) for p_, v in widths.items())
    w_bad['extra'][w_bad['extra'].index(9)] = 8
    expect_reject(ctl_fill, 'wrong width table (one 9 -> 8)', ['R-b.prefix', 'R-c.mass'], own(rows, wd=w_bad),
                  vend(fc_all(rows, wd=w_bad), dict(ctx, widths=w_bad)))
    l_bad = dict(local)
    l_bad['extra'] = local['extra'] - Counter({1: 1}) + Counter({2: 1})
    expect_reject(ctl_fill, 'local profile of provider extra with one rank-1 child counted as rank 2', ['R-c.mass'],
                  own(rows, lp=l_bad), vend(drows, dict(ctx, local_profiles=l_bad)))

    # R-g: X2 (one pending axis of a child copied into another child of the same family, at port 0), and the chart
    # count (the only role producing one of the charts moved to offset 0 of its bin, where another chart exists)
    ca, cb = next((x, y) for x in sorted(rank) for y in sorted(rank)
                  if x < y and (pair_of[x], side_of[x]) == (pair_of[y], side_of[y]))
    kids = list(phases['recipes'][0]['idle_children'])
    kids[cb] = dict(kids[cb], orthogonal_axes=[kids[ca]['orthogonal_axes'][0]] + list(kids[cb]['orthogonal_axes'][1:]))
    phases_bad = dict(phases, recipes=[dict(phases['recipes'][0], idle_children=kids)] + list(phases['recipes'][1:]))
    expect_fail(ctl_fill, 'X2: pending axis of child %d copied into child %d of the same family (port 0)' % (ca, cb),
                'R-g.pending_axes', lambda: rg_charts(rank, pair_of, side_of, phases_bad, ports, rdicts,
                                                      exp['actual_73column_sigmas']))
    keys = Counter((z['port'], z['child'], z['offset'], z['width']) for z in rdicts)
    chart_mut = None
    for key in sorted(x for x, m in keys.items() if m == 1 and x[2] > 0 and (x[0], x[1], 0, x[3]) in keys):
        q = next(q for q, z in enumerate(rdicts) if (z['port'], z['child'], z['offset'], z['width']) == key)
        cand = list(rdicts)
        cand[q] = dict(rdicts[q], offset=0)
        uniq = [dict(port=x[0], child=x[1], offset=x[2], width=x[3]) for x in sorted(set(
            (z['port'], z['child'], z['offset'], z['width']) for z in cand))]
        if FC.pending_axes_and_charts(dict(rank=rank, child_pair=pair_of, child_side=side_of), phases,
                                      FC.owner_bases(ports), uniq)['actual_73column_charts'] != xg['actual_73column_charts']:
            chart_mut = (q, key, cand)
            break
    need(chart_mut is not None, 'controls: no chart-count control')
    expect_fail(ctl_fill, 'the only role with slice key (port, child, offset, width) = %r moved to offset 0 (one chart '
                'fewer)' % (chart_mut[1],), 'R-g.charts',
                lambda: rg_charts(rank, pair_of, side_of, phases, ports, chart_mut[2], exp['actual_73column_sigmas']))

    # physical occupancy: one host family of call 0 replaced by an active-pair family
    s0, r0 = order[0]
    h_bad = dict(hosts)
    h_bad[0] = (hosts[0] - {min(hosts[0])}) | {r0 * FPR + 2 * stage_pair[s0] * V}
    expect_reject(ctl_fill, 'busy families: a host of call 0 on its active pair', ['physical.busy_families'],
                  lambda skip: busy_families(order, stage_pair, h_bad, skip))
    # provenance: the namespace receipt with one interval shifted; PLAN's windows with one call time dropped
    ig_bad = dict(ig, namespace=dict(ig['namespace']))
    ig_bad['namespace']['tableau'] = [x + 1 for x in ig['namespace']['tableau']]
    ctl_prov = []
    expect_fail(ctl_prov, 'INDEPENDENT-GLOBAL namespace with the tableau interval shifted by one (stock unchanged)',
                'physical.namespace_receipt', lambda: namespace_receipt(ig_bad, phys, CLAIM['helpers']))
    k0 = next(k for k in sorted(wt) if wt[k])
    plan_bad = dict(plan['windows'])
    plan_bad['%d,%d' % k0] = [rank[k0[1]], wt[k0][:-1]]
    expect_fail(ctl_prov, 'PLAN window (owner %d, child %d) with its last call time dropped' % k0, 'windows.plan',
                lambda: windows_bound(plan_bad, wt, rank, 'windows.plan'))
    plan_extra = dict(plan['windows'])
    extra_key = next('%d,%d' % (o, c) for o in range(10 ** 6) for c in (0,) if (o, c) not in wt)
    plan_extra[extra_key] = [1, [0]]
    expect_fail(ctl_prov, 'PLAN windows with one spurious extra window %s' % extra_key, 'windows.plan',
                lambda: windows_bound(plan_extra, wt, rank, 'windows.plan'))
    ig_phys = dict(ig, physical=ig['physical'] + 1)
    expect_fail(ctl_prov, 'INDEPENDENT-GLOBAL physical stock + 1 (namespace unchanged)', 'physical.namespace_receipt',
                lambda: namespace_receipt(ig_phys, phys, CLAIM['helpers']))
    log('fill: %d order/window/template, %d fill/stock and %d provenance negative controls, each rejected by its named '
        'rule (the fill controls first by that rule, breaking exactly their listed rules, and by fill_check80 by the '
        'same rule)' % (len(ctl_order), len(ctl_fill), len(ctl_prov)))
    return res, dict(order_windows_template=ctl_order, fill_and_stock=ctl_fill, provenance_fill=ctl_prov)

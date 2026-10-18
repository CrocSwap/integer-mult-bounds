#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bit-supplier helper-deletion ladder: what d = 0..6 deleted width-8 helpers would be worth (bit headroom only).

PR589's bit word has R = 439 width-8 helpers; PR1043 deletes helper 470 (R = 438).  PR1250 / seed11 found that 470 is
the only removable helper of the fixed word, so every further deletion needs a changed word.  This script prices
what such deletions would be worth under the PR1023 slot model, assuming nothing about the changed words except a
declared per-deletion local-profile model.  For d = 0..6 (R = 439 - d, slack S = 3996 - 9R width-8 units per
replica) it computes:

 1. Layout.  The certified unique moment-minimising no-bank slot layout for slack S, its runner-up and the runner-up
    gap, with PR2423's exact top-3 interval DP (verify_rehost.certify_optimum), cross-checked for every row by
    PR2423's independent branch-and-bound enumerator over all layouts (counts checked against a generating function).
 2. Windows.  Every split of the optimum's modified slots over the two children of each capacity class is tested with
    seed72's maxflow_assign and PR2423's all-subsets Hall test.  For one split an explicit placement of all 9R helper
    occurrences per replica is built with seed14's allocate (R overridden on the module instance), compared slot for
    slot with PR442's hosting_core.expand, and audited by seed14's placement_audit and PR2423's audit_slots.
 3. Endpoints.  The hosted idle profile is combined with three declared local-profile models and certified with
    PR1023's packing.endpoint (both pinned engines; accepted at c, rejected at c + 1e-24):
        TEMPLATE  R439 local + d * {1:-2, 2:+2, 3:-1, 7:-1}   (PR1043's measured one-deletion delta, repeated)
        RANK1     R439 local + d * {1:-8}                      (each deletion removes eight rank-1 children; illustrative,
                                                               NOT an upper envelope: same-mass deltas can price higher)
        RANK7     R439 local + d * {7:-1, 1:-1}                (each deletion removes one rank-7 and one rank-1 child;
                                                               illustrative; d=1 equals PR2423's transported word)
    The DP is re-certified at each row's own c + 1e-24 and must return the priced layout.
 4. Controls.  d = 0 reproduces PR589's c; d = 1 TEMPLATE equals PR1043's certified local profile and reproduces
    PR2423's 0.001734802047828389852783; PR2423's verify_rehost.main is replayed end to end and must agree; a wrong
    slack (S + 1 and S - 1) is rejected by the rank-mass and window-demand checks; further negative controls below.

No word is constructed here.  Rows d >= 2 are prices of hypothetical words; every row d >= 1 is conditional on a word
with that many fewer helpers and the declared local model.  The selected record is complex-bound; no kappa is claimed.

Usage: python3 -I -B deletion_ladder.py [--repo ROOT] [--out RECEIPT.json] [--check RECEIPT.json]
The last line printed is PASS_BIT_DELETION_LADDER ... or FAIL_BIT_DELETION_LADDER ...
Standard-library CPython only.  Main-tree inputs are read through PR2423's pins (sha256 + git blob); PR2423's
verify_rehost.py and PR1043's CERTIFICATE.json are vendored byte copies pinned here (vendor/NOTICE.md).
"""
import argparse
import hashlib
import itertools
import json
import os
import sys
import time
import types
from collections import Counter
from fractions import Fraction as Q

TAG = 'BIT_DELETION_LADDER'
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

VENDOR = {
    'vendor/pr2423/verify_rehost.py': dict(
        sha256='4774841de10a8386204519174c5e56eb14f5852b20058db38a65a1034eeba275',
        git_blob='58c76b9d7b6ed12e4473a4b38b5193f867b2d674',
        origin='PR2423 (Sagar Thakrar, @thakrarsagar) head 13cd273dc13c98244b1f9bcf588b6e828cbc0347, '
               'research/bit-r438-transport-rehost/verify_rehost.py'),
    'vendor/pr2423/vendor/pr1043/CERTIFICATE.json': dict(
        sha256='32c6cd6103006d627909cabdaf5083238c661a6582016a8b21075bd01c892eff',
        git_blob='56400920050c523e6e399f2455137b36c35cf528',
        origin='PR1043 (Ali Romman, @aliromman) head e309e17f83f5759b1ea1fa24a76f24838784cb4d, '
               'research/bit-boundary-persistence/CERTIFICATE.json (via PR2423 vendor/pr1043/)'),
}

DMAX = 6
MODELS = (('template', {1: -2, 2: 2, 3: -1, 7: -1}),
          ('rank1', {1: -8}),
          ('rank7', {7: -1, 1: -1}))
PR2423_R438_OPT = '0.001734802047828389852783'          # PR2423 R438 optimal re-hosting, PR1043 local profile


class Fail(Exception):
    pass


def require(ok, message):
    if not ok:
        raise Fail(message)


def git_blob(raw):
    return hashlib.sha1(b'blob %d\0' % len(raw) + raw).hexdigest()


def load_vendored(rel):
    path = os.path.join(HERE, *rel.split('/'))
    with open(path, 'rb') as handle:
        raw = handle.read()
    pin = VENDOR[rel]
    require(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'sha256 pin: ' + rel)
    require(git_blob(raw) == pin['git_blob'], 'git blob pin: ' + rel)
    return path, raw


def exec_module(name, path, raw):
    module = types.ModuleType(name)
    module.__file__ = path
    sys.modules[name] = module
    exec(compile(raw, path, 'exec'), module.__dict__)
    return module


def layout_count(S, umaxes):
    """Number of no-bank layouts with S unused width-8 units: coefficient of x^S in prod_class prod_{u<=umax} 1/(1-x^u)
    (one multiset of unused counts per capacity class).  Independent of the enumerator."""
    poly = [1] + [0] * S
    for umax in umaxes:
        for u in range(1, umax + 1):
            for s in range(u, S + 1):
                poly[s] += poly[s - u]
    return poly[S]


def main(args):
    t0 = time.time()
    repo = os.path.abspath(args.repo)
    controls = []
    vr_path, vr_raw = load_vendored('vendor/pr2423/verify_rehost.py')
    _, cert_raw = load_vendored('vendor/pr2423/vendor/pr1043/CERTIFICATE.json')
    VR = exec_module('ladder_pr2423_verify_rehost', vr_path, vr_raw)
    # PR2423's own pin of the PR1043 certificate must be the one used here.
    require(VR.VENDOR['vendor/pr1043/CERTIFICATE.json']['sha256'] == VENDOR['vendor/pr2423/vendor/pr1043/'
                                                                          'CERTIFICATE.json']['sha256'], 'cert pin')
    for rel in VENDOR:
        path = os.path.join(HERE, *rel.split('/'))
        with open(path, 'rb') as handle:
            good = handle.read()
        bad = good[:-2] + bytes([good[-2] ^ 1]) + good[-1:]
        VR.expect_reject(controls, 'vendored_tampered:' + rel,
                         lambda bad=bad, rel=rel: VR.check_pin(bad, VENDOR[rel]['sha256'], VENDOR[rel]['git_blob'], rel),
                         'sha256 pin')
    raw = {rel: VR.read_pinned(repo, rel, sha, blob) for rel, (sha, blob) in VR.PINS.items()}
    P = VR.load_module('ladder_packing', *raw['research/bit589-width-packing/packing.py'])
    S72 = VR.load_module('ladder_seed72_verify', *raw['research/bit589-width7-windows-seed72/verify.py'])
    S14 = VR.load_module('ladder_seed14_verify', *raw['research/bit-helper470-window-placement-seed14/verify.py'])
    HC = VR.load_module('ladder_pr442_hosting_core', *raw['research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/'
                                                          'vendor/idle-axis-hosting/hosting_core.py'])
    T, STAGES, M, V, COPIES, GRID = VR.T, VR.STAGES, VR.M, VR.V, VR.COPIES, VR.GRID
    gd = VR.grid_decimal
    out = dict(status='PASS_' + TAG,
               scope='bit headroom only; no new kappa (the selected record is complex-bound); rows d >= 1 price '
                     'hypothetical words with d fewer width-8 helpers under a declared local-profile model; d = 1 '
                     'TEMPLATE is PR1043 (open, not admitted) with PR2423 re-hosting; d >= 2 needs changed words '
                     '(PR1250: helper 470 is the only removable helper of the fixed word)',
               inputs=dict(main_tree={rel: dict(sha256=s, git_blob=b) for rel, (s, b) in sorted(VR.PINS.items())},
                           vendored={rel: dict(sha256=p['sha256'], git_blob=p['git_blob'], origin=p['origin'])
                                     for rel, p in sorted(VENDOR.items())}))

    # -- 0. Baseline binding (PR589 record, PR1023 slot model, PR1043 certificate, windows). --------------------------
    record = P.pinned_json('bit_record')
    selection = P.pinned_json('selection')
    model = P.slot_model(record, selection)
    W = record['nine']['bit']['live']
    require((model['R'], model['v'], W, model['calls']) == (439, V, 28416, STAGES * T), 'PR589 record dimensions')
    c0 = Q(record['nine']['bit_lower'])
    require(gd(c0) == VR.C0_DECIMAL, 'PR589 bit endpoint')
    local439 = Counter(model['local'])
    mass439, kids439 = sum(r * n for r, n in local439.items()), sum(local439.values())
    require((mass439, kids439) == (8 * 439 + 63 + 14 * V, 2920), 'R439 local mass and child count')
    cert = json.loads(cert_raw)
    require(VR.unkeyed(cert['local']['baseline']['profile']) == dict(local439), 'PR1043 baseline local = PR589')
    local1043 = Counter(VR.unkeyed(cert['local']['candidate']['profile']))
    require(cert['local']['candidate']['helpers'] == 438, 'PR1043 candidate is R438')

    WIN72 = S72.WIN
    win14 = S14.windows(S14.schedule())
    require(set(WIN72) == {i for i, (p, r, st) in win14.items() if r and st}, 'hosting children agree')
    require(all(win14[i][1:] == (WIN72[i][0], tuple(WIN72[i][1])) for i in WIN72), 'seed72 and seed14 windows agree')
    require({i: c for i, (c, st) in WIN72.items()} == model['caps'], 'window capacities = PR1023 slot capacities')
    hosting = {i: (win14[i][0], WIN72[i][0], tuple(WIN72[i][1])) for i in sorted(WIN72)}
    active = {e['stage']: e['pair'] for e in S72.wopt.windows.schedule() if e['kind'] == 'local_cover_sweep'}
    require(sorted(active) == list(range(STAGES)), 'one local sweep per stage')
    slots = Counter()
    for i, (c, st) in WIN72.items():
        slots[c] += COPIES
    require(slots == model['slots'] == Counter({7: 666, 14: 444, 28: 444, 42: 444}), 'slots per replica')
    units = sum((c // 8) * n for c, n in slots.items())
    require(units == 3996, 'width-8 capacity per replica')
    cap_mass = sum(c * n for c, n in slots.items())
    pairs = {}
    for i, (pair, cap, st) in hosting.items():
        if cap // 8:
            pairs.setdefault(cap, []).append(i)
    require({cap: len(ch) for cap, ch in pairs.items()} == {14: 2, 28: 2, 42: 2}, 'two children per capacity class')
    umaxes = sorted(cap // 8 for cap in pairs)
    for S_, n in VR.EXPECTED_LAYOUTS.items():
        require(layout_count(S_, umaxes) == n, 'generating-function layout count = PR2423 at S=%d' % S_)
    HOSTED_MASS = 9 * T * mass439 + T * (cap_mass - 72 * 439)
    require(HOSTED_MASS == 1808352, 'hosted rank mass invariant')

    # -- helpers -----------------------------------------------------------------------------------------------------
    def local_model(delta, d):
        loc = Counter(local439)
        for r, n in delta.items():
            loc[r] += d * n
        require(all(n >= 0 for n in loc.values()), 'local profile counts nonnegative')
        require(sum(r * n for r, n in loc.items()) == mass439 - 8 * d, 'local rank mass = R439 mass - 8d')
        return +loc

    def price(local, idle, label):
        H = Counter({r: n * STAGES * T for r, n in local.items()})
        for r, n in idle.items():
            H[r] += n * T
        require(all(n > 0 for n in H.values()), 'positive profile entries (%s)' % label)
        require(sum(idle.values()) == sum(slots.values()), 'one idle child per slot (%s)' % label)
        require(sum(r * n for r, n in H.items()) == HOSTED_MASS, 'hosted rank mass (%s)' % label)
        require(M * M > 2 * max(H) ** 2, 'halving guard (%s)' % label)
        H = dict(sorted(H.items()))
        return P.endpoint(H, W), H

    def splits(layout):
        items = sorted(layout)
        for combo in itertools.product(*[range(k + 1) for _, k in items]):
            assign = {}
            for ((cap, u), k), ka in zip(items, combo):
                a, b = pairs[cap]
                for child, n in ((a, ka), (b, k - ka)):
                    if n:
                        assign.setdefault(child, []).append((u, n))
            yield combo, assign

    def demand_of(assign):
        dem = {}
        for i, (pair, cap, st) in hosting.items():
            dem[i] = (cap // 8) * COPIES - sum(u * n for u, n in assign.get(i, ()))
            require(sum(n for _, n in assign.get(i, ())) <= COPIES, 'modified copies within a child')
        return dem

    def windows_check(layout, R):
        supply = {s: R for s in range(STAGES)}
        allowed = {i: set(st) for i, (p, c, st) in hosting.items()}
        n_cfg, feasible, first = 0, 0, None
        for combo, assign in splits(layout):
            dem = demand_of(assign)
            require(sum(dem.values()) == STAGES * R, 'window demand total = 9R')
            x = S72.maxflow_assign(supply, dem, allowed)
            ok, _ = VR.hall_check(supply, dem, allowed)
            require((x is not None) == ok, 'max-flow and Hall disagree at %s' % (combo,))
            n_cfg += 1
            if x is not None:
                require(all(s in allowed[i] and n > 0 for (s, i), n in x.items()), 'flow inside windows')
                require(all(sum(n for (s, i), n in x.items() if i == j) == dem[j] for j in dem), 'flow meets demand')
                require(all(sum(n for (s, i), n in x.items() if s == t) == R for t in range(STAGES)), 'flow = supply')
                feasible += 1
                if first is None:
                    first = (combo, assign, x)
        return n_cfg, feasible, first

    def placement(assign, x, R, idle_expected):
        pats = []
        for i, (pair, cap, st) in sorted(hosting.items()):
            f = cap // 8
            mods = Counter()
            for u, n in assign.get(i, ()):
                mods[f - u] += n
            full = COPIES - sum(mods.values())
            if f == 0:
                pats.append([i, [], COPIES])
                continue
            for h in sorted(mods):
                pats.append([i, [8] * h, mods[h]])
            if full:
                pats.append([i, [8] * f, full])
        sel = dict(patterns=pats, stages=sorted([i, 8, s, n] for (s, i), n in x.items()))
        require(S14.R == 439, 'seed14 R constant')
        S14.R = R
        try:
            alloc = S14.allocate(sel)
            rem, _ = S14.placement_audit(alloc, win14, frozenset())
            owners = S14.owners_for_replicas(alloc, win14)
        finally:
            S14.R = 439
        require(len(alloc) == STAGES * R, 'occurrences per replica')
        win_hc = {i: (p, c, frozenset(st)) for i, (p, c, st) in hosting.items()}
        ys = {(i, tuple(pat)): n for i, pat, n in pats}
        zs = {(i, w, s): n for i, w, s, n in sel['stages']}
        slots_hc, rem_hc = HC.expand(win_hc, ys, zs, {s: [(h, 8) for h in range(R)] for s in range(STAGES)}, COPIES)
        require(slots_hc == alloc, 'seed14 allocate = PR442 expand (slot for slot)')
        idle_s14 = Counter(r for r in rem.values() if r)
        idle_hc = Counter(r for r in rem_hc.values() if r)
        idle_ind = VR.audit_slots(alloc, hosting, active, R)
        require(idle_s14 == idle_hc == idle_ind == idle_expected, 'placement remainders = DP optimum')
        seen = set()
        for stage, rep, h, fam, child, off, w in owners:
            r_, rest = divmod(fam, 8 * V)
            pair2, port = divmod(rest, V)
            require(r_ == rep and pair2 // 2 == hosting[child][0] != active[stage], 'owner family pair')
            require((stage, rep, h) not in seen, 'owner once')
            seen.add((stage, rep, h))
        require(len(seen) == STAGES * T * R, 'all hosted residual roles')
        canon = json.dumps([list(t) for t in alloc], separators=(',', ':')).encode()
        return dict(selection_patterns=pats, occurrences_per_replica=len(alloc), hosted_residual_roles=len(seen),
                    slot_list_sha256=hashlib.sha256(canon).hexdigest())

    def certify_row(local, S, exhaustive, label):
        """Candidate from the DP at c0 + 1e-24, priced; the DP is re-certified at the row's own c + 1e-24 and must
        return the priced layout (fixed point; at most four rounds)."""
        c_try = c0
        for _ in range(4):
            cand = VR.certify_optimum(P, slots, S, c_try + GRID, W, check_exhaustive=False)
            c, H = price(local, cand['idle_opt'], label)
            cs = VR.certify_optimum(P, slots, S, c + GRID, W, check_exhaustive=exhaustive)
            if cs['idle_opt'] == cand['idle_opt']:
                return c, H, cs
            c_try = c
        raise Fail('DP optimum did not reach a fixed point (%s)' % label)

    # -- 1-3. The ladder. --------------------------------------------------------------------------------------------
    ladder, table = [], []
    layout_cache = {}
    for d in range(DMAX + 1):
        R = 439 - d
        S = units - STAGES * R
        require(S == 45 + 9 * d, 'slack')
        expected = layout_count(S, umaxes)
        row = dict(d=d, R=R, slack_units_per_replica=S, layouts_total=expected, models={})
        lays = {}
        for name, delta in MODELS:
            local = local_model(delta, d)
            require(sum(local.values()) == kids439 + d * sum(delta.values()), 'local child count')
            c, H, cs = certify_row(local, S, True, '%s d=%d' % (name, d))
            require(cs['covered'] == expected, 'exhaustive enumeration covered every layout (d=%d %s)' % (d, name))
            require(VR.claim_is_optimal(cs, cs['opt']), 'optimum certifies')
            VR.expect_reject(controls, 'runner_up_claimed_optimal/d%d/%s' % (d, name),
                             lambda cs=cs: require(VR.claim_is_optimal(cs, cs['run']), 'claimed optimum not certified'),
                             'claimed optimum not certified')

            def accept_next(H=H, c=c):
                lo, hi = P.MOMENT.moment(H, M, W, c + GRID, True)
                require(hi < 1, 'moment at c + 1e-24 is not below one')
            VR.expect_reject(controls, 'endpoint_plus_1e-24_accepted/d%d/%s' % (d, name), accept_next, 'not below one')
            lays[name] = cs
            row['models'][name] = dict(local_profile=VR.keyed(local), local_rank_mass=sum(r * n for r, n in local.items()),
                                       endpoint=gd(c), endpoint_fraction=str(c),
                                       gain_vs_pr589_percent=VR.dfloor(100 * (c - c0) / c0, 8),
                                       hosted_profile=VR.keyed(H), hosted_children=sum(H.values()),
                                       dp_certificate=cs['receipt'])
            row['models'][name]['_c'] = c
        layouts = {cs['opt'] for cs in lays.values()}
        require(len(layouts) == 1, 'all three models select the same layout at d=%d' % d)
        cs = lays['template']
        opt, idle_opt = cs['opt'], cs['idle_opt']
        require(all(x['idle_opt'] == idle_opt for x in lays.values()), 'same idle profile')
        if opt not in layout_cache:
            n_cfg, n_ok, first = windows_check(opt, R)
            plc = placement(first[1], first[2], R, idle_opt) if first is not None else None
            layout_cache[opt] = (n_cfg, n_ok, first, plc)
        n_cfg, n_ok, first, plc = layout_cache[opt]
        row.update(optimum=VR.layout_name(opt), optimum_idle_per_replica=VR.keyed(idle_opt),
                   runner_up=VR.layout_name(cs['run']), third=VR.layout_name(cs['third']),
                   exhaustive_layouts_covered=cs['covered'],
                   windows=dict(splits_checked=n_cfg, splits_feasible=n_ok,
                                note='every split of each (capacity, u) count over the two children of that capacity '
                                     'class; seed72 maxflow_assign and the all-subsets Hall test agree on each'),
                   placement=None if plc is None else dict(plc, split=VR.layout_name(opt) + ' with split ' +
                                                           json.dumps({str(k): v for k, v in sorted(first[1].items())})))
        # Wrong slack controls: the S+1 and S-1 optima must be rejected by the rank-mass and window-demand checks.
        for wrong in (S + 1, S - 1):
            bad = VR.certify_optimum(P, slots, wrong, c0 + GRID, W, check_exhaustive=False)
            VR.expect_reject(controls, 'wrong_slack_%d_priced/d%d' % (wrong, d),
                             lambda bad=bad: price(local_model(MODELS[0][1], d), bad['idle_opt'], 'wrong slack'),
                             'hosted rank mass')
            VR.expect_reject(controls, 'wrong_slack_%d_windows/d%d' % (wrong, d),
                             lambda bad=bad: windows_check(bad['opt'], R), 'window demand total')
        # Supply of R+1 helpers per stage into the R optimum must not fit.
        if first is not None:
            VR.expect_reject(controls, 'supply_R_plus_1_into_optimum/d%d' % d,
                             lambda: require(S72.maxflow_assign({s: R + 1 for s in range(STAGES)},
                                                                demand_of(first[1]),
                                                                {i: set(st) for i, (p, c, st) in hosting.items()})
                                             is not None, 'infeasible: R+1 helpers per stage do not fit'), 'do not fit')
        # DP with the optimum's rarest move dropped must disagree with the exhaustive enumerator.
        drop = min(opt, key=lambda t: (t[1], t[0]))[0]
        VR.expect_reject(controls, 'dp_with_move_%d_%d_dropped_vs_exhaustive/d%d' % (drop + (d,)),
                         lambda drop=drop: VR.certify_optimum(P, slots, S, row['models']['template']['_c'] + GRID, W,
                                                              check_exhaustive=True, dp_drop=(drop,)),
                         'exhaustive enumeration disagrees with the DP')
        ladder.append(row)
        print('  d=%d R=%d S=%d %s  splits %d/%d  (%.0f s)' % (d, R, S, VR.layout_name(opt), n_ok, n_cfg,
                                                               time.time() - t0), flush=True)

    # -- 4. Controls on the ladder. ----------------------------------------------------------------------------------
    cs0 = {n: ladder[0]['models'][n]['_c'] for n, _ in MODELS}
    require(all(c == c0 for c in cs0.values()), 'd=0 reproduces the PR589 endpoint in every model')
    require(ladder[0]['optimum'] == '9x(42,5)' and
            VR.unkeyed(ladder[0]['optimum_idle_per_replica']) == dict(model['idle_rep']), 'd=0 layout = PR589 selection')
    require(local_model(MODELS[0][1], 1) == local1043, 'd=1 TEMPLATE local = PR1043 certified local profile')
    c1t = ladder[1]['models']['template']['_c']
    require(gd(c1t) == PR2423_R438_OPT == VR.SCOUT_A, 'd=1 TEMPLATE reproduces PR2423 R438 optimal re-hosting')
    require(ladder[1]['optimum'] == '10x(42,5) + 1x(42,4)', 'd=1 layout = PR2423 optimum')
    # d = 1 RANK7 coincides with PR2423's transported-word profile (b); its endpoint must be PR2423's c_b.
    require(local_model(MODELS[2][1], 1) == Counter(VR.LOCAL_B), 'd=1 RANK7 local = PR2423 transported profile (b)')
    c1w = ladder[1]['models']['rank7']['_c']
    require(gd(c1w) == VR.SCOUT_B, 'd=1 RANK7 reproduces PR2423 c_b')
    VR.expect_reject(controls, 'local_model_mass_minus_7', lambda: local_model({1: -7}, 1), 'local rank mass')
    VR.expect_reject(controls, 'local_model_negative_counts', lambda: local_model({7: -4, 1: 20}, 6),
                     'nonnegative')
    # End-to-end replay of PR2423's verify_rehost.main (vendored, pinned) must agree with the d = 1 row.
    vr_out, _, ca, cb, c1043 = VR.main(types.SimpleNamespace(repo=repo))
    require(ca == c1t and cb == c1w, 'PR2423 verify_rehost c_a, c_b = ladder d=1 TEMPLATE, RANK7')
    require(gd(c1043) == VR.PR1043_DECIMAL, 'PR2423 replay: PR1043 in-place endpoint')
    require(vr_out['dp']['S54_at_c_a_next'] == ladder[1]['models']['template']['dp_certificate'],
            'PR2423 S=54 DP certificate = ladder d=1 TEMPLATE certificate')
    require(vr_out['placement']['slot_list_sha256'] == ladder[1]['placement']['slot_list_sha256'],
            'PR2423 placement = ladder d=1 placement (slot list sha256)')
    out['pr2423_replay'] = dict(status=vr_out['status'], c_a=gd(ca), c_b=gd(cb), c_pr1043_inplace=gd(c1043),
                                negative_controls=len(vr_out['negative_controls']),
                                placement_slot_list_sha256=vr_out['placement']['slot_list_sha256'])
    # Monotone in d within each model; per-step increments.
    for name, _ in MODELS:
        cs_ = [row['models'][name]['_c'] for row in ladder]
        require(all(a < b for a, b in zip(cs_, cs_[1:])), 'endpoint increases with d (%s)' % name)
        for d in range(1, DMAX + 1):
            ladder[d]['models'][name]['step_vs_previous_d_percent'] = VR.dfloor(100 * (cs_[d] - cs_[d - 1]) / c0, 8)
    for row in ladder:
        for name, _ in MODELS:
            c = row['models'][name].pop('_c')
            table.append((row['d'], name, c))
    out['ladder'] = ladder
    out['negative_controls'] = controls
    out['claims'] = dict(kappa='unchanged; the bit side does not bind', max_d=DMAX,
                         certificate='per row: moment(opt, c+1e-24) > 1 by both engines; every other no-bank slot '
                                     'layout has a certified larger idle sum at c+1e-24 with the same child count and '
                                     'local profile; so no layout in the PR1023 slot model reaches c+1e-24 for that '
                                     'local model')
    return out, time.time() - t0, ladder, table, c0


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--repo', default=DEFAULT_REPO,
                    help='repository root (default: the parent of the research/ directory holding this script)')
    ap.add_argument('--out', help='write the JSON receipt here')
    ap.add_argument('--check', help='require the regenerated receipt to equal this file byte for byte')
    a = ap.parse_args()
    if sys.flags.optimize or not __debug__:
        print('FAIL_%s refusing to run under python -O (assert-based checks in pinned modules would be skipped)' % TAG)
        sys.exit(2)
    try:
        receipt, elapsed, ladder, table, c0 = main(a)
        text = json.dumps(receipt, indent=1, sort_keys=True) + '\n'
        if a.check:
            with open(a.check) as handle:
                require(handle.read() == text, 'receipt differs from ' + a.check)
        if a.out:
            with open(a.out, 'w') as handle:
                handle.write(text)
    except (Exception, SystemExit) as e:  # seed72's need() raises SystemExit
        print('FAIL_%s %s: %s' % (TAG, type(e).__name__, e))
        sys.exit(1)
    print('d  R    S   layout                    windows  c_template                  c_rank1'
          '                      c_rank7                     %vsPR589 (T/R1/R7)')
    for row in ladder:
        m = row['models']
        print('%d  %d  %-3d %-25s %2d/%-2d    %s  %s  %s  +%s/+%s/+%s' % (
            row['d'], row['R'], row['slack_units_per_replica'], row['optimum'],
            row['windows']['splits_feasible'], row['windows']['splits_checked'],
            m['template']['endpoint'], m['rank1']['endpoint'], m['rank7']['endpoint'],
            m['template']['gain_vs_pr589_percent'][:7], m['rank1']['gain_vs_pr589_percent'][:7],
            m['rank7']['gain_vs_pr589_percent'][:7]))
    print('python %s; %.1f s' % (sys.version.split()[0], elapsed))
    top = ladder[-1]['models']
    print('PASS_%s d=0..%d exhaustive=%d/%d windows_feasible=%d/%d c_template(d=%d)=%s c_rank1=%s c_rank7=%s '
          'controls=%d no_new_kappa' % (
              TAG, len(ladder) - 1, sum(1 for r in ladder for m in r['models'].values()
                                     if m['dp_certificate']['exhaustive_layouts_covered'] == r['layouts_total']),
              3 * len(ladder),
              sum(1 for r in ladder if r['windows']['splits_feasible']), len(ladder), ladder[-1]['d'],
              top['template']['endpoint'], top['rank1']['endpoint'], top['rank7']['endpoint'],
              len(receipt['negative_controls'])))

#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Restore-only optimum of PR #3042's six-skip words (Python standard library only).

Theorem (both providers). Keep A (with its prelude), B, warps, cut, initial corrections, precondition, compensation, start
frames, helper end frames, removed helpers and private buffers of WORD-3042-{base,extra} fixed; replace the restore by ANY
scalar gate sequence that PR2833's auditor accepts, and re-solve all frames. Then the certified local cost is at least
10,868,103,087 = LB_forced (10,867,765,164: exact frame optimum of the empty-restore word under the 88 forced entry caps)
+ forced restore-phase extras (337,923 = 292,959 for 42 blocked registers + 9 x 4,996 for nine payer groups). The word's
own restore attains it, so it is optimal in that class (no new kappa).

This script recomputes, from the pinned exports: the exact frame optimum (frames_exact.py, the certified solver's model),
the restore-entry rows in the auditor's free algebra (vendored PR2833 audit_local.walg_apply), their independence and the
forced coordinates of every restored helper, the caps, LB_forced, the classification (restore_bound.py), the literal
visits of the published frames, the calibration on PR #2979's words, the per-block attribution of PR #3042's two edits,
the auditor semantics controls (vendored auditor run in-process), two third-party attainment controls (PR #3056's and
PR #3060's restore[175:179] blocks) and the rejection controls. With --work DIR it writes RESULT.json and the regenerated
certificates there; otherwise it compares them with certificates/. Marius-Paul Dumitrean, with substantial AI assistance
(Claude Code).
"""
import argparse
import collections
import contextlib
import copy
import gzip
import hashlib
import io
import json
import sys
import tempfile
import time
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import frames_exact as FX   # noqa: E402
import restore_bound as RB  # noqa: E402

PINS = {
    'data/WORD-3042-base.json.gz': '7e98f6f2a6c9ce9e7e04b515bd8ce4a4a533ff05f01ea265be2a1a994695260e',
    'data/WORD-3042-extra.json.gz': '1396410de482883416fc7f534062ab005b484056b035fdcfa3b5cc065536ba35',
    'data/WORD-2979-base.json.gz': 'abaf67bfcb257528658c906b612f57025617592bd7889828f92b97a5f4f4300d',
    'data/WORD-2979-extra.json.gz': 'e0eaf64c4d5d324693d43889bce1b9e53e8da00402105c8c978fd102f208bed7',
    'data/EDITS-3042.json': 'ebffcc1e57e59439b9678ff8d9be518c457af22ce77235c2fdb46540ab9b9b79',
    'vendor/audit_local.py': 'a38940094f7d19cd6376aafdd4734fa68eabc9aff4c98c3c4a3e9540328b1c90',
    'vendor/moment.py': '81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482',
    'vendor/base_two_moment.py': 'aee70c242a2f1d225528fabe2002e1564d1dc884797c07d28a831c7878ee9098',
    'vendor/gk_common.py': 'e68d190fd436b2f3955decb590adb53344d5d4ea0a19d62d86df1e4b55ecd198',
}
CLAIM_PROFILE = {1: 2433, 2: 712, 3: 232, 4: 108, 5: 18, 8: 8}          # PR3042 declared local profile
PR2979_PROFILE = {1: 2445, 2: 706, 3: 232, 4: 108, 5: 18, 8: 8}
EXPECT = dict(cost=10868103087, lb=10867765164, lb_profile={1: 2370, 2: 693, 3: 255, 4: 116, 5: 18, 8: 8}, caps=88,
              live=632, restored=91, visits=51, forced=337923, blocked=42, blocked_units=292959, groups=9, group_units=44964,
              variables=743, components=210, largest=94, cost2979=10868133063)
WEIGHTS = (0, 2116671, 4228346, 6338140, 8446713, 10554378)
PR3042_README = dict(R1_E42=dict(units=-14888, registers=[63, 54, 40], gates='26 -> 29'),
                     R2_E7=dict(units=-14938, registers=[22, 73, 5], gates='13 -> 14'), total=-29826)
SKIPS_3042 = [5, 22, 40, 54, 63, 73]
FRAME_175 = [256, 128, 64, 38, 20, 10, 1]
OLD_175 = [['add', x, y, c, 1, FRAME_175] for x, y, c in ((22, 230, -1), (230, 22, 1), (22, 230, -1), (230, 22, 1))]
PR3056_175 = [['add', x, y, c, 1, FRAME_175] for x, y, c in ((230, 22, 1), (22, 230, -1), (230, 22, 2))]   # rank7-restore-contraction
PR3060_175 = [['add', 230, 22, -1, 1, FRAME_175], ['add', 22, 230, 1, 1, FRAME_175],
              ['scale', 22, -1, 1, FRAME_175], ['scale', 230, -1, 1, FRAME_175]]                       # rank7-native-tariff-optimum
NORMAL45 = dict(visitors=[2, 70, 71, 72], pivots=[249, 251, 265, 267])
BLOCKS = (('n45: PR2942 paired extraction, pivots 249/251/265/267 at V45', ((121, 161),)),
          ('n42: PR2979 extraction + PR3042 R1_E42', ((162, 196),)),
          ('n7: PR2979 extraction + PR3042 R2_E7', ((197, 211),)),
          ('PR2908/PR2917 paired-extraction outputs', ((94, 120),)),
          ('stage-1 group gates (W_A..W_D)', ((20, 39), (49, 52), (60, 63), (73, 76))))
OTHER_BLOCK = 'PR2857/PR2894 kernel-preload restore pairs'


def block_of(label):
    i = int(label[1:])
    for name, ranges in BLOCKS:
        if any(lo <= i <= hi for lo, hi in ranges):
            return name
    return OTHER_BLOCK


def require(ok, message):
    if not ok:
        raise AssertionError(message)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def authenticate(root=HERE, pins=PINS):
    for rel, h in sorted(pins.items()):
        require(sha(root / rel) == h, 'pinned input drift: ' + rel)
    return len(pins)


def load_word(name, root=HERE):
    rel = 'data/WORD-%s.json.gz' % name
    raw = (root / rel).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == PINS[rel], 'pinned export mismatch: ' + rel)
    return json.loads(gzip.decompress(raw))


def iprof(p):
    return {int(k): int(v) for k, v in p.items()}


def sprof(p):
    return {str(k): v for k, v in sorted(iprof(p).items())}


# ------------------------------------------------------------------------------------------------ auditor helpers
def framed(w, sol):
    """the word with the solver's frames written into every A/B/restore gate, its paid profile and width inventory;
    the cleanup key is dropped so that the auditor derives its inverse-reverse cleanup itself"""
    x = copy.deepcopy(w)
    g = sol['graph']
    A_idx = sol['meta']['A_idx']
    for k, (regs, F0, sec, idx) in enumerate(g.nodes):
        if sec not in ('A', 'B', 'tail'):
            continue
        Fr = list(sol['assign'].get(k, F0))
        if sec == 'A':
            x['A'][A_idx[idx]][-1] = Fr
        elif sec == 'B':
            x['B'][idx][-1] = Fr
        else:
            x['restore'][idx][-1] = Fr
    E = RB.end_frames(w)
    n = 2 * FX.V + w['report']['R']
    start = {q: () for q in range(2 * FX.V, n)}
    for q, U in w.get('start_extra', {}).items():
        start[int(q)] = FX.basis(tuple(U))
    live = set(RB.live_registers(w))
    inv = collections.Counter(len(E[q]) - len(start[q]) for q in range(2 * FX.V, n) if q in live)
    x['report'] = dict(x['report'])
    x['report']['local_profile'] = sprof(sol['profile'])
    x['report']['width_inventory'] = {str(k): v for k, v in sorted(inv.items())}
    x.pop('cleanup', None)
    return x


def audit(w):
    """vendored PR2833 auditor, in-process; returns its status or the failing requirement"""
    with tempfile.TemporaryDirectory(prefix='rank7sro-audit-') as d:
        p = Path(d) / 'w.json.gz'
        p.write_bytes(gzip.compress(json.dumps(w, separators=(',', ':')).encode(), mtime=0))
        sink = io.StringIO()
        try:
            with contextlib.redirect_stdout(sink):
                rec = RB.AL.run(p, Path(d) / 'r.json')
        except RuntimeError as ex:
            return dict(status='FAIL', reason=str(ex)[:160])
        return dict(status=rec['status'], forward=rec['orientations']['forward'], dual=rec['orientations']['dual'])


def price_and_audit(w, rows, base_cost):
    """exactness (Lemma 1 end conditions) and certified cost of a restore-only variant, plus the vendored auditor"""
    fin = RB.run_restore(w['restore'], rows)
    dirty, leaks, targets = RB.end_conditions(w, fin, rows)
    try:
        sol = FX.frame_optimum(w)
    except FX.Infeasible as ex:
        return dict(exact=not dirty and not leaks and not targets, dirty=len(dirty), leaks=len(leaks), feasible=False,
                    why=str(ex)[:120])
    out = dict(exact=not dirty and not leaks and not targets, dirty=len(dirty), leaks=len(leaks), feasible=True,
               delta=sol['cost'] - base_cost, profile=sprof(sol['profile']))
    out['auditor'] = audit(framed(w, sol))
    return out


# ------------------------------------------------------------------------------------------------ the theorem per provider
def certify(name, w):
    t0 = time.monotonic()
    c = FX.weights()
    require(tuple(c[:6]) == WEIGHTS, 'integer weights')
    sol = FX.frame_optimum(w)
    require(sol['cost'] == EXPECT['cost'] and iprof(sol['profile']) == CLAIM_PROFILE, 'certified optimum of ' + name)
    require(iprof(w['report']['local_profile']) == CLAIM_PROFILE, 'declared profile')
    require((sol['variables'], sol['components'], sol['largest_component']) == (EXPECT['variables'], EXPECT['components'], EXPECT['largest']),
            'frame-graph structure (PR3065 independently reports 743 variables, 210 components, largest 94)')
    lit = RB.literal_restore_chains(w)
    rows = RB.entry_rows(w)
    R = RB.restored(w)
    live = RB.live_registers(w)
    require(len(live) == EXPECT['live'] and len(R) == EXPECT['restored'], 'register counts')
    Mc, rk = RB.coordinates(rows, {x: {(x, ()): Q(1)} for x in R})
    require(rk == len(live), 'restore-entry rows independent (rank %d)' % rk)
    rmap = RB.restore_map(w)
    require(all({q: v for q, v in rmap[x].items() if v} == Mc[x] for x in R), 'the current restore realizes the forced coordinates')
    fin = RB.run_restore(w['restore'], rows)
    dirty, leaks, targets = RB.end_conditions(w, fin, rows)
    require(not dirty and not leaks and not targets, 'current restore exact (Lemma 1 conditions)')
    aud = audit(w)
    require(aud['status'] == 'PASS_INDEPENDENT_EXACT_BORROWING_WORD' and aud['forward'] == aud['dual'] == 'PASS', 'auditor on ' + name)
    b = RB.bound(w, rows=rows, M={x: dict(v) for x, v in Mc.items()})
    require(b['forced_caps'] == EXPECT['caps'], 'forced caps')
    require(b['LB_forced'] == EXPECT['lb'] and iprof(b['LB_profile']) == EXPECT['lb_profile'], 'LB_forced')
    require((b['blocked'], b['extras_blocked'], b['groups'], b['extras_open']) ==
            (EXPECT['blocked'], EXPECT['blocked_units'], EXPECT['groups'], EXPECT['group_units']), 'classification totals')
    require(b['bound'] == sol['cost'], 'bound == certified cost (tight)')
    visits = {q: x['overhead'] for q, x in lit.items() if x['overhead']}
    require(len(visits) == EXPECT['visits'] and sum(visits.values()) == EXPECT['forced'], 'literal visits')
    require(sum(visits.values()) == sol['cost'] - b['LB_forced'], 'literal visits = cost - LB_forced')
    beta = {int(x): v for x, v in b['beta'].items()}
    require(all(visits.get(x, 0) == v for x, v in beta.items()), 'each blocked register pays exactly its forced extra')
    unit = 2 * c[1] - c[2]
    group_of = {}
    for i, m in enumerate(b['merged']):
        vis = [q for q in m['members'] if q in visits and q not in beta]
        require(len(vis) == 1 and visits[vis[0]] == unit, 'each payer group has exactly one paying visit of 2c1 - c2')
        group_of[vis[0]] = i
    require(set(visits) == set(beta) | set(group_of), 'every literal visit is charged')
    facts = normal45_facts(w, b)
    table = []
    for q in sorted(visits):
        st = 'BLOCKED' if q in beta else 'OPEN-forced'
        kinds = [p['kind'] for p in b['merged'][group_of[q]]['parts']] if q in group_of else []
        table.append(dict(register=q, block=block_of(lit[q]['jumps'][0][0]), restored=q in R, entry_dim=lit[q]['entry_dim'], jumps=lit[q]['jumps'],
                          overhead=visits[q], verdict=st, charge=('beta' if q in beta else '/'.join(sorted(set(kinds)))),
                          payer_group=(b['merged'][group_of[q]]['members'] if q in group_of else None),
                          receivers=b['info'].get(str(q), {}).get('receivers'), leaks=b['info'].get(str(q), {}).get('leaks')))
    by_block = collections.OrderedDict()
    for row in table:
        e = by_block.setdefault(row['block'], dict(registers=[], units=0, verdicts=collections.Counter()))
        e['registers'].append(row['register'])
        e['units'] += row['overhead']
        e['verdicts'][row['charge']] += 1
    blocks = [dict(block=k, registers=v['registers'], units=v['units'], charges=dict(sorted(v['verdicts'].items())))
              for k, v in sorted(by_block.items(), key=lambda kv: -kv[1]['units'])]
    require(sum(x['units'] for x in blocks) == EXPECT['forced'], 'block totals')
    cert = dict(word=name, word_sha256=PINS['data/WORD-%s.json.gz' % name], certified_cost=sol['cost'],
                certified_profile=sprof(sol['profile']), frame_graph=dict(variables=sol['variables'], components=sol['components'],
                                                                          largest_component=sol['largest_component']),
                weights=dict(c1=c[1], c2=c[2], c3=c[3], c4=c[4], c5=c[5], visit_unit=unit),
                restore_entry=dict(live_registers=len(live), rank=rk, restored_helpers=len(R), forced_coordinates_match_restore=True),
                current_restore=dict(gates=len(w['restore']), dirty=dirty, leaks=leaks, targets_changed=targets, auditor=aud),
                forced_caps=b['forced_caps'], caps=b['caps'], LB_forced=b['LB_forced'], LB_profile=b['LB_profile'],
                blocked=b['blocked'], extras_blocked=b['extras_blocked'], payer_groups=b['groups'], extras_open=b['extras_open'],
                bound=b['bound'], gap=sol['cost'] - b['bound'], literal_visits=len(visits), literal_visit_units=sum(visits.values()),
                visits=table, visit_blocks=blocks, groups=b['merged'], blocked_detail=b['why'], open_detail=b['open_info'], normal45=facts,
                theorem=('For every exact restore-only rewrite of WORD-%s (A, B, warps, cut, corrections, compensation, start '
                         'frames, helper ends and buffers fixed; any restore gate sequence; all frames re-solved; exact = PR2833 '
                         'auditor), certified cost >= LB_forced + forced extras = %d = certified cost of WORD-%s.') % (name, b['bound'], name),
                seconds=None)
    return cert, dict(sol=sol, rows=rows, M=Mc, b=b, lit=lit, seconds=round(time.monotonic() - t0, 2))


def normal45_facts(w, b):
    """the four normal-45 visits: eight pairwise-distinct 6-dim entry lower bounds inside V45; no partner"""
    LU = b['_LU']
    E = b['_E']
    V45 = E[NORMAL45['pivots'][0]]
    eight = NORMAL45['visitors'] + NORMAL45['pivots']
    require(all(E[p] == V45 and len(V45) == 7 for p in NORMAL45['pivots']), 'pivots end at V45')
    Ls = {q: LU[q][0] for q in eight}
    require(all(len(Ls[q]) == 6 and FX.leq(Ls[q], V45) for q in eight), 'eight 6-dim entry frames inside V45')
    require(len(set(Ls.values())) == 8, 'pairwise distinct')
    require(len(FX.basis(tuple(v for q in eight for v in Ls[q]))) == 7, 'they span V45')
    live = [q for q in LU if not RB.is_target(q)]
    rows = []
    for r in NORMAL45['visitors']:
        recv = b['caps'][str(r)]['receivers']
        for c in recv:
            X = FX.meet(LU[r][1], E[c])
            require(X == Ls[r], 'U_r meet E_c = L_r for visitor %d receiver %d' % (r, c))
            require(not any(s != r and FX.leq(LU[s][0], Ls[r]) and FX.leq(Ls[r], E[s]) for s in live), 'no partner for %d' % r)
        rows.append(dict(register=r, receivers=recv, entry_lower=list(Ls[r]), beta=b['beta'][str(r)]))
    return dict(V45=list(V45), entry_lower_bounds={str(q): list(Ls[q]) for q in eight}, visitors=rows)


# ------------------------------------------------------------------------------------------------ calibration and erratum
def calibration(name):
    """the same bound on PR #2979's words (same A/B): the unforced part of its restore overhead is exactly what PR #3042 removed"""
    w = load_word(name)
    sol = FX.frame_optimum(w)
    require(sol['cost'] == EXPECT['cost2979'] and iprof(sol['profile']) == PR2979_PROFILE, 'PR2979 certified optimum')
    b = RB.bound(w)
    lit = RB.literal_restore_chains(w)
    visits = {q: x['overhead'] for q, x in lit.items() if x['overhead']}
    beta = {int(x): v for x, v in b['beta'].items()}
    unit = 2 * FX.weights()[1] - FX.weights()[2]
    blocked_excess = {str(q): visits.get(q, 0) - v for q, v in sorted(beta.items()) if visits.get(q, 0) != v}
    require(all(visits.get(q, 0) >= v for q, v in beta.items()), 'every blocked register pays at least its forced extra')
    in_group = set()
    group_excess = []
    for m in b['merged']:
        vis = {q: visits[q] for q in m['members'] if q in visits and q not in beta}
        require(sum(vis.values()) >= unit, 'every payer group pays at least one visit')
        in_group |= set(vis)
        if sum(vis.values()) > unit:
            group_excess.append(dict(members_visiting={str(q): v for q, v in sorted(vis.items())}, forced=unit,
                                     excess=sum(vis.values()) - unit, kinds=sorted({p['kind'] for p in m['parts']})))
    uncharged = {str(q): v for q, v in sorted(visits.items()) if q not in beta and q not in in_group}
    total = sum(blocked_excess.values()) + sum(g['excess'] for g in group_excess) + sum(uncharged.values())
    involved = sorted({int(q) for q in blocked_excess} | {int(q) for q in uncharged} |
                      {int(q) for g in group_excess for q in g['members_visiting']})
    require(b['bound'] == EXPECT['cost'] and sol['cost'] - b['bound'] == total == EXPECT['cost2979'] - EXPECT['cost'], 'PR2979 bound')
    require(set(SKIPS_3042) <= set(involved) and total == len(SKIPS_3042) * unit, 'unforced overhead = the six PR3042 skips')
    return dict(word=name, word_sha256=PINS['data/WORD-%s.json.gz' % name], certified_cost=sol['cost'], certified_profile=sprof(sol['profile']),
                LB_forced=b['LB_forced'], bound=b['bound'], gap=sol['cost'] - b['bound'], literal_visits=len(visits),
                literal_visit_units=sum(visits.values()), blocked_excess=blocked_excess, group_excess=group_excess,
                uncharged_visits=uncharged, unforced_total=total, registers_involved=involved, pr3042_skips=SKIPS_3042,
                realized_by_pr3042=EXPECT['cost2979'] - EXPECT['cost'])


def erratum():
    spec = json.loads((HERE / 'data/EDITS-3042.json').read_bytes())
    out = {}
    for prov in ('base', 'extra'):
        w = load_word('2979-' + prov)
        f = load_word('3042-' + prov)
        c0 = FX.frame_optimum(w)
        lit0 = RB.literal_restore_chains(w)
        edits = {e['id']: e for e in spec['edits'][prov]}
        require(sorted(edits) == ['R1_E42', 'R2_E7'], 'two declared blocks')

        def apply(ids):
            x = copy.deepcopy(w)
            for e in sorted((edits[i] for i in ids), key=lambda e: -e['start']):
                require(e['section'] == 'restore' and x['restore'][e['start']:e['stop']] == e['old'], 'literal preimage ' + e['id'])
                x['restore'][e['start']:e['stop']] = copy.deepcopy(e['new'])
            return x
        rows = {}
        for ids in (['R1_E42'], ['R2_E7'], ['R1_E42', 'R2_E7']):
            x = apply(ids)
            s = FX.frame_optimum(x)
            lit = RB.literal_restore_chains(x)
            changed = sorted(q for q in lit if lit[q]['overhead'] != lit0[q]['overhead'])
            dp = {str(k): iprof(s['profile']).get(k, 0) - iprof(c0['profile']).get(k, 0) for k in range(1, 9)
                  if iprof(s['profile']).get(k, 0) != iprof(c0['profile']).get(k, 0)}
            rows['+'.join(ids)] = dict(delta_units=s['cost'] - c0['cost'], profile_delta=dp, skipped_registers=changed,
                                       literal_skip_units=sum(lit0[q]['overhead'] - lit[q]['overhead'] for q in changed))
            if len(ids) == 2:
                require(x['restore'] == f['restore'] and all(x[k] == f[k] for k in f if k not in ('restore', 'report', 'cleanup')),
                        'both blocks reproduce the PR3042 word')
        require(rows['R1_E42']['delta_units'] == -19984 and rows['R1_E42']['skipped_registers'] == [22, 40, 54, 63], 'R1_E42')
        require(rows['R2_E7']['delta_units'] == -9992 and rows['R2_E7']['skipped_registers'] == [5, 73], 'R2_E7')
        require(rows['R1_E42+R2_E7']['delta_units'] == -29976, 'total')
        out[prov] = rows
    require(out['base'] == out['extra'], 'providers agree')
    sizes = {e['id']: '%d -> %d' % (len(e['old']), len(e['new'])) for e in spec['edits']['base']}
    require(sizes == {'R1_E42': '26 -> 33', 'R2_E7': '13 -> 15'}, 'declared block sizes')
    return dict(certified=out['base'], providers_identical=True, declared_block_gates=sizes, pr3042_readme=PR3042_README,
                corrections=dict(R1_E42='-19,984 units/call (four skips: 63, 54, 40, 22; -8 H1 + 4 H2), not -14,888 for 63, 54, 40',
                                 R2_E7='-9,992 units/call (two skips: 73, 5; -4 H1 + 2 H2), not -14,938 for 22, 73, 5',
                                 total='-29,976 units/call (-12 H1 + 6 H2 = 6 x 4,996), not -29,826; final words, profile and kappa unaffected'))


# ------------------------------------------------------------------------------------------------ controls
def controls(state):
    w = load_word('3042-base')
    st = state['3042-base']
    rows, sol, b = st['rows'], st['sol'], st['b']
    base = sol['cost']
    out = {}
    # auditor semantics: appended gates between non-restored FULL registers pass with cost delta 0
    sem = []
    for g in (['add', 0, 1, 1, 1, list(FX.FULL9)], ['add', 62, 70, 1, 1, list(FX.FULL9)]):
        x = copy.deepcopy(w)
        x['restore'].append(g)
        r = price_and_audit(x, rows, base)
        require(r['exact'] and r['delta'] == 0 and r['auditor']['status'] == 'PASS_INDEPENDENT_EXACT_BORROWING_WORD', 'appended ' + str(g[:5]))
        sem.append(dict(appended=g[:5], **r))
    x = copy.deepcopy(w)
    x['restore'].append(['add', 249, 251, 1, 1, list(b['_E'][249])])
    r = price_and_audit(x, rows, base)
    require(not r['exact'] and r['auditor']['status'] == 'FAIL', 'a gate into a restored helper is rejected')
    sem.append(dict(appended=['add', 249, 251, 1, 1], **r))
    out['auditor_semantics'] = sem
    # attainment: two third-party restore rewrites (different gate sequences) tie the bound
    att = []
    for label, block in (('PR3056 three-ADD contraction of restore[175:179]', PR3056_175), ('PR3060 four-gate tariff word of restore[175:179]', PR3060_175)):
        x = copy.deepcopy(w)
        require(x['restore'][175:179] == OLD_175, 'literal block')
        x['restore'][175:179] = copy.deepcopy(block)
        r = price_and_audit(x, rows, base)
        require(r['exact'] and r['delta'] == 0 and r['auditor']['status'] == 'PASS_INDEPENDENT_EXACT_BORROWING_WORD', label)
        att.append(dict(control=label, gates=len(x['restore']), **r))
    out['attainment'] = att
    rej = []

    def rejected(label, fn):
        try:
            fn()
        except (AssertionError, ValueError, KeyError) as ex:
            rej.append(dict(control=label, rejected=True, reason=str(ex)[:160]))
            return
        raise AssertionError('control was not rejected: ' + label)
    # 1-2 source binding
    rejected('mislabeled provider (extra export under the base pin)',
             lambda: require(sha(HERE / 'data/WORD-3042-extra.json.gz') == PINS['data/WORD-3042-base.json.gz'], 'pinned export mismatch'))
    raw = bytearray((HERE / 'data/WORD-3042-base.json.gz').read_bytes())
    raw[len(raw) // 2] ^= 1
    rejected('one flipped byte in the base export', lambda: require(hashlib.sha256(bytes(raw)).hexdigest() == PINS['data/WORD-3042-base.json.gz'], 'pinned export mismatch'))
    # 3 wrong cap: weakening one forced cap lowers LB_forced below the cost, and the recomputed caps differ
    caps = {int(r): tuple(v['cap']) for r, v in b['caps'].items()}
    weak = dict(caps)
    weak.pop(2)
    lb_weak = FX.frame_optimum(RB.empty_restore(w), caps=weak)['cost']
    require(lb_weak < b['LB_forced'], 'the cap of register 2 is load-bearing')
    rejected('certificate with the cap of register 2 dropped (LB %d)' % lb_weak,
             lambda: require(lb_weak + b['extras_blocked'] + b['extras_open'] == base and len(weak) == len(caps), 'tight sum fails without the cap'))
    # 4 dropped visit
    rejected('certificate with the forced visit of register 44 dropped',
             lambda: require(b['LB_forced'] + b['extras_blocked'] - b['beta']['44'] + b['extras_open'] == base, 'tight sum fails'))
    # 5 perturbed entry row
    def perturbed():
        rows2 = {q: dict(v) for q, v in rows.items()}
        rows2[70] = dict(rows2[70])
        rows2[70][(70, ())] = rows2[70][(70, ())] * 2
        Mc2, rk2 = RB.coordinates(rows2, {x: {(x, ()): Q(1)} for x in RB.restored(w)})
        rmap = RB.restore_map(w)
        require(all({q: v for q, v in rmap[x].items() if v} == Mc2[x] for x in RB.restored(w)), 'restore does not realize the perturbed coordinates')
    rejected('perturbed restore-entry row of register 70', perturbed)
    # 6-8 fake cheaper restores that violate exactness (cheaper certified frames, rejected by Lemma 1 and by the auditor)
    fakes = []
    for label, edit in (('empty restore', lambda x: x.__setitem__('restore', [])),
                        ('deleted R44 475 += -1/2*498 (keeps a restored input in 475)', lambda x: x['restore'].pop(44)),
                        ('deleted R82 584 += -1*439 (restored 584 not its own input)', lambda x: x['restore'].pop(82))):
        x = copy.deepcopy(w)
        edit(x)
        r = price_and_audit(x, rows, base)
        require(r['feasible'] and r['delta'] < 0, 'fake restore is cheaper: ' + label)
        require(not r['exact'] and r['auditor']['status'] == 'FAIL', 'fake restore rejected twice: ' + label)
        fakes.append(dict(control=label, **r))
        rejected('fake cheaper restore: %s (delta %d)' % (label, r['delta']),
                 lambda r=r: require(r['exact'], 'Lemma 1 end conditions fail (%d dirty restored, %d leaks); auditor: %s' % (
                     r['dirty'], r['leaks'], r['auditor'].get('reason', ''))))
    out['fake_cheaper_restores'] = fakes
    # 9 wrong claimed cost
    rejected('claimed cost 10,868,103,086', lambda: require(base == 10868103086, 'recomputed certified cost differs'))
    # 10 optimality claim for PR2979's words (calibration: the bound leaves a gap)
    rejected('optimality claimed for PR2979 base', lambda: require(state['2979-base']['gap'] == 0, 'PR2979 gap 29,976'))
    # 11 ablation of the departure lemma: rows restricted to receivers containing the frame
    abl = ablation(w, b)
    rejected('departure lemma with rows restricted to receivers containing the frame (bound %d)' % abl['bound'],
             lambda: require(abl['bound'] == base, 'the restricted lemma no longer certifies optimality'))
    # 12 caps taken from the restore map of the emptied word (lane K's fixed bug class) instead of forced coordinates
    w0 = RB.empty_restore(w)
    caps_bug, _ = RB.forced_caps(RB.restore_map(w0), b['_E'], RB.restored(w0))
    b0 = RB.bound(w0)
    require(b0['bound'] == base and b0['forced_caps'] == EXPECT['caps'], 'the bound depends only on A/B (caps from coordinates)')
    rejected('caps from the restore map of the emptied word (%d caps)' % len(caps_bug), lambda: require(len(caps_bug) == EXPECT['caps'], 'no caps'))
    out['rejection'] = rej
    out['ablation'] = abl
    out['empty_restore_word_bound'] = dict(bound=b0['bound'], forced_caps=b0['forced_caps'])
    require(len(rej) >= 8, 'rejection controls')
    return out


def ablation(w, b):
    """departure test with rows restricted to restored c whose end contains the departure frame: the (1,3) splits of the
    eight (2,2) registers are admitted and the bound drops by 8 x (c2 + c2 - c4 - (c1 + c3 - c4))"""
    c = FX.weights()
    E = b['_E']
    LU = b['_LU']
    M = b['_M']
    R = RB.restored(w)
    live = [q for q in LU if not RB.is_target(q)]
    drop = 0
    admitted = []
    for x, why in b['why'].items():
        x = int(x)
        for ex in why['excluded_two_jump_frames']:
            if 'departure' not in ex['why']:
                continue
            G = tuple(ex['frame'])
            SG = set(FX.span(G))
            Z = [x] + [y for y in live if y != x and set(FX.span(LU[y][0])) <= SG]
            O = [cc for cc in sorted(R) if cc != x and FX.leq(G, E[cc]) and not FX.leq(E[x], E[cc])]
            mat = [[M[cc].get(q, Q(0)) for q in Z] for cc in O]
            if RB.rank([r_ for r_ in mat if any(r_)]) < len(Z):
                dE = len(E[x])
                d = len(LU[x][0])
                f = len(G)
                o = c[f - d] + c[dE - f] - c[dE - d]
                if o < b['beta'][str(x)]:
                    admitted.append(dict(register=x, frame=list(G), overhead=o, beta=b['beta'][str(x)]))
    best = {}
    for a in admitted:
        best[a['register']] = min(best.get(a['register'], a['beta']), a['overhead'])
    drop = sum(b['beta'][str(x)] - v for x, v in best.items())
    return dict(admitted=admitted, registers=sorted(best), bound=b['bound'] - drop, drop=drop)


# ------------------------------------------------------------------------------------------------ main
def canonical(x):
    return json.dumps(x, indent=1, sort_keys=True, default=str) + '\n'


def strip(cert):
    return {k: v for k, v in cert.items() if not k.startswith('_') and k != 'seconds'}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--work', type=Path, help='write RESULT.json and the regenerated certificates here')
    a = ap.parse_args()
    t0 = time.monotonic()
    n = authenticate()
    certs = {}
    state = {}
    for prov in ('base', 'extra'):
        name = '3042-' + prov
        cert, st = certify(name, load_word(name))
        certs['BOUND-%s.json' % name] = strip(cert)
        state[name] = st
        print('PASS', name, 'cost', cert['certified_cost'], '= LB_forced', cert['LB_forced'], '+ forced', cert['extras_blocked'] + cert['extras_open'],
              '(caps %d, blocked %d, groups %d, visits %d)' % (cert['forced_caps'], cert['blocked'], cert['payer_groups'], cert['literal_visits']),
              st['seconds'], 's', flush=True)
    a_ = dict(certs['BOUND-3042-base.json'])
    b_ = dict(certs['BOUND-3042-extra.json'])
    for k in ('word', 'word_sha256', 'theorem'):
        a_.pop(k)
        b_.pop(k)
    require(canonical(a_) == canonical(b_), 'both providers give the identical certificate')
    cal = {}
    for prov in ('base', 'extra'):
        cal[prov] = calibration('2979-' + prov)
        state['2979-' + prov] = dict(gap=cal[prov]['gap'])
    require({k: v for k, v in cal['base'].items() if k not in ('word', 'word_sha256')} ==
            {k: v for k, v in cal['extra'].items() if k not in ('word', 'word_sha256')}, 'calibration agrees')
    certs['CALIBRATION-2979.json'] = cal
    print('PASS calibration: bound on PR2979 words', cal['base']['bound'], 'gap', cal['base']['gap'], '= unforced overhead of',
          cal['base']['registers_involved'], flush=True)
    err = erratum()
    certs['ERRATUM-3042.json'] = err
    print('PASS erratum: R1_E42', err['certified']['R1_E42']['delta_units'], err['certified']['R1_E42']['skipped_registers'],
          'R2_E7', err['certified']['R2_E7']['delta_units'], err['certified']['R2_E7']['skipped_registers'], flush=True)
    ctl = controls(state)
    certs['CONTROLS.json'] = ctl
    print('PASS controls: auditor semantics %d, attainment %d, rejection %d, ablation drop %d' % (
        len(ctl['auditor_semantics']), len(ctl['attainment']), len(ctl['rejection']), ctl['ablation']['drop']), flush=True)
    result = dict(status='PASS_RANK7_SKIP_RESTORE_OPTIMUM', providers=2, pinned_inputs=n, certified_cost=EXPECT['cost'],
                  LB_forced=EXPECT['lb'], forced_caps=EXPECT['caps'], forced_extras=EXPECT['forced'], blocked=EXPECT['blocked'],
                  payer_groups=EXPECT['groups'], calibration_gap_2979=cal['base']['gap'], rejection_controls=len(ctl['rejection']),
                  certificates={k: hashlib.sha256(canonical(v).encode()).hexdigest() for k, v in sorted(certs.items())},
                  no_new_kappa=True)
    if a.work:
        a.work.mkdir(parents=True, exist_ok=True)
        for k, v in certs.items():
            (a.work / k).write_text(canonical(v))
        (a.work / 'RESULT.json').write_text(canonical(result))
    else:
        for k, v in list(certs.items()) + [('RESULT.json', result)]:
            stored = (HERE / 'certificates' / k).read_text()
            require(stored == canonical(v), 'regenerated certificate differs from certificates/' + k)
    print('PASS_RANK7_SKIP_RESTORE_OPTIMUM providers=2 cost=%d LB_forced=%d forced=%d caps=%d blocked=%d groups=%d rejections=%d '
          'calibration_gap=%d no_new_kappa (%.1f s)' % (EXPECT['cost'], EXPECT['lb'], EXPECT['forced'], EXPECT['caps'], EXPECT['blocked'],
                                                        EXPECT['groups'], len(ctl['rejection']), cal['base']['gap'], time.monotonic() - t0))


if __name__ == '__main__':
    main()

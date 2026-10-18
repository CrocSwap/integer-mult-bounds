#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bounded replay: exact climb ledger, adjoint responses, dirty-entry and frame-refit screens, with controls.

`--part core`   (about 1 minute): input pins; ledger reproduces both providers' reported profiles/inventories;
                response model reproduces stored compensation; positive control (PR2833 words -> exactly the
                16 PR2853 quartet helpers); current PR2857 and PR2894 words -> 0 helpers in `direct` and `pre-only` modes;
                frame-refit screens -> 0 improving moves; failure controls (corrupted compensation, broken frame
                chain, frame-relaxed subset, de-optimised word found by the refit screen); dual sanity.
`--part chains2857|chains2894` (about 4 minutes each): one-hop relays on both providers of that word family:
                apparent relays exist, none valid; (chains2857) the validity test accepts a known PR2833 quartet relay.

Prepared for digitalis-p with Claude (Anthropic) assistance. Apache-2.0.
"""
import argparse
import copy
import hashlib
import json
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools'))
import wordlib as W  # noqa: E402
import entry_screen as ES  # noqa: E402
import refit_screens as RS  # noqa: E402
import dual_screen as DS  # noqa: E402

QUARTETS = [460, 461, 462, 463, 468, 469, 470, 471, 478, 479, 480, 481, 490, 491, 492, 493]
PROFILE_2857 = {1: 2394, 2: 642, 3: 266, 4: 128, 5: 26, 8: 8}
INV_2857 = {4: 26, 5: 2, 7: 62, 8: 84, 9: 234}
PROFILE_2894 = {1: 2404, 2: 642, 3: 262, 4: 128, 5: 26, 8: 8}
INV_2894 = {4: 26, 5: 2, 7: 62, 8: 86, 9: 232}
PROFILE_2833 = {1: 2382, 2: 650, 3: 266, 4: 128, 5: 26, 8: 8}
INV_2833 = {4: 26, 5: 2, 7: 62, 8: 80, 9: 238}


def need(ok, msg):
    if not ok:
        raise SystemExit('FAIL: ' + msg)


def inputs():
    pins = json.loads((ROOT / 'vendor' / 'INPUTS.json').read_text())
    words = {}
    for item in pins['files']:
        path = ROOT / item['path']
        need(hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256'], 'input pin ' + item['path'])
        if item['path'].endswith('.json.gz'):
            words[item['role']] = W.load(path)[0]
    need(set(words) == {'pr2857-base', 'pr2857-extra', 'pr2833-base', 'pr2833-extra', 'pr2894-base', 'pr2894-extra'},
         'input roles')
    return words


def core(words, report):
    for role, x in words.items():
        paid, inv = W.ledger(x)
        exp_p, exp_i = {'pr2857': (PROFILE_2857, INV_2857), 'pr2894': (PROFILE_2894, INV_2894),
                        'pr2833': (PROFILE_2833, INV_2833)}[role[:6]]
        need(dict(paid) == exp_p and dict(inv) == exp_i, 'ledger profile/inventory ' + role)
        need(dict(paid) == {int(k): v for k, v in x['report']['local_profile'].items()}, 'reported profile ' + role)
        resp, taint, _, _ = W.adjoint(x)
        match, mismatch = W.check_responses(x, resp, taint)
        need(match == 402 and len(mismatch) == 6 and all(m['tainted'] and m['correction_source'] for m in mismatch),
             'response model vs stored compensation ' + role)
        report['ledger_and_responses_' + role] = dict(profile=dict(paid), inventory=dict(inv), response_match=match,
                                                      tainted_correction_sources=[m['helper'] for m in mismatch])
    # positive control and main negative result
    for role, x in words.items():
        for mode in ('direct', 'pre-only'):
            sc = ES.Screen(x, mode)
            elig = [h for h in range(2 * W.V, W.NREG) if sc.eligible(h)]
            rows = [sc.run(h) for h in elig]
            hits = sorted(r['q0'] for r in rows if r.get('in_span'))
            zero = sorted(r['q0'] for r in rows if r.get('reason'))
            if role.startswith('pr2833'):
                need(hits == QUARTETS, 'positive control (PR2853 quartets) %s %s: %s' % (role, mode, hits))
            else:
                need(hits == [], 'current word has a dirty-entry candidate %s %s: %s' % (role, mode, hits))
            report['entry_%s_%s' % (role, mode)] = dict(eligible=len(elig), in_span=hits, zero_frame_first=len(zero))
    # consistency with PR2894: its two preload-move quartets are zero-frame-first helpers of the PR2857 words
    # (outside the fixed-gate class screened here); PR2894 lets one member of each (457, 458) enter dirty
    pm = [456, 457, 458, 459, 464, 465, 466, 467]
    for side in ('base', 'extra'):
        need(set(pm) <= set(range(2 * W.V, W.NREG)) and
             all(len(W.basis(next(e for _, _, e in W.program(words['pr2857-' + side])
                                  if e[0] in ('add', 'scale') and h in W.regs_of(e))[-1])) == 0 for h in pm),
             'PR2894 quartets are not zero-frame-first in PR2857 ' + side)
        new_entries = sorted(set(map(int, words['pr2894-' + side]['start_extra']))
                             - set(map(int, words['pr2857-' + side]['start_extra'])))
        need(new_entries == [457, 458], 'PR2894 new dirty entries ' + side + ': %s' % new_entries)
    report['pr2894_quartets_zero_frame_first_in_pr2857'] = pm
    for role in ('pr2857-base', 'pr2857-extra', 'pr2894-base', 'pr2894-extra'):
        r = RS.screens(words[role])
        need(not r['single']['improving'] and not r['forward']['improving'] and not r['backward']['improving'],
             'refit improvement on ' + role)
        report['refit_' + role] = {k: {kk: (len(vv) if isinstance(vv, list) else vv) for kk, vv in v.items()}
                                   for k, v in r.items()}
    x = words['pr2857-base']
    # failure control 1: corrupted compensation must be detected by the response model
    bad = copy.deepcopy(x)
    g = bad['compensation'][0]
    g[3] = g[3] + g[4]
    resp, taint, _, _ = W.adjoint(bad)
    match, _ = W.check_responses(bad, resp, taint)
    need(match < 402, 'corrupted compensation not detected')
    # failure control 2: a broken frame chain must be rejected by the ledger
    bad = copy.deepcopy(x)
    climbed, nxt = set(), None
    for i, e in enumerate(bad['A']):
        if e[0] != 'add':
            continue
        if set(W.regs_of(e)) & climbed:
            nxt = i
            break
        if len(W.basis(e[-1])) > 0:
            climbed |= set(W.regs_of(e))
    need(nxt is not None, 'no gate for the broken-chain control')
    bad['A'][nxt] = bad['A'][nxt][:-1] + [[]]
    try:
        W.ledger(bad)
        need(False, 'broken frame chain accepted')
    except W.LedgerError:
        pass
    # failure control 3: with frames relaxed the same algebra finds every subset helper in span
    subset = [401, 409, 413, 417, 429, 440, 461, 242, 246, 300, 502, 514]
    sc = ES.Screen(x, 'direct', relax=True)
    rel = sorted(h for h in subset if sc.run(h).get('in_span'))
    need(rel == sorted(subset), 'frame-relaxed control: %s' % rel)
    report['relaxed_subset_in_span'] = rel
    # failure control 4: a de-optimised word (one climb split by lowering a gate frame) is repaired by the screen
    found = None
    start, ev, gates, _, pos = RS.build(x)
    for i, e in enumerate(x['A']):
        key = ('A', i)
        if e[0] != 'add' or key not in gates:
            continue
        u = gates[key]['frame']
        lo = W.join(*[RS.frame_at(r, pos[(r, key)], start, ev, gates, {}, True)[0] for r in gates[key]['regs']])
        if len(u) - len(lo) < 2:
            continue
        extra = next(v for v in u if not W.contained((v,), lo))
        y = copy.deepcopy(x)
        y['A'][i] = e[:-1] + [list(W.join(lo, (extra,)))]
        try:
            W.ledger(y)
        except W.LedgerError:
            continue
        found = (i, RS.screens(y)['single']['improving'])
        break
    need(found is not None and len(found[1]) > 0, 'refit screen missed a de-optimised climb')
    report['deoptimised_refit_control'] = dict(gate=found[0], improving_moves=len(found[1]))
    d = DS.rows()
    need(abs(d['phi_at_root'] - 1) < 1e-12, 'dual model normalisation')
    report['dual_phi_at_root'] = d['phi_at_root']


def chains(words, report, family):
    for role in (family + '-base', family + '-extra'):
        sc = ES.Screen(words[role], 'direct')
        rows = [sc.run(h, chains=True) for h in range(2 * W.V, W.NREG) if sc.eligible(h)]
        apparent = sorted(r['q0'] for r in rows if r.get('chain_relays'))
        valid = sorted(r['q0'] for r in rows if r.get('chain_valid'))
        need(apparent and not valid, 'chain result %s apparent=%s valid=%s' % (role, apparent, valid))
        report['chains_' + role] = dict(apparent=apparent, valid=valid)
    if family != 'pr2857':
        return
    # the validity test can return True: a direct quartet relay on the PR2833 word
    x = words['pr2833-base']
    sc = ES.Screen(x, 'direct')
    q0 = 478
    evs = sc.events(q0)
    t0, first = evs[0]
    partners = [(e[2], F(e[3], e[4]), k) for k, e in evs if e[0] == 'add' and e[1] == q0]
    pset = {s for s, _, _ in partners}
    opts = sc.direct_options(q0, t0, W.basis(first[-1]), partners, sc.horizon(q0, evs, t0), pset)
    ch = sc.chain_check(q0, {t: -v for t, v in sc.R0[q0].items()}, opts, pset)
    need(any(c['valid'] for c in ch), 'chain validity test never returns True')
    report['chain_validity_positive_control'] = dict(q0=q0, valid_relays=sum(c['valid'] for c in ch))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--part', choices=['core', 'chains2857', 'chains2894'], default='core')
    a = ap.parse_args()
    need(not sys.flags.optimize, 'assertions required')
    words = inputs()
    report = {}
    if a.part == 'core':
        core(words, report)
    else:
        chains(words, report, 'pr' + a.part[-4:])
    status = 'PASS_T185_DIRTY_ENTRY_SCREENS_' + a.part.upper()
    print(json.dumps(dict(status=status, **report), default=list))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay the exact packing statement, its failure controls and the recorded sweep tallies (standard library).

Checks:
  1. byte pins of the vendored #1193/#1207 inputs;
  2. packing.check(): exact helper-width recount from both words, flow conservation, the Phi lemma and the
     idle-remainder optimum for the fixed mix, compared with evidence/PACKING.json;
  3. failure controls: each mutation must be rejected at the intended check;
  4. the recorded sweep files recount to the tallies in RESULT.json (no gain in any family);
  5. evidence/AGGREGATE.json is present and reports ILP = incumbent (rerun it with aggregate.py; needs SciPy).
"""
import copy, gzip, hashlib, json, sys
from pathlib import Path

PKG = Path(__file__).resolve().parent
sys.path.insert(0, str(PKG))
import packing  # noqa: E402

PINS = {
    'inputs/D3-WORD.json.gz': '4e837da23d932fc1336ef84dd1a802b46dbcb43bcf783b1338eeb7fa260eca1e',
    'inputs/D4-WORD.json.gz': 'eccbead1c65cd56111c3516bd4f5ab0a002df34b1ffda1faa5e1c5eaf5baf0d7',
    'inputs/FLOW.json.gz': 'e8e6dfa66e083ff8f3617a8441b5b2d766c3c9d9ac62ddc37d99edc24051f79e',
    'inputs/MIX.json': 'dd86bbb792a5c9f0d7507d55bd2f8392c66716023934b03b24f48ca737204eea',
}


def rejected(mutate, expect, data, cache):
    d = copy.deepcopy(data)
    mutate(d)
    try:
        packing.check(d, cache)
    except AssertionError as e:
        if expect in str(e):
            return str(e)
        raise AssertionError(f'control rejected for the wrong reason: {e!r} (expected {expect!r})')
    raise AssertionError('control accepted: ' + expect)


def controls(data, cache):
    out = {}

    def swap_mix(d):            # one D4 call becomes D3
        i = next(i for i, e in enumerate(d['mix']) if e[0] == 'demote4'); d['mix'][i][0] = 'demote3'
    out['mix'] = rejected(swap_mix, 'call mix', data, cache)

    def widen(d):               # a width-4 helper of D3 starts one dimension lower (width 5)
        q = next(q for q, U in d['d3']['start_extra'].items() if len(U) == 4); d['d3']['start_extra'][q] = d['d3']['start_extra'][q][:3]
    out['inventory'] = rejected(widen, 'D3 width inventory', data, cache)

    def fill(d):                # make one remainder-one bin full without supplying a width-5 helper
        g = next(g for g in d['flow'] if any(p['widths'] == [4, 9, 9, 9] for p in g['patterns']))
        p = next(p for p in g['patterns'] if p['widths'] == [4, 9, 9, 9]); p['widths'] = [5, 9, 9, 9]
        f = next(x for x in p['flow'] if x[1] == 4); f[1] = 5
    out['conservation'] = rejected(fill, 'hosts every whole helper', data, cache)

    def drop_bin(d):            # remove one empty capacity-48 bin
        g = next(g for g in d['flow'] if any(p['widths'] == [] for p in g['patterns']))
        next(p for p in g['patterns'] if p['widths'] == [])['count'] -= 1
    out['bin_count'] = rejected(drop_bin, 'every port is one bin', data, cache)

    saved = dict(packing.PHI)   # weights without the invariant property break the full-bin lemma
    try:
        packing.PHI[9] = 0
        out['phi_weights'] = rejected(lambda d: None, 'Phi', data, cache)
    finally:
        packing.PHI.clear(); packing.PHI.update(saved)
    return out


def tallies():
    out = {}
    for w in ('D3', 'D4'):
        rows = json.load(gzip.open(PKG / f'evidence/sweeps/REPAIR-{w}.json.gz', 'rt'))
        ds = [r['best']['delta'] for r in rows if r['best']]
        fam = {'repair': dict(candidates=len(rows), feasible=len(ds), gains=sum(x < 0 for x in ds))}
        for name in ('exchange', 'joint'):
            rows = json.load(gzip.open(PKG / f'evidence/sweeps/{name.upper()}-{w}.json.gz', 'rt'))
            ds = [r['delta'] for r in rows if r['delta'] is not None]
            fam[name] = dict(candidates=len(rows), feasible=len(ds), gains=sum(x < 0 for x in ds))
        out[w] = fam
    return out


def main():
    for rel, h in PINS.items():
        assert hashlib.sha256((PKG / rel).read_bytes()).hexdigest() == h, 'input pin ' + rel
    data, cache = packing.load_inputs(), {}
    result = packing.check(data, cache)
    assert json.loads(json.dumps(result)) == json.loads((PKG / 'evidence/PACKING.json').read_text()), 'PACKING.json differs'
    ctl = controls(data, cache)
    claim = json.loads((PKG / 'RESULT.json').read_text())
    t = tallies()
    assert t == claim['sweeps'], 'sweep tallies'
    assert all(f['gains'] == 0 for w in t.values() for f in w.values())
    agg = json.loads((PKG / 'evidence/AGGREGATE.json').read_text())
    assert agg['ilp_minus_incumbent'] == 0.0 and agg['ilp_total_extra_groups'] == 208
    assert agg['price_structure_residual'] < 1e-9
    print(json.dumps(dict(packing=result['status'], controls_rejected=sorted(ctl), sweeps=t), sort_keys=True))
    print('PASS_X54_MIXED_T37_SATURATION_NO_NEW_KAPPA')


if __name__ == '__main__':
    main()

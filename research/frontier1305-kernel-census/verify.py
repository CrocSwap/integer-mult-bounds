#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Standard-library replay of the #1297/#1305 helper-donor kernel census (no new kappa).

Checks:
  1. inputs: SHA256 and Git blob ids of the three vendored words equal inputs/PINS.json (the #1297/#1305 blobs);
  2. census replay: census.py (exact rational two-shock relations, both restoration rules) is rerun on both final words
     and on the control word; every result equals evidence/CENSUS-*.json exactly;
  3. binding: every record of evidence/PRICES-*.json is exactly one census match, and every match is priced once;
  4. tallies: PRICES, RETIME, DELETION and IDLE-OPTIMUM evidence recount to RESULT.json; no priced or re-timed
     candidate has a negative delta (no gain);
  5. positive control: on #1297's input word the census reproduces #1297's five hooks for each of pivots 555 and 567
     (including its committed donors 620 and 628), each priced at the realized kernel gain -11707 (H1 -3, H3 +1);
  6. true-moment bounds (revision 2): every priced or re-timed candidate with a surrogate optimum carries PR #1186
     revision 2's interval bounds, and none of them can lower the per-call moment at b by more than the bound declared in
     RESULT.json (max_gain_units_ceil, rounded up from exact rationals);
  7. failure controls: a one-byte input change, a changed early-read coefficient, a forged negative price, a priced edit
     absent from the census and a forged true-gain bound are each rejected at the intended check.
Coverage: this script recounts and binds the stored evidence; it does not rerun the frame optimization or the interval
certificates.  regenerate.py reruns every price with PR #1186 revision 3 and compares the evidence byte for byte.
"""
import collections, copy, gzip, hashlib, json, sys
from fractions import Fraction
from pathlib import Path
if not __debug__:
    raise SystemExit('verify.py: assertions are the checks; do not run with -O')
PKG = Path(__file__).resolve().parent
sys.path.insert(0, str(PKG))
import census  # noqa: E402
EV = PKG / 'evidence'
rd = lambda p: json.loads(Path(p).read_text())
canon = lambda x: json.dumps(x, sort_keys=True, separators=(',', ':'))
def blob(b): return hashlib.sha1(b'blob %d\0' % len(b) + b).hexdigest()

def check_pins(raw):
    pins = rd(PKG / 'inputs/PINS.json')['files']
    for name, pin in pins.items():
        b = raw[name]
        assert hashlib.sha256(b).hexdigest() == pin['sha256'], 'input pin: ' + name
        assert blob(b) == pin['git_blob'], 'input git blob: ' + name
    return pins

def pivots(w):
    B = w['B']; first = {}
    for i, g in enumerate(B): first.setdefault(g[1], i)
    return sorted({g[2] for i, g in enumerate(B) if g[0] == 'add' and g[2] >= 224 and i < first.get(g[2], len(B))})

def run_census(word_json, restore, only=None):
    census.W = word_json; census.RESTORE = restore
    return json.loads(canon(sorted((census.relations(q) for q in (only or pivots(word_json))), key=lambda r: r['pivot'])))

def match_key(m): return canon({k: v for k, v in m.items() if k != 'price'})

def check_binding(cen, priced):
    a = collections.Counter(match_key(m) for r in cen for m in r['matches'])
    b = collections.Counter(match_key(m) for m in priced)
    assert a == b, 'priced records must be exactly the census matches'

def tally(records, key):
    return dict(sorted(collections.Counter(key(r) for r in records).items()))

def price_key(r): return '%s:%s' % (r['price']['status'], r['price'].get('delta'))

def check_no_gain(priced, label):
    assert all(r['price'].get('delta') is None or r['price']['delta'] >= 0 for r in priced), 'negative price in ' + label

BOUND_FIELDS = ('realized_delta_units', 'gain_certified', 'max_gain_units_ceil', 'interval_width_units_ceil')
def check_bounds(records, get, label, declared):
    """every candidate with a surrogate optimum carries the interval bounds; returns (bounded, largest possible true gain)."""
    worst = Fraction(0); n = 0
    for r in records:
        p = get(r)
        if p.get('status') not in ('ok', 'uncertified'): continue
        assert all(k in p for k in BOUND_FIELDS), 'missing interval bounds in ' + label
        if p['delta'] < 0: continue
        g = Fraction(p['max_gain_units_ceil']); n += 1; worst = max(worst, g)
        assert g <= declared, 'possible true gain above the declared bound in ' + label
    return n, worst

def main():
    res = rd(PKG / 'RESULT.json'); raw = {n: (PKG / 'inputs' / n).read_bytes() for n in ('BASE-WORD.json.gz', 'EXTRA-WORD.json.gz', 'CONTROL-WORD.json.gz')}
    check_pins(raw)
    words = {k: json.loads(gzip.decompress(raw[f])) for k, f in (('base', 'BASE-WORD.json.gz'), ('extra', 'EXTRA-WORD.json.gz'), ('control', 'CONTROL-WORD.json.gz'))}
    out = dict(census={}, prices={}, retime={}, deletion={}, intervals={})
    declared = Fraction(res['true_moment_bound']['max_gain_units_ceil'])
    def bound(name, n_worst):
        n = n_worst[1] * 10 ** 6; assert n.denominator == 1
        out['intervals'][name] = dict(bounded=n_worst[0], max_gain_units_ceil=f'{n.numerator // 10 ** 6}.{n.numerator % 10 ** 6:06d}')
    for w in ('base', 'extra'):
        for rule in ('tail', 'first'):
            name = f'{w}-{rule}'; cen = run_census(words[w], rule)
            assert cen == rd(EV / f'CENSUS-{name}.json'), 'census replay differs: ' + name
            priced = rd(EV / f'PRICES-{name}.json'); check_binding(cen, priced); check_no_gain(priced, name)
            out['census'][name] = dict(pivots=len(cen), with_matches=sum(1 for r in cen if r['matches']), matches=sum(len(r['matches']) for r in cen))
            out['prices'][name] = tally(priced, price_key)
            bound('prices-' + name, check_bounds(priced, lambda r: r['price'], name, declared))
        rt = rd(EV / f'RETIME-{w}.json'); assert all(r['delta'] is None or r['delta'] >= 0 for r in rt), 'negative re-timing price'
        out['retime'][w] = tally(rt, lambda r: '%s:%s' % (r['status'], r['delta']))
        bound('retime-' + w, check_bounds(rt, lambda r: r, 'retime-' + w, declared))
        dl = rd(EV / f'DELETION-{w}.json')
        out['deletion'][w] = dict(statuses=tally(dl, lambda r: r['status']), negative=sum(1 for r in dl if r.get('delta') is not None and r['delta'] < 0))
    cen = run_census(words['control'], 'tail', [555, 567]); assert cen == rd(EV / 'CENSUS-control-tail.json'), 'control census replay differs'
    priced = rd(EV / 'PRICES-control-tail.json'); check_binding(cen, priced)
    by = {r['pivot']: r['matches'] for r in cen}
    assert [len(by[555]), len(by[567])] == [5, 5] and 620 in {m['donor'] for m in by[555]} and 628 in {m['donor'] for m in by[567]}, 'control hooks'
    assert {m['helper'] for m in by[555]} == {383} and {m['helper'] for m in by[567]} == {399}, 'control partners'
    assert all({k: r['price'][k] for k in ('status', 'delta', 'profile')} == dict(status='ok', delta=-11707, profile={'1': 2349, '2': 504, '3': 413, '4': 130, '5': 82})
               and r['price']['audit'] is True and r['price']['gain_certified'] is True for r in priced), 'control prices'
    true = sorted({tuple(r['price']['realized_delta_units']) for r in priced}); assert len(true) == 1 and true[0][1] < 0, 'control true delta'
    out['control'] = dict(matches=len(priced), delta=-11707, true_delta_units=list(true[0]), audit_local=True,
                          deletion=[r['status'] for r in rd(EV / 'DELETION-control.json')])
    idle = rd(EV / 'IDLE-OPTIMUM-1305.json')
    assert idle['status'] == 'PASS_1305_IDLE_SELECTION_EQUALS_EXACT_GROUP_OPTIMUM' and idle['improvable_groups'] == 0
    assert all(s['current'] == s['optimum'] for s in idle['shapes']) and sum(s['groups'] for s in idle['shapes']) == idle['groups']
    out['idle'] = {k: idle[k] for k in ('eligible', 'groups', 'group_sizes', 'improvable_groups', 'donors', 'receivers')}
    assert out == res['tallies'], 'evidence tallies differ from RESULT.json'
    # failure controls
    rejected = {}
    def expect(fn, needle, label):
        try: fn()
        except AssertionError as e:
            assert needle in str(e), (label, str(e)); rejected[label] = str(e); return
        raise AssertionError('control accepted: ' + label)
    bad = dict(raw); b = bytearray(bad['BASE-WORD.json.gz']); b[-5] ^= 1; bad['BASE-WORD.json.gz'] = bytes(b)
    expect(lambda: check_pins(bad), 'input pin', 'one-byte input change')
    w2 = copy.deepcopy(words['control']); first = next(i for i, g in enumerate(w2['B']) if g[1] == 555)
    j = next(i for i in range(first) if w2['B'][i][0] == 'add' and w2['B'][i][2] == 555); w2['B'][j][3] *= 3
    def mutated():
        assert run_census(w2, 'tail', [555]) == [r for r in rd(EV / 'CENSUS-control-tail.json') if r['pivot'] == 555], 'census replay differs: mutated coefficient'
    expect(mutated, 'census replay differs', 'changed early-read coefficient')
    forged = copy.deepcopy(rd(EV / 'PRICES-base-tail.json')); next(r for r in forged if r['price']['status'] == 'ok')['price']['delta'] = -1
    expect(lambda: check_no_gain(forged, 'forged'), 'negative price', 'forged negative price')
    moved = copy.deepcopy(rd(EV / 'PRICES-base-tail.json')); moved[0]['ed']['insert'][2][0] += 1
    expect(lambda: check_binding(rd(EV / 'CENSUS-base-tail.json'), moved), 'exactly the census matches', 'priced edit absent from census')
    loose = copy.deepcopy(rd(EV / 'RETIME-base.json')); next(r for r in loose if r['status'] == 'ok')['max_gain_units_ceil'] = '1.000000'
    expect(lambda: check_bounds(loose, lambda r: r, 'forged', declared), 'above the declared bound', 'forged true-gain bound')
    print(json.dumps(dict(status='PASS_FRONTIER1305_KERNEL_CENSUS_NO_GAIN', tallies=out, controls_rejected=sorted(rejected)), indent=2))

if __name__ == '__main__':
    main()

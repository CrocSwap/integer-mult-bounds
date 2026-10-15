"""Independent owner-map and pricing check (adapted from the search session's checkmap.py).

Imports no code from this package's search or from the strict PR1087 verifier.
It uses three merged, separately authored checkers on the candidate data:
  * the seed67 owner auditor (research/t16-owner-audit-seed67, Josie Elliston,
    PR1091): rules R1-R7, X1, X2 and its 11 rejecting mutation controls;
  * the pinned exact moment/base-two/outer engines through
    research/frontier1094-idle-star-ceiling/analyze.py (pricing both suppliers,
    native and conservative surcharge);
  * the PR1069 independent pricing sweep (research/pending-claims-independent-pricing,
    Sagar Thakrar), fed with the strict replay's own complex/bit lowers.
"""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import argparse
import gzip
import hashlib
import importlib.util
import json
from decimal import Decimal
import sys

if not __debug__:
    raise RuntimeError('Assertions must remain enabled')
P = Path(__file__).resolve().parent
SELECTED_KAPPA = '0.001672660197076918'
INDICATIVE_CEILING_KAPPA = '0.001674088611862992'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read(p):
    p = Path(p)
    b = p.read_bytes()
    return json.loads(gzip.decompress(b) if p.suffix == '.gz' else b)


def run(main, replay, out_path):
    a = load('owners', main/'research/t16-owner-audit-seed67/verify.py')
    pins = read(main/'research/t16-owner-audit-seed67/SOURCES.json')['inputs']
    assert hashlib.sha256((main/a.TEMPLATE).read_bytes()).hexdigest() == pins['template_sha256']
    assert hashlib.sha256((main/a.PHASES).read_bytes()).hexdigest() == pins['data_phases_sha256']
    assert hashlib.sha256(gzip.decompress(a.WORD.read_bytes())).hexdigest() == pins['word_content_sha256']
    word = read(a.WORD)
    geo = a.geometry(read(main/a.TEMPLATE), read(main/a.PHASES))
    widths = a.word_widths(word)
    local = a.as_profile(word['report']['local_profile'])
    sel = main/'research/complex-t16-rare-pattern-exchanges/data'
    selplan, selroles = read(sel/'PLAN.json'), read(sel/'OWNERS.json.gz')
    span, callpos = a.windows(geo, [tuple(x) for x in selplan['order']])

    def idle_of(roles):
        used = Counter()
        for z in roles:
            used[z['owner_replica'], z['child'], z['port']] += z['width']
        idle = Counter()
        for (o, c) in span:
            for p in range(a.V):
                f = geo['rank'][c] - used[o, c, p]
                if f:
                    idle[f] += 1
        return idle

    def audit(roles, plan):
        idle = idle_of(roles)
        r = a.audit(geo, widths, local, roles, plan, idle, 16)
        r['controls'] = len(a.controls(geo, widths, local, roles, plan, idle, 16))
        return r

    st = load('idlestar', main/'research/frontier1094-idle-star-ceiling/analyze.py')
    st.ROOT = main
    st.ENGINE_ROOT = main/'research/complex-k492-owner-repair/vendor/multicold/engines'
    engines = tuple(st.load_engine(n) for n in ('moment', 'base_two_moment', 'outer'))
    baseline = json.loads((main/'research/community-frontier1094-audit/ASSEMBLY.json').read_text())

    def price(profile, bad=False):
        return st.price(Counter({int(k): v for k, v in profile.items()}), bad, baseline, engines)

    roles = read(P/'data/OWNERS.json.gz')
    plan, spec = read(P/'data/PLAN.json'), read(P/'data/SPEC.json')
    assert plan['order'] == selplan['order'] and plan['windows'] == selplan['windows']
    assert a.as_profile(spec['providers']['gauge44']['expected_profile']) == local
    assert Counter(widths) == a.as_profile(spec['providers']['gauge44']['inventory'])
    out = dict(spec_idle=spec['expected']['idle_remainder_profile'])
    old, new = audit(selroles, selplan), audit(roles, plan)
    assert new['profile'] == a.as_profile(plan['profile'])
    assert new['idle'] == {int(k): v for k, v in out['spec_idle'].items()}
    assert old['controls'] == new['controls'] == 11
    for tag, r in (('selected', old), ('candidate', new)):
        out[tag] = {k: r[k] for k in ('idle', 'profile', 'rank_mass', 'deficit', 'controls', 'cross_replica_roles')}
    diff = [i for i, (x, y) in enumerate(zip(selroles, roles)) if x != y]
    key = lambda z: (z['owner_replica'], z['child'], z['port'])
    moved = [i for i in diff if key(selroles[i]) != key(roles[i])]
    for i in diff:
        assert all(selroles[i][k] == roles[i][k] for k in ('stage', 'replica', 'time', 'helper', 'width'))
    out.update(changed_rows=len(diff), relocated_rows=moved, offset_only_rows=len(diff)-len(moved))
    assert len(roles) == len(selroles)
    out['all_strictly_inside'] = all(span[z['owner_replica'], z['child']][0] < callpos[z['stage'], z['replica']]
                                     < span[z['owner_replica'], z['child']][1] for z in roles)
    per = Counter((z['stage'], z['replica'], z['helper']) for z in roles)
    out['helper_once_per_call'] = set(per.values()) == {1} and len(per) == 144*len(widths)
    assert out['all_strictly_inside'] and out['helper_once_per_call']

    # Majorization of the idle residual vectors (sorted descending, padded with zeros to the
    # common bin count): equal totals, and every partial sum of the candidate vector is at
    # least the selected one's, strictly somewhere. Karamata then gives a strict decrease of
    # sum H(r) for every strictly concave H (PROOF.md); the exact engines below give the value.
    nbins = len(span)*a.V
    def residuals(idle):
        v = sorted((r for r, n in idle.items() for _ in range(n)), reverse=True)
        assert len(v) <= nbins
        return v+[0]*(nbins-len(v))
    vn, vo = residuals(new['idle']), residuals(old['idle'])
    assert sum(vn) == sum(vo)
    sn = so = 0
    dominated, strict = True, False
    for x, y in zip(vn, vo):
        sn += x
        so += y
        dominated &= sn >= so
        strict |= sn > so
    assert dominated and strict, 'candidate idle vector does not strictly majorize the selected one'
    out['majorization'] = dict(residual_total=sum(vn), bins=nbins, candidate_majorizes_selected=True, strict=True)

    ps, pn, pc = price(old['profile']), price(new['profile']), price(new['profile'], True)
    out.update(price_selected=ps, price_new=pn, price_new_conservative=pc)
    assert Decimal(ps['kappa_decimal']) == Decimal(SELECTED_KAPPA)
    assert pn['kappa'] == spec['expected']['kappa'] and pn['endpoint'] == spec['expected']['complex_lower']
    # Compare kappa decimals as Decimal, never as strings: the native assembler drops trailing zeros.
    assert Decimal(pc['kappa_decimal']) == Decimal(spec['expected']['conservative_kappa_decimal'])
    out['rel_gain'] = str((Q(pn['kappa'])-Q(ps['kappa']))/Q(ps['kappa']))
    # Indicative only (PROOF.md, "A proved packing ceiling"): price the idle multiset that attains the proved surrogate
    # bound {1: 2431, 17: 1, 48: 4887} in place of the selected idle remainders. This is not a kappa bound.
    ceiling_idle = Counter({1: 2431, 17: 1, 48: 4887})
    base = Counter(a.as_profile(selplan['profile']))
    base.subtract(old['idle'])
    ceiling_profile = +(base+ceiling_idle)
    assert sum(r*n for r, n in ceiling_profile.items()) == 1041408
    pi = price(ceiling_profile)
    assert Decimal(pi['kappa_decimal']) == Decimal(INDICATIVE_CEILING_KAPPA)
    out['indicative_ceiling_price'] = dict(idle={str(k): v for k, v in sorted(ceiling_idle.items())},
                                           kappa_decimal=pi['kappa_decimal'], complex_lower=pi['endpoint'])

    if replay is not None:
        rep = json.loads((replay/'REPLAY.json').read_text())
        assert rep['status'] == 'PASS_GAUGE44_T16_STRICT_GLOBAL_REPLAY'
        assert a.as_profile(rep['complex_profile']) == new['profile']
        assert rep['kappa'] == pn['kappa'] and rep['complex_lower'] == pn['endpoint']
        sys.path.insert(0, str(main/'research/pending-claims-independent-pricing'))
        sweep = load('pricing', main/'research/pending-claims-independent-pricing/sweep.py')
        claim = dict(pr=0, head='x', profile=new['profile'], live=14336, calls=144, complex_lower=rep['complex_lower'],
                     record_kappa=rep['kappa'], claimed_kappa_decimal=rep['kappa_decimal'], bit_lower=rep['bit_lower'])
        swept = sweep.price(claim)
        keys = ('endpoint_certified', 'deficit_equals_W_minus_64N', 'halving', 'record_bit_is_pr589',
                'kappa_equals_record', 'kappa_equals_title', 'kappa_exact_decimal', 'binding')
        out['sweep'] = {k: swept.get(k) for k in keys}
        assert all(out['sweep'][k] is True for k in keys[:6])
        assert Decimal(out['sweep']['kappa_exact_decimal']) == Decimal(spec['expected']['kappa_decimal']) and out['sweep']['binding'] == 'complex'
    if out_path is not None:
        out_path.write_text(json.dumps(out, indent=1, default=str)+'\n')
    print('PASS_INDEPENDENT_OWNER_AND_PRICING_CHECK', pn['kappa_decimal'], dict(sorted(new['idle'].items())),
          'controls', new['controls'], 'sweep', replay is not None)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--main', type=Path, default=P.parents[1])
    ap.add_argument('--replay', type=Path, help='strict replay work dir containing REPLAY.json (enables the PR1069 sweep)')
    ap.add_argument('--out', type=Path)
    args = ap.parse_args()
    run(args.main.resolve(), args.replay and args.replay.resolve(), args.out)

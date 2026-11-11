"""Authenticate #7334 readbacks and independently direct its signed invoice."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha1, sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path

HEAD = 'aaeec8c0acf01e99a5f331ef363a698d9c084ace'
PARENT = '9d0119eb12fbd9fa534b48cd37b68e7099757b91'
CALLER = '07a76c5e2738882c0cb322278e56f6cae3c9885d'
CALLER_SHA = '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc'
BLOBS = {
    'EARLY-RESULT.json':'675d6cf2374f3384019dfd53b2bdffd845005f13',
    'NATIVE-RESULT.json':'eb101307d4d0399efed96d88cf6d4c01ec9c7369',
    'RESULT.json':'3034a490f5b0656ae71495c99493c4ab1ac1f5c6',
    'PROPOSED-CLAIM.json':'6b491894580741e3e2c11a453722a0302db7b5d6',
    'PROOF.md':'7644e5571d583183ee93b686612b5ec4555f6911',
    'INPUTS.json':'95c53f4594287a72d9b586f10ee136d0a1686984',
    'REFERENCE.json':'8859e243cc39546bcb1e257d95c19a658c455dc7',
    'VERIFY.json':'cc98ee2a5c5a79e670094a6f55c7cacda8fd330c',
    'construct.py':'89e923bd738dfc404ca76b7ae36f13844ac4bfbb',
    'REPLAY.txt':'0b8d8048c18740060f4b7f6d380a5f3a0f30ee53',
    'SOURCES.json':'6b97e903a6df8de437068a0e2907823885928053',
    'README.md':'b3a055f4e0d334ce2e7df3310caaa0849eb3eba1',
}
DEPENDENCIES = {
    'dependencies/7314/RESULT.json':'432191ca572c9221935787ebe392699e3a1ef4512b0bf4fbc704657321cc87ca',
    'dependencies/7314/NATIVE-RESULT.json':'336f463da5afe5b60bfd3b9f0ce8aeea5a5feb1f854613bf4218ba0b28b3371b',
    'dependencies/7314/PROPOSED-CLAIM.json':'41a08c4b7d0b2de4af22bc778948a143027eb3065fff47b0400b6ded1cc52778',
    'dependencies/7298/pricing.py':'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182',
    'dependencies/round65/price.json':'25205ad2cf4230bd2b2b704eec9f96ec4a5486fd575b5599861b28ffdd15b00b',
}


def unique(items):
    result = dict(items)
    if len(result) != len(items):
        raise ValueError('duplicate JSON key')
    return result


def parse(raw):
    return loads(raw, object_pairs_hook=unique)


def hist(row):
    return Counter({int(rank): n for rank,n in row.items()})


def checked_receipts():
    receipts, pins = {}, {}
    for filename, expected in BLOBS.items():
        path = f'receipts/{filename}'
        raw = Path(path).read_bytes()
        actual = sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        if actual != expected:
            raise ValueError(f'changed Git blob {path}')
        receipts[filename] = raw
        pins[path] = {'git_blob':expected, 'sha256':sha256(raw).hexdigest()}
    replay = receipts['REPLAY.txt'].decode()
    for filename in ('EARLY-RESULT.json','NATIVE-RESULT.json','RESULT.json','PROPOSED-CLAIM.json'):
        assert f"{pins[f'receipts/{filename}']['sha256']}  {filename}" in replay
    dependencies = {}
    for path, digest in DEPENDENCIES.items():
        raw = Path(path).read_bytes()
        if sha256(raw).hexdigest() != digest:
            raise ValueError(f'changed dependency {path}')
        assert path not in pins
        dependencies[path] = raw
        pins[path] = {'sha256':digest}
    return receipts, dependencies, pins


def main():
    assert __debug__
    receipts, deps, pins = checked_receipts()
    early,native,signed,proposed,ref,source = (parse(receipts[name]) for name in (
        'EARLY-RESULT.json','NATIVE-RESULT.json','RESULT.json','PROPOSED-CLAIM.json','REFERENCE.json','INPUTS.json'))
    old,old_native,old_claim,prior = (parse(deps[path]) for path in (
        'dependencies/7314/RESULT.json','dependencies/7314/NATIVE-RESULT.json',
        'dependencies/7314/PROPOSED-CLAIM.json','dependencies/round65/price.json'))
    assert source['source_head'] == ref['source_head'] == native['source_head'] == prior['head'] == PARENT
    assert ref['signed_caller_head'] == CALLER and signed['caller_sha256'] == old['caller_sha256'] == CALLER_SHA
    assert ref['source_word_sha256'] == old_native['word_canonical_sha256']
    assert early['word_sha256'] == native['word_canonical_sha256']
    claim, incumbent = Q(proposed['kappa']), Q(old_claim['kappa'])
    assert claim == Q(signed['claim']) == Q(early['gate']['claim']) == Q('0.00364665195644')
    assert incumbent == Q(ref['comparison']) == Q(prior['claim']) == Q('0.003646221436446')
    assert proposed['assumptions'] == old_claim['assumptions'] and len(proposed['assumptions']) == 5
    assert all(x['id'] in {'native_all_columns','owned_erasure','compiler','precision_tape','analytic_recovery'} for x in proposed['assumptions'])
    checks = signed['checks']
    application = checks['ODD-8X9-APPLICATION-CHECKS.json']
    gate = checks['ODD-ADMISSION-PARTIAL.json']['compiler_outer']
    assert gate == signed['price']['gate'] == early['gate'] == application['numeric_gate']
    assert gate['outer']['strict_count'] == 54 and gate['outer']['functional_count'] == 4
    assert sum(row['checked_maps'] for row in signed['catalogue']) == 3037
    assert sum(row['main_boundary_pairs'] for row in signed['catalogue']) == 104
    assert all(row['phase_control_rejected'] for row in signed['catalogue'])
    assert all(native['controls'].values()) and not native['native']['bad_inputs']
    P,T = (hist(early['invoice'][key]) for key in ('P','T'))
    P0,T0 = (hist(old['price']['after'][key]) for key in ('P','T'))
    for row in (signed['price']['after'],checks['ODD-ADMISSION-PARTIAL.json']['invoice']):
        assert hist(row['P']) == P and hist(row['T']) == T
        assert row['S'] == 1424 and row['empty_root_credits'] == 0
    assert P == hist(prior['new_paid']) and P0 == hist(prior['old_paid'])
    assert T == T0 == hist(prior['productive'])
    delta = P.copy(); delta.subtract(P0)
    assert {r:n for r,n in delta.items() if n} == {1:-17,5:-17,6:17}
    assert sum(P.values()) == 110519 and sum(T.values()) == 22461
    assert application['physical_binding']['native_calls'] == 17
    assert application['physical_binding']['paid_positions'] == 110519
    old_net,net = T0.copy(),T.copy()
    old_net.subtract(P0); net.subtract(P)
    assert sum(r*n for r,n in net.items()) == sum(r*n for r,n in old_net.items()) == 1424
    cost = run_path('dependencies/7298/pricing.py')['cost']
    lo,hi = map(Q,early['price']['independent_raw_bracket'])
    old_upper = Q(prior['crossing_upper'])
    tested = Q(gate['tested'])
    new_at_claim,old_at_claim = cost(net,claim),cost(old_net,claim)
    new_at_old,old_at_old = cost(net,old_upper),cost(old_net,old_upper)
    new_at_tested,new_at_lower,new_at_upper = (cost(net,k) for k in (tested,lo,hi))
    assert old_upper < claim < tested < lo < hi
    assert old_at_claim[1] < 0 < new_at_claim[0] and old_at_old[1] < 0 < new_at_old[0]
    assert new_at_tested[0] > 0 and new_at_lower[0] > 0 > new_at_upper[1]
    assert list(map(str,new_at_old)) == prior['complete_new_margin_at_old_crossing_upper']
    assert Q(early['price']['gain_exact']) == claim-incumbent
    bit = Q(proposed['complex_BIT_premise']); admitted_bit = Q(proposed['admitted_BIT_saving'])
    assert claim < bit < admitted_bit and bit == Q(gate['BIT_pin']) == Q(prior['bit_bound'])
    assert Q(gate['BIT_margin']) == bit-tested
    outer_min = min(map(Q,proposed['nine_outer_savings'].values()))
    assert outer_min == Q(proposed['limiting_outer_saving']) and outer_min-claim == Q(proposed['strict_limiting_slack']) > 0
    ordinary = checks['ODD-ADMISSION-PARTIAL.json']['ordinary']['conservative_total']
    old_ordinary = old['checks']['ODD-ADMISSION-PARTIAL.json']['ordinary']['conservative_total']
    precision = checks['ODD-PRECISION.json']['context_c']
    assert (ordinary,old_ordinary,precision) == (782715464,782663376,2430)
    assert precision == old['checks']['ODD-PRECISION.json']['context_c']
    assert native['derived_grid']['odd_scale'] == 1125 and native['derived_grid']['fractional_bits'] == 25
    bounds = {key:list(map(str,pair)) for key,pair in (
        ('new_at_claim',new_at_claim),('old_at_claim',old_at_claim),('new_at_tested',new_at_tested),
        ('new_at_old_crossing_upper',new_at_old),('old_at_old_crossing_upper',old_at_old),
        ('new_at_raw_lower',new_at_lower),('new_at_raw_upper',new_at_upper))}
    doc = {'head':HEAD,'parent':PARENT,'caller_head':CALLER,'claim':str(claim),'incumbent':str(incumbent),
           'exact_gain':str(claim-incumbent),'exact_relative_percent':str(100*(claim-incumbent)/incumbent),
           'new_raw_interval':list(map(str,(lo,hi))),'old_raw_upper':str(old_upper),
           'raw_strict_separation':str(lo-old_upper),'tested':str(tested),'directed_bounds':bounds,
           'paid':dict(P),'targets':dict(T),'copies':17,'paid_delta':{r:n for r,n in delta.items() if n},
           'paid_positions':110519,'productive_fields':22461,'rank_surplus':1424,'empty_root_credits':0,
           'bit_premise':str(bit),'bit_claim_headroom':str(bit-claim),'bit_admitted':str(admitted_bit),
           'ordinary':ordinary,'ordinary_delta':ordinary-old_ordinary,'ordinary_headroom':10**9-ordinary,
           'context_c':precision,'context_headroom':4096-precision,'native_grid':[1125,25],
           'native_ingredient_claim':native['gate']['claim'],'physical_maps':3037,'main_boundaries':104,
           'outer_strict':54,'outer_functional':4,'outer_strict_slack':str(outer_min-claim),
           'owned_lifetimes':native['native']['lifetimes'],'owned_peak':native['native']['owned_peak'],
           'assumptions':[x['id'] for x in proposed['assumptions']],'source_archive_sha256':source['archive_sha256'],
           'path_pins':pins,'scope':'Exact receipt and directed-price readback. No native or caller execution in this audit.'}
    print(dumps(doc,indent=2,sort_keys=True))


if __name__ == '__main__':
    main()

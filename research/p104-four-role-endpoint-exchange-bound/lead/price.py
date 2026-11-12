"""Predecode paid, source-unit and fixed-tape reservation for a four-role basis."""
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps,loads
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PINS={
 'inputs/R148-PRICE.json':'8b71d05eddb3aee641ffa41a57a3922292bc4d45c5eb8aae8f2e4514388f6524',
 'inputs/R143-GEOMETRY.json':'f2aa238ed8c49f0633c3837c6961bfba19482385851a5606578fa6368db79542',
 'inputs/7334-CALLER-RESULT.json':'7f2d587c59f063b01f1e8b320084a7f0943f2f05d65e3e0f5e80448c6c8e8194',
 'inputs/7113-independent.py':'21f46a8340331abb1486b50bd4e04453f1968b0a5950d86ff7780dd368590874',
 'inputs/7113-fixed-tape.py':'e6246e9f8fbeae3077d82e585eafd3647c1a8758c58f33c7c13e7efa6c1e42bb',
 'inputs/7334-WORD.json.gz':'4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a',
}


def unique(items):
    d=dict(items)
    assert len(d)==len(items)
    return d


def raw(path):
    b=(ROOT/path).read_bytes()
    assert sha256(b).hexdigest()==PINS[path],path
    return b


def doc(path):
    return loads(raw(path),object_pairs_hook=unique)


def main():
    assert __debug__
    previous=doc('inputs/R148-PRICE.json')
    geometry=doc('inputs/R143-GEOMETRY.json')
    admission=doc('inputs/7334-CALLER-RESULT.json')
    assert previous['head']==geometry['head']=='aaeec8c0acf01e99a5f331ef363a698d9c084ace'
    assert previous['caller']==geometry['caller']=='07a76c5e2738882c0cb322278e56f6cae3c9885d'
    assert previous['ranges']==geometry['ranges'] and geometry['raw_cuts']==20455
    assert previous['paid_delta']=={} and previous['productive_delta']=={'5':-17,'6':17,'8':17,'9':-17}
    assert Q(previous['quote']['probe']['complete_one_margin'][0])>0
    assert Q(previous['quote']['old_crossing_upper']['complete_one_margin_with_extra_rank_one'][1])<0
    ordinary=raw('inputs/7113-independent.py')
    tape_source=raw('inputs/7113-fixed-tape.py')
    assert b'scalar+=4*(a.bit_length()+d.bit_length()+1+(a.bit_count()' in ordinary
    assert b'scalar_services=32*' in tape_source and b'scalar_services*2**20' in tape_source
    assert b'records_per_map=4*(b["ambient"]+1)**2' in tape_source

    partial=admission['checks']['ODD-ADMISSION-PARTIAL.json']
    tape=admission['checks']['ODD-FIXED-TAPE-COUNTS.json']
    assert (sum(partial['invoice']['P'].values()),sum(partial['invoice']['T'].values()),partial['invoice']['S'])==(110519,22461,1424)
    assert tape['native_invocations']==17 and tape['max_scalar_numerator_bits']==24
    assert tape['native_sha256']=='9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac'
    assert partial['ordinary']['conservative_total']==previous['ordinary_baseline']==782715464
    assert tape['context_c']==previous['context_c']==2430
    assert tape['monomial_map_slots']==298808
    den=1125*2**25
    den_bits=den.bit_length()
    add,scale=4*(24+den_bits+1+24),4*(24+den_bits+1)
    assert (add,scale)==(340,244)
    # One rank-one basis recipe uses <=12 ADD and <=4 SCALE. Reserve a
    # second such recipe for return work if the exact normalized identity allows it.
    adds,scales,wraps=24,8,4
    native=17
    charged=native*(adds*add+scales*scale+1000*wraps)
    ordinary_upper=partial['ordinary']['conservative_total']+charged
    assert ordinary_upper<10**9
    macro_delta=native*(adds+scales)
    service_delta=32*macro_delta
    map_delta=native*wraps
    map_upper=tape['monomial_map_slots']+map_delta
    print(dumps({'head':previous['head'],'caller':previous['caller'],'pins':PINS,'quote':previous['quote'],
      'ranges':geometry['ranges'],'raw_cuts':geometry['raw_cuts'],'additional_roles':[1454,1251],
      'paid':110519,'productive':22461,'surplus':1424,'extra_paid':0,'compatible_edit_cap':1,
      'ordinary':{'max_adds_per_native':adds,'max_scales_per_native':scales,'reserved_monomial_maps_per_native':wraps,
        'coefficient_denominator_divides':den,'numerator_bits':24,'add_unit_upper':add,'scale_unit_upper':scale,
        'charged_source_units':charged,'complete_upper':ordinary_upper,'headroom':10**9-ordinary_upper},
      'tape':{'scalar_macro_delta':macro_delta,'scalar_services_delta':service_delta,
        'scalar_services_upper':tape['scalar_services_upper']+service_delta,
        'scalar_steps_coefficient_upper':tape['scalar_steps_coefficient']+service_delta*2**20,
        'monomial_map_slots_upper':map_upper,'elementary_records_upper':map_upper*tape['elementary_records_per_map_upper'],
        'baseline_context_c':tape['context_c'],'context_cap':4096,'native_grid_baseline':[1125,25],
        'condition':'Recompute actual grid, context, complete tape and all physical wrappers before any candidate. Scope retains owned and external lanes.'},
      'caps':{'events':76466,'ranges':20,'raw_cuts':20455,'geometry_seconds':20,
        'prefix_keys':8,'prefix_seconds':25,'suffix_keys':4,'suffix_seconds':35}},indent=2,sort_keys=True))


if __name__=='__main__':
    main()

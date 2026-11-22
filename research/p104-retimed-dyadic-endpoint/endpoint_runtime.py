#!/usr/bin/env python3
"""Bounded source-bound probe of a new-coupling seven-stage candidate.

Only restored461/installations.py changes: it sets the required binary trial.
No production-dimensional binary rank or calendar is allocated.
"""

from fractions import Fraction as Q
from hashlib import sha1, sha256
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import json
import sys

ROOT = Path(sys.argv[1]).resolve()
MACHINE = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(MACHINE))
sys.path.insert(1, str(ROOT))


def gitblob(path):
    content = path.read_bytes()
    return sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()


def main():
    expected = {
        'activation.py': '20525c7fa39de6300e0a01b1e0155dbc324d6940',
        'installations.py': '4feaf4ce771646cf363791b4770609f1da773140',
        'transport.py': '7006360e5b9a117a64ba77a215339ea8242a8ba3',
        'retimed_supplier.py': '388b2cf6591d979ffc29bd3a187d35a3cc72f4cc',
        'raw_binary_stage.py': '444da9677aed25cc881312435d825fb5b6312f0c',
        'check_complete.py': '3c13191ead65cfdb3c0c75e4958f5d6853939fba',
        'machine.patch': '16b6205d1f2da87e643159add52146a4e3475211',
        'receiver.patch': '4b7db79b29b83e17e49faa981a0b7a4c4ea21a11',
        'five_exchange.py': 'dbbba0ba77fc7d4ce9fc82d63e6cf9a0bd3c1b24',
    }
    assert {name: gitblob(ROOT/name) for name in expected} == expected
    for name in ('transport.py', 'retimed_supplier.py', 'raw_binary_stage.py', 'five_exchange.py'):
        assert (MACHINE/name).read_bytes() == (ROOT/name).read_bytes()
    old = (ROOT/'installations.py').read_text()
    replace_old = 'BINARY_C = Q(4484997569314581, 2**60)'
    replace_new = 'BINARY_C = Q(287039844436133239, 2**66)'
    assert old.count(replace_old) == 1
    expected_text=old.replace(replace_old,replace_new)
    assert (MACHINE/'installations.py').read_text().startswith(expected_text)
    assert 'PROFILES["dyadic-endpoint"] = DYADIC_ENDPOINT' in (MACHINE/'installations.py').read_text()
    assert sha256((ROOT/'outer_budget.py').read_bytes()).hexdigest() == 'ca4438db28a447ed5c43d87d43f0ac10a0cb2b4e183342ac93139d517b9d4d02'

    from upstream import install
    install()
    from installations import DYADIC_ENDPOINT, PROFILES, BINARY_C
    from activation import resource_receipt
    from check_complete import profile_row, first_external_swap
    from unpowered_price import ranks
    from ordinary_carrier import stage_for_width_log, ternary
    from raw_binary_stage import binary_recipe
    import five_exchange
    import receiver
    import direct_body

    profile = PROFILES['dyadic-endpoint']
    assert profile is DYADIC_ENDPOINT
    assert BINARY_C == Q(287039844436133239,2**66)
    assert Q(4484997569314581,2**60) < profile.kappa
    stock = resource_receipt(profile)
    row = profile_row(profile)
    cuts = stock['binary_cuts']
    assert stock['retimed_all_size_margin_floor'] > 1024
    for i, (h, cut) in enumerate(zip(profile.rank_logs, cuts), 1):
        assert stage_for_width_log(cut-1,7,profile.rank_logs) == i-1
        assert stage_for_width_log(cut,7,profile.rank_logs) == i
        assert stage_for_width_log(cut,i-1,profile.rank_logs) == i-1
        assert 249*cut >= 250*(h+64)
        if i > 1:
            assert cuts[i-2]+2 < h
        class FakeDigits:
            def __lt__(self, n): return False
            def bit_length(self): return cut+1
        with patch('ordinary_carrier.stage_body') as body:
            ternary(None,None,FakeDigits(),1,1,1,maximum=7,profile=profile)
            assert body.call_args.args[6] == i
            assert body.call_args.args[7] is profile
    assert receiver.same_order_line is five_exchange.same_order_line
    assert direct_body.direct_line is five_exchange.direct_line
    print('PASS_461_PRICING_AND_TRUE_SEVEN_SELECTOR_BOUNDARIES', flush=True)

    recipes = [binary_recipe(h) for h in profile.rank_logs]
    assert all(recipe.rank_log == h and recipe.width_log == 92*h
               for recipe,h in zip(recipes,profile.rank_logs,strict=True))
    assert all(recipe.trial == BINARY_C for recipe in recipes)
    print('PASS_461_ACTUAL_BINARY_COUPLING_AND_SEVEN_RECIPES', flush=True)

    census = ranks()
    assert sum(census[0].values()) == 105216
    assert sum(census[1].values()) == 564144
    import check_complete
    with patch.object(check_complete, 'PROFILES', {'candidate': profile}):
        crossing = first_external_swap(census)
    assert crossing['placements']['36000']['period'] == 1620
    assert crossing['placements']['36000']['first_tickets'] == [0,324,648]
    print('PASS_461_PRODUCTION_RANK_FIRST_PHYSICAL_ALIGNMENT_GUARD', flush=True)

    from retimed_supplier import Positive
    supplier = Positive(profile.complex_log, profile.positive_stop_denominator)
    assert supplier.carrier.bit_length() - 1 == 36000
    assert supplier.denominator == 10**21
    assert supplier.recipe.rank_log == 36000 and supplier.recipe.width_log == 92*36000
    assert len(supplier.recipe.targets) == 105216 and len(supplier.recipe.paid) == 564144
    assert len(supplier.recipe.cells) == 54
    import positive_dispatch
    m = supplier.carrier
    # A fresh source call checks the true rank boundary. The payload is deliberately mocked.
    class DummyPositive:
        def __init__(self,*args,**kwargs): pass
        def hadamard(self,*args,**kwargs): pass
    with patch.object(positive_dispatch,'Positive',DummyPositive), \
         patch.object(positive_dispatch,'place_and_apply') as placement:
        positive_dispatch.native_h(None,0,m,1792,0,1,None,36000,lambda:supplier)
        assert not placement.called
        positive_dispatch.native_h(None,0,m+1,1792,0,1,None,36000,lambda:supplier)
        assert placement.call_count == 1 and placement.call_args.args[-1] is supplier
    print('PASS_461_ACTUAL_POSITIVE_RECIPE_AND_DISPATCH_BOUNDARY', flush=True)

    previous = Q()
    for i,h in enumerate(profile.rank_logs):
        limit = min(profile.eta,(249*(BINARY_C-Q(11,8*h))+previous)/250)
        booked = profile.ordinary if i==6 else Q((limit*10**21).__floor__()-1,10**21)
        assert str(booked) == row['stage_rates'][i] and previous < booked < limit
        previous = booked
    final_limit_margin = limit-booked
    assert final_limit_margin == Q(27007124810227343,1759218604441600000000000000000000000)
    assert row['signed_gate']['smallest_margin'] == '1/10000000000000000000000'
    result = {'e264_git_blobs': expected, 'source_mutation': 'BINARY_C and an installed named profile in installations.py',
              'candidate': {'kappa': str(profile.kappa), 'gap': '1/1000000000000000000000',
                            'binary_C': str(BINARY_C),
                            'binary_H': list(profile.rank_logs), 'numerical_H':profile.complex_log},
              'arithmetic_and_stock': row, 'binary_recipe_count':len(recipes),
              'positive_word': {'target_count':sum(census[0].values()), 'paid_count':sum(census[1].values()),
                                'cells':len(supplier.recipe.cells), 'first_crossing':crossing},
              'last_rate_margin':str(final_limit_margin),
              'scope':'feasible source-bound controls and exact arithmetic; no production payload or all-size proof'}
    Path(sys.argv[3]).write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('PASS_461_SOURCE_OVERLAY_FINITE_GUARDS_ONLY',flush=True)


if __name__ == '__main__':
    main()

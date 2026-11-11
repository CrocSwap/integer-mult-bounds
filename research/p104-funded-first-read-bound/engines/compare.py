"""Reconcile both first-read censuses and price the two terminal coincidences."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path

STATUS = {
    'excluded_helper':'protected_h',
    'first_contact_not_source_add':'first_not_add_source',
    'helper_next_not_move':'helper_next_not_move',
    'nonunit_or_no_positive_residual':'not_rank_one_ascent',
    'partner_next_not_move':'partner_next_not_move',
    'partner_not_unprotected_productive_helper':'partner_not_public_productive',
    'zero_residual_after_rank_one':'zero_residual_rank',
}
TARIFF_SHA = 'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182'


def compare(root):
    def read(name):
        return loads((root/name).read_bytes())
    p,a,b = read('PRICE.json'),read('CONTACT.json'),read('independent/RESULT.json')
    pin = sha256((root/'PRICE.json').read_bytes()).hexdigest()
    assert p['head'] == a['head'] == b['head']
    assert a['price_sha256'] == b['price_sha256'] == pin
    assert a['events'] == b['visited_events'] == 76461
    assert not any((a['survivors'],b['survivors'],a['unvisited'],b['unvisited_roles']))
    lead = {r['h']:r for r in a['rows']}
    exact = {r['h']:r for r in b['records']}
    assert set(lead) == set(exact) and len(lead) == len(a['rows']) == len(b['records']) == 1101
    full = []
    for h,x in lead.items():
        y = exact[h]
        assert STATUS[x['status']] == y['status'] and x['rank'] == y['rank']
        for primary,independent in [('g','g'),('add','first'),('start','initial'),('end','final'),
                                    ('h_next','next_h'),('g_next','next_g'),
                                    ('lift','helper_destination'),('partner_lift','partner_destination')]:
            if primary in x:
                assert x[primary] == y[independent]
        if x['status'] == 'nonunit_or_no_positive_residual':
            assert x['lift'] == x['partner_lift'] == x['end']
            full.append(x)
    assert len(full) == 2
    assert sorted(x['rank'] for x in full) == [2,5]
    tariff = root/'inputs/7298/pricing.py'
    assert sha256(tariff.read_bytes()).hexdigest() == TARIFF_SHA
    cost = run_path(str(tariff))['cost']
    k = Fraction(p['crossing_upper'])
    stock = []
    for x in full:
        d = x['rank']
        parts = []
        for r in range(1,d):
            # Split the partner ascent; both roles still transport the
            # residual. The helper's productive residual cancels its bill.
            delta = Counter({d:17})
            delta[r] -= 17
            delta[d-r] -= 17
            credit = cost(delta,k)
            assert credit[1] < 0
            parts.append({'prefix_rank':r,'residual_rank':d-r,
                          'credit':list(map(str,credit))})
        stock.append({'h':x['h'],'g':x['g'],'add':x['add'],'final':x['end'],
                      'ascent_rank':d,'proper_split_price_only':parts,
                      'full_lift_deletion_signed_delta_if_legal':0})
    return {'head':p['head'],'price_sha256':pin,'matched_helpers':len(lead),
            'scope_exhausted':True,'remaining':0,'compatible_saving_upper':0,
            'terminal_coincidences':stock,
            'partial_scope':'split partner paid ascent, keep both residual paid children, no other changes'}


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('root',type=Path)
    args = parser.parse_args()
    print(dumps(compare(args.root),sort_keys=True,indent=2))

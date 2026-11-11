"""Compare the exact A2 stock and preserve public-middle diagnostics."""
from argparse import ArgumentParser
from hashlib import sha256
from json import dumps, loads
from pathlib import Path


def main(root):
    def read(path):
        return loads((root/path).read_bytes())
    p = read('PRICE.json')
    s = read('SUPPORT.json')
    g = read('independent/run/GEOMETRY.json')
    b = read('independent/run/RESULT.json')
    price_pin = sha256((root/'PRICE.json').read_bytes()).hexdigest()
    geometry_pin = sha256((root/'independent/run/GEOMETRY.json').read_bytes()).hexdigest()
    assert p['head'] == s['head'] == g['head'] == b['head']
    assert s['price_sha256'] == g['primary_price_sha256'] == price_pin
    assert b['geometry_sha256'] == geometry_pin
    assert p['stock']['complete'] and p['stock']['visited'] == 76461
    assert p['stock']['native_paid'] == g['old_native_paid_histogram']
    assert b['scope_exhausted'] and s['unresolved'] == 0
    assert not any((p['unvisited_keys'],b['unresolved'],p['rows'],s['survivors'],b['surviving']))
    assert g['structural_count'] == g['geometry_checked'] == 0
    a, z = p['stock']['counts'],g['structural_filter_counts']
    for first,second in [('consecutive_add_triples','all_add_triples'),('cross_chart_triples','cross_chart'),
                         ('directed_triangle_any_middle','directed_triangles'),('three_role_cross_chart_triples','exactly_three_roles')]:
        assert a[first] == z[second]
    diagnostics = []
    for row in g['excluded_public_middle_diagnostics']:
        assert not row['geometry']['legal'] and row['geometry']['invalid_edges']
        diagnostics.append({'clocks':row['clocks'],'middle':row['middle'],
                            'illegal_edges':row['geometry']['invalid_edges']})
    assert len(diagnostics) == 2
    return {'head':p['head'],'price_sha256':price_pin,'independent_geometry_sha256':geometry_pin,
            'counts':a,'owned_middle_keys':0,'public_middle_diagnostics':diagnostics,
            'compatible_saving_upper':0,'unresolved':0}


if __name__ == '__main__':
    p=ArgumentParser(description=__doc__)
    p.add_argument('root',type=Path)
    a=p.parse_args()
    print(dumps(main(a.root),sort_keys=True,indent=2))

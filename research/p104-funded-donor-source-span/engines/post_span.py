"""Bounded post-bank exterior-minor test for the #7314 donor fusion."""

from argparse import ArgumentParser
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from math import gcd, isqrt
from pathlib import Path
from runpy import run_path
from time import monotonic

ADAPTER_SHA = '0ceee0b3248671d97d54b49d8782ac0598ad99c740a64a4b72db0ff0b580ce45'
PRICE = '25205ad2cf4230bd2b2b704eec9f96ec4a5486fd575b5599861b28ffdd15b00b'
FIRST = '8191afd3f089c48806eed17565c7801ed9d5fe84a4dca0f0bb57e9905c19b5f2'
P = 65521
TARGET = 863


def checked(path, digest):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != digest:
        raise ValueError(f'Changed input {path.name}')
    return raw


def primitive(terms):
    items = sorted(terms.items())
    scale = gcd(*(n for _,n in items))
    if items[0][1] < 0:
        scale = -scale
    return tuple((i,n//scale) for i,n in items)


def exterior_minor(rows, check_time, deadline):
    basis, pivots, determinant = {}, [], 1
    for role, entries in rows:
        check_time(deadline)
        row = {k: n % P for k,n in entries if k != TARGET and n % P}
        while row:
            pivot = min(row)
            coefficient = row[pivot]
            if pivot not in basis:
                inverse = pow(coefficient, -1, P)
                basis[pivot] = {k:v*inverse % P for k,v in row.items()}
                pivots.append([role,pivot,coefficient])
                determinant = determinant*coefficient % P
                break
            for key, val in basis[pivot].items():
                new = (row.get(key,0) - coefficient*val) % P
                if new:
                    row[key] = new
                else:
                    row.pop(key,None)
    assert determinant and len(basis) == len(pivots)
    return pivots, determinant


def assess(rows, check_time, deadline, legal_add):
    assert all(denominator % P for denominator,_ in rows.values())
    target_rows = [role for role, (_,row) in rows.items() if TARGET in row]
    if not target_rows:
        return {'disposition':'exact_coordinate_dual', 'dual':{str(TARGET):'1'},
                'dual_target_value':'1','roles_with_x863':[]}
    for role in target_rows:
        denominator, row = rows[role]
        if len(row) == 1:
            coeff = Fraction(-2*denominator,row[TARGET])
            if legal_add(coeff):
                return {'disposition':'exact_legal_adds','roles_with_x863':target_rows,
                        'literal_adds':[['ADD',1355,role,str(coeff),127]]}
    representative = {}
    for role, (_,row) in rows.items():
        if row:
            representative.setdefault(primitive(row),role)
    reps = sorted((role,entries) for entries,role in representative.items())
    pivots, determinant = exterior_minor(reps, check_time, deadline)
    full = len(pivots) == len(reps)
    return {'disposition':'certified_full_exterior_minor' if full else 'unresolved_rank_deficiency',
            'roles_with_x863':target_rows, 'nonzero_rows':sum(bool(row) for _,row in rows.values()),
            'rational_span_preserving_representatives':[r for r,_ in reps],
            'exterior_rank_lower':len(pivots), 'exterior_minor_pivots':pivots,
            'exterior_minor_determinant_mod_prime':determinant, 'prime':P}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('root',type=Path)
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args()
    if not __debug__:
        parser.error('Run with assertions enabled')
    deadline = monotonic() + 13
    assert all(P % d for d in range(2,isqrt(P)+1))
    adapter = args.root/'source_span.py'
    checked(adapter,ADAPTER_SHA)
    engine = run_path(str(adapter))
    read, encode, check_time, legal = (engine[key] for key in ('read','encode','check_time','legal_add'))
    no_deadline = lambda _ : None
    assert assess({4:(1,{1:2})},no_deadline,0,legal)['disposition'] == 'exact_coordinate_dual'
    assert assess({4:(1,{TARGET:2})},no_deadline,0,legal)['disposition'] == 'exact_legal_adds'
    assert assess({4:(1,{TARGET:1,1:2}),5:(1,{2:3})},no_deadline,0,legal)['disposition'] == 'certified_full_exterior_minor'
    assert assess({4:(1,{TARGET:1,1:2}),5:(1,{1:2})},no_deadline,0,legal)['disposition'] == 'unresolved_rank_deficiency'
    price = read(checked(args.root/'price.json',PRICE))
    first = read(checked(args.root/'support.json',FIRST))
    assert price['word_sha256'] == first['word_sha256'] == engine['WORD']
    assert first['unvisited_cuts'] == [48185] and first['price_sha256'] == PRICE
    core = args.root/'inputs/replay_core.py'
    checked(core,engine['CORE'])
    word = read(decompress(checked(args.root/'price-inputs'/engine['WORD_PATH'],engine['WORD'])))

    def bank(cut, frame, rows, charts, public, deadline):
        eligible = {role:rows[role] for role, chart in enumerate(charts)
                    if chart == frame and role not in engine['PROTECTED']}
        if cut == 48182:
            assert not eligible
            return {'cut':cut,'chart':frame,'disposition':'confirmed_empty_first_bank'}
        result = {'cut':cut,'chart':frame,'eligible_roles':list(eligible),
                  'eligible_owned_roles':[role for role in eligible if role >= public]}
        result.update(assess(eligible,check_time,deadline,legal))
        return result

    records,visited,copies = engine['audit'](word,run_path(str(core)),deadline,bank)
    receipt = {'head':price['head'],'price_sha256':PRICE,'word_sha256':engine['WORD'],
               'first_support_sha256':FIRST,'adapter_sha256':ADAPTER_SHA,
               'visited_prefix_events':visited,'checked_copies':copies,'records':records,
               'unvisited_cuts':[cut for cut in engine['CUTS'] if cut not in {row['cut'] for row in records}],
               'controls':['absent_target_coordinate','legal_one_row_injection','full_minor','rank_deficiency_unresolved'],
               'hard_seconds':15,'cooperative_seconds':13}
    args.out.write_bytes(encode(receipt))


if __name__ == '__main__':
    main()

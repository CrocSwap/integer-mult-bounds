#!/usr/bin/env python3
"""Exact integer replay of a thin-configuration obstruction and #7113 prices.

This is a configuration-level calculation, not a construction of a legal word.
All inequalities on 99/100 powers are certified by integer arithmetic. No
third-party modules and no floating point numbers are used in the calculations.
"""
from collections import Counter
from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_CEILING
from fractions import Fraction as F
from hashlib import sha256
from itertools import permutations
from math import comb
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCALE = 10**12
TARGET = F(128891, 1000)


def blob(path):
    b = path.read_bytes()
    from hashlib import sha1
    return sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()


def check_sources():
    expected = {
        'CallerHPQ.lean': 'd1c93bc474630c0c251f8e1c7b08f5fe4f67e32e',
        'HPDual.lean': 'cfeb604c351b23d95a843269dc353e341e11368f',
        'CallerRC2.lean': '321ec331931fecddd844f3b12fe0caf27178269c',
        'CallerCfgBridge.lean': '696bf9234da325cee26918f887590a1ea8e885e3',
        'CallerSGram.lean': '6c03a7f3b3c50fe4340cd105378409ca39abc474',
        'SchemaCostB.lean': 'b6a1c4b03a81a99e59c433d110871f605bef9694',
        'CertCallerCore.lean': '0bbe8179a901512ccac2948676367eef2d3acc04',
        'emit_odd_type_ab.py': '504316b91bb70bb3697a2488a2b400647067f279',
        'ODD-TYPE-AB-CALLER.json': '9451ceaf6e8e037894680b549f3ef41c21b260d7',
        'ODD-TYPE-AB-REPLAY.json': '7c7641f7727c3e889ab05f87612d01abf8e8b296',
    }
    for name, value in expected.items():
        assert blob(HERE / 'source' / name) == value, name
    caller = HERE / 'source' / 'ODD-TYPE-AB-CALLER.json'
    digest = sha256(caller.read_bytes()).hexdigest()
    assert digest == json.loads((HERE / 'source' / 'ODD-TYPE-AB-REPLAY.json').read_text())['caller_sha256']
    return {'git_blob_sha1': expected, 'caller_sha256': digest}


def root_bounds(m):
    """Return rational L,U with L <= m^(99/100) <= U, verified by powers."""
    assert m > 0
    rhs = m**99 * SCALE**100
    lo, hi = 0, (m + 1) * SCALE
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if mid**100 <= rhs:
            lo = mid
        else:
            hi = mid
    assert lo**100 <= rhs < (lo + 1)**100
    return F(lo, SCALE), F(lo if lo**100 == rhs else lo + 1, SCALE)


ROOTS = {}


def expr(items=()):
    d = {}
    for base, coefficient in items:
        d[base] = d.get(base, F(0)) + F(coefficient)
    return {int(b): c for b, c in d.items() if c}


def add(*es):
    return expr((b, c) for e in es for b, c in e.items())


def mul(e, q):
    return expr((b, c * F(q)) for b, c in e.items())


def interval(e):
    low, high = F(0), F(0)
    for b, c in e.items():
        if b not in ROOTS:
            ROOTS[b] = root_bounds(b)
        l, u = ROOTS[b]
        if c >= 0:
            low, high = low + c*l, high + c*u
        else:
            low, high = low + c*u, high + c*l
    return low, high


def decimal_bound(v, rounding):
    with localcontext() as c:
        c.prec = 45
        c.rounding = rounding
        return str((Decimal(v.numerator) / Decimal(v.denominator)).quantize(Decimal('0.000000000001')))


def report_expr(e):
    l, u = interval(e)
    return {
        'coefficient_by_base': {str(b): str(c) for b, c in sorted(e.items())},
        'exact_lower': str(l), 'exact_upper': str(u),
        'decimal_lower': decimal_bound(l, ROUND_FLOOR),
        'decimal_upper': decimal_bound(u, ROUND_CEILING),
    }


def f2(k):
    # 2k-2 + 2((8k+1)^s - k*8^s - 1)
    #   -(1-(9^s-8^s))*k^2/(k-1) -(k-4)*(1-(17^s-16^s)).
    core = expr([(1, 2*k-4-F(k*k,k-1)-(k-4)),
                 (8*k+1, 2), (8, -2*k-F(k*k,k-1)),
                 (9, F(k*k,k-1)), (17, k-4), (16, -(k-4))])
    return mul(core, F(104, k))


def make_configuration(k):
    # Two all-stage singleton-piece hubs; k-3 pair roles; k leaves, one
    # at each stage. Explicit sets allow both RC2 pair and leaf-cap checks.
    stages = frozenset(range(k))
    roles = []
    for _ in range(2):
        roles.append({'mask': stages, 'pieces': tuple(frozenset((s,)) for s in range(k)), 'main': True})
    for _ in range(k-3):
        roles.append({'mask': frozenset((0,1)), 'pieces': (frozenset((0,1)),), 'main': False})
    for s in range(k):
        roles.append({'mask': frozenset((s,)), 'pieces': (frozenset((s,)),), 'main': False})
    return roles


def make_cluster_configuration(k):
    assert k % 2 == 0
    roles = []
    stages = frozenset(range(k))
    for _ in range(2):
        roles.append({'mask': stages, 'pieces': tuple(frozenset((s,)) for s in range(k)), 'main': True})
    for j in range(2):
        mask = frozenset(range(j*k//2,(j+1)*k//2))
        roles.append({'mask': mask, 'pieces': (mask,), 'main': False})
    for _ in range(k-5):
        roles.append({'mask': frozenset((0,1)), 'pieces': (frozenset((0,1)),), 'main': False})
    for s in range(k):
        roles.append({'mask': frozenset((s,)), 'pieces': (frozenset((s,)),), 'main': False})
    return roles


def piece_at(role, stage):
    found = [p for p in role['pieces'] if stage in p]
    assert len(found) == 1
    return found[0]


def validate_configuration(k, roles, clusters=False):
    n, Q = len(roles), len(roles)-(2*k-2)
    assert Q == 1 and n+2 == 2*k+Q
    masks = [r['mask'] for r in roles]
    for r in roles:
        assert 1 <= len(r['mask']) <= k
        assert all(len(p) >= 1 and p <= r['mask'] for p in r['pieces'])
        assert sum(map(len, r['pieces'])) == len(r['mask'])
        assert set().union(*r['pieces']) == set(r['mask'])
        if r['main']:
            assert all(len(p) == 1 for p in r['pieces'])
    leaves = [r for r in roles if len(r['mask']) == 1]
    nonleaves = n-len(leaves)
    leaf_stages = [sum(r['mask'] == {s} for r in leaves) for s in range(k)]
    assert leaf_stages == [1]*k and max(leaf_stages) <= Q
    assert len(leaves) <= k+Q and len(leaves) <= k*Q
    assert nonleaves >= k-2
    assert k*n-len(leaves) >= k*(2*k-2)
    mains_per_stage = [sum(r['main'] and s in r['mask'] for r in roles) for s in range(k)]
    assert mains_per_stage == [2]*k
    # For l = 2..k+1, both hubs separately meet the deep/shallow
    # definition for each ordered pair. All other contributions are >= 0.
    # l > k is identical to l = k+1. Thus all pairwise RC2 rows hold.
    pair_checks = 0
    for s,t in permutations(range(k),2):
        for l in range(2,k+2):
            count = 0
            for r in roles[:2]:
                d = len(r['mask']); p = piece_at(r,s)
                deep = s in r['mask'] and d >= l and len(p) < l and t not in p
                shallow = s in r['mask'] and t in r['mask'] and d < l and t not in p
                count += int(deep) + int(shallow)
            assert count == 2
            pair_checks += 1
    # All averaged rows are exact: 2 hubs each contribute k(k-1),
    # all pairs/leaves contribute 0 when l >= 3.
    for l in range(3,k+1):
        row = 0
        for r in roles:
            D = len(r['mask'])
            for s in r['mask']:
                a = len(piece_at(r,s))
                row += (k-a if a < l else 0) if l <= D else D-a
        assert row == 2*k*(k-1), (k,l,row)
    pairs = [r['mask'] for r in roles if len(r['mask']) == 2]
    sample = {2,3,4}
    assert all(not p <= sample for p in pairs)
    base = {'k':k,'n':n,'Q':Q,'T_assumed':Q,'e':0,
            'two_hubs':2,'pair_roles':k-3,'leaves':len(leaves),
            'leaf_count_per_stage':leaf_stages, 'nonleaves':nonleaves,
            'mains_per_stage':mains_per_stage, 'pairwise_rc2_checks':pair_checks,
            'averaged_rc2_each':2*k*(k-1),
            'LEAF_left':k*(2*k-2), 'LEAF_right':k*n-len(leaves),
            'pair_role_masks': {'mask':[0,1], 'multiplicity':len(pairs)},
            'three_stage_sample': sorted(sample)}
    if not clusters:
        # Any signed-Gram realization needs a non-hub pair role in every
        # 3-set. Count occurrences, even counting duplicate edges separately.
        assert len(pairs) == k-3
        total3 = comb(k,3)
        cover_occurrences = len(pairs)*(k-2)
        minimum_pairs = (k*(k-1)+5)//6
        assert cover_occurrences < total3 and len(pairs) < minimum_pairs
        for s,t in permutations(sample,2):
            assert sum(s in r['mask'] and t in r['mask'] for r in roles) == 2
        base.update(three_sets_total=total3, pair_cover_occurrences_upper=cover_occurrences,
                    uncovered_three_sets_lower=total3-cover_occurrences,
                    necessary_pair_roles_for_a_frame=minimum_pairs)
    else:
        assert len(pairs) == k-5 and k == 76
        cs = [r for r in roles if len(r['mask']) == k//2]
        assert len(cs) == 2 and not cs[0]['mask'] & cs[1]['mask']
        assert cs[0]['mask'] | cs[1]['mask'] == frozenset(range(k))
        assert all(r['pieces'] == (r['mask'],) for r in cs)
        # Two groups cover every stage triple by pigeonhole, so the simple
        # non-hub pair-coverage cut is satisfied. But in-group triples must
        # also be covered by pair roles by the common-piece kernel argument.
        for s,t in permutations(sample,2):
            assert sum(s in r['mask'] and t in r['mask'] for r in roles) == 3
        assert sum(cs[0]['mask'] <= r['mask'] for r in roles) == 3
        intragroup3 = 2*comb(k//2,3)
        group_cover_occurrences = len(pairs)*(k//2-2)
        per_group_min = (comb(k//2,3)+(k//2-3))//(k//2-2)
        assert group_cover_occurrences < intragroup3
        base.update(pair_roles=len(pairs),cluster_roles=2,cluster_masks=[sorted(r['mask']) for r in cs],
                    cluster_piece_sizes=[len(r['pieces'][0]) for r in cs],
                    nonhub_pair_capacity=sum(comb(len(r['mask']),2) for r in roles[2:]),
                    simple_graph_cut_satisfied=True, within_cluster_triples=intragroup3,
                    pair_cover_occurrences_upper=group_cover_occurrences,
                    necessary_pair_roles_under_common_piece_cut=2*per_group_min)
    return base


def config_prices(k, roles):
    target = Counter(8*len(r['mask'])+1 for r in roles)
    model_pieces = Counter()
    for r in roles:
        for p in r['pieces']:
            model_pieces[8*len(p)] += 1
    model = add(expr(target.items()), mul(expr(model_pieces.items()), -1), expr([(1,-1)]))
    # Stage contacts are the two hub pieces per stage. All other pieces
    # become abstract IDLE_ONEs, except one singleton IDLE_ODD.
    paid = model_pieces.copy()
    paid[8] -= 2*k + 1
    paid[9] += 1
    assert all(c >= 0 for c in paid.values())
    actual = add(expr(target.items()),mul(expr(paid.items()),-1),expr([(8,-2*k)]))
    delta = expr([(8,1),(1,1),(9,-1)])
    assert add(model,delta) == actual
    return {'target_rank_histogram':dict(sorted(target.items())),
            'model_all_pieces_rank_histogram':dict(sorted(model_pieces.items())),
            'plain_actual_rank_histogram':dict(sorted(paid.items())),
            'contact_rank_8_count':2*k,
            'model_scaled':report_expr(mul(model,F(104,k))),
            'actual_scaled':report_expr(mul(actual,F(104,k))),
            'delta_scaled':report_expr(mul(delta,F(104,k)))}


def caller_control():
    C = json.loads((HERE/'source'/'ODD-TYPE-AB-CALLER.json').read_text())
    k=C['stages']
    assert k == 17 and C['schema'] == 'mixed-root-caller/1'
    js=[e for e in C['events'] if e[0]=='J']
    assert len(js)==k and sorted(e[1] for e in js)==list(range(1,k+1))
    result={}; expressions={}
    for ty, contacts in [('A',4),('B',2)]:
        t=C['types'][ty]; n=t['roles']; ports=len(t['ports']); Q=n-(2*k-2)
        assert n==36 and Q==4 and all(row[:2]==[-1,0] for row in t['diagonal'])
        target=Counter(1+8*sum(row[2:]) for row in t['diagonal'])
        es=[e for e in C['events'] if e[0]==ty]
        odd=[e for e in es if e[1]=='IDLE_ODD']
        query=[e for e in es if e[1]=='QUERY']
        assert len(odd)+len(query)==Q
        paid=Counter(); model_pieces=Counter()
        for e in es:
            if e[1]=='QUERY':
                assert e[4]%2==1
                paid[1]+=1
            elif e[1] in ('IDLE_ONE','IDLE_ODD'):
                mask=e[3]
                assert len(set(mask))==len(mask) and all(1<=i<=k for i in mask)
                d=len(mask)
                assert d>0
                paid[8*d+(e[1]=='IDLE_ODD')]+=1
                model_pieces[8*d]+=1
        modeled = add(expr(target.items()),mul(expr(model_pieces.items()),-1),expr([(8,-contacts*k),(1,-Q)]))
        actual = add(expr(target.items()),mul(expr(paid.items()),-1),expr([(8,-contacts*k)]))
        delta = expr((b,c) for e in odd for b,c in [(8*len(e[3]),1),(1,1),(8*len(e[3])+1,-1)])
        assert add(modeled,delta)==actual
        expressions[ty]=(modeled,actual,delta)
        result[ty]={'roles':n,'ports':ports,'Q':Q,'contacts_per_stage':contacts,
                    'target_histogram':dict(sorted(target.items())),
                    'actual_plain_histogram':dict(sorted(paid.items())),
                    'idle_odd_records':odd,'query_records':query,
                    'model_scaled':report_expr(mul(modeled,F(104,k))),
                    'repo_scaled':report_expr(mul(actual,F(104,k))),
                    'repo_minus_model_per_port':report_expr(delta)}
    assert len(result['A']['query_records'])==4 and not result['A']['idle_odd_records']
    assert len(result['B']['idle_odd_records'])==4 and not result['B']['query_records']
    assert [e[3] for e in result['B']['idle_odd_records']]==[[8],[8],[9],[9]]
    weighted = add(mul(expressions['A'][2],F(96,k)),mul(expressions['B'][2],F(8,k)))
    result['weighted_correction']=report_expr(weighted)
    return result


def main():
    sources=check_sources()
    k76,k77=(make_configuration(k) for k in (76,77))
    results={}
    for k, roles in [(76,k76),(77,k77)]:
        results[str(k)]={'constraints':validate_configuration(k,roles),'prices':config_prices(k,roles),
                         'F2_closed_form':report_expr(f2(k))}
    model76=results['76']['prices']['model_scaled']; actual76=results['76']['prices']['actual_scaled']
    model77=results['77']['prices']['model_scaled']; actual77=results['77']['prices']['actual_scaled']
    assert F(model76['exact_lower']) > TARGET and F(actual76['exact_lower']) > TARGET
    assert F(model77['exact_upper']) < TARGET and F(actual77['exact_lower']) > TARGET
    assert F(results['77']['F2_closed_form']['exact_upper']) < TARGET
    clustered=make_cluster_configuration(76)
    cluster_result={'constraints':validate_configuration(76,clustered,clusters=True),
                    'prices':config_prices(76,clustered)}
    assert F(cluster_result['prices']['model_scaled']['exact_lower']) > TARGET
    assert F(cluster_result['prices']['actual_scaled']['exact_lower']) > TARGET
    control=caller_control()
    output={'sources':sources,'configuration_results':results,'clustered_configuration':cluster_result,'caller_7113':control,
            'rpow_integer_certificate':{str(b): {'lower_numerator':int(l*SCALE), 'upper_numerator':int(u*SCALE),
                                               'denominator':SCALE, 'inequality':'L^100 <= base^99 * denominator^100 < (L+1)^100'}
                                         for b,(l,u) in sorted(ROOTS.items())},
            'scope':'Abstract mask/piece and charge-profile configurations only. The accompanying three-stage rank and common-piece kernel arguments rule out a tight signed-Gram realization for the described families. No legal word, endpoint identity, kappa bound, or caller counterexample is claimed.'}
    (HERE/'RESULT.json').write_text(json.dumps(output,indent=2)+'\n')
    print('PASS source blob hashes, #7113 replay hash and charge masks')
    print('PASS integer enclosures, adjacent k=77 F2 control and configuration checks')
    for k in ('76','77'):
        p=results[k]['prices']
        print(f"k={k}: model [{p['model_scaled']['decimal_lower']}, {p['model_scaled']['decimal_upper']}], "
              f"repo IDLE_ODD [{p['actual_scaled']['decimal_lower']}, {p['actual_scaled']['decimal_upper']}]")
    p=cluster_result['prices']
    print(f"k=76 clustered: model [{p['model_scaled']['decimal_lower']}, {p['model_scaled']['decimal_upper']}], "
          f"repo IDLE_ODD [{p['actual_scaled']['decimal_lower']}, {p['actual_scaled']['decimal_upper']}]")
    print('result:',HERE/'RESULT.json')


if __name__=='__main__':
    main()

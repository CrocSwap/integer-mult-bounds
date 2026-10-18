"""Exact uniform audit of PR942's signed-dual supporting lemma.

Apache-2.0. Eva Ayala / ToikY, with substantial OpenAI Codex assistance.
No retained arithmetic engine or repository module is imported.
"""
import argparse
import ast
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
WIDTHS = (4, 5, 7, 8, 9)
PRICES = (-1, -20, -8, -2, 4)
CAPACITIES = {8: (672, 2), 16: (448, 4), 32: (448, 8), 48: (448, -13)}
INVENTORY = {4: 80, 5: 32, 7: 54, 8: 122, 9: 216}
Z_MAX = Q(1, 500)
INHERITED_ENDPOINT = Q("0.001664727258740678855773")


def need(condition, message):
    if not condition:
        raise ValueError(message)


def strict_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            need(key not in result, 'duplicate JSON field: ' + key)
            result[key] = value
        return result
    def invalid(value):
        raise ValueError('nonfinite JSON value: ' + value)
    return json.loads(path.read_text(), object_pairs_hook=unique, parse_constant=invalid)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def source_bindings():
    sources = strict_json(HERE / 'SOURCES.json')
    need(sources['base_commit'] == '407d52ff15b2217b6e22bce44728b4c3907b6515', 'base pin')
    paths = []
    for entry in sources['files']:
        raw = (HERE / entry['retained_path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == entry['sha256'], 'source SHA256: ' + entry['retained_path'])
        git_blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        need(git_blob == entry['git_blob'], 'source Git blob: ' + entry['retained_path'])
        paths.append(entry['repository_path'])
    expected = ['research/complex-t37-owners/ALL-T-PROOF.md',
                'research/complex-t37-owners/independent/all_t_bound.py',
                'research/complex-t21-owner-bound/PROOF.md',
                'certificates/selected-result.json']
    need(paths == expected, 'complete source inventory')
    retained = HERE / 'references' / expected[1].replace('/', '__')
    assignments = {}
    for node in ast.parse(retained.read_text()).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in ('WIDTHS', 'PRICES', 'CAPACITIES', 'INVENTORY'):
                assignments[name] = ast.literal_eval(node.value)
    need(assignments == dict(WIDTHS=WIDTHS, PRICES=PRICES, CAPACITIES=CAPACITIES, INVENTORY=INVENTORY),
         'literal fixed-family source constants')
    selected = strict_json(HERE / 'references' / expected[3].replace('/', '__'))
    need(selected['source_prs'][0] == 942 and selected['kappa'] == '1661960547713947/1000000000000000000',
         'selected context')
    return sources


def enumerate_bins(prices=PRICES, capacities=CAPACITIES):
    """Bounded recursive count vectors; retains a maximizing bin witness."""
    upper, witnesses, count = {}, {}, 0
    for cap, (_, bonus) in sorted(capacities.items()):
        def visit(index, available, score, vector):
            nonlocal count
            if index == len(WIDTHS):
                count += 1
                if available not in upper or score > upper[available]:
                    upper[available] = score
                    witnesses[available] = [cap, list(vector)]
                return
            width = WIDTHS[index]
            for n in range(available // width + 1):
                visit(index + 1, available - n * width, score + n * prices[index], vector + (n,))
        visit(0, cap, bonus, ())
    return upper, witnesses, count


def elementary_constants(z_max=Z_MAX):
    need(0 < z_max <= Z_MAX, 'proved exponent range 0<z<=1/500')
    # exp(4) > this finite positive Taylor sum > 48, hence log(48)<4.
    term, total = Q(1), Q(1)
    for k in range(1, 7):
        term *= Q(4, k)
        total += term
    need(total == Q(437, 9) and total > 48, 'strict logarithm upper certificate')
    # exp(y)<=sum y^k=1/(1-y), 0<=y<1; apply y=4/500.
    y = 4 * z_max
    need(0 < y < 1, 'geometric exponential bound domain')
    upper = 4 / (1 - y)
    need(upper <= Q(125, 31), 'uniform logarithm-times-power bound')
    return {'exp4_partial_sum': str(total), 'log48_upper': '4',
            'exp_log48_z_upper': str(1 / (1-y)), 'log48_times_48_power_z_upper': str(upper)}


def support_table(upper, z_max=Z_MAX):
    constants = elementary_constants(z_max)
    rows = []
    for r, u in sorted(upper.items()):
        if r in (0, 1, 48):
            continue
        need(0 < r < 48, 'attainable rank domain')
        v = 48*u + 13*r
        # log(48/r)>=2*(48-r)/(48+r). The negative-credit term is
        # favorable and can be dropped; a positive term needs an upper bound.
        margin = Q(2*r*(48-r), 48+r) - Q(max(v, 0)*125, 925*31)
        need(margin > Q(4, 5), 'positive uniform support margin at rank ' + str(r))
        rows.append({'rank': r, 'u': u, 'v': v, 'credit_sign': 'positive' if v > 0 else 'nonpositive',
                     'normalized_margin_lower': str(margin)})
    need(len(rows) == 42, 'all 42 strict-rank obligations')
    return rows, constants


def inventory_audit(upper):
    mass = sum(cap * n for cap, (n, _) in CAPACITIES.items()) - 9*sum(w*n for w, n in INVENTORY.items())
    signed = sum(n*bonus for n, bonus in CAPACITIES.values()) + 9*sum(INVENTORY[w]*p for w, p in zip(WIDTHS, PRICES))
    need((mass, signed) == (14382, -3892), 'fixed rank and signed-price totals')
    need((upper[0], upper[1], upper[48]) == (0, 19, -13), 'zero/rank-one/rank-48 endpoints')
    credit = 48*signed+13*mass
    need(credit == 150 and 48*upper[1]+13 == 925, 'credit elimination direction and demand')
    n1 = Q(credit, 925)
    n48 = (mass - n1)/48
    need((n1, n48) == (Q(6, 37), Q(11086, 37)), 'normalized equality profile')
    need(n1.denominator == 37 and n48.denominator == 37, 'smallest integral equality replica count')
    return {'mass_per_replica': mass, 'signed_price_per_replica': signed, 'credit_per_replica': credit,
            'rank_one_credit': 925, 'normalized_idle': {'1': str(n1), '48': str(n48)},
            'equality_replica_counts': 'positive multiples of 37; necessary in the relaxation'}


def certificate():
    sources = source_bindings()
    upper, witnesses, count = enumerate_bins()
    need(count == 1163 and len(upper) == 45, 'complete bin enumeration')
    rows, constants = support_table(upper)
    need(0 < INHERITED_ENDPOINT <= Z_MAX, 'inherited endpoint inside proved interval')
    need('0.001664727258740678855773' in (HERE/'references'/'research__complex-t37-owners__ALL-T-PROOF.md').read_text(), 'inherited endpoint source statement')
    minimum = min(rows, key=lambda row: Q(row['normalized_margin_lower']))
    return {'status': 'PASS_T37_UNIFORM_SUPPORT_AUDIT', 'base_commit': sources['base_commit'],
            'assignment_seed': 66, 'scope': 'Fixed U8 signed-dual supporting lemma only; no moment-root or outer replay; no new kappa',
            'exponent_domain': '0<z<=1/500', 'inherited_endpoint': str(INHERITED_ENDPOINT), 'bin_vectors': count, 'attainable_ranks': len(upper),
            'strict_rank_obligations': len(rows), 'positive_credit_ranks': sum(row['v'] > 0 for row in rows),
            'nonpositive_credit_ranks': sum(row['v'] <= 0 for row in rows),
            'elementary_certificates': constants, 'u': {str(r): x for r, x in sorted(upper.items())},
            'maximizing_bin_witnesses': {str(r): w for r, w in sorted(witnesses.items())},
            'support': rows, 'minimum_normalized_margin_lower': minimum,
            'inventory': inventory_audit(upper)}


def mathematical_controls():
    upper, _, _ = enumerate_bins()
    def reject(fn, label):
        try:
            fn()
        except ValueError:
            return
        raise ValueError('negative control accepted: ' + label)
    bad = dict(upper); bad[2] += 10
    reject(lambda: support_table(bad), 'unpaid signed credit')
    bad = dict(upper); bad[1] = 18
    reject(lambda: inventory_audit(bad), 'rank-one multiplier')
    bad = dict(upper); bad[48] = 13
    reject(lambda: inventory_audit(bad), 'capacity-48 bonus sign')
    bad = dict(upper); bad[0] = 1
    reject(lambda: inventory_audit(bad), 'zero-rank credit')
    bad = dict(upper); del bad[44]
    reject(lambda: support_table(bad), 'missing attainable rank')
    reject(lambda: support_table(upper, Q(1, 499)), 'unsupported wider interval')
    reject(lambda: support_table(upper, Q(0)), 'zero exponent is equality')
    # At z=0 all costs vanish: strictness genuinely needs z>0.
    need(48*2 - 2*48 - Q(650,925)*(48 - 48) == 0, 'zero-exponent exact boundary control')
    # Rank mass alone is insufficient: all residual mass at 48 has credit 0,
    # less than the required 150 per replica. Reversing >= admits this vector.
    all48, replicas = 2397, 8
    need(48*all48 == 14382*replicas and 0 < 150*replicas, 'integer reversed-credit counterexample')
    need(-13*all48 == -31161 < -3892*replicas == -31136, 'signed-price direction counterexample')
    # Exact rational counterexample outside the certified interval at z=2.
    phi = lambda r: r*Q(73,r)**2
    c1 = 48*phi(1)-phi(48)
    c2 = 48*phi(2)-2*phi(48)
    need(c2-Q(650,925)*c1 == -Q(1923769,37), 'wider-range rank-two counterexample')
    # Incorrectly treating negative credit as a positive expense is detectable.
    rows, _ = support_table(upper)
    sign_errors = [r for r in rows if r['v'] < 0 and
                   Q(2*r['rank']*(48-r['rank']),48+r['rank']) - Q(-r['v']*125,925*31) <= 0]
    need(len(sign_errors) > 0, 'negative-credit absolute-value counterexample')
    return {'rejected_mutations': 7, 'exact_boundary_controls': 4,
            'negative_credit_wrong_sign_witness_rank': sign_errors[0]['rank']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--write', type=Path)
    args = parser.parse_args()
    result = certificate()
    controls = mathematical_controls()
    if args.write:
        with args.write.open('x') as stream:
            stream.write(json.dumps(result, indent=2)+'\n')
    else:
        need(canonical(result) == canonical(strict_json(HERE/'CERTIFICATE.json')), 'complete typed certificate equality')
    # This separate module uses a fill DP and fixed-point transcendental
    # enclosures. It imports no code or outputs from this implementation.
    import importlib.util
    spec = importlib.util.spec_from_file_location('standalone_support_check', HERE/'independent.py')
    independent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(independent)
    other = independent.audit()
    need({str(row['rank']): row['u'] for row in other['table']} == result['u'], 'independent complete bin upper table')
    need(other['strict_ranks_checked'] == 42, 'independent full support coverage')
    if args.json:
        print(json.dumps({'certificate': result, 'controls': controls, 'independent': other}, indent=2))
    print('PASS_T37_UNIFORM_SUPPORT_AUDIT bins=1163 ranks=42 z=(0,1/500] minimum_margin=24274/28675 no_new_kappa')


if __name__ == '__main__':
    main()

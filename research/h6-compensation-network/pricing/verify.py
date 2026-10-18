#!/usr/bin/env python3
"""Exact nominal invoices for the conditional H6 compensation network.

The independent rational-series oracle from h6-independent-audit is reused;
the predecessor banked module only nominates root intervals for a separately
checked invoice. No partial block is normalized to a full-port saving.
"""
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
sys.path.insert(0, str(PACKAGE))
from artifact import load_receipt


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


oracle = load('h6_independent_invoice_oracle', ROOT / 'research/h6-independent-audit/invoice/verify.py')
sys.path.insert(0, str(ROOT / 'research/niemeier-lattices/workbench/paid-controller'))
import banked
require = oracle.require
N, H, R, R3 = 30960, 17, 480337920, 3363840
DISPLAY = 10**24


def scaled(low, high):
    return oracle.display_interval(low, high)


def helper_terms(stages, path, count):
    m = 16 * stages + 1
    q, pad = divmod(m, H)
    require(sum(path) == H, 'ordinary helper path spans17')
    terms = [(F(count * stages * rank), rank) for rank in path]
    if pad:
        terms.append((F(count * stages * pad, q), pad))
    require(sum(mass for mass, _ in terms) == F(count * stages * m, q),
            'complete helper mass including pads')
    return terms, q, pad


def full_invoice(stages, histogram, compensation_helpers=R):
    original = oracle.model(stages)
    centers = sum(width * count for width, count in histogram.items())
    terms = [(F(2 * N * stages * 16), 16)]
    terms.extend((F(stages * width * count), width) for width, count in histogram.items())
    for block in original['idle_parts']:
        terms.extend((F(2 * N * rank), rank) for rank in block)
    stock = F((stages - 1) * N)
    deficit = stock - stages * centers
    require(sum(mass for mass, _ in terms) == original['m'] * stock - deficit,
            'independent full base identity')
    for count, path in ((compensation_helpers, [1, 15, 1]), (816, [17])):
        add, q, pad = helper_terms(stages, path, count)
        terms.extend(add)
        stock += F(stages * count, q)
    require(sum(mass for mass, _ in terms) == original['m'] * stock - deficit,
            'independent complete invoice identity')
    require(all(original['m']**2 > 2 * rank**2 for _, rank in terms),
            'strict child cap on every actual/pad child')
    return dict(stages=stages, m=original['m'], cap=original['cap'], q=q, pad=pad,
                terms=terms, stock=stock, deficit=deficit, center_bill=centers,
                idle_slots=original['idle_slots'], compensation_helpers=compensation_helpers)


def comparison(row, target):
    low, high = oracle.pressure(row['terms'], row['m'], target / (1 - target))
    slack = row['deficit'] - high, row['deficit'] - low
    require(slack[1] < 0, 'full edge invoice strictly fails requested target')
    return dict(target=str(target), pressure_scaled_1e24=scaled(low, high),
                slack_scaled_1e24=scaled(*slack), verdict='STRICTLY_FAILS_NOMINAL_SCREEN')


def edge_budget(row, target):
    """Reprice the edge allowance using its actual [1,15,1] helper path."""
    unit, _, _ = helper_terms(row['stages'], [1,15,1], 1)
    by_rank = Counter()
    for mass, rank in row['terms']:
        by_rank[rank] += mass
    for mass, rank in unit:
        by_rank[rank] -= row['compensation_helpers'] * mass
    require(all(value >= 0 for value in by_rank.values()), 'removed only edge helper work')
    base = [(mass, rank) for rank, mass in by_rank.items() if mass]
    alpha = target/(1-target)
    bl, bu = oracle.pressure(base, row['m'], alpha)
    hl, hu = oracle.pressure(unit, row['m'], alpha)
    low, high = (row['deficit']-bu)/hu, (row['deficit']-bl)/hl
    count = oracle.floor_fraction(low)
    require(count == oracle.floor_fraction(high), 'exact edge helper allowance resolves')
    pass_slack = row['deficit']-bu-count*hu, row['deficit']-bl-count*hl
    fail_slack = row['deficit']-bu-(count+1)*hu, row['deficit']-bl-(count+1)*hl
    require(pass_slack[0] > 0 > fail_slack[1], 'edge allowance adjacent signs')
    return dict(max_edge_helpers=count, boundary_slack_scaled_1e24=scaled(*pass_slack),
                next_slack_scaled_1e24=scaled(*fail_slack),
                scope='Actual [1,15,1] edge path with the same base and816 K helpers; not the earlier H6 [1,7,8,1] budget.')


def nominal_root(row):
    # Nomination and source certification are differential checks, not the oracle.
    source = dict(m=row['m'], terms=[(mass, F(row['m'], rank))
                                   for mass, rank in row['terms']],
                  stock=row['stock'], deficit=row['deficit'])
    a, b = banked.c.bracket(source)
    pair = banked.c.scaled(a / (1 + a), b / (1 + b))
    lo, hi = (F(value, 10**18) for value in pair)
    pl = oracle.pressure(row['terms'], row['m'], lo / (1 - lo))
    ph = oracle.pressure(row['terms'], row['m'], hi / (1 - hi))
    require(pl[1] < row['deficit'] < ph[0], 'independent nominal-root enclosure')
    return pair


def partial_profile(path):
    result = load_receipt(path)
    proof_descriptor = json.loads(path.read_text()).get('proof_data')
    require(result.get('full_forward_and_same_order_dual_checks') is True,
            'partial route must have both arbitrary-dirt orientations')
    profiles = []
    for role, key in (('sources', 'source_paths'), ('targets', 'target_paths'), ('helpers', 'helper_paths')):
        entries = result[key]
        if isinstance(entries, dict):
            entries = [entries]
        profiles.extend((role, entry['count'], entry['path']) for entry in entries)
    mass = sum(count * sum(profile) for _, count, profile in profiles)
    require(mass == result['total_local_transition_rank'], 'partial actual emitted path mass')
    out = []
    for stages in (3, 5, 7):
        m = 16 * stages + 1
        terms = []
        for _, count, profile in profiles:
            terms.extend((F(stages * count * rank), rank) for rank in profile)
        helpers = sum(count for role, count, _ in profiles if role == 'helpers')
        for role, count, profile in profiles:
            if role == 'helpers':
                helper_terms(stages, profile, count)
        q, pad = divmod(m, H)
        terms.append((F(stages * helpers * pad, q), pad))
        require(all(m*m > 2 * rank*rank for _, rank in terms), 'partial strict child caps')
        helper_stock = F(stages * helpers, q)
        ordinary_mass = stages * mass
        pad_mass = F(stages * helpers * pad, q)
        out.append(dict(stages=stages, m=m, ordinary_transition_rank_mass=ordinary_mass,
            pad_rank_mass=str(pad_mass), helper_stock=str(helper_stock),
            replication=q, physical_helper_banks_per_stage=helpers,
            replicated_pad_rank_mass=stages * helpers * pad,
            target_pressure_scaled_1e24={name: scaled(*oracle.pressure(terms, m, target/(1-target)))
                                       for name, target in targets.items()}))
    return dict(path=str(path.relative_to(ROOT)), sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        proof_data_descriptor=proof_descriptor,
        status=result['status'], role_profiles=[dict(role=role, count=count, path=profile)
                                               for role, count, profile in profiles],
        local_transition_rank_mass=mass, helper_count=result['helper_count'], invoices=out,
        scope='Partial standalone compensation only: actual register-path and helper-bank contributions at the specified full-template m. No complete data/controller stock, deficit, K composition or full-port nominal root is inferred. Source-set size is not used as N in an overall saving.')


selected = json.loads((ROOT / 'certificates/selected-result.json').read_text())
packet = json.loads((ROOT / 'research/community-efficient500-audit/packets/1424.json').read_text())
targets = {'selected': F(selected['kappa']),
           'pr1424_pending': F(re.search(r'\d+\.\d+', packet['title']).group(0))}


def main():
    k_path = PACKAGE / 'k_encoder/RESULT.json'
    k_word = json.loads(k_path.read_text())
    require(k_word['status'] == 'PASS_EXPLICIT_K_WORD_AND_COMPOSED_FIXTURES' and
            k_word['K_ordinary_roles'] == 816 and k_word['ordinary_center_path'] == [17] and
            k_word['private_descent_C'] == 13872, 'explicit K word supplies the billed profile')
    def primitive(coefficient):
        value = abs(F(coefficient))
        return 3+(value.numerator.bit_length()-1)+value.numerator.bit_count()+(value.denominator.bit_length()-1)
    gather_cost = sum(count*primitive(value) for value,count in k_word['gather_coefficients'].items())
    scatter_cost = sum(count*primitive(value) for value,count in k_word['scatter_coefficients'].items())
    require(sum(k_word['gather_coefficients'].values()) == k_word['feature_nonzeros'] ==
            sum(k_word['scatter_coefficients'].values()), 'complete K nonzero coefficient counts')
    # Clear/copy/erase contributes3 per private episode; the dual replacement
    # prices the copy as a unit add (4), raising its episode charge to6.
    k_forward = 2*(gather_cost+scatter_cost)+3*816
    k_dual = 2*(gather_cost+scatter_cost)+6*816
    require(k_forward == k_word['K_forward_primitive_bound'] and
            k_dual == k_word['K_dual_primitive_bound'] == 247219488,
            'independent K weighted-primitive recount in both orientations')
    k_bound = max(k_forward,k_dual)
    bucket_path = PACKAGE / 'routes/FULL-MASK-SCREEN.json'
    bucket = load_receipt(bucket_path)
    lanes = bucket['required_distinct_ordinary_helper_lanes']
    require(lanes == 227312640 and bucket['every_target_mask_span_dimension'] == 16,
            'full bucket compensation lane inventory')
    models = []
    for name, hist, compensation_helpers in (
            ('fullwidth_K_conditional_profile', {17: 816}, R),
            ('heterogeneous_K_conditional_alternative', {17: 256, 15: 560}, R),
            ('bucketed_fullwidth_K_conditional_profile', {17: 816}, lanes)):
        rows = []
        for stages in (3, 5, 7):
            row = full_invoice(stages, hist, compensation_helpers)
            pair = nominal_root(row)
            require(F(pair[1], 10**18) < targets['selected'], 'nominal root below selected')
            # T=q supplies an exactly integral bank arrangement, separately for
            # the edge helper group and the K-center helper group.
            replication = row['q']
            banks_per_stage = replication * (compensation_helpers + 816) // row['q']
            require(replication * (compensation_helpers + 816) % row['q'] == 0,
                    'integral replicated helper banks')
            require((replication * row['stock']).denominator == 1, 'integral replicated complete stock')
            rows.append(dict(stages=stages, m=row['m'], center_private_copy_bill=row['center_bill'],
                deficit=str(row['deficit']), stock_per_template=str(row['stock']),
                replication=replication, replicated_stock=str(replication * row['stock']),
                stock_replication_factor=row['q'], helper_pad=row['pad'],
                physical_helper_banks_per_stage=banks_per_stage,
                replicated_helper_banks_all_stages=stages * banks_per_stage,
                replicated_pad_rank_mass=stages * banks_per_stage * row['pad'],
                local_helper_path_rank_mass=17 * (compensation_helpers + 816),
                complete_rank_mass_per_template=str(sum(mass for mass, _ in row['terms'])),
                idle_slots=row['idle_slots'], max_child_rank=max(rank for _, rank in row['terms']),
                nominal_kappa_interval_scaled_1e18=pair,
                exact_edge_helper_budgets={name:edge_budget(row,target) for name,target in targets.items()},
                target_comparisons={name: comparison(row, target) for name, target in targets.items()}))
        models.append(dict(name=name, histogram={str(k):v for k,v in hist.items()},
            compensation_helpers=dict(count=compensation_helpers, path=[1,15,1]),
            K_helpers=dict(count=816,path=[17]),
            scalar_ADDs=2*R+2*compensation_helpers,
            compensation_scalar_primitive_bound=16*R+8*compensation_helpers+6*R3,
            K_scalar_ADDs=k_word['K_full_scalar_additions'],
            composite_scalar_ADDs=2*R+2*compensation_helpers+k_word['K_full_scalar_additions'],
            K_scalar_primitive_bound=k_bound,
            composite_scalar_primitive_bound=16*R+8*compensation_helpers+6*R3+k_bound,
            scalar_charge_scope='All weighted precompensation/scatter edges remain; gather/cleanup is once per physical lane. K charge is independently recounted from the bound full-center coefficient histograms in both orientations. Physical compiler, adapters, precision/tape and all-size supplier charges remain separate.',
            data_source_and_target_paths=[16], rows=rows,
            scope='Conditional complete rank profile, assuming the K-word realizes this data/center/helper inventory. Scalar/compiler/precision charges and actual K admission remain separate.'))
    # Fixed two-copy/full-center mask model: even removing ALL helpers and
    # center pressure cannot overcome the active data lower bound at these targets.
    mask = []
    center_bill = 2 * 816 * 17
    for name, target in targets.items():
        alpha = target / (1 - target)
        logarithm_low, _ = oracle.log_interval(F(7))
        tail_low = 32 * alpha * logarithm_low
        tail_right = F(N - center_bill, N)
        require(tail_low > tail_right, 'all-L mask necessary-screen exclusion')
        negative = {str(L): (L - 1)*N - L*center_bill for L in (3,5)}
        require(all(v < 0 for v in negative.values()), 'first two odd stages have negative deficit')
        mask.append(dict(target=name, kappa=str(target), center_bill=center_bill,
            negative_deficits=negative, tail_start=7,
            active_pressure_per_NL_lower=str(tail_low), deficit_per_NL_upper=str(tail_right),
            gap_scaled_1e24=scaled(tail_low-tail_right, tail_low-tail_right),
            status='FAILS_FIXED_MODEL_FOR_EVERY_ODD_L_GE_3',
            proof='m/16>L; exp(alpha*log(m/16))-1 >= alpha*log L. Active mass2NL*16 alone gives pressure/(NL)>32alpha*log L>=32alpha*log7>1-C/N>D/(NL) for every L>=7. L3/L5 have negative deficits. Additional paid work only strengthens rejection; altered paths/factorizations remain outside scope.'))
    partials = []
    for name in ('RESULT.json', 'MASK-2-RESULT.json', 'MASK-4-RESULT.json'):
        route_receipt = PACKAGE / 'routes' / name
        require(route_receipt.exists(), 'named partial route receipt exists: '+name)
        partials.append(partial_profile(route_receipt))
    census_path = ROOT / 'research/h6-independent-audit/walsh/results.json'
    census = json.loads(census_path.read_text())
    require(census['compensation_nonzeros'] == R and census['exceptional_abs_t_3_pairs'] == R3,
            'full census binds scalar counts')
    names = ['research/h6-independent-audit/invoice/verify.py',
        'research/h6-compensation-network/artifact.py',
        'research/h6-compensation-network/contract/THEOREM.md',
        'research/h6-compensation-network/construction/network.py',
        'research/h6-compensation-network/routes/FULL-MASK-SCREEN.json',
        'research/h6-compensation-network/k_encoder/RESULT.json',
        'research/h6-compensation-network/k_encoder/network.py',
        'research/h6-independent-audit/walsh/results.json',
        'certificates/selected-result.json',
        'research/community-efficient500-audit/packets/1424.json']
    receipt = dict(status='PASS_EXACT_CONDITIONAL_COMPENSATION_PRICING', no_new_kappa=True,
        edge_count=R, abs_t3_edges=R3, scalar_ADDs=4*R,
        scalar_primitive_bounds=dict(one_sixteenth=8,five_sixteenths=11,unit=4,
            total_per_invocation=24*R+6*R3,
            scope='Contract emission bound for compensation alone; excludes K, adapters, controller routing, tape, precision and all-size compilation. These scalar primitives are not extra Fourier children.'),
        source_hashes={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in names},
        proof_data_bindings={str(path.relative_to(ROOT)):json.loads(path.read_text()).get('proof_data')
            for path in [bucket_path]+[ROOT/item['path'] for item in partials]},
        K_scalar_recount=dict(feature_nonzeros=k_word['feature_nonzeros'],
            forward=k_forward,dual=k_dual,max_orientation=k_bound,
            scalar_ADDs=k_word['K_full_scalar_additions']),
        models=models, full_K_mask_two_center_chains_all_stage_screen=mask,
        partial_routes=partials,
        open_obligations='Admitted emitted K arbitrary-input word, complete representative/adapter counts, precision and tape recount, controller/child recipes, exact recovery, bit and outer transfer. Standalone cheap mask/partial routes do not implement K at frame zero for free.')
    require(receipt['scalar_primitive_bounds']['total_per_invocation'] == 11548293120,
            'contract scalar primitive count')
    (HERE / 'RESULT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(receipt['status'])
    for model in models:
        print(model['name'],[(r['stages'],r['nominal_kappa_interval_scaled_1e18']) for r in model['rows']])
    print('all-L two-full-center-chain model rejected; partial routes',len(partials))


if __name__ == '__main__':
    main()

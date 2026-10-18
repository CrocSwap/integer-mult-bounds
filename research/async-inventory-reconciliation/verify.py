#!/usr/bin/env python3
"""Reconcile one archived finite-menu obstruction, without changing its sources.

Alexander Templeton (azide0x37), with substantial OpenAI Codex assistance.
Apache-2.0. The archive and inherited arithmetic retain their original credit.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
from itertools import product
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = ROOT / 'research/experiment-log'
WALL = ARCHIVE / 'negative-searches/async505-inventory-wall'
EXACT = WALL / 'exact-certificate'
RECEIPTS = WALL / 'async505-inventory-bound'
STATUS = 'PASS_EXACT_FIXED_INVENTORY_FINITE_MENU_DUAL_WALL'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return sha256(raw).hexdigest()


def read_json(path):
    return json.loads(path.read_bytes())


def pinned_bytes(path, expected):
    raw = path.read_bytes()
    require(digest(raw) == expected, 'Source bytes changed: ' + str(path))
    return raw


def positive_counts(value, name):
    require(isinstance(value, dict) and value, 'Empty ' + name)
    require(all(isinstance(k, str) and str(int(k)) == k and int(k) > 0
                and type(v) is int and v > 0 for k, v in value.items()),
            'Invalid positive integer counts: ' + name)
    return {int(k): v for k, v in value.items()}


def source_rows(data, pins, load_source):
    """Check the copied numerical menu against its retained constructor reports."""
    menu = data['word_menu']
    require(len(menu) == 146, 'Expected the complete 146-row archived menu')
    seen = set()
    rows = []
    for row in menu:
        source = PurePosixPath(row['source'])
        require(not source.is_absolute() and '..' not in source.parts
                and len(source.parts) == 3 and source.name == 'RESULT.json',
                'Invalid menu source path')
        require(source.parts[0] in pins['source_prefixes'], 'Unknown menu source prefix')
        relative = str(PurePosixPath(pins['source_prefixes'][source.parts[0]])
                       / source.parts[1] / source.name)
        require(relative not in seen, 'Duplicate menu source')
        seen.add(relative)
        original = load_source(relative)
        require(original['status'] == 'PASS_LOCAL_CONSTRUCTOR_ONLY', 'Source scope changed')
        require(original['label'] == pins['label_aliases'].get(row['label'], row['label']),
                'Source label differs')
        profile = positive_counts(row['profile'], 'menu profile')
        widths = positive_counts(row['widths'], 'menu widths')
        require(('width_counts' in original) != ('widths' in original),
                'Ambiguous source widths')
        key = 'width_counts' if 'width_counts' in original else 'widths'
        require(profile == positive_counts(original['profile'], 'source profile'),
                'Source profile differs: ' + row['label'])
        require(widths == positive_counts(original[key], 'source widths'),
                'Source widths differ: ' + row['label'])
        require(sum(widths.values()) == data['helpers_per_call'], 'Helper total differs')
        rows.append({'label': row['label'], 'source_label': original['label'], 'path': relative})
    return rows


def all_patterns(capacity, widths):
    """Independent enumeration by multiplicity tuples, including the empty bin."""
    return [counts for counts in product(*(range(capacity // w + 1) for w in widths))
            if sum(w * n for w, n in zip(widths, counts)) <= capacity]


def exact_costs(data, engine, base_two):
    """Reuse the two pinned interval engines; this is not a third interval proof."""
    m, b = data['ambient'], Q(data['rejected_endpoint'])
    require(type(m) is int and m == 73 and 0 < b < Q(1, 500), 'Unsupported moment domain')
    result = {0: (Q(0), Q(0))}
    for rank in range(1, 49):
        if base_two:
            main = engine.moment(m, 1, [(rank, 1)], b)
            fallback = engine.moment(m, 1, [(1, 32 * m * m)], b)
            interval = tuple(m * (main[i] + fallback[i] / 10**16) for i in range(2))
        else:
            interval = tuple(m * x for x in engine.moment({rank: 1}, m, 1, b, True))
        require(0 < interval[0] <= interval[1], 'Invalid cost interval')
        result[rank] = interval
    return result


def check_receipt(data, receipt, costs, method, input_hash, engine_hash):
    """Check the dual itself with explicit failures, including under python -O."""
    require(receipt['status'] == STATUS and receipt['engine_method'] == method,
            'Wrong receipt kind')
    require(receipt['inputs_sha256'] == input_hash and receipt['engine_sha256'] == engine_hash,
            'Receipt source digest differs')
    for key in ('ambient', 'live', 'calls'):
        require(type(data[key]) is int and data[key] > 0
                and type(receipt[key]) is int and receipt[key] == data[key],
                'Receipt model differs: ' + key)
    require(Q(receipt['rejected_endpoint']) == Q(data['rejected_endpoint']), 'Wrong endpoint')
    families = positive_counts(data['families_by_rank'], 'family inventory')
    menu = data['word_menu']
    widths = sorted({int(w) for row in menu for w in row['widths']})
    require(set(families) == {8, 16, 32, 48} and widths == [5, 7, 8, 9],
            'Unsupported inventory domain')
    alpha = {int(k): Q(v) for k, v in receipt['alpha'].items()}
    beta = {int(k): Q(v) for k, v in receipt['beta'].items()}
    require(set(alpha) == set(families) and set(beta) == set(widths), 'Incomplete dual')
    counts_by_rank = {}
    for rank in sorted(families):
        patterns = all_patterns(rank, widths)
        counts_by_rank[str(rank)] = len(patterns)
        for pattern in patterns:
            remainder = rank - sum(w * n for w, n in zip(widths, pattern))
            lhs = alpha[rank] + sum(beta[w] * n for w, n in zip(widths, pattern))
            require(lhs <= costs[remainder][0], 'Infeasible dual inequality')
    require(receipt['patterns_checked'] == sum(counts_by_rank.values()), 'Pattern count differs')
    scores = []
    for row in menu:
        profile = positive_counts(row['profile'], 'profile')
        stock = positive_counts(row['widths'], 'widths')
        require(set(profile) <= set(costs) and set(stock) <= set(beta), 'Unsupported menu rank')
        require(sum(stock.values()) == data['helpers_per_call'], 'Helper total differs')
        scores.append(sum(n * costs[r][0] for r, n in profile.items())
                      + sum(n * beta[w] for w, n in stock.items()))
    minimum = min(scores)
    best = [i for i, score in enumerate(scores) if score == minimum]
    bound = (sum(n * alpha[r] for r, n in families.items()) + data['calls'] * minimum)
    bound /= data['ambient'] * data['live']
    require(bound > 1, 'Nonpositive obstruction margin')
    require(Q(receipt['moment_lower_bound']) == bound
            and Q(receipt['strict_margin']) == bound - 1, 'Bound arithmetic differs')
    require(receipt['word_menu_size'] == len(menu) and receipt['minimizing_menu_indices'] == best
            and receipt['minimizing_labels'] == [menu[i]['label'] for i in best],
            'Menu minimum differs')
    require([Q(x) for x in receipt['word_reduced_costs']] == [s - minimum for s in scores],
            'Reduced costs differ')
    cfg = data['outer']
    eta, beta_outer = Q(cfg['eta']), Q(cfg['beta'])
    s = (1 - beta_outer) * Q(data['rejected_endpoint'])
    require(0 < eta < Q(1, 2) and 0 < beta_outer < 1 and 0 < s < Q(1, 2),
            'Outer domain differs')
    chain = Q(cfg['initial'])
    require(type(cfg['steps']) is int and cfg['steps'] == 6, 'Outer step count differs')
    for _ in range(cfg['steps']):
        require(1 - 2 * s + chain > 0, 'Outer recurrence denominator condition')
        chain = (1 - s) * s + s * chain
    q = (1 - 2 * eta) * chain
    margin = (1 - eta) * q / (1 + q)
    base, grid = Q(cfg['baseline_kappa']), Q(cfg['grid'])
    require(grid > 0 and base < margin < base + grid, 'Outer next grid point not excluded')
    outer = receipt['fixed_outer_grid_obstruction']
    require(Q(outer['upper_margin']) == margin and Q(outer['next_kappa']) == base + grid
            and outer['next_kappa_rejected'] is True and outer['scope'] == cfg['scope'],
            'Outer receipt differs')
    return {'method': method, 'patterns_by_capacity': counts_by_rank,
            'strict_margin': str(bound - 1), 'minimizing_labels': [menu[i]['label'] for i in best],
            'next_kappa': str(base + grid)}


def rejection_controls(data, receipt, costs, method, input_hash, engine_hash, pins, load_source):
    rejected = []

    def rejects(name, action):
        try:
            action()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('Negative control accepted: ' + name)

    for name in ('missing_source', 'changed_profile', 'changed_widths', 'truncated_menu',
                 'duplicate_source', 'boolean_count'):
        changed = deepcopy(data)
        row = changed['word_menu'][0]
        if name == 'missing_source':
            row['source'] = 'absent/source/RESULT.json'
        elif name == 'changed_profile':
            row['profile']['1'] += 1
        elif name == 'changed_widths':
            row['widths']['9'] -= 1
            row['widths']['8'] += 1
        elif name == 'truncated_menu':
            changed['word_menu'].pop()
        elif name == 'duplicate_source':
            changed['word_menu'][1]['source'] = row['source']
        elif name == 'boolean_count':
            row['profile']['7'] = True
        rejects(name, lambda: source_rows(changed, pins, load_source))
    for name in ('raise_capacity_dual', 'raise_width_dual', 'wrong_input_digest',
                 'changed_bound', 'changed_outer_grid', 'removed_rank1_charges'):
        changed, report = deepcopy(data), deepcopy(receipt)
        if name == 'raise_capacity_dual':
            report['alpha']['48'] = str(Q(report['alpha']['48']) + 1)
        elif name == 'raise_width_dual':
            report['beta']['9'] = str(Q(report['beta']['9']) + 1)
        elif name == 'wrong_input_digest':
            report['inputs_sha256'] = '0' * 64
        elif name == 'changed_bound':
            report['moment_lower_bound'] = '1'
        elif name == 'changed_outer_grid':
            report['fixed_outer_grid_obstruction']['next_kappa'] = '1/100'
        elif name == 'removed_rank1_charges':
            for row in changed['word_menu']:
                row['profile'].pop('1')
        rejects(name, lambda: check_receipt(changed, report, costs, method, input_hash, engine_hash))
    return rejected


def historical_replays(data, method, engine_path, receipt_path):
    """Reproduce the old entry point's behavior, with all writes in a fresh tempdir."""
    results = []
    with tempfile.TemporaryDirectory(prefix='async-inventory-reconcile-') as temp:
        work = Path(temp)
        for case in ('unchanged', 'wrong_source', 'removed_rank1_charges'):
            changed = deepcopy(data)
            if case == 'wrong_source':
                changed['word_menu'][0]['source'] = 'absent/source/RESULT.json'
            elif case == 'removed_rank1_charges':
                for row in changed['word_menu']:
                    row['profile'].pop('1')
            inputs = EXACT / 'INPUTS.json'
            if case != 'unchanged':
                inputs = work / (case + '.json')
                inputs.write_text(json.dumps(changed) + '\n')
            for optimized in (False, True):
                out = work / (case + str(optimized) + '.json')
                command = [sys.executable, '-I', '-B', *(['-O'] if optimized else []),
                           str(EXACT / 'verify.py'), str(inputs), str(engine_path), str(out)]
                if method == 'base-two':
                    command.append('--base-two')
                run = subprocess.run(command, capture_output=True, text=True, timeout=30)
                emitted = read_json(out) if out.exists() else None
                expected_failure = case == 'removed_rank1_charges' and not optimized
                require((run.returncode == 1 and emitted is None and 'wall not certified' in run.stderr)
                        if expected_failure else (run.returncode == 0 and emitted is not None),
                        'Historical behavior changed: ' + case)
                if not expected_failure:
                    require(emitted['status'] == STATUS, 'Historical status changed')
                    sign = Q(emitted['strict_margin']) > 0
                    require(sign == (case != 'removed_rank1_charges'), 'Historical margin sign changed')
                    if case == 'unchanged':
                        require(out.read_bytes() == receipt_path.read_bytes(), 'Historical receipt differs')
                results.append({'case': case, 'optimized': optimized, 'exit_code': run.returncode,
                                'emitted_pass': emitted is not None,
                                'strict_margin': None if emitted is None else emitted['strict_margin'],
                                'strict_margin_positive': None if emitted is None else sign})
    return results


def reconcile():
    pins = read_json(HERE / 'SOURCE-PINS.json')
    for relative, expected in pins['files'].items():
        pinned_bytes(ROOT / relative, expected)
    manifest = read_json(ARCHIVE / 'MANIFEST.json')
    source_digests = {}

    def load_source(relative):
        require(relative in manifest, 'Source absent from archived manifest')
        raw = pinned_bytes(ARCHIVE / relative, manifest[relative])
        source_digests[relative] = digest(raw)
        return json.loads(raw)

    raw_inputs = (EXACT / 'INPUTS.json').read_bytes()
    data = json.loads(raw_inputs)
    rows = source_rows(data, pins, load_source)
    arithmetic, controls, historical = [], {}, {}
    for method, filename, receipt_name in (
        ('mercator', 'moment.py', 'EXACT-WALL-146.json'),
        ('base-two', 'base_two_moment.py', 'EXACT-WALL-146-BASE-TWO.json'),
    ):
        engine_path = EXACT / filename
        spec = importlib.util.spec_from_file_location('inventory_' + method, engine_path)
        engine = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(engine)
        costs = exact_costs(data, engine, method == 'base-two')
        receipt_path = RECEIPTS / receipt_name
        receipt = read_json(receipt_path)
        args = (data, receipt, costs, method, digest(raw_inputs), digest(engine_path.read_bytes()))
        arithmetic.append(check_receipt(*args))
        controls[method] = rejection_controls(*args, pins, load_source)
        historical[method] = historical_replays(data, method, engine_path, receipt_path)
    return {
        'status': 'PASS_ASYNC_INVENTORY_RECONCILIATION',
        'base_commit': pins['base_commit'], 'assignment_seed': 95,
        'source_rows_checked': len(rows),
        'source_prefix_counts': dict(sorted(Counter(row['path'].split('/')[2] for row in rows).items())),
        'source_status': 'PASS_LOCAL_CONSTRUCTOR_ONLY',
        'label_aliases': pins['label_aliases'],
        'source_bindings_sha256': digest(json.dumps(source_digests, sort_keys=True).encode()),
        'source_pins_sha256': digest((HERE / 'SOURCE-PINS.json').read_bytes()),
        'arithmetic': arithmetic, 'rejection_controls': controls,
        'historical_replays': historical,
        'scope': 'Pinned historical profile/width reports and two exact finite-menu dual receipts. '
                 'Uses inherited interval engines. No new search, supplier admission, kappa, '
                 'independent interval implementation, or full multiplication theorem.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path, help='save a freshly computed report instead of checking RESULT.json')
    args = parser.parse_args()
    try:
        result = reconcile()
        if args.write:
            require(not args.write.exists(), 'Use a fresh report path')
            args.write.write_text(json.dumps(result, indent=2) + '\n')
        else:
            require(result == read_json(HERE / 'RESULT.json'), 'Reconciliation report differs')
    except (ValueError, KeyError, OSError, subprocess.TimeoutExpired) as error:
        print('FAIL_ASYNC_INVENTORY_RECONCILIATION:', error, file=sys.stderr)
        return 1
    print(result['status'], '146 source rows, 696 dual inequalities, 24 rejection controls, 12 historical replays')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

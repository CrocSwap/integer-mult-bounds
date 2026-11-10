#!/usr/bin/env python3
"""Independent factorial/pair oracle; execution wrapper is supplied separately."""
from itertools import combinations_with_replacement, product
from math import factorial, prod


FIELDS = (
    'n', 'height', 'sources', 'exits', 'boundary_exits', 'units',
    'column_mass', 'source_count', 'matched_jobs', 'minimum_source',
    'all_sources_above_n_over_m', 'rank_one_surplus', 'unit_count_upper',
    'mirror',
)


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _positive(value, message):
    _require(type(value) is int and value > 0, message)
    return value


def _pairs(value, minimum):
    _require(type(value) is list and value, 'nonempty inventory list')
    result = []
    for row in value:
        _require(type(row) is list and len(row) == 2, 'inventory pair')
        rank = _positive(row[0], 'integer positive rank')
        count = _positive(row[1], 'integer positive multiplicity')
        _require(rank >= minimum, 'inventory rank lower bound')
        result.append((rank, count))
    _require(len({rank for rank, count in result}) == len(result),
             'distinct inventory ranks')
    return tuple(sorted(result))


def _raw_pairs(value, minimum):
    _require(type(value) is dict and value, 'raw inventory dictionary')
    rows = []
    for key, count in value.items():
        _require(type(key) is str and key.isascii() and key.isdecimal(),
                 'raw rank decimal string')
        rank = int(key)
        _require(str(rank) == key, 'canonical raw rank string')
        rows.append([rank, count])
    return _pairs(rows, minimum)


def _case_inventory(case, raw_inventory):
    if 'inventory' in case:
        _require(case['inventory'] == 'raw_p7', 'known raw inventory')
        _require(type(raw_inventory) is dict, 'complete raw source dictionary')
        profile = raw_inventory['strictification']
        _require(type(profile) is dict, 'strictification dictionary')
        return (_raw_pairs(profile['targets'], 2),
                _raw_pairs(profile['paid'], 1))
    return _pairs(case['targets'], 2), _pairs(case['paid'], 1)


def _lattice(targets, degree):
    """All degree multisets, without source recursion or partial cap pruning."""
    rows = []
    for multiset in combinations_with_replacement(range(len(targets)), degree):
        exponents = tuple(multiset.count(i) for i in range(len(targets)))
        coefficient = factorial(degree) // prod(factorial(a) for a in exponents)
        coefficient *= prod(count ** a for (rank, count), a in zip(targets, exponents))
        column = prod(rank ** a for (rank, count), a in zip(targets, exponents))
        rows.append((column, coefficient))
    return tuple(rows)


def _paid_words(paid, depth):
    """Enumerate support words; multiplicities stay exact integer factors."""
    for word in product(paid, repeat=depth):
        yield prod(rank for rank, count in word), prod(count for rank, count in word)


def _add(histogram, rank, count):
    _require(type(rank) is int and rank >= 0, 'nonnegative histogram rank')
    _require(type(count) is int and count > 0, 'positive histogram contribution')
    histogram[rank] = histogram.get(rank, 0) + count


def _root_targets(sources, targets, lattice, cap):
    for column, coefficient in lattice:
        if column <= cap:
            for rank, count in targets:
                _add(sources, rank * column, coefficient * count)


def _present_units(lattice, rho, paths, cap):
    present = [(rho * column, paths * coefficient)
               for column, coefficient in lattice if rho * column <= cap]
    return sum(weight for scale, weight in present), sum(
        scale * weight for scale, weight in present)


def _pair_edges(targets, paid, lattice, rho, paths, cap, histograms):
    sources, exits, boundary = histograms
    matched = 0
    for column, coefficient in lattice:
        z = rho * column
        for target, target_count in targets:
            parent_present = target * z <= cap
            for rank, paid_count in paid:
                child_present = rank * z <= cap
                weight = paths * coefficient * target_count * paid_count
                job_rank = target * rank * z
                if parent_present and child_present:
                    matched += weight
                elif parent_present:
                    _add(exits, job_rank, weight)
                    _add(boundary, job_rank, weight)
                elif child_present:
                    _add(sources, job_rank, weight)
    return matched


def _histogram(value):
    return [[rank, value[rank]] for rank in sorted(value)]


def _check_laws(n, targets, paid, histograms, units, columns, upper):
    sources, exits, boundary = histograms
    m, kmin, rmax = targets[-1][0], targets[0][0], paid[-1][0]
    _require(sources and all(1 <= s <= n and n < m * s for s in sources),
             'source support law')
    _require(all(1 <= e < n and m * e <= rmax * n for e in exits),
             'paid exit support law')
    _require(all(m * e > kmin * n for e in boundary), 'boundary support law')
    delta = sum(k * c for k, c in targets) - sum(r * c for r, c in paid)
    balance = sum(k * c for k, c in sources.items()) - sum(r * c for r, c in exits.items())
    _require(balance == delta * columns, 'rank-mass identity')
    _require(units <= upper and sum(sources.values()) <= sum(c for k, c in targets) * units,
             'full unit/source budget')
    return delta


def _one_case(case, targets, paid):
    n = _positive(case['n'], 'integer ambient rank')
    m, kmin, rmax = targets[-1][0], targets[0][0], paid[-1][0]
    _require(rmax < m <= n, 'strict paid/target/ambient domain')
    cap, height, least = n // m, 0, 1
    while least * kmin <= cap:
        height += 1
        least *= kmin
    levels = [_lattice(targets, degree) for degree in range(height + 1)]
    sources, exits, boundary = {}, {}, {}
    histograms = sources, exits, boundary
    _root_targets(sources, targets, levels[height], cap)
    units = columns = matched = 0
    for depth in range(height + 1):
        for rho, paths in _paid_words(paid, depth):
            local_units, local_columns = _present_units(levels[height - depth], rho, paths, cap)
            units += local_units
            columns += local_columns
            if depth == height:
                if rho <= cap:
                    for rank, count in paid:
                        _add(exits, rho * rank, paths * count)
            else:
                matched += _pair_edges(targets, paid, levels[height - depth - 1],
                                       rho, paths, cap, histograms)
    return _finish_case(n, height, targets, paid, histograms, units, columns, matched)


def _finish_case(n, height, targets, paid, histograms, units, columns, matched):
    sources, exits, boundary = histograms
    W, P = sum(c for k, c in targets), sum(c for r, c in paid)
    upper = sum(P ** d * W ** (height - d) for d in range(height + 1))
    delta = _check_laws(n, targets, paid, histograms, units, columns, upper)
    mirror = dict(exits)
    for rank, count in sources.items():
        _add(mirror, n - rank, count)
    return {
        'n': n, 'height': height, 'sources': _histogram(sources),
        'exits': _histogram(exits), 'boundary_exits': _histogram(boundary),
        'units': units, 'column_mass': columns, 'source_count': sum(sources.values()),
        'matched_jobs': matched, 'minimum_source': min(sources),
        'all_sources_above_n_over_m': all(n < targets[-1][0] * s for s in sources),
        'rank_one_surplus': delta, 'unit_count_upper': upper,
        'mirror': _histogram(mirror),
    }


def build_cases(contract, raw_inventory):
    _require(type(contract) is dict and contract.get('schema') == 'finite-complete-flow-audit/1',
             'finite complete flow contract')
    _require(contract['fields'] == list(FIELDS), 'complete field schema')
    _require(contract['defaults'] == {'extra_height': 0, 'height_base': None},
             'default height domain')
    _require(type(contract['cases']) is list, 'finite cases list')
    result = {}
    for case in contract['cases']:
        _require(type(case) is dict and type(case.get('id')) is str, 'case identifier')
        _require(case['id'] not in result, 'distinct case identifiers')
        targets, paid = _case_inventory(case, raw_inventory)
        result[case['id']] = _one_case(case, targets, paid)
    return result


# Shared coordinator-authored byte/CLI wrapper; not an independent math model.
def _run_cli():
    import argparse
    import hashlib
    import json
    from pathlib import Path
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description='Complete finite flow certificate')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--emit', type=Path)
    mode.add_argument('--check', action='store_true')
    args = parser.parse_args()
    contract_raw = (base / 'CONTRACT.json').read_bytes()
    if hashlib.sha256(contract_raw).hexdigest() != '4fc49527e728be80abaa4c5f7f0bd62da30afaea70b71be2c77b8457136da1f1':
        raise ValueError('contract byte drift')
    pins_raw = (base / 'SOURCE-PINS.json').read_bytes()
    if hashlib.sha256(pins_raw).hexdigest() != 'a533c5c9513470c2294c3b6217caf052eca63ce568a075d35e5f6c2251358812':
        raise ValueError('source manifest byte drift')
    for row in json.loads(pins_raw)['objects']:
        data = (base / row['local_path']).read_bytes()
        blob = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if len(data) != row['bytes'] or hashlib.sha256(data).hexdigest() != row['sha256'] or blob != row['git_blob']:
            raise ValueError('source byte drift: '+row['local_path'])
    # These fixed mathematical inputs cannot be replaced by changing pin metadata.
    if hashlib.sha256((base/'inputs/flow.py.txt').read_bytes()).hexdigest() != '460f0b0262d7b6880973f46240b3fff1e9f04601fa1d658dda18688b1e26575a':
        raise ValueError('canonical flow drift')
    raw = (base/'inputs/p7-RESULT.json.txt').read_bytes()
    if hashlib.sha256(raw).hexdigest() != '9b814be97e3b45fcc28eafa8a65694897a7387f71a14d44796c6aadf303d7fab':
        raise ValueError('raw inventory drift')
    contract, inventory = json.loads(contract_raw), json.loads(raw)
    if 'build_packet' in globals():
        packet = build_packet(contract, inventory)
    else:
        packet = {'schema': contract['schema'], 'cases': build_cases(contract, inventory)}
    encoded = json.dumps(packet, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')+b'\n'
    if args.emit is not None:
        if args.emit.exists():
            raise ValueError('refusing to replace first packet')
        args.emit.write_bytes(encoded)
    else:
        reference = base / globals().get('REFERENCE_FILE', 'FIRST.json')
        if encoded != reference.read_bytes():
            raise ValueError('complete packet mismatch')
    print('PASS_COMPLETE_FINITE_FLOW', hashlib.sha256(encoded).hexdigest(), len(encoded))


if __name__ == '__main__':
    try:
        _run_cli()
    except (ValueError, OSError) as error:
        import sys
        print('FAIL_COMPLETE_FINITE_FLOW', error, file=sys.stderr)
        raise SystemExit(1)

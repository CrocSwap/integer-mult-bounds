#!/usr/bin/env python3
"""Eligibility-sensitive source counts; JoyboyBrian with OpenAI Codex, Apache-2.0."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import sys
from types import ModuleType

PACKAGE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sources():
    retained = json.loads((PACKAGE / 'VENDOR.json').read_text())
    out = {}
    for row in retained:
        raw = (PACKAGE / row['retained_path']).read_bytes()
        need(sha256(raw).hexdigest() == row['sha256'], 'changed source bytes')
        out[Path(row['retained_path']).name] = raw
    return out


def words(inventory, degree):
    """Weighted ordered rank words, used only for tiny reduced fixtures."""
    out = Counter({1: 1})
    for _ in range(degree):
        following = Counter()
        for x, count in out.items():
            for rank, multiplicity in inventory.items():
                following[x * rank] += count * multiplicity
        out = following
    return out


def census(targets, paid, n):
    """Independent ordered-word sum of root and absent-parent target slots."""
    m, low = max(targets), min(targets)
    need(n >= m and low >= 2 and max(paid) < m, 'rank contract')
    g, column = 0, 1
    while m * column * low <= n:
        g += 1
        column *= low
    need(g <= 3, 'bounded fixture budget')
    root_spectrum = Counter()
    for c, count in words(targets, g).items():
        if m * c <= n:
            for k, multiplicity in targets.items():
                root_spectrum[c * k] += count * multiplicity
    root = sum(root_spectrum.values())
    nonroot_spectrum = Counter()
    nonroot, first = 0, None
    by_depth = []
    for d in range(1, g + 1):
        subtotal = 0
        for rho, paths in words(paid, d - 1).items():
            for r, repetitions in paid.items():
                for c, units in words(targets, g - d).items():
                    if m * rho * r * c > n:
                        continue
                    for k, multiplicity in targets.items():
                        if m * rho * c * k > n:
                            count = paths * repetitions * units * multiplicity
                            subtotal += count
                            nonroot_spectrum[rho * r * c * k] += count
                            if first is None:
                                first = {'depth': d, 'parent_multiplier': rho, 'paid_rank': r,
                                         'child_column': c, 'target_rank': k, 'source_rank': rho * r * c * k,
                                         'count': count}
        nonroot += subtotal
        by_depth.append(subtotal)
    return {'n': n, 'height': g, 'root': root, 'nonroot': nonroot,
            'by_depth': by_depth, 'total': root + nonroot, 'first_nonroot': first,
            'source_spectrum': [list(row) for row in sorted((root_spectrum + nonroot_spectrum).items())]}


def complete(targets, paid, floor, cutoff):
    t, p = Counter(), Counter(paid)
    for k, count in targets.items():
        t[max(k, floor)] += count
        if k < floor:
            p[floor - k] += count
    split = Counter()
    for k, count in p.items():
        quotient, remainder = divmod(k, cutoff)
        split[cutoff] += quotient * count
        if remainder:
            split[remainder] += count
    return +t, +split


def mass(inventory):
    return sum(k * count for k, count in inventory.items())


def rejected(condition, name):
    try:
        need(condition, name)
    except ValueError:
        return name
    raise ValueError('negative control accepted: ' + name)


def verify():
    inputs = sources()
    flow_module = ModuleType('pinned_flow')
    exec(compile(inputs['flow.py'], 'vendor/flow.py', 'exec'), flow_module.__dict__)
    selected = json.loads(inputs['selected.json'])
    raw_t = {int(k): v for k, v in selected['targets'].items()}
    raw_p = {int(k): v for k, v in selected['paid'].items()}
    targets, paid = complete(raw_t, raw_p, 21, 20)
    need(mass(targets) - mass(paid) == mass(raw_t) - mass(raw_p) == 752, 'completion/split conservation')
    calibration = []
    for g in (1, 2):
        for offset in (-1, 0, 1):
            n = 145 * 21 ** g + offset
            exact = census(targets, paid, n)
            flow = flow_module.Flow(targets, paid, n).merged()
            need(exact['total'] == flow['source_count'], 'selected root/nonroot census mismatch')
            need(dict(exact['source_spectrum']) == dict(flow['sources']), 'selected spectrum mismatch')
            need(all(145 * s > n for s in flow['sources']), 'strict source threshold')
            degree = exact['height']
            envelope = Fraction((degree + 1) * mass(targets) ** (degree + 1) * 145, n)
            need(exact['total'] < envelope, 'selected moment envelope')
            calibration.append(exact)
    # This downward jump occurs inside a fixed-height slab, not at a height reset.
    decline = [census(targets, paid, n) for n in (145 * 25 - 1, 145 * 25)]
    need(decline[0]['height'] == decline[1]['height'] == 1, 'decline in one slab')
    need(decline[0]['total'] > decline[1]['total'], 'source count is not monotone')
    literal_cases = []
    for t, p in [({2: 1, 5: 1}, {1: 2}), ({2: 2, 5: 1}, {1: 1, 4: 1})]:
        for n in (5, 9, 10, 19, 20, 25):
            f = flow_module.Flow(t, p, n)
            actual = f.literal([r for r, count in p.items() for _ in range(count)])
            independent = census(t, p, n)
            need(independent['total'] == sum(actual['sources'].values()), 'literal census mismatch')
            need(dict(independent['source_spectrum']) == dict(actual['sources']), 'literal spectrum mismatch')
            need(all(count > 0 for _, count in independent['source_spectrum']), 'positive source multiplicity')
            t1, p1, g = mass(t), mass(p), independent['height']
            upper = Fraction(5 * t1 * sum(p1 ** d * t1 ** (g-d) for d in range(g+1)), n)
            need(independent['total'] < upper, 'general moment bound')
            need(all(5 * s > n and s <= n for s in actual['sources']), 'source bounds')
            literal_cases.append([n, independent['root'], independent['nonroot'], independent['total']])
    v, H = selected['strictification']['power'], selected['compiler']['H']
    need((v, H) == (1024, 64215200000000), 'selected context')
    W, L, M = sum(raw_t.values()) ** v, 21 ** v, 145 ** v
    tbar = mass(raw_t) ** v + W * L
    hhi = (H - (M.bit_length() - 1)) // (L.bit_length() - 1)
    ratio_log_upper = tbar.bit_length() - (L.bit_length() - 1)
    x = (hhi + 1).bit_length() + tbar.bit_length() + hhi * ratio_log_upper
    need(mass(raw_t) > mass(raw_p), 'positive completed surplus')
    need(1000 * x < 3070 * H, 'K/N < 3.070')
    need(x < 233670787813430, 'strict improvement against PR5026 Xhi')
    root_fixture = calibration[1]
    controls = [
        rejected(root_fixture['root'] == sum(targets.values()) ** 2, 'ignore-root-eligibility'),
        rejected(root_fixture['total'] == root_fixture['root'], 'omit-nonroot-demand'),
        rejected(decline[1]['total'] >= decline[0]['total'], 'assume-source-monotonicity'),
        rejected(sum(targets.values()) == mass(targets), 'rank-mass-is-call-count'),
        rejected(mass(targets) - mass(raw_p) == 752, 'omit-paid-completion'),
        rejected(all(n - s == 0 for n in (10,) for s in flow_module.Flow({2:1,5:1},{1:2},n).merged()['sources']), 'omit-source-complements'),
    ]
    need(sources() == inputs, 'source bytes changed during replay')
    for row in calibration + decline:
        spectrum = row.pop('source_spectrum')
        row['source_rank_types'] = len(spectrum)
        row['source_spectrum_sha256'] = sha256(json.dumps(spectrum, separators=(',', ':')).encode()).hexdigest()
    return {'schema_version': 1, 'evidence': 'author-checked scoped proof and finite calibration',
            'selected_kappa_unchanged': '60403/20000000', 'selected_v1': calibration,
            'nonmonotonicity': decline, 'literal_checks': literal_cases, 'negative_controls': controls,
            'coefficient': {'H': H, 'N': '2^64215200000000', 'raw_target_mass': mass(raw_t),
                            'raw_paid_mass': mass(raw_p), 'Tbar_log2_upper': tbar.bit_length(),
                            'ratio_log2_upper': ratio_log_upper, 'height_upper': hhi, 'X': x,
                            'K_over_N_strict_upper': '3070/1000', 'previous_strict_upper': '3639/1000',
                            'previous_X': 233670787813430}}


if __name__ == '__main__':
    try:
        need(sys.argv[1:] in ([], ['--emit']), 'usage: verify.py [--emit]')
        result = verify()
        if sys.argv[1:] == ['--emit']:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            need(result == json.loads((PACKAGE / 'RESULT.json').read_text()), 'changed receipt')
            print('PASS_SELECTED_TRUNCATED_SOURCE_ENVELOPE: K/N < 3.070; 6 selected fixtures; 12 literal checks; 6 controls')
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print('FAIL_SELECTED_TRUNCATED_SOURCE_ENVELOPE: ' + str(exc), file=sys.stderr)
        sys.exit(1)

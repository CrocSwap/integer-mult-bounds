#!/usr/bin/env python3
"""Independent literal-frame and whole-idle contract audit for #6833.

Prepared for @CubeJerry with substantial OpenAI ChatGPT/Codex assistance.
Apache-2.0. Imports no predecessor implementation. Construction and compiler
credit is preserved in NOTICE.md and the byte-identical retained notices.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha1, sha256
from pathlib import Path
import argparse
import json

HERE = Path(__file__).resolve().parent
BASE = '7c49fe32c55de02c2c873655c804b16e4c3fef0a'
HEAD = 'ad24ad966b857dbfed50d9121624db84b2eccc92'
N, PORTS, DIMENSION = 20, 104, 153


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n=N):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def unit(j):
    return [F(i == j) for i in range(N)]


def inverse(matrix):
    n = len(matrix)
    a = [list(row) + identity(n)[i] for i, row in enumerate(matrix)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if a[i][j]), None)
        require(pivot is not None, 'singular ordinary frame')
        a[j], a[pivot] = a[pivot], a[j]
        q = a[j][j]
        a[j] = [x / q for x in a[j]]
        for i in range(n):
            if i != j and a[i][j]:
                q = a[i][j]
                a[i] = [x - q * y for x, y in zip(a[i], a[j])]
    return [row[n:] for row in a]


def dot(a, b):
    return sum((x * y for x, y in zip(a, b)), F())


def column(a, j):
    return [row[j] for row in a]


def multiply(a, b):
    cols = list(zip(*b))
    return [[dot(row, col) for col in cols] for row in a]


def outer(x, y):
    return [[u * v for v in y] for u in x]


def normalized(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(k): normalized(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [normalized(v) for v in value]
    return value


def sparse(v):
    return [[i, str(x)] for i, x in enumerate(v) if x]


def digest(value):
    return sha256(json.dumps(normalized(value), sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def source_check():
    manifest = json.loads((HERE / 'SOURCE-PINS.json').read_text())
    require((manifest['base_commit'], manifest['pending_chain_head']) == (BASE, HEAD), 'frozen source heads')
    hashes = {}
    for row in manifest['files']:
        relative = row['retained_path']
        require(relative.startswith('retained/') and '..' not in Path(relative).parts, 'retained source path')
        require(relative not in hashes, 'distinct retained sources')
        raw = (HERE / relative).read_bytes()
        require(sha256(raw).hexdigest() == row['sha256'], 'retained SHA256: ' + relative)
        blob = sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        require(blob == row['git_blob'], 'retained Git blob: ' + relative)
        require(row['source_commit'] in (BASE, HEAD), 'source commit outside frozen scope')
        hashes[relative] = row['sha256']
    require(len(hashes) == 11, 'complete retained source inventory')
    return hashes


def parse_frames(word):
    """Maintain F with physical value = F * logical value, without setting Q,D.

    A whole four-event kernel acts logically as F^-1 K F. Its correction ADD
    belongs to K, not to F. Every other ordinary scalar gate updates F exactly.
    """
    require((word['roles'], word['n'], word['stages'], word['ambient_rank']) == (N, N, 18, DIMENSION), 'priced caller dimensions')
    require(word['sL'] == word['sR'] == [1] * 9 and word['nodes'] == [], 'priced all-one shape')
    events = word['events']
    require(events[-N:] == [['LAMBDA', r, -1] for r in range(N)], 'one final total-Q normalization per role')
    frame, sites, idles = identity(), [], []
    basis_gates, coefficient_max, index = 0, F(), 0
    while index < len(events) - N:
        event = events[index]
        op = event[0]
        if op == 'ADD':
            _, dst, src, coefficient = event
            require(dst != src and 0 <= dst < N and 0 <= src < N, 'ordinary ADD roles')
            q = F(coefficient)
            require(q and q.denominator == 1, 'integral nonzero ADD')
            frame[dst] = [x + q * y for x, y in zip(frame[dst], frame[src])]
            coefficient_max = max(coefficient_max, abs(q))
            basis_gates += 1
        elif op == 'SWAP':
            _, a, b = event
            require(a != b and 0 <= a < N and 0 <= b < N, 'ordinary SWAP roles')
            frame[a], frame[b] = frame[b], frame[a]
            basis_gates += 1
        elif op == 'SCALE':
            _, role, coefficient = event
            q = F(coefficient)
            require(q in (-1, 1) and 0 <= role < N, 'unimodular scalar frame')
            frame[role] = [q * x for x in frame[role]]
            coefficient_max = max(coefficient_max, abs(q))
            basis_gates += 1
        elif op == 'LAMBDA':
            raw = events[index + 1]
            require(raw[0] in ('LOCAL', 'QUERY'), 'normalization encloses a native/query kernel')
            if raw[0] == 'LOCAL':
                _, stage, src, dst = raw
            else:
                _, dst, src, power = raw
                require(power == -1, 'thin inverse query')
                stage = None
            require(0 <= dst < N and 0 <= src < N and dst != src, 'kernel uses two distinct fields')
            require(events[index:index + 4] == [['LAMBDA', dst, -1], raw, ['LAMBDA', dst, 1], ['ADD', dst, src, '-1']], 'complete normalized four-event kernel')
            back = inverse(frame)
            require(multiply(back, frame) == identity(), 'ordinary frame inverse')
            active = [[back[a][dst] * frame[dst][b] + back[a][src] * frame[src][b] for b in range(N)] for a in range(N)]
            sites.append({'event': index, 'stage': stage, 'dst': dst, 'src': src, 'frame': deepcopy(frame), 'back': back, 'x': column(back, dst), 'y': list(frame[src]), 'active': active})
            index += 4
            continue
        elif op == 'IDLE_ONE':
            _, role, stages = event
            require(0 <= role < N, 'idle physical role')
            require(stages and len(stages) == len(set(stages)) and all(isinstance(s, int) and 1 <= s <= 18 for s in stages), 'distinct valid fresh idle stages')
            back = inverse(frame)
            idles.append({'event': index, 'role': role, 'stages': stages[:], 'host_stage': sites[-1]['stage'], 'phi': column(back, role), 'gamma': list(frame[role]), 'frame': deepcopy(frame), 'back': back})
        else:
            raise ValueError('unsupported literal event: ' + op)
        index += 1
    require(frame == identity(), 'complete ordinary frame returns to identity')
    require([s['stage'] for s in sites if s['stage'] is not None] == list(range(1, 19)), 'each full stage occurs exactly once in order')
    require(len(sites) == 21 and len(idles) == 16, 'full caller kernel and idle census')
    require(coefficient_max <= 3, 'literal coefficients fit retained scalar envelope')
    receipt = {'events': len(events), 'basis_gates': basis_gates, 'kernel_correction_adds': 21, 'ordinary_lambdas': 62, 'kernel_normalizers': 42, 'final_normalizers': 20, 'maximum_literal_scalar': str(coefficient_max), 'frame_returns_to_identity': True, 'frame_certificate_sha256': digest([[s['event'], s['frame']] for s in sites] + [[x['event'], x['frame']] for x in idles])}
    return sites, idles, receipt


def expected_site(stage):
    x, y = [F()] * N, [F()] * N
    if stage <= 9:
        i = stage - 1
        x[0] = y[0] = F(1)
        x[1 + i], y[1 + i] = F(1), F(-1)
        for j in range(i):
            x[1 + j] = F(2)
        support = set(range(i + 2))
    else:
        m = stage - 10
        x[0], y[0] = F(-1), F(1)
        x[10 + m] = y[10 + m] = F(1)
        for j in range(m + 1, 9):
            x[10 + j] = F(2)
        support = {0, *range(10 + m, 19)}
    return x, y, support


def check_inactive(phi, gamma, site):
    """Both image and dual, on both columns of the actual native active plane."""
    require(dot(gamma, phi) == 1, 'unit dual idle line')
    for coordinate in (site['dst'], site['src']):
        require(dot(site['frame'][coordinate], phi) == 0, 'idle image meets actual native active plane')
        require(dot(gamma, column(site['back'], coordinate)) == 0, 'idle dual meets actual native active plane')


def carrier_in_frame(idle, site):
    image = [dot(row, idle['phi']) for row in site['frame']]
    dual = [dot(idle['gamma'], column(site['back'], j)) for j in range(N)]
    carriers = [j for j in range(N) if image == unit(j) and dual == unit(j)]
    require(len(carriers) == 1, 'one physical carrier with both unit image and dual')
    return carriers[0]


def check_field_geometry(sites, idles):
    full = {s['stage']: s for s in sites if s['stage'] is not None}
    for stage, site in full.items():
        x, y, _ = expected_site(stage)
        require((site['x'], site['y']) == (x, y), 'actual full-site field coupling')
    thin = [s for s in sites if s['stage'] is None]
    for site, (a, u, p, q) in zip(thin, [(0, 1, 0, 1), (-1, 2, 1, 0), (-1, 3, 1, -1)]):
        x = [F(a)] + [F(a + 1)] * 9 + [F(1 - a)] * 9 + [F(q)]
        y = [F(u)] + [F((1 - u) * (-1) ** j) for j in range(9)] + [F((u - 1) * (-1) ** (8 - j)) for j in range(9)] + [F(p)]
        require((site['x'], site['y']) == (x, y), 'actual thin-site field coupling')
    expected = [(j, -2, list(range(j + 1, 10)), j + 1, j + 1) for j in range(1, 9)]
    expected += [(11 + j, 2, list(range(10, 11 + j)), 10, 2 + j) for j in range(8)]
    for idle, (logical_role, coefficient, stages, host, role) in zip(idles, expected):
        phi, gamma = unit(logical_role), unit(logical_role)
        gamma[0] = F(coefficient)
        require((idle['phi'], idle['gamma'], idle['stages'], idle['host_stage'], idle['role']) == (phi, gamma, stages, host, role), 'literal idle line, dual, stages and insertion point')
    for i, idle in enumerate(idles):
        for j, other in enumerate(idles):
            require(dot(idle['gamma'], other['phi']) == int(i == j), 'mutually orthogonal idle projectors')
    incidences, transitions, records = 0, [], []
    for idle in idles:
        covered = [full[s] for s in idle['stages']]
        require(all(a['event'] < b['event'] for a, b in zip(covered, covered[1:])), 'chronological stage cover')
        encountered = [s for s in sites if covered[0]['event'] <= s['event'] <= covered[-1]['event']]
        require([s['stage'] for s in encountered] == idle['stages'], 'cover crosses no thin query or uncovered native kernel')
        carriers = []
        for site in covered:
            check_inactive(idle['phi'], idle['gamma'], site)
            carriers.append(carrier_in_frame(idle, site))
            incidences += 1
        require(carriers[0] == idle['role'], 'paid job uses first covered physical carrier')
        host = covered[0]
        require(host['event'] + 4 <= idle['event'] and not any(host['event'] < s['event'] < idle['event'] for s in sites), 'idle follows its host kernel before another kernel')
        host_transition = multiply(idle['frame'], host['back'])
        require(column(host_transition, carriers[0]) == unit(idle['role']) and host_transition[idle['role']] == unit(carriers[0]), 'actual host-to-idle ordinary segment preserves carrier and dual')
        for a, b, old, new in zip(covered, covered[1:], carriers, carriers[1:]):
            transition = multiply(b['frame'], a['back'])
            require(column(transition, old) == unit(new), 'ordinary transition preserves carrier image')
            require(transition[new] == unit(old), 'ordinary transition preserves carrier dual')
            transitions.append([idle['event'], a['stage'], b['stage'], old, new])
        records.append({'event': idle['event'], 'paid_register': idle['role'], 'stages': idle['stages'], 'phi': sparse(idle['phi']), 'gamma': sparse(idle['gamma']), 'carrier_registers_at_covered_sites': carriers})
    for stage, site in full.items():
        reconstructed = deepcopy(site['active'])
        for idle in idles:
            if stage in idle['stages']:
                e = outer(idle['phi'], idle['gamma'])
                reconstructed = [[x + y for x, y in zip(row, extra)] for row, extra in zip(reconstructed, e)]
        _, _, support = expected_site(stage)
        desired = [[F(i == j and i in support) for j in range(N)] for i in range(N)]
        require(reconstructed == desired, 'actual active plane plus idles equals stage support')
    require(incidences == 72 and len(transitions) == 56, 'complete covered-site incidence census')
    require(sum(r[3] != r[4] for r in transitions) == 28, 'right-side carriers genuinely change registers')
    return {'full_sites': 18, 'thin_sites': 3, 'idle_lines': len(idles), 'covered_line_site_incidences': incidences, 'carrier_transitions': len(transitions), 'transitions_changing_register': 28, 'unit_row_and_column_checks': 2 * len(transitions), 'host_to_idle_transports': len(idles), 'no_uncovered_kernel_crossed': True, 'stage_support_decompositions': len(full), 'idle_records': records, 'carrier_transition_records': transitions}


def selected_axes(stages):
    require(stages and len(stages) == len(set(stages)), 'repeated stage cannot be assigned fresh Gaussian rank')
    require(all(isinstance(s, int) and 1 <= s <= 18 for s in stages), 'fresh stage range')
    return [9 + 8 * (s - 1) + j for s in stages for j in range(8)]


def adapter(selected):
    require(len(selected) == len(set(selected)) and all(0 <= a < DIMENSION for a in selected), 'distinct Gaussian axes')
    selected_set, destination = set(selected), set(range(len(selected)))
    exchanges = list(zip(sorted(selected_set - destination), sorted(destination - selected_set)))
    permutation = list(range(DIMENSION))
    for a, b in exchanges:
        permutation[a], permutation[b] = permutation[b], permutation[a]
    return permutation, exchanges


def check_lowering(selected, rank, incoming, outgoing, global_phase=0, f=1):
    """Exact Fourier monomial equality, not exponential sample columns.

    Positive coordinate Gaussians have a linear mod-4 phase polynomial.
    Check its constant and every coefficient, plus the full net permutation.
    """
    require(rank == len(selected) and rank > 0, 'Gaussian address rank is axis count, not field-space rank')
    require(f >= 1, 'positive tensor multiplicity')
    require(sorted(incoming) == sorted(outgoing) == list(range(DIMENSION)), 'complete coordinate permutations')
    require(all(outgoing[incoming[a]] == a for a in range(DIMENSION)), 'both whole-job adapters restore every spectator')
    require(global_phase % 4 == 0, 'absolute phase at zero Fourier character')
    pin = [incoming[a] * f + j for a in range(DIMENSION) for j in range(f)]
    pout = [outgoing[a] * f + j for a in range(DIMENSION) for j in range(f)]
    require(all(pout[pin[a]] == a for a in range(DIMENSION * f)), 'complete block-adapter inverse at f')
    actual = [int(pin[a] < rank * f) for a in range(DIMENSION * f)]
    wanted_axes = {axis * f + j for axis in selected for j in range(f)}
    require(actual == [int(a in wanted_axes) for a in range(DIMENSION * f)], 'every Fourier phase coefficient of whole positive job')


def check_jobs(idles):
    histogram, rows, exchanges_per_port = Counter(), [], 0
    for idle in idles:
        axes = selected_axes(idle['stages'])
        rank = len(axes)
        permutation, exchanges = adapter(axes)
        for f in (1, 2, 3):
            check_lowering(axes, rank, permutation, permutation, f=f)
        histogram[rank] += PORTS
        exchanges_per_port += 2 * len(exchanges)
        rows.append({'event': idle['event'], 'rank': rank, 'register': idle['role'], 'exchanges_per_boundary': len(exchanges), 'exchanges': exchanges})
    require(histogram == {rank: 208 for rank in range(8, 65, 8)}, 'one whole job on each actual owner and port')
    require(exchanges_per_port * PORTS == 100464, 'complete two-boundary idle exchange recount')
    return {'paid_jobs': sum(histogram.values()), 'paid_histogram': dict(sorted(histogram.items())), 'address_rank_mass': sum(k * v for k, v in histogram.items()), 'two_axis_exchanges': exchanges_per_port * PORTS, 'ordinary_exchange_rate_inherited': 1000, 'idle_adapter_work': exchanges_per_port * PORTS * 1000, 'extra_field_space_wrappers': 0, 'new_owned_fields': 0, 'new_productive_credit': 0, 'checked_multiplicities': [1, 2, 3], 'all_positive_multiplicities': 'proved in PROOF.md; finite f checks are corroboration', 'jobs': rows}


def expect_rejection(action, label):
    try:
        action()
    except ValueError as error:
        return str(error)
    raise ValueError('negative control unexpectedly accepted: ' + label)


def controls(word, sites, idles):
    results, first = {}, idles[0]
    full = {s['stage']: s for s in sites if s['stage'] is not None}
    site = full[first['stages'][0]]
    wrong_dual = [x + y for x, y in zip(first['gamma'], site['y'])]
    require(dot(wrong_dual, first['phi']) == 1, 'dual mutation still fixes same image line')
    results['same_line_wrong_dual'] = expect_rejection(lambda: check_inactive(first['phi'], wrong_dual, site), 'same line, wrong dual')
    results['move_idle_across_uncovered_active_site'] = expect_rejection(lambda: check_inactive(first['phi'], first['gamma'], full[1]), 'uncovered site')
    results['repeated_stage'] = expect_rejection(lambda: selected_axes(first['stages'] + first['stages'][:1]), 'repeated stage')
    axes = selected_axes(first['stages'])
    permutation, _ = adapter(axes)
    results['scalar_coupling_rank_used_as_gaussian_rank'] = expect_rejection(lambda: check_lowering(axes, 1, permutation, permutation), 'rank confusion')
    results['missing_input_adapter'] = expect_rejection(lambda: check_lowering(axes, len(axes), list(range(DIMENSION)), permutation), 'output-only adapter')
    results['missing_output_adapter'] = expect_rejection(lambda: check_lowering(axes, len(axes), permutation, list(range(DIMENSION))), 'input-only adapter')
    results['wrong_global_phase'] = expect_rejection(lambda: check_lowering(axes, len(axes), permutation, permutation, global_phase=1), 'absolute phase')
    wrong = deepcopy(word)
    wrong['events'][first['event']][1] = 1
    def wrong_role():
        a, b, _ = parse_frames(wrong)
        check_field_geometry(a, b)
    results['idle_on_native_register'] = expect_rejection(wrong_role, 'wrong literal physical role')
    wrong_frame = deepcopy(word)
    wrong_frame['events'][0][-1] = '-2'
    def broken_frame():
        a, b, _ = parse_frames(wrong_frame)
        check_field_geometry(a, b)
    results['corrupt_ordinary_basis_gate'] = expect_rejection(broken_frame, 'ordinary frame corruption')
    changed = next(r for r in check_field_geometry(sites, idles)['carrier_transition_records'] if r[3] != r[4])
    _, before, after, old, _ = changed
    transition = multiply(full[after]['frame'], full[before]['back'])
    results['assume_one_unchanging_physical_register'] = expect_rejection(lambda: require(column(transition, old) == unit(old) and transition[old] == unit(old), 'right-chain carrier is routed to a different register'), 'unchanging physical register')
    return results


def run():
    hashes = source_check()
    word = json.loads((HERE / 'retained/CALLER.json').read_text())
    sites, idles, literal = parse_frames(word)
    geometry, jobs = check_field_geometry(sites, idles), check_jobs(idles)
    negative = controls(word, sites, idles)
    census = Counter(e[0] for e in word['events'])
    require(census == {'ADD': 690, 'SWAP': 393, 'LAMBDA': 62, 'SCALE': 55, 'LOCAL': 18, 'IDLE_ONE': 16, 'QUERY': 3}, 'literal gate census')
    envelope = 32 * N * PORTS * len(word['events'])
    require(envelope == 82334720, 'paid ordinary caller envelope')
    return {'schema': 'p104-chain-idle-applicability/1', 'status': 'PASS_CHAIN_IDLE_APPLICABILITY', 'base_commit': BASE, 'audited_chain_head': HEAD, 'kappa_effect': 'No new κ', 'scope': 'Conditional finite whole-idle lowering and carrier transport only; not complete supplier, compiler, native all-column or outer-theorem admission.', 'source_sha256': hashes, 'literal': dict(literal, event_census=dict(sorted(census.items())), caller_ordinary_envelope=envelope), 'field_geometry': geometry, 'whole_jobs': jobs, 'negative_controls': negative, 'assumptions_retained': ['native_all_columns', 'owned_erasure', 'compiler', 'precision_tape', 'analytic_recovery']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path, help='write complete deterministic receipt')
    parser.add_argument('--check', type=Path, help='compare complete frozen receipt')
    args = parser.parse_args()
    result = normalized(run())
    if args.check:
        require(json.loads(args.check.read_text()) == result, 'frozen result agrees with independent audit')
    if args.write:
        args.write.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': result['status'], 'idle_lines': result['field_geometry']['idle_lines'], 'covered_incidences': result['field_geometry']['covered_line_site_incidences'], 'carrier_transitions': result['field_geometry']['carrier_transitions'], 'paid_jobs': result['whole_jobs']['paid_jobs'], 'two_axis_exchanges': result['whole_jobs']['two_axis_exchanges'], 'negative_controls': len(result['negative_controls']), 'kappa_effect': result['kappa_effect']}, sort_keys=True))


if __name__ == '__main__':
    main()

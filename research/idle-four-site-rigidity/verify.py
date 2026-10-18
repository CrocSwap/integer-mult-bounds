#!/usr/bin/env python3
"""Exact finite hypotheses for the four-site theorem proved in PROOF.md.
Tekalign (@tekuuu), with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import random

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BASE = '463113d675af7410ac91d53a4fed51ec6494eb9a'
PREFIX = 'research/rank7-joint-endframes/allocation/vendor/'
INPUTS = {'template': PREFIX + 'TEMPLATE.json.gz', 'plan': PREFIX + 'PLAN.json.gz',
          'phases': 'research/adaptive-kernel-demotion/inputs/DATA-PHASES.json'}
EARLY, LATE = (8, 10), (12, 13)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def read_inputs(root=ROOT, manifest_path=PACKAGE / 'SOURCES.json'):
    manifest = json.loads(manifest_path.read_bytes())
    require(manifest['base_commit'] == BASE, 'base pin')
    pins = {x['path']: x for x in manifest['files'] if x['usage'] == 'input'}
    require(set(pins) == set(INPUTS.values()), 'complete input declarations')
    result = {}
    for key, relative in INPUTS.items():
        path = root / relative
        require(path.is_file() and not path.is_symlink(), 'missing or linked input')
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == pins[relative]['sha256'], 'source SHA256: ' + relative)
        blob = b'blob ' + str(len(raw)).encode() + b'\0' + raw
        require(hashlib.sha1(blob, usedforsecurity=False).hexdigest() == pins[relative]['git_blob'], 'source Git blob')
        result[key] = json.loads(gzip.decompress(raw) if relative.endswith('.gz') else raw)
    return result


def schedule_cut(template, plan):
    """Certify a fixed invariant coordinate subspace across the actual interval."""
    events = template['execution_schedule']
    local = {e['stage']: e for e in template['recipe'] if e['kind'] == 'local'}
    require(len(local) == 9 and set(local) == set(range(9)), 'nine local stages')
    sites = {}
    for i, event in enumerate(events):
        if event['kind'] == 'idle_cover_sweep':
            for side, child in enumerate(event['child_indices']):
                require(child not in sites, 'duplicate child event')
                sites[child] = (i, 2 * event['pair'] + side)
    require(all(c in sites for c in EARLY + LATE), 'missing changed child')
    start, end = sites[8][0], sites[12][0]
    require(sites[10][0] == start and sites[13][0] == end and start < end, 'two ordered idle events')
    early, late = [sites[c][1] for c in EARLY], [sites[c][1] for c in LATE]
    require(early == [6, 7] and late == [0, 1], 'changed physical streams')
    for c in EARLY + LATE:
        require(2 * plan['pairs'][str(c)] + plan['sides'][str(c)] == sites[c][1], 'plan/event physical stream mismatch')
    interval = []
    for index in range(start + 1, end):
        event = events[index]
        kind = event['kind']
        if kind == 'bridge':
            require(type(event['coefficient']) is int and event['coefficient'] in (-1, 1), 'invertible bridge alphabet')
            require(event['src'] != event['dst'], 'distinct bridge pairs')
            mixed = {2 * event[k] + side for k in ('src', 'dst') for side in (0, 1)}
        elif kind == 'local_cover_sweep':
            stage = local[event['stage']]
            require(type(stage['reverse']) is bool, 'F/B orientation')
            mixed = {2 * stage['pair'], 2 * stage['pair'] + 1}
        else:
            require(kind == 'idle_cover_sweep', 'unproved intervening operation')
            mixed = set()  # Nonzero diagonal phases preserve every coordinate cut.
        require(all(0 <= s < 8 for s in mixed), 'eight-stream domain')
        require(not mixed & set(late), 'late coordinate subspace is mixed')
        interval.append({'index': index, 'kind': kind, 'mixed_streams': sorted(mixed)})
    return {'early_event': start, 'late_event': end, 'early_streams': early,
            'late_streams': late, 'interval': interval}


def parity(a, b):
    return (a & b).bit_count() & 1


def binary_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            p = row.bit_length() - 1
            if p not in pivots:
                pivots[p] = row
                break
            row ^= pivots[p]
    return len(pivots)


def phase_signature(axes, dimension, translation=0):
    require(type(dimension) is int and dimension >= 1, 'positive dimension')
    require(type(translation) is int and 0 <= translation < 1 << dimension, 'translation domain')
    linear = [2 * ((translation >> j) & 1) for j in range(dimension)]
    polar = [0] * dimension
    for axis in axes:
        require(type(axis) is int and 0 < axis < 1 << dimension, 'axis domain')
        for j in range(dimension):
            if axis >> j & 1:
                linear[j] = (linear[j] + 1) % 4
                polar[j] ^= axis
    return {'linear_mod4': linear, 'polar_rows': polar}


def signature_value(s, x):
    return (sum(c for j, c in enumerate(s['linear_mod4']) if x >> j & 1)
            + 2 * sum(parity(row & ~((1 << (j + 1)) - 1), x)
                      for j, row in enumerate(s['polar_rows']) if x >> j & 1)) % 4


def direct_phase(axes, x, translation=0):
    return (sum(parity(v, x) for v in axes) + 2 * parity(translation, x)) % 4


def input_rank_certificate(recipes):
    require(len(recipes) == 112, 'complete port catalogue')
    signatures = []
    for port, recipe in enumerate(recipes):
        require(recipe['port'] == port, 'ordered unique port catalogue')
        for child in EARLY + LATE:
            entry = recipe['idle_children'][child]
            axes = list(map(int, entry['orthogonal_axes']))
            require(len(axes) == 48, 'source full child rank')
            require(all(parity(v, w) == int(i == j) for i, v in enumerate(axes)
                        for j, w in enumerate(axes)), 'source orthonormality')
            s = phase_signature(axes, 73, translation=int(entry['translation_after']))
            require(binary_rank(axes) == binary_rank(s['polar_rows']) == 48, 'phase recovers source rank')
            signatures.append([port, child, s])
    return {'ports': 112, 'child_positions': list(EARLY + LATE), 'full_axis_sets': len(signatures),
            'ranks_per_port': [48] * 4, 'signature_sha256': hashlib.sha256(canonical(signatures)).hexdigest(),
            'nonzero_character_signature_probes': 73 + 73 * 72 // 2}


def phase_controls():
    sets = checks = 0
    for n in range(1, 5):
        for size in range(n + 1):
            for axes in itertools.combinations(range(1, 1 << n), size):
                # Independent explicit-span oracle, distinct from binary elimination.
                span = {0}
                for a in axes:
                    span |= {x ^ a for x in span}
                if len(span) != 1 << size:
                    continue
                sets += 1
                s = phase_signature(axes, n)
                require(binary_rank(s['polar_rows']) == size, 'independent-set polar rank')
                for x in range(1 << n):
                    require(signature_value(s, x) == direct_phase(axes, x), 'quadratic phase identity')
                    checks += 1
    standard6 = [1 << j for j in range(6)]
    changed6 = [63 ^ a for a in standard6]
    require(phase_signature(standard6, 6) == phase_signature(changed6, 6), 'nontrivial basis positive control')
    require(all(direct_phase(standard6, x) == direct_phase(changed6, x) for x in range(64)), 'basis-change oracle')
    standard4 = [1 << j for j in range(4)]
    changed4 = [15 ^ a for a in standard4]
    a, b = phase_signature(standard4, 4), phase_signature(changed4, 4)
    require(a['polar_rows'] == b['polar_rows'] and a != b, 'polar-only false-positive control')
    require(direct_phase(standard4, 1) != direct_phase(changed4, 1), 'linear phase witness')
    require(a == phase_signature(changed4, 4, translation=15), 'translation repair preserves rank')
    require(phase_signature([1] * 4, 1) == phase_signature([], 1), 'dependent-axis boundary')
    require(binary_rank([1] * 4) != 4, 'independence is required')
    return {'independent_axis_sets': sets, 'all_character_checks': checks,
            'nontrivial_same_phase_basis_change': [standard6, changed6],
            'polar_only_false_positive': [standard4, changed4], 'translation_repair': 15,
            'dependent_axis_control': [1] * 4}


def rotate(z, k):
    a, b = z
    return ((a, b), (-b, a), (-a, -b), (b, -a))[k % 4]


def identity():
    return [[(int(i == j), 0) for j in range(8)] for i in range(8)]


def add_row(matrix, dst, src, coefficient):
    matrix[dst] = [(a + coefficient * c, b + coefficient * d)
                   for (a, b), (c, d) in zip(matrix[dst], matrix[src])]


def interval_matrix(template, cut, rng):
    matrix = identity()
    local = {e['stage']: e for e in template['recipe'] if e['kind'] == 'local'}
    for index in range(cut['early_event'] + 1, cut['late_event']):
        # Arbitrary invertible diagonal fixtures include frame/host phase effects.
        for row in range(8):
            k = rng.randrange(4)
            matrix[row] = [rotate(z, k) for z in matrix[row]]
        event = template['execution_schedule'][index]
        if event['kind'] == 'bridge':
            dst, src, c = event['dst'], event['src'], event['coefficient']
            add_row(matrix, 2 * dst, 2 * src, c)
            add_row(matrix, 2 * src + 1, 2 * dst + 1, -c)
        elif event['kind'] == 'local_cover_sweep':
            op = local[event['stage']]
            x, y = 2 * op['pair'], 2 * op['pair'] + 1
            add_row(matrix, x if op['reverse'] else y, y if op['reverse'] else x,
                    -1 if op['reverse'] else 1)
    return matrix


def phase_relation(matrix, changes):
    """Direct exact entry test of E_late M E_early = M."""
    early, late = {6: changes[0], 7: changes[1]}, {0: changes[2], 1: changes[3]}
    return all(rotate(matrix[i][j], late.get(i, 0) + early.get(j, 0)) == matrix[i][j]
               for i in range(8) for j in range(8))


def cut_controls(template, plan, cut):
    rng = random.Random(40)
    for _ in range(32):
        matrix = interval_matrix(template, cut, rng)
        solutions = [x for x in itertools.product(range(4), repeat=4) if phase_relation(matrix, x)]
        require(solutions == [(0, 0, 0, 0)], 'four independent phases are rigid')
    crossing = identity()
    crossing[0], crossing[6] = crossing[6], crossing[0]
    require(phase_relation(crossing, (3, 0, 1, 0)), 'crossing-cut positive transfer')
    require(phase_relation([[(0, 0)] * 8 for _ in range(8)], (1, 1, 1, 1)), 'singular boundary control')
    def rejected(t, p, message):
        try:
            schedule_cut(t, p)
        except ValueError as error:
            require(message in str(error), 'wrong rejecting rule: ' + str(error))
            return
        raise ValueError('mutated schedule accepted')
    clone = lambda x: json.loads(json.dumps(x))
    t = clone(template)
    t['execution_schedule'][cut['early_event'] + 1]['src'] = 0
    rejected(t, plan, 'late coordinate subspace is mixed')
    t = clone(template)
    next(e for e in t['recipe'] if e.get('stage') == 6)['pair'] = 0
    rejected(t, plan, 'late coordinate subspace is mixed')
    t = clone(template)
    t['execution_schedule'][cut['early_event'] + 1]['kind'] = 'erase'
    rejected(t, plan, 'unproved intervening operation')
    p = clone(plan)
    p['sides']['8'] ^= 1
    rejected(template, p, 'plan/event physical stream mismatch')
    t = clone(template)
    t['execution_schedule'].append(t['execution_schedule'][cut['early_event']])
    rejected(t, plan, 'duplicate child event')
    return {'seed': 40, 'diagonal_fixtures': 32, 'phase_tuples_per_fixture': 256,
            'nonidentity_tuples_rejected': 32 * 255, 'source_schedule_mutations_rejected': 5,
            'crossing_cut_transfer_accepted': True, 'singular_boundary_exhibited': True}


def calculate():
    x = read_inputs()
    cut = schedule_cut(x['template'], x['plan'])
    return {'base_commit': BASE, 'status': 'scoped-written-proof-with-exact-finite-hypotheses',
            'schedule_cut': cut, 'source_axes': input_rank_certificate(x['phases']['recipes']),
            'phase_controls': phase_controls(), 'cut_controls': cut_controls(x['template'], x['plan'], cut),
            'claim': 'Each of the four child ranks is invariant under operator-preserving independent-axis replacements with the remaining schedule fixed.',
            'new_kappa': False, 'formal_kernel_proof': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit-result', action='store_true')
    args = parser.parse_args()
    result = calculate()
    if args.emit_result:
        print(json.dumps(result, sort_keys=True, indent=2))
        return
    require(canonical(result) == canonical(json.loads((PACKAGE / 'RESULT.json').read_bytes())), 'stored result mismatch')
    print('PASS_IDLE_FOUR_SITE_RIGIDITY ports=112 axesets=448 full_recipe_ranks=48,48,48,48 phase_tuples=8192')


if __name__ == '__main__':
    main()

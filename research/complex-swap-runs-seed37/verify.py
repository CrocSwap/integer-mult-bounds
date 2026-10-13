"""Exact historical scalar SWAP-run construction. ToikY/Codex, Apache-2.0."""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import compiler
import independent_checker as independent

BASE = '007664306fff84fbb1c9a1b4053b69f439764034'
PROVIDERS = 'research/community-k492-audit/pr626/replay/mixed-global/base/providers/'
WORK = compiler.WORK
LOWER_PATH = 'research/complex-dyadic-lowering/lower.py'
INPUTS = [LOWER_PATH, 'research/complex-k492-owner-repair/code/hpe_emit_local.py',
          'research/complex-k492-owner-repair/code/construct_k_triangle.py',
          'docs/research/community-k492-review.md', 'docs/research/community-frontier890-review.md']
INPUTS += [PROVIDERS + p + '/' + f for p in ('ck', 'jp8')
           for f in ('LOCAL-PROGRAMS.json.gz', 'LOCAL-CHECKS.json', 'INDEPENDENT-LOCAL-REPLAY.json')]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def sources(root=ROOT):
    pins = read(HERE / 'SOURCES.json')
    require(pins['base_commit'] == BASE and set(pins['files']) == set(INPUTS), 'source inventory/base')
    for path, pin in pins['files'].items():
        resolved = (root / path).resolve()
        require(resolved.is_relative_to(root.resolve()) and resolved.is_file(), 'source path: ' + path)
        raw = resolved.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'source SHA256: ' + path)
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        require(blob == pin['git_blob'], 'source Git blob: ' + path)
    namespace = {'__name__': 'pinned_pr696'}
    exec(compile((root / LOWER_PATH).read_bytes(), LOWER_PATH, 'exec', optimize=0), namespace)
    return namespace['lower']


def step(rows, op):
    tag, target = op[0], tuple(op[1])
    require(target in rows, 'unknown primitive target')
    if tag == 'clear':
        rows[target] = {}
    elif tag == 'copy':
        source = tuple(op[2]); require(source in rows and source != target, 'copy source')
        rows[target] = rows[source].copy()
    elif tag in ('double', 'halve', 'negate'):
        q = {'double': Q(2), 'halve': Q(1, 2), 'negate': Q(-1)}[tag]
        rows[target] = {k: q * v for k, v in rows[target].items()}
    elif tag in ('add', 'subtract'):
        source = tuple(op[2]); require(source in rows and source != target, 'add source')
        sign = 1 if tag == 'add' else -1
        for k, v in rows[source].items():
            x = rows[target].get(k, Q(0)) + sign * v
            if x:
                rows[target][k] = x
            else:
                rows[target].pop(k, None)
    else:
        raise ValueError('unknown primitive tag')


def clear_elision(word, known_zero=False):
    """Only erase a CLEAR whose target is already proven zero in this word.

    Matches the stronger known-zero idea credited to PR839; no arithmetic or
    frame reordering. Copy/add/scale writes conservatively invalidate the fact.
    """
    result = []
    for op in word:
        if tuple(op[1]) == WORK:
            if op[0] == 'clear':
                if known_zero:
                    continue
                known_zero = True
            else:
                known_zero = False
        result.append(op)
    return result, known_zero


def direct_blocks(events, lower):
    return [{'start': a, 'end': b, 'frame': frame,
             'primitives': [primitive for e in events[a:b] for primitive in lower(e[1], WORK)]}
            for a, b, frame in compiler.scalar_runs(events)]


def elide_blocks(blocks):
    result, known_zero = [], False
    for block in blocks:
        word, known_zero = clear_elision(block['primitives'], known_zero)
        result.append(dict(block, primitives=word))
    return result


def replay(events, blocks, orientation):
    coordinates = [('L', r) for r in range(716)] + [('C', r) for r in range(8)] + [WORK]
    rows = {r: {i: Q(1)} for i, r in enumerate(coordinates)}
    peak, fractional_depth = Q(1), 0
    counts, stream = Counter(), hashlib.sha256()
    for block in blocks:
        for op in block['primitives']:
            step(rows, op)
            row = rows[tuple(op[1])]
            peak = max(peak, sum(abs(x) for x in row.values()))
            for x in row.values():
                d = x.denominator
                require(d > 0 and d & (d - 1) == 0, 'non-dyadic prefix')
                fractional_depth = max(fractional_depth, d.bit_length() - 1)
            counts[op[0]] += 1
            stream.update(canonical([block['frame'], op]) + b'\n')
        if any(e[1][0] == 'add' for e in events[block['start']:block['end']]):
            require(not rows[WORK], 'private work at frame/event boundary')
    for r in range(716):
        expected = {r: Q(1)}
        if orientation == 'forward' and 112 <= r < 224:
            expected[r - 112] = Q(1)
        if orientation == 'backward' and r < 112:
            expected[r + 112] = Q(-1)
        require(rows['L', r] == expected, 'persistent endpoint at ' + str(r))
    require(all(not rows[r] for r in coordinates if r[0] != 'L'), 'dirty private endpoint')
    return {'real_primitives': 2 * sum(counts.values()),
            'primitive_tags_per_component': dict(sorted(counts.items())),
            'primitive_word_sha256': stream.hexdigest(), 'prefix_row_l1': str(peak),
            'fractional_depth': fractional_depth, 'arbitrary_input_columns': len(coordinates),
            'dirty_helpers_restored': 492, 'private_columns_cleared': 9}


def controls(lower):
    a, b, c = ['L', 0], ['L', 1], ['L', 2]
    swap = [['scalar', ['add', a, b, 1, 1], 0],
            ['scalar', ['add', b, a, -1, 1], 0],
            ['scalar', ['add', a, b, 1, 1], 0],
            ['scalar', ['scale', b, -1, 1], 0]]
    events = swap + [['scalar', ['add', c, a, 3, 2], 0]] + swap
    block = compiler.compile_block(events, 0, len(events), lower)
    independent.check_block(events, 0, len(events), block['primitives'])
    # A non-involutive three-cycle checks which direction gets materialized.
    perm = {tuple(a): tuple(b), tuple(b): tuple(c), tuple(c): tuple(a)}
    word, cycles = compiler.materialize(perm)
    independent.check_replacement({'permutation': tuple(perm.items())}, word)
    rejected = []
    mutants = {
        'missing_final_clear': None,
        'unremapped_intervening_read': lower(['add', c, a, 3, 2], WORK) + [('clear', WORK)],
        'missing_intervening_update': [('clear', WORK)],
    }
    for name, bad in mutants.items():
        control_events = events
        if name == 'missing_final_clear':
            control_events = swap + swap
            bad = []
        try:
            independent.check_block(control_events, 0, len(control_events), bad)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('accepted mutant ' + name)
    altered = json.loads(json.dumps(swap))
    altered[1][2] = 1
    require(compiler.swapped_pair(altered, 0) is None, 'mixed-frame swap accepted')
    require(len(compiler.scalar_runs(swap[:2] + [['phase', 'barrier']] + swap[2:])) == 2,
            'non-scalar barrier crossed')
    require(compiler.swapped_pair(swap + swap, 0) == (tuple(a), tuple(b)), 'positive swap')
    cancelled = compiler.compile_block(swap + swap, 0, 8, lower)
    require(cancelled['primitives'] == [('clear', WORK)], 'identity permutation dirty-work clear')
    independent.check_block(swap + swap, 0, 8, cancelled['primitives'])
    return {'rejected': rejected + independent.negative_controls(),
            'positive': ['intervening_remapped_fraction', 'three_cycle_direction', 'cancelled_swaps_dirty_work'],
            'barriers': ['mixed_frame_rejected', 'non_scalar_stops_run'],
            'independent_block_controls': independent.block_controls()}


def run(root=ROOT):
    lower = sources(root)
    results, candidates = {}, {}
    for provider in ('jp8', 'ck'):  # Seed37 diversified provider/report ordering.
        directory = root / PROVIDERS / provider
        programs, checks = read(directory / 'LOCAL-PROGRAMS.json.gz'), read(directory / 'LOCAL-CHECKS.json')
        require(set(programs) == {'forward', 'backward'}, 'orientation inventory')
        for orientation in ('forward', 'backward'):
            events = programs[orientation]
            require(hashlib.sha256(canonical(events)).hexdigest() == checks[orientation]['sha256'], 'program semantic hash')
            scalar_count = sum(e[0] == 'scalar' for e in events)
            source_bill = 0
            for e in events:
                if e[0] != 'scalar':
                    continue
                op = e[1]
                if op[0] in ('clear', 'copy'):
                    source_bill += 2
                else:
                    q = Q(*op[3:5]) if op[0] == 'add' else Q(*op[2:4])
                    a, b = abs(q.numerator), q.denominator
                    per_component = (3 + a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1) if op[0] == 'add' else (abs(a.bit_length() - b.bit_length()) + int(q < 0))
                    source_bill += 2 * per_component
            require(source_bill == checks[orientation]['real_component_primitive_bound'], 'original Horner source bill')
            require(scalar_count == checks[orientation]['scalar_macros'], 'macro count')
            paid = Counter()
            for e in events:
                if e[0] == 'climb': paid[e[5]] += 1
                elif e[0] == 'center': paid[e[4]] += 1
                else: require(e[0] in ('scalar', 'phase', 'adapter', 'residual_adapter'), 'event kind')
            require(dict(paid) == {int(k): v for k, v in checks[orientation]['paid_profile'].items()}, 'paid profile')
            original = direct_blocks(events, lower)
            compiled = compiler.compile_program(events, lower)
            require(compiler.scalar_runs(events) == [(z['start'], z['end'], z['frame']) for z in independent.scalar_runs(events)], 'independent run partition')
            changed = [z for z in compiled if z['swap_starts']]
            complete_independent_swaps = [i for i in range(len(events) - 3) if independent.recognize(events, i) is not None]
            require(complete_independent_swaps == [i for z in changed for i in z['swap_starts']], 'independent complete swap coverage')
            local = []
            for block in changed:
                found = [i for i in range(block['start'], block['end']) if independent.recognize(events, i) is not None and i + 4 <= block['end']]
                require(found == block['swap_starts'], 'independent exhaustive swap census')
                local.append(independent.check_block(events, block['start'], block['end'], block['primitives']))
            versions = {'pr696': original, 'pr696_known_zero': elide_blocks(original),
                        'deferred': compiled, 'deferred_known_zero': elide_blocks(compiled)}
            receipts = {name: replay(events, words, orientation) for name, words in versions.items()}
            require(Q(receipts['deferred']['prefix_row_l1']) <= Q(receipts['pr696']['prefix_row_l1']), 'whole prefix growth')
            require(receipts['deferred']['fractional_depth'] == receipts['pr696']['fractional_depth'], 'whole fractional depth changed')
            require(Q(receipts['deferred_known_zero']['prefix_row_l1']) <= Q(receipts['pr696_known_zero']['prefix_row_l1']), 'strong prefix growth')
            gain = receipts['pr696']['real_primitives'] - receipts['deferred']['real_primitives']
            strong_gain = receipts['pr696_known_zero']['real_primitives'] - receipts['deferred_known_zero']['real_primitives']
            require(gain > 0 and strong_gain > 0, 'no strict paid circuit gain')
            key = provider + '/' + orientation
            results[key] = {'receipts': receipts, 'saved_against_pr696': gain,
                            'additional_saved_after_known_zero_elision': strong_gain,
                            'scalar_runs': len(compiled), 'changed_runs': len(changed),
                            'swaps_elided': sum(len(z['swap_starts']) for z in changed),
                            'cycles_materialized': sum(len(z['cycles']) for z in changed),
                            'independent_changed_block_checks': local,
                            'paid_profile_unchanged': {str(k): v for k, v in sorted(paid.items())}}
            candidates[key] = [{k: v for k, v in z.items() if k != 'primitives'} for z in changed]
    return {'status': 'PASS_DEFERRED_SWAP_SCALAR', 'base_commit': BASE, 'assignment_seed': 37,
            'programs': results, 'candidate_blocks': candidates, 'controls': controls(lower),
            'scope': 'Historical PR626 scalar projections only; no new kappa or physical admission.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='write verified receipt to a NEW file')
    args = parser.parse_args()
    result = run()
    require(canonical(result) == canonical(read(HERE / 'EXPECTED.json')), 'typed full receipt mismatch')
    if args.output:
        with args.output.open('x') as handle:
            handle.write(json.dumps(result, indent=2, sort_keys=True) + '\n')
    gains = ','.join(str(z['additional_saved_after_known_zero_elision']) for z in result['programs'].values())
    print('PASS_DEFERRED_SWAP_SCALAR programs=4 columns=725 swaps=126_each extra_after_clear_elision=' + gains + ' no_new_kappa')

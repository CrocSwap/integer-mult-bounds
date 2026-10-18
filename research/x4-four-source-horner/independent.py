"""Independent finite X4 Horner census, forward DP, and integer-dyadic replay.

No constructor, inherited checker, or sibling implementation is imported.
Prepared for ToikY with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
W = ('W', 0)
INPUTS = HERE.parent / 'complex-x4-compensation-pairs' / 'inputs'
INPUT_HASHES = {
    'CANONICAL-WORD.json.gz': '1c0e9da767d4418f70016af599e4a447a3f7777acabe930318459c0fbbd260aa',
    'LOCAL-CHECKS.json': '4cca9475a0d9a93041696c570cbc8d91a40be76e63196a670256ce7e79521580',
    'LOCAL-PROGRAMS.json.gz': '223c2bb27ad68a4e9468c3ddaece1899d577b661190922fdd25f5976052c4cab',
}


def demand(condition, explanation):
    if not condition:
        raise ValueError(explanation)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def load_inputs(root=None):
    location = Path(root) if root is not None else INPUTS
    data = {}
    for name, expected in INPUT_HASHES.items():
        raw = (location / name).read_bytes()
        data[name] = json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw)
        demand(digest(data[name]) == expected, 'immutable input mismatch: ' + name)
    return data['LOCAL-PROGRAMS.json.gz'], data['CANONICAL-WORD.json.gz'], data['LOCAL-CHECKS.json']


def dyadic(num, den):
    demand(type(num) is int and type(den) is int and den != 0, 'invalid scalar')
    if den < 0:
        num, den = -num, -den
    g = math.gcd(abs(num), den)
    num, den = num // g, den // g
    demand(num != 0 and den & (den - 1) == 0, 'not a nonzero dyadic')
    return num, den.bit_length() - 1


def lower_baseline(scalar):
    """PR696 binary expansion independently spelled as primitive instructions."""
    tag, dst = scalar[0], tuple(scalar[1])
    demand(dst != W, 'coefficient work aliases scalar destination')
    if tag == 'copy':
        demand(tuple(scalar[2]) != W, 'coefficient work aliases scalar source')
        return [('copy', dst, tuple(scalar[2]))]
    if tag == 'clear':
        return [('clear', dst)]
    if tag == 'scale':
        num, exp = dyadic(*scalar[2:4])
        magnitude = abs(num)
        demand(magnitude & (magnitude - 1) == 0, 'nonbinary scale')
        shift = magnitude.bit_length() - 1 - exp
        result = [('double' if shift > 0 else 'halve', dst)] * abs(shift)
        if num < 0:
            result.append(('negate', dst))
        return result
    demand(tag == 'add' and tuple(scalar[2]) not in (dst, W), 'invalid additive macro')
    src = tuple(scalar[2])
    num, exp = dyadic(*scalar[3:5])
    magnitude = abs(num)
    if magnitude == 1 and exp == 0:
        return [('add' if num > 0 else 'subtract', dst, src), ('clear', W)]
    result = [('copy', W, src)]
    for digit in reversed(range(magnitude.bit_length() - 1)):
        result.append(('double', W))
        if magnitude & (1 << digit):
            result.append(('add', W, src))
    result.extend([('halve', W)] * exp)
    result.extend([('add' if num > 0 else 'subtract', dst, W), ('clear', W)])
    return result


def eligible(window):
    if not 2 <= len(window) <= 4:
        return False
    if any(event[0] != 'scalar' or event[1][0] != 'add' for event in window):
        return False
    frame = window[0][2]
    dst = window[0][1][1]
    sources = [tuple(event[1][2]) for event in window]
    return (frame != 0 and all(event[2] == frame and event[1][1] == dst for event in window)
            and len(set(sources)) == len(window) and tuple(dst) not in sources and W not in sources
            and tuple(dst) != W)


def lower_joint(window):
    """Shared signed binary Horner, overwriting W and charging its final clear."""
    demand(eligible(window), 'window outside the frozen class')
    scalars = [event[1] for event in window]
    coeff = [dyadic(*scalar[3:5]) for scalar in scalars]
    exp = max(pair[1] for pair in coeff)
    integers = [num << (exp - e) for num, e in coeff]
    top = max(abs(n).bit_length() for n in integers) - 1
    initial = next(i for i, n in enumerate(integers) if abs(n) & (1 << top))
    sign = 1 if integers[initial] > 0 else -1
    result = [('copy', W, tuple(scalars[initial][2]))]
    for digit in range(top, -1, -1):
        if digit != top:
            result.append(('double', W))
        for i, (num, scalar) in enumerate(zip(integers, scalars)):
            if digit == top and i == initial:
                continue
            if abs(num) & (1 << digit):
                result.append(('add' if num * sign > 0 else 'subtract', W, tuple(scalar[2])))
    result.extend([('halve', W)] * exp)
    result.extend([('add' if sign > 0 else 'subtract', tuple(scalars[0][1]), W), ('clear', W)])
    return result


def census(events, max_sources=4):
    demand(max_sources in (2, 3, 4), 'invalid fan-in')
    result = []
    for start in range(len(events)):
        for size in range(2, max_sources + 1):
            window = events[start:start + size]
            if len(window) != size or not eligible(window):
                continue
            old = sum(len(lower_baseline(event[1])) for event in window)
            new = len(lower_joint(window))
            result.append([start, size, old, new, old - new])
    return result


def select_forward(events, candidates):
    """Prefix dynamic program; tie policy intentionally independent of suffix DP."""
    ending = {}
    for start, size, before, after, saving in candidates:
        demand(saving == before - after, 'inconsistent candidate')
        if saving > size - 1:
            ending.setdefault(start + size, []).append((start, size, saving))
    scores = [0] * (len(events) + 1)
    predecessor = [None] * (len(events) + 1)
    for end in range(1, len(events) + 1):
        scores[end] = scores[end - 1]
        predecessor[end] = (end - 1, None)
        for start, size, saving in ending.get(end, []):
            proposed = scores[start] + saving
            if proposed > scores[end]:
                scores[end] = proposed
                predecessor[end] = (start, [start, size])
    selected, end = [], len(events)
    while end:
        end, window = predecessor[end]
        if window is not None:
            selected.append(window)
    selected.reverse()
    return scores[-1], selected


def check_recipe(events, recipe, candidates=None, require_optimal=True):
    candidates = census(events) if candidates is None else candidates
    by_window = {(row[0], row[1]): row for row in candidates}
    previous_end, saving = 0, 0
    for entry in recipe:
        demand(isinstance(entry, (list, tuple)) and len(entry) == 2
               and all(type(x) is int for x in entry), 'invalid recipe entry')
        start, size = entry
        demand(start >= previous_end, 'overlapping or unsorted recipe')
        demand((start, size) in by_window, 'ineligible recipe window')
        row = by_window[start, size]
        demand(row[4] > size - 1, 'does not beat redundant clears alone')
        saving += row[4]
        previous_end = start + size
    optimum, _ = select_forward(events, candidates)
    if require_optimal:
        demand(saving == optimum, 'recipe is not optimal in the finite window class')
    return saving


# A row is (denominator exponent, sparse integer numerators). Each operation
# allocates a new row: shallow state copies are safe for boundary comparison.
def row(exp, entries):
    entries = {k: n for k, n in entries.items() if n}
    if not entries:
        return 0, {}
    if exp:
        cancel = min(exp, min((abs(n) & -abs(n)).bit_length() - 1 for n in entries.values()))
        if cancel:
            entries = {k: n >> cancel for k, n in entries.items()}
            exp -= cancel
    return exp, entries


def add_rows(left, right, sign=1):
    exponent = max(left[0], right[0])
    values = {k: n << (exponent - left[0]) for k, n in left[1].items()}
    shift = exponent - right[0]
    for k, n in right[1].items():
        values[k] = values.get(k, 0) + sign * (n << shift)
    return row(exponent, values)


def scalar_pair(num, exp):
    if num == 0:
        return (0, 0)
    cancel = min(exp, (abs(num) & -abs(num)).bit_length() - 1)
    return num >> cancel, exp - cancel


def add_pairs(left, right):
    exp = max(left[1], right[1])
    return scalar_pair((left[0] << (exp - left[1])) + (right[0] << (exp - right[1])), exp)


def larger(left, right):
    return (left[0] << right[1]) > (right[0] << left[1])


def execute(state, op):
    tag, dst = op[:2]
    if tag == 'clear':
        state[dst] = (0, {})
    elif tag == 'copy':
        state[dst] = state[op[2]]
    elif tag in ('add', 'subtract'):
        state[dst] = add_rows(state[dst], state[op[2]], 1 if tag == 'add' else -1)
    elif tag == 'double':
        exp, values = state[dst]
        state[dst] = (exp - 1, values) if exp else (0, {k: n * 2 for k, n in values.items()})
    elif tag == 'halve':
        exp, values = state[dst]
        state[dst] = row(exp + 1, values)
    elif tag == 'negate':
        exp, values = state[dst]
        state[dst] = exp, {k: -n for k, n in values.items()}
    else:
        raise ValueError('unknown primitive ' + str(tag))


def replay(events, selected=None, orientation='backward', logical_count=728, width=112):
    demand(orientation in ('forward', 'backward'), 'unknown orientation')
    selected = [] if selected is None else selected
    if selected:
        check_recipe(events, selected, require_optimal=False)
    starts = dict(selected)
    keys = [('L', i) for i in range(logical_count)] + [('C', i) for i in range(8)] + [W]
    state = {key: (0, {i: 1}) for i, key in enumerate(keys)}
    envelope = {key: (1, 0) for key in keys}
    exact_peak = envelope_peak = (1, 0)
    grid_exp = component_count = source_reads = nonwork_reads = operand_reads = boundaries = 0
    counts = Counter()
    stream = []
    index = 0

    def update(op, frame):
        nonlocal exact_peak, envelope_peak, grid_exp, component_count, source_reads, nonwork_reads, operand_reads
        tag, dst = op[:2]
        demand(dst in state and (len(op) == 2 or op[2] in state), 'unknown register')
        execute(state, op)
        if tag == 'clear':
            envelope[dst] = (0, 0)
        elif tag == 'copy':
            envelope[dst] = envelope[op[2]]
            operand_reads += 1
        elif tag in ('add', 'subtract'):
            envelope[dst] = add_pairs(envelope[dst], envelope[op[2]])
            operand_reads += 2
        elif tag == 'double':
            envelope[dst] = scalar_pair(2 * envelope[dst][0], envelope[dst][1])
            operand_reads += 1
        elif tag == 'halve':
            envelope[dst] = scalar_pair(envelope[dst][0], envelope[dst][1] + 1)
            operand_reads += 1
        elif tag == 'negate':
            operand_reads += 1
        if tag in ('copy', 'add', 'subtract') and dst == W and op[2] != W:
            source_reads += 1
        if tag in ('copy', 'add', 'subtract') and op[2] != W:
            nonwork_reads += 1
        exact = scalar_pair(sum(abs(n) for n in state[dst][1].values()), state[dst][0])
        if larger(exact, exact_peak):
            exact_peak = exact
        if larger(envelope[dst], envelope_peak):
            envelope_peak = envelope[dst]
        grid_exp = max(grid_exp, state[dst][0])
        counts[tag] += 1
        component_count += 1
        stream.append(['primitive', list(op), frame])

    while index < len(events):
        event = events[index]
        if index in starts:
            size = starts[index]
            window = events[index:index + size]
            shadow = dict(state)
            for entry in window:
                for op in lower_baseline(entry[1]):
                    execute(shadow, op)
            for op in lower_joint(window):
                update(op, event[2])
            demand(state == shadow, 'all-column window boundary mismatch at ' + str(index))
            boundaries += 1
            index += size
        else:
            if event[0] == 'scalar':
                for op in lower_baseline(event[1]):
                    update(op, event[2])
            else:
                stream.append(event)
            index += 1
    for i in range(logical_count):
        expected = {i: 1}
        if orientation == 'forward' and width <= i < 2 * width:
            expected[i - width] = 1
        if orientation == 'backward' and i < width:
            expected[i + width] = -1
        demand(state[('L', i)] == (0, expected), 'logical endpoint failure at ' + str(i))
    demand(all(state[key] == (0, {}) for key in keys[logical_count:]), 'private erasure failure')
    endpoint = [[list(key), exp, sorted(values.items())] for key, (exp, values) in state.items()]
    return {
        'component_primitives': component_count,
        'real_component_primitives': 2 * component_count,
        'primitive_histogram': dict(sorted(counts.items())),
        'source_reads_into_work': source_reads,
        'nonwork_source_reads': nonwork_reads,
        'operand_reads': operand_reads,
        'stream_sha256': digest(stream),
        'endpoint_sha256': digest(endpoint),
        'exact_prefix_l1': [exact_peak[0], 1 << exact_peak[1]],
        'positive_prefix_l1': [envelope_peak[0], 1 << envelope_peak[1]],
        'max_grid_exponent': grid_exp,
        'checked_columns': len(keys),
        'window_boundaries_checked': boundaries,
        'logical_endpoint_verified': True,
        'private_erasure_verified': True,
    }


def local_identity(window, replacement=None):
    """Compare on independent target/source/dirty-W coordinates, before context."""
    demand(eligible(window), 'ineligible local identity')
    keys = [tuple(window[0][1][1])] + [tuple(event[1][2]) for event in window] + [W]
    original = {key: (0, {i: 1}) for i, key in enumerate(keys)}
    changed = dict(original)
    for event in window:
        for op in lower_baseline(event[1]):
            execute(original, op)
    for op in lower_joint(window) if replacement is None else replacement:
        execute(changed, op)
    demand(original == changed, 'local arbitrary-input identity failed')


def adverse_controls(events, recipe):
    import copy

    def rejected(action, label):
        try:
            action()
        except ValueError:
            return
        raise ValueError('negative control accepted: ' + label)

    # The highest first digit is on the second source, with negative sign;
    # coefficients have unequal denominators and W starts arbitrarily dirty.
    coefficients = [(1, 8), (-9, 2), (3, 4), (-1, 1)]
    specimen = [['scalar', ['add', ['L', 0], ['L', i + 1], num, den], 7]
                for i, (num, den) in enumerate(coefficients)]
    local_identity(specimen)
    word = lower_joint(specimen)
    demand(word[0] == ('copy', W, ('L', 2)) and word[-2][0] == 'subtract',
           'signed high-digit control not exercised')
    half = next(i for i, op in enumerate(word) if op[0] == 'halve')
    mutants = {
        'omitted final clear': word[:-1],
        'omitted initial copy with dirty work': word[1:],
        'wrong global high-digit sign': word[:-2] + [('add', ('L', 0), W), word[-1]],
        'omitted halving': word[:half] + word[half + 1:],
    }
    for label, changed in mutants.items():
        rejected(lambda changed=changed: local_identity(specimen, changed), label)
    aliased = copy.deepcopy(specimen)
    aliased[0][1][2] = ['L', 0]
    rejected(lambda: lower_joint(aliased), 'target aliases source')
    duplicate = copy.deepcopy(specimen)
    duplicate[1][1][2] = duplicate[0][1][2]
    rejected(lambda: lower_joint(duplicate), 'duplicate source')
    shifted = copy.deepcopy(specimen)
    shifted[1][2] = 8
    rejected(lambda: lower_joint(shifted), 'frame change')
    rejected(lambda: check_recipe(events, []), 'suboptimal empty recipe')
    rejected(lambda: check_recipe(events, [recipe[0], recipe[0]]), 'overlapping recipe')
    return 9


def run(root=None, recipe=None):
    programs, word, checks = load_inputs(root)
    per_size, pair_score = {}, None
    for maximum in (2, 3, 4):
        cases = census(programs['backward'], maximum)
        gain, chosen = select_forward(programs['backward'], cases)
        per_size[str(maximum)] = {
            'eligible': len(cases), 'strictly_beyond_clear_only': sum(r[4] > r[1] - 1 for r in cases),
            'gain_component': gain, 'gain_real': 2 * gain,
            'selected': len(chosen), 'census_sha256': digest(cases),
        }
        if maximum == 2:
            pair_score = gain
    demand(pair_score * 2 == 13072, 'pair-only comparison changed')
    demand(gain * 2 == 22048, 'four-source optimum changed')
    if recipe is None:
        recipe = chosen
    check_recipe(programs['backward'], recipe, cases)
    for start, size, _before, _after, _saving in cases:
        local_identity(programs['backward'][start:start + size])
    results = {
        'census': per_size,
        'recipe_sha256': digest(recipe),
        'local_candidate_identities': len(cases),
        'adverse_controls_rejected': adverse_controls(programs['backward'], recipe),
        'backward_baseline': replay(programs['backward']),
        'backward_candidate': replay(programs['backward'], recipe),
        'forward_retained': replay(programs['forward'], orientation='forward'),
    }
    for orientation in ('forward', 'backward'):
        key = 'forward_retained' if orientation == 'forward' else 'backward_baseline'
        additions = [e[1] for e in programs[orientation] if e[0] == 'scalar' and e[1][0] == 'add']
        units = sum(dyadic(*op[3:5]) in ((1, 0), (-1, 0)) for op in additions)
        discount = 2 * (len(additions) + units)
        demand(results[key]['real_component_primitives'] + discount == checks[orientation]['real_component_primitive_bound'],
               'PR696 closed-form discount against inherited original invoice mismatch')
    demand(results['backward_baseline']['real_component_primitives'] -
           results['backward_candidate']['real_component_primitives'] == 22048,
           'emitted saving does not match interval optimum')
    demand(results['backward_candidate']['endpoint_sha256'] == results['backward_baseline']['endpoint_sha256'],
           'full endpoint digest mismatch')
    return results


def check_expected(results, expected):
    """Compare immutable receipt fields without importing the other checker."""
    def core(result):
        num, den = result['exact_prefix_l1']
        positive_num, positive_den = result['positive_prefix_l1']
        return {
            'exact_prefix_fraction_bits': result['max_grid_exponent'],
            'exact_prefix_row_l1': str(num) if den == 1 else str(num) + '/' + str(den),
            'positive_prefix_row_l1': str(positive_num) if positive_den == 1 else str(positive_num) + '/' + str(positive_den),
            'work_source_reads': result['source_reads_into_work'],
            'nonwork_source_reads': result['nonwork_source_reads'],
            'operand_reads': result['operand_reads'],
            'per_component_opcodes': result['primitive_histogram'],
            'per_component_primitives': result['component_primitives'],
            'real_component_primitives': result['real_component_primitives'],
        }
    before, after = results['backward_baseline'], results['backward_candidate']
    census_result = results['census']
    observed = {
        'before': core(before), 'after': core(after),
        'baseline_stream_sha256': before['stream_sha256'],
        'candidate_stream_sha256': after['stream_sha256'],
        'boundaries': after['window_boundaries_checked'],
        'recipe_sha256': results['recipe_sha256'],
        'candidate_counts': {
            '2': census_result['2']['eligible'],
            '3': census_result['3']['eligible'] - census_result['2']['eligible'],
            '4': census_result['4']['eligible'] - census_result['3']['eligible'],
        },
        'pair_only_saved_real': census_result['2']['gain_real'],
        'pair_only_windows': census_result['2']['selected'],
        'saved_real': census_result['4']['gain_real'],
        'extra_beyond_pairs_real': census_result['4']['gain_real'] - census_result['2']['gain_real'],
        'formal_columns': after['checked_columns'],
        'local_candidate_identities': results['local_candidate_identities'],
        'forward_retained_real': results['forward_retained']['real_component_primitives'],
    }
    for key, value in observed.items():
        demand(key in expected and canonical(value) == canonical(expected[key]),
               'independent receipt disagreement: ' + key)
    return len(observed)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', type=Path)
    parser.add_argument('--recipe', type=Path, help='JSON list of [start event index, length]')
    parser.add_argument('--out', type=Path, help='optional JSON result destination')
    parser.add_argument('--json', action='store_true', help='print detailed result JSON')
    args = parser.parse_args()
    expected = json.loads((HERE / 'EXPECTED.json').read_text())
    recipe = json.loads(args.recipe.read_text()) if args.recipe else expected['recipe']
    if isinstance(recipe, dict):
        recipe = recipe['recipe'] if 'recipe' in recipe else recipe['windows']
    results = run(args.inputs, recipe)
    if not args.recipe:
        check_expected(results, expected)
    if args.out:
        demand(not args.out.exists(), 'output already exists')
        args.out.write_text(json.dumps(results, indent=2, sort_keys=True) + '\n')
    if args.json:
        print(json.dumps(results, indent=2, sort_keys=True))
    print('PASS_X4_FOUR_SOURCE_INDEPENDENT pair_gain_real=13072 four_gain_real=22048 columns=737 no_new_kappa')


if __name__ == '__main__':
    main()

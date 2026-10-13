"""Independent exact dyadic-operator check of pinned CK sign normalization.

Ross Richardson, with substantial OpenAI Codex assistance. Apache-2.0.
Checks finite scalar runs, not the complete multiplication theorem. The row
interpreter uses no Fraction, production interpreter, or production run splitter.
The shared pinned predecessor lowering uses Fraction. Standard library only.
"""
import argparse
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROGRAM = ROOT / 'research/community-k492-audit/pr626/replay/mixed-global/base/providers/ck/LOCAL-PROGRAMS.json.gz'
PROGRAM_SHA256 = '854f17274092263dc25e60367f4cd0d29f60a8446becd17cc1883ebed7a97900'
LOWERING = ROOT / 'research/complex-dyadic-lowering/lower.py'
LOWERING_SHA256 = 'eb37d00063dc09323e9aca041d23da749ce17fbd71dade9aaf1c059cab0b9753'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalize(exponent, coefficients):
    """Canonical sparse integer row multiplied by 2**(-exponent)."""
    coefficients = {i: n for i, n in coefficients.items() if n}
    if not coefficients:
        return (0, ())
    powers = [(abs(n) & -abs(n)).bit_length() - 1 for n in coefficients.values()]
    common = min(powers)
    return (exponent - common,
            tuple(sorted((i, n >> common) for i, n in coefficients.items())))


def unsigned(row):
    exponent, coefficients = row
    if coefficients and coefficients[0][1] < 0:
        coefficients = tuple((i, -n) for i, n in coefficients)
    return exponent, coefficients


def registers(word):
    result = set()
    for op in word:
        tag = op[0]
        arity = 3 if tag in ('copy', 'add', 'subtract') else 2
        require(tag in ('clear', 'copy', 'add', 'subtract', 'double', 'halve', 'negate'),
                'unknown primitive')
        require(len(op) == arity, 'primitive arity')
        for reg in op[1:]:
            require(isinstance(reg, tuple) and len(reg) == 2, 'register encoding')
            result.add(reg)
    return result


def step(rows, op):
    tag, target = op[:2]
    exponent, coefficients = rows[target]
    if tag == 'clear':
        rows[target] = (0, ())
    elif tag == 'copy':
        rows[target] = rows[op[2]]
    elif tag == 'negate':
        rows[target] = (exponent, tuple((i, -n) for i, n in coefficients))
    elif tag in ('double', 'halve'):
        rows[target] = (exponent + (1 if tag == 'halve' else -1), coefficients) if coefficients else (0, ())
    elif tag in ('add', 'subtract'):
        other_exponent, other_coefficients = rows[op[2]]
        common_exponent = max(exponent, other_exponent)
        values = {i: n << (common_exponent - exponent) for i, n in coefficients}
        sign = 1 if tag == 'add' else -1
        for i, n in other_coefficients:
            values[i] = values.get(i, 0) + sign * (n << (common_exponent - other_exponent))
        rows[target] = normalize(common_exponent, values)
    else:
        raise ValueError('unknown primitive')


def norm(row):
    exponent, coefficients = row
    return sum(abs(n) for _, n in coefficients), exponent


def larger_norm(left, right):
    common = max(left[1], right[1])
    return left if left[0] << (common - left[1]) >= right[0] << (common - right[1]) else right


def norm_receipt(value):
    numerator, exponent = value
    while numerator and numerator % 2 == 0:
        numerator //= 2
        exponent -= 1
    return {'numerator': numerator << max(0, -exponent),
            'denominator': 1 << max(0, exponent)}


def compare(reference, candidate, exact_count=None):
    """All touched inputs are independent, including every private register.

    Besides the endpoint operator, check exact per-register prefix containment
    modulo sign. This implies preservation of each baseline absolute coefficient
    envelope for this run. Containment uses exact tuples, never digest equality.
    """
    touched = registers(reference)
    require(registers(candidate) <= touched, 'candidate introduced register')
    initial = {reg: (0, ((i, 1),)) for i, reg in enumerate(sorted(touched))}
    expected, actual = initial.copy(), initial.copy()
    seen = {reg: {unsigned(row)} for reg, row in initial.items()}
    reference_norm = candidate_norm = (1, 0) if touched else (0, 0)
    reference_denominator = candidate_denominator = 0
    for primitive in reference:
        step(expected, primitive)
        target = primitive[1]
        seen[target].add(unsigned(expected[target]))
        reference_norm = larger_norm(reference_norm, norm(expected[target]))
        reference_denominator = max(reference_denominator, expected[target][0])
    for primitive in candidate:
        step(actual, primitive)
        target = primitive[1]
        require(unsigned(actual[target]) in seen[target], 'prefix row outside signed baseline')
        candidate_norm = larger_norm(candidate_norm, norm(actual[target]))
        candidate_denominator = max(candidate_denominator, actual[target][0])
    require(actual == expected, 'full endpoint operator differs')
    if exact_count is not None:
        require(len(candidate) == exact_count, 'primitive count differs')
    return {'basis': len(touched), 'reference_norm': reference_norm,
            'candidate_norm': candidate_norm,
            'reference_denominator': reference_denominator,
            'candidate_denominator': candidate_denominator}


def split_events(events, lower):
    """Maximal consecutive scalar events at a single frame, independently split."""
    runs, current, frame, start = [], [], None, None
    for index, event in enumerate(events):
        is_scalar = event[0] == 'scalar'
        if start is not None and (not is_scalar or frame != event[2]):
            runs.append((start, index, frame, current))
            current, frame, start = [], None, None
        if is_scalar:
            if start is None:
                start, frame = index, event[2]
            current.extend(lower(event[1]))
    if start is not None:
        runs.append((start, len(events), frame, current))
    return runs


def controls(optimize):
    t, s = ('T', 0), ('S', 0)
    cases = {
        'omitted_boundary_flush': ([('negate', t)], [], None),
        'missed_source_sign_flip':
            ([('negate', s), ('add', t, s), ('negate', s)], [('add', t, s)], None),
        'lost_copy_sign':
            ([('negate', s), ('copy', t, s), ('negate', s)], [('copy', t, s)], None),
        # Keeping a negative sign through clear can be algebraically valid but
        # needlessly pays a subtraction and final negate instead of one add.
        'clear_reset_cost':
            ([('negate', t), ('clear', t), ('add', t, s)],
             [('clear', t), ('subtract', t, s), ('negate', t)], 2),
        'endpoint_neutral_prefix_growth':
            ([('add', t, s)], [('double', s), ('halve', s), ('add', t, s)], None),
    }
    rejected = {}
    for name, (reference, mutant, count) in cases.items():
        compare(reference, optimize(reference), count)
        try:
            compare(reference, mutant, count)
        except ValueError as error:
            rejected[name] = str(error)
        else:
            raise ValueError('accepted negative control: ' + name)
    require(rejected['clear_reset_cost'] == 'primitive count differs', 'clear control was not count-sensitive')
    require(rejected['endpoint_neutral_prefix_growth'] == 'prefix row outside signed baseline',
            'prefix control was not prefix-sensitive')
    # An ordinary frame change, a nonscalar boundary, and the end of the word
    # each independently require a flush. No production splitter is consulted.
    events = [['scalar', ['negate', t], 0], ['scalar', ['negate', t], 1],
              ['phase', 'barrier'], ['scalar', ['negate', t], 1]]
    runs = split_events(events, lambda op: [tuple(op)])
    require([(a, b, f) for a, b, f, _ in runs] == [(0, 1, 0), (1, 2, 1), (3, 4, 1)],
            'boundary splitter control')
    for _, _, _, word in runs:
        compare(word, optimize(word))
    rejected['boundary_segmentation'] = 'frame, nonscalar, and end boundaries retained'
    return rejected


def verify():
    payload = gzip.decompress(PROGRAM.read_bytes())
    require(hashlib.sha256(payload).hexdigest() == PROGRAM_SHA256, 'pinned program payload differs')
    programs = json.loads(payload)
    require(hashlib.sha256(LOWERING.read_bytes()).hexdigest() == LOWERING_SHA256, 'pinned lowering differs')
    lower = load(LOWERING, 'ck_independent_baseline_lowering').lower
    optimize = load(HERE / 'compile.py', 'ck_candidate_compiler').optimize_run
    require(set(programs) == {'forward', 'backward'}, 'program orientation set')
    results = {}
    for orientation in ('forward', 'backward'):
        runs = split_events(programs[orientation], lower)
        scalar_macros = sum(event[0] == 'scalar' for event in programs[orientation])
        require(sum(end - start for start, end, _, _ in runs) == scalar_macros, 'scalar event coverage')
        before = after = largest_columns = 0
        max_reference_norm = max_candidate_norm = (0, 0)
        max_reference_denominator = max_candidate_denominator = 0
        digest = hashlib.sha256()
        boundaries = hashlib.sha256()
        for start, end, frame, reference in runs:
            candidate = optimize(reference)
            checked = compare(reference, candidate)
            largest_columns = max(largest_columns, checked['basis'])
            max_reference_norm = larger_norm(max_reference_norm, checked['reference_norm'])
            max_candidate_norm = larger_norm(max_candidate_norm, checked['candidate_norm'])
            max_reference_denominator = max(max_reference_denominator, checked['reference_denominator'])
            max_candidate_denominator = max(max_candidate_denominator, checked['candidate_denominator'])
            before += len(reference)
            after += len(candidate)
            boundaries.update(json.dumps([start, end, frame], separators=(',', ':')).encode() + b'\n')
            for op in candidate:
                digest.update(json.dumps([frame, op], separators=(',', ':')).encode() + b'\n')
        results[orientation] = {
            'scalar_runs': len(runs),
            'scalar_macros': scalar_macros,
            'baseline_real_primitives': 2 * before,
            'candidate_real_primitives': 2 * after,
            'saved_real_primitives': 2 * (before - after),
            'largest_independent_input_basis': largest_columns,
            'max_run_basis_prefix_l1_reference': norm_receipt(max_reference_norm),
            'max_run_basis_prefix_l1_candidate': norm_receipt(max_candidate_norm),
            'max_run_basis_denominator_exponent_reference': max_reference_denominator,
            'max_run_basis_denominator_exponent_candidate': max_candidate_denominator,
            'primitive_word_sha256': digest.hexdigest(),
            'run_boundaries_sha256': boundaries.hexdigest(),
            'all_run_endpoint_operators_equal': True,
            'all_prefix_rows_contained_modulo_sign': True,
        }
    return {'status': 'PASS_CK_SIGN_INDEPENDENT', 'programs': results,
            'controls': controls(optimize)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    result = verify()
    if args.json:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        print('PASS_CK_SIGN_INDEPENDENT programs=2 controls=' + str(len(result['controls'])))

#!/usr/bin/env python3
"""Source-bound exact factory fusion and fresh complete raw-word admission.

Prepared for CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Reuses Alluri's PR681 validator and attributed PR622/626 native checkers.
The circuit search is not imported. No new kappa or selected-word admission.
"""
import argparse
import copy
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREDECESSOR = ROOT / 'research/complex-factory5-resynthesis'
BASE = 'f567884aeb8851b6e794af1184119a3bfbe1e631'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_pins():
    pins = read(HERE / 'SOURCE-PINS.json')
    require(pins['base_commit'] == BASE, 'wrong base commit')
    for rel, expected in pins['files'].items():
        path = ROOT / rel
        raw = path.read_bytes()
        if path.suffix == '.gz':
            raw = gzip.decompress(raw)
        require(hashlib.sha256(raw).hexdigest() == expected,
                'Source pin mismatch: ' + rel)
    return pins


def validate_gate_types(word):
    for e in word:
        require(isinstance(e, list) and e and e[0] in ('add', 'scale'),
                'invalid scalar gate')
        require(len(e) == (6 if e[0] == 'add' else 5), 'invalid gate arity')
        require(all(type(x) is int for x in e[1:-1]), 'non-integer gate field')
        require(isinstance(e[-1], list) and all(type(x) is int for x in e[-1]),
                'non-integer frame field')


def commute(a, b):
    if a[0] == b[0] == 'add':
        return a[1] != b[2] and b[1] != a[2]
    if a[0] == b[0] == 'scale':
        return True
    scale, add = (a, b) if a[0] == 'scale' else (b, a)
    return scale[1] not in add[1:3]


def replay_recipe(old, cert, inherited):
    """Check each splice, including every operation crossed by a moved gate."""
    word = copy.deepcopy(old)
    for step in cert['fusions']:
        indices, order = step['indices'], step['pair_order']
        require(len(indices) == 3 and all(type(x) is int for x in indices),
                'invalid fusion indices')
        i, j, k = indices
        require(0 <= i < j < k < len(word), 'fusion indices not ordered')
        require(len(order) == 2 and all(type(x) is int and 0 <= x < 3 for x in order)
                and len(set(order)) == 2, 'invalid pair order')
        triple = [word[x] for x in indices]
        require(all(e[0] == 'add' for e in triple), 'fusion is not an ADD triple')
        require(all(commute(word[j], word[x]) for x in range(i + 1, j)),
                'second gate crosses a dependency')
        require(all(commute(word[k], word[x]) for x in range(i + 1, k) if x != j),
                'third gate crosses a dependency')
        pair = [triple[x] for x in order]
        require(inherited.columns(triple) == inherited.columns(pair),
                'fusion changes the exact map')
        word = word[:i] + pair + [e for x, e in enumerate(word[i + 1:], i + 1)
                                 if x not in (j, k)]
        require(len(word) == step['gates'] and
                len(inherited.lowering(word)) == step['primitive_cost'],
                'fusion accounting mismatch')
    require(word == cert['replacement'], 'recipe does not reconstruct replacement')
    return word


def primitive_stats(events, inherited):
    """Dense exact replay on eight native plus arbitrary private-work columns.

    This supplements the inherited column checker with all intermediate
    dyadic denominators and exact scalar row norms; it is not compiler precision.
    """
    rows = [[Q(i == j) for j in range(9)] for i in range(9)]
    depth, norm = 0, Q(1)
    primitives = inherited.lowering(events)
    for e in primitives:
        op, t = e[:2]
        if op == 'clear':
            rows[t] = [Q(0)] * 9
        elif op in ('double', 'halve', 'negate'):
            factor = {'double': Q(2), 'halve': Q(1, 2), 'negate': Q(-1)}[op]
            rows[t] = [factor * x for x in rows[t]]
        else:
            require(op == 'add', 'unknown lowered primitive')
            rows[t] = [a + e[3] * b for a, b in zip(rows[t], rows[e[2]])]
        require(all(x.denominator & (x.denominator - 1) == 0 for x in rows[t]),
                'non-dyadic primitive state')
        depth = max(depth, *(x.denominator.bit_length() - 1 for x in rows[t]))
        norm = max(norm, sum(map(abs, rows[t])))
    require(rows[8] == [0] * 9 and all(row[8] == 0 for row in rows[:8]),
            'private coefficient dirt was not cleared')
    endpoint = [list(column) for column in zip(*(row[:8] for row in rows[:8]))]
    require(endpoint == inherited.columns(events), 'dense primitive endpoint mismatch')
    return {'primitives': len(primitives), 'fractional_guard_bits': depth,
            'prefix_row_l1_max': str(norm), 'arbitrary_columns': 9}


def local_controls(old, good, cert, reference, inherited):
    frame, entry = reference['frame'], reference['entry_frames']
    rejected = []

    def reject(name, mutant, reason):
        try:
            validate_gate_types(mutant)
            inherited.validate(old, mutant, frame, entry)
        except ValueError as error:
            require(reason in str(error), name + ': unexpected rejection: ' + str(error))
            rejected.append({'name': name, 'reason': reason})
        else:
            raise ValueError('Accepted negative control: ' + name)

    for i in range(len(good)):
        reject('delete_gate_' + str(i), good[:i] + good[i + 1:], 'exact local map differs')
        mutant = copy.deepcopy(good)
        mutant[i][3 if mutant[i][0] == 'add' else 2] *= -1
        reject('flip_gate_sign_' + str(i), mutant, 'exact local map differs')
    mutant = copy.deepcopy(good)
    mutant[0][-1][0] ^= 1
    reject('wrong_frame', mutant, 'changed frame path')
    mutant = copy.deepcopy(good)
    mutant[0][3] = True
    reject('boolean_coefficient', mutant, 'non-integer gate field')
    # Omitting the first original gate without the necessary reordering is false.
    reject('drop_without_reordering', old[1:], 'exact local map differs')
    mutant = good + [['scale', 0, 2**40, 1, frame],
                     ['scale', 0, 1, 2**40, frame]]
    require(inherited.columns(mutant) == inherited.columns(good),
            'prefix mutant must preserve exact endpoint')
    reject('neutral_prefix_growth', mutant, 'prefix growth increased')
    mutant = good + [['scale', 0, -1, 1, frame]] * 20
    require(inherited.columns(mutant) == inherited.columns(good),
            'cost mutant must preserve exact endpoint')
    reject('neutral_cost_inflation', mutant, 'no primitive improvement')
    bad_recipe = copy.deepcopy(cert)
    bad_recipe['fusions'][0]['pair_order'] = [1, 2]
    try:
        replay_recipe(old, bad_recipe, inherited)
    except ValueError as error:
        require('fusion changes the exact map' in str(error), 'wrong recipe rejection')
        rejected.append({'name': 'wrong_fusion_order', 'reason': 'fusion changes the exact map'})
    else:
        raise ValueError('Wrong fusion order accepted')
    return rejected


def make_raw(raw, template, replacement, blocks, inherited):
    changed = copy.deepcopy(raw)
    for block in reversed(blocks):
        regs = [r - 16 if r >= 240 else r - 8
                for r in block['registers_before_112_port_restriction']]

        def relocate(events):
            result = copy.deepcopy(events)
            for e in result:
                e[1] = regs[e[1]]
                if e[0] == 'add':
                    e[2] = regs[e[2]]
                e[-1] = block['frame']
            return result

        start, end = block['A_window_zero_based']
        require(raw['A'][start:end] == relocate(template), 'raw constructor window differs')
        changed['A'][start:end] = relocate(replacement)
    full = [256, 128, 64, 32, 16, 8, 4, 2, 1]
    changed['cleanup'] = [e[:-1] + [full] for e in inherited.inverse(
        [e for e in changed['A'] + changed['B'] if not 112 <= e[1] < 224])]
    return changed


def verify(out):
    pins = check_pins()
    inherited = load('factory_predecessor', PREDECESSOR / 'verify.py')
    reference = read(PREDECESSOR / 'CIRCUIT.json')
    cert = read(HERE / 'CIRCUIT.json')
    blocks = read(PREDECESSOR / 'BLOCKS.json')
    require(cert['format'] == 'complex-factory-triple-fusion-v1', 'wrong certificate format')
    require(type(cert['assignment_seed']) is int and cert['assignment_seed'] == 23
            and type(cert['seed_block_index']) is int and cert['seed_block_index'] == 23 % 14,
            'wrong seed block')
    old, good = reference['replacement'], cert['replacement']
    validate_gate_types(good)
    replay_recipe(old, cert, inherited)
    require(len(old) == cert['predecessor_gates'] == 34 and
            len(good) == cert['replacement_gates'] == 32, 'wrong gate count')
    local = inherited.validate(old, good, reference['frame'], reference['entry_frames'])
    controls = local_controls(old, good, cert, reference, inherited)
    variants = {'main': lambda x: x, 'cleanup': inherited.inverse,
                'dual_main': inherited.dual,
                'dual_cleanup': lambda x: inherited.dual(inherited.inverse(x))}
    primitives = {}
    copy_lowering = load('factory_copy_lowering', ROOT / 'research/complex-dyadic-lowering/lower.py')
    for name, transform in variants.items():
        before, after = primitive_stats(transform(old), inherited), primitive_stats(transform(good), inherited)
        require(after['fractional_guard_bits'] <= before['fractional_guard_bits']
                and Q(after['prefix_row_l1_max']) <= Q(before['prefix_row_l1_max']),
                'local primitive precision envelope increased')

        def copied_cost(events):
            count = 0
            for e in events:
                op = ([e[0], ['L', e[1]], ['L', e[2]], e[3], e[4]] if e[0] == 'add'
                      else [e[0], ['L', e[1]], e[2], e[3]])
                count += len(copy_lowering.lower(op))
            return count

        primitives[name] = {'before': before, 'after': after,
                            'pr696_comparator_before': copied_cost(transform(old)),
                            'pr696_comparator_after': copied_cost(transform(good))}
        require(primitives[name]['pr696_comparator_before'] -
                primitives[name]['pr696_comparator_after'] == 4, 'PR696 comparator differs')
    inherited.run(PREDECESSOR / 'extract.py', [out / 'original'], out / 'constructor.log')
    windows = read(out / 'original/WINDOWS.json')
    inherited.bind_blocks(blocks, windows, reference)
    for block in blocks:
        a, b = copy.deepcopy(old), copy.deepcopy(good)
        for e in a + b:
            e[-1] = block['frame']
        require(inherited.validate(a, b, block['frame'], block['entry_frames']) == local,
                'block-specific frame/map check differs')
    raw = read(out / 'original/FULL-WORD.json.gz')
    reports, words = {}, {}
    for name, replacement in [('before', old), ('after', good)]:
        changed = make_raw(raw, reference['original'], replacement, blocks, inherited)
        path = out / (name + '.json.gz')
        path.write_bytes(gzip.compress(canonical(changed), mtime=0))
        reports[name], words[name] = inherited.native(path, out / (name + '-native'), out)
    require(canonical(reports['before']) == canonical(read(PREDECESSOR / 'RESULT.json')['after']),
            'fresh predecessor replay differs from its retained result')
    for key in ('local_profile', 'start', 'final', 'compensation', 'ports', 'centers',
                'center_frames', 'frames', 'edges'):
        require(words['before'][key] == words['after'][key], 'native invariant differs: ' + key)
    for key in ('helpers', 'widths', 'local_rank_mass', 'directed_edges', 'compensation_additions'):
        require(reports['before']['native'][key] == reports['after']['native'][key],
                'native inventory differs: ' + key)
    macro_saved = 2 * len(blocks) * (len(old) - len(good))
    primitive_saved = 2 * len(blocks) * sum(local[k]['old_real_primitives'] -
                                          local[k]['new_real_primitives'] for k in ('main', 'cleanup'))
    require(macro_saved == 56 and primitive_saved == 448, 'unexpected full circuit saving')
    require(reports['before']['native']['scalar_operations'] -
            reports['after']['native']['scalar_operations'] == macro_saved, 'native macro cost differs')
    for direction in ('forward', 'backward'):
        before, after = (reports[k]['emitted'][direction] for k in ('before', 'after'))
        require(before['scalar_macros'] - after['scalar_macros'] == macro_saved,
                'emitted macro cost differs')
        require(before['real_component_primitive_bound'] - after['real_component_primitive_bound']
                == primitive_saved, 'emitted primitive cost differs')
        require(before['paid_profile'] == after['paid_profile'], 'paid profile changed')
        require(Q(reports['after']['local']['local'][direction]['prefix_l1_upper']) <=
                Q(reports['before']['local']['local'][direction]['prefix_l1_upper']),
                'whole raw word positive prefix increased')
    bad = make_raw(raw, reference['original'], good, blocks, inherited)
    bad['cleanup'].pop()
    bad_path = out / 'missing-cleanup.json.gz'
    bad_path.write_bytes(gzip.compress(canonical(bad), mtime=0))
    try:
        inherited.native(bad_path, out / 'bad-native', out)
    except ValueError:
        require('cleanup is not the literal reversed inverse' in
                (out / 'bad-native-native.log').read_text(), 'wrong missing-cleanup rejection')
        controls.append({'name': 'missing_cleanup', 'reason': 'literal reversed inverse mismatch'})
    else:
        raise ValueError('Missing cleanup accepted')
    return {'status': 'PASS_COMPLEX_FACTORY_FUSION', 'base_commit': BASE,
            'source_files_checked': len(pins['files']), 'seed_block_index': 9, 'block_count': 14,
            'circuit_sha256': hashlib.sha256((HERE / 'CIRCUIT.json').read_bytes()).hexdigest(),
            'old_gates': len(old), 'new_gates': len(good), 'local_checks': local,
            'primitive_checks': primitives, 'scalar_operations_saved_with_cleanup': macro_saved,
            'real_component_primitives_saved_per_orientation': primitive_saved,
            'pr696_lowering_comparator_saving_per_orientation': 224,
            'negative_controls': controls, 'before': reports['before'], 'after': reports['after'],
            'scope': 'Raw PR622 factory after PR681 only; no transported supplier, new kappa, '
                     'phase lowering, hosted invoice, or full multiplication theorem.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='retain replay artifacts in a new directory')
    parser.add_argument('--write', type=Path, help='write a new receipt instead of checking RESULT.json')
    args = parser.parse_args()
    if args.write:
        require(not args.write.exists(), 'receipt output already exists')
    if args.out:
        args.out.mkdir(parents=True, exist_ok=False)
        result = verify(args.out.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix='factory-fusion-23-') as tmp:
            result = verify(Path(tmp))
    if args.write:
        with args.write.open('x') as handle:
            handle.write(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        require(canonical(result) == canonical(read(HERE / 'RESULT.json')),
                'receipt differs from frozen result')
    print('PASS_COMPLEX_FACTORY_FUSION windows=14 gates=34->32 saved_with_cleanup=56 '
          'primitives_saved=448 columns=716 controls=' + str(len(result['negative_controls'])) +
          ' no_new_kappa')


if __name__ == '__main__':
    main()

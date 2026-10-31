"""Ordered unchanged70 plus concrete consumer acceptance controls; parent only."""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
from types import FunctionType

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference
import bounded_serialization
import serialization_controls
from full_consumer import accept_operation, need, write_record

ORDER = ['legitimate-bool-float-slots', 'ordered-duplicate-ranks', 'literal-fallback-no-credit',
         'int-only-rank-bool-fallback-no-credit', 'missing-marker-no-credit', 'faults-enabled-no-credit',
         'incomplete-phase-no-credit', 'missing-batches-no-credit', 'oversize-batch-no-credit',
         'wrong-copy-limit-no-credit', 'missing-file-counter-no-credit', 'wrong-byte-counter-no-credit',
         'digest-copy-mismatch-no-credit', 'incomplete-cleanup-no-credit', 'missing-stage-no-credit']


def finite_writer(values):
    result, witness, ranks = values
    expected = {'result_sha256': hashlib.sha256(reference.canonical(result)).hexdigest(),
                'exact_witness_sha256': hashlib.sha256(reference.canonical(witness)).hexdigest(),
                'rank_trace_sha256': hashlib.sha256(reference.canonical(ranks)).hexdigest(),
                'rank_call_count': len(ranks), 'rank_distinct_matrix_count': len({row for row, _ in ranks})}
    namespace = dict(reference.write_scientific.__globals__)
    namespace['EXPECTED'] = expected
    original = FunctionType(reference.write_scientific.__code__, namespace,
                            reference.write_scientific.__name__, reference.write_scientific.__defaults__,
                            reference.write_scientific.__closure__)
    return bounded_serialization.make_writer(original, reference.canonical, expected, reference.require)


def run(root, receipt_path):
    need(sys.flags.optimize in (0, 1), 'Undeclared control optimization')
    need(not root.exists() and not root.is_symlink(), 'Control root must be fresh')
    need(not receipt_path.exists() and not receipt_path.is_symlink(), 'Control receipt must be fresh')
    root.mkdir(mode=0o700)
    spec = json.loads((HERE / 'CONTROL-SPEC.json').read_text(encoding='utf-8'))
    old = serialization_controls.run_controls(reference, root / 'original70')
    need(old['case_count'] == spec['count_per_mode'] == 70, 'Original control count differs')
    need([row['case'] for row in old['cases']] == spec['ordered_cases'], 'Original control order differs')
    need(old['optimization'] == sys.flags.optimize, 'Original control optimization differs')
    rows = []

    def fresh():
        return serialization_controls._fixture()[:3]

    def actual(name, transform, bounded):
        result, witness, ranks = fresh()
        values = transform(result, witness, ranks)
        writer = finite_writer(values)
        output = root / name
        output.mkdir()
        receipt = writer(output, *values)
        if bounded:
            accept_operation(writer.last_operation, receipt['serialized_bytes'], writer._h25_serialization_faults_enabled)
            need(not list(output.glob('.serialization-*')), 'Successful bounded staging leaked')
        else:
            need(writer.last_operation['status'] == 'LITERAL_REFERENCE_FALLBACK', 'Literal fallback was not observed')
            try:
                accept_operation(writer.last_operation, receipt['serialized_bytes'], False)
            except RuntimeError:
                pass
            else:
                raise RuntimeError('Literal fallback incorrectly qualified as bounded')
        rows.append({'case': name, 'status': 'PASS', 'operation': writer.last_operation})
        return writer.last_operation, receipt['serialized_bytes']

    def floats(result, witness, ranks):
        result.update({'bool_slot': True, 'roles_per_target': 47.041})
        return result, witness, ranks
    operation, sizes = actual(ORDER[0], floats, True)

    def duplicates(result, witness, ranks):
        ranks[:] = [((2, 1), 1), ((2, 1), 1), ((1, 2), 2)]
        return result, witness, ranks
    actual(ORDER[1], duplicates, True)

    def unsupported(result, witness, ranks):
        class DictSubclass(dict):
            pass
        return DictSubclass(result), witness, ranks
    actual(ORDER[2], unsupported, False)

    def rank_bool(result, witness, ranks):
        ranks[0] = ((True, 2), 1)
        return result, witness, ranks
    actual(ORDER[3], rank_bool, False)

    mutations = [
        lambda op: op.update(status='LITERAL_REFERENCE_FALLBACK'),
        lambda op: None,
        lambda op: op.update(phase='copy:witness.json'),
        lambda op: op.update(batch_count=0),
        lambda op: op.update(largest_batch_bytes=1048577),
        lambda op: op.update(copy_bytes_limit=1048577),
        lambda op: op['files'].pop('witness.json'),
        lambda op: op['files']['witness.json'].update(copy_write_bytes=0),
        lambda op: op['files']['result.json'].update(copy_sha256='0' * 64),
        lambda op: op.update(cleanup=['result.json']),
        lambda op: op.pop('stage'),
    ]
    for name, mutation in zip(ORDER[4:], mutations):
        changed = copy.deepcopy(operation)
        mutation(changed)
        try:
            accept_operation(changed, sizes, name == 'faults-enabled-no-credit')
        except RuntimeError as error:
            rows.append({'case': name, 'status': 'PASS', 'expected_rejection': str(error)})
        else:
            raise RuntimeError('Consumer accepted invalid bounded evidence: ' + name)
    need([row['case'] for row in rows] == ORDER, 'New consumer control count/order differs')
    receipt = {'schema': 'h25-o03-consumer-controls-v1', 'status': 'CONSUMER_CONTROLS_RETURNED',
               'optimization': sys.flags.optimize, 'old_case_count': 70, 'new_case_count': len(rows),
               'old_control_receipt': str(root / 'original70' / 'controls.json'), 'cases': rows,
               'scope': 'Finite controls only; authentic full replay is separately mandatory'}
    write_record(receipt_path, receipt)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    receipt = run(args.output_root, args.receipt)
    print(json.dumps({'status': receipt['status'], 'optimization': receipt['optimization'],
                      'old_cases': 70, 'new_cases': len(ORDER)}, sort_keys=True))


if __name__ == '__main__':
    main()

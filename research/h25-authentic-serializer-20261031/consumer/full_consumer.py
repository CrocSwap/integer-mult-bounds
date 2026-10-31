"""Authentic retained-value serializer arm. Execute only after parent admission.

Explicit sibling imports support python -B -I. The envelope authenticates these
exact source directories before and after execution. No scientific imports.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(HERE.parent / 'loader'))
import reference

NAMES = ('result.json', 'witness.json', 'rank-trace.json')
SIZE_KEYS = ('result', 'witness', 'rank_trace')
HASH_KEYS = ('result_sha256', 'exact_witness_sha256', 'rank_trace_sha256')
SIZES = dict(zip(SIZE_KEYS, (527, 58143622, 2674272)))
CHUNK = 1048576


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def exact_int(value, low=0, high=None):
    return type(value) is int and value >= low and (high is None or value <= high)


def accept_operation(operation, sizes, faults_enabled):
    """Require complete source-bound bounded path; fallback never earns credit."""
    need(faults_enabled is False, 'Production fault seam enabled')
    need(type(operation) is dict and operation.get('status') == 'BOUNDED_SERIALIZATION_PASS',
         'Genuine complete replay did not take bounded serializer path')
    need(operation.get('phase') == 'complete', 'Bounded serialization incomplete')
    need(operation.get('batch_bytes_limit') == CHUNK and type(operation.get('batch_bytes_limit')) is int,
         'Batch-byte limit differs')
    need(operation.get('batch_rows_limit') == 1024 and type(operation.get('batch_rows_limit')) is int,
         'Batch-row limit differs')
    need(operation.get('copy_bytes_limit') == CHUNK and type(operation.get('copy_bytes_limit')) is int,
         'Copy limit differs')
    need(exact_int(operation.get('batch_count'), 1), 'Missing actual bounded batches')
    need(exact_int(operation.get('largest_batch_bytes'), 2, CHUNK), 'Batch size differs')
    need(operation.get('cleanup') == list(NAMES) + ['stage_directory'], 'Success cleanup incomplete')
    need(type(operation.get('stage')) is str, 'Missing private stage identity')
    need(set(operation.get('files', {})) == set(NAMES), 'Bounded file counters incomplete')
    for name, key in zip(NAMES, SIZE_KEYS):
        row = operation['files'][name]
        need(type(row) is dict, 'Malformed bounded file counters')
        need(all(exact_int(row.get(field)) and row[field] == sizes[key] for field in
                 ('hashed_bytes', 'accepted_write_bytes', 'copy_read_bytes', 'copy_write_bytes')),
             'Bounded copy/hash counters differ: ' + name)
        need(type(row.get('sha256')) is str and row['sha256'] == row.get('copy_sha256'),
             'Private/final digest differs: ' + name)


def file_identity(info):
    # Access time may legitimately change during readback under relatime.
    return (info.st_dev, info.st_ino, info.st_mode, info.st_size, info.st_mtime_ns,
            info.st_ctime_ns, info.st_nlink, info.st_uid, info.st_gid)


def read_files(root, scientific, expected, sizes):
    need(set(path.name for path in root.iterdir()) == set(NAMES), 'Unexpected output or staging files')
    files = {}
    for name, key, size_key in zip(NAMES, HASH_KEYS, SIZE_KEYS):
        path = root / name
        before = path.lstat()
        need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1, 'Output is not private regular file')
        h, total = hashlib.sha256(), 0
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(fd, 'rb') as stream:
            need(file_identity(os.fstat(stream.fileno())) == file_identity(before), 'Output descriptor/path differs')
            while True:
                chunk = stream.read(CHUNK)
                if not chunk:
                    break
                total += len(chunk)
                need(total <= sizes[size_key], 'Output exceeds frozen size')
                h.update(chunk)
            need(file_identity(os.fstat(stream.fileno())) == file_identity(before), 'Output changed while reading')
        need(file_identity(path.lstat()) == file_identity(before), 'Output path changed while reading')
        need(total == sizes[size_key] == scientific['serialized_bytes'][size_key], 'Output size differs')
        need(h.hexdigest() == expected[key] == scientific[key], 'Output digest differs')
        files[name] = {'bytes': total, 'sha256': h.hexdigest()}
    return files


def write_record(path, value):
    raw = json.dumps(value, sort_keys=True, indent=2, allow_nan=False).encode('ascii') + b'\n'
    need(len(raw) <= 65536, 'Consumer receipt exceeds fixed bound')
    with path.open('xb') as stream:
        need(stream.write(raw) == len(raw), 'Short consumer receipt write')


def run(arm, input_root, custody, output_root, receipt_path):
    need(arm in ('baseline', 'candidate'), 'Unknown serializer arm')
    need(sys.flags.optimize == 0, 'Full arm requires optimization0')
    need(not output_root.exists() and not output_root.is_symlink(), 'Output root must be fresh')
    need(not receipt_path.exists() and not receipt_path.is_symlink(), 'Receipt must be fresh')
    need(receipt_path.parent.resolve() != output_root.resolve(), 'Receipt must be outside artifact root')
    from frozen_h25_inputs import load_frozen_inputs
    loaded = load_frozen_inputs(input_root, custody)
    result, witness, ranks = loaded['result'], loaded['witness'], loaded['ranks']
    need(len(ranks) == reference.EXPECTED['rank_call_count'], 'Full rank count differs')
    need(len({rows for rows, _ in ranks}) == reference.EXPECTED['rank_distinct_matrix_count'],
         'Full distinct rank row count differs')
    output_root.mkdir(mode=0o700)
    writer = reference.write_scientific
    faults = None
    if arm == 'candidate':
        import bounded_serialization
        writer = bounded_serialization.make_writer(reference.write_scientific, reference.canonical,
                reference.EXPECTED, reference.require, batch_bytes=CHUNK, batch_rows=1024, copy_bytes=CHUNK)
        faults = writer._h25_serialization_faults_enabled
        need(faults is False, 'Fault injection enabled')
    started = time.monotonic_ns()
    scientific = writer(output_root, result, witness, ranks)
    ended = time.monotonic_ns()
    need(scientific == dict(reference.EXPECTED, serialized_bytes=SIZES), 'Original complete receipt differs')
    operation = None if arm == 'baseline' else writer.last_operation
    if arm == 'candidate':
        accept_operation(operation, SIZES, faults)
        stage = Path(operation['stage'])
        need(stage.parent == output_root and stage.name.startswith('.serialization-') and
             not stage.exists() and not stage.is_symlink(), 'Private stage cleanup differs')
        need(operation['batch_count'] <= len(ranks) + sum(len(witness[k]) for k in witness if k != 'code') +
             sum(len(v) for k, v in witness['code'].items() if k != 'roles'), 'Impossible batch count')
        for name, digest_key in zip(NAMES, HASH_KEYS):
            need(operation['files'][name]['sha256'] == reference.EXPECTED[digest_key], 'Bounded digest differs')
    files = read_files(output_root, scientific, reference.EXPECTED, SIZES)
    # Complete second authentication is paid and must not allocate another full input.
    from frozen_h25_inputs import authenticate_inputs
    after = authenticate_inputs(input_root, custody)
    receipt = {'schema': 'h25-o03-full-consumer-v1', 'status': 'COMPLETE_RETAINED_VALUE_SERIALIZATION_RETURNED',
               'arm': arm, 'optimization': sys.flags.optimize, 'scientific_receipt': scientific,
               'files': files, 'candidate_operation': operation, 'faults_enabled': faults,
               'input_receipt': loaded['input_receipt'], 'after_input_receipt': after,
               'writer_monotonic_ns': {'start': started, 'end': ended, 'elapsed': ended - started},
               'scope': 'Complete authentic retained values; no fresh scientific construction or caller claim'}
    write_record(receipt_path, receipt)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--arm', choices=('baseline', 'candidate'), required=True)
    parser.add_argument('--input-root', type=Path, required=True)
    parser.add_argument('--custody-json', type=Path, required=True)
    parser.add_argument('--output-root', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    try:
        custody = json.loads(args.custody_json.read_text(encoding='utf-8'))
        result = run(args.arm, args.input_root, custody, args.output_root, args.receipt)
    except BaseException as error:
        # Preserve all partial final/private files. A failure is never rerolled.
        if not args.receipt.exists() and not args.receipt.is_symlink():
            try:
                write_record(args.receipt, {'schema': 'h25-o03-full-consumer-v1', 'status': 'FAILED_EVIDENCE_RETAINED',
                    'arm': args.arm, 'error': {'type': type(error).__name__, 'message': str(error)[:2048]}})
            except BaseException:
                pass
        raise
    print(json.dumps({'status': result['status'], 'arm': args.arm}, sort_keys=True))


if __name__ == '__main__':
    main()

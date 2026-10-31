"""Independent bounded complete validator; imports neither loader nor consumer.

Input witnesses are streamed directly from newly authenticated fixed transports
against both complete outputs. Only the fixed <=5662-byte certificate and the
fixed <=2674272-byte rank trace are parsed; witness parsing is never repeated.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import stat
import sys

CHUNK = 1048576
EXPECTED = {'result_sha256': '342e99212b12e518902ae9598613f5484113bacee8747c27a13b58a4b1d3986c',
'exact_witness_sha256': '4b170c1dbfc33c7cb141a2284c6fd69eac7b6d100971d3e9ee625502b5893f82',
'rank_trace_sha256': '85006ca332bbc57c2ba9fd06f61a0281d4cee600c9f3b449342379bf2aedec8f',
'rank_call_count': 59959, 'rank_distinct_matrix_count': 252}
SIZES = {'result': 527, 'witness': 58143622, 'rank_trace': 2674272}
PREFIX = 'baseline/evidence/canonical/'
SPECS = {
'witness.json.gz': (16995263, '8e1b8b03320d5e077c0414c3644396faf182bdfa1a72d8067c8fea8a33dbf5d0', 58143622, EXPECTED['exact_witness_sha256']),
'rank-trace.json.gz': (22029, '20e76cd894807cf84ca740312fdc2a73d1d70740e2f0c5ec55b3d0afdd9311fa', 2674272, EXPECTED['rank_trace_sha256']),
'complex-network.json': (5662, '1f763d95c7ff163aa71d13cd82784f16665be8afb21f75e76941e2119562098f', 5662, '1f763d95c7ff163aa71d13cd82784f16665be8afb21f75e76941e2119562098f')}
NAMES = ('result.json', 'witness.json', 'rank-trace.json')


def need(value, message):
    if not value:
        raise RuntimeError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def pairs(rows):
    result = {}
    for key, value in rows:
        need(key not in result, 'Duplicate JSON key')
        result[key] = value
    return result


def constant(value):
    raise ValueError('Nonfinite JSON constant: ' + value)


def parse(raw):
    return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs, parse_constant=constant)


def identity(info):
    return {'dev': info.st_dev, 'ino': info.st_ino, 'mode': stat.S_IMODE(info.st_mode),
            'uid': info.st_uid, 'gid': info.st_gid, 'nlink': info.st_nlink,
            'mtime_ns': info.st_mtime_ns, 'ctime_ns': info.st_ctime_ns}


def opened(path):
    before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1, 'Expected private regular file: ' + str(path))
    stream = os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW), 'rb')
    try:
        need(identity(os.fstat(stream.fileno())) == identity(before) and os.fstat(stream.fileno()).st_size == before.st_size,
             'File descriptor identity differs')
    except BaseException:
        stream.close()
        raise
    return stream, before


def unchanged(path, before):
    after = path.lstat()
    need(identity(after) == identity(before) and after.st_size == before.st_size, 'File changed: ' + str(path))


def custody_check(root, custody):
    need(custody['schema'] == 'h25-input-custody-v1' and custody['root'] == str(root), 'Input custody binding differs')
    need(root.is_absolute() and root.resolve() == root, 'Input root must be canonical absolute path')
    for relative, binding in [('', custody['root_identity'])] + list(custody['directories'].items()):
        path = root / relative
        info = path.lstat()
        need(stat.S_ISDIR(info.st_mode) and stat.S_IMODE(info.st_mode) == 0o555,
             'Input directory mode/type differs')
        need(set(identity(info)) == set(binding) and all(type(binding[key]) is int for key in identity(info)) and
             identity(info) == binding, 'Input directory identity differs')
    need(set(custody['directories']) == {'baseline', 'baseline/evidence', 'baseline/evidence/canonical'},
         'Input custody directory closure differs')
    need(set(custody['files']) == {PREFIX + name for name in SPECS}, 'Input file closure differs')
    unique = set()
    for name, spec in SPECS.items():
        path = root / PREFIX / name
        stream, before = opened(path)
        binding = custody['files'][PREFIX + name]
        key = (before.st_dev, before.st_ino)
        need(key not in unique, 'Aliased input files')
        unique.add(key)
        need(all(type(binding.get(key)) is int for key in identity(before)) and type(binding.get('size')) is int and
             identity(before) == {key: binding[key] for key in identity(before)} and
             stat.S_IMODE(before.st_mode) == 0o444 and before.st_size == spec[0] == binding['size'] and
             binding['sha256'] == spec[1], 'Input metadata custody differs')
        h, count = hashlib.sha256(), 0
        with stream:
            while True:
                raw = stream.read(CHUNK)
                if not raw:
                    break
                count += len(raw)
                need(count <= spec[0], 'Transport size overrun')
                h.update(raw)
        unchanged(path, before)
        need(count == spec[0] and h.hexdigest() == spec[1], 'Input transport authentication failed')


def bounded_file(path, limit):
    stream, before = opened(path)
    with stream:
        raw = stream.read(limit + 1)
        need(len(raw) <= limit and stream.read(1) == b'', 'Bounded metadata overrun')
    unchanged(path, before)
    return raw


def logical(root, name, outputs=(), collect=False):
    """Authenticate exact logical bytes and compare fresh regular outputs."""
    spec = SPECS[name]
    source = root / PREFIX / name
    incoming, before = opened(source)
    outgoing = []
    h, total = hashlib.sha256(), 0
    collected = bytearray() if collect else None
    try:
        for path in outputs:
            outgoing.append(opened(path))
        with incoming:
            data = gzip.GzipFile(fileobj=incoming, mode='rb') if name.endswith('.gz') else incoming
            try:
                while True:
                    raw = data.read(min(CHUNK, spec[2] - total + 1))
                    if not raw:
                        break
                    total += len(raw)
                    need(total <= spec[2], 'Logical size overrun')
                    h.update(raw)
                    for stream, _ in outgoing:
                        need(stream.read(len(raw)) == raw, 'Complete output differs from authenticated logical input')
                    if collect:
                        collected.extend(raw)
                need(total == spec[2] and h.hexdigest() == spec[3], 'Logical digest/final size differs')
                for stream, _ in outgoing:
                    need(stream.read(1) == b'', 'Output trailing data')
            finally:
                if data is not incoming:
                    data.close()
    finally:
        incoming.close()
        for path, (stream, facts) in zip(outputs, outgoing):
            stream.close()
            unchanged(path, facts)
        unchanged(source, before)
    return {'bytes': total, 'sha256': h.hexdigest()}, collected


def validate_receipt(receipt, arm, root, files):
    need(receipt['schema'] == 'h25-o03-full-consumer-v1' and
         receipt['status'] == 'COMPLETE_RETAINED_VALUE_SERIALIZATION_RETURNED' and
         receipt['arm'] == arm and type(receipt['optimization']) is int and receipt['optimization'] == 0,
         'Full consumer receipt status differs')
    for key, schema in [('input_receipt', 'h25-fresh-input-receipt-v1'),
                        ('after_input_receipt', 'h25-input-authentication-v1')]:
        record = receipt[key]
        need(record['schema'] == schema and record['custody_before_after'] == 'MATCH' and
             record['cached_pass'] is False, 'Fresh input receipt differs')
        need(set(record['files']) == {PREFIX + name for name in SPECS}, 'Input receipt closure differs')
        for name, spec in SPECS.items():
            row = record['files'][PREFIX + name]
            need(row == dict(encoding='gzip' if name.endswith('.gz') else 'plain',
                transport_bytes=spec[0], transport_sha256=spec[1], logical_bytes=spec[2], logical_sha256=spec[3]),
                'Input receipt fixed pins differ')
    need(receipt['input_receipt']['rank_call_count'] == 59959 and
         type(receipt['input_receipt']['rank_call_count']) is int and
         receipt['input_receipt']['rank_distinct_matrix_count'] == 252 and
         type(receipt['input_receipt']['rank_distinct_matrix_count']) is int, 'Input rank counts differ')
    need(receipt['after_input_receipt']['logical_validation'] == 'NOT_PERFORMED_IN_TRANSPORT_READBACK',
         'After input receipt silently supplied logical PASS')
    scientific = receipt['scientific_receipt']
    need(scientific == dict(EXPECTED, serialized_bytes=SIZES), 'Independent original EXPECTED mismatch')
    need(all(type(scientific[key]) is int for key in ('rank_call_count', 'rank_distinct_matrix_count')),
         'Rank receipt scalar type differs')
    need(all(type(value) is int for value in scientific['serialized_bytes'].values()), 'Receipt byte scalar type differs')
    need(receipt['files'] == files, 'Consumer file receipt differs')
    if arm == 'baseline':
        need(receipt['candidate_operation'] is None and receipt['faults_enabled'] is None, 'Baseline used candidate')
        return
    op = receipt['candidate_operation']
    need(receipt['faults_enabled'] is False and op['status'] == 'BOUNDED_SERIALIZATION_PASS' and
         op['phase'] == 'complete', 'Candidate fallback/fault/incomplete route')
    for key, value in [('batch_bytes_limit', CHUNK), ('batch_rows_limit', 1024), ('copy_bytes_limit', CHUNK)]:
        need(type(op[key]) is int and op[key] == value, 'Bounded limit differs')
    need(type(op['batch_count']) is int and 1 <= op['batch_count'] <= 1000000 and
         type(op['largest_batch_bytes']) is int and 2 <= op['largest_batch_bytes'] <= CHUNK,
         'Actual bounded batch evidence differs')
    need(op['cleanup'] == list(NAMES) + ['stage_directory'], 'Cleanup receipt differs')
    stage = Path(op['stage'])
    need(stage.parent == root and stage.name.startswith('.serialization-') and not stage.exists() and
         not stage.is_symlink(), 'Private stage persists or has wrong identity')
    need(set(op['files']) == set(NAMES), 'Bounded file bill incomplete')
    for name in NAMES:
        row, expected = op['files'][name], files[name]
        for key in ('hashed_bytes', 'accepted_write_bytes', 'copy_read_bytes', 'copy_write_bytes'):
            need(type(row[key]) is int and row[key] == expected['bytes'], 'Bounded byte counter differs')
        need(row['sha256'] == row['copy_sha256'] == expected['sha256'], 'Bounded digest counter differs')


def validate(args):
    need(sys.flags.optimize == 0, 'Independent validation requires optimization0')
    custody = parse(bounded_file(args.custody_json, 65536))
    custody_check(args.input_root, custody)
    need(args.baseline_root != args.candidate_root and
         (args.baseline_root.stat().st_dev, args.baseline_root.stat().st_ino) !=
         (args.candidate_root.stat().st_dev, args.candidate_root.stat().st_ino), 'Arms share output root')
    for root in (args.baseline_root, args.candidate_root):
        need(root.is_absolute() and root.resolve() == root and stat.S_ISDIR(root.lstat().st_mode), 'Invalid output root')
        need(set(p.name for p in root.iterdir()) == set(NAMES), 'Unexpected output/failure/staging file')
    cert_facts, cert_raw = logical(args.input_root, 'complex-network.json', collect=True)
    certificate = parse(cert_raw)
    result = {key: certificate[key] for key in ('circuit', 'side_map', 'labels', 'role_frames')}
    result_raw = canonical(result)
    need(len(result_raw) == SIZES['result'] and hashlib.sha256(result_raw).hexdigest() == EXPECTED['result_sha256'],
         'Independent original literal result projection differs')
    files = {'result.json': {'bytes': len(result_raw), 'sha256': hashlib.sha256(result_raw).hexdigest()}}
    for root in (args.baseline_root, args.candidate_root):
        need(bounded_file(root / 'result.json', 527) == result_raw, 'Complete result output differs')
    for source, output in [('witness.json.gz', 'witness.json'), ('rank-trace.json.gz', 'rank-trace.json')]:
        facts, raw = logical(args.input_root, source,
            [args.baseline_root / output, args.candidate_root / output], collect=(output == 'rank-trace.json'))
        files[output] = facts
        if raw is not None:
            ranks = parse(raw)
            need(type(ranks) is list and len(ranks) == 59959, 'Independent full rank count differs')
            distinct = set()
            for event in ranks:
                need(type(event) is list and len(event) == 2 and type(event[0]) is list and
                     type(event[1]) is int and all(type(row) is int for row in event[0]), 'Rank exact-int schema differs')
                distinct.add(tuple(event[0]))
            need(len(distinct) == 252, 'Independent distinct rank count differs')
            del ranks, distinct, raw
    for arm, root, path in [('baseline', args.baseline_root, args.baseline_receipt),
                            ('candidate', args.candidate_root, args.candidate_receipt)]:
        validate_receipt(parse(bounded_file(path, 65536)), arm, root, files)
    custody_check(args.input_root, custody)
    report = {'schema': 'h25-o03-independent-complete-validation-v1', 'status': 'COMPLETE_OUTPUTS_VALIDATED',
              'expected': EXPECTED, 'files': files, 'certificate': cert_facts,
              'comparison_chunk_bytes': CHUNK, 'rank_parse_cap_bytes': 2674272,
              'independence': 'No loader/consumer/candidate imports; fixed independent pins, literal original canonical and certificate projection; complete source logical bytes compared with both outputs',
              'scope': 'Exact complete retained values only; resource/custody/runtime envelope and O03 adjudication remain separate'}
    encoded = json.dumps(report, sort_keys=True, indent=2).encode('ascii') + b'\n'
    with args.report.open('xb') as stream:
        need(stream.write(encoded) == len(encoded), 'Short validation report write')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('input-root', 'custody-json', 'baseline-root', 'candidate-root', 'baseline-receipt', 'candidate-receipt', 'report'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps({'status': validate(args)['status']}, sort_keys=True))


if __name__ == '__main__':
    main()

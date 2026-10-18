#!/usr/bin/env python3
"""Reconstruct the exact later PR279 head without replacing the reviewed package.

The default command checks source coverage and retained evidence. --replay runs
the unchanged candidate verifier in a new directory. Apache-2.0; prepared for
mihir-s-05 with substantial OpenAI Codex assistance.
"""
from array import array
from collections import Counter
from hashlib import sha1, sha256
from pathlib import Path, PurePosixPath
import argparse
import gzip
import io
import json
import os
import subprocess
import sys
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = '66849e1475c930fd7732b1a0067ffee7e1e95f60'
REVIEWED = '4d8c31eec7ae618645cb058101cb4e72a97268d3'
CANDIDATE = '913ccc48a0bc1173709ea92280b96252256b7754'
KAPPA = '724098741932703/1000000000000000000'
HISTORICAL = 'research/five-stage-gen4-banks'
STAGES = {'virtual', 'raw', 'bit', 'scalar', 'primes', 'banks', 'complex', 'math', 'finite'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return sha256(data).hexdigest()


def git_blob(data):
    return sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def canonical_records(data):
    """Bind every instruction field, independently of the gzip container bytes."""
    records = array('i')
    require(records.itemsize == 4, 'Candidate instruction format requires 32-bit C ints')
    records.frombytes(gzip.decompress(data))
    require(len(records) % 6 == 0, 'Incomplete instruction sextuple')
    if sys.byteorder != 'big':
        records.byteswap()
    return dict(encoding='big-endian signed 32-bit integers, six per instruction',
                records=len(records) // 6, sha256=digest(records.tobytes()))


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def archive_files(data):
    """Read regular relative files, rejecting duplicate and unexpected path forms."""
    files = {}
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
        for entry in archive:
            path = PurePosixPath(entry.name)
            require(entry.isfile() and not path.is_absolute() and
                    '..' not in path.parts and '\\' not in entry.name and
                    ':' not in entry.name and str(path) == entry.name,
                    'Invalid archive member: ' + entry.name)
            require(entry.name not in files, 'Duplicate archive member: ' + entry.name)
            stream = archive.extractfile(entry)
            require(stream is not None, 'Unreadable archive member: ' + entry.name)
            files[entry.name] = stream.read()
    return files


def validate_candidate(source, files):
    require(source['base_commit'] == BASE and source['reviewed_head'] == REVIEWED and
            source['candidate_head'] == CANDIDATE, 'Unexpected source commit')
    require(source['historical_package'] == HISTORICAL, 'Unexpected historical package')
    expected = source['candidate_files']
    require(len(expected) == 115 and set(files) == set(expected),
            'Missing or additional candidate file')
    for name, pin in expected.items():
        require(digest(files[name]) == pin['sha256'] and git_blob(files[name]) == pin['git_blob'],
                'Changed candidate file: ' + name)
    manifest = json.loads(files['MANIFEST.json'])
    require(digest(files['MANIFEST.json']) == source['candidate_manifest_sha256'],
            'Wrong candidate manifest')
    actual = {name: digest(data) for name, data in files.items() if name != 'MANIFEST.json'}
    require(manifest['files'] == actual, 'Candidate manifest does not bind all inputs')


def collect_candidate(root=ROOT, package=HERE):
    source = read_json(package / 'SOURCE.json')
    archive = (package / 'source-update.tar.gz').read_bytes()
    require(digest(archive) == source['archive_sha256'], 'Changed source archive')
    updated = archive_files(archive)
    changes = {row['path']: row for row in source['changes']}
    require(len(changes) == len(source['changes']) == 12 and set(updated) == set(changes),
            'Missing or additional update member')
    require(Counter(row['status'] for row in changes.values()) == {'modified': 10, 'added': 2},
            'Unexpected update classification')
    for name, pin in source['candidate_files'].items():
        require(pin['source'] == ('update_archive' if name in changes else 'historical_package'),
                'Incorrect coverage source: ' + name)
    for name, pin in source['context_sources'].items():
        require(digest((root / name).read_bytes()) == pin, 'Changed historical context: ' + name)
    workflow = source['unchanged_workflow']
    workflow_data = (root / workflow['path']).read_bytes()
    require(digest(workflow_data) == workflow['sha256'] and
            git_blob(workflow_data) == workflow['git_blob'], 'Changed historical workflow')
    comparison = read_json(root / 'research/pr-reconciliation-20261012/content-comparison.json')['279']
    require(comparison['total'] == 116 and len(comparison['matched']) == 104 and
            {row['path']: row['blob'] for row in comparison['unresolved']} ==
            {HISTORICAL + '/' + name: row['new_git_blob'] for name, row in changes.items()},
            'Retained update does not resolve the recorded source gap')
    historical = root / HISTORICAL
    old_manifest = (historical / 'MANIFEST.json').read_bytes()
    require(digest(old_manifest) == source['historical_manifest_sha256'],
            'Changed historical manifest')
    old_pins = json.loads(old_manifest)['files']
    actual_names = {p.relative_to(historical).as_posix() for p in historical.rglob('*') if p.is_file()}
    require(actual_names == set(old_pins) | {'MANIFEST.json'} and len(actual_names) == 113,
            'Historical inventory changed')
    files = {}
    for name in sorted(actual_names):
        path = historical / name
        require(not path.is_symlink() and path.resolve().is_relative_to(historical.resolve()),
                'Historical file escapes package: ' + name)
        data = path.read_bytes()
        if name != 'MANIFEST.json':
            require(digest(data) == old_pins[name], 'Changed historical file: ' + name)
        if name in changes:
            row = changes[name]
            require(digest(data) == row['old_sha256'] and git_blob(data) == row['old_git_blob'],
                    'Historical update base mismatch: ' + name)
        files[name] = data
    for name, data in updated.items():
        row = changes[name]
        require((name in files) == (row['status'] == 'modified'), 'Wrong change kind: ' + name)
        require(digest(data) == row['new_sha256'] and git_blob(data) == row['new_git_blob'],
                'Update source identity mismatch: ' + name)
        files[name] = data
    validate_candidate(source, files)
    return source, files


def check_selection(files):
    """Check the submitted finite schedule and its advertised accounting, not its theorem."""
    selection = json.loads(files['target-selection.json'])
    groups = selection['groups']
    require(len(groups) == 220, 'Wrong group count')
    targets, delta = set(), Counter()
    inserted = 0
    for row in groups:
        ts = row['targets']
        require(len(ts) == len(set(ts)) == 4 and all(0 <= t < 1760 for t in ts),
                'Invalid target square')
        require(not targets.intersection(ts), 'Overlapping target squares')
        targets.update(ts)
        dep = row['dependent']
        require(len(dep) == 1, 'Wrong dependency count')
        target, retained = next(iter(dep.items()))
        require(set(retained) == set(row['retained']) == set(ts) - {int(target)} and
                len(retained) == 3, 'Invalid retained targets')
        require(row['cut_record'] == selection['cut_record'] == 566579 and
                row['close_after_record'] > row['cut_record'] and row['close_rank'] == 21,
                'Invalid cut/close contract')
        require(row['local_histogram_delta'] == {'1': -1, '20': -1, '21': 1},
                'Wrong local rank delta')
        require(row['extra_setup_restore_additions'] == 2 * len(retained),
                'Unpaid setup/restore additions')
        inserted += 2 * len(retained)
        delta.update({int(k): v for k, v in row['local_histogram_delta'].items()})
    require(dict(delta) == {int(k): v for k, v in selection['expected_total_delta'].items()},
            'Wrong total delta')
    require(sum(rank * count for rank, count in delta.items()) == 0,
            'Rank mass changed')
    return dict(groups=220, targets=len(targets), setup_restore_additions=inserted,
                local_paid_call_delta=sum(delta.values()),
                five_stage_paid_call_delta=5 * sum(delta.values()),
                rank_mass_delta=0,
                scope='Schedule/count consistency only; literal identities need --replay.')


def reconstruct(files, destination):
    destination.mkdir(parents=True, exist_ok=False)
    for name, data in files.items():
        path = destination / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def check_replay(report, manifest_sha):
    require(report.get('status') == 'PASS_IMMUTABLE_PARITY_FUSED_GEN4_FIVE_STAGE_BANKED_CONSTRUCTION',
            'Replay did not complete')
    require(report.get('manifest_sha256') == manifest_sha and report.get('files') == 114,
            'Replay source mismatch')
    require(report.get('inputs_unchanged') is True and report.get('kappa') == KAPPA,
            'Replay changed inputs or historical exponent')
    require(set(report.get('fresh_stages', [])) == STAGES and len(report['fresh_stages']) == 9,
            'Incomplete fresh-stage coverage')
    require(set(report.get('negative_controls', [])) == {'omitted ' + s + ' stage' for s in STAGES},
            'Missing stage-omission controls')


def check_retained_evidence(package, source):
    inventory = read_json(package / 'EVIDENCE.json')
    require(inventory['candidate_head'] == CANDIDATE, 'Evidence head mismatch')
    require(digest((package / 'RESULTS.json').read_bytes()) == inventory['results_sha256'],
            'Changed reconciliation result')
    require(digest((package / 'SOURCE-CI.json').read_bytes()) == inventory['source_ci_metadata_sha256'],
            'Changed source CI metadata')
    ci = read_json(package / 'SOURCE-CI.json')
    require(ci['head_sha'] == CANDIDATE and ci['status'] == 'completed' and ci['conclusion'] == 'success',
            'CI metadata does not cover the candidate head')
    archive = (package / 'replay-evidence.tar.gz').read_bytes()
    require(digest(archive) == inventory['archive_sha256'], 'Changed evidence archive')
    files = archive_files(archive)
    require(set(files) == set(inventory['files']), 'Missing or additional evidence file')
    for name, pin in inventory['files'].items():
        require(digest(files[name]) == pin, 'Changed evidence: ' + name)
    report = json.loads(files['verification.json'])
    check_replay(report, source['candidate_manifest_sha256'])
    require(json.loads(files['certificate.json'])['kappa'] == KAPPA, 'Wrong evidence certificate')
    require({stage + '.json' for stage in STAGES} | {'target.json', 'replay.log'} <= set(files),
            'Missing per-stage replay evidence')
    target = json.loads(files['target.json'])
    expected_target = dict(
        status='PASS_EXACT_F2_TARGET_PREFIX_COMPRESSION', selected_groups=220,
        targets=880, deleted_prefix_adds=1100, inserted_setup_restore_adds=1320,
        remaining_payload_additions=626580,
        local_histogram_delta={'1': -220, '20': -220, '21': 220},
        negative_control='omitted target-prefix setup rejected')
    require(all(target.get(key) == value for key, value in expected_target.items()),
            'Wrong target-prefix evidence')
    for name, key in [('target-selection.json', 'selection_sha256'),
                      ('target_transform.py', 'transform_sha256')]:
        require(target.get(key) == source['candidate_files'][name]['sha256'],
                'Target receipt is from different source: ' + name)
    for direction in ('forward', 'inverse'):
        row = target[direction]
        require(row['all_formal_columns'] == 19930 and
                row['all_source_and_dirty_restored'] is True and
                row['arbitrary_target_contents_preserved'] is True and
                row['weighted_additions'] == 626580 and row['literal_unit_additions'] == 630100,
                'Incomplete target-prefix scalar evidence')
    return dict(status='PASS_RETAINED_REPLAY_BINDING', fresh_execution=False,
                retained_stages=sorted(STAGES), scope='Checks stored evidence; use --replay for a fresh run.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument('--replay', action='store_true')
    action.add_argument('--extract', action='store_true', help='Reconstruct source for inspection without executing it')
    parser.add_argument('--work', type=Path, help='New directory outside the repository')
    args = parser.parse_args()
    require((args.replay or args.extract) == (args.work is not None),
            '--extract/--replay requires --work, and --work requires an action')
    source, files = collect_candidate()
    schedule = check_selection(files)
    retained = check_retained_evidence(HERE, source)
    print('PASS_PR279_SOURCE_RECONCILIATION old=113 current=115 modified=10 added=2', flush=True)
    print(json.dumps({'schedule': schedule, 'retained_evidence': retained}, sort_keys=True), flush=True)
    if args.replay or args.extract:
        work = args.work.resolve()
        require(not work.exists() and not work.is_relative_to(ROOT.resolve()),
                'Work directory must be new and outside the repository')
        work.mkdir(parents=True)
        candidate = work / 'source'
        reconstruct(files, candidate)
        if args.extract:
            print('PASS_PR279_EXTRACTED_SOURCE ' + str(candidate))
            return
        output = work / 'replay'
        env = dict(os.environ, PYTHONUTF8='1')
        env.pop('PYTHONOPTIMIZE', None)
        command = [sys.executable, '-X', 'utf8', '-B', str(candidate / 'verify.py'),
                   '--output', str(output)]
        with (work / 'replay.log').open('wb') as log:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, env=env)
        require(result.returncode == 0, 'Candidate replay failed; see ' + str(work / 'replay.log'))
        check_replay(read_json(output / 'verification.json'), source['candidate_manifest_sha256'])
        evidence = read_json(HERE / 'EVIDENCE.json')
        require(canonical_records((output / 'records.bin.gz').read_bytes()) == evidence['emitted_word'],
                'Fresh literal instruction stream differs from the recorded replay')
        print('PASS_PR279_FRESH_REPLAY stages=9 kappa=' + KAPPA)


if __name__ == '__main__':
    main()

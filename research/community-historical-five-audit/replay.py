#!/usr/bin/env python3
"""Verify receipts, or extract/replay one complete historical contribution.

Receipt integrity is not a mathematical proof. --run executes the recorded
focused checks; inherited all-size and analytic hypotheses remain assumptions.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(name):
    return json.loads((HERE / name).read_text())


def sources():
    for name, digest in read('MANIFEST.json')['sha256'].items():
        require(hashlib.sha256((HERE / name).read_bytes()).hexdigest() == digest,
                'Changed evidence: ' + name)
    pool = {}
    with tarfile.open(HERE / 'sources.tar.gz', 'r:gz') as archive:
        for member in archive:
            require(member.isfile() and member.name not in pool, 'Invalid archive member')
            data = archive.extractfile(member).read()
            oid = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
            require(oid == member.name, 'Changed Git blob')
            pool[oid] = data
    rows = read('SOURCES.json')['pull_requests']
    require([r['number'] for r in rows] == [2, 4, 8, 9, 12], 'Wrong scope')
    coverage = {r['number']: r for r in json.loads(gzip.decompress(
        (ROOT / 'research/pr-reconciliation100-20261013/COVERAGE.json.gz').read_bytes()
    ))['pull_requests']}
    decisions = {d['number']: d for d in read('DISPOSITIONS.json')['pull_requests']}
    execution = {r['number']: r for r in read('EXECUTION.json')['pull_requests']}
    used = set()
    for row in rows:
        n = row['number']; meta = row['metadata']; prior = coverage[n]
        require(row['head'] == meta['headRefOid'] == prior['head'], 'Head mismatch')
        require(row['changed_files'] == prior['files'], 'Original diff changed')
        require(len(row['changed_files']) == meta['changedFiles'], 'Missing changed paths')
        files = {f['path']: f for f in row['files']}
        require(len(files) == len(row['files']), 'Repeated source path')
        for name, f in files.items():
            path = PurePosixPath(name)
            require(not path.is_absolute() and '..' not in path.parts and
                    '.git' not in path.parts, 'Unsafe source path')
            require(f['mode'] in ('100644', '100755'), 'Unsupported source mode')
            data = pool[f['blob']]; used.add(f['blob'])
            require(len(data) == f['bytes'] and hashlib.sha256(data).hexdigest() == f['sha256'],
                    'Changed source: ' + name)
        for f in row['changed_files']:
            require(f['new_blob'] == files[f['path']]['blob'] and
                    f['new_mode'] == files[f['path']]['mode'], 'Diff not fully retained')
        d = decisions[n]; e = execution[n]
        require(d['reviewed_head'] == d['current_head'] == e['head'] == row['head'], 'Evidence head mismatch')
        require(d['metadata']['author'] == meta['author'], 'Attribution mismatch')
        require(set(d['file_dispositions']) == {f['path'] for f in row['changed_files']}, 'Incomplete dispositions')
        for name, detail in d['file_dispositions'].items():
            require(detail['blob'] == files[name]['blob'] and detail['scope'], 'Unscoped file disposition')
        require(e['status'] == 'PASS' and e['commands'] and e['scope'], 'Incomplete execution')
        for name, digest in e['regenerated_sha256'].items():
            require(digest == files[name]['sha256'], 'Regeneration does not match original')
        if d['closure']:
            c = d['closure']
            require(c['headRefOid'] == row['head'] and c['state'] == d['github_state'] and
                    c['comment_url'] and c['integration_commit'], 'Incomplete closure')
    require(used == set(pool), 'Unexpected archive content')
    print('PASS historical five: complete exact-head sources, 126 changed paths, scoped execution receipts; no new kappa')
    return rows, pool


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pr', type=int, choices=[2, 4, 8, 9, 12])
    parser.add_argument('--extract', type=Path, help='new directory; never overwrites an existing tree')
    parser.add_argument('--run', action='store_true', help='execute focused checks after extraction; PR12 needs several GB RAM')
    args = parser.parse_args()
    if bool(args.pr) != bool(args.extract) or (args.run and not args.extract):
        parser.error('--pr and --extract are required together; --run requires both')
    rows, pool = sources()
    if not args.extract:
        return
    dest = args.extract.absolute()
    require(not dest.exists(), 'Extraction directory already exists')
    row = next(r for r in rows if r['number'] == args.pr)
    dest.mkdir(parents=True)
    for f in row['files']:
        path = dest / f['path']; path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(pool[f['blob']]); path.chmod(int(f['mode'][-3:], 8))
    print('Extracted original historical tree:', dest)
    if args.run:
        recipe = next(r for r in read('EXECUTION.json')['pull_requests'] if r['number'] == args.pr)
        for command in recipe['commands']:
            argv = [sys.executable if a == '{python}' else a for a in command]
            if argv == ['mkdir-build']:
                (dest / 'build/geometric-dimensions').mkdir(parents=True, exist_ok=True)
                continue
            print('Running:', argv, flush=True)
            subprocess.run(argv, cwd=dest, check=True)
        for f in row['files']:
            require(hashlib.sha256((dest / f['path']).read_bytes()).hexdigest() == f['sha256'],
                    'Regenerated original file differs: ' + f['path'])
        print('PASS focused replay; original tracked files unchanged')


if __name__ == '__main__':
    main()

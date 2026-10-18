#!/usr/bin/env python3
"""Offline receipt checks; --git additionally rechecks complete original PR diffs.

Not a mathematical verifier, live-head check, or approval of unresolved sources.
"""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import subprocess
import tarfile
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

def require(ok, message):
    if not ok:
        raise ValueError(message)

def load(name):
    return json.loads((HERE / name).read_text())

def blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--git', action='store_true')
    args = parser.parse_args()
    manifest = load('MANIFEST.json')
    for name, digest in manifest['sha256'].items():
        require(hashlib.sha256((HERE / name).read_bytes()).hexdigest() == digest, 'Changed evidence: ' + name)
    start = load('STARTING-SNAPSHOT.json')
    decisions = load('DISPOSITIONS.json')['pull_requests']
    coverage = json.loads(gzip.decompress((HERE / 'COVERAGE.json.gz').read_bytes()))['pull_requests']
    shared = json.loads(gzip.decompress((HERE / 'SHARED-CONTENT.json.gz').read_bytes()))
    snapshots = {p['number']: p for p in start['pull_requests']}
    covered = {p['number']: p for p in coverage}
    require(len(snapshots) == len(covered) == len(decisions) == 100, 'Wrong frozen scope')
    require(set(snapshots) == set(covered) == {d['number'] for d in decisions}, 'PR scope differs')
    residuals = Counter()
    with tarfile.open(HERE / 'pr3-original.tar.gz', 'r:gz') as archive:
        members = archive.getmembers()
        originals = {m.name: archive.extractfile(m).read() for m in members if m.isfile()}
    require(len(members) == len(originals) == len(covered[3]['files']), 'Incomplete original PR3 packet')
    for d in decisions:
        n = d['number']; s = snapshots[n]; c = covered[n]
        require(s['headRefOid'] == s['live']['headRefOid'] == c['head'] == d['reviewed_head'] == d['current_head'], f'#{n}: head differs')
        require(s['author'] == d['metadata']['author'], f'#{n}: attribution differs')
        require(c['base_ref_oid'] == s['live']['baseRefOid'], f'#{n}: source base differs')
        files = {f['path']: f for f in c['files']}
        require(len(files) == len(c['files']) == c['changed_paths'] == s['live']['changedFiles'], f'#{n}: incomplete file inventory')
        for f in c['files']:
            if f['screen'].startswith(('unmatched', 'unresolved')):
                residuals[(n, f['path'], f['new_mode'], f['new_blob'])] += 1
        if args.git:
            raw = subprocess.check_output(['git', 'diff', '--raw', '--no-abbrev', '--no-renames', '-z', c['merge_base'], c['head']], cwd=ROOT).split(b'\0')
            require(raw.pop() == b'', 'Invalid raw diff')
            pairs = {}
            for meta, name in zip(raw[::2], raw[1::2]):
                a,b,x,y,status = meta.decode().lstrip(':').split()
                pairs[name.decode()] = (a,b,x,y,status)
            require(pairs == {f['path']:(f['old_mode'],f['new_mode'],f['old_blob'],f['new_blob'],f['status']) for f in c['files']}, f'#{n}: Git diff differs')
            merge_base = subprocess.check_output(['git', 'merge-base', '--all', c['base_ref_oid'], c['head']], cwd=ROOT, text=True).splitlines()
            require(merge_base == [c['merge_base']], f'#{n}: merge base differs')
        ready = n in (3,90,183)
        if ready:
            require(all(type(v) is bool and v for v in d['review_completion'].values()), f'#{n}: premature completion')
            receipt = d['closure']
            require(receipt is not None and receipt['headRefOid'] == c['head'] and receipt['state'] == d['github_state'], f'#{n}: closure head/state mismatch')
            require(receipt['state'] == ('CLOSED' if n==90 else 'MERGED') and receipt['comment_url'] and receipt['integration_commit'], f'#{n}: incomplete closure receipt')
        require(c['changed_file_review_complete'] == ready, f'#{n}: unsupported coverage')
        require(d['review_completion']['changed_file_coverage'] == ready, f'#{n}: unsupported completion')
        if not ready:
            require(d['disposition'] == 'partially_reviewed' and d['unresolved_question'] and d['closure'] is None, f'#{n}: unsupported resolution')
            continue
        require(set(c['resolution']) == set(files), f'#{n}: missing file decision')
        for name, resolution in c['resolution'].items():
            if 'integrated_path' in resolution:
                content = (ROOT / resolution['integrated_path']).read_bytes()
                require(hashlib.sha256(content).hexdigest() == resolution['sha256'], 'Changed integrated source: ' + name)
                if not (n==183 and name=='docs/research/assembly-ceiling.md'):
                    require(blob(content) == files[name]['new_blob'], 'Unrecorded adaptation: ' + name)
            if n==3:
                require(blob(originals[name]) == files[name]['new_blob'], 'Original PR3 blob changed: ' + name)
        if n==90:
            for path in ('CONTRIBUTING.md','docs/reproducibility.md'):
                require('selected-result.json' in (ROOT/path).read_text(), 'Dynamic checkpoint link missing')
            require('Historical reviewed checkpoint: #596' in (ROOT/'docs/reproducibility.md').read_text(), 'Stale checkpoint heading')
    pool = Counter((o['number'],o['path'],row['mode'],row['blob']) for row in shared for o in row['occurrences'])
    require(pool == residuals, 'Shared content index lost a contextual occurrence')
    receipts = {r['number']:r for r in load('CLOSURES.json')['closures']}
    require(set(receipts) == {3,90,183}, 'Closure scope differs')
    for d in decisions:
        if d['number'] in receipts: require(d['closure'] == receipts[d['number']], 'Projected closure receipt differs')
    summary = load('SUMMARY.json')
    require(sum(c['changed_paths'] for c in coverage) == summary['changed_paths'], 'File total differs')
    require(len(shared) == summary['distinct_unmatched_blobs'] and sum(pool.values()) == summary['unmatched_entries'], 'Shared-work totals differ')
    for name, tests in [('pr183-tests.txt',22),('pr3-tests.txt',10)]:
        log = (HERE/name).read_text()
        require(f'Ran {tests} tests' in log and log.rstrip().endswith('OK'), 'Replay log incomplete: ' + name)
    require('anxkhn' in (ROOT/'CONTRIBUTORS.md').read_text() and 'eumemic' in (ROOT/'CONTRIBUTORS.md').read_text() and 'romainhedouin' in (ROOT/'CONTRIBUTORS.md').read_text(), 'Attribution missing')
    print(f'PASS reconciliation100: 100 exact-head inventories; {summary["changed_paths"]} paths; 3 completed dispositions, 97 explicit carry-forwards; no new kappa')

if __name__ == '__main__':
    main()

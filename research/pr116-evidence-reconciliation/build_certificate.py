#!/usr/bin/env python3
"""Capture immutable PR116 Git objects and already downloaded public CI evidence.
Apache-2.0; Ross Richardson, with substantial OpenAI Codex assistance.
"""
import argparse
import base64
from datetime import date
import hashlib
import json
from pathlib import Path
import subprocess

OLD = '97750ec74fc714638c0aa4f31aaa880e56cb8b4d'
NEW = '295a48a3b966428896057a98c6b4834c0b4b7416'
MERGE = '0db8566d07ae1fd7765d5d98fbb32ad22775ed32'
PREFIX = 'research/cube-deferred/'
BLOBS = ['README.md', 'SOURCE.json', 'validation.json', 'certificate.json']
WORKFLOW = '.github/workflows/cube-deferred.yml'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repository', type=Path, required=True)
    p.add_argument('--checks', type=Path, required=True)
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--jobs', type=Path, required=True)
    p.add_argument('--log', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--observed-on', type=date.fromisoformat, required=True,
                   help='UTC date on which the supplied API/log inputs were retrieved')
    a = p.parse_args()
    objects = {}

    def git(*args):
        return subprocess.check_output(['git', '-C', str(a.repository), *args])

    def add(oid, kind):
        if oid not in objects:
            data = git('cat-file', kind, oid)
            objects[oid] = dict(type=kind, base64=base64.b64encode(data).decode(),
                                sha256=hashlib.sha256(data).hexdigest())
            if kind == 'tree':
                for row in git('ls-tree', '-z', oid).split(b'\0'):
                    if row:
                        mode, typ, child = row.split(b'\t', 1)[0].split()
                        if typ == b'tree':
                            add(child.decode(), 'tree')
        return oid

    roots = {}
    for label, commit in [('historical', OLD), ('current', NEW), ('ci_checkout', MERGE)]:
        add(commit, 'commit')
        roots[label] = git('rev-parse', commit + '^{tree}').decode().strip()
        add(roots[label], 'tree')
    for commit in (OLD, NEW):
        for path in [PREFIX + n for n in BLOBS] + [WORKFLOW]:
            if path.endswith('validation.json') and commit == OLD:
                continue
            add(git('rev-parse', commit + ':' + path).decode().strip(), 'blob')
    checks = json.loads(a.checks.read_text())
    fields = ('id', 'name', 'head_sha', 'status', 'conclusion', 'details_url',
              'started_at', 'completed_at')
    snapshot = dict(
        check_endpoint=f'https://api.github.com/repos/CrocSwap/integer-mult-bounds/commits/{OLD}/check-runs?per_page=100',
        retrieved_on_utc=a.observed_on.isoformat(),
        total_count=checks['total_count'],
        checks=sorted([{k: row[k] for k in fields} for row in checks['check_runs']], key=lambda x: x['id']),
        cube_run=json.loads(a.run.read_text()), cube_jobs=json.loads(a.jobs.read_text()),
        combined_log_sha256=hashlib.sha256(a.log.read_bytes()).hexdigest(),
        log_excerpts={})
    previous = ''
    for line in a.log.read_text().splitlines():
        name = line.split('\t', 1)[0]
        if any(text in line for text in ('git log -1 --format=%H',
                'Run python3 research/cube-deferred/verify.py',
                'Ran 14 tests in', 'PASS read-only finite package verification;',
                'Run git diff --exit-code')) or 'git log -1 --format=%H' in previous:
            snapshot['log_excerpts'].setdefault(name, []).append(line)
        previous = line
    data = dict(schema=1, base='8bddbee377e2f3ce1f1247196c4b290d55767d20',
                commits=dict(historical=OLD, current=NEW, ci_checkout=MERGE),
                objects=objects, ci=snapshot)
    a.out.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(f'Captured {len(objects)} objects, {len(snapshot["checks"])} checks')


if __name__ == '__main__':
    main()

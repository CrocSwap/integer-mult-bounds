#!/usr/bin/env python3
"""Materialize one unchanged historical PR. This does not certify its claims."""
import argparse
import gzip
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GIT = ['git', '-c', 'maintenance.auto=false', '-c', 'gc.auto=0']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pr', type=int, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--fetch', action='store_true', help='Fetch the pinned archival tag if objects are unavailable')
    args = parser.parse_args()
    rows = json.loads(gzip.decompress((HERE/'SOURCES.json.gz').read_bytes()))['pull_requests']
    row = next((r for r in rows if r['number'] == args.pr), None)
    if row is None:
        parser.error('PR is outside this frozen batch')
    dest = args.destination.resolve()
    if dest.exists():
        parser.error('destination must not exist')
    if args.fetch:
        archive = json.loads((HERE/'ARCHIVE.json').read_text())
        subprocess.run([*GIT, 'fetch', '--no-tags', 'https://github.com/CrocSwap/integer-mult-bounds.git',
                        'refs/tags/'+archive['tag']], cwd=ROOT, check=True)
        fetched = subprocess.check_output([*GIT, 'rev-parse', 'FETCH_HEAD'], cwd=ROOT, text=True).strip()
        if fetched != archive['commit']:
            raise ValueError('Archival tag no longer resolves to the pinned commit')
    subprocess.run([*GIT, 'cat-file', '-e', row['head']+'^{commit}'], cwd=ROOT, check=True)
    subprocess.run([*GIT, 'worktree', 'add', '--detach', str(dest), row['head']], cwd=ROOT, check=True)
    print(f'PR #{args.pr}: {row["head"]} at {dest}')
    print('Use REVIEW.json and EXECUTION.json for scope, commands and known portability limits.')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Build offline review packets from gh-pr-view JSON and complete Git diffs.

No GitHub mutations, code execution, approval, or inference of scientific
equivalence. A matching blob is source identity, not a passing test.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import subprocess


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def tree(repo, commit):
    result = {}
    for row in git(repo, 'ls-tree', '-r', '-z', commit).split(b'\0'):
        if not row:
            continue
        meta, path = row.split(b'\t', 1)
        mode, kind, oid = meta.decode().split()
        result[path.decode()] = {'mode': mode, 'kind': kind, 'oid': oid}
    return result


def packet(repo, metadata, baseline, baseline_tree=None):
    head = git(repo, 'rev-parse', '--verify', metadata['headRefOid'] + '^{commit}').decode().strip()
    if head != metadata['headRefOid']:
        raise ValueError('Metadata must name a full immutable commit')
    base = git(repo, 'merge-base', head, metadata['baseRefOid']).decode().strip()
    before, after = tree(repo, base), tree(repo, head)
    current = baseline_tree if baseline_tree is not None else tree(repo, baseline)
    files = []
    for path in sorted(before.keys() | after.keys()):
        if before.get(path) == after.get(path):
            continue
        source, target = after.get(path), current.get(path)
        relation = ('identical' if source == target else
                    'absent_on_baseline' if target is None else 'different_on_baseline')
        files.append(dict(path=path, source=source, baseline=target,
                          change='delete' if source is None else 'add' if path not in before else 'modify',
                          baseline_relation=relation))
    groups = collections.Counter('/'.join(f['path'].split('/')[:2]) for f in files)
    checks = metadata.get('statusCheckRollup') or []
    return dict(schema_version=1, number=metadata['number'], title=metadata['title'],
                author=metadata['author'], url=metadata.get('url'), head=head,
                merge_base=base, baseline=baseline, files=files, path_groups=dict(groups),
                github_reported_file_count=len(metadata.get('files', [])),
                complete_git_file_count=len(files), body=metadata.get('body', ''),
                checks=[{k: c.get(k) for k in ('name', 'status', 'conclusion', 'detailsUrl')}
                        for c in checks],
                limits='Metadata and source identity only. Checks require source/command/coverage review; no green-badge inference.',
                decision=None)


def load_metadata(paths):
    """Capture one byte snapshot per input and validate the output identities."""
    rows, seen = [], set()
    for path in paths:
        raw = path.read_bytes()
        data = json.loads(raw)
        number = data.get('number') if isinstance(data, dict) else None
        if type(number) is not int or number <= 0:
            raise ValueError(f'{path}: PR number must be a positive integer')
        if number in seen:
            raise ValueError(f'{path}: duplicate PR number {number}')
        seen.add(number)
        rows.append((data, hashlib.sha256(raw).hexdigest()))
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', type=Path, default=Path.cwd())
    ap.add_argument('--baseline', required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('metadata', nargs='+', type=Path)
    args = ap.parse_args()
    try:
        inputs = load_metadata(args.metadata)
    except (OSError, ValueError) as error:
        ap.error(str(error))
    baseline = git(args.repo, 'rev-parse', '--verify', args.baseline + '^{commit}').decode().strip()
    args.output.mkdir(parents=True, exist_ok=False)
    bt = tree(args.repo, baseline)
    rows = []
    for metadata, metadata_sha256 in inputs:
        row = packet(args.repo, metadata, baseline, bt)
        row['metadata_sha256'] = metadata_sha256
        dest = args.output / f"{row['number']}.json"
        dest.write_text(json.dumps(row, indent=2) + '\n')
        rows.append(row)
    lines = ['# Review packets', '', f'Baseline: `{baseline}`.', '',
             'Source identity and triage only; no automatic approval.', '',
             '| PR | Author | Full diff files | GitHub list | Packages |',
             '| --- | --- | ---: | ---: | --- |']
    for row in rows:
        groups = ', '.join(f'{p} ({n})' for p, n in row['path_groups'].items())
        lines.append(f"| #{row['number']} | {row['author']['login']} | {len(row['files'])} | "
                     f"{row['github_reported_file_count']} | {groups} |")
    (args.output / 'INDEX.md').write_text('\n'.join(lines) + '\n')
    print(f'Wrote {len(rows)} packets; no GitHub state changed.')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Report pinned bytes that a branch changes, before review or a cold replay.

For every file a branch modifies or deletes relative to its merge base, this
computes the SHA-256 of the merge-base bytes and searches the merge-base tree
for that full 64-hex digest. A file containing the digest pins the old bytes.
Each pin is classified at the branch head:

- ``stale``: the pinning file still contains the old digest, so its check will
  fail (or silently describe bytes that no longer exist);
- ``repinned``: the pinning file was rewritten so the old digest is gone. This
  passes byte checks but may rewrite frozen evidence; review it as such;
- ``pinner_removed``: the pinning file was deleted on the branch.

Living records (the selected record, the task catalogue, docs and shared
scripts) are routinely updated while older packages keep their digests as
context, so their stale pins are advisory. Files under ``research/`` and
``upstream/`` are frozen by repository policy: exit status is 1 when one of
them has a stale pin, or for any stale pin with ``--strict``. Standard library
only.

Only full lowercase 64-hex digests in text files are found. Abbreviated
digests, other hash functions and pins computed over decompressed payloads or
canonical JSON are outside this search; an empty report is therefore not proof
that no frozen evidence changed. A trigger and drift guard, not a replay or a
mathematical check.

Prepared for apoursh with substantial Anthropic Claude assistance. Apache-2.0.
CR/LF framing and repository-selection repairs by OpenAI Codex, with
independent delegated regression review.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

# Retain direct script execution under -I; the shared helper uses stdlib only.
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from research_package import git_source_env
finally:
    sys.path.pop(0)

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = 'https://github.com/CrocSwap/integer-mult-bounds.git'
FROZEN_PREFIXES = ('research/', 'upstream/')


def git(root, *args, check=True, data=None):
    result = subprocess.run(['git', '--no-replace-objects', *args], cwd=root, input=data,
                            capture_output=True, check=False, env=git_source_env())
    if check and result.returncode != 0:
        raise SystemExit('git %s failed: %s' % (' '.join(args[:3]), result.stderr.decode(errors='replace').strip()))
    return result


def blobs(root, specs):
    """Return bytes for each ``rev:path`` spec, or None when it is absent."""
    if not specs:
        return {}
    found, framed = {}, []
    for spec in specs:
        if '\n' in spec or '\r' in spec:
            # Resolve a literal path without placing it in a line protocol.
            revision, path = spec.split(':', 1)
            listing = git(root, '--literal-pathspecs', 'ls-tree', '-z', '--full-tree',
                          revision, '--', path).stdout
            if not listing:
                found[spec] = None
                continue
            entries = listing.split(b'\0')
            if len(entries) != 2 or entries[1]:
                raise SystemExit('unexpected Git tree entries for: ' + repr(path))
            header, name = entries[0].split(b'\t', 1)
            mode, kind, oid = header.split()
            if name != path.encode() or len(oid) not in (40, 64) or any(c not in b'0123456789abcdef' for c in oid):
                raise SystemExit('unexpected Git tree entry for: ' + repr(path))
            found[spec] = git(root, 'cat-file', 'blob', oid.decode('ascii')).stdout if kind == b'blob' else None
        else:
            framed.append(spec)
    if not framed:
        return found
    out = git(root, 'cat-file', '--batch', data=''.join(s + '\n' for s in framed).encode()).stdout
    pos = 0
    for spec in framed:
        end = out.find(b'\n', pos)
        if end < 0:
            raise SystemExit('missing Git batch response header for: ' + repr(spec))
        header = out[pos:end]
        pos = end + 1
        if header == spec.encode() + b' missing':
            found[spec] = None
            continue
        fields = header.split()
        if len(fields) != 3 or not fields[2].isdigit():
            raise SystemExit('invalid Git batch response header for: ' + repr(spec))
        payload_end = pos + int(fields[2])
        if out[payload_end:payload_end + 1] != b'\n':
            raise SystemExit('invalid Git batch payload terminator for: ' + repr(spec))
        # Trees and other successful objects have payloads too.
        found[spec] = out[pos:payload_end] if fields[1] == b'blob' else None
        pos = payload_end + 1
    if pos != len(out):
        raise SystemExit('unexpected trailing bytes in Git batch response')
    return found


def changed_paths(root, base, head):
    rows = git(root, 'diff', '--name-status', '-z', '--no-renames', base, head).stdout.split(b'\0')
    changed = {}
    for status, name in zip(rows[0::2], rows[1::2]):
        status = status.decode()
        if status[:1] in 'MDT':
            changed[name.decode()] = 'deleted' if status[:1] == 'D' else 'modified'
    return changed


def check(root, base, head='HEAD'):
    root = Path(root).resolve()
    merge_base = git(root, 'merge-base', base, head).stdout.decode().strip()
    head_commit = git(root, 'rev-parse', head + '^{commit}').stdout.decode().strip()
    changed = changed_paths(root, merge_base, head_commit)
    old = blobs(root, [merge_base + ':' + p for p in changed])
    digests = {}
    for path in changed:
        data = old[merge_base + ':' + path]
        if data is not None:
            digests.setdefault(sha256(data).hexdigest(), []).append(path)
    pins = []
    if digests:
        patterns = [arg for d in sorted(digests) for arg in ('-e', d)]
        grep = git(root, 'grep', '-I', '-l', '-z', '-F', *patterns, merge_base, '--', check=False)
        if grep.returncode not in (0, 1):
            raise SystemExit('git grep failed: ' + grep.stderr.decode(errors='replace').strip())
        pinners = [entry.decode().split(':', 1)[1] for entry in grep.stdout.split(b'\0') if entry]
        before = blobs(root, [merge_base + ':' + p for p in pinners])
        after = blobs(root, [head_commit + ':' + p for p in pinners])
        for pinner in pinners:
            text_before = before[merge_base + ':' + pinner]
            text_after = after[head_commit + ':' + pinner]
            for digest, targets in digests.items():
                if digest.encode() not in text_before:
                    continue
                if text_after is None:
                    state = 'pinner_removed'
                elif digest.encode() in text_after:
                    state = 'stale'
                else:
                    state = 'repinned'
                for target in targets:
                    pins.append({'pinned': target, 'change': changed[target], 'pinner': pinner,
                                 'sha256': digest, 'state': state,
                                 'frozen': target.startswith(FROZEN_PREFIXES)})
    pins.sort(key=lambda row: (not row['frozen'], row['state'] != 'stale', row['pinned'], row['pinner']))
    return {'merge_base': merge_base, 'head': head_commit, 'changed_files': len(changed),
            'pinned_changed_files': len({row['pinned'] for row in pins}),
            'stale': sum(row['state'] == 'stale' for row in pins),
            'frozen_stale': sum(row['state'] == 'stale' and row['frozen'] for row in pins), 'pins': pins,
            'scope': 'Full lowercase SHA-256 hex digests in merge-base text files only; '
                     'not a replay, and an empty report does not prove frozen evidence is unchanged.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--base', default='main',
                        help='base revision; for a fork, fetch %s main and pass FETCH_HEAD or its commit' % CANONICAL)
    parser.add_argument('--head', default='HEAD')
    parser.add_argument('--json', action='store_true', help='print the full machine-readable report')
    parser.add_argument('--strict', action='store_true', help='also fail on stale pins of living records')
    args = parser.parse_args(argv)
    report = check(args.root, args.base, args.head)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print('merge base %s, head %s: %d modified or deleted files, %d with pinned old bytes, '
              '%d stale pins (%d on frozen research/upstream files)'
              % (report['merge_base'][:12], report['head'][:12], report['changed_files'],
                 report['pinned_changed_files'], report['stale'], report['frozen_stale']))
        for row in report['pins']:
            if row['frozen'] or args.strict:
                print('%-14s %s  pinned by  %s' % (row['state'].upper(), row['pinned'], row['pinner']))
        advisory = sorted({row['pinned'] for row in report['pins'] if not row['frozen']})
        if advisory and not args.strict:
            print('Advisory: living records with old-byte pins (list them with --strict): ' + ', '.join(advisory))
        print(report['scope'])
    failing = report['stale'] if args.strict else report['frozen_stale']
    return 1 if failing else 0


if __name__ == '__main__':
    sys.exit(main())

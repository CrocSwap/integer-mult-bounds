#!/usr/bin/env python3
"""Compare package working bytes with a commit before publishing hash receipts.

This is a byte-transport preflight, not a research verifier or CI-equivalence
claim. Prepared for ywz65 with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
from contextlib import closing
from pathlib import Path

from research_package import (
    canonical_relative_path,
    git,
    git_blobs,
    git_source_env,
    relative_file,
    require,
    source_pin,
)

ROOT = Path(__file__).resolve().parents[1]
MAX_SOURCE_METADATA_BYTES = 16 * 1024 * 1024
MAX_SOURCE_ROWS = 100000
MAX_SOURCE_COMMITS = 256


def history_git(root, *args):
    env = git_source_env()
    env['GIT_GRAFT_FILE'] = os.devnull
    env.pop('GIT_SHALLOW_FILE', None)
    return subprocess.run(['git', '--no-replace-objects', *args], cwd=root, env=env,
                          capture_output=True, check=False, timeout=30)


def publication_sources(root, package, commit):
    """Read bounded, immutable metadata without local replacements or grafts."""
    spec = commit + ':' + package + '/SOURCES.json'
    size = history_git(root, 'cat-file', '-s', spec)
    require(size.returncode == 0 and size.stdout.strip().isdigit(), 'missing publication SOURCES.json')
    require(int(size.stdout) <= MAX_SOURCE_METADATA_BYTES, 'source metadata byte limit exceeded')
    payload = history_git(root, 'cat-file', 'blob', spec)
    require(payload.returncode == 0 and len(payload.stdout) == int(size.stdout),
            'incomplete publication SOURCES.json')
    return json.loads(payload.stdout)


def source_history(root, package, commit):
    """Check committed pins against raw publication ancestry, not local refs.

    This is declared history availability, not full SOURCES.json validation
    or discovery of imports, archive references or runtime dependencies.
    """
    sources = publication_sources(root, package, commit)
    require(isinstance(sources, dict), 'SOURCES.json must be an object')
    base = sources.get('base_commit')
    require(isinstance(base, str) and re.fullmatch(r'[0-9a-f]{40,64}', base),
            'SOURCES.json base_commit must be an exact commit ID')
    rows = sources.get('files')
    require(isinstance(rows, list), 'SOURCES.json files must be a list')
    require(len(rows) <= MAX_SOURCE_ROWS, 'source row limit exceeded')
    commits = {base}
    for row in rows:
        require(isinstance(row, dict) and isinstance(row.get('path'), str),
                'SOURCES.json files rows need a string path')
        canonical_relative_path(row['path'])
        commits.add(source_pin(row, base).split(':', 1)[0])
    require(len(commits) <= MAX_SOURCE_COMMITS, 'source commit limit exceeded')
    shallow = history_git(root, 'rev-parse', '--is-shallow-repository')
    require(shallow.returncode == 0, 'cannot inspect Git history')
    require(shallow.stdout.strip() == b'false', 'source-history check requires full Git history')
    for pin in sorted(commits):
        resolved = history_git(root, 'rev-parse', '--verify', '--end-of-options', pin + '^{commit}')
        require(resolved.returncode == 0 and resolved.stdout.strip() == pin.encode('ascii'),
                'unavailable source commit: ' + pin)
        ancestor = history_git(root, 'merge-base', '--is-ancestor', pin, commit)
        require(ancestor.returncode in (0, 1),
                'Git ancestry check failed: ' + ancestor.stderr.decode('utf-8', errors='replace').strip())
        require(ancestor.returncode == 0,
                'source pin is not an ancestor of publication ' + commit + ': ' + pin
                + '; a separate cached branch/object is not publication history')
    return sorted(commits)


def check(root, package, ref='HEAD', check_source_history=False):
    require(re.fullmatch(r'research/[a-z0-9][a-z0-9-]*', package), 'package must be research/<slug>')
    manifest = json.loads(relative_file(root, package+'/VERIFY.json').read_text(encoding='utf-8'))
    require(isinstance(manifest, dict), 'VERIFY.json must be an object')
    inputs = manifest.get('inputs')
    require(isinstance(inputs, list), 'declare input paths in VERIFY.json')
    for name in inputs:
        canonical_relative_path(name)
    commit = git(root, 'rev-parse', '--verify', '--end-of-options', ref+'^{commit}').decode('ascii').strip()
    # Literal pathspecs keep wildcard filenames from selecting other files.
    records = git(root, '--literal-pathspecs', 'ls-tree', '-r', '-z', '--full-tree',
                  commit, '--', package, *inputs).split(b'\0')
    entries = {}
    for record in records:
        if not record:
            continue
        header, raw_name = record.split(b'\t', 1)
        mode, kind, obj = header.split()
        name = raw_name.decode('utf-8')
        require(mode in (b'100644', b'100755') and kind == b'blob',
                'commit contains a non-regular file: '+name)
        entries[name] = obj.decode('ascii')
    # New nonignored local checkers must not disappear from the publication.
    local = git(root, '--literal-pathspecs', 'ls-files', '-c', '-o', '--exclude-standard',
                '-z', '--', package).decode('utf-8').split('\0')
    expected = {name for name in local if name} | set(inputs)
    require(set(entries) == expected, 'working/commit file inventory differs: '+
            ', '.join(sorted(set(entries) ^ expected)))
    names = sorted(entries)
    require(names, 'empty package inventory')
    with closing(git_blobs(root, [entries[name] for name in names])) as blobs:
        # Advance the blob iterator once past its last yield, so its final
        # Git exit-status check runs before reporting success.
        for (_, committed), name in zip(blobs, names):
            working = relative_file(root, name).read_bytes()
            require(working == committed,
                    'working/commit bytes differ: '+name+' (working SHA256 '+
                    hashlib.sha256(working).hexdigest()+', commit SHA256 '+
                    hashlib.sha256(committed).hexdigest()+')')
    result = {'commit':commit, 'files':len(names), 'package':package}
    if check_source_history:
        result['source_history_commits'] = source_history(root, package, commit)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', required=True)
    parser.add_argument('--ref', default='HEAD', help='commit to publish; default HEAD')
    parser.add_argument('--check-source-history', action='store_true',
                        help='also require declared SOURCES.json pin commits in publication ancestry; full history only')
    args = parser.parse_args()
    try:
        result = check(ROOT, args.package, args.ref, args.check_source_history)
    except (OSError, ValueError, TypeError, subprocess.SubprocessError) as exc:
        parser.exit(1, str(exc)+'\n')
    print('PASS_RESEARCH_COMMIT_BYTES '+json.dumps(result))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Export committed package bytes and explicit inputs; check bundles without Git.

Tekalign, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from contextlib import closing
import hashlib
import io
import json
import ntpath
import os
from pathlib import Path
import re
import subprocess
import tarfile
import tempfile

from research_package import canonical_relative_path, git, git_blobs, require

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = '.research-export.json'
FORMAT = 'research-package-export-v1'


def unique_json_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate export JSON key: ' + key)
        result[key] = value
    return result


def bundle_relative_path(name):
    canonical_relative_path(name)
    # A POSIX-relative name such as C:/file or C:file can discard the extraction
    # directory on Windows. Apply the bundle policy on every producer/check host.
    require(not ntpath.splitdrive(name)[0], 'drive-qualified export path: ' + name)


def inventory(root, package, ref, input_ref=None):
    require(re.fullmatch(r'research/[a-z0-9][a-z0-9-]*', package),
            'package must be research/<slug>')
    commit = git(root, 'rev-parse', '--verify', '--end-of-options',
                 ref + '^{commit}').decode('ascii').strip()
    # Read declarations from the publication, never the working manifest.
    with closing(git_blobs(root, [commit + ':' + package + '/VERIFY.json'])) as rows:
        values = list(rows)
    manifest = json.loads(values[0][1], object_pairs_hook=unique_json_keys)
    require(isinstance(manifest, dict), 'VERIFY.json must be an object')
    inputs = manifest.get('inputs')
    require(isinstance(inputs, list), 'VERIFY.json inputs must be a list')
    for name in inputs:
        bundle_relative_path(name)
        require(name != RECEIPT, 'reserved export path: ' + name)
    require(len(inputs) == len(set(inputs)), 'duplicate declared input')
    contexts = [(commit, [package, *inputs])]
    if input_ref is not None:
        require(all(name != package and not name.startswith(package + '/') for name in inputs),
                'separate input commit requires external declared inputs')
        input_commit = git(root, 'rev-parse', '--verify', '--end-of-options',
                           input_ref + '^{commit}').decode('ascii').strip()
        contexts = [(commit, [package]), (input_commit, inputs)]
    records = []
    for tree, paths in contexts:
        if paths:
            records.extend(git(root, '--literal-pathspecs', 'ls-tree', '-r', '-z', '--full-tree',
                               tree, '--', *paths).split(b'\0'))
    entries = {}
    for record in filter(None, records):
        header, raw_name = record.split(b'\t', 1)
        mode, kind, obj = header.split()
        name = raw_name.decode('utf-8')
        bundle_relative_path(name)
        require(mode in (b'100644', b'100755') and kind == b'blob',
                'non-regular committed file: ' + name)
        require(name.startswith(package + '/') or name in inputs,
                'input must name one file, not a directory: ' + name)
        entries[name] = (int(mode, 8) & 0o777, obj.decode('ascii'))
    require(set(inputs) <= entries.keys(), 'missing declared input: ' +
            ', '.join(sorted(set(inputs) - entries.keys())))
    require(package + '/VERIFY.json' in entries, 'missing committed manifest')
    require_file_tree([*entries, RECEIPT])
    return commit, entries


def require_file_tree(names):
    """Regular-file members cannot also be implicit directories for other files."""
    files = set(names)
    for name in sorted(files):
        for parent in canonical_relative_path(name).parents:
            require(parent.as_posix() not in files,
                    'file/directory collision: ' + parent.as_posix() + ' and ' + name)


def member(name, data, mode=0o644):
    info = tarfile.TarInfo(name)
    info.size = len(data)
    info.mode = mode
    # TarInfo defaults give zero timestamps/owners and empty owner names.
    return info, io.BytesIO(data)


def export(root, package, ref, output, input_ref=None):
    # Resolve a moving input ref once, before collecting either snapshot.
    input_commit = (git(root, 'rev-parse', '--verify', '--end-of-options',
                        input_ref + '^{commit}').decode('ascii').strip()
                    if input_ref is not None else None)
    commit, entries = inventory(root, package, ref, input_commit)
    receipt = {'format': FORMAT, 'commit': commit, 'package': package, 'files': []}
    if input_commit is not None:
        receipt['input_commit'] = input_commit
    output = Path(output)
    require(not output.exists() and not output.is_symlink(), 'output already exists')
    # Publish only after Git's final status and the archive close both succeed.
    fd, name = tempfile.mkstemp(prefix='.research-export-', dir=output.parent)
    try:
        with os.fdopen(fd, 'wb') as stream, tarfile.open(fileobj=stream, mode='w', format=tarfile.PAX_FORMAT) as archive:
            names = sorted(entries)
            with closing(git_blobs(root, [entries[n][1] for n in names])) as rows:
                for (obj, data), path in zip(rows, names):
                    mode, expected = entries[path]
                    require(obj == expected, 'Git blob mismatch: ' + path)
                    archive.addfile(*member(path, data, mode))
                    receipt['files'].append({'path': path, 'mode': mode, 'size': len(data),
                                             'sha256': hashlib.sha256(data).hexdigest()})
            data = (json.dumps(receipt, sort_keys=True, indent=2) + '\n').encode('utf-8')
            archive.addfile(*member(RECEIPT, data))
        # Both operations refuse an existing destination, including one created
        # after the check above. Windows rename needs no hard-link permission;
        # POSIX rename would overwrite, so retain link there. The staging file
        # is in the destination directory and all writer handles are closed.
        if os.name == 'nt':
            os.rename(name, output)
        else:
            os.link(name, output)
    finally:
        Path(name).unlink(missing_ok=True)
    return receipt


def check_declared_inputs(path, receipt, seen):
    """Check the bundled manifest's file declarations without extraction or Git."""
    name = receipt['package'] + '/VERIFY.json'
    with tarfile.open(path, mode='r:') as archive:
        item = archive.getmember(name)
        require(item.isfile() and item.size <= 16 * 1024 * 1024,
                'invalid or oversized bundled manifest')
        with archive.extractfile(item) as stream:
            raw = stream.read(16 * 1024 * 1024 + 1)
    require(len(raw) == seen[name]['size'] and hashlib.sha256(raw).hexdigest() == seen[name]['sha256'],
            'bundled manifest changed during declaration check')

    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'duplicate bundled manifest key: ' + key)
            result[key] = value
        return result

    manifest = json.loads(raw.decode('utf-8'), object_pairs_hook=unique)
    require(isinstance(manifest, dict) and isinstance(manifest.get('inputs'), list),
            'bundled VERIFY.json needs an inputs list')
    inputs = manifest['inputs']
    require(len(inputs) <= 100000, 'bundled input count exceeds 100000')
    for entry in inputs:
        bundle_relative_path(entry)
        require(entry != RECEIPT, 'reserved declared input: ' + entry)
    declared = set(inputs)
    require(len(inputs) == len(declared), 'duplicate bundled input')
    missing = declared - seen.keys()
    require(not missing, 'missing bundled declared input: ' + ', '.join(sorted(missing)))
    extra = {entry for entry in seen if not entry.startswith(receipt['package'] + '/') and entry not in declared}
    require(not extra, 'undeclared external bundle file: ' + ', '.join(sorted(extra)))
    return len(inputs)


def check_bundle(path, check_inputs=False):
    """Check declared inventory, modes and payload hashes; never extract or execute."""
    seen, receipt = {}, None
    with tarfile.open(path, mode='r:') as archive:
        for item in archive:
            bundle_relative_path(item.name)
            require(item.isfile(), 'non-regular archive member: ' + item.name)
            require(item.name not in seen, 'duplicate archive member: ' + item.name)
            require(item.mode in (0o644, 0o755), 'unsupported mode: ' + item.name)
            digest = hashlib.sha256()
            with archive.extractfile(item) as data:
                if item.name == RECEIPT:
                    require(item.size <= 16 * 1024 * 1024, 'oversized export receipt')
                    receipt = json.load(data, object_pairs_hook=unique_json_keys)
                else:
                    for block in iter(lambda: data.read(1024 * 1024), b''):
                        digest.update(block)
            seen[item.name] = {'path': item.name, 'mode': item.mode, 'size': item.size,
                               'sha256': digest.hexdigest()}
    require_file_tree(seen)
    require(isinstance(receipt, dict) and receipt.get('format') == FORMAT, 'missing or invalid export receipt')
    require(isinstance(receipt.get('commit'), str) and
            re.fullmatch(r'(?:[0-9a-f]{40}|[0-9a-f]{64})', receipt['commit']), 'invalid commit label')
    if 'input_commit' in receipt:
        require(isinstance(receipt['input_commit'], str) and
                re.fullmatch(r'(?:[0-9a-f]{40}|[0-9a-f]{64})', receipt['input_commit']), 'invalid input commit label')
    require(isinstance(receipt.get('package'), str) and
            re.fullmatch(r'research/[a-z0-9][a-z0-9-]*', receipt['package']), 'invalid package label')
    files = receipt.get('files')
    require(isinstance(files, list), 'invalid receipt files')
    expected = {}
    for row in files:
        require(isinstance(row, dict), 'invalid receipt row')
        require(type(row.get('size')) is int and row['size'] >= 0, 'invalid receipt size')
        require(type(row.get('mode')) is int and row['mode'] in (0o644, 0o755),
                'invalid receipt mode')
        name = row.get('path')
        bundle_relative_path(name)
        require(name != RECEIPT and name not in expected, 'duplicate or reserved receipt path')
        expected[name] = row
    del seen[RECEIPT]
    require(seen == expected, 'bundle inventory, mode, size or SHA256 mismatch')
    require(receipt['package'] + '/VERIFY.json' in seen, 'missing bundled manifest')
    if check_inputs:
        receipt = {**receipt, 'declared_inputs_checked': check_declared_inputs(path, receipt, seen)}
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    make = commands.add_parser('export')
    make.add_argument('--package', required=True)
    make.add_argument('--ref', default='HEAD')
    make.add_argument('--input-ref', help='explicit commit for all external declared inputs; default: --ref')
    make.add_argument('--output', type=Path, required=True)
    check = commands.add_parser('check')
    check.add_argument('archive', type=Path)
    check.add_argument('--check-inputs', action='store_true',
                       help='also check bundled VERIFY.json input coverage; see docs/research/export-input-coverage.md')
    args = parser.parse_args()
    try:
        result = (export(ROOT, args.package, args.ref, args.output, args.input_ref) if args.command == 'export'
                  else check_bundle(args.archive, args.check_inputs))
    except (OSError, ValueError, TypeError, KeyError, RecursionError, tarfile.TarError, subprocess.SubprocessError) as exc:
        parser.exit(1, str(exc) + '\n')
    print('PASS_RESEARCH_EXPORT ' + json.dumps({k: result[k] for k in ('commit', 'package')} |
                                             {'files': len(result['files'])} |
                                             ({'input_commit': result['input_commit']} if 'input_commit' in result else {}) |
                                             ({'declared_inputs_checked': result['declared_inputs_checked']}
                                              if 'declared_inputs_checked' in result else {})))


if __name__ == '__main__':
    main()

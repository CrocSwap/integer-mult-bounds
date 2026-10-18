#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Export the exact PR2833 source from local Git objects, without fetching.

The output is the package directory itself, suitable for reproduce.py --source.
Jeremy Kothe and the retained PR2833 contributors retain source attribution.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tarfile

sys.dont_write_bytecode = True
HEAD = 'e9307b48d7d1b690939935ecef0f8e524e6d92f4'
PREFIX = 'research/gmx-t74-borrow43-handoff'
MANIFEST_SHA = 'c8ec4d1b7be08d2ad30730a07392ad9cb6d0222f2c35bef43c9a80a39b16e41f'
FILE_COUNT = 541


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def safe_relative(name):
    path = PurePosixPath(name)
    need(name and not path.is_absolute() and '..' not in path.parts
         and '\\' not in name and '\0' not in name,
         'unsafe source path: ' + name)
    need('__pycache__' not in path.parts and path.suffix != '.pyc',
         'bytecode is forbidden in exact source: ' + name)
    return path


def authenticate_payload(files):
    need('MANIFEST.json' in files, 'missing exact source manifest')
    need(digest(files['MANIFEST.json']) == MANIFEST_SHA, 'exact PR2833 manifest hash')
    pins = json.loads(files['MANIFEST.json'])
    need(isinstance(pins, dict) and len(pins) == FILE_COUNT, 'exact 541-entry manifest')
    for name in pins:
        safe_relative(name)
    actual = {name: digest(raw) for name, raw in files.items() if name != 'MANIFEST.json'}
    need(actual == pins, 'complete exact PR2833 file inventory and hashes')
    return pins


def authenticate_source(source):
    source = Path(source)
    need(source.is_dir() and not source.is_symlink(), 'source must be a real directory')
    files = {}
    for path in sorted(source.rglob('*')):
        name = path.relative_to(source).as_posix()
        safe_relative(name)  # Checks empty __pycache__ directories too.
        need(not path.is_symlink(), 'source symlink: ' + name)
        if path.is_file():
            files[name] = path.read_bytes()
        else:
            need(path.is_dir(), 'nonregular source entry: ' + name)
    return authenticate_payload(files)


def export(repo, out):
    repo, out = Path(repo).resolve(), Path(out).resolve()
    need(not out.exists() and not out.is_symlink(), 'fresh output directory required')
    check = subprocess.run(['git', '-C', str(repo), 'rev-parse', '--verify', HEAD + '^{commit}'],
                           check=True, capture_output=True, text=True)
    need(check.stdout.strip() == HEAD, 'exact locally available PR2833 commit')
    archive = subprocess.run(['git', '-C', str(repo), 'archive', '--format=tar', HEAD, PREFIX],
                             check=True, capture_output=True).stdout
    prefix = PurePosixPath(PREFIX)
    files = {}
    with tarfile.open(fileobj=io.BytesIO(archive), mode='r:') as package:
        for member in package.getmembers():
            path = PurePosixPath(member.name)
            need(not path.is_absolute() and '..' not in path.parts and '\\' not in member.name,
                 'unsafe Git archive path')
            if member.isdir() and (path == prefix or path in prefix.parents):
                continue
            need(path.is_relative_to(prefix), 'archive entry outside pinned package')
            relative = path.relative_to(prefix).as_posix()
            safe_relative(relative)
            need(member.isfile() or member.isdir(), 'archive links/special files forbidden')
            if member.isdir():
                continue
            need(relative not in files, 'duplicate archive file')
            stream = package.extractfile(member)
            need(stream is not None, 'missing archive file stream')
            files[relative] = stream.read()
    authenticate_payload(files)
    out.mkdir(parents=True, exist_ok=False)
    for name, raw in files.items():
        destination = out / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open('xb') as handle:
            handle.write(raw)
    authenticate_source(out)
    return {'status': 'PASS_EXACT_PR2833_SOURCE_EXPORT', 'head': HEAD,
            'manifest_sha256': MANIFEST_SHA, 'manifest_entries': FILE_COUNT,
            'source': str(out), 'network_fetch': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path.cwd(),
                        help='Local Git repository containing the pinned commit (default: cwd)')
    parser.add_argument('--out', type=Path, required=True, help='Fresh source package directory')
    args = parser.parse_args()
    print(json.dumps(export(args.repo, args.out), sort_keys=True))


if __name__ == '__main__':
    main()

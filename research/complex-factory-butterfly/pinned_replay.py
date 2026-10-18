#!/usr/bin/env python3
"""Replay PR931 with its authenticated historical source closure, offline.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
The original manifest, experiment, checker and frozen receipts are unchanged.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = PurePosixPath('research/complex-factory-butterfly')
BASE = '91a2094f2e022930069e8cfdc810a3ea1b81cd09'
MANIFEST_SHA256 = '752b8982b5ca566944d9f217a6ef6d3010b9c0ad2bb79a3353fce35b2d4fea1b'


class ReplayError(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise ReplayError(message)


def safe_relative(name):
    need(isinstance(name, str) and name and '\\' not in name and '\0' not in name,
         'invalid source path')
    path = PurePosixPath(name)
    need(bool(path.parts) and not path.is_absolute() and str(path) == name and
         all(part not in ('.', '..', '.git', '__pycache__') for part in path.parts) and
         path.suffix != '.pyc', 'unsafe source path: ' + name)
    return path


def manifest(path):
    raw = path.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == MANIFEST_SHA256,
         'historical SOURCES.json digest differs')
    pins = json.loads(raw)
    need(pins['base_commit'] == BASE, 'historical base differs')
    need(isinstance(pins['files'], dict) and len(pins['files']) == 29,
         'historical source inventory differs')
    for name, digest in pins['files'].items():
        safe_relative(name)
        need(isinstance(digest, str) and len(digest) == 64 and
             all(c in '0123456789abcdef' for c in digest), 'invalid source digest')
    return pins


def git(root, *args):
    result = subprocess.run(['git', '-C', str(root), *args],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    need(result.returncode == 0, 'Git history unavailable for ' + ' '.join(args) +
         '; use a checkout containing historical base ' + BASE)
    return result.stdout


def checkout_state(root):
    """Retain HEAD plus staged/unstaged and untracked inventory, without mutation."""
    top = Path(os.fsdecode(git(root, 'rev-parse', '--show-toplevel')).strip()).resolve()
    need(top == root.resolve(), 'package is not at its checkout root')
    return tuple(hashlib.sha256(git(root, *args)).hexdigest() for args in (
        ('rev-parse', 'HEAD'), ('status', '--porcelain=v1', '-z', '--untracked-files=all'),
        ('diff', '--binary', '--no-ext-diff'),
        ('diff', '--cached', '--binary', '--no-ext-diff')))


def unchanged(root, before):
    need(checkout_state(root) == before, 'source checkout changed during replay')


def export_sources(root, destination, pins):
    base = pins['base_commit']
    need(isinstance(base, str) and len(base) == 40 and
         all(c in '0123456789abcdef' for c in base), 'invalid historical base')
    git(root, 'cat-file', '-e', base + '^{commit}')
    for name, expected in sorted(pins['files'].items()):
        relative = safe_relative(name)
        raw = git(root, 'show', base + ':' + str(relative))
        need(hashlib.sha256(raw).hexdigest() == expected,
             'historical source digest differs: ' + name)
        target = destination.joinpath(*relative.parts)
        need(not target.exists(), 'occupied export path: ' + name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)


def copy_package(source, destination):
    destination.mkdir(parents=True, exist_ok=False)
    for path in sorted(source.iterdir()):
        need(not path.is_symlink(), 'package contains a symlink: ' + path.name)
        if path.name == '__pycache__' or path.suffix == '.pyc':
            continue
        need(path.is_file(), 'unexpected package directory: ' + path.name)
        safe_relative(path.name)
        shutil.copyfile(path, destination / path.name)


def verifier_environment():
    environment = dict(os.environ)
    for name in ('PYTHONOPTIMIZE', 'PYTHONPATH', 'PYTHONHOME'):
        environment.pop(name, None)
    environment['PYTHONDONTWRITEBYTECODE'] = '1'
    return environment


def verifier_command(script, out=None):
    # No -O: inherited native auditors deliberately retain their assertions.
    return [sys.executable, '-I', '-B', str(script)] + (
        ['--out', str(out)] if out is not None else [])


def replay(out=None, check_sources=False):
    pins = manifest(HERE / 'SOURCES.json')
    if out is not None:
        out = out.resolve()
        need(not out.exists(), 'output directory already exists')
        need(not out.is_relative_to(ROOT.resolve()),
             'output directory must be outside the source checkout')
    before = checkout_state(ROOT)
    try:
        with tempfile.TemporaryDirectory(prefix='factory-butterfly-pinned-') as temporary:
            exported = Path(temporary) / 'historical checkout'
            exported.mkdir()
            export_sources(ROOT, exported, pins)
            package = exported.joinpath(*PACKAGE.parts)
            copy_package(HERE, package)
            need(not list(exported.rglob('*.pyc')), 'bytecode entered the fresh export')
            if not check_sources:
                result = subprocess.run(verifier_command(package / 'verify.py', out),
                                        cwd=exported, env=verifier_environment())
                need(result.returncode == 0, 'historical verifier failed')
            need(not list(exported.rglob('*.pyc')), 'replay wrote bytecode into the export')
    finally:
        unchanged(ROOT, before)
    print(('PASS_PINNED_FACTORY_SOURCES' if check_sources else
           'PASS_PINNED_FACTORY_BUTTERFLY') + ' sources=29 base=' + BASE +
          ' checkout=unchanged')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='retain replay products in a new directory outside the checkout')
    parser.add_argument('--check-sources', action='store_true',
                        help='authenticate and export all sources without the full experiment')
    args = parser.parse_args()
    need(not (args.check_sources and args.out), '--out requires the full replay')
    replay(args.out, args.check_sources)


if __name__ == '__main__':
    try:
        main()
    except (ReplayError, OSError, KeyError, json.JSONDecodeError) as error:
        sys.exit('pinned replay: ' + str(error))

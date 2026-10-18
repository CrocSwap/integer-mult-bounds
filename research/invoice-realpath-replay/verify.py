#!/usr/bin/env python3
"""Source-bound portable replay of PR2158. ywz65/Codex, Apache-2.0."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import types

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
REPAIR = b"    work = work.resolve()\n"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def same(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


def load(raw):
    module = types.ModuleType('invoice_alias_fixture')
    module.__file__ = str(PACKAGE / 'audit.py')
    exec(compile(raw, module.__file__, 'exec'), module.__dict__)
    return module


def rejected_prepare(module, work, expected):
    try:
        module.prepare(work)
    except AssertionError as exc:
        require(str(exc) == expected, 'wrong rejection: ' + str(exc))
    else:
        raise ValueError('expected preparation rejection')


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    require(__debug__, 'Assertions must remain enabled for the unchanged invoice')
    manifest = json.loads((PACKAGE / 'SOURCES.json').read_bytes())
    for row in manifest['files'] + manifest['vendored_files']:
        if row['usage'] == 'input':
            require(sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'],
                    'source hash: ' + row['path'])
    fixed = (PACKAGE / 'audit.py').read_bytes()
    require(fixed.count(REPAIR) == 1, 'exact repair line')
    original = fixed.replace(REPAIR, b'')
    require(sha256(original).hexdigest() == manifest['derived_source']['sha256'], 'original source reconstruction')
    old, repaired = load(original), load(fixed)

    with tempfile.TemporaryDirectory(prefix='invoice-alias-controls.') as name:
        # Resolve the containing test root so the deliberate aliases below are
        # the only difference even when the operating-system temp root is aliased.
        root = Path(name).resolve()
        spelling = root / 'spelling'; spelling.mkdir()
        first = root / 'old'; first.mkdir()
        rejected_prepare(old, spelling / '..' / 'old', 'unsafe archive member')
        second = root / 'fixed'; second.mkdir()
        src, fixture = repaired.prepare(spelling / '..' / 'fixed')
        require(src == src.resolve() and fixture == fixture.resolve(), 'canonical returned roots')
        require((src / 'code/invoice_allcold.py').is_file(), 'actual invoice extracted')
        require((fixture / 'audit/PREFIX-AND-INVOICE.json').is_file(), 'actual fixture extracted')

        cases = [('../outside', tarfile.REGTYPE),
                 (str((root.parent / 'invoice-escape').resolve()), tarfile.REGTYPE),
                 ('link', tarfile.SYMTYPE), ('directory', tarfile.DIRTYPE)]
        for index, (member_name, member_type) in enumerate(cases):
            archive = root / ('bad-%d.tar' % index)
            with tarfile.open(archive, 'w') as stream:
                member = tarfile.TarInfo(member_name); member.type = member_type
                if member_type == tarfile.SYMTYPE:
                    member.linkname = '../outside'
                stream.addfile(member)
            module = load(fixed); module.ARCHIVE = archive
            work = root / ('bad-work-%d' % index); work.mkdir()
            rejected_prepare(module, work, 'unsafe archive member')
            require(not (work / 'outside').exists(), 'no traversal output')
        module = load(fixed); module.FIXTURE = root / 'bad-0.tar'
        work = root / 'bad-fixture'; work.mkdir()
        rejected_prepare(module, work, 'unsafe fixture member')

        # The child runs the actual minimally changed audit, with its original
        # assertion semantics. It retains all positive, mutation and downstream
        # checks and emits the entire receipt for a separate typed comparison.
        output = root / 'complete-receipt.json'
        run = subprocess.run([sys.executable, '-I', '-B', str(PACKAGE / 'audit.py'),
                              '--json', str(output)], capture_output=True, text=True, timeout=540)
        require(run.returncode == 0, run.stdout + run.stderr)
        actual = json.loads(output.read_bytes())
        expected = json.loads((PACKAGE / 'EXPECTED.json').read_bytes())
        require(same(actual, expected), 'complete typed receipt mismatch')
        require((actual['checked_mutants'], actual['rejected'], actual['accepted']) == (37, 31, 6),
                'declared invoice coverage')
        require(all(r['downstream'].startswith('assemble_rejected') for r in actual['records']
                    if r['verdict'] == 'accepted'), 'all accepted mutants rejected downstream')
    print('PASS_INVOICE_REALPATH_REPLAY original_alias_rejected repaired_alias_passed '
          'traversal_controls=5 mutants=37 invoice_rejected=31 downstream_rejected=6')


if __name__ == '__main__':
    main()

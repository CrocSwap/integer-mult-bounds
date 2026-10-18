#!/usr/bin/env python3
"""Opt-in prototype: reuse checked paths in selected-record source binding.

This fast check does not replay the construction. Run the selected record's
reproduce command
for the complete selected finite replay. Douglas Colkitt, with OpenAI Codex
assistance. Path reuse by Arham Tahir with substantial OpenAI Codex
assistance; primary-proof guards retain Mihir Srivastava and the source-closure
lineage. The production verifier and its frozen consumers are unchanged.
Apache-2.0.
"""
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def path(root, relative):
    p = (root / relative).resolve()
    require(p.is_relative_to(root.resolve()) and p.is_file(), 'Invalid selected file: ' + relative)
    return p


def package_files(package):
    """Yield each inventory path and its checked canonical path, without caching."""
    for p in package.rglob('*'):
        # rglob does not descend into directory symlinks. Reject them (and
        # dangling links) before is_file can silently remove them from coverage.
        require(not p.is_symlink() or p.is_file(),
                'Package symlink is not a regular file: ' + str(p))
        if p.is_file():
            resolved = p.resolve()
            require(resolved.is_relative_to(package), 'Package symlink escapes root')
            yield p, resolved


def check(record, root=ROOT):
    root = root.resolve()
    certificate_path = path(root, record['certificate'])
    certificate = json.loads(certificate_path.read_text())
    kappa = Fraction(record['kappa'])
    require(kappa > 0 and kappa == Fraction(certificate['kappa']), 'Selected kappa differs from finite certificate')
    require(kappa == Fraction(record['decimal']), 'Selected decimal differs from exact kappa')
    require(sha256(certificate_path.read_bytes()).hexdigest() == record['certificate_sha256'],
            'Selected certificate bytes changed')
    manifest_path = path(root, record['source_manifest'])
    manifest = json.loads(manifest_path.read_text())
    require(manifest.get('files'), 'Empty selected source inventory')
    verified_paths = set()
    if manifest.get('format') == 'repository-packages-sha256-v1':
        roots = manifest.get('package_roots', [])
        require(roots and len(roots) == len(set(roots)), 'Invalid package roots')
        actual = {}
        for relative in roots:
            package = (root / relative).resolve()
            require(package.is_relative_to(root.resolve()) and package != root.resolve()
                    and package.is_dir(), 'Invalid package root: ' + relative)
            for p, resolved in package_files(package):
                name = p.relative_to(root).as_posix()
                require(name not in actual, 'Overlapping package roots')
                actual[name] = sha256(p.read_bytes()).hexdigest()
                verified_paths.add(resolved)
    else:
        package = manifest_path.parent
        actual = {}
        for p, resolved in package_files(package):
            if p != manifest_path:
                actual[p.relative_to(package).as_posix()] = sha256(p.read_bytes()).hexdigest()
                verified_paths.add(resolved)
    require(actual == manifest['files'], 'Selected package inventory or bytes changed')
    # Canonical paths come from this invocation's containment checks, in both
    # inventory formats. No source digest or filesystem result survives a call.
    require(record['proof_supplements'], 'Missing construction proof supplement')
    for relative, digest in record['proof_supplements'].items():
        require(sha256(path(root, relative).read_bytes()).hexdigest() == digest,
                'Selected proof supplement changed: ' + relative)
        verified_paths.add(path(root, relative))
    require(path(root, record['proof']) in verified_paths,
            'Selected primary proof is not covered by a verified digest')
    # Other publication pointers retain their existence check; any explicit
    # digest above still applies.
    for key in ('review', 'validation'):
        path(root, record[key])
    return kappa


def main():
    require(not sys.flags.optimize, 'Assertions must remain enabled for the verification pipeline')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', type=Path, default=ROOT / 'certificates/selected-result.json',
                        help='Selected or historical checkpoint record to verify')
    args = parser.parse_args()
    record = json.loads(args.record.read_text())
    kappa = check(record)
    print('PASS selected record, exact kappa, original source inventory and proof supplement: ' + str(kappa))


if __name__ == '__main__':
    main()

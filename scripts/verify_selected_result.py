#!/usr/bin/env python3
"""Bind the published selection to its frozen finite certificate and proof files.

This fast check does not replay the construction. Run the selected record's
reproduce command
for the complete selected finite replay. Douglas Colkitt, with OpenAI Codex
assistance. Apache-2.0.
"""
from fractions import Fraction
from hashlib import sha256
from pathlib import Path, PurePosixPath
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def path(root, relative):
    p = (root / relative).resolve()
    require(p.is_relative_to(root.resolve()) and p.is_file(), 'Invalid selected file: ' + relative)
    return p


def explicit_file(root, relative):
    """Canonical, non-aliased input for an explicitly exported replay closure."""
    require(isinstance(relative, str), 'Invalid explicit input name')
    name = PurePosixPath(relative)
    require(bool(name.parts) and not name.is_absolute() and '..' not in name.parts
            and '\\' not in relative and name.as_posix() == relative,
            'Noncanonical explicit input: ' + relative)
    current = root
    for part in name.parts:
        current /= part
        require(not current.is_symlink(), 'Explicit input symlink: ' + relative)
    return path(root, relative)


def package_files(package):
    """Enumerate a closed package, retaining only contained regular-file aliases."""
    for p in package.rglob('*'):
        # rglob does not descend into directory symlinks. Reject them (and
        # dangling links) before is_file can silently remove them from coverage.
        require(not p.is_symlink() or p.is_file(),
                'Package symlink is not a regular file: ' + str(p))
        if p.is_file():
            require(p.resolve().is_relative_to(package), 'Package symlink escapes root')
            yield p


def supplement_bytes(root, relative, digest, historical=False):
    """Read exact proof bytes; opt-in historical checks retain their own context.

    The reviewed UTF-8 helper replaced an older checkpoint supplement. Admit
    only that exact successor and authenticate the original archived bytes.
    Current selected-record verification remains strict and never takes this path.
    Dennis, with substantial OpenAI Codex assistance; Apache-2.0.
    """
    raw = path(root, relative).read_bytes()
    if (historical and relative == 'scripts/verify_hpe_lean_binding.py'
            and digest == '52aa1d23641e4c716b43c98f6b883ad042087dd03a9d01369e8e6a735b07aa03'
            and sha256(raw).hexdigest() == '2fe5aac5828b1fdb79ff5e9ba87faef4db77e0c9339f362a1775b498a6d59e13'):
        original = path(root, 'scripts/historical-ci-inputs/verify_hpe_lean_binding.py').read_bytes()
        require(sha256(original).hexdigest() == digest, 'Historical HPE supplement changed')
        return original
    return raw


def check(record, root=ROOT, *, historical=False):
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
    explicit = manifest.get('format') == 'repository-files-sha256-v1'
    if explicit:
        actual = {name: sha256(explicit_file(root, name).read_bytes()).hexdigest()
                  for name in manifest['files']}
    elif manifest.get('format') == 'repository-packages-sha256-v1':
        roots = manifest.get('package_roots', [])
        require(roots and len(roots) == len(set(roots)), 'Invalid package roots')
        actual = {}
        for relative in roots:
            package = (root / relative).resolve()
            require(package.is_relative_to(root.resolve()) and package != root.resolve()
                    and package.is_dir(), 'Invalid package root: ' + relative)
            for p in package_files(package):
                name = p.relative_to(root).as_posix()
                require(name not in actual, 'Overlapping package roots')
                actual[name] = sha256(p.read_bytes()).hexdigest()
    else:
        package = manifest_path.parent
        actual = {p.relative_to(package).as_posix(): sha256(p.read_bytes()).hexdigest()
                  for p in package_files(package) if p != manifest_path}
    require(actual == manifest['files'], 'Selected package inventory or bytes changed')
    # The legacy manifest uses package-relative keys; the newer format uses
    # repository-relative keys. Bind the primary proof to the same checked files.
    inventory_root = root if explicit or manifest.get('format') == 'repository-packages-sha256-v1' else manifest_path.parent
    verified_paths = {(inventory_root / relative).resolve() for relative in actual}
    require(record['proof_supplements'], 'Missing construction proof supplement')
    for relative, digest in record['proof_supplements'].items():
        require(sha256(supplement_bytes(root, relative, digest, historical)).hexdigest() == digest,
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
    kappa = check(record, historical=args.record.resolve() != (ROOT / 'certificates/selected-result.json').resolve())
    print('PASS selected record, exact kappa, original source inventory and proof supplement: ' + str(kappa))


if __name__ == '__main__':
    main()

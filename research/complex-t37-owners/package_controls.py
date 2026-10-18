# SPDX-License-Identifier: Apache-2.0
"""Check package boundaries and assertion guards without changing source files."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from common import P, ROOT
from package import validate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    assert not args.out.exists() and not args.out.resolve().is_relative_to(ROOT)
    pins = validate()
    rejected = []
    args.out=args.out.resolve()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='t37-package-controls-',dir=args.out.parent) as directory:
        folder = Path(directory).resolve()
        assert folder.is_relative_to(args.out.parent)
        def case(name, mutate):
            dest = folder/name
            shutil.copytree(P, dest, ignore=shutil.ignore_patterns('__pycache__'))
            mutate(dest)
            try:
                validate(dest)
            except (ValueError, FileNotFoundError) as error:
                rejected.append(dict(name=name, reason=str(error)))
            else:
                raise AssertionError('Accepted invalid package: '+name)

        case('changed_owner_payload', lambda d: (d/'OWNERS.json.gz').write_bytes(b'changed'))
        case('missing_frozen_order', lambda d: (d/'ORDER.json').unlink())
        case('undeclared_package_file', lambda d: (d/'undeclared.txt').write_text('extra'))
        def changed_dependency(dest, relative):
            path = dest/'DEPENDENCY-PINS.json'
            pins = json.loads(path.read_text())
            pins[relative] = '0'*64
            path.write_text(json.dumps(pins))
            manifest = dest/'MANIFEST.json'
            contents = json.loads(manifest.read_text())
            contents['DEPENDENCY-PINS.json'] = hashlib.sha256(path.read_bytes()).hexdigest()
            manifest.write_text(json.dumps(contents))
        case('changed_ancestry_source', lambda d: changed_dependency(d, 'scripts/verify_frontier799.py'))
        case('dependency_path_escape', lambda d: changed_dependency(d, '../outside'))

    guards = ['verify.py', 'prepare.py', 'replay.py', 'final_binding.py', 'package.py',
              'independent/verify_construct.py', 'independent/check_t37.py',
              'independent/check_payload_controls.py', 'independent/all_t_bound.py']
    for relative in guards:
        result = subprocess.run([sys.executable, '-B', '-O', str(P/relative), '--help'],
                                capture_output=True, text=True)
        assert result.returncode != 0 and ('Assertions must remain enabled' in result.stderr or
               'Retained arithmetic assertions must stay enabled' in result.stderr), relative
        rejected.append(dict(name='optimized_python:'+relative, reason='Explicit assertion guard'))
    receipt = dict(status='PASS_T37_PACKAGE_CONTROLS', pins=pins, rejected=rejected)
    args.out.write_text(json.dumps(receipt, indent=2)+'\n')
    print(receipt['status'], len(rejected))


if __name__ == '__main__':
    main()

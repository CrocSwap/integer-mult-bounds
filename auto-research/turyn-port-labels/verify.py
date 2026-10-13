#!/usr/bin/env python3
"""Replay exact finite witnesses and the explicitly scoped cost comparisons."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent


def require(value, message):
    if not value:
        raise ValueError(message)


def verify_manifest():
    expected = json.loads((ROOT/'MANIFEST.json').read_text())
    actual = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in ROOT.rglob('*') if path.is_file()
              and path.name != 'MANIFEST.json' and '__pycache__' not in path.parts}
    require(actual == expected, 'Package file hashes and inventory match MANIFEST.json')
    return hashlib.sha256((ROOT/'MANIFEST.json').read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Write a replay receipt outside this package')
    parser.add_argument('--check-pins', action='store_true', help='Check package and inherited source hashes only')
    args = parser.parse_args()
    manifest = verify_manifest()
    sys.path.insert(0, str(ROOT/'code'))
    import geometry
    sources = geometry.source_check()
    if args.check_pins:
        print('PASS_TURYN_PORT_LABEL_PINS')
        return
    import costs
    geometry_receipt, cost_receipt = geometry.run(), costs.run()
    require(geometry_receipt == geometry.load('GEOMETRY-VERIFICATION.json'), 'Exact finite geometry receipt')
    require(cost_receipt == geometry.load('COSTS.json'), 'Exact scoped cost receipt')
    receipt = dict(status='PASS_TURYN_FULL_PORT_LABEL_RESEARCH', package_manifest_sha256=manifest,
                   sources=sources, geometry=geometry_receipt, costs=cost_receipt)
    if args.output:
        output = args.output.resolve()
        require(not output.is_relative_to(ROOT), 'Keep generated output outside the pinned package')
        output.mkdir(parents=True, exist_ok=True)
        (output/'REPLAY.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print(receipt['status'])


if __name__ == '__main__':
    main()

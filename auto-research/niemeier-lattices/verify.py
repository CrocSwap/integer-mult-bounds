#!/usr/bin/env python3
"""Replay the Niemeier geometry, scoped costs, and optional construction workbench."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import subprocess
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT/'code'/f'{name}.py')
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def canonical(value):
    return json.loads(json.dumps(value))


def verify_manifest():
    manifest = json.loads((ROOT/'MANIFEST.json').read_text())
    actual = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in ROOT.rglob('*') if path.is_file()
              and '__pycache__' not in path.parts and path.suffix != '.pyc'
              and path.name != 'MANIFEST.json'}
    require(actual == manifest['sha256'], 'Package file inventory and SHA256 manifest')


def replay_workbench():
    flags = ['-B', '-I']
    if sys.flags.optimize:
        flags.append('-' + 'O' * sys.flags.optimize)
    with tempfile.TemporaryDirectory(prefix='niemeier-workbench-') as temporary:
        output = Path(temporary)
        cases = [
            ('workbench/bit-routes/verify_portable.py', []),
            ('workbench/helper-routes/replay.py', [str(output/'helpers')]),
            ('workbench/continuation/tensor-routes/replay.py', [str(output/'tensor')]),
            ('workbench/paid-controller/verify_portable.py',
             ['--workspace', str(output/'paid')]),
            ('workbench/continuation/endpoint-costs/verify_portable.py',
             ['--workspace', str(output/'endpoints')]),
            ('workbench/root-probes/rectangles.py', ['--output', str(output/'rectangles.json')]),
        ]
        for relative, arguments in cases:
            if relative.endswith('verify_portable.py') and 'bit-routes' not in relative:
                if not sys.flags.optimize:
                    arguments.append('--normal')
            print(f'Replaying {relative}', flush=True)
            subprocess.run([sys.executable, *flags, str(ROOT/relative), *arguments], check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--workbench', action='store_true',
                        help='Also replay the construction and scoped-obstruction receipts')
    args = parser.parse_args()
    verify_manifest()
    census = canonical(module('catalog').census())
    require(census == json.loads((ROOT/'catalog.json').read_text()), 'Exact catalogue receipt')
    receipts = {
        'D24.json': module('d24').certify_d24(),
        'E8-CUBED.json': module('e8_cubed').certify_e8_cubed(),
        'E8-SECTIONS.json': module('e8_sections').certify_sections(),
    }
    for name, result in receipts.items():
        require(canonical(result) == json.loads((ROOT/'evidence'/name).read_text()),
                f'Exact geometric receipt: {name}')
    costs = module('costs')
    inputs = json.loads((ROOT/'evidence/COST-INPUTS.json').read_text())
    costs.verify_input_links(inputs, receipts)
    result = costs.run()
    require(canonical(result) == json.loads((ROOT/'evidence/COSTS.json').read_text()),
            'Exact scoped cost receipt')
    if args.output:
        output = args.output.resolve()
        require(not output.is_relative_to(ROOT), 'Replay output stays outside the research package')
        output.mkdir(parents=True, exist_ok=True)
        (output/'REPLAY.json').write_text(json.dumps(dict(catalog=census, geometry=receipts,
                                                       costs=result), indent=2, sort_keys=True)+'\n')
    print('PASS_NIEMEIER_GEOMETRY_AND_SCOPED_COSTS', flush=True)
    if args.workbench:
        replay_workbench()
        print('PASS_NIEMEIER_WORKBENCH')
    print('No complete supplier or new kappa is certified.')


if __name__ == '__main__':
    main()

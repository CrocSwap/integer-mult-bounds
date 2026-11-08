"""Registered exact receipt for the scoped recursive minimal-width audit."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from margin_sources import authenticate, need, opened
import affine_bounds
import source_inventory
import width_checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--emit', action='store_true', help='author-only regenerate complete evidence')
    parser.add_argument('--poison')
    args = parser.parse_args()
    if args.poison:
        sys.modules[args.poison] = ModuleType(args.poison)
        try:
            with opened():
                raise RuntimeError('stale numerical source cohort accepted')
        except ValueError as exc:
            need('cold word-margin cohort' in str(exc), 'intended stale-module guard')
        print('PASS_COLD_WORD_MARGIN_GUARD:' + args.poison)
        return
    count = authenticate()
    inventory = source_inventory.build()
    if not args.emit:
        source_inventory.verify(json.loads((HERE/'INVENTORY.json').read_text()), inventory)
    structural = source_inventory.controls(inventory)
    bounds = affine_bounds.certify()
    affine_controls = affine_bounds.controls()
    cold = []
    for module in ('layout', 'routes', 'controller', 'ordinary', 'bank_codec',
                   'stream_runner', 'linear_sign'):
        command = [sys.executable, '-I', '-Werror', '-B']
        if sys.flags.optimize:
            command.append('-O')
        result = subprocess.run(command+[str(HERE/'verify.py'), '--poison', module],
                                text=True, capture_output=True, timeout=30, check=False)
        need(result.returncode == 0 and
             result.stdout.strip() == 'PASS_COLD_WORD_MARGIN_GUARD:' + module,
             'fresh-process cold source control: ' + module + '\n' + result.stderr)
        cold.append(module)
    with opened():
        physical = width_checks.run()
    observed = dict(schema_version=1, base_commit='7c49fe32c55de02c2c873655c804b16e4c3fef0a',
                    source_files=count,
                    inventory_sha256=sha256(source_inventory.canonical(inventory).encode()).hexdigest(),
                    affine=bounds, physical=physical,
                    controls=dict(structural=structural, affine=affine_controls, cold=cold),
                    scope='all-size written word-width audit with exact affine certificates and scoped finite source corroboration; no full GL64 payload or new kappa')
    if args.emit:
        (HERE/'INVENTORY.json').write_text(json.dumps(inventory, indent=2)+'\n')
        (HERE/'RESULT.json').write_text(json.dumps(observed, indent=2)+'\n')
    else:
        expected = json.loads((HERE/'RESULT.json').read_text())
        need(source_inventory.canonical(expected)==source_inventory.canonical(observed),
             'complete typed word-margin scientific receipt')
    print('PASS_RECURSIVE_NATIVE_WORD_MARGINS')
    print(json.dumps(dict(affine_certificates=bounds['certificates'],
                          source_modules=len(inventory['modules']), divisors=len(inventory['divisors']),
                          actual_geometry_cases=physical['indices']['cases'],
                          actual_selected_records=len(physical['records']['cases']),
                          source_files=count, no_new_kappa=True), sort_keys=True))


if __name__ == '__main__':
    main()

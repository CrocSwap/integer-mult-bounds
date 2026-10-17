#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Run the bounded exact comparison, separate checker and full fractional screen."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def module(name):
    spec = importlib.util.spec_from_file_location('v45_' + name, HERE / (name + '.py'))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def controls(primary):
    record = primary.read(ROOT / primary.FRAME_EDITS)
    parent = primary.read(ROOT / primary.source_paths('base')['PR2942'])
    broken = copy.deepcopy(record)
    broken['frame_edits'][0]['gate'][1] += 1
    try:
        primary.stage1(parent, broken)
    except ValueError as error:
        need(str(error) == 'stage1 gate preimage', 'frame control wrong rejection')
    else:
        raise ValueError('changed frame-edit preimage accepted')
    original_root, original_package = primary.ROOT, primary.PACKAGE
    try:
        with tempfile.TemporaryDirectory(prefix='v45-binding-') as temp:
            root = Path(temp)
            row = {'path': 'source.json', 'usage': 'input', 'sha256': '0' * 64}
            (root / 'source.json').write_text('{}\n')
            (root / 'SOURCES.json').write_text(json.dumps({'files': [row]}))
            primary.ROOT = primary.PACKAGE = root
            try:
                primary.authenticated_sources()
            except ValueError as error:
                need(str(error) == 'input hash mismatch: source.json', 'source control wrong rejection')
            else:
                raise ValueError('changed source bytes accepted')
    finally:
        primary.ROOT, primary.PACKAGE = original_root, original_package
    return ['changed_frame_edit_preimage', 'source_hash_before_import']


def compute():
    primary, independent, cost = [module(name) for name in ('compare', 'independent', 'cost')]
    expected = json.loads((HERE / 'EXPECTED.json').read_bytes())
    actual = primary.compute()
    need(actual == expected, 'complete primary receipt differs')
    return {
        'status': 'PASS_V45_RECOVERY_TRANSFER',
        'no_new_kappa': True,
        'primary': {'providers': 2, 'stages_per_provider': 5,
                    'readout_rows': 12, 'fresh_dimensions': [4, 4, 0, 0, 0]},
        'independent': independent.run(expected),
        'cost': cost.verify_cost(ROOT),
        'additional_controls': controls(primary),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true')
    args = parser.parse_args()
    result = compute()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        need(result == json.loads((HERE / 'RESULT.json').read_bytes()), 'complete result differs')
        print('PASS_V45_RECOVERY_TRANSFER providers=2 stages=5 exact_cost_patterns=2551 no_new_kappa')


if __name__ == '__main__':
    main()

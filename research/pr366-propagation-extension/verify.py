#!/usr/bin/env python3
"""Full pinned parent replay, ten-gate propagation, official checks and price.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from construction import derive

if not __debug__:
    raise SystemExit('Assertions must be enabled')
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
PARENT = ROOT.parent/'pr364-kernel-extension'
PARENT_MANIFEST = '6f86aaaf6d926283c7a623d18f66ab8fd9339d1536eccc162c82607f867850fb'
EXPECTED_KAPPA = '804946219504150552042557/1000000000000000000000000000'
sys.path.insert(0, str(PARENT))
spec = importlib.util.spec_from_file_location('pinned_parent_verifier', PARENT/'verify.py')
parent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parent)


def portable(result):
    value = parent.portable(result)
    value['gain_over_parent'] = parent.serial(result['gain_over_parent'])
    value['parent_kappa'] = result['parent_kappa']
    return value


def extension(parent_output, output):
    """Continue the freshly completed parent pipeline using its native binaries."""
    from fractions import Fraction
    original = json.loads((parent_output/'CERTIFICATE.json').read_text())
    assert parent.portable(original) == json.loads((PARENT/'EXPECTED.json').read_text())
    assert parent.check_manifest(PARENT) == PARENT_MANIFEST
    word = output/'extension'
    derivation = derive(parent_output/'extension', word)
    negative = parent.controls(word)
    banks = parent.verify_banks(word)
    baseline = parent_output/'baseline'
    official = output/'official'
    official.mkdir()
    commands = [
        [sys.executable, '-B', str(parent.PARENT/'code/stage_official.py'), str(baseline/'parity'), str(word), str(official/'cin'), str(official/'cout')],
        [str(baseline/'legality'), str(official/'cin'), str(official/'cout'), str(official/'legality.json')],
        [str(baseline/'columns'), str(official/'cout/COHORT249-RECORDS.bin'), str(official/'columns.json')],
        [sys.executable, '-B', str(parent.PARENT/'code/nondeg.py'), str(word), str(baseline/'parity')],
    ]
    with (output/'physical-replay.txt').open('w') as log:
        for command in commands:
            subprocess.run(command, check=True, stdout=log, stderr=subprocess.STDOUT)
    legality = json.loads((official/'legality.json').read_text())
    columns = json.loads((official/'columns.json').read_text())
    assert legality['status'] == 'PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE'
    assert columns['status'] == 'PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL'
    assert columns['formal_columns_checked'] == 11930
    assert columns['local_odd_scalar_additions'] == 357762
    assert columns['payload_prefix_bits'] == 93
    result = parent.refine(word, parent.PARENT)
    assert str(result['kappa']) == EXPECTED_KAPPA
    assert result['width'] == banks['normalized_stock'] == 208646
    assert result['residual'] == banks['residual_rank_sum'] == 131846
    gain = result['kappa'] - Fraction(original['kappa'])
    assert gain == Fraction(32623579768771017, 10**25) > 0
    delta = {d: result['local_histogram'].get(d, 0) - original['local_histogram'].get(str(d), 0)
             for d in set(result['local_histogram']) | {int(d) for d in original['local_histogram']}}
    assert {d:c for d,c in delta.items() if c} == {1:-3, 2:-5, 3:4, 4:1, 9:3, 10:-3}
    result.update(status='PASS_TEN_GATE_PROPAGATION_FULL_REPLAY',
                  parent_manifest_sha256=PARENT_MANIFEST, parent_kappa=original['kappa'],
                  gain_over_parent=gain, derivation=derivation,
                  local_operator_and_controls=negative, banks=banks,
                  physical_legality=legality, physical_columns=columns,
                  benchmark_pr366_kappa=original['benchmark_pr366_kappa'])
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--boost-include', type=Path)
    parser.add_argument('--cxx')
    args = parser.parse_args()
    output = args.output.resolve()
    paths = [str(ROOT), str(output), sys.executable,
             str(args.boost_include or os.environ.get('BOOST_INCLUDE', '/usr/include')),
             args.cxx or os.environ.get('CXX', 'c++')]
    if any(any(c.isspace() for c in path) for path in paths):
        raise SystemExit('The pinned upstream shell verifier requires source, output, Python, compiler and Boost paths without whitespace.')
    assert not output.exists(), 'Use a fresh output directory'
    assert not output.is_relative_to(ROOT.parent), 'Output must be outside research packages'
    manifest = parent.check_manifest(ROOT)
    assert parent.check_manifest(PARENT) == PARENT_MANIFEST
    output.mkdir(parents=True)
    command = [sys.executable, '-B', str(PARENT/'verify.py'), '--output', str(output/'parent')]
    if args.boost_include: command += ['--boost-include', str(args.boost_include.resolve())]
    if args.cxx: command += ['--cxx', args.cxx]
    with (output/'parent-replay.txt').open('w') as log:
        subprocess.run(command, check=True, stdout=log, stderr=subprocess.STDOUT)
    result = extension(output/'parent', output)
    assert portable(result) == json.loads((ROOT/'EXPECTED.json').read_text()), 'Portable certificate differs'
    assert parent.check_manifest(ROOT) == manifest
    assert parent.check_manifest(PARENT) == PARENT_MANIFEST
    result.update(package_manifest_sha256=manifest,
                  parent_certificate_sha256=parent.sha(output/'parent/CERTIFICATE.json'),
                  physical_log_sha256=parent.sha(output/'physical-replay.txt'))
    (output/'CERTIFICATE.json').write_text(json.dumps(parent.serial(result), indent=2, sort_keys=True)+'\n')
    print(result['status'], EXPECTED_KAPPA, float(result['kappa']), flush=True)


if __name__ == '__main__':
    main()

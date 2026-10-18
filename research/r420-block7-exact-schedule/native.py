#!/usr/bin/env python3
"""Compile unchanged native checkers and check both words, with 5/9/11 stages.
Yuzhou Wang + OpenAI Codex, Apache-2.0. C++17 and Boost headers required.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('block7_verify', HERE / 'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
ROOT = v.ROOT
BASE = ROOT / 'research/e8-bit-carrier-skeleton'
CK = BASE / 'code/bit/checkers'


def command(args, log):
    with log.open('w') as out:
        subprocess.run(list(map(str, args)), check=True, stdout=out, stderr=subprocess.STDOUT)


def replay(out):
    # run() performs source pins, both complete finite words and all package controls.
    receipt = v.run(out)
    bindir = out / 'bin'
    bindir.mkdir()
    boost = os.environ.get('BOOST_INCLUDE', '/opt/homebrew/include' if sys.platform == 'darwin' else '/usr/include')
    common = [os.environ.get('CXX', 'c++'), '-O2', '-std=c++17', '-DHDIM=8', '-DNCOPY=9',
              '-DVPORTS=120', '-DRHELP=420', '-I' + str(BASE / 'portable-include'), '-I' + str(CK), '-I' + boost]
    command(common + [CK / 'legality_h.cpp', '-o', bindir / 'legality'], out / 'compile-legality.log')
    for k in (2, 4, 5):
        command(common + ['-DKPAIRS=' + str(k), CK / 'columns_k.cpp', '-o', bindir / ('columns' + str(k))],
                out / ('compile-columns' + str(k) + '.log'))
    summary = []
    for index, name in enumerate(('original', 'replacement')):
        wd = out / name
        expected = receipt['native'][index]
        command([sys.executable, '-I', '-B', BASE / 'code/bit/regression/stage_cohort.py',
                 wd / 'records', wd / 'records', wd / 'cin', wd / 'cout'], wd / 'stage.log')
        command([bindir / 'legality', wd / 'cin', wd / 'cout', wd / 'legality.json'], wd / 'legality.log')
        legality = json.loads((wd / 'legality.json').read_text())
        v.need(legality['status'] == 'PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE', 'native legality status')
        v.need(legality['common_frame_ADDs'] == expected['adds'] and legality['rank_mass'] == 5112 and
               legality['copies'] == legality['erasures'] == 9, 'native legality bill')
        stages = []
        for k in (2, 4, 5):
            result = wd / ('columns' + str(k) + '.json')
            command([bindir / ('columns' + str(k)), wd / 'cout/COHORT249-RECORDS.bin', result],
                    wd / ('columns' + str(k) + '.log'))
            checked = json.loads(result.read_text())
            status = ('PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL' if k == 2 else
                      'PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL')
            v.need(checked['status'] == status, 'native column status')
            v.need(checked['formal_columns_checked'] == 2 * k * 120 + 420, 'native column coverage')
            v.need(checked['local_scalar_additions'] == expected['adds'], 'native scalar count')
            v.need(checked['payload_prefix_upper'] == expected['payload'], 'independent prefix bill')
            v.need(len(checked['negative_controls']) == 6 * (k - 1) and
                   all(c['rejected'] for c in checked['negative_controls']), 'native bridge controls')
            stages.append({'stages': 2 * k + 1, 'columns': checked['formal_columns_checked'],
                           'bridge_controls': len(checked['negative_controls'])})
        summary.append({'word': name, 'adds': expected['adds'], 'rank_mass': 5112,
                        'payload_bits': expected['payload_bits'], 'stages': stages})
    evidence = {'status': 'PASS_R420_BLOCK7_NATIVE', 'words': summary}
    (out / 'native-receipt.json').write_text(json.dumps(evidence, sort_keys=True, indent=2) + '\n')
    print('PASS_R420_BLOCK7_NATIVE words=2 stages=5,9,11 bridge_controls=96')
    return evidence


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='fresh directory for binaries, words and all logs')
    args = parser.parse_args()
    if args.out:
        destination = args.out.resolve()
        v.need(destination != HERE and HERE not in destination.parents, 'output inside package')
        destination.mkdir(parents=True, exist_ok=False)
        replay(destination)
    else:
        with tempfile.TemporaryDirectory(prefix='r420-block7-native-') as tmp:
            replay(Path(tmp))

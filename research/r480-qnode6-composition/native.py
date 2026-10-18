#!/usr/bin/env python3
"""Unchanged C++ cohort checks for all eight verified subsets; Apache-2.0.

Prepared for @CubeJerry with OpenAI Codex assistance. Commands follow ToikY's
PR1003 harness and the PR503/510 native contract; checker sources are unchanged.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import shlex
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def run(input_dir, output):
    spec = importlib.util.spec_from_file_location('qnode6_verifier', HERE / 'verify.py')
    verify = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verify)
    verify.pins()
    certificate = json.loads((HERE / 'CERTIFICATE.json').read_text())
    verify.need(json.loads((input_dir / 'REPORT.json').read_text()) == certificate,
                'input replay certificate')
    output.mkdir(parents=True, exist_ok=False)
    compiler = shlex.split(os.environ.get('CXX', 'c++'))
    boost = Path(os.environ.get('BOOST_INCLUDE', '/usr/include')).resolve()
    verify.need((boost / 'boost/multiprecision/cpp_int.hpp').is_file(),
                'BOOST_INCLUDE must contain boost/multiprecision/cpp_int.hpp')
    bit = ROOT / 'research/e8-bit-carrier-skeleton/code/bit'
    checks = bit / 'checkers'
    flags = ['-O2', '-std=c++17', '-DHDIM=8', '-DNCOPY=9', '-DVPORTS=120', '-DRHELP=480',
             '-I' + str(ROOT / 'research/e8-bit-carrier-skeleton/portable-include'),
             '-I' + str(checks), '-I' + str(boost)]
    for name, source, extra in [('legality', 'legality_h.cpp', []),
                                 ('columns5', 'columns_h.cpp', []),
                                 ('columns9', 'columns_k.cpp', ['-DKPAIRS=4']),
                                 ('columns11', 'columns_k.cpp', ['-DKPAIRS=5'])]:
        verify.call(compiler + flags + extra + [checks / source, '-o', output / name],
                    output, 'compile-' + name)
    python = [sys.executable, '-I', '-B']
    results = []
    for row in certificate['subsets']:
        mask = row['mask']
        word = input_dir / f'mask-{mask}/word.json.gz'
        import gzip
        verify.need(verify.digest(verify.canonical(json.loads(gzip.decompress(word.read_bytes())))) ==
                    row['word_sha256'], 'native input word binding')
        work = output / f'mask-{mask}'
        work.mkdir()
        records, cin, cout = (work / d for d in ('records', 'cin', 'cout'))
        verify.call(python + [bit / 'export_records.py', word, records], work, 'export')
        verify.need(hashlib.sha256((records / '249-records.bin').read_bytes()).hexdigest() ==
                    row['records_sha256'], 'native exporter record binding')
        verify.call(python + [bit / 'regression/stage_cohort.py', records, records, cin, cout],
                    work, 'cohort')
        verify.call([output / 'legality', cin, cout, cout / 'legality.json'], work, 'legality')
        legality = json.loads((cout / 'legality.json').read_text())
        verify.need(legality['status'] ==
                    'PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE', 'native legality')
        verify.need(legality['copies'] == legality['erasures'] == 9, 'native copies')
        verify.need(legality['common_frame_ADDs'] == row['adds'] and legality['rank_mass'] == 5592,
                    'native complete invoice')
        stages = {}
        for k in (5, 9, 11):
            receipt = cout / f'columns{k}.json'
            verify.call([output / f'columns{k}', cout / 'COHORT249-RECORDS.bin', receipt],
                        work, f'columns{k}')
            data = json.loads(receipt.read_text())
            expected = ('PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL' if k == 5
                        else 'PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL')
            verify.need(data['status'] == expected, 'native formal columns')
            verify.need(data['formal_columns_checked'] == 120 * (k - 1) + 480,
                        'native complete column count')
            verify.need(len(data['negative_controls']) == 3 * (k - 3) and
                        all(x['rejected'] is True for x in data['negative_controls']),
                        'native omitted-bridge controls')
            verify.need(int(data['payload_prefix_upper']) == int(row['precision']['payload']) and
                        data['local_scalar_additions'] == row['adds'], 'independent native precision')
            expected_histogram = [[int(rank), count] for rank, count in
                                  sorted(certificate['paid_profile'].items(), key=lambda x: int(x[0]))]
            verify.need(data['local_raw_H'] == legality['paid_histogram'] ==
                        expected_histogram, 'native paid histogram')
            # Only non-mathematical timing and temporary input pathname are removed.
            data.pop('seconds', None)
            data.pop('local_scalar_stream', None)
            stages[str(k)] = data
        legality.pop('seconds', None)
        results.append(dict(mask=mask, legality=legality, stages=stages))
        print(f'PASS_NATIVE_SUBSET mask={mask} stages=5,9,11 bridges_rejected=48', flush=True)
    report = dict(format='r480-qnode6-native-v1', certificate_sha256=verify.digest(
                  verify.canonical(certificate)), subsets=results,
                  normalization='Remove seconds and local_scalar_stream only; retain all other native fields.')
    (output / 'ENVIRONMENT.json').write_text(json.dumps(dict(
        python=sys.version, platform=platform.platform(),
        compiler=subprocess.check_output(compiler + ['--version'], text=True),
        boost_version_header_sha256=hashlib.sha256((boost / 'boost/version.hpp').read_bytes()).hexdigest(),
        flags=flags), indent=2, sort_keys=True) + '\n')
    (output / 'NATIVE.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path, help='output of the complete verify.py command')
    parser.add_argument('output', type=Path, help='new directory')
    parser.add_argument('--write-certificate', type=Path, help='development: new native receipt')
    args = parser.parse_args()
    report = run(args.input.resolve(), args.output.resolve())
    if args.write_certificate:
        with args.write_certificate.open('x') as target:
            json.dump(report, target, indent=2, sort_keys=True)
            target.write('\n')
    elif report != json.loads((HERE / 'NATIVE.json').read_text()):
        raise ValueError('native certificate drift')
    print('PASS_R480_QNODE6_NATIVE subsets=8 stages=5,9,11 bridge_controls=384')

#!/usr/bin/env python3
"""Fresh unchanged C++ legality and 5/9/11-stage replays for all three words.

Adapted from Cinna Davis (@1337isnot1337)'s PR973 harness, which adapts
Jerry Chen (@CubeJerry)'s PR906 native harness. Hanson Sun (@bbMisk).
Substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import platform
import shlex
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BIT = ROOT / 'research/e8-bit-carrier-skeleton/code/bit'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def run(command, logfile):
    result = subprocess.run([str(x) for x in command], capture_output=True, text=True)
    logfile.write_text(result.stdout + result.stderr)
    need(result.returncode == 0, 'command failed; see ' + str(logfile))
    return result.stdout


def native(output, compiler, boost):
    output.mkdir(parents=True, exist_ok=False)
    command = [sys.executable, '-I', '-B', HERE / 'verify.py', '--output', output / 'python']
    run(command, output / 'python.log')
    reference = json.loads((output / 'python/RESULT.json').read_text())
    includes = ['-I' + str(BIT / 'checkers'), '-I' + str(boost),
                '-I' + str(ROOT / 'research/e8-bit-carrier-skeleton/portable-include')]
    common = compiler + ['-O2', '-std=c++17', '-DHDIM=8', '-DNCOPY=9',
                         '-DVPORTS=111', '-DRHELP=439'] + includes
    configurations = [('legality', 'legality_h.cpp', []),
                      ('columns_h', 'columns_h.cpp', [])] + [
        ('columns_k' + str(k), 'columns_k.cpp', ['-DKPAIRS=' + str(k)]) for k in (2, 4, 5)]

    def compile_one(config):
        name, source, flags = config
        run(common + flags + [BIT / 'checkers' / source, '-o', output / name],
            output / ('compile-' + name + '.log'))

    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(compile_one, configurations))
    summary = {}
    for name in ('baseline', 'prior973', 'candidate'):
        record_dir = output / 'python' / (name + '-records')
        cin, cout = output / (name + '-in'), output / (name + '-out')
        run([sys.executable, '-I', '-B', BIT / 'regression/stage_cohort.py',
             record_dir, record_dir, cin, cout], output / (name + '-stage.log'))
        run([output / 'legality', cin, cout, cout / 'legality.json'],
            output / (name + '-legality.log'))
        legality = json.loads((cout / 'legality.json').read_text())
        py = reference['words'][name]
        for field, local in [('common_frame_ADDs', 'additions'), ('rank_mass', 'rank_mass'),
                             ('nested_MOVEs', 'moves'), ('copies', 'copies'), ('records', 'records')]:
            need(legality[field] == py[local], 'native legality mismatch: ' + field)
        need({str(k): v for k, v in legality['paid_histogram']} == py['paid_profile'],
             'native paid profile mismatch')
        columns = {}
        for binary, _, _ in configurations[1:]:
            receipt = cout / (binary + '.json')
            run([output / binary, cout / 'COHORT249-RECORDS.bin', receipt],
                output / (name + '-' + binary + '.log'))
            data = json.loads(receipt.read_text())
            need(data['local_scalar_additions'] == py['additions'], 'native ADD mismatch')
            need(data['payload_prefix_upper'] == py['payload_upper'], 'native payload mismatch')
            need(data['payload_prefix_bits'] == py['payload_bits'], 'native payload bits mismatch')
            bounds = [int(x['cancellation_free_signed_row_l1_upper'])
                      for x in data['signed_lift_prefix']]
            need(bounds == [py['forward_positive_bound'], py['reverse_positive_bound']],
                 'native positive prefix mismatch')
            need({str(k): v for k, v in data['local_raw_H']} == py['paid_profile'],
                 'native column profile mismatch')
            expected_columns = {'columns_h': 883, 'columns_k2': 883,
                                'columns_k4': 1327, 'columns_k5': 1549}[binary]
            need(data['formal_columns_checked'] == expected_columns, 'native coverage mismatch')
            expected_controls = {'columns_h': 6, 'columns_k2': 6,
                                 'columns_k4': 18, 'columns_k5': 24}[binary]
            need(len(data['negative_controls']) == expected_controls and
                 all(x['rejected'] for x in data['negative_controls']), 'bridge control failure')
            data.pop('seconds')
            data.pop('local_scalar_stream')
            columns[binary] = data
        need(columns['columns_h'] == columns['columns_k2'], 'five-stage regression mismatch')
        summary[name] = {'legality': legality, 'columns': columns}
    result = {'status': 'PASS_R439_B509_BOOLEAN_NATIVE', 'words': summary,
              'distinct_omitted_bridge_controls': 144,
              'expected_python_receipt_sha256': hashlib.sha256((HERE / 'EXPECTED.json').read_bytes()).hexdigest()}
    (output / 'NATIVE.json').write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    environment = {'python': sys.version, 'platform': platform.platform(),
                   'compiler': run(compiler + ['--version'], output / 'compiler.log').splitlines()[0],
                   'boost_cpp_int_sha256': hashlib.sha256(
                       (boost / 'boost/multiprecision/cpp_int.hpp').read_bytes()).hexdigest()}
    (output / 'ENVIRONMENT.json').write_text(json.dumps(environment, sort_keys=True, indent=2) + '\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='fresh directory; default temporary')
    parser.add_argument('--cxx', default=os.environ.get('CXX', 'c++'))
    parser.add_argument('--boost-include', type=Path,
                        default=Path(os.environ.get('BOOST_INCLUDE', '/usr/include')))
    parser.add_argument('--write-expected', action='store_true', help='explicit receipt regeneration')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='r439-frame509-native-') as temporary:
        result = native(args.output or Path(temporary) / 'replay', shlex.split(args.cxx),
                        args.boost_include)
    expected = HERE / 'NATIVE.json'
    if args.write_expected:
        expected.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    else:
        need(result == json.loads(expected.read_text()), 'committed native receipt mismatch')
    print('PASS_R439_B509_BOOLEAN_NATIVE words=3 columns=883/1327/1549 '
          'bridge_controls=144 five_stage_regression=PASS')


if __name__ == '__main__':
    main()

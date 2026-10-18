#!/usr/bin/env python3
"""Replay two R420 words through unchanged, pinned native cohort checkers.

Usage: python3 -B native.py ORIGINAL.json.gz CANDIDATE.json.gz OUTPUT_DIR
Requires a C++17 compiler and Boost headers. CXX and BOOST_INCLUDE are supported.
Outputs must be outside this repository. No hosted or outer assembly is run.
Jerry Lin, with substantial OpenAI Codex assistance; Apache-2.0.
"""
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import shlex
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / 'research/e8-bit-carrier-skeleton'
BIT = PACKAGE / 'code/bit'
CHECKERS = BIT / 'checkers'
PINS = {
    'code/bit/export_records.py': '8a5999601f917dbb492bb9ae9a344611f18cc7cedc53dc3c76496a369e530eb3',
    'code/bit/regression/stage_cohort.py': '6c288f6f234b528c1a7c0a4adfb724e91e0fe6b18c8dffad96af3f973de1829a',
    'code/bit/checkers/legality_h.cpp': '6c1ef2b24e57781d6951c172a1024fc4300e6fd392c9d6672079a7806ab663b3',
    'code/bit/checkers/columns_h.cpp': 'd1297f9052be4f2496e1ff2a77e4db2c0cdbd7d460d489b4c03e50bf317238ce',
    'code/bit/checkers/columns_k.cpp': '1c344d18fcd494eeca93e259f10cafae7705780e6592f6dcb35b34752dab9bc2',
    'code/bit/checkers/json.hpp': 'aaf127c04cb31c406e5b04a63f1ae89369fccde6d8fa7cdda1ed4f32dfc5de63',
    'portable-include/bits/stdc++.h': '420094be2af295eed03a983dd66debbbe9cfb78d8252859f4498a615a0074b99',
}


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def read_json(path):
    with (gzip.open(path, 'rt') if str(path).endswith('.gz') else open(path)) as stream:
        return json.load(stream)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(word):
    return digest(json.dumps(word, sort_keys=True, separators=(',', ':')).encode())


def run(args, log, reject=False):
    result = subprocess.run([str(x) for x in args], text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    log.write_text(result.stdout)
    need((result.returncode != 0) if reject else (result.returncode == 0),
         f'Unexpected exit {result.returncode}: {shlex.join([str(x) for x in args])}; see {log}')
    return result


def export(word_path, directory):
    directory.mkdir(parents=True, exist_ok=True)
    run([sys.executable, '-I', '-B', BIT / 'export_records.py', word_path, directory / 'records'],
        directory / 'export.log')
    run([sys.executable, '-I', '-B', BIT / 'regression/stage_cohort.py', directory / 'records',
         directory / 'records', directory / 'cin', directory / 'cout'], directory / 'stage.log')


def replay(word_path, directory, binaries):
    word = read_json(word_path)
    need((word['h'], word['v'], word['R'], len(word['ret'])) == (8, 120, 420, 9), 'Not an R420 word')
    export(word_path, directory)
    cout = directory / 'cout'
    run([binaries / 'legality', directory / 'cin', cout, cout / 'legality.json'], directory / 'legality.log')
    legality = read_json(cout / 'legality.json')
    need(legality['status'] == 'PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE', 'Legality failed')
    need(legality['copies'] == legality['erasures'] == 9, 'Wrong copy count')
    receipts = {}
    for name, stages, omissions in [('columns_h', 5, 6), ('columns_k2', 5, 6),
                                     ('columns_k4', 9, 18), ('columns_k5', 11, 24)]:
        run([binaries / name, cout / 'COHORT249-RECORDS.bin', cout / (name + '.json')], directory / (name + '.log'))
        receipt = read_json(cout / (name + '.json'))
        suffix = 'FIVE_STAGE' if stages == 5 else 'BRIDGED_STAGE'
        need(receipt['status'] == f'PASS_NEW_COHORT249_ALL_{suffix}_FORMAL_COLUMNS_AND_PREFIX_BILL', 'Columns failed')
        need(receipt['formal_columns_checked'] == (stages - 1) * 120 + 420, 'Wrong column count')
        need(len(receipt['stages']) == stages, 'Wrong stage count')
        need(receipt['bridge_additions'] == omissions * 120, 'Wrong bridge count')
        controls = receipt['negative_controls']
        need(len(controls) == omissions and all(x['rejected'] for x in controls), 'Omitted bridge accepted')
        need(dict(receipt['local_raw_H']) == dict(legality['paid_histogram']), 'Histogram mismatch')
        need(receipt['local_scalar_additions'] == legality['common_frame_ADDs'], 'ADD count mismatch')
        receipts[name] = receipt
    five = receipts['columns_h']
    need({k: v for k, v in five.items() if k != 'seconds'} ==
         {k: v for k, v in receipts['columns_k2'].items() if k != 'seconds'}, 'K2 regression failed')
    bounds = five['signed_lift_prefix']
    need([x['reverse'] for x in bounds] == [False, True], 'Wrong prefix orientations')
    forward, backward = [int(x['cancellation_free_signed_row_l1_upper']) for x in bounds]
    local_payload = 64 * forward ** 3 * backward ** 2
    need(local_payload == int(five['payload_prefix_upper']) < 2 ** 104, 'Wrong five-stage prefix bound')
    schedule_bounds = {}
    for pairs in (2, 4, 5):
        receipt = receipts[f'columns_k{pairs}']
        need(receipt['signed_lift_prefix'] == bounds and
             int(receipt['payload_prefix_upper']) == local_payload, 'Local prefix disagreement')
        bound = 2 ** (6 * (pairs - 1)) * forward ** (pairs + 1) * backward ** pairs
        schedule_bounds[str(2 * pairs + 1)] = {'upper': str(bound), 'bits': bound.bit_length()}
    # Delete one actual cleanup XOR. Legality remains valid; every formal-column checker must reject it.
    mutant = json.loads(json.dumps(word))
    removed = [mutant['C'][0][0], mutant['C'][0][1], mutant['C'][0][2].pop()]
    if not mutant['C'][0][2]:
        del mutant['C'][0]
    mutant_path = directory / 'missing-cleanup.json.gz'
    with gzip.open(mutant_path, 'wt') as stream:
        json.dump(mutant, stream, separators=(',', ':'))
    bad = directory / 'missing-cleanup'
    export(mutant_path, bad)
    run([binaries / 'legality', bad / 'cin', bad / 'cout', bad / 'cout/legality.json'], bad / 'legality.log')
    rejected = []
    for name in receipts:
        result = run([binaries / name, bad / 'cout/COHORT249-RECORDS.bin', bad / 'cout' / (name + '.json')],
                     bad / (name + '.log'), reject=True)
        need('local defining-decoder full formal column' in result.stdout, 'Unexpected mutation failure')
        rejected.append(name)
    return {'word_content_sha256': canonical(word), 'record_sha256': digest((cout / 'COHORT249-RECORDS.bin').read_bytes()),
            'gates': {phase: len(word[phase]) for phase in 'DABC'},
            'legality': legality, 'forward_signed_row_l1_upper': str(forward),
            'reverse_signed_row_l1_upper': str(backward), 'local_raw_H': five['local_raw_H'],
            'five_stage_payload_upper': str(local_payload), 'five_stage_payload_bits': local_payload.bit_length(),
            'whole_scalar_schedule_prefix_bounds': schedule_bounds,
            'formal_columns': {str(s): receipts[n]['formal_columns_checked'] for n, s in
                               [('columns_h', 5), ('columns_k4', 9), ('columns_k5', 11)]},
            'omitted_bridge_controls': {'5': 6, '9': 18, '11': 24}, 'K2_equals_five_stage': True,
            'missing_cleanup_control': {'removed_frame_destination_source': removed,
                                        'legality_passed': True, 'rejected_by': rejected}}


def main():
    need(len(sys.argv) == 4, __doc__)
    original, candidate, out = [Path(x).resolve() for x in sys.argv[1:]]
    need(out != ROOT and ROOT not in out.parents, 'Output directory must be outside this repository')
    need(not out.exists(), 'Use a new output directory to avoid stale receipts')
    for path, expected in PINS.items():
        need(digest((PACKAGE / path).read_bytes()) == expected, f'Source pin mismatch: {path}')
    out.mkdir(parents=True)
    binaries = out / 'bin'
    binaries.mkdir(exist_ok=True)
    cxx = shlex.split(os.environ.get('CXX', 'c++'))
    boost = os.environ.get('BOOST_INCLUDE')
    if not boost:
        boost = next((p for p in ('/usr/include', '/usr/local/include', '/opt/homebrew/include')
                      if (Path(p) / 'boost/multiprecision/cpp_int.hpp').exists()), None)
    need(boost is not None, 'Set BOOST_INCLUDE to the Boost header directory')
    base = cxx + ['-O2', '-std=c++17', '-DHDIM=8', '-DNCOPY=9',
                  '-I' + str(PACKAGE / 'portable-include'), '-I' + str(CHECKERS), '-I' + boost]
    commands = []
    for name, source, options in [('legality', 'legality_h.cpp', []), ('columns_h', 'columns_h.cpp', [])] + [
            (f'columns_k{k}', 'columns_k.cpp', [f'-DKPAIRS={k}']) for k in (2, 4, 5)]:
        flags = [] if name == 'legality' else ['-DVPORTS=120', '-DRHELP=420']
        command = base + flags + options + ['-o', str(binaries / name), str(CHECKERS / source)]
        commands.append(command)
        run(command, out / (name + '-build.log'))
    result = {'status': 'PASS_NATIVE_R420_LOCAL_REPLAY', 'source_package': str(PACKAGE.relative_to(ROOT)),
              'source_sha256': PINS, 'compile_commands': commands,
              'environment': {'python': platform.python_version(), 'platform': platform.platform(),
                              'compiler': subprocess.check_output(cxx + ['--version'], text=True).splitlines()[0],
                              'boost_include': boost},
              'prefix_scope': 'The unchanged K4/K5 receipts retain the five-stage payload formula. Whole scalar schedule bounds here multiply local forward/reverse bounds and one factor 2 per bridge shear. These are not hosted physical prefix bills.',
              'remaining_obligations': ['Signed decoder evidence beyond F2 column replay',
                                        'Mutable-basis common-label realization and exact-bank completion',
                                        'Hosted physical replay, routing, pricing, and outer assembly'],
              'words': {}}
    for name, path in [('original', original), ('candidate', candidate)]:
        print(f'Replaying {name}: {path}', flush=True)
        result['words'][name] = replay(path, out / name, binaries)
    (out / 'native-summary.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print('PASS:', out / 'native-summary.json')


if __name__ == '__main__':
    main()

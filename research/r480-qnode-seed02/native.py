#!/usr/bin/env python3
"""Pinned native replay of the R480 Q-node2 replacement.

Prepared for ToikY with substantial OpenAI Codex assistance. Apache-2.0.
Adapted from Ross Richardson's retained R439 harness (itself credits Ali Romman
PR688) and DreamingOfClouds's PR503/510 R480 verification commands. The
retained legality, transform, interface and Gram checkers remain unchanged.
"""
import argparse
import copy
import gzip
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
PACKAGE = 'research/e8-bit-carrier-skeleton'
SOURCE = 'research/e8-r480-dead-totals/data/bitE8mut-r480.json.gz'
NATIVE_INPUTS = [
    SOURCE,
    PACKAGE + '/code/bit/export_records.py',
    PACKAGE + '/code/bit/regression/stage_cohort.py',
    PACKAGE + '/code/bit/checkers/legality_h.cpp',
    PACKAGE + '/code/bit/checkers/columns_h.cpp',
    PACKAGE + '/code/bit/checkers/columns_k.cpp',
    PACKAGE + '/code/bit/checkers/json.hpp',
    PACKAGE + '/portable-include/bits/stdc++.h',
    PACKAGE + '/code/bit/independent/checkword.py',
    PACKAGE + '/code/bit/independent/relax.py',
    PACKAGE + '/code/bit/independent/interface.py',
    PACKAGE + '/code/bit/checkers/gram_frames.py',
    PACKAGE + '/code/pricing/prime_witnesses.py',
    PACKAGE + '/code/pricing/moment.py',
]
# Frozen at base 407d52ff15b2217b6e22bce44728b4c3907b6515.
NATIVE_PINS = {
    "research/e8-bit-carrier-skeleton/code/bit/checkers/columns_h.cpp": "d1297f9052be4f2496e1ff2a77e4db2c0cdbd7d460d489b4c03e50bf317238ce",
    "research/e8-bit-carrier-skeleton/code/bit/checkers/columns_k.cpp": "1c344d18fcd494eeca93e259f10cafae7705780e6592f6dcb35b34752dab9bc2",
    "research/e8-bit-carrier-skeleton/code/bit/checkers/gram_frames.py": "223a5a07731fc315a90a3e48177796babc155c1d9985c7ae5017eff6af2a0608",
    "research/e8-bit-carrier-skeleton/code/bit/checkers/json.hpp": "aaf127c04cb31c406e5b04a63f1ae89369fccde6d8fa7cdda1ed4f32dfc5de63",
    "research/e8-bit-carrier-skeleton/code/bit/checkers/legality_h.cpp": "6c1ef2b24e57781d6951c172a1024fc4300e6fd392c9d6672079a7806ab663b3",
    "research/e8-bit-carrier-skeleton/code/bit/export_records.py": "8a5999601f917dbb492bb9ae9a344611f18cc7cedc53dc3c76496a369e530eb3",
    "research/e8-bit-carrier-skeleton/code/bit/independent/checkword.py": "11bf9620ca9db16d52d9fe806b814fc9ec9a89c4d7645354d1861d96f6e805ad",
    "research/e8-bit-carrier-skeleton/code/bit/independent/interface.py": "2c63a039f97e3a11ce5a6b83302d4f5beda160c1db14164a5a9b0855aeb19d3c",
    "research/e8-bit-carrier-skeleton/code/bit/independent/relax.py": "d6e9f58de3fa41f538516b6227c249d61fb30f0f6843027cc8a07a1a372fa6b6",
    "research/e8-bit-carrier-skeleton/code/bit/regression/stage_cohort.py": "6c288f6f234b528c1a7c0a4adfb724e91e0fe6b18c8dffad96af3f973de1829a",
    "research/e8-bit-carrier-skeleton/code/pricing/moment.py": "81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482",
    "research/e8-bit-carrier-skeleton/code/pricing/prime_witnesses.py": "98cd03bc9582e7bd0ab194c191ea8eea940539e510051443ab9fd3e572a364ab",
    "research/e8-bit-carrier-skeleton/portable-include/bits/stdc++.h": "420094be2af295eed03a983dd66debbbe9cfb78d8252859f4498a615a0074b99",
    "research/e8-r480-dead-totals/data/bitE8mut-r480.json.gz": "92e399e9a486b55229b5624632ac54f800dd9e022f2aee97f1e5f264bbc0ef5c"
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def check_sources():
    need(set(NATIVE_PINS) == set(NATIVE_INPUTS), 'incomplete native source pins')
    for path, expected in NATIVE_PINS.items():
        need(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected,
             'native source hash mismatch: ' + path)


def words(out):
    """Independent mechanical splice, including its literal inverse cleanup."""
    old = json.loads(gzip.decompress((ROOT / SOURCE).read_bytes()))
    recipe = json.loads((HERE / 'RECIPE.json').read_text())
    need(old['v'] == 120 and old['R'] == 480 and len(old['ret']) == 9,
         'wrong baseline dimensions')
    item = recipe['object']
    need(item['phase'] == 'A' and item['slice_start_inclusive'] == 2250
         and item['slice_end_exclusive'] == 2302 and item['frame'] == 484,
         'wrong replacement scope')
    replacement = recipe['replacement_A_events']
    need(len(replacement) == 43, 'wrong replacement gate count')
    registers = set(item['registers_in_matrix_order'])
    need(len(registers) == 12 and all(type(r) is int and 0 <= r < 120 for r in registers),
         'wrong Q-node source registers')
    for frame, dst, srcs in old['A'][2250:2302] + replacement:
        need(frame == 484 and dst in registers and len(srcs) == 1
             and srcs[0] in registers and dst != srcs[0], 'wrong block operation')
    full = old['C'][0][0]
    need(old['C'] == [[full, dst, srcs] for _, dst, srcs in reversed(old['A'])],
         'baseline cleanup is not literal inverse')
    new = copy.deepcopy(old)
    new['A'][2250:2302] = replacement
    new['C'] = [[full, dst, list(srcs)] for _, dst, srcs in reversed(new['A'])]
    need(all(not (0 <= dst < 120 or dst >= 240) for _, dst, _ in old['B']),
         'phase B writes a source or helper')
    result = {}
    for name, word in [('original', old), ('replacement', new)]:
        data = canonical(word)
        (out / (name + '.json.gz')).write_bytes(gzip.compress(data, mtime=0))
        result[name] = hashlib.sha256(data).hexdigest()
    return result


def run(out):
    bit = ROOT / PACKAGE / 'code/bit'
    checkers = bit / 'checkers'
    pricing = ROOT / PACKAGE / 'code/pricing'
    # -I explicitly ignores PYTHONOPTIMIZE: retained assertion-based checkers
    # must run normally even when this wrapper is invoked with python -O.
    python = [sys.executable, '-I', '-B']
    compiler = shlex.split(os.environ.get('CXX', 'c++'))
    include = Path(os.environ.get('BOOST_INCLUDE', '/usr/include')).resolve()
    need((include / 'boost/multiprecision/cpp_int.hpp').is_file(),
         'Set BOOST_INCLUDE to the directory containing boost/multiprecision/cpp_int.hpp')
    flags = ['-O0', '-std=c++17', '-DHDIM=8', '-DNCOPY=9', '-DVPORTS=120', '-DRHELP=480',
             '-I' + str(ROOT / PACKAGE / 'portable-include'), '-I' + str(checkers), '-I' + str(include)]
    bindir = out / 'bin'
    bindir.mkdir()

    def call(name, command, failure=None):
        with (out / (name + '.log')).open('w') as log:
            process = subprocess.run(list(map(str, command)), stdout=log, stderr=subprocess.STDOUT)
        text = (out / (name + '.log')).read_text()
        if failure is None:
            need(process.returncode == 0, name + ' failed: ' + text[-2000:])
        else:
            need(process.returncode != 0 and failure in text, name + ' failed to reject expected control')
        return text.strip()

    call('compile-legality', compiler + flags + ['-o', bindir / 'legality', checkers / 'legality_h.cpp'])
    call('compile-columns5', compiler + flags + ['-o', bindir / 'columns5', checkers / 'columns_h.cpp'])
    for pairs in (4, 5):
        call('compile-columns' + str(2 * pairs + 1), compiler + flags + ['-DKPAIRS=' + str(pairs), '-o',
             bindir / ('columns' + str(2 * pairs + 1)), checkers / 'columns_k.cpp'])
    call('relax', python + [bit / 'independent/relax.py', out / 'relaxed'])
    results = {}
    for name in ('original', 'replacement'):
        base = out / name
        records, cin, cout = (base / item for item in ('records', 'cin', 'cout'))
        word = out / (name + '.json.gz')
        call(name + '-export', python + [bit / 'export_records.py', word, records])
        call(name + '-cohort', python + [bit / 'regression/stage_cohort.py', records, records, cin, cout])
        call(name + '-legality', [bindir / 'legality', cin, cout, cout / 'legality.json'])
        legality = json.loads((cout / 'legality.json').read_text())
        need(legality['status'] == 'PASS_INDEPENDENT_COHORT_LEGALITY_SOURCE_OWNERS_AND_LIFECYCLE',
             'Legality did not pass')
        need(legality['copies'] == legality['erasures'] == 9, 'Wrong copy/erase count')
        result = {'legality': legality, 'stages': {}}
        for pairs in (2, 4, 5):
            stages = str(2 * pairs + 1)
            receipt = cout / ('columns' + stages + '.json')
            call(name + '-columns' + stages, [bindir / ('columns' + stages),
                 cout / 'COHORT249-RECORDS.bin', receipt])
            data = json.loads(receipt.read_text())
            expected_status = ('PASS_NEW_COHORT249_ALL_FIVE_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL' if pairs == 2
                               else 'PASS_NEW_COHORT249_ALL_BRIDGED_STAGE_FORMAL_COLUMNS_AND_PREFIX_BILL')
            need(data['status'] == expected_status, 'Formal columns did not pass')
            need(len(data['negative_controls']) == 6 * (pairs - 1)
                 and all(c['rejected'] is True for c in data['negative_controls']), 'A bridge control failed')
            need(data['formal_columns_checked'] == 240 * pairs + 480, 'Wrong formal column count')
            need(int(data['payload_prefix_upper']) < 2 ** 104, 'Payload limit failed')
            need(data['local_raw_H'] == legality['paid_histogram'], 'Column and legality histograms disagree')
            data.pop('seconds', None)
            data.pop('local_scalar_stream', None)
            result['stages'][stages] = data
            print(name + ' stages=' + stages + ' payload_bits=' + str(data['payload_prefix_bits']), flush=True)
        call(name + '-stock-negative', python + [bit / 'independent/checkword.py', word, pricing],
             failure='x register written')
        result['stock_immutable_source_checker_rejects'] = True
        result['relaxed_word_stdout'] = call(name + '-relaxed', python + [out / 'relaxed/checkword_mut.py', word, pricing])
        call(name + '-interface', python + [bit / 'independent/interface.py', word, '--json', base / 'interface.json'])
        result['interface'] = json.loads((base / 'interface.json').read_text())
        need(result['interface']['status'] == 'PASS_PR425_INTERFACE_HYPOTHESES', 'Interface did not pass')
        result['gram_stdout'] = call(name + '-gram', python + [checkers / 'gram_frames.py', records,
                                     '--gram', 'e8ham', '--h', '8', '--positive'])
        results[name] = result
    comparisons = {}
    for stages in ('5', '9', '11'):
        old, new = (results[name]['stages'][stages] for name in ('original', 'replacement'))
        need(old['local_raw_H'] == new['local_raw_H'], 'Paid histogram changed')
        need(old['local_scalar_additions'] - new['local_scalar_additions'] == 18, 'Wrong whole-word saving')
        # F2 equality does not imply positive-envelope dominance. Record the
        # measured values without imposing or claiming that stronger condition.
        comparisons[stages] = {
            'same_local_paid_histogram': True,
            'local_scalar_additions_saved': 18,
            'payload_upper_original': old['payload_prefix_upper'],
            'payload_upper_replacement': new['payload_prefix_upper'],
            'payload_upper_nonincrease': int(new['payload_prefix_upper']) <= int(old['payload_prefix_upper']),
        }
    old_l, new_l = (results[name]['legality'] for name in ('original', 'replacement'))
    need(old_l['common_frame_ADDs'] - new_l['common_frame_ADDs'] == 18, 'Legality saving differs')
    need(old_l['rank_mass'] == new_l['rank_mass'] and old_l['nested_MOVEs'] == new_l['nested_MOVEs'],
         'Frame costs changed')
    (out / 'ENVIRONMENT.json').write_text(json.dumps({
        'python': sys.version, 'platform': platform.platform(),
        'compiler': subprocess.check_output(compiler + ['--version'], text=True),
        'boost_include': str(include),
        'compile_flags': flags,
        'boost_version_header_sha256': hashlib.sha256((include / 'boost/version.hpp').read_bytes()).hexdigest(),
    }, sort_keys=True, indent=2) + '\n')
    return {'words': results, 'comparisons': comparisons}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='new output directory, preserving every log and receipt')
    parser.add_argument('--write-certificate', action='store_true', help='write NATIVE.json after all checks pass')
    args = parser.parse_args()
    check_sources()
    with tempfile.TemporaryDirectory(prefix='r480-qnode2-native-') as temporary:
        out = args.out.resolve() if args.out else Path(temporary) / 'work'
        out.mkdir(parents=True, exist_ok=False)
        hashes = words(out)
        receipt = {'schema': 'r480-qnode2-native/1', 'word_content_sha256': hashes,
                   'normalization': 'Only seconds and local_scalar_stream removed from native JSON; all other fields retained.',
                   **run(out)}
        data = json.dumps(receipt, sort_keys=True, indent=2) + '\n'
        (out / 'NATIVE.json').write_text(data)
        if args.write_certificate:
            (HERE / 'NATIVE.json').write_text(data)
        else:
            need(canonical(receipt) == canonical(json.loads((HERE / 'NATIVE.json').read_text())), 'native certificate mismatch')
        print('PASS_R480_QNODE2_NATIVE words=2 columns=960/1440/1680 bridge_controls=96 ADDs_saved=18 payload_lt_2^104')


if __name__ == '__main__':
    main()

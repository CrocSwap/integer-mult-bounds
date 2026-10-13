#!/usr/bin/env python3
"""Rebuild the bounded search and independently check the complete finite words.

Ross Richardson, substantial OpenAI Codex assistance; Apache-2.0.
Native harness and source package credit are in NOTICE.md.
"""
import argparse
import copy
import os
from pathlib import Path
import runpy
import shlex
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
C = runpy.run_path(str(HERE / 'common.py'))
I = runpy.run_path(str(HERE / 'independent_checks.py'))
need, same = C['need'], I['same']


def preflight():
    compiler = shlex.split(os.environ.get('CXX', 'c++'))
    need(bool(compiler) and shutil.which(compiler[0]) is not None, 'C++17 compiler required (CXX)')
    headers = Path(os.environ.get('BOOST_INCLUDE', '/usr/include'))
    need((headers / 'boost/multiprecision/cpp_int.hpp').is_file(),
         'Set BOOST_INCLUDE to the directory containing boost/multiprecision/cpp_int.hpp')


def run(output):
    preflight()
    sources = C['pins'](C['ROOT'])
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    baseline = C['load'](HERE / 'vendor/pr904/candidate.json.gz')
    candidate = C['load'](HERE / 'candidate.json.gz')
    certificate = C['load'](HERE / 'CERTIFICATE.json')
    print('Rebuild all 1,805 five-wire windows and the frozen PR904 comparison', flush=True)
    subprocess.run([sys.executable, '-I', '-B', str(HERE / 'build.py'),
                    '--output', str(output / 'generated')], check=True)
    same(certificate, C['load'](output / 'generated/CERTIFICATE.json'), 'search certificate changed')
    same(candidate, C['load'](output / 'generated/candidate.json.gz'), 'candidate payload changed')
    local = I['check_rewrites'](baseline, candidate, certificate)
    controls = I['controls']()
    old_builder = runpy.run_path(str(HERE / 'vendor/pr904/build.py'))
    _, second_pass = old_builder['construct'](baseline)
    same(second_pass['counts'], {
        'A': {'windows': 2240, 'shorter': 62, 'all_used': 62, 'dominant': 62, 'selected': 32, 'saved': 40},
        'B': {'windows': 599, 'shorter': 5, 'all_used': 5, 'dominant': 5, 'selected': 2, 'saved': 2}},
        'second four-wire pass changed')
    comparison = dict(counts=second_pass['counts'], paired_saving=84,
                      certificate_sha256=C['digest'](second_pass),
                      scope='one unchanged seed-11 PR904 pass on the same frozen input; not saturation or optimality')
    print('Independent 32-input local checks and unchanged 661-column H1-H5 replay', flush=True)
    checker = C['module']('source_xcheck_p', C['ROOT'] / C['CHECKER'])
    source = {}
    for name, word in (('baseline', baseline), ('candidate', candidate)):
        _, labels, full, hypotheses, conclusions, info = checker.check(word)
        need(all(value is True for value in hypotheses.values()), 'source interface hypotheses')
        need(all(value is True for value in conclusions.values()), 'source interface conclusions')
        source[name] = dict(labels=labels, full=full, hypotheses=hypotheses, conclusions=conclusions, info=info)
    # Stale cleanup has the correct semantic map but violates the literal H4 contract.
    stale = copy.deepcopy(candidate)
    stale['C'] = copy.deepcopy(baseline['C'])
    audited = checker.Word(stale)
    audited.full()
    hypotheses, conclusions, _ = audited.interface()
    need(hypotheses['H4_C_literal_reverse_at_full'] is False, 'stale cleanup H4 control')
    need(all(value for key, value in hypotheses.items() if key != 'H4_C_literal_reverse_at_full')
         and all(conclusions.values()), 'stale cleanup semantic premise')
    controls.append('actual stale cleanup fails literal H4 despite correct endpoint')
    broken = copy.deepcopy(candidate)
    del broken['A'][0]
    try:
        checker.Word(broken).full()
    except checker.Reject as error:
        need('not restored' in str(error), 'wrong dropped-gate rejection')
        controls.append('actual dropped prefix gate fails full endpoint')
    else:
        raise ValueError('dropped prefix gate accepted')
    print('Fresh native legality and 5/9/11-stage checks, including omitted bridges', flush=True)
    native = runpy.run_path(str(HERE / 'native.py'))['run'](
        C['ROOT'], HERE / 'vendor/pr904/candidate.json.gz', HERE / 'candidate.json.gz', output / 'native')
    return dict(status='PASS_R439_FIVE_WIRE_PREFIX', source_files=sources['files'],
                baseline_sha256=C['digest'](baseline), candidate_sha256=C['digest'](candidate),
                certificate_sha256=C['digest'](certificate), independent=local,
                repeated_four_wire_pass=comparison, source_replay=source,
                controls_rejected=controls, native=native)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='fresh directory for logs and binaries')
    parser.add_argument('--receipt', type=Path, help='write a new deterministic receipt; never overwrite')
    args = parser.parse_args()
    if args.output:
        need(not args.output.exists(), 'output already exists')
    if args.receipt:
        need(not args.receipt.exists(), 'receipt already exists')
    expected = C['load'](HERE / 'EXPECTED.json')
    with tempfile.TemporaryDirectory(prefix='r439-five-wire-') as temp:
        receipt = run(args.output or Path(temp) / 'replay')
        same(receipt, expected, 'receipt differs from EXPECTED.json')
        if args.receipt:
            C['write'](args.receipt, receipt)
    print('PASS_R439_FIVE_WIRE_PREFIX: 88 rewrites; 340 further ADDs saved; H1-H5; 5/9/11 stages; 17 controls; no new kappa')

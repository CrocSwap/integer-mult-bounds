#!/usr/bin/env python3
"""Rerun the selected record's final stage and compare it with the reviewed run.

The selected #1094 replay has one stage after the #1042 baseline:
``research/complex-t16-rare-pattern-exchanges/verify.py`` (the frozen PR1087
strict verifier on Rohan Arun's owner exchanges). This script

1. extracts its ``--local`` input (``slots/local``) from the committed #1042
   replay archive and checks all ten files against the #1042 receipt;
2. extracts the reviewed #1094 output from the committed #1094 archive and binds
   it to the committed #1094 receipts;
3. reruns the stage with the active interpreter in a fresh directory;
4. compares every output file by bytes and canonical payload
   (``compare_payloads.py``) and requires the recorded classification:
   102 byte-identical files, ``INDEPENDENT-T16.json`` equal after relocating
   absolute paths, and ``REPLAY.json``/``STAGES.json`` differing only in
   wall-clock ``seconds``;
5. runs negative controls showing that the comparison flags a changed
   proof-relevant value, a changed inner log digest, a changed gzip payload,
   a missing file and an unmapped path, and accepts a re-compressed gzip
   container.

Standard library only; Python 3.10+ (``tarfile`` ``filter=`` needs 3.10.12+ or
3.11.4+). Prepared with Claude Code (Claude Opus 5.5) for JosieElliston's
donated session 26. Apache-2.0.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from compare_payloads import compare, roots  # noqa: E402

A1042 = ROOT / 'research/community-frontier1042-audit'
A1094 = ROOT / 'research/community-frontier1094-audit'
STAGE = ROOT / 'research/complex-t16-rare-pattern-exchanges/verify.py'
# Absolute directories used by the reviewed run, as recorded in its receipts.
REF_WORK = '/private/tmp/batch1099-selected/candidate'
REF_LOCAL = '/private/tmp/batch1047-selected/slots/local'
KAPPA = '0.001672660197076918'
EXPECTED = {'bytes': 102, 'json-relocated': 1, 'json-diff:volatile': 2}
NON_BYTE = {'INDEPENDENT-T16.json': 'json-relocated', 'REPLAY.json': 'json-diff',
            'STAGES.json': 'json-diff'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check(cond, msg):
    if not cond:
        raise SystemExit('FAIL: ' + msg)


def extract(archive, dest, wanted=None):
    with tarfile.open(archive) as t:
        members = [m for m in t.getmembers() if wanted is None or m.name.startswith(wanted)]
        for m in members:
            check(m.isfile() or m.isdir(), 'unexpected archive member ' + m.name)
            check((dest / m.name).resolve().is_relative_to(dest.resolve()), 'unsafe member ' + m.name)
        t.extractall(dest, members=members, filter='data')


def counts(result):
    out = {}
    for v in result.values():
        k = v['cls'] + (':' + v['verdict'] if 'verdict' in v else '')
        out[k] = out.get(k, 0) + 1
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--work', type=Path, help='fresh directory (default: a temporary one)')
    ap.add_argument('--keep', action='store_true', help='keep the temporary directory')
    a = ap.parse_args()
    check(not sys.flags.optimize, 'assertions are required by the rerun stage')
    if a.work:
        work = a.work.resolve()
        check(not work.exists(), 'use a fresh --work directory')
        work.mkdir(parents=True)
    else:
        work = Path(tempfile.mkdtemp(prefix='final-stage-portability.')).resolve()
    try:
        run(work)
    finally:
        if not a.work and not a.keep:
            shutil.rmtree(work, ignore_errors=True)


def run(work):
    # 1. Input bound to the #1042 receipt.
    receipt1042 = json.loads((A1042 / 'RESULT.json').read_bytes())
    inp = work / 'in1042'
    inp.mkdir()
    extract(A1042 / 'selected-replay.tar.gz', inp, 'slots/local/')
    local = inp / 'slots/local'
    bound = {k: v for k, v in receipt1042['artifacts'].items() if k.startswith('slots/local/')}
    present = {'slots/local/' + p.name for p in local.iterdir()}
    check(len(bound) == 10 and set(bound) == present, 'slots/local inventory differs from the #1042 receipt')
    for name, digest in bound.items():
        check(sha(inp / name) == digest, '#1042 artifact hash: ' + name)
    # 2. Reference output bound to the committed #1094 receipts.
    ref = work / 'ref1094'
    ref.mkdir()
    extract(A1094 / 'selected-replay.tar.gz', ref)
    for name in ('RESULT.json', 'STAGES.json'):
        check((ref / name).read_bytes() == (A1094 / name).read_bytes(), 'archived #1094 ' + name)
    check((ref / 'candidate/strict/REPLAY.json').read_bytes() == (A1094 / 'REPLAY.json').read_bytes(),
          'archived #1094 REPLAY.json')
    result1094 = json.loads((A1094 / 'RESULT.json').read_bytes())
    check(sha(ref / 'candidate/strict/ASSEMBLY.json') == result1094['assembly_sha256'], 'archived #1094 assembly')
    check(sha(A1042 / 'RESULT.json') == result1094['baseline_receipt_sha256'], '#1094 names the #1042 receipt')
    check(result1094['baseline'] + '/slots/local' == REF_LOCAL, 'reviewed --local path')
    stage = [s for s in result1094['stages'] if s['name'] == 'rare-pattern-exchanges']
    check(len(stage) == 1 and stage[0]['script_sha256'] == sha(STAGE), 'final-stage script is the reviewed one')
    # 3. Rerun with the active interpreter.
    out = work / 'run'
    log = work / 'rare-pattern-exchanges.log'
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    env.pop('PYTHONOPTIMIZE', None)
    with log.open('w') as stream:
        p = subprocess.run([sys.executable, '-B', str(STAGE), '--main', str(ROOT), '--local', str(local),
                            '--work', str(out)], cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT)
    text = log.read_text()
    check(p.returncode == 0 and text.endswith('PASS_T16_RARE_PATTERN_EXCHANGES ' + KAPPA + '\n'),
          'final stage did not pass; see ' + str(log))
    # The outer stage log prints wall-clock seconds, so its #1094 log_sha256 is
    # not reproducible; the inner logs are compared byte for byte below.
    ref_log = (ref / 'rare-pattern-exchanges.log').read_text().splitlines()
    run_log = text.splitlines()
    strip = lambda lines: [l.rsplit(' ', 1)[0] if l.startswith('PASS ') and l.count(' ') == 2 else l for l in lines]
    check(strip(ref_log) == strip(run_log), 'outer stage log differs beyond per-stage seconds')
    # 4. Canonical comparison.
    ref_roots = roots(['<WORK>=' + REF_WORK, '<LOCAL>=' + REF_LOCAL])
    run_roots = roots(['<WORK>=' + str(out), '<LOCAL>=' + str(local)])
    res = compare(ref / 'candidate/strict', out / 'strict', ref_roots, run_roots)
    check(counts(res) == EXPECTED, 'classification differs: ' + json.dumps(counts(res), sort_keys=True))
    for name, cls in NON_BYTE.items():
        check(res[name]['cls'] == cls, 'unexpected class for ' + name)
    for name in ('REPLAY.json', 'STAGES.json'):
        check(res[name]['verdict'] == 'volatile' and res[name]['differing'] == 11, name + ' differs beyond seconds')
    # The #1094 certificate (selected at base 0b1cccf8) is this file's bytes.
    check((out / 'strict/ASSEMBLY.json').read_bytes() == (A1094 / 'ASSEMBLY.json').read_bytes(),
          'rerun ASSEMBLY.json differs from the committed #1094 certificate bytes')
    print('PASS comparison', json.dumps(counts(res), sort_keys=True), flush=True)
    # 5. Negative controls on copies of the rerun output.
    controls(ref / 'candidate/strict', out / 'strict', ref_roots, run_roots, work / 'controls')
    print('PASS_SELECTED_FINAL_STAGE_PORTABILITY', sys.version.split()[0], KAPPA)


def controls(ref, run, ref_roots, run_roots, base):
    def variant(name, mutate, expect_file, expect):
        d = base / name
        shutil.copytree(run, d)
        mutate(d)
        # File contents still name the rerun's own directories, so the roots are unchanged.
        res = compare(ref, d, ref_roots, run_roots)
        got = res[expect_file]['cls'] + (':' + res[expect_file]['verdict'] if 'verdict' in res[expect_file] else '')
        check(got == expect, f'control {name}: {expect_file} classified {got}, expected {expect}')
        print('PASS control', name, '->', got, flush=True)

    def edit_json(rel, fn):
        def mutate(d):
            p = d / rel
            j = json.loads(p.read_bytes())
            fn(j)
            p.write_text(json.dumps(j, indent=2) + '\n')
        return mutate

    def bump_profile(j):
        j['live'] += 1
    variant('proof-value', edit_json('INDEPENDENT-T16.json', bump_profile),
            'INDEPENDENT-T16.json', 'json-diff:proof-relevant-candidate')

    def kappa(j):
        j['kappa_decimal'] = j['kappa_decimal'][:-1] + '9'
    variant('kappa-with-seconds', edit_json('REPLAY.json', kappa),
            'REPLAY.json', 'json-diff:proof-relevant-candidate')
    def log_digest(j):
        j[0]['log_sha256'] = '0' * 64
    variant('inner-log-digest', edit_json('STAGES.json', log_digest),
            'STAGES.json', 'json-diff:proof-relevant-candidate')
    gz = 'global/hosted/GLOBAL-TEMPLATE.json.gz'

    def recompress(d):
        p = d / gz
        p.write_bytes(gzip.compress(gzip.decompress(p.read_bytes()), compresslevel=1, mtime=12345))
    variant('gzip-recompressed', recompress, gz, 'gzip-container')

    def gz_payload(d):
        p = d / gz
        j = json.loads(gzip.decompress(p.read_bytes()))
        j = {'tampered': True, **j} if isinstance(j, dict) else j + [0]
        p.write_bytes(gzip.compress(json.dumps(j).encode(), mtime=0))
    variant('gzip-payload', gz_payload, gz, 'json-diff:proof-relevant-candidate')
    variant('missing-file', lambda d: (d / 'ASSEMBLY.json').unlink(), 'ASSEMBLY.json', 'missing')

    def foreign_path(j):
        k = next(iter(j['input_sha256']))
        j['input_sha256']['/elsewhere/' + k.rsplit('/', 1)[-1]] = j['input_sha256'].pop(k)
    variant('unmapped-path', edit_json('INDEPENDENT-T16.json', foreign_path),
            'INDEPENDENT-T16.json', 'json-diff:proof-relevant-candidate')


if __name__ == '__main__':
    main()

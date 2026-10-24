#!/usr/bin/env python3
"""Portable transport/replay adapter; scientific checkers are retained unchanged.

Chris R / Clear1nsight, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha256
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
EVIDENCE_SHA256 = 'b670cc75811f6d42190029ef9cd2f65e67a588d5d147e2c9e3f47693aa7c5c1b'
TOP = Path('outputs/new-approach-ceilings-20261023')
REVIEW = Path('outputs/new-approach-verification-20261023')


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    raw = (HERE/'EVIDENCE.json').read_bytes()
    need(sha256(raw).hexdigest() == EVIDENCE_SHA256, 'retained inventory changed')
    pins = json.loads(raw)['files']
    actual_paths = {p.relative_to(HERE).as_posix() for p in (HERE/'evidence').rglob('*') if p.is_file()}
    need(actual_paths == set(pins), 'retained evidence inventory changed')
    for path, digest in pins.items():
        need(sha256((HERE/path).read_bytes()).hexdigest() == digest, 'retained bytes changed: '+path)
    top = HERE/'evidence'/TOP
    for path, digest in json.loads((top/'FILES.json').read_bytes())['files'].items():
        need(sha256((top/path).read_bytes()).hexdigest() == digest, 'author packet changed: '+path)
    physical = HERE/'evidence/physical-interface'
    for path, digest in json.loads((physical/'FILES.json').read_bytes()).items():
        need(sha256((physical/path).read_bytes()).hexdigest() == digest, 'physical source packet changed: '+path)
    for row in json.loads((physical/'SOURCES.json').read_bytes())['files']:
        need(sha256((physical/row['local']).read_bytes()).hexdigest() == row['sha256'], 'physical source hash')
    review = HERE/'evidence'/REVIEW
    freeze = json.loads((review/'FREEZE.json').read_bytes())
    # FREEZE also describes unrelated p2 work; authenticate only retained direct files.
    for row in freeze['files']:
        if (review/row['path']).is_file():
            data = (review/row['path']).read_bytes()
            need(len(data) == row['bytes'] and sha256(data).hexdigest() == row['sha256'], 'independent freeze changed')
    return pins


def launch(path, cwd, extra=(), success=True):
    args = [sys.executable, '-I']
    if sys.flags.optimize:
        args.append('-O')
    args.extend(['-W', 'error', '-B', str(path), *extra])
    env = {k:v for k,v in os.environ.items() if not k.startswith('GIT_') and not k.startswith('PYTHON')}
    done = subprocess.run(args, cwd=cwd, env=env, capture_output=True, timeout=90, check=False)
    if success:
        need(done.returncode == 0, 'scientific replay failed: '+done.stderr.decode('utf-8', errors='replace'))
        need(done.stderr == b'', 'warning-strict replay emitted stderr')
    else:
        need(done.returncode != 0, 'corrupt frozen input was accepted')
        need(b'Changed source' in done.stderr or b'source manifest hash' in done.stderr, 'unexpected rejection reason')
    return done.stdout


def main():
    before = authenticate()
    suffix = '-OPTIMIZED' if sys.flags.optimize else ''
    with tempfile.TemporaryDirectory(prefix='cap2-physical-ceiling-') as temp:
        scratch = Path(temp)
        # Copy bytes only: a read-only export must yield writable private outputs.
        for relative in (TOP, REVIEW):
            source_tree = HERE/'evidence'/relative
            for original in source_tree.rglob('*'):
                if original.is_file():
                    destination = scratch/relative/original.relative_to(source_tree)
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(original, destination)
        expected = (scratch/TOP/('CHECK-RESULT'+suffix+'.json')).read_bytes()
        stdout = launch(scratch/TOP/'check_screen.py', scratch)
        need(stdout == expected, 'author replay differs from frozen receipt')
        expected_review = (scratch/REVIEW/('ECONOMIC-REVIEWS-DIRECT-RESULT'+suffix+'.json')).read_bytes()
        stdout_review = launch(scratch/REVIEW/'check_economic_reviews.py', scratch, ('--direct-only',))
        message = json.loads(stdout_review)
        need(message['status'] == 'PASS_SCOPED_INDEPENDENT_ECONOMIC_REVIEW_DIRECT', 'independent replay status')
        need(Path(message['result']).resolve() == (scratch/REVIEW/('ECONOMIC-REVIEWS-DIRECT-RESULT'+suffix+'.json')).resolve(), 'independent result destination')
        need((scratch/REVIEW/('ECONOMIC-REVIEWS-DIRECT-RESULT'+suffix+'.json')).read_bytes() == expected_review, 'independent replay differs from frozen receipt')
        # A real scientific input mutation must fail each unchanged source checker.
        source = scratch/TOP/'frozen/notes__three-stage-cover-bit.tex'
        source.write_bytes(source.read_bytes()+b'\nCORRUPTION CONTROL\n')
        launch(scratch/TOP/'check_screen.py', scratch, success=False)
        launch(scratch/REVIEW/'check_economic_reviews.py', scratch, ('--direct-only',), success=False)
    need(authenticate() == before, 'package changed during replay')
    print(json.dumps({'status':'PASS_CAP2_PHYSICAL_CEILING_PACKAGE',
                      'retained_files':len(before),
                      'author_receipt':'BYTE_IDENTICAL',
                      'independent_direct_receipt':'BYTE_IDENTICAL',
                      'source_corruption_rejections':2,
                      'package_bytes_unchanged':True,
                      'native_or_formal_word_or_compiler_execution':False,
                      'physical_supplier_verified':False,
                      'new_kappa':None}, sort_keys=True))


if __name__ == '__main__':
    main()

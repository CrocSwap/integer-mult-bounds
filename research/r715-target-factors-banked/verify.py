#!/usr/bin/env python3
"""Reproduce the source-pinned non-hosting R715 target-interval construction.

Prepared for eumemic with OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import gzip
import hashlib
import io
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def package_hashes():
    return {p.relative_to(HERE).as_posix(): digest(p) for p in HERE.rglob('*')
            if p.is_file() and '__pycache__' not in p.parts and p != HERE / 'MANIFEST.json'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('output', type=Path)
    a = ap.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(HERE), 'output must be outside the package'
    assert not out.exists(), 'use a fresh output directory'
    assert sys.flags.optimize == 0, 'assertions must remain enabled'
    out.mkdir(parents=True)
    manifest_sha = digest(HERE / 'MANIFEST.json')
    manifest = json.loads((HERE / 'MANIFEST.json').read_text())
    assert package_hashes() == manifest, 'package manifest mismatch'
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    count = 0
    for entry in sources.values():
        for rel, sha in entry['files'].items():
            data = (HERE / rel).read_bytes()
            assert hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest() == sha, rel
            count += 1
    expected = json.loads((HERE / 'EXPECTED.json').read_text())
    parent = HERE / 'e8-r740-replica32'
    upstream = HERE / 'vendor478'
    word = upstream / 'bit470/data/word.json'
    old_word = upstream / 'bit470/data/parent473.json'
    assert digest(word) == expected['content_sha256']
    B = parent / 'parent436/code/bit'
    # The sole change to this inherited mutation driver prevents a vacuous
    # frame-zero corruption now that phase B genuinely begins at frame zero.
    original_mutator = (B / 'mutate_records.py').read_text()
    old_predicate = 'lambda e,i:e[0]==1 and e[5]==4,lambda e:e.__setitem__(4,0)'
    assert original_mutator.count(old_predicate) == 1
    adapted = original_mutator.replace(old_predicate,
        'lambda e,i:e[0]==1 and e[5]==4 and e[4]!=0,lambda e:e.__setitem__(4,0)')
    assert (HERE / 'code/mutate_records.py').read_text() == adapted
    env = dict(os.environ, PYTHON=sys.executable, PYTHONDONTWRITEBYTECODE='1')
    env.pop('PYTHONOPTIMIZE', None)
    steps = []

    def run(name, argv):
        start = time.monotonic()
        with (out / (name + '.log')).open('w') as log:
            process = subprocess.run(list(map(str, argv)), cwd=out, env=env,
                                     stdout=log, stderr=subprocess.STDOUT)
        steps.append(dict(name=name, exit_code=process.returncode,
                          seconds=time.monotonic() - start))
        write(out / 'STEPS.json', steps)
        if process.returncode:
            write(out / 'FAILURE.json', dict(step=name, exit_code=process.returncode))
            print((out / (name + '.log')).read_text()[-8000:], flush=True)
            raise RuntimeError(name)
        print('PASS', name, flush=True)

    def py(name, source, *args):
        run(name, [sys.executable, '-B', source, *args])

    run('parent443-full', ['bash', parent / 'verify.sh', out / 'parent443'])
    py('schur-rebuild', upstream / 'code/schur_constructor.py', old_word,
       upstream / 'code/SELECTION473.json', out / 'schur')
    assert (out / 'schur/word.json').read_bytes() == word.read_bytes()
    schur = json.loads((out / 'schur/SCHUR-AUDIT.json').read_text())
    for key in ('source_canonical_sha256', 'candidate_sha256', 'delta'):
        assert schur[key] == expected['schur'][key], key
    assert len(schur['mutations_rejected']) == expected['schur']['mutations_rejected']
    assert set(schur['mutations_rejected'].values()) == {'REJECTED'}
    assert schur['all_other_word_fields_identical']
    # The pinned label checker reads a .gz file relative to itself. Give it a
    # private runtime copy, preserving every published upstream source byte.
    runtime = out / 'upstream-runtime'
    shutil.copytree(upstream, runtime)
    runtime_word = runtime / 'bit470/data/word.json.gz'
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode='wb', filename='', mtime=0) as z:
        z.write(word.read_bytes())
    runtime_word.write_bytes(buf.getvalue())
    assert digest(runtime_word) == expected['global']['word_sha256']
    candidate = out / 'candidate'
    nine = candidate / 'nine'
    nine.mkdir(parents=True)
    binaries = candidate / 'bin'
    binaries.mkdir()
    py('export', B / 'export_records.py', word, candidate / 'records')
    py('labels', runtime / 'bit470/code/labels.py', candidate / 'records')
    py('cohort', B / 'regression/stage_cohort.py', candidate / 'records',
       candidate / 'records', candidate / 'cin', candidate / 'cout')
    compiler = shlex.split(os.environ.get('CXX', 'c++'))
    assert compiler
    include = ['-I' + str(parent / 'parent436/portable-include'),
               '-I' + str(B / 'checkers'), '-I' + os.environ.get('BOOST_INCLUDE', '/usr/include')]
    for name, source, definitions in [
        ('legality', 'legality_h.cpp', ['-DNCOPY=9']),
        ('legality_ncopy_h', 'legality_h.cpp', []),
        ('columns_h', 'columns_h.cpp', ['-DNCOPY=9', '-DVPORTS=120', '-DRHELP=715']),
        ('columns_k4', 'columns_k.cpp', ['-DNCOPY=9', '-DVPORTS=120', '-DRHELP=715', '-DKPAIRS=4']),
    ]:
        run('compile-' + name, compiler + ['-O2', '-std=c++17', '-DHDIM=8'] + definitions
            + include + ['-o', binaries / name, B / 'checkers' / source])
    run('legality', [binaries / 'legality', candidate / 'cin', candidate / 'cout',
                    candidate / 'cout/legality.json'])
    run('columns-five', [binaries / 'columns_h', candidate / 'cout/COHORT249-RECORDS.bin',
                        candidate / 'cout/columns.json'])
    run('columns-nine', [binaries / 'columns_k4', candidate / 'cout/COHORT249-RECORDS.bin',
                        candidate / 'cout/columns_k4.json'])
    py('record-mutations', HERE / 'code/mutate_records.py', candidate / 'records',
       candidate / 'cin', candidate / 'cout', binaries / 'legality',
       binaries / 'columns_k4', binaries / 'legality_ncopy_h')
    py('gram', B / 'checkers/gram_frames.py', candidate / 'records',
       '--gram', 'e8ham', '--h', 8, '--positive')
    py('isometries', HERE / 'code/residual_isometries.py', '--word', word,
       '--frames', candidate / 'records/frames.json', '--out', candidate / 'isometries.json')
    geometry = json.loads((out / 'parent443/candidate/nine/GEOMETRY.json').read_text())
    geometry['seconds'] = 0
    write(nine / 'GEOMETRY.json', geometry)
    py('global', parent / 'code/global_kernel.py', '--word', runtime_word,
       '--local-check', candidate, '--out', nine, '--isometries', candidate / 'isometries.json')
    py('audit', parent / 'code/audit_kernel.py', '--word', runtime_word,
       '--local-check', candidate, '--out', nine)
    py('bank-owner-audit', HERE / 'code/bank_owner_audit.py', word,
       nine / 'GLOBAL-TEMPLATE.json.gz', out / 'BANK-OWNER-AUDIT.json')
    py('compose', parent / 'code/compose_kernel.py', '--pricing', parent / 'parent436/code/pricing',
       '--out', nine, '--cited', parent / 'parent436/data/complex-b-433.json',
       '--receipt', parent / 'parent436/data/controls/pr433/CERTIFICATE.json')
    py('operator-audit', HERE / 'code/operator_audit.py', '--word', word, '--parent', old_word,
       '--out', out / 'OPERATOR-AUDIT.json')
    g = json.loads((nine / 'GLOBAL.json').read_text())
    result = json.loads((nine / 'COMPOSED-433.json').read_text())
    operator = json.loads((out / 'OPERATOR-AUDIT.json').read_text())
    banks = json.loads((out / 'BANK-OWNER-AUDIT.json').read_text())
    for key, value in expected['global'].items():
        assert g[key] == value, (key, g[key], value)
    for key, value in expected['result'].items():
        assert result[key] == value, (key, result[key], value)
    for key, value in expected['operator'].items():
        assert operator[key] == value, (key, operator[key], value)
    for key, value in expected['bank_owner_audit'].items():
        assert banks[key] == value, (key, banks[key], value)
    assert len(result['strict_outer_constraints']) == 47 and len(result['outer_controls']) == 4
    assert digest(HERE / 'MANIFEST.json') == manifest_sha, 'manifest changed during replay'
    assert package_hashes() == manifest, 'source changed during replay'
    write(out / 'RESULT.json', dict(status='PASS_NONHOSTING_R715_TARGET_INTERVALS',
          kappa=result['kappa'], bit_lower=result['bit_lower'], complex_lower=result['complex_lower'],
          content_sha256=expected['content_sha256'], template_sha256=g['template_sha256'],
          operator_audit_sha256=digest(out / 'OPERATOR-AUDIT.json'),
          bank_owner_audit_sha256=digest(out / 'BANK-OWNER-AUDIT.json'),
          package_manifest_sha256=manifest_sha, source_blobs_checked=count,
          local_columns=955, dirty_helpers=715, target_additions_per_orientation=140,
          new_interval_target_additions=28, schur_mutations_rejected=28,
          scope='Finite non-hosting conditional construction; cited PR433 complex supplier, no full complex phase rerun.',
          steps=steps, python=sys.version))
    print('PASS conditional kappa', result['kappa'], '=', result['kappa_decimal'], flush=True)


if __name__ == '__main__':
    main()

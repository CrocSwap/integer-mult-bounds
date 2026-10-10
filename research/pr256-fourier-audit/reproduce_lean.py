#!/usr/bin/env python3
"""Reproduce the pinned upstream Lean proof and its statement/axiom comparisons.

Requires the pinned Lean toolchain on PATH (or --lake). Downloads pinned
Mathlib dependencies/cache unless --cache-ready is set. Extracts the vendored
source archive into --work-dir, or checks every source byte if it already exists.
Does not run the official Linux comparator, an independent kernel, or the DFT.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import time

from verify import BASE, VENDOR, require, source_check


def prepare(work, archive_path):
    work.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path) as archive:
        members = [m for m in archive.getmembers() if m.isfile()]
        hashes = {}
        for member in members:
            relative = Path(member.name)
            require(not relative.is_absolute() and '..' not in relative.parts,
                    'unsafe source archive path')
            data = archive.extractfile(member).read()
            path = work / relative
            require(path.resolve().is_relative_to(work.resolve()), 'source path leaves work directory')
            if path.exists():
                require(path.read_bytes() == data, 'existing source differs: '+member.name)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
                path.chmod(member.mode & 0o777)
            hashes[member.name] = hashlib.sha256(data).hexdigest()
    return hashes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work-dir', type=Path, required=True)
    parser.add_argument('--lake', default='lake')
    parser.add_argument('--cache-ready', action='store_true')
    parser.add_argument('--threads', type=int, default=2)
    parser.add_argument('--receipt', type=Path, default=Path('/tmp/pr256-fourier-audit/lean-receipt.json'))
    args = parser.parse_args()
    require(args.threads > 0, 'threads must be positive')
    source = source_check()
    work = args.work_dir.resolve()
    hashes = prepare(work, VENDOR/source['fourier_proof']['archive'])
    lake = shutil.which(args.lake)
    require(lake is not None, 'Lake not found; install leanprover/lean4:v4.34.1 first')
    env = dict(os.environ)
    env['PATH'] = str(Path(lake).resolve().parent) + os.pathsep + env.get('PATH', '')
    env['LEAN_NUM_THREADS'] = str(args.threads)
    log_dir = args.receipt.resolve().parent / 'five_stage_lean_logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    commands = []
    started = datetime.now(timezone.utc).isoformat()
    fresh = not (work/'.lake/build/lib/lean/Work').exists()

    def run(label, command):
        print('Running '+label+' ...', flush=True)
        t0 = time.monotonic()
        log_path = log_dir/(label+'.log')
        with log_path.open('w') as log:
            p = subprocess.run(command, cwd=work, env=env, stdout=log, stderr=subprocess.STDOUT)
        output = log_path.read_text()
        commands.append({'label': label, 'command': command, 'exit_code': p.returncode,
                         'seconds': round(time.monotonic()-t0, 3),
                         'log_sha256': hashlib.sha256(log_path.read_bytes()).hexdigest()})
        if p.returncode:
            print(output[-6000:])
            raise SystemExit('FAILED '+label+'; log: '+str(log_path))
        print('PASS '+label, flush=True)
        return output

    version = run('toolchain', [lake, '--version']).strip()
    require('Lean version 4.34.1' in version, 'incorrect Lean toolchain')
    if not args.cache_ready:
        run('mathlib_cache', [lake, 'exe', 'cache', 'get'])
    mathlib = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=work/'.lake/packages/mathlib', text=True).strip()
    require(mathlib == source['fourier_proof']['mathlib_commit'], 'Mathlib revision differs')
    generated = run('regenerate_certificate', [sys.executable, '-B', 'tools/gx/regen_check.py',
                    'tools/certificate/gcert1-p11-pr233-flow.json.gz', 'P233', 'B2Gp233'])
    require('41 repository files reproduced byte for byte, 0 different, 0 generated files not in the repository' in generated,
            'Lean certificate generation differs')
    transfer = run('regenerate_fourier', [sys.executable, '-B', 'tools/fourier/regen_check233.py'])
    require('14 repository files reproduced byte for byte, 0 different, 0 generated files not in the repository' in transfer,
            'Fourier generation differs')
    # Each scalar reduction can use several GB. Keep these two independent
    # kernel checks sequential, even when other compilation uses two workers.
    run('build_scalar0', [lake, 'build', 'Work.GCert.Data.Gen.P233Scal0'])
    run('build_scalar1', [lake, 'build', 'Work.GCert.Data.Gen.P233Scal1'])
    targets = ['Work.GCert.Data.ChallengeB2Gp233x', 'Work.GCert.Data.SolutionB2Gp233x',
               'Work.Fourier233.UniformFourierChallenge', 'Work.Fourier233.Main', 'Work.Fourier233.Axioms']
    build = run('build', [lake, 'build', *targets])
    axioms = run('axioms', [lake, 'env', 'lean', 'Work/Fourier233/Axioms.lean'])
    allowed = {'propext', 'Classical.choice', 'Quot.sound'}
    required = ['OAI.PowerSaving.transform_mainY', 'OAI.PowerSaving.convolution_mainY',
                'OAI.PowerSaving.RAM.hillsY_program']
    found = {}
    for name in required:
        match = re.search(re.escape("'"+name+"' depends on axioms: ")+r'\[([^]]*)\]', axioms)
        require(match is not None, 'missing axiom report: '+name)
        values = {v.strip() for v in match.group(1).split(',')}
        require(values == allowed, 'unexpected axioms: '+name)
        found[name] = sorted(values)
    comparisons = [
        ('compare_wht', ['Work.GCert.Data.ChallengeB2Gp233x', 'Work.GCert.Data.SolutionB2Gp233x',
                         'OAI.PowerSaving.WHT.wht_main_block_B2Gp233x']),
        ('compare_fourier', ['Work.Fourier233.UniformFourierChallenge', 'Work.Fourier233.Main',
                             'OAI.PowerSaving.transform_mainY', 'OAI.PowerSaving.convolution_mainY'])]
    for label, names in comparisons:
        output = run(label, [lake, 'env', 'lean', '--run', 'tools/Compare.lean', *names])
        require('RESULT: PASS' in output, 'missing successful statement comparison')
    for path, digest in hashes.items():
        require(hashlib.sha256((work/path).read_bytes()).hexdigest() == digest, 'source changed during build: '+path)
    receipt = {'schema': 1, 'started_utc': started, 'finished_utc': datetime.now(timezone.utc).isoformat(),
               'source_commit': source['fourier_proof']['commit'], 'source_archive_sha256':
                   source['files'][source['fourier_proof']['archive']],
               'source_files_checked': len(hashes), 'fresh_project_build': fresh,
               'mathlib_commit': mathlib, 'mathlib_from_cache': True,
               'toolchain': version, 'platform': platform.platform(), 'machine': platform.machine(),
               'threads': args.threads, 'commands': commands, 'axioms': found,
               'statement_comparison': 'upstream tools/Compare.lean; WHT, all-length DFT and convolution passed',
               'official_comparator_run': False, 'independent_kernel_run': False,
               'numerical_dft_executed': False, 'independent_human_review': False,
               'success': True}
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print('PASS: pinned Lean build, standard axioms and theorem/definition comparisons; receipt '+str(args.receipt))


if __name__ == '__main__':
    main()

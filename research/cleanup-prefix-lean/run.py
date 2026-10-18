#!/usr/bin/env python3
"""Recheck the source binding and compile universal + actual CK Lean proofs.
No downloads, global toolchain changes, or full supplier replay.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
import argparse
import os
import re
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
VERSION = '4.27.0'


def reported_lean_version(output):
    """Read the complete version token, retaining prerelease/build suffixes."""
    match = re.match(r'Lean \(version ([^,\s)]+)(?=[,\s)])', output.strip())
    return match.group(1) if match else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lean-bin', type=Path, help='directory containing pinned lean and lake')
    args = parser.parse_args()
    candidates = [args.lean_bin] if args.lean_bin else [
        Path(os.environ['LEAN_BIN']) if os.environ.get('LEAN_BIN') else None,
        Path(shutil.which('lean')).parent if shutil.which('lean') else None,
        Path('/tmp/swarm-research-lean-tools/lean-4.27.0-linux/bin'),
    ]
    chosen = None
    for candidate in candidates:
        if candidate and (candidate / 'lean').is_file() and (candidate / 'lake').is_file():
            version = subprocess.check_output([str(candidate / 'lean'), '--version'], text=True)
            if reported_lean_version(version) == VERSION:
                chosen = candidate.resolve()
                print(version.strip(), flush=True)
                break
    if chosen is None:
        raise SystemExit('Lean 4.27.0 required. Pass --lean-bin /path/to/lean-4.27.0-linux/bin; no global default is changed.')
    env = dict(os.environ, PATH=str(chosen) + os.pathsep + os.environ.get('PATH', ''), PYTHONDONTWRITEBYTECODE='1')
    for script in ('check_source.py', 'generate_lean.py'):
        subprocess.run([sys.executable, '-B', str(HERE / script)], cwd=HERE, env=env, check=True)
    # Lake replays retained elaboration messages, including axiom audits, for unchanged modules.
    process = subprocess.run([str(chosen / 'lake'), 'build'], cwd=HERE, env=env,
                             text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(process.stdout, end='', flush=True)
    if process.returncode:
        raise SystemExit(process.returncode)
    found = re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]", process.stdout)
    audits = {name: {x.strip() for x in values.split(',') if x.strip()} for name, values in found}
    audits.update({name: set() for name in re.findall(r"'([^']+)' does not depend on any axioms", process.stdout)})
    expected = {'CleanupPrefix.commute_sound', 'CleanupPrefix.sourceExtract_in_context',
                'CleanupPrefix.CK.checked', 'CleanupPrefix.CK.scalar_rewrite',
                'CleanupPrefix.CK.source_coefficient_rewrite'}
    if not expected <= audits.keys():
        raise SystemExit('Missing axiom audit output: ' + str(expected - audits.keys()))
    for name, axioms in audits.items():
        if not axioms <= {'propext', 'Quot.sound', 'Classical.choice'}:
            raise SystemExit(f'Unexpected axioms in {name}: {axioms}')
    print('PASS_CLEANUP_PREFIX_LEAN: universal semantics, actual CK bridge, standard-axiom audit')

if __name__ == '__main__':
    main()

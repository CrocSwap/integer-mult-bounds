"""Run unchanged native checks on the literal E4 variant. Apache-2.0.

PR635 native scalar/frame/precision checks and PR558 phase checks are reused
without changing a mathematical predicate. Prepared with OpenAI Codex assistance.
"""
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from support import ROOT, SOURCE, dump, require, sha, validate_sources


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--word', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(__debug__, 'Native checks require assertions')
    validate_sources()
    require(not args.out.exists() and not args.out.resolve().is_relative_to(ROOT), 'Fresh external output')
    args.out.mkdir(parents=True)
    code = ROOT / 'research/complex-sw4-frame8/vendor/pr635/research/complex-571-cold14-st2/code'
    base = SOURCE / 'vendor/pr558'
    parent = base / 'vendor/pr552'
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1',
               PYTHONINTMAXSTRDIGITS='0', MULTICOLD_SOURCE=str(SOURCE), GAIN_PR564_SOURCE=str(SOURCE))
    for key in ('PYTHONOPTIMIZE', 'XPARAM', 'EXTRAH', 'PAIRING_RANKS', 'DIAG', 'HYBBUDGET', 'PR635_CODE'):
        env.pop(key, None)
    local = args.out / 'local'
    commands = [
        ('native', code / 'hpe_audit_and_transport.py', '--raw', args.word,
         '--routing', parent / 'complex-local/inputs/phase-baseline/CANONICAL-WORD.json.gz', '--out', local),
        ('ledgers', code / 'hpe_emit_local.py', local),
        ('local-replay', code / 'hpe_audit_local.py', local),
        ('wrappers', code / 'hpe_adapters_local.py', local / 'CANONICAL-WORD.json.gz',
         local / 'RESIDUAL-ADAPTERS.json', local / 'WRAPPER-CHECKS.json'),
        ('phases', base / 'code/phases_full.py', local, parent / 'complex-global/vendor531/vendor/clifford')]
    stages = []
    for name, script, *argv in commands:
        start = time.monotonic()
        log = args.out / (name + '.log')
        with log.open('w') as stream:
            result = subprocess.run([sys.executable, '-B', str(SOURCE / 'code/run_portable.py'),
                                     str(script), *map(str, argv)], cwd=ROOT, env=env,
                                    stdout=stream, stderr=subprocess.STDOUT)
        stages.append(dict(name=name, exit_code=result.returncode,
                           seconds=round(time.monotonic() - start, 3), log_sha256=sha(log)))
        dump(args.out / 'STAGES.json', stages)
        require(result.returncode == 0, name + ': ' + log.read_text(errors='replace')[-5000:])
        print('PASS E4 native', name, flush=True)


if __name__ == '__main__':
    main()

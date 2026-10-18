"""Emit and audit mixed-provider T37 with unmodified PR942 runtime code.

Discovery recounts the fixed construction, then a separate strict run checks
its frozen values. No optimizer runs. Apache-2.0; OpenAI Codex assistance.
"""
import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from support import P, ROOT, SOURCE, dump, read, require, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('discovery', 'strict'))
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--baseline942', type=Path, required=True)
    args = parser.parse_args()
    require(__debug__, 'Supplier checks require assertions')
    work, baseline = args.work, args.baseline942
    stage = work / args.mode
    require(not stage.exists(), 'New replay output required')
    stage.mkdir()
    code = work / 'runtime/code'
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0',
               MULTICOLD_SOURCE=str(SOURCE), GAIN_PR564_SOURCE=str(SOURCE),
               WITNESS_SPEC=str(work / 'runtime/data/SPEC.json'))
    for key in ('PYTHONOPTIMIZE', 'WITNESS_DISCOVER', 'WITNESS_RECORD'):
        env.pop(key, None)
    if args.mode == 'discovery':
        env.update(WITNESS_DISCOVER='1', WITNESS_RECORD=str(stage / 'WITNESS-RECORD.jsonl'))
    parent = work / 'parent'
    if not parent.exists():
        shutil.copytree(baseline / 'baseline799/global/parent558', parent)
        shutil.copyfile(work / 'lift/GLOBAL-TEMPLATE.json.gz', parent / 'complex-global/base/split-centres/GLOBAL-TEMPLATE.json.gz')
    g = stage / 'global'
    commands = [
        ('bind', code / 'bind_providers_portable.py', '--baseline', parent,
         '--provider', 'gauge44=' + str(baseline / 'native/local'),
         '--provider', 'gauge44_e4=' + str(work / 'native/local'), '--plan', work / 'lift/PLAN.json', '--out', g),
        ('emit', code / 'emit_allcold.py', '--base', g / 'base', '--owners', work / 'construction/OWNERS.json.gz',
         '--plan', g / 'PLAN.json', '--out', g / 'hosted'),
        ('audit', code / 'audit_allcold.py', g / 'base', g / 'hosted', g / 'audit/ASYNC-AUDIT.json', '--mutation-controls'),
        ('invoice', code / 'invoice_allcold.py', '--base', g / 'base', '--hosted', g / 'hosted',
         '--audit', g / 'audit', '--out', g / 'audit', '--retained-invoice',
         SOURCE / 'vendor/pr558/vendor/pr552/complex-global/vendor531/evidence/audit/PREFIX-AND-INVOICE.json'),
        ('assembly', code / 'assemble.py', SOURCE, g, stage / 'ASSEMBLY.json')]
    if args.mode == 'discovery':
        commands.append(('freeze', code / 'freeze_spec.py', '--spec', work / 'runtime/data/SPEC.json', '--discovery', stage))
        commands.append(('freeze-metadata', P / 'freeze_metadata.py', '--work', work))
    else:
        for label, script, output in [('admission-controls', 'assembly_controls.py', 'ADMISSION-CONTROLS.json'),
                                       ('bit-controls', 'bit_supplier_controls.py', 'BIT-CONTROLS.json')]:
            commands.append((label, code / script, '--source-package', SOURCE,
                             '--owner', g / 'audit/OWNERS-AND-PROFILE.json',
                             '--invoice', g / 'audit/PREFIX-AND-INVOICE.json', '--out', stage / output))
    stages = []
    for name, script, *argv in commands:
        start = time.monotonic()
        log = stage / (name + '.log')
        with log.open('w') as stream:
            result = subprocess.run([sys.executable, '-B', str(SOURCE / 'code/run_portable.py'),
                                     str(script), *map(str, argv)], cwd=ROOT, env=env,
                                    stdout=stream, stderr=subprocess.STDOUT)
        stages.append(dict(name=name, exit_code=result.returncode,
                           seconds=round(time.monotonic()-start, 3), log_sha256=sha(log)))
        dump(stage / 'STAGES.json', stages)
        require(result.returncode == 0, name + ': ' + log.read_text(errors='replace')[-6000:])
        print('PASS E4', args.mode, name, flush=True)
    print('COMPLETE', args.mode, read(stage / 'ASSEMBLY.json')['kappa_decimal'], flush=True)


if __name__ == '__main__':
    main()

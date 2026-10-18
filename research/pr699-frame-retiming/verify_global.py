"""Run the unchanged PR676 global admission on explicit provider directories.

Adapted from gauge44-promo-p6/verify_global.py. Its exact controller, invoice,
assembly and mutation checks remain in the pinned dependency package.
Prepared for tekuuu with substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('main', 'dependency', 'plan', 'owners', 'spec', 'work'):
        ap.add_argument('--' + name, type=Path, required=True)
    ap.add_argument('--provider', action='append', required=True, metavar='PID=DIR')
    ap.add_argument('--discover', action='store_true',
                    help='Recompute candidate expectations; a separate strict replay is required')
    args = ap.parse_args()
    need(__debug__, 'Assertions required in inherited checks')
    root, dep, plan, owners, spec, work = [getattr(args, name).resolve()
                                         for name in ('main', 'dependency', 'plan', 'owners', 'spec', 'work')]
    need(not work.exists(), 'Output directory must be new')
    providers = {}
    for item in args.provider:
        pid, separator, directory = item.partition('=')
        need(separator and pid and pid not in providers, 'Unique PID=DIR provider arguments required')
        providers[pid] = Path(directory).resolve()
        need(providers[pid].is_dir(), 'Missing provider directory: ' + directory)
    witness = read(spec)
    counts = Counter(p for _, _, p in witness['dispatch'])
    need(set(providers) == set(counts), 'Provider arguments differ from spec dispatch')
    need(len(witness['dispatch']) == 72 and sum(counts.values()) == 72, '72 dispatch rows required')
    source = root / 'research/complex-k492-owner-repair/vendor/multicold'
    baseline = root / 'research/community-k492-audit/pr622/replay/baseline558'
    vendor = source / 'vendor/pr558/vendor/pr552/complex-global/vendor531'
    pins = dep / 'data/UPSTREAM-PINS.json'
    for relative, expected in read(pins).items():
        need(sha(root / relative) == expected, 'Upstream dependency changed: ' + relative)
    # Check the dependency's own submitted inventory before invoking any code.
    subprocess.run([sys.executable, '-B', str(dep / 'verify_manifest.py')], check=True)
    work.mkdir(parents=True)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1',
               PYTHONINTMAXSTRDIGITS='0', MULTICOLD_SOURCE=str(source),
               GAIN_PR564_SOURCE=str(source), WITNESS_SPEC=str(spec))
    for key in ('PYTHONOPTIMIZE', 'WITNESS_DISCOVER', 'WITNESS_RECORD'):
        env.pop(key, None)
    if args.discover:
        env.update(WITNESS_DISCOVER='1', WITNESS_RECORD=str(work / 'WITNESS-RECORD.jsonl'))
    stages = []

    def run(name, script, *arguments, record=True):
        started = time.monotonic()
        log = work / (name + '.log')
        stage_env = env.copy()
        if not record:
            # Mutated admission receipts must never contaminate frozen expectations.
            stage_env.pop('WITNESS_RECORD', None)
        with log.open('w') as stream:
            result = subprocess.run([sys.executable, '-B', str(source / 'code/run_portable.py'),
                                     str(script), *map(str, arguments)], env=stage_env,
                                    stdout=stream, stderr=subprocess.STDOUT)
        stages.append(dict(name=name, seconds=round(time.monotonic() - started, 3),
                           exit_code=result.returncode, log_sha256=sha(log)))
        dump(work / 'STAGES.json', stages)
        if result.returncode:
            raise RuntimeError(name + ' failed:\n' + log.read_text()[-7000:])
        print('PASS', name, stages[-1]['seconds'], flush=True)

    code = dep / 'code'
    global_dir = work / 'global'
    run('restore-parent', code / 'restore_parent.py', '--source', source,
        '--baseline', baseline, '--out', work / 'parent558')
    provider_args = [value for pid, path in sorted(providers.items())
                     for value in ('--provider', pid + '=' + str(path))]
    run('bind', code / 'bind_providers_portable.py', '--baseline', work / 'parent558',
        *provider_args, '--plan', plan, '--out', global_dir)
    run('emit', code / 'emit_allcold.py', '--base', global_dir / 'base',
        '--owners', owners, '--plan', global_dir / 'PLAN.json', '--out', global_dir / 'hosted')
    run('audit', code / 'audit_allcold.py', global_dir / 'base', global_dir / 'hosted',
        global_dir / 'audit/ASYNC-AUDIT.json', '--mutation-controls')
    run('invoice', code / 'invoice_allcold.py', '--base', global_dir / 'base',
        '--hosted', global_dir / 'hosted', '--audit', global_dir / 'audit', '--out', global_dir / 'audit',
        '--retained-invoice', vendor / 'evidence/audit/PREFIX-AND-INVOICE.json')
    run('assembly', code / 'assemble.py', source, global_dir, work / 'ASSEMBLY.json')
    # Discovery also enumerates every admission control. Its accepted spec-only
    # mutations are recorded, and strict mode must reject the entire set.
    run('admission-controls', code / 'assembly_controls.py', '--source-package', source,
        '--owner', global_dir / 'audit/OWNERS-AND-PROFILE.json',
        '--invoice', global_dir / 'audit/PREFIX-AND-INVOICE.json',
        '--out', work / 'ADMISSION-CONTROLS.json', record=False)
    admission = read(work / 'ADMISSION-CONTROLS.json')
    if not args.discover:
        need(not admission['discovery_accepted_controls'], 'Strict admission accepted a mutation')
        run('bit-supplier-controls', code / 'bit_supplier_controls.py', '--source-package', source,
            '--owner', global_dir / 'audit/OWNERS-AND-PROFILE.json',
            '--invoice', global_dir / 'audit/PREFIX-AND-INVOICE.json',
            '--out', work / 'BIT-SUPPLIER-CONTROLS.json', record=False)
        bit = read(work / 'BIT-SUPPLIER-CONTROLS.json')
        need(bit['status'] == 'PASS_PR589_BIT_SUPPLIER_DERIVED_DEFICIT_NEGATIVE_CONTROLS'
             and len(bit['rejected_controls']) == 12 and bit['derived_deficit'] == 10272,
             'Incomplete inherited bit-supplier controls')
    result = read(work / 'ASSEMBLY.json')
    need(result['provider_counts'] == counts, 'Assembly dispatch changed')
    dump(work / 'REPLAY.json', dict(
        status='PASS_FRAME_RETIMING_DISCOVERY' if args.discover else 'PASS_FRAME_RETIMING_STRICT_GLOBAL_REPLAY',
        kappa=result['kappa'], kappa_decimal=result['kappa_decimal'],
        complex_lower=result['complex_lower'], bit_lower=result['bit_lower'],
        bit_supplier=result['bit_supplier'], provider_counts=dict(counts),
        gain_over_pr635_percent=result['gain_over_pr635_percent'], stages=stages,
        dependency_manifest_sha256=sha(dep / 'MANIFEST.json'),
        spec_sha256=sha(spec), plan_sha256=sha(plan), owners_sha256=sha(owners),
        scope=result['scope']))
    print(result['status'], result['kappa_decimal'], flush=True)


if __name__ == '__main__':
    main()

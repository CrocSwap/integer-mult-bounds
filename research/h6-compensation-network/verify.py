"""Replay the successor package with frozen inherited source bindings."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started = time.monotonic()
    pins = json.loads((HERE/'gate/PINS.json').read_text())
    task = json.loads((HERE/'TASK.json').read_text())
    need(pins['base'] == task['base'], 'Inherited pin base differs')
    for name, pin in pins['files'].items():
        need(sha(ROOT/name) == pin['sha256'], 'Frozen source binding: '+name)
    logs = HERE/'checks'
    logs.mkdir(exist_ok=True)
    scripts = ['artifact.py', 'contract/replay.py', 'construction/network.py', 'k_encoder/network.py',
               'coefficient_horner.py', 'independent/bucketed.py', 'independent/routes.py',
               'physical_compiler/compile.py', 'physical_compiler/universal.py',
               'pricing/verify.py', 'bank_physical/review.py', 'finite_grid.py']
    checks = []
    for script in scripts:
        command = [sys.executable, '-I', '-O', '-B', str(HERE/script)]
        run = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        output = run.stdout+run.stderr
        log = logs/(script.replace('/', '-')+'.txt')
        log.write_text(output)
        need(run.returncode == 0, script+' failed:\n'+output[-4000:])
        checks.append(dict(script=script, status='PASS', sha256=sha(HERE/script),
                           log=str(log.relative_to(HERE)), log_sha256=sha(log)))
        print(script+': PASS', flush=True)
    independent = json.loads((HERE/'independent/RESULT.json').read_text())
    need(independent['factor']['polynomial_entries'] == 665856 and
         independent['factor']['actual_feature_entries_bound'] == 25263360,
         'Complete factor/evaluator binding')
    full = independent['full_schema']
    need(full['helper_count'] == 227312640 and full['weighted_edges'] == 480337920,
         'Full bucket census')
    need(full['compensation_ADD_count'] == 1415301120 and
         full['standalone_compensation_total_events'] == 2097300960,
         'Complete compensation opcode census')
    need(json.loads((HERE/'physical_compiler/UNIVERSAL-RESULT.json').read_text())
         ['full_endpoint_completion_checks'] == 14670, 'Universal endpoint census')
    grid = json.loads((HERE/'GRID.json').read_text())
    need(grid['extra_fractional_bits']['common'] == 60, 'Exact-child grid ledger')
    result = dict(status='PASS_UNIFIED_SCOPED_COMPENSATION_PACKAGE', base=task['base'],
        selected_base=task['selected_base'], checks=checks,
        inherited_files_checked=len(pins['files']), inherited_pins_sha256=sha(HERE/'gate/PINS.json'),
        elapsed_seconds=round(time.monotonic()-started, 3),
        scope='Complete compressed full-edge/bucket schemas and exact factor proof, emitted finite all-column words, physical recipe family, coefficient streams, finite exact-child grid and rational nominal pricing. No billion-event full execution or admitted all-size supplier.',
        no_new_kappa=True, hosted_CI=False)
    (HERE/'RESULT.json').write_text(json.dumps(result, sort_keys=True, indent=2)+'\n')
    print(result['status'], flush=True)


if __name__ == '__main__':
    main()

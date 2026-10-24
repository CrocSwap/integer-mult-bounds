"""Complete provider's resource-stopped arithmetic without rerunning its algebra.

The prior two successful engines are fresh in this session. Their logs and
complete mathematical outputs are authenticated before final acceptance.
"""
from pathlib import Path
import hashlib
import json
import os
import runpy
import subprocess
import sys
import tempfile
import time

base = Path(__file__).resolve().parent
package = Path(sys.argv[1]).resolve()
prior = json.loads((base / 'PROVIDER-REPLAY.json').read_text())
assert [r['name'] for r in prior['runs']] == ['algebra', 'same-chart-control', 'budget']
assert [r['returncode'] for r in prior['runs']] == [0, 0, 1]
root = Path(prior['scratch']).resolve()
scope = runpy.run_path(str(package / 'verify.py'), run_name='_maintainer_authenticated')
before = scope['check'](package)
assert before == prior['bindings']
commands = json.loads((package / 'COMMANDS.json').read_text())['commands']
for i, record in enumerate(prior['runs'][:2]):
    for stream in ('stdout', 'stderr'):
        assert hashlib.sha256((root / f'run-{i}.{stream}').read_bytes()).hexdigest() == record[stream + '_sha256']
trace = base / 'provider-resource-fallback.jsonl'
assert not trace.exists()
trace.touch()
env = os.environ.copy()
env['MAINTAINER_RLIMIT_TRACE'] = str(trace)
report = {'status': 'RUNNING', 'mode': 'resume_after_Darwin_RLIMIT_AS_failure',
          'prior_receipt_sha256': hashlib.sha256((base / 'PROVIDER-REPLAY.json').read_bytes()).hexdigest(),
          'bindings': before, 'scratch': str(root), 'runs': prior['runs'][:2],
          'fresh_algebra_reused_from_this_session': True}
try:
    for index, command in enumerate(commands[2:], 2):
        output = root / command['result']
        assert not output.exists(), str(output)
        argv = [sys.executable, '-I', '-B', str(base / 'macos_engine.py'),
                str(package / 'engine_adapter.py'), str(root), command['engine'],
                *command['argv']]
        start = time.monotonic()
        run = subprocess.run(argv, cwd=root, env=env, capture_output=True,
                             timeout=command['timeout_seconds'])
        row = {'name': command['name'], 'argv': argv, 'returncode': run.returncode,
               'seconds': time.monotonic() - start}
        for stream in ('stdout', 'stderr'):
            raw = getattr(run, stream)
            (root / f'resumed-{index}.{stream}').write_bytes(raw)
            row[stream + '_sha256'] = hashlib.sha256(raw).hexdigest()
        report['runs'].append(row)
        if run.returncode:
            raise RuntimeError(command['name'] + ': ' + run.stderr.decode())
    report['fresh_scientific_summary'] = scope['validate'](package, root, commands)
    assert scope['check'](package) == before
    report['status'] = 'PASS_INDEPENDENT_PARTIAL_PROVIDER_AND_CONDITIONAL_BUDGET'
except BaseException as error:
    report['status'] = 'FAIL'
    report['error'] = repr(error)
    raise
finally:
    report['resource_fallbacks'] = [json.loads(s) for s in trace.read_text().splitlines()]
    with (base / 'PROVIDER-COMPLETED.json').open('x') as f:
        json.dump(report, f, indent=2, sort_keys=True)
        f.write('\n')
    print(json.dumps({'status': report['status'], 'runs': [(r['name'], r['returncode']) for r in report['runs']]}))

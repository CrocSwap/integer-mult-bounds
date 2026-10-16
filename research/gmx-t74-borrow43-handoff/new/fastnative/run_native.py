#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Complete T74 native replay; fresh source snapshot, no result cache.

Uses the unchanged T74 transport, emitter, local audit, adapters, phase lowering
and independent warp-recipe audit. Only Op.zero_state in the two Clifford-using
stages changes to the previously published exact sparse evaluator.
"""
import argparse
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import HERE, need, sha, source_bytes

STEPS = ('native', 'ledgers', 'local-replay', 'wrappers', 'phases')

def main():
    need(__debug__, 'assertions must remain enabled')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('word', type=Path)
    parser.add_argument('work', type=Path)
    parser.add_argument('--engine', choices=('reference', 'sparse'), default='sparse')
    args = parser.parse_args()
    started = time.monotonic()
    blobs = source_bytes(HERE / 'vendor')
    original = args.word.resolve()
    need(original.is_file(), 'input word missing')
    body = original.read_bytes()
    work = args.work.resolve()
    need(not work.exists(), 'fresh work directory required')
    work.mkdir(parents=True)
    vendor = work / 'source'
    for name, contents in blobs.items():
        target = vendor / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(contents)
    word = work / ('INPUT.json.gz' if original.suffix == '.gz' else 'INPUT.json')
    word.write_bytes(body)
    native = vendor / 'native/new/code/borrow'
    output = work / 'native'
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONINTMAXSTRDIGITS='0')
    env.pop('PYTHONOPTIMIZE', None)
    commands = []
    def run(name, command, cwd):
        before = time.monotonic()
        with (work / (name + '.log')).open('w') as log:
            result = subprocess.run(command, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                                    stdout=log, stderr=subprocess.STDOUT)
        entry = {'step': name, 'exit_code': result.returncode,
                 'seconds': time.monotonic()-before, 'command': command}
        commands.append(entry)
        (work / 'COMMANDS.json').write_text(json.dumps(commands, indent=2)+'\n')
        need(result.returncode == 0, 'stage failed: '+name+'; see '+str(work/(name+'.log')))
        return entry
    if args.engine == 'reference':
        run('reference-driver', [sys.executable, '-I', '-B', str(vendor/'native/new/run_native_borrow.py'), str(word), str(output)], native)
        steps = json.loads((output/'STEPS.json').read_text())
    else:
        output.mkdir()
        local = output/'local'
        plan = [
            ('native', [('bw_transport.py', [word, local])]),
            ('ledgers', [('bw_emit.py', [local])]),
            ('local-replay', [('bw_audit_local.py', [local])]),
            ('wrappers', [('bw_adapters.py', [local/'CANONICAL-WORD.json.gz', local/'RESIDUAL-ADAPTERS.json', local/'WRAPPER-CHECKS.json'])]),
            ('phases', [('bw_phases.py', [local]), ('bw_check_recipes.py', [local])]),
        ]
        steps = []
        for label, scripts in plan:
            before = time.monotonic()
            for script, arguments in scripts:
                if script in ('bw_adapters.py', 'bw_phases.py'):
                    command = [sys.executable, '-I', '-B', str(HERE/'stage.py'), '--vendor', str(vendor), '--script', script]
                else:
                    command = [sys.executable, '-I', '-B', str(native/script)]
                run(label+'-'+script, command + list(map(str, arguments)), native)
            steps.append({'step':label,'exit_code':0,'seconds':time.monotonic()-before})
            (output/'STEPS.json').write_text(json.dumps(steps,indent=2)+'\n')
            print('PASS', label, flush=True)
    need([s['step'] for s in steps] == list(STEPS) and all(s['exit_code']==0 for s in steps), 'complete native stage coverage')
    need(source_bytes(vendor) == blobs and word.read_bytes() == body, 'source or input modified')
    result = {'status':'PASS_COMPLETE_T74_NATIVE_REPLAY', 'engine':args.engine,
              'word_sha256':sha(body), 'source_sha256':{k:sha(v) for k,v in sorted(blobs.items())},
              'steps':steps, 'seconds':time.monotonic()-started, 'python':platform.python_version(),
              'scope':'Full five-stage native replay including independent all-column warp recipes and original rejection controls; supplier/outer admission separate.'}
    (work/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'], args.engine, round(result['seconds'],3), flush=True)

if __name__ == '__main__':
    main()

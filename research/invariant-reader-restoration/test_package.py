#!/usr/bin/env python3
"""Relocation and rejection tests for the scoped evidence package."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def run(directory, *args, success=True):
    result = subprocess.run([sys.executable, '-I', '-O', '-B', str(directory/'verify.py'), *map(str,args)],
                            cwd=directory.parent, capture_output=True, text=True)
    require((result.returncode == 0) == success,
            f'Unexpected verifier result ({result.returncode}): {result.stdout}{result.stderr}')
    if success and not args:
        require('PASS_INVARIANT_READER_RESTORATION' in result.stdout, 'missing success marker')
    return result


def main():
    controls = 0
    with tempfile.TemporaryDirectory(prefix='reader-restoration-') as tmp:
        root = Path(tmp)
        base = root/'relocated-package'
        shutil.copytree(HERE, base)
        run(base)
        out = root/'export.json'
        run(base, '--write', out)
        require(out.read_bytes() == (base/'CERTIFICATE.json').read_bytes(), 'nondeterministic export')

        def mutated(name, filename, change):
            nonlocal controls
            directory = root/name
            shutil.copytree(base, directory)
            path = directory/filename
            path.write_text(change(path.read_text()))
            run(directory, success=False)
            controls += 1

        def unpaid(text):
            receipt = json.loads(text)
            receipt['catalytic_wrapper']['invoice_deferred']['add_instructions'] -= 1
            return json.dumps(receipt)

        def replace_once(old, new):
            def change(text):
                require(text.count(old) == 1, 'mutation anchor ambiguous or missing')
                return text.replace(old, new)
            return change

        mutated('unpaid-operation', 'CERTIFICATE.json', unpaid)
        mutated('source-drift', 'sources/PR1155-README.md', lambda text: text+'\nCORRUPTED\n')
        mutated('unrestored-accumulator', 'backend.py',
                replace_once('accumulator -= memory[source]', 'accumulator += memory[source]'))
        mutated('bad-swap', 'backend.py',
                replace_once('("add", first, temp, -1)', '("add", first, temp, 1)'))
        mutated('wrong-product-order', 'backend.py',
                replace_once('composed = [composed[source] for source in permutation]',
                             'composed = [permutation[source] for source in composed]'))
        mutated('missing-wrapper-inverse', 'verify.py',
                replace_once("wrapped_d = pre_reads + load + deferred['program'] + unload",
                             "wrapped_d = pre_reads + load + deferred['program']"))
        mutated('missing-wrapper-preread', 'verify.py',
                replace_once("wrapped_d = pre_reads + load + deferred['program'] + unload",
                             "wrapped_d = load + deferred['program'] + unload"))
        mutated('wrong-shared-criterion', 'verify.py',
                replace_once('expected_shared = not any(total)', 'expected_shared = expected'))
    print(f'PASS_READER_RESTORATION_PACKAGE relocation=1 deterministic_export=1 corruption_controls={controls}')

if __name__ == '__main__':
    main()

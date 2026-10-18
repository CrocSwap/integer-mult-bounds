#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exercise the actual read-only CLI on a disposable Git-free export.
Prepared for commdata2338 with substantial OpenAI Codex assistance.
"""
from hashlib import sha256
from pathlib import Path
import copy
import json
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/direct-delivery504-global/inputs/hamming/PROTOTYPE.json'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def main():
    with tempfile.TemporaryDirectory(prefix='p112-coefficient-controls-') as tmp:
        export = Path(tmp)
        package = export/'research'/'p112-coefficient-copy-floor'
        package.mkdir(parents=True)
        for filename in ('verify.py', 'CERTIFICATE.json'):
            shutil.copyfile(HERE/filename, package/filename)
        source = export/SOURCE
        source.parent.mkdir(parents=True)
        shutil.copyfile(ROOT/SOURCE, source)
        checker, certificate = package/'verify.py', package/'CERTIFICATE.json'
        original = certificate.read_bytes()
        parsed = json.loads(original)
        source_bytes = source.read_bytes()
        checked_files = [checker, certificate, source]
        before = {p: sha256(p.read_bytes()).hexdigest() for p in checked_files}

        def run(expect=None, *args):
            completed = subprocess.run([sys.executable, '-I', '-O', '-B', str(checker), *args],
                                       cwd=export, capture_output=True, text=True, timeout=30)
            if expect is None:
                need(completed.returncode == 0, completed.stderr)
                need('PASS_P112_COEFFICIENT_COPY_FLOOR' in completed.stdout, 'missing success marker')
            else:
                need(completed.returncode != 0 and expect in completed.stderr,
                     'unexpected control outcome: '+completed.stdout+completed.stderr)

        # A complete positive export works with no Git or write permission on inputs.
        for p in checked_files:
            p.chmod(0o444)
        run()
        for p in checked_files:
            p.chmod(0o644)
        need(before == {p: sha256(p.read_bytes()).hexdigest() for p in checked_files},
             'read-only replay changed an input')
        controls = ['optimized_Git_free_read_only_export']
        source.write_bytes(source_bytes+b' ')
        run('source digest mismatch')
        source.write_bytes(source_bytes)
        controls.append('changed_source_bytes')

        def mutate(change):
            obj = copy.deepcopy(parsed)
            change(obj)
            certificate.write_text(json.dumps(obj))
            run('certificate mismatch')
            certificate.write_bytes(original)

        mutate(lambda obj: obj.__setitem__('exceptional_lambda', -7))
        controls.append('wrong_exceptional_parameter')
        mutate(lambda obj: obj.__setitem__('schema_version', True))
        controls.append('bool_integer_substitution')
        mutate(lambda obj: obj['uniform_attainer']['ranks'].__setitem__(0, 7))
        controls.append('wrong_actual_support_rank')
        mutate(lambda obj: obj['exceptional_attainer']['N'][8].__setitem__(1, '0'))
        controls.append('wrong_exceptional_basis')
        certificate.write_text('{"schema_version":1,"schema_version":1}')
        run('duplicate JSON key')
        certificate.write_text('{"schema_version":NaN}')
        run('nonfinite JSON number')
        certificate.write_bytes(original)
        controls.extend(['duplicate_JSON_key', 'nonfinite_JSON_number'])
        occupied = export/'occupied.json'
        occupied.write_bytes(b'preserve this output\n')
        run('output exists', '--write', str(occupied))
        need(occupied.read_bytes() == b'preserve this output\n', 'occupied output modified')
        controls.append('occupied_output_preserved')
        fresh = export/'fresh.json'
        run(None, '--write', str(fresh))
        need(json.loads(fresh.read_bytes()) == parsed, 'fresh receipt differs')
        need(before == {p: sha256(p.read_bytes()).hexdigest() for p in checked_files},
             'controls failed to restore input bytes')
        print('PASS_P112_COEFFICIENT_CLI_CONTROLS groups='+str(len(controls))+' fresh_receipt=identical')


if __name__ == '__main__':
    main()

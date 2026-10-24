#!/usr/bin/env python3
"""Portable adapter for the unchanged independent one-CZ grade check.

Only the source acquisition line is replaced: Git output becomes authenticated
vendored bytes. Scientific code/receipt stay unchanged; generation is in private
scratch. Apache-2.0; substantial OpenAI Codex assistance; predecessor credit in
grade/check.py and PROOF.md.
"""
from contextlib import redirect_stdout
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import io
import json

HERE = Path(__file__).resolve().parent
AUTHOR_SHA = '6d77983fccc03afc9bbc2b8b06dc1dc9db0baf2431f503bca834cf42b69edc2b'
COMPILER_SHA = '2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962'
OLD = "raw=subprocess.check_output(['git','show',PIN+':'+PATH],env={**os.environ,'GIT_NO_REPLACE_OBJECTS':'1'})"


def need(ok, why):
    if not ok:
        raise ValueError(why)


def run():
    body = (HERE/'grade/check.py').read_bytes()
    compiler = (HERE/'inputs/native/clifford_exact.py').read_bytes()
    need(sha256(body).hexdigest() == AUTHOR_SHA, 'Unchanged independent grade checker')
    need(sha256(compiler).hexdigest() == COMPILER_SHA, 'Exact retained Clifford source')
    text = body.decode('utf-8')
    need(text.count(OLD) == 1, 'Only exact documented source loader is adapted')
    adapted = text.replace(OLD, 'raw=FROZEN_COMPILER_SOURCE')
    expected = json.loads((HERE/'grade/RESULT.json').read_text())
    with TemporaryDirectory(prefix='two-full-grade-') as scratch:
        local = Path(scratch)
        env = {'__file__': str(local/'check.py'), '__name__': 'grade_private_replay',
               'FROZEN_COMPILER_SOURCE': compiler}
        with redirect_stdout(io.StringIO()):
            exec(compile(adapted, 'unchanged_grade_check_with_portable_loader', 'exec'), env)
        actual = json.loads((local/'RESULT.json').read_text())
        need(actual == expected, 'Independent controlled-phase scientific receipt')
    return {'status': 'PASS_PORTABLE_CONTROLLED_PHASE_GRADE_REPLAY',
            'full17_axis_grades': actual['full17_axis_grades'],
            'lower_grade_purity_gate_passed': actual['lower_grade_purity_gate_passed'],
            'endpoint_identity_proved': actual['endpoint_identity_proved'],
            'source_loader_only_adapted': True, 'registered_outputs_read_only': True}


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True))

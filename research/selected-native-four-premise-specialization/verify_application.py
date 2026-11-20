#!/usr/bin/env python3
"""Freshly run the unchanged selected application checker and bind its output."""
from contextlib import redirect_stdout
from hashlib import sha256
from pathlib import Path
import io
import json
import runpy

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    for pin in json.loads((HERE/'SOURCE-PINS.json').read_text()):
        data = (HERE/'inputs'/pin['path']).read_bytes()
        need(sha256(data).hexdigest() == pin['sha256'], 'source bytes: '+pin['path'])
    prefix = HERE/'inputs/docs/research/pr-intake-evidence/pr7000-application'
    stream = io.StringIO()
    with redirect_stdout(stream):
        runpy.run_path(str(prefix/'check_application.py'), run_name='__main__')
    actual = stream.getvalue().encode()
    need(actual == (prefix/'application.log').read_bytes(), 'fresh exact application output differs from selected receipt')
    result = json.loads(actual)
    need(result['status'] == 'PASS_CURRENT_SOURCE_APPLICATION_MAPS', 'application success marker')
    print(json.dumps(dict(status='PASS_FRESH_SELECTED_APPLICATION_REPLAY',
                         output_sha256=sha256(actual).hexdigest(),
                         complex=result['complex'], bit=result['bit'],
                         negative_controls=result['negative_controls']), indent=2))


if __name__ == '__main__':
    main()

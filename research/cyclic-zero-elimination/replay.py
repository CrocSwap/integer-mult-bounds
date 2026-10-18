#!/usr/bin/env python3
"""Run PR621's exact checks with zero-coefficient row updates omitted.

Ali Romman's original verifier remains byte-pinned and unchanged. Adapter by
thakrarsagar with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
SOURCE = PACKAGE.parent / 'prime-power-cyclic-inverse'
PINS = json.loads((PACKAGE / 'SOURCE.json').read_text())['files']
ANCHOR = '            value = a[row][col]\n            for j'
GUARD = '            value = a[row][col]\n            if value == k.zero:\n                continue\n            for j'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def prepare(data, fast):
    require(hashlib.sha256(data).hexdigest() == PINS['verify.py'],
            'Predecessor verifier source changed')
    text = data.decode('utf-8')
    require(text.count(ANCHOR) == 1, 'Expected exactly one elimination anchor')
    return text.replace(ANCHOR, GUARD) if fast else text


def load(fast):
    namespace = {'__name__': 'cyclic_verifier', '__file__': str(SOURCE / 'verify.py')}
    exec(compile(prepare((SOURCE / 'verify.py').read_bytes(), fast),
                 str(SOURCE / 'verify.py'), 'exec'), namespace)
    return namespace


if __name__ == '__main__':
    code = prepare((SOURCE / 'verify.py').read_bytes(), True)
    exec(compile(code, str(SOURCE / 'verify.py'), 'exec'),
         {'__name__': '__main__', '__file__': str(SOURCE / 'verify.py')})

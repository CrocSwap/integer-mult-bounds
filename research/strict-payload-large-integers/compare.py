#!/usr/bin/env python3
"""Opt-in PR2040 successor with process-limit-independent exact JSON integers.

Arham Tahir, with substantial OpenAI Codex assistance. Apache-2.0.
The frozen comparator and all its other comparison rules are retained.
"""
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import sys
from types import ModuleType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREDECESSOR = 'research/strict-replay-payload-comparison/compare.py'


def source(name):
    """Return the very bytes authenticated, without consulting a .pyc cache."""
    manifest = json.loads((HERE / 'SOURCES.json').read_bytes())
    rows = [r for r in manifest['files'] if r['path'] == name and r['usage'] == 'input']
    if len(rows) != 1:
        raise ValueError('missing unique source pin: ' + name)
    raw = (ROOT / name).read_bytes()
    row = rows[0]
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    if hashlib.sha256(raw).hexdigest() != row['sha256'] or blob != row['git_blob']:
        raise ValueError('source bytes differ: ' + name)
    return raw


def predecessor():
    module = ModuleType('_strict_integer_predecessor')
    module.__file__ = str(ROOT / PREDECESSOR)
    exec(compile(source(PREDECESSOR), module.__file__, 'exec'), module.__dict__)
    return module


strict = predecessor()


def read_json(raw):
    """Keep integer tags and exact values without changing sys's digit limit.

    Decimal's string constructor and conversion to int are exact and do not
    apply the int<->decimal-string limit or the decimal arithmetic precision.
    JSON's own lexer still enforces the integer grammar before this callback.
    """
    def pairs(items):
        result = {}
        for key, value in items:
            strict.require(key not in result, 'duplicate JSON key: ' + repr(key))
            result[key] = value
        return result

    def constant(value):
        raise strict.InvalidPayload('nonfinite JSON constant: ' + value)

    return json.loads(raw, object_pairs_hook=pairs,
                      parse_int=lambda text: int(Decimal(text)),
                      parse_float=Decimal, parse_constant=constant)


def integer_summary(value):
    """A bounded diagnostic, never an equality test or a decimal conversion."""
    magnitude = abs(value)
    raw = magnitude.to_bytes((magnitude.bit_length() + 7) // 8, 'big')
    digest = hashlib.sha256((b'-' if value < 0 else b'+') + raw).hexdigest()
    return "('integer', sign={}, bits={}, sha256={})".format(
        '-' if value < 0 else '+', magnitude.bit_length(), digest)


def summary(node):
    if node[0] == 'integer':
        return integer_summary(node[1])
    try:
        return repr(node)[:160]
    except ValueError:
        return '<' + node[0] + ': representation exceeds integer digit limit>'


_first_difference = strict.first_difference


def first_difference(a, b, path=()):
    # The predecessor's repr(integer) can hit the same process limit on an
    # unequal pair. Its recursive calls use this wrapper, so the typed path is
    # preserved at the leaf where that conversion fails.
    try:
        return _first_difference(a, b, path)
    except ValueError:
        return {'path': list(path), 'kind': 'value-or-type',
                'reference': summary(a), 'run': summary(b)}


strict.read_json = read_json
strict.first_difference = first_difference


def __getattr__(name):
    return getattr(strict, name)


if __name__ == '__main__':
    sys.exit(strict.main())

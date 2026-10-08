"""Exact input boundary for the PR53 skip-prefix clones. Apache-2.0.

Prepared by Chafik Boukhalfa with OpenAI Codex assistance.
"""
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def loads(text):
    def reject(value):
        raise ValueError('Noninteger JSON number forbidden: '+value)
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'Duplicate JSON key: '+key)
            result[key] = value
        return result
    return json.loads(text, parse_float=reject, parse_constant=reject,
                      object_pairs_hook=unique)


def read(path):
    return loads(Path(path).read_text())


def integer(value, name, minimum=0):
    require(type(value) is int and value >= minimum, 'Invalid integer: '+name)
    return value


def bit_list(value, name):
    require(type(value) is list, 'Bit schedule must be a JSON array: '+name)
    require(all(type(bit) is int and bit in (0, 1) for bit in value),
            'Bits must be integer 0 or 1: '+name)
    return value[:]

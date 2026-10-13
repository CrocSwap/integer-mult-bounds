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


REPLAY_INPUTS = ['cloned_graph.py', 'clone-jobs-23.json', 'clone-jobs-25.json',
                 'clone_io.py', 'producer.py', 'profiles.cpp', 'links-23.uses', 'links-25.uses']
CERTIFICATE_INPUTS = REPLAY_INPUTS + ['witness.py', 'parameters.json', 'comparison-pr53.json',
                                    'PROOF.md', 'README.md']
CERTIFICATE_INPUTS += [f'{kind}-{h}.json' for h in (23, 25)
                       for kind in ('original', 'profiles', 'scalar', 'timeline')]


def check_sources(required=()):
    source = read(HERE/'SOURCE.json')
    require(type(source.get('files')) is dict, 'Missing pinned source dictionary')
    current = [path.name for path in HERE.iterdir()
               if path.suffix in ('.py', '.cpp', '.uses', '.json', '.md') and path.name not in
               ('SOURCE.json', 'certificate.json', 'validation.json', 'producer-receipt.json')]
    required = list(required)+current
    for name in required:
        require('research/skip-clones/'+name in source['files'], 'Missing source pin: '+name)
    for name, digest in source['files'].items():
        require(sha256((ROOT/name).read_bytes()).hexdigest() == digest,
                'Pinned inherited source changed: '+name)
    return source

"""Read the source-bound rational P104 word. apoursh with OpenAI Codex, Apache-2.0."""
from fractions import Fraction
from functools import cache
import gzip
import hashlib
import json
from pathlib import Path


def require(test, message):
    if not test:
        raise ValueError(message)


@cache
def scalar(value):
    return Fraction(value)


def read_word():
    raw = (Path(__file__).parent / 'retained' / 'WORD.json.gz').read_bytes()
    require(hashlib.sha256(raw).hexdigest() ==
            'fde0f7eaa3749d0934a9fc0d6320074f021cd722ed6753f3a59a62fb5b221949',
            'original archive')
    data = gzip.decompress(raw)
    require(hashlib.sha256(data).hexdigest() ==
            'c447b6d5ba956fbe40834fe3c1bc69af2f225736f1b97ecd84b57bab9dd283cb',
            'literal source word')
    word = json.loads(data)
    program = {k: {s: scalar(q) for s, q in row} for k, row in word['forms']}
    routes = {k: (a, b) for k, a, b in word['moves']}
    terminals = {word['first_output'] + j: c for j, c in enumerate(word['final'])}
    require(len(word['schedule']) == len(program) == 6998 and
            len(routes) == 5709 and len(terminals) == len(word['initial']) == 1289,
            'source dimensions')
    require(set(word['schedule']) == set(program) == routes.keys() | terminals.keys(),
            'complete schedule')
    return word, program, routes, terminals


def check_causality(word, program, routes, terminals):
    homes = {~i: chart for i, chart in enumerate(word['initial'])}
    for k in word['schedule']:
        owner = routes[k][0] if k in routes else terminals[k]
        require(all(homes.get(s) == owner for s in program[k]),
                f'wrong causal stock at {k}')
        if k in routes:
            homes[k] = routes[k][1]

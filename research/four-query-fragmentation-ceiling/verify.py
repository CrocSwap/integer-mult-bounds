#!/usr/bin/env python3
"""Bind independent literal words and replay the complete result.
Jerry Chen / @CubeJerry, substantial OpenAI Codex assistance. Apache-2.0.
"""
from contextlib import redirect_stdout
from hashlib import sha256
from io import StringIO
from pathlib import Path
import importlib.util
import json
import subprocess
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent

def require(condition, message):
    if not condition:
        raise ValueError(message)

def module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

def main():
    author = module('construct')
    reverse = module('reverse_check')
    translated = []
    for gate in reverse.AUTHOR_WORD:
        op = gate[0]
        if op == 'native':
            _, dst, src, body = gate
            require(body in (reverse.L, reverse.R), 'literal native body')
            translated.append(('NATIVE', 'L' if body == reverse.L else 'R', dst, src))
        elif op == 'idle':
            _, dst, body = gate
            require(body in (reverse.L, reverse.R), 'literal idle body')
            translated.append(('IDLE', dst, 'L' if body == reverse.L else 'R'))
        elif op == 'query':
            _, dst, src, coefficient = gate
            require(coefficient == 1, 'literal positive-query coefficient')
            translated.append(('QUERY', dst, src))
        else:
            translated.append((op.upper(), *gate[1:]))
    require(translated == author.construct(), 'independent literal words agree')
    buf = StringIO()
    with redirect_stdout(buf):
        author.main()
    require(buf.getvalue() == (HERE / 'CONSTRUCTION-REPLAY.txt').read_text(),
            'retained construction receipt and source expansion')
    buf = StringIO()
    with redirect_stdout(buf):
        reverse.main()
    reverse_receipt = json.loads(buf.getvalue())
    require(reverse_receipt['status'] == 'PASS_INDEPENDENT_REVERSE_FOUR_QUERY',
            'independent reverse replay')
    options = ['-I', '-B'] + (['-O'] if sys.flags.optimize else [])
    for name in ('economics.py', 'decimal_review.py'):
        done = subprocess.run([sys.executable, *options, str(HERE / name)],
                              capture_output=True, text=True, timeout=180)
        require(done.returncode == 0, name + ': ' + done.stderr)
    result = json.loads((HERE / 'RESULT.json').read_text())
    print(json.dumps({
        'status': 'PASS_FOUR_QUERY_FRAGMENTATION_CEILING',
        'arbitrary_input_coefficients': 36,
        'source_expansion_events': 21,
        'construction_mutations_rejected': 21,
        'reverse_controls_rejected': len(reverse_receipt['controls']),
        'economic_status': result['status'],
        'complex_raw_ceiling': result['complex']['raw_ceiling'],
        'bit_raw_ceiling': result['bit']['raw_ceiling'],
        'economic_receipt_sha256': sha256((HERE / 'RESULT.json').read_bytes()).hexdigest(),
        'kappa_change': 'No new κ',
        'scope': 'Formal atomic construction and fixed-source complete grammar ceiling; no physical admission.'
    }, indent=2, sort_keys=True))

if __name__ == '__main__':
    main()

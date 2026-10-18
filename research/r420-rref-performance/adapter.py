# SPDX-License-Identifier: Apache-2.0
"""Opt-in PR543 RREF adapter; preserves the pinned checker's remaining code.

Prepared for MrPink604 with substantial OpenAI Codex assistance.
The integer kernel is Aman's PR367, unchanged; see NOTICE.md.
"""
import hashlib
import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'research/e8-bit-r420/code/xcheck.py'
WORD = ROOT / 'research/e8-bit-r420/data/bitE8mut-r420.json.gz'
MUTANTS = ROOT / 'research/e8-bit-r420/code/mutants.py'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def bind_sources(root=ROOT):
    require(not sys.flags.optimize, 'Assertions must remain enabled for the original mutation harness')
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    for row in manifest['files']:
        data = (root / row['path']).read_bytes()
        require(len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256']
                and hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == row['git_blob'],
                'Source pin mismatch: ' + row['path'])


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


bind_sources()
_kernel = load_module('r420_integer_rows', HERE / 'vendor/exact_rows.py')


def rref(rows):
    """Return exactly PR543's rational basis rows and pivot columns.

    Scope: finite rectangular matrices of integers or Fractions. No input
    cache, floating arithmetic, modular rank guess or input mutation.
    """
    matrix, pivots = _kernel._eliminate(rows, reduced=True)
    return [[Fraction(x, row[column]) for x in row]
            for row, column in zip(matrix, pivots)], pivots


def load_checker(fast=True):
    checker = load_module('r420_reference', SOURCE)
    if fast:
        checker.rref = rref
    return checker


# The original mutants.py imports these through its XCHECK_PY argument.
_checker = load_checker()
Reject = _checker.Reject
Word = _checker.Word
check = _checker.check


if __name__ == '__main__':
    raise SystemExit('Use verify.py or benchmark.py; adapter.py is an import-only checker adapter')

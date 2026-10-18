#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Authenticate the closed source snapshot before importing any vendored code."""
import hashlib
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent

def need(condition, message):
    if not condition:
        raise ValueError(message)

def sha(body):
    return hashlib.sha256(body).hexdigest()

def source_bytes(vendor):
    pins = json.loads((HERE / 'PINS.json').read_text())
    expected = {p.removeprefix('vendor/'): h for p, h in pins.items() if p.startswith('vendor/')}
    paths = list(vendor.rglob('*'))
    need(not vendor.is_symlink() and all(not p.is_symlink() for p in paths), 'source symlink')
    actual = {p.relative_to(vendor).as_posix(): p.read_bytes() for p in paths if p.is_file()}
    need(set(actual) == set(expected), 'complete source path inventory')
    for name, body in actual.items():
        need(sha(body) == expected[name], 'source digest: ' + name)
    return actual

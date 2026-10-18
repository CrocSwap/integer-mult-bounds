#!/usr/bin/env python3
"""Reproduce every field of pinned PR2464's original result, without edits.

This is a primary-source positive control, not the independent cost audit.
Canonical JSON equality was first checked against its original RESULT.json.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXPECTED = '5da6570f9f06c27892578a829382d6d043f2ab9c8ed6deec3089e39efc1bba8f'


def main():
    for entry in json.loads((HERE/'EXTERNAL-SOURCE.json').read_text())['files']:
        if hashlib.sha256((HERE/entry['path']).read_bytes()).hexdigest() != entry['sha256']:
            raise ValueError('external source mismatch')
    spec = importlib.util.spec_from_file_location('primary2464', HERE/'inputs/pr2464/verify.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Relocate input paths only. The archived source code remains byte-identical.
    module.ROOT = ROOT
    module.PRE_DIR = ROOT/'research/z4-persistent-pair-seed57/inputs'
    module.CERT_PATH = module.PRE_DIR/'PR1391-CERTIFICATE.json'
    module.CODE_PATH = module.PRE_DIR/'PR1391-verify.py'
    # JSON object keys are strings in the published receipt. Normalize before
    # sorting so Python's integer-key order cannot change the canonical form.
    result = json.loads(json.dumps(module.build_result()))
    digest = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    if digest != EXPECTED:
        raise ValueError('original full result differs')
    print('PASS_PR2464_FULL_PAYLOAD_REPLAY controls=51 primary_source_only')


if __name__ == '__main__':
    main()

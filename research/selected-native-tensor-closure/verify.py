#!/usr/bin/env python3
"""Source-bound selected native tensor closure; see PROOF.md for all-size proof.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
# Direct replay also avoids reading stale preexisting package bytecode. The
# repository's registered runner supplies its own private cache as well.
_cache = tempfile.TemporaryDirectory(prefix='native-tensor-closure-pycache-')
sys.pycache_prefix = _cache.name
sys.dont_write_bytecode = True

from gauss_trace import require
from native_check import check_native
from source_algebra import free_laurent, local_gauge, ownership_and_invoice
from caller_check import check_caller
from controls import run as negative_controls


BASE = '7c49fe32c55de02c2c873655c804b16e4c3fef0a'
PINS = {
    'research/p104-helper470-twin-rung-removal/WORD.json.gz': '7834725d9e34ee846a9ccc615221ea81e0201613938afa185d2eda0c9a6c232f',
    'research/p104-helper470-twin-rung-removal/RESULT.json': '84fcbe2a0b64307b5703c363408042bdd91555b0419509aa50daa43b3b1924ad',
    'research/p104-productive-controller/CONTROLLER.json': 'a84f6bbd547379597464e56c420cc665f96bc43a9a1351eed4b7cd0fce3cc4b9',
    'research/p104-caller-independent-audit/capsule/outputs/p104-caller-route-audit-v2-20261025/sources/DATA-PHASES.json': 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa',
    'research/p104-native-channel/vendor/clifford_exact.py': '2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962',
    'research/p104-productive-controller/local.py': '878734dfd64c4b9d362d0ae476cc5c2a19fe93e48b7378763b23f3e0dd0a5a71',
    'research/p104-productive-controller/caller.py': '300d40043953e4f6aecfde8f2d1004b8ad6dc5a79ec3c7666c9908c2466c91c8',
}


def authenticate(path, data):
    require(path in PINS and hashlib.sha256(data).hexdigest() == PINS[path], 'source byte pin: '+path)
    return data


def run():
    raw = {path: authenticate(path, (ROOT/path).read_bytes()) for path in PINS}
    word = json.loads(gzip.decompress(raw['research/p104-helper470-twin-rung-removal/WORD.json.gz']))
    source_result = json.loads(raw['research/p104-helper470-twin-rung-removal/RESULT.json'])
    controller = json.loads(raw['research/p104-productive-controller/CONTROLLER.json'])
    phase_source = json.loads(raw['research/p104-caller-independent-audit/capsule/outputs/p104-caller-route-audit-v2-20261025/sources/DATA-PHASES.json'])
    candidates = json.loads(gzip.decompress((HERE/'NATIVE.json.gz').read_bytes()))
    local = local_gauge(word, source_result)
    native = check_native(word, source_result, candidates)
    laurent = free_laurent(controller)
    caller = check_caller(word, controller, phase_source, source_result)
    invoice = ownership_and_invoice(word, controller, source_result)
    controls = negative_controls(word, source_result, candidates, controller, phase_source)
    for path in ('research/p104-helper470-twin-rung-removal/WORD.json.gz', 'research/p104-productive-controller/caller.py'):
        try:
            authenticate(path, raw[path]+b' ')
        except ValueError:
            controls['source_drift:'+path] = 'Rejected before parsing or execution'
        else:
            raise ValueError('source mutation accepted: '+path)
    return {
        'schema': 'selected-native-tensor-closure-result/1',
        'status': 'PASS_SELECTED_NATIVE_TENSOR_CLOSURE',
        'base_commit': BASE,
        'source_sha256': PINS,
        'local_gauge': local,
        'native_trace': native,
        'complete_caller': laurent,
        'whole_job_algebra': caller,
        'ownership_and_invoice': invoice,
        'negative_controls': dict(sorted(controls.items())),
        'all_size_status': 'PROOF.md proves the typed algebraic implication for every positive f and arbitrary spectator factors; finite replay is the exact selected-source premise',
        'limitations': ['ideal owned reset semantics remain assumed', 'physical selected-rate dispatcher not implemented',
                        'compiler, precision_tape and analytic_recovery not discharged', 'No new kappa'],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='write the deterministic new-package result receipt')
    args = parser.parse_args()
    result = run()
    path = HERE/'RESULT.json'
    encoded = (json.dumps(result, sort_keys=True, indent=2)+'\n').encode()
    if args.write:
        path.write_bytes(encoded)
    else:
        require(path.read_bytes() == encoded, 'complete deterministic result receipt')
    print(result['status'], json.dumps({
        'native_pairs': result['native_trace']['distinct_native_pairs'],
        'raw_contacts': result['whole_job_algebra']['complete_raw_contacts'],
        'productive_fields': result['ownership_and_invoice']['productive_inputs'],
        'paid_calls': result['ownership_and_invoice']['paid_calls'],
        'rejecting_controls': len(result['negative_controls']), 'kappa_changed': False,
    }, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    finally:
        _cache.cleanup()

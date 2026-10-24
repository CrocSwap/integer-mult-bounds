#!/usr/bin/env python3
"""Replay scoped border identities and costs; no native admission.

Dillon with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def module(name):
    spec = importlib.util.spec_from_file_location('border_' + name, HERE / (name + '.py'))
    out = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(out)
    return out


def replay():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    hashes = {}
    for row in pins['files']:
        if row['usage'] != 'input':
            continue
        digest = hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
        need(digest == row['sha256'], 'Authenticated scientific input: ' + row['path'])
        hashes[row['path']] = digest
    algebra = module('border_algebra').run()
    # Discovery roots are deliberately excluded from the exact receipt.
    sweep = algebra.pop('sweep')
    p16 = next(row for row in sweep if row['pairs'] == 16)
    algebra.pop('root_evidence')
    algebra['p16_profiles'] = {
        name: {key: p16[name][key] for key in ('targets', 'paid')}
        for name in ('complex', 'bit')
    }
    algebra['discovery_not_certified'] = 'Floating root estimates are omitted from this exact receipt.'
    result = {
        'status': 'PASS_SCOPED_CONTROLLER_BORDER_INTERFACE',
        'claim': 'Formal border construction and scoped cost obstructions; no admitted supplier or kappa.',
        'source_sha256': hashes,
        'algebra': algebra,
        'budget': module('budget').run(),
        'independent': module('independent_check').run(),
    }
    return json.loads(json.dumps(result, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true', help='Authoring only: replace the exact receipt')
    args = parser.parse_args()
    result = replay()
    receipt = HERE / 'RESULT.json'
    if args.write:
        receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        need(result == json.loads(receipt.read_text()), 'Exact receipt matches replay')
    print(json.dumps({
        'status': result['status'],
        'exact_laurent_pair_counts': [x['pairs'] for x in result['algebra']['cases']],
        'independent_rational_instances': result['independent']['exact_instances'],
        'wrong_weight_rejections': result['independent']['wrong_weight_controls_rejected'],
        'budget_scope': 'all positive p; fixed inventories and declared determinant/output contract',
        'new_kappa': None,
    }, sort_keys=True))


if __name__ == '__main__':
    main()

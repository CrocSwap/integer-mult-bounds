#!/usr/bin/env python3
"""Read-only exact replay, with an explicit receipt authoring option."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run():
    sources = json.loads((HERE / 'SOURCES.json').read_bytes())
    inputs = [row for row in sources['files'] if row['usage'] == 'input']
    need(len(inputs) == 1, 'one pinned scientific source')
    for row in inputs:
        data = (REPO / row['path']).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row['sha256'], 'live source byte hash')
    local, whole, main = load('check'), load('check_whole'), load('check_main')
    payload = local.read_source()
    result = {'status': 'PASS_PRODUCTIVE_HELPER_INVERSE_SUPPORT',
              'local': local.verify(payload), 'whole_encoder': whole.verify(payload),
              'main_support': main.verify(payload),
              'controls': {'local': local.controls(payload), 'whole_encoder': whole.controls(payload),
                           'main_support': main.controls(payload)}}
    need(sum(r['count'] for r in result['controls'].values()) == 16, 'all sixteen controls ran')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='explicitly replace RESULT.json with this fresh replay')
    args = parser.parse_args()
    result = run()
    path = HERE / 'RESULT.json'
    if args.write:
        path.write_bytes((json.dumps(result, indent=2, sort_keys=True) + '\n').encode())
    else:
        need(result == json.loads(path.read_bytes()), 'fresh proof result matches committed receipt')
    print(json.dumps({'status': result['status'], 'cold_roles_local': len(result['local']['cold_roles']),
                      'cold_roles_whole_encoder': result['whole_encoder']['cold_role_count'],
                      'corruption_controls': 16, 'new_bound': False}, sort_keys=True))

#!/usr/bin/env python3
"""Read-only source-bound replay; --write explicitly authors RESULT.json."""
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


def run():
    manifest = json.loads((HERE / 'SOURCES.json').read_bytes())
    inputs = [row for row in manifest['files'] if row['usage'] == 'input']
    need(len(inputs) == 1, 'one source input')
    row = inputs[0]
    source = REPO / row['path']
    need(hashlib.sha256(source.read_bytes()).hexdigest() == row['sha256'], 'live source byte hash')
    spec = importlib.util.spec_from_file_location('productive_color_check', HERE / 'check.py')
    check = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(check)
    return check.run(source, controls=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = run()
    path = HERE / 'RESULT.json'
    if args.write:
        path.write_bytes((json.dumps(result, indent=2, sort_keys=True) + '\n').encode())
    else:
        need(result == json.loads(path.read_bytes()), 'fresh result matches committed receipt')
    print(json.dumps({'status': result['status'], 'new_bound': False}, sort_keys=True))

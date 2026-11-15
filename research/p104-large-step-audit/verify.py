#!/usr/bin/env python3
"""Authenticate self-contained source exports, with a corrupt-byte control."""
from pathlib import Path
import hashlib
import json
HERE = Path(__file__).resolve().parent

def check(raw, digest):
    if hashlib.sha256(raw).hexdigest() != digest:
        raise ValueError('immutable source SHA256')

def main():
    count = 0
    for row in json.loads((HERE / 'SOURCE-VERSIONS.json').read_text())['files']:
        check((HERE / row['path']).read_bytes(), row['sha256'])
        count += 1
    bit = json.loads((HERE / 'bit/SOURCES.json').read_text())
    for row in [bit['scientific_input']] + bit['retained_notices']:
        check((HERE / 'bit' / row['local']).read_bytes(), row['sha256'])
        count += 1
    row = bit['scientific_input']
    raw = (HERE / 'bit' / row['local']).read_bytes()
    try:
        check(bytes([raw[0] ^ 1]) + raw[1:], row['sha256'])
    except ValueError:
        pass
    else:
        raise ValueError('source corruption was accepted')
    print(f'PASS_SELF_CONTAINED_SOURCE_CUSTODY: {count} immutable exports; corrupt-byte rejected')

if __name__ == '__main__':
    main()

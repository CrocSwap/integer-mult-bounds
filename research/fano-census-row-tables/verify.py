#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check every actual triple key, then run the complete original Fano check."""
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_adapter():
    spec = importlib.util.spec_from_file_location('adapter', HERE / 'adapter.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compare_products(ref, kernel, matrices):
    indexed, actions, domain = kernel.prepare(matrices)
    checked = 0
    for a in range(len(matrices)):
        for b in range(len(matrices)):
            if a == b:
                continue
            ab = ref.mul(matrices[a], matrices[b])
            for c in range(len(matrices)):
                if c != b:
                    actual = kernel.product_key(indexed[a, b], actions[c])
                    expected = ref.pack(ref.mul(ab, matrices[c]))
                    if actual != expected:
                        raise ValueError(f'exact product differs at {(a, b, c)}')
                    checked += 1
    return checked, len(domain)


def main():
    adapter = load_adapter()
    ref = adapter.reference()
    matrices = [ref.to_rows(r) for r in ref.load_routes()]
    checked, rows = compare_products(ref, adapter.load_kernel(), matrices)
    if (checked, rows) != (1379952, 18388):
        raise ValueError('actual domain changed')
    print('PASS_ALL_EXACT_TRIPLE_KEYS', checked, 'rows', rows, flush=True)
    result = adapter.run('tables')
    print('PASS_FANO_ROW_TABLES', hashlib.sha256(result).hexdigest())


if __name__ == '__main__':
    main()

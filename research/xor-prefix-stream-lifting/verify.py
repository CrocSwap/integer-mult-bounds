#!/usr/bin/env python3
"""External finite premises for the separate generic Lean lifting theorem.

No producer/checker imports, Git calls, or tracked writes on normal execution.
Prepared by ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from copy import deepcopy
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BASE = '0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2'
OLD = 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
NEW = 'research/r439-bsection-stars-seed01/candidate.json.gz'
PINS = {
    OLD: 'e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f',
    NEW: 'b452d2c2b0b2a546d1105b1da9769aa78e5c54d6f00e97b30c77e3f54ce445ee',
    'research/r439-semantic-d-contract-seed10/PROOF.md':
        'dfbca8c61a92fdf0db8af450dc4466849da37fc296e28b67f357e196e87327db',
}
LEAN_SHA256 = 'e1186a7b11753378ce01d22e68c83abde87ba358fc5ef7449bcd6c0ff2905737'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def strict_json(data):
    def pairs(rows):
        out = {}
        for key, value in rows:
            require(key not in out, 'duplicate JSON key')
            out[key] = value
        return out
    def constant(value):
        raise ValueError('nonfinite JSON value: ' + value)
    return json.loads(data, object_pairs_hook=pairs, parse_constant=constant)


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def lean_source(package=PACKAGE):
    raw = (package / 'Lifting.lean').read_bytes()
    require(digest(raw) == LEAN_SHA256, 'Lean source bytes changed')
    return raw.decode('utf-8')


def words(root=ROOT):
    raw = {}
    for name, expected in PINS.items():
        raw[name] = (root / name).read_bytes()
        require(digest(raw[name]) == expected, 'source bytes changed: ' + name)
    # Authenticate compressed bytes before either decompression or parsing.
    return [strict_json(gzip.decompress(raw[name])) for name in (OLD, NEW)]


def gates(word):
    require(type(word['v']) is int and word['v'] == 111 and
            type(word['R']) is int and word['R'] == 439, 'wrong role counts')
    n = 2 * word['v'] + word['R']
    require(word['frames'][0] == [], 'frame zero is not the empty frame')
    require(type(word['start']) is list and len(word['start']) == n and
            all(type(x) is int and x == 0 for x in word['start'][111:]),
            'target/helper entry is not the common zero frame')
    require(type(word['D']) is list, 'D must be a literal list')
    flat = []
    for gate in word['D']:
        require(type(gate) is list and len(gate) == 3, 'D gate is not a compressed ADD')
        frame, dst, sources = gate
        require(type(frame) is int and frame == 0, 'D ADD is not at zero frame')
        require(type(dst) is int and 111 <= dst < n, 'D destination is not target/helper')
        require(type(sources) is list and sources, 'D source list must be explicit and nonempty')
        for src in sources:
            require(type(src) is int and 111 <= src < n and src != dst,
                    'D ADD source is not a distinct target/helper')
            flat.append((dst, src))
    return n, flat


def row_engine(n, flat):
    rows = [1 << i for i in range(n)]
    for dst, src in flat:
        rows[dst] ^= rows[src]
    return rows


def column_engine(word, n):
    # Literal Boolean execution reads the compressed source directly rather
    # than the row engine's flattened gate list or masks.
    columns = []
    for column in range(n):
        values = [i == column for i in range(n)]
        for _, dst, sources in word['D']:
            for src in sources:
                values[dst] = values[dst] != values[src]
        columns.append(bytes(values))
    return columns


def reject(call, message):
    try:
        call()
    except ValueError:
        return
    raise ValueError('negative control accepted: ' + message)


def calculate(root=ROOT, package=PACKAGE):
    lean_source(package)
    old, new = words(root)
    n, before = gates(old)
    n2, after = gates(new)
    require(n == n2 == 661 and len(before) == 18085 and len(after) == 5548,
            'literal gate inventory changed')
    a, b = row_engine(n, before), row_engine(n, after)
    require(a == b, 'D prefixes differ on a dirty input')
    ca, cb = column_engine(old, n), column_engine(new, n)
    require(ca == cb, 'literal Boolean basis columns differ')
    require(all(ca[j][i] == ((a[i] >> j) & 1) for i in range(n) for j in range(n)),
            'row/column engines disagree')
    require(row_engine(n, after[1:]) != a, 'omitted first ADD was not detected')
    require(row_engine(n, after[:-1]) != a, 'omitted final ADD was not detected')
    wrong_frame = deepcopy(new)
    wrong_frame['D'][0][0] = 1
    reject(lambda: gates(wrong_frame), 'nonzero D frame')
    identity = row_engine(n, [])
    dirty = row_engine(n, [(111, 222)])
    source_mask = (1 << 111) - 1
    require(identity != dirty and all((x & source_mask) == (y & source_mask)
                                      for x, y in zip(identity, dirty)),
            'source-only check must miss dirty helper contamination')
    zero = [False] * n
    zero[111] = zero[111] != zero[222]
    require(not any(zero), 'zero-only witness changed')
    return {
        'schema_version': 1, 'status': 'PASS_XOR_PREFIX_FINITE_BINDING', 'base_commit': BASE,
        'source_sha256': PINS, 'lean_source_sha256': LEAN_SHA256,
        'sources': 111, 'targets': 111, 'dirty_helpers': 439, 'wires': n,
        'old_adds': len(before), 'new_adds': len(after), 'basis_columns': n,
        'matrix_coefficients': n * n, 'row_column_agree': True, 'prefix_equal': True,
        'matrix_sha256_little_endian_rows': digest(b''.join(row.to_bytes((n + 7) // 8, 'little') for row in a)),
        'controls': ['omit_first_add', 'omit_last_add', 'reject_nonzero_frame',
                     'source_only_and_zero_only_miss_dirty_helper'],
        'scope': 'External finite premise check; no Lean compilation, source-to-Lean translation proof, physical realization or new kappa.'}


def check_receipt(result, path):
    require(canonical(result) == canonical(strict_json(path.read_bytes())),
            'finite receipt differs in value or type')


def export_controls():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        package = root / 'research/xor-prefix-stream-lifting'
        package.mkdir(parents=True)
        for name in PINS:
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        for name in ('verify.py', 'Lifting.lean', 'RESULT.json'):
            shutil.copyfile(PACKAGE / name, package / name)
        argv = [sys.executable, '-B', str(package / 'verify.py'), '--no-export-controls']
        env = {**os.environ, 'PATH': ''}
        result = subprocess.run(argv, cwd=root, env=env, capture_output=True, timeout=60)
        require(result.returncode == 0, 'Git-free export failed: ' + result.stderr.decode('utf-8', 'replace'))
        source = root / OLD
        original = source.read_bytes()
        source.write_bytes(original + b'changed')
        result = subprocess.run(argv, cwd=root, env=env, capture_output=True, timeout=60)
        require(result.returncode != 0 and b'source bytes changed' in result.stderr,
                'export source corruption accepted')
        source.write_bytes(original)
        proof = package / 'Lifting.lean'
        original_proof = proof.read_bytes()
        proof.write_bytes(original_proof + b'\n-- changed\n')
        result = subprocess.run(argv, cwd=root, env=env, capture_output=True, timeout=60)
        require(result.returncode != 0 and b'Lean source bytes changed' in result.stderr,
                'export Lean source corruption accepted')
        proof.write_bytes(original_proof)
        receipt = package / 'RESULT.json'
        data = strict_json(receipt.read_bytes())
        data['prefix_equal'] = 1  # Python == alone conflates this with True.
        receipt.write_bytes(canonical(data))
        result = subprocess.run(argv, cwd=root, env=env, capture_output=True, timeout=60)
        require(result.returncode != 0 and b'finite receipt differs' in result.stderr,
                'export typed-receipt corruption accepted')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit-result', type=Path, help='explicitly write a new receipt; refuse overwrite')
    parser.add_argument('--no-export-controls', action='store_true', help='internal export child mode')
    args = parser.parse_args()
    result = calculate()
    if args.emit_result:
        with args.emit_result.open('x', encoding='utf-8', newline='\n') as out:
            out.write(json.dumps(result, indent=2) + '\n')
    else:
        check_receipt(result, PACKAGE / 'RESULT.json')
        if not args.no_export_controls:
            export_controls()
    print(result['status'], '661 columns; 436921 coefficients; Lean compilation is a separate check')


if __name__ == '__main__':
    main()

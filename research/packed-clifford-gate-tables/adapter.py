#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Source-bound opt-in integration; no frozen source file is edited.

ywz65, with substantial OpenAI Codex assistance. Table recurrences are Charles
Bethin's retained PR662 code, not a new algorithm. See README for the boundary.
"""
import ast
from contextlib import contextmanager, redirect_stdout
from functools import lru_cache
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import time
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIOR = 'research/frontier1094-recipes-exact-seed76/'
TABLES = 'research/clifford-state-performance/fast_state.py'
EDITS = (
    ('table = [apply_rows(g[1], x) for x in range(DIM)]',
     'table = _permutation_table(N_AXES, tuple(g[1]))'),
    ("elif kind in ('D', 'PH'):\n            r2, i2 = [0] * DIM, [0] * DIM",
     "elif kind in ('D', 'PH'):\n            phases = _phase_table(N_AXES, tuple(g[1]), tuple(g[2])) if kind == 'D' else None\n            r2, i2 = [0] * DIM, [0] * DIM"),
    ("k = _z4_phase(g[1], g[2], x) if kind == 'D' else g[1]",
     "k = phases[x] if kind == 'D' else g[1]"),
)


class Reject(ValueError):
    pass


def need(ok, message):
    if not ok:
        raise Reject(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def authenticated_inputs(root=ROOT):
    """Capture every declared runtime input before compiling any source."""
    manifest = json.loads((HERE / 'SOURCES.json').read_bytes())
    entries = [e for e in manifest['files'] if e['usage'] == 'input']
    captured = {}
    for entry in entries:
        path = entry['path']
        raw = (root / path).read_bytes()
        need(sha(raw) == entry['sha256'], 'source drift: ' + path)
        captured[path] = raw
    need(len(captured) == 14, 'exact runtime input inventory')
    return captured


def transform(raw):
    source = raw.decode('utf-8')
    for old, new in EDITS:
        need(source.count(old) == 1, 'unique source edit anchor')
        source = source.replace(old, new)
    return source.encode('utf-8')


def table_functions(raw):
    """Compile only the two authenticated function definitions, not zero_state."""
    parsed = ast.parse(raw, filename=TABLES)
    names = ('permutation_table', 'phase_table')
    definitions = [n for n in parsed.body
                   if isinstance(n, ast.FunctionDef) and n.name in names]
    need(tuple(n.name for n in definitions) == names, 'credited table definitions')
    scope = {'lru_cache': lru_cache, '__name__': 'credited_gate_tables'}
    exec(compile(ast.Module(body=definitions, type_ignores=[]), TABLES, 'exec'), scope)
    return scope['permutation_table'], scope['phase_table']


def gate_domain(n, rows, linear=None):
    need(type(n) is int and n == 9 and len(rows) == 9 and
         all(type(v) is int and 0 <= v < 512 for v in rows),
         'nine-axis integer gate domain')
    if linear is not None:
        need(len(linear) == 9 and all(type(v) is int and 0 <= v < 4 for v in linear),
             'nine-axis Z4 linear domain')


@contextmanager
def session(mode='candidate', audit=False, root=ROOT):
    need(mode in ('baseline', 'candidate'), 'mode')
    captured = authenticated_inputs(root)
    old_module = sys.modules.get('clifford')
    old_path, old_argv = list(sys.path), list(sys.argv)
    with tempfile.TemporaryDirectory(prefix='packed-clifford-') as temporary:
        snapshot = Path(temporary)
        for path, raw in captured.items():
            target = snapshot / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)  # compile/read the bytes that passed the gate
        original = captured[PRIOR + 'clifford.py']
        executed = original if mode == 'baseline' else transform(original)
        kernel = types.ModuleType('clifford')
        kernel.__file__ = str(snapshot / PRIOR / 'clifford.py')
        p_table, d_table = table_functions(captured[TABLES])
        seen_p, seen_d = set(), set()
        calls = {'P': 0, 'D': 0}

        def permutation(n, rows):
            gate_domain(n, rows)
            calls['P'] += 1
            result = p_table(n, rows)
            if audit and rows not in seen_p:
                # The original scalar expression is unchanged in the kernel.
                need(result == tuple(kernel.apply_rows(rows, x) for x in range(512)),
                     'independent scalar permutation comparison')
                seen_p.add(rows)
            return result

        def phase(n, rows, linear):
            gate_domain(n, rows, linear)
            calls['D'] += 1
            result = d_table(n, rows, linear)
            key = (rows, linear)
            if audit and key not in seen_d:
                need(result == tuple(kernel._z4_phase(rows, linear, x) for x in range(512)),
                     'independent scalar phase comparison')
                seen_d.add(key)
            return result

        kernel._permutation_table = permutation
        kernel._phase_table = phase
        exec(compile(executed, kernel.__file__, 'exec'), kernel.__dict__)
        sys.modules['clifford'] = kernel
        verifier = types.ModuleType('authenticated_packed_verifier')
        verifier.__file__ = str(snapshot / PRIOR / 'verify.py')
        try:
            exec(compile(captured[PRIOR + 'verify.py'], verifier.__file__, 'exec'),
                 verifier.__dict__)
            yield dict(kernel=kernel, verifier=verifier, p_table=p_table, d_table=d_table,
                       captured=captured, snapshot=snapshot, executed=executed,
                       seen_p=seen_p, seen_d=seen_d, calls=calls)
        finally:
            if old_module is None:
                sys.modules.pop('clifford', None)
            else:
                sys.modules['clifford'] = old_module
            sys.path[:], sys.argv[:] = old_path, old_argv


def full_replay(mode='candidate', audit=False, root=ROOT):
    start, cpu = time.perf_counter(), time.process_time()
    with session(mode, audit, root) as loaded:
        V = loaded['verifier']
        receipt_path = loaded['snapshot'] / 'receipts.jsonl'
        sys.argv = [V.__file__, '--receipts', str(receipt_path)]
        output = io.StringIO()
        check_start, check_cpu = time.perf_counter(), time.process_time()
        with redirect_stdout(output):
            V.main()  # unchanged full main; no --write or --subset is exposed
        elapsed, cpu_elapsed = time.perf_counter()-check_start, time.process_time()-check_cpu
        receipt = receipt_path.read_bytes()
        expected = json.loads(loaded['captured'][PRIOR + 'RESULT.json'])
        need(sha(receipt) == expected['evaluation']['receipts_sha256'], 'exact legacy receipts')
        for path, raw in loaded['captured'].items():
            need((loaded['snapshot'] / path).read_bytes() == raw, 'snapshot input unchanged')
        result = dict(
            mode=mode, audit=audit, checker_stdout=output.getvalue(),
            source_sha256={p: sha(b) for p, b in sorted(loaded['captured'].items())},
            executed_kernel_sha256=sha(loaded['executed']),
            adapter_sha256=sha(Path(__file__).read_bytes()),
            legacy_result_sha256=sha(loaded['captured'][PRIOR + 'RESULT.json']),
            legacy_receipts_sha256=sha(receipt),
            legacy_receipt_header='Names the original source kernel; use this companion executed_kernel_sha256 for the transformed execution.',
            checker_wall_seconds=elapsed, checker_cpu_seconds=cpu_elapsed,
            unique_tables_audited={'P':len(loaded['seen_p']), 'D':len(loaded['seen_d'])},
            table_calls=loaded['calls'],
            caches={'P':loaded['p_table'].cache_info()._asdict(),
                    'D':loaded['d_table'].cache_info()._asdict()},
        )
    result.update(total_wall_seconds=time.perf_counter()-start,
                  total_cpu_seconds=time.process_time()-cpu)
    return result, receipt


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--mode', choices=['baseline', 'candidate'], default='candidate')
    ap.add_argument('--audit-tables', action='store_true')
    ap.add_argument('--out', type=Path)
    ap.add_argument('--receipts', type=Path)
    args = ap.parse_args()
    for target in (args.out, args.receipts):
        need(target is None or not target.exists(), 'output already exists')
    result, receipt = full_replay(args.mode, args.audit_tables)
    if args.receipts is not None:
        with args.receipts.open('xb') as handle:
            handle.write(receipt)
    if args.out is not None:
        with args.out.open('x', encoding='utf-8') as handle:
            json.dump(result, handle, indent=2)
            handle.write('\n')
    print(result['checker_stdout'], end='')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()

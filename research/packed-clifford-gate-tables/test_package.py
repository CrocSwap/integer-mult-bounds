#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Failure-mode controls for the bounded opt-in adapter."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
A = types.ModuleType('tested_adapter')
A.__file__ = str(HERE / 'adapter.py')
exec(compile((HERE / 'adapter.py').read_bytes(), A.__file__, 'exec'), A.__dict__)


class AdapterTests(unittest.TestCase):
    def test_all_input_mutations_refused_before_compilation(self):
        captured = A.authenticated_inputs()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for path, raw in captured.items():
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
            for path, raw in captured.items():
                with self.subTest(path=path):
                    (root / path).write_bytes(raw + b'\n')
                    with patch.object(A, 'table_functions') as compiler:
                        with self.assertRaisesRegex(A.Reject, 'source drift'):
                            with A.session(root=root):
                                self.fail('drifted input admitted')
                        compiler.assert_not_called()
                    (root / path).write_bytes(raw)

    def test_only_two_credited_functions_compiled(self):
        raw = A.authenticated_inputs()[A.TABLES]
        p, d = A.table_functions(raw)
        self.assertEqual(set(p.__wrapped__.__globals__),
                         {'lru_cache', '__name__', '__builtins__', 'permutation_table', 'phase_table'})
        self.assertEqual(p.cache_info().maxsize, 64)
        self.assertEqual(d.cache_info().maxsize, 64)

    def test_in_place_gate_changes_and_state_freshness(self):
        rows, quad, linear = [1 << i for i in range(9)], [0]*9, [0]*9
        gates = [('P', rows), ('D', quad, linear), ('C', 3, 1)]
        with A.session() as candidate, A.session('baseline') as original:
            C, B = candidate['kernel'], original['kernel']
            prior = C.run(gates, 4)
            self.assertEqual(prior, B.run(gates, 4))
            rows[0] ^= 2
            linear[3] = 3
            quad[0] = 4
            changed = C.run(gates, 4)
            self.assertNotEqual(prior, changed)
            self.assertEqual(changed, B.run(gates, 4))
            changed[0][0] = 999  # output never enters the cache
            self.assertEqual(C.run(gates, 4), B.run(gates, 4))
            self.assertIsInstance(candidate['p_table'](9, tuple(rows)), tuple)
            self.assertIsInstance(candidate['d_table'](9, tuple(quad), tuple(linear)), tuple)

    def test_eviction_recomputation_and_cache_keys(self):
        with A.session() as loaded:
            C, p, d = loaded['kernel'], loaded['p_table'], loaded['d_table']
            identity, zero = tuple(1 << i for i in range(9)), (0,)*9
            first_p, first_d = p(9, identity), d(9, zero, zero)
            for mask in range(1, 90):
                rows = (1 ^ (mask << 1),) + identity[1:]
                linear = tuple((mask >> (2*i)) & 3 for i in range(9))
                self.assertEqual(p(9, rows), tuple(C.apply_rows(rows, x) for x in range(512)))
                self.assertEqual(d(9, zero, linear), tuple(C._z4_phase(zero, linear, x) for x in range(512)))
            self.assertEqual(p.cache_info().currsize, 64)
            self.assertEqual(d.cache_info().currsize, 64)
            before_p, before_d = p.cache_info().misses, d.cache_info().misses
            self.assertEqual(p(9, identity), first_p)
            self.assertEqual(d(9, zero, zero), first_d)
            self.assertEqual(p.cache_info().misses, before_p+1)
            self.assertEqual(d.cache_info().misses, before_d+1)

    def test_permutation_fault_fails_original_calibration(self):
        with A.session() as loaded:
            C, V = loaded['kernel'], loaded['verifier']
            data, _ = V.load()
            good = C._permutation_table
            C._permutation_table = lambda n, rows: tuple(x ^ 1 for x in good(n, rows))
            with self.assertRaises(V.Reject):
                V.calibrate(data['word']['frames'])

    def test_phase_fault_fails_original_calibration(self):
        with A.session() as loaded:
            C, V = loaded['kernel'], loaded['verifier']
            data, _ = V.load()
            good = C._phase_table
            C._phase_table = lambda n, rows, linear: tuple((x+1) % 4 for x in good(n, rows, linear))
            with self.assertRaises(V.Reject):
                V.calibrate(data['word']['frames'])

    def test_existing_rejections_and_declared_domain(self):
        with A.session() as loaded:
            C = loaded['kernel']
            for gate in [('P', [0]*9), ('C', 0, 1), ('C', 1, 0), ('unknown',)]:
                with self.subTest(gate=gate), self.assertRaises(ValueError):
                    C.run([gate], 4)
            for gate in [('P', [True]*9), ('D', [0]*9, [0]*8), ('D', [-1]*9, [0]*9)]:
                with self.subTest(gate=gate), self.assertRaises(A.Reject):
                    C.run([gate], 4)

    def test_exact_snapshot_and_source_transform(self):
        with A.session() as loaded:
            raw = loaded['captured'][A.PRIOR+'clifford.py']
            restored = loaded['executed'].decode()
            for old, new in reversed(A.EDITS):
                self.assertEqual(restored.count(new), 1)
                restored = restored.replace(new, old)
            self.assertEqual(restored.encode(), raw)
            self.assertEqual((loaded['snapshot']/A.PRIOR/'clifford.py').read_bytes(), raw)
            self.assertNotEqual(hashlib.sha256(raw).hexdigest(), hashlib.sha256(loaded['executed']).hexdigest())
            with self.assertRaises(A.Reject):
                A.transform(raw+b'\n'+A.EDITS[0][0].encode())


if __name__ == '__main__':
    unittest.main()

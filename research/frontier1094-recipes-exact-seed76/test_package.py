# SPDX-License-Identifier: Apache-2.0
"""Controls for the independent RecipesExact check (about 20 s).

Run: python3 -I -B -m unittest discover -s research/frontier1094-recipes-exact-seed76 -p test_package.py -v
"""
import ast
import io
import json
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import clifford as C  # noqa: E402
import verify as V  # noqa: E402

DATA, BINDING = V.load()
CHILDREN, ADAPTERS, _ = V.inventory(DATA)
WORD = DATA['word']
FRAMES = WORD['frames']
BY_KEY = {(c['old'], c['new']): c for c in CHILDREN}
RESULT = json.loads((HERE / 'RESULT.json').read_text())


class Independence(unittest.TestCase):
    def test_kernel_and_verifier_import_only_the_standard_library(self):
        allowed = {'argparse', 'gzip', 'hashlib', 'io', 'json', 're', 'sys', 'tarfile', 'time', 'collections',
                   'pathlib', 'clifford'}
        for name in ('verify.py', 'clifford.py'):
            tree = ast.parse((HERE / name).read_text())
            mods = {a.name.split('.')[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
            mods |= {n.module.split('.')[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
            self.assertLessEqual(mods, allowed, name)
            names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
            self.assertFalse(names & set(V.FORBIDDEN), name)


class Comparator(unittest.TestCase):
    def test_k1_a_projective_comparator_would_accept_a_global_phase_error(self):
        c = BY_KEY[(0, 174)]
        bad = V._mutate(c, ('left', 'phase'), lambda p: (p + 1) % 4)
        c1, c2 = V.child_circuits(bad, FRAMES)
        self.assertFalse(C.same_operator(c1, c2))                       # the exact comparator rejects it
        k1, k2 = C.c_gates(c1), C.c_gates(c2)
        beta = C.radix(max(k1, k2))
        s1, s2 = C.run(c1, beta), C.run(c2, beta)
        rotated = C.run(c2 + [('PH', 1)], beta)                          # side2 times i
        self.assertTrue(C.equal(s1, k1, rotated, k2, beta))             # equal up to the unit i: projectively equal

    def test_k2_a_column0_comparator_would_accept_an_input_character_error(self):
        c = BY_KEY[(0, 2)]
        bad = V._mutate(c, ('right', 'linear_Z4'), lambda a: a[:5] + [(a[5] + 2) % 4] + a[6:])
        c1, c2 = V.child_circuits(bad, FRAMES)
        self.assertFalse(C.same_operator(c1, c2))
        k = max(C.c_gates(c1), C.c_gates(c2))
        beta = C.radix(k)
        col1 = C.columns(C.run(c1, beta), beta)
        col2 = C.columns(C.run(c2, beta), beta)
        sc1, sc2 = 1 << (k - C.c_gates(c1)), 1 << (k - C.c_gates(c2))
        scale = lambda col, s: {y: (re * s, im * s) for y, (re, im) in col.items()}  # noqa: E731
        self.assertEqual(scale(col1[0], sc1), scale(col2[0], sc2))       # column 0 alone cannot see it
        self.assertNotEqual(scale(col1[32], sc1), scale(col2[32], sc2))  # column e5 does

    def test_k3_radix_guard(self):
        s = C.run([], 4)
        with self.assertRaises(ValueError):
            C.equal(s, 1, s, 1, 3)

    def test_digit_bound_on_the_largest_identities(self):
        # the lemma behind beta = 2K + 2: after k C gates every numerator component is at most 4^k, so the scaled
        # digit difference of the two sides is at most 2 * 4^K < 2^(2K+2); check the bound on the K = 16 centre children
        for key in ((415, 0), (418, 0)):
            c1, c2 = V.child_circuits(BY_KEY[key], FRAMES)
            k = C.c_gates(c1)
            self.assertEqual(k, 16)
            beta = C.radix(k)
            biggest = max(max(abs(re), abs(im)) for col in C.columns(C.run(c1, beta), beta).values() for re, im in col.values())
            self.assertLessEqual(biggest, 4 ** k)

    def test_radix_2k_would_be_unsound(self):
        # at beta = 2K a digit difference of 4^K is allowed by the bound, and (4^K, -1) packs to zero: a collision
        K = 3
        B = 1 << (2 * K)
        self.assertEqual(4 ** K * B ** 0 + (-1) * B ** 1, 0)
        self.assertLessEqual(4 ** K, 2 * 4 ** K)
        # at beta = 2K + 2 the same digits cannot cancel
        B2 = 1 << C.radix(K)
        self.assertNotEqual(4 ** K - B2, 0)
        self.assertLess(2 * 4 ** K, B2)


class Semantics(unittest.TestCase):
    def test_all_semantic_controls_reject(self):
        out = V.semantic_controls(CHILDREN, ADAPTERS, WORD)
        self.assertEqual(out, RESULT['controls'])
        self.assertEqual(len(out), 12)

    def test_rank_off_by_one_is_rejected_structurally_and_by_the_evaluator(self):
        c = dict(BY_KEY[(0, 174)], rank=2)
        bad = {'children': [c if (x['old'], x['new']) == (0, 174) else x for x in CHILDREN],
               'endpoint_adapters': ADAPTERS}
        with self.assertRaisesRegex(V.Reject, 'I3 child rank'):
            V.inventory(dict(DATA, recipes=bad))
        self.assertFalse(C.same_operator(*V.child_circuits(c, FRAMES)))

    def test_swapped_matrix_rows_and_adapter_phase_are_rejected(self):
        c = V._mutate(BY_KEY[(0, 415)], ('left', 'matrix_rows'), lambda G: [G[1], G[0]] + G[2:])
        self.assertFalse(C.same_operator(*V.child_circuits(c, FRAMES)))
        x = V._mutate(ADAPTERS[1], ('left', 'phase'), lambda p: (p + 1) % 4)
        self.assertFalse(C.same_operator(*V.adapter_circuits(x, WORD)))

    def test_every_rank_class_has_a_rejected_phase_mutant(self):
        seen = set()
        for c in CHILDREN:
            if c['rank'] in seen:
                continue
            seen.add(c['rank'])
            bad = V._mutate(c, ('left', 'phase'), lambda p: (p + 1) % 4)
            self.assertTrue(C.same_operator(*V.child_circuits(c, FRAMES)), c['rank'])
            self.assertFalse(C.same_operator(*V.child_circuits(bad, FRAMES)), c['rank'])
        self.assertEqual(seen, {1, 2, 3, 4, 5, 8})


class Binding(unittest.TestCase):
    def test_d1_decoy_recipes_rejected(self):
        with self.assertRaisesRegex(V.Reject, 'B6 provider file digest: recipes'):
            V.load(member_overrides={'recipes': V.CASES['decoys']['recipes']})

    def test_d2_decoy_word_rejected(self):
        with self.assertRaisesRegex(V.Reject, 'B6 provider file digest: canonical_word'):
            V.load(member_overrides={'canonical_word': V.CASES['decoys']['canonical_word']})

    def test_d3_one_phase_digit_changed_in_the_recipe_bytes(self):
        raw = V.canonical_bytes(DATA['recipes'])
        i = raw.index(b'"phase":0')
        flipped = raw[:i] + b'"phase":1' + raw[i + 9:]
        with self.assertRaisesRegex(V.Reject, 'B6 provider file digest: recipes'):
            V.load(byte_overrides={'recipes': flipped})

    def test_d4_duplicate_json_key(self):
        with self.assertRaisesRegex(V.Reject, 'duplicate JSON key'):
            V.strict_loads(b'{"a":1,"a":2}')

    def _archive(self, mutate):
        raw = (V.ROOT / V.CASES['archive']['path']).read_bytes()
        return mutate(raw)

    def test_archive_byte_flip(self):
        with tempfile.TemporaryDirectory() as d:
            raw = self._archive(lambda b: b[:-1] + bytes([b[-1] ^ 1]))
            p = Path(d) / 'a.tar.gz'
            p.write_bytes(raw)
            with self.assertRaisesRegex(V.Reject, 'B1 archive digest'):
                V.load(archive_path=p)

    def test_unsafe_archive_members(self):
        for name in ('../escape', 'dup'):
            buf = io.BytesIO()
            with tarfile.open(fileobj=buf, mode='w') as tar:
                for n in ([name] if name != 'dup' else ['dup', 'dup']):
                    info = tarfile.TarInfo(n)
                    info.size = 0
                    tar.addfile(info, io.BytesIO(b''))
            buf.seek(0)
            with tarfile.open(fileobj=buf, mode='r') as tar:
                with self.assertRaisesRegex(V.Reject, 'B2'):
                    V.safe_members(tar)

    def test_binding_is_recorded(self):
        self.assertEqual(BINDING, RESULT['binding'])
        self.assertTrue(BINDING['global8_twin_byte_identical'])


class Coverage(unittest.TestCase):
    def test_result_covers_every_record_and_column(self):
        ev = RESULT['evaluation']
        self.assertEqual((ev['children'], ev['adapters'], ev['columns']), (2896, 224, 512))
        self.assertTrue(ev['global_phase_included'])
        self.assertEqual(sum(ev['K_histogram'].values()), 2896)

    def test_subset_counts_one_child_and_one_port(self):
        out = V.evaluate(CHILDREN, ADAPTERS, WORD, subset='pair=0:174,ports=5')
        self.assertEqual((out['children'], out['adapters']), (1, 2))

    def test_evaluator_rejects_a_mutated_child_record(self):
        bad = [V._mutate(c, ('right', 'linear_Z4'), lambda a: a[:5] + [(a[5] + 2) % 4] + a[6:])
               if (c['old'], c['new']) == (0, 174) else c for c in CHILDREN]
        with self.assertRaisesRegex(V.Reject, 'E child 0:174'):
            V.evaluate(bad, ADAPTERS, WORD, subset='pair=0:174,adapters=none')

    def test_evaluator_rejects_a_mutated_adapter_record(self):
        bad = [V._mutate(x, ('left', 'phase'), lambda p: (p + 1) % 4) if (x['port'], x['role']) == (3, 'target') else x
               for x in ADAPTERS]
        with self.assertRaisesRegex(V.Reject, 'E adapter 3 target'):
            V.evaluate(CHILDREN, bad, WORD, subset='children=none,ports=3')

    def test_receipts_list_each_selected_pair_once(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'r.jsonl'
            V.evaluate(CHILDREN, ADAPTERS, WORD, subset='dim=1..2,adapters=none', receipts=path)
            lines = [json.loads(x) for x in path.read_text().splitlines()]
        pairs = [tuple(pq) for x in lines if x['kind'] == 'children' for pq in x['pairs']]
        expect = [(c['old'], c['new']) for c in CHILDREN if 1 <= len(FRAMES[c['new']]) <= 2]
        self.assertEqual(sorted(pairs), sorted(expect))
        self.assertEqual(len(pairs), len(set(pairs)))


class Inventory(unittest.TestCase):
    def _programs(self, mutate):
        progs = json.loads(json.dumps(DATA['programs']))
        mutate(progs)
        return dict(DATA, programs=progs)

    def test_i5_a_dropped_climb_event_is_rejected(self):
        def drop(progs):
            i = next(n for n, e in enumerate(progs['forward']) if e[0] == 'climb')
            del progs['forward'][i]
        with self.assertRaisesRegex(V.Reject, 'I5'):
            V.inventory(self._programs(drop))

    def test_i6_a_moved_adapter_frame_is_rejected(self):
        def move(progs):
            i = next(n for n, e in enumerate(progs['forward']) if e[0] == 'adapter' and e[1] == 'old_to_new' and e[2] == 0)
            progs['forward'][i] = progs['forward'][i][:3] + [progs['forward'][i][3] + 1]
        with self.assertRaisesRegex(V.Reject, 'I6'):
            V.inventory(self._programs(move))

    def test_i7_an_asymmetric_q_is_rejected(self):
        recipes = json.loads(json.dumps(DATA['recipes']))
        Q = recipes['children'][0]['left']['quadratic_rows']
        Q[0] ^= 1 << 5                      # Q_05 set without Q_50
        with self.assertRaisesRegex(V.Reject, 'I7'):
            V.inventory(dict(DATA, recipes=recipes))

    def test_calibration_runs_and_a_wrong_fixture_pin_is_rejected(self):
        out = V.calibrate(FRAMES)
        self.assertEqual(out, RESULT['calibration'])
        saved = V.CASES['fixtures']['pr702']['sha256']
        try:
            V.CASES['fixtures']['pr702']['sha256'] = '0' * 64
            with self.assertRaisesRegex(V.Reject, 'FX3 #702 EXPECTED pinned'):
                V.calibrate(FRAMES)
        finally:
            V.CASES['fixtures']['pr702']['sha256'] = saved


if __name__ == '__main__':
    unittest.main()

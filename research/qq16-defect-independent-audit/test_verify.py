"""Behavioral controls and a separate literal constant-array execution.

Arham Tahir with OpenAI Codex assistance. Apache-2.0.
"""
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('independent_audit', Path(__file__).with_name('verify.py'))
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def literal(word, faults, early, stop=None, field=None):
    """Physical execution on constant owner/payload arrays, initially zero.

    Native lines, stages and permutations fix these constant arrays. This
    executes numeric states and never uses the reverse sensitivity engine.
    """
    state = dict.fromkeys(early, Q(0))
    for i, e in enumerate(word):
        op = e['op']
        if op == 'history_boundary':
            state.update({s + str(p): Q(0) for p in range(112) for s in ('X', 'Y')})
        elif op == 'clear':
            state[e['field']] = Q(0)
        elif op == 'add':
            state[e['dst']] += Q(e['coefficient']) * state[e['src']]
        elif op == 'private_end':
            for name in e['fields']:
                audit.require(state.pop(name) == 0, 'literal private retirement')
        elif op not in ('private_begin', 'checkpoint', 'line', 'stage', 'current_map'):
            raise ValueError('unknown literal opcode')
        if op in audit.FAULT_OPS:
            dst = e.get('dst', e.get('field'))
            state[dst] += faults.get(i, Q(0))
        if i == stop:
            return state[field]
    return state


class AuditControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word, cls.packet, cls.expected = audit.authenticate()
        cls.maps = audit.owner_maps(cls.packet)
        cls.early = {'X' + str(p) for p in cls.packet['A_ports'] + cls.packet['T_ports']}

    def test_signed_interior_witness(self):
        _, rows = audit.reverse_row(self.word, 1717, 'F0', self.maps, self.early, save=True)
        collapsed = {site: sum(row.values(), Q(0)) for site, row in rows.items()}
        faults = {i: Q(1 if c > 0 else -1) for i, c in collapsed.items() if c}
        response = sum(map(abs, collapsed.values()), Q(0))
        self.assertEqual(response, 841)
        self.assertEqual(literal(self.word, faults, self.early, 1717, 'F0'), response)
        self.assertGreater(response, max(Q(v['A']) for v in self.expected['final'].values()))

    def test_capture_errors_cross_temporal_boundary(self):
        first = next(i for i, e in enumerate(self.word) if e['op'] == 'add')
        values, rows = audit.reverse_row(self.word, 1717, 'F0', self.maps, self.early, save=True)
        capture_sites = [i for i in rows if i < 32]
        self.assertEqual(len(capture_sites), 12)  # twelve of sixteen affect this particular row
        self.assertGreater(sum(audit.absolute(rows[i]) for i in capture_sites), 0)
        bad = deepcopy(self.word)
        bad[first] = dict(op='clear', field=bad[first]['dst'], frame='old')
        mutated, _ = audit.reverse_row(bad, 1717, 'F0', self.maps, self.early)
        self.assertNotEqual(mutated, values)
        execution = literal(self.word, {first: Q(1)}, self.early)
        self.assertTrue(any(v for name, v in execution.items() if name.startswith('Z')))
        self.assertEqual(execution['Z0'], -execution['W0'])

    def test_owned_clear_does_not_erase_escaped_error(self):
        site = next(i for i, e in enumerate(self.word)
                    if e['op'] == 'add' and e['dst'] == 'C')
        result = literal(self.word, {site: Q(1)}, self.early)
        outputs = {k: v for k, v in result.items() if k[0] in ('Z', 'W') and v}
        self.assertEqual(len(outputs), 56)
        self.assertEqual(outputs['W0'], -3)
        self.assertNotIn('C', result)

    def test_borrowed_inverse_is_not_exact_error_cleanup(self):
        site = next(i for i, e in enumerate(self.word) if e['op'] == 'line')
        name = self.word[site]['field']
        self.assertEqual(literal(self.word, {site: Q(1)}, self.early)[name], 1)

    def test_noncommuting_owner_order(self):
        # Embed two noncommuting invertible 2x2 binary matrices into 73 bits.
        h = (2, 1) + audit.IDENTITY[2:]
        k = (1, 3) + audit.IDENTITY[2:]
        self.assertNotEqual(audit.product(h, k), audit.product(k, h))
        word = [dict(op='current_map', field='X0', port=p) for p in (0, 1, 0)]
        _, rows = audit.reverse_row(word, 2, 'X0', {0: h, 1: k}, {'X0'}, save=True)
        route = next(iter(rows[0]))
        for vector in (1, 2, 3, 1 << 72):
            self.assertEqual(audit.apply_columns(route, vector),
                             audit.apply_columns(h, audit.apply_columns(k, vector)))
        wrong = {audit.product(k, h): Q(1)}
        self.assertNotEqual(rows[0], wrong)

    def test_signed_cancellation_before_absolute_value(self):
        word = [dict(op='clear', field='Z0'),
                dict(op='add', dst='Z0', src='X0', coefficient='1'),
                dict(op='add', dst='Z0', src='X0', coefficient='-1')]
        values, _ = audit.reverse_row(word, 2, 'Z0', {}, {'X0'})
        self.assertEqual(values, dict(P=0, A=2, K=4, native=0, cover=0))
        self.assertEqual(literal(word, {1: Q(1), 2: Q(1)}, {'X0'})['Z0'], 2)

    def test_chronology_and_uninitialized_dirt(self):
        bad = deepcopy(self.word)
        i = next(i for i, e in enumerate(bad) if e['op'] == 'history_boundary')
        bad.insert(0, bad.pop(i))
        with self.assertRaisesRegex(ValueError, 'capture initialized'):
            audit.timeline(bad, self.packet)
        bad = deepcopy(self.word)
        i = next(i for i, e in enumerate(bad) if e['op'] == 'clear' and e['field'] == 'W0')
        bad.pop(i)
        with self.assertRaisesRegex(ValueError, 'initialized ADD'):
            audit.timeline(bad, self.packet)

    def test_20_bit_feedback_and_19_bit_failure(self):
        # Direct substitution in the claimed error inequality, including b=0.
        for b in (0, 1, 32, 1024):
            u = Q(1, 2 ** (b + 20))
            self.assertLessEqual(551520 * u / (1 - 2298 * u), Q(1, 2 ** b))
        u = Q(1, 2 ** 19)
        self.assertGreater(551520 * u / (1 - 2298 * u), 1)
        # Failure is of this sufficient majorant, not a physical impossibility.
        self.assertEqual(audit.feedback_guard(Q(240), Q(2298))['uniform_guard_bits'], 20)

    def test_snapshot_corruption_rejected_before_interpretation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(audit.HERE / 'sources', root / 'sources')
            shutil.copy(audit.HERE / 'SOURCES.json', root / 'SOURCES.json')
            word = root / 'sources/PR2540-WORD.json'
            word.chmod(0o600)  # change only the disposable copy, including from read-only exports
            word.write_bytes(word.read_bytes() + b' ')
            with patch.object(audit, 'HERE', root):
                with self.assertRaisesRegex(ValueError, 'snapshot hash'):
                    audit.authenticate()


if __name__ == '__main__':
    unittest.main()

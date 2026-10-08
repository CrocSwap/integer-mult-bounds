"""Independent small controls and rejection tests for the exact direct producer."""
from pathlib import Path
import json
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts/experiments'))
from ternary_target_certify import build_checkers, exact_run, file_hash
from ternary_target_circuit import DirectProducer, frame_control, hybrid_labels


class ExactDirectProducer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix='test-ternary-target-')
        cls.workdir = Path(cls.temporary.name)
        cls.binaries = build_checkers(cls.workdir)
        cls.small = exact_run(8, cls.workdir, cls.binaries)
        cls.words = list(struct.unpack('<'+'I'*((cls.workdir/'plan-8.bin').stat().st_size//4),
                                       (cls.workdir/'plan-8.bin').read_bytes()))

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_exact_zdd_agrees_with_independent_bitset_circuit_and_frames(self):
        circuit = DirectProducer(8)
        original = circuit.verify_map()
        for key in ('inputs', 'outputs', 'roles'):
            self.assertEqual(self.small['support'][key], original[key])
        self.assertEqual(self.small['support']['retained_additions'], original['additions'])
        self.assertEqual(original['roles'], 546)
        labels, audit = hybrid_labels(circuit)
        self.assertEqual(audit['degenerate_nodes'], [])
        physical = frame_control(circuit, labels)
        self.assertEqual([x['downward_rank'] for x in physical], [168, 168])
        self.assertTrue(self.small['frames']['every_final_frame_nondegenerate'])

    def reject_modified_plan(self, words, expected_message):
        path = self.workdir/'corrupted-plan.bin'
        path.write_bytes(struct.pack('<'+'I'*len(words), *words))
        result = subprocess.run([str(self.binaries['exact']), str(path)],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(expected_message, result.stderr)

    def test_duplicate_source_is_rejected_before_support_merging(self):
        words = self.words[:]
        offset = 4
        for _ in range(words[2]):
            gates, outputs = words[offset+5:offset+7]
            if gates:
                words[offset+8] = words[offset+7]
                break
            offset += 7+2*gates+outputs
        else:
            self.fail('Small plan contains no addition')
        self.reject_modified_plan(words, 'Overlapping source supports')

    def test_missing_local_output_is_rejected_by_independent_family_check(self):
        words = self.words[:]
        first_output = 4+7+2*words[9]
        self.assertNotEqual(words[first_output], 0)
        words[first_output] = 0
        self.reject_modified_plan(words, 'Wrong full side coefficient family')

    def test_published_target_size_audit_has_no_unresolved_final_frames(self):
        data = json.loads((ROOT/'certificates/ternary-target-network.json').read_text())
        self.assertEqual(data['support']['roles'], 10365877)
        self.assertTrue(data['support']['every_output_family_independently_checked'])
        self.assertEqual(data['frames']['unresolved_gram_families'], 60)
        self.assertEqual(data['frames']['delayed_source_nodes'], 64)
        self.assertEqual(data['frames']['unresolved_source_nodes'], 0)
        self.assertEqual(data['frame_proof']['final_unresolved_frames'], 0)
        self.assertEqual(data['global_roles']['center_loss'], 9828)
        for name, expected in data['proof_sha256'].items():
            self.assertEqual(file_hash(ROOT/name), expected, name)


if __name__ == '__main__':
    unittest.main()

# SPDX-License-Identifier: Apache-2.0
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent

def module(name):
    spec = importlib.util.spec_from_file_location(name, HERE/(name+'.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

V, I = module('verify'), module('independent')

class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cert = json.loads((HERE/'CERTIFICATE.json').read_text())
        cls.word = V.load()
        cls.rows, cls.current, _ = V.cut(cls.word)
        cls.fb = [V.basis([cls.word['lines'][i] for i in f]) for f in cls.word['frames']]

    def test_complete_separate_replays(self):
        V.verify(self.cert, self.word)
        I.check(self.cert)

    def test_all_ten_gate_omissions(self):
        total = 0
        for row in self.cert['rank_seven_cases']:
            if row['legal']:
                for j in range(len(row['isolation_gates'])):
                    gates = row['isolation_gates'][:j]+row['isolation_gates'][j+1:]
                    with self.assertRaisesRegex(ValueError, 'restoration|another column'):
                        V.station_check(self.word, self.rows, self.current, self.fb,
                                        row['helper'], row['station'], gates)
                    total += 1
        self.assertEqual(total, 10)

    def test_three_target_caps_and_relaxed_positive_controls(self):
        count = 0
        for row in self.cert['rank_seven_cases']:
            if not row['legal']:
                with self.assertRaisesRegex(ValueError, 'final endpoint cap'):
                    V.station_check(self.word, self.rows, self.current, self.fb,
                                    row['helper'], row['station'], row['isolation_gates'])
                relaxed = copy.deepcopy(self.word)
                for r in row['endpoint_blockers']:
                    relaxed['final'][r] = 1
                V.station_check(relaxed, self.rows, self.current, self.fb,
                                row['helper'], row['station'], row['isolation_gates'])
                count += 1
        self.assertEqual(count, 3)

    def test_certificate_corruptions_both_engines(self):
        mutations = [lambda c:c['join_rank_counts'].update({'8':432}),
                     lambda c:c['legal_helpers'].append(465),
                     lambda c:c['rank_seven_cases'][0]['endpoint_blockers'].clear(),
                     lambda c:c['rank_seven_cases'][3].update({'minimum_adds':2}),
                     lambda c:c['rank_seven_cases'][4]['isolation_gates'].pop(),
                     lambda c:c['rank_seven_cases'][5]['first_fixed_B_conflict'].update({'gate_index':285})]
        for mutation in mutations:
            bad = copy.deepcopy(self.cert)
            mutation(bad)
            with self.assertRaisesRegex(ValueError, 'certificate mismatch'):
                V.verify(bad, self.word)
            with self.assertRaisesRegex(ValueError, 'certificate mismatch'):
                I.check(bad)

    def test_wrong_station_and_original_dirty_endpoint(self):
        row = self.cert['rank_seven_cases'][3]
        with self.assertRaisesRegex(ValueError, 'station arrival'):
            V.station_check(self.word, self.rows, self.current, self.fb, 469, 513, row['isolation_gates'])
        bad = copy.deepcopy(self.word)
        bad['C'] = bad['C'][:-1]
        with self.assertRaisesRegex(ValueError, 'baseline full endpoint'):
            V.derive(bad)

    def test_relocation_source_pin_regeneration_and_overwrite(self):
        with tempfile.TemporaryDirectory(prefix='station exits ') as tmp:
            root = Path(tmp)
            pkg = root/'research/r439-later-retirement-cuts'
            shutil.copytree(HERE, pkg)
            raw = root/V.WORD
            raw.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(V.ROOT/V.WORD, raw)
            for script in ['verify.py','independent.py']:
                run = subprocess.run([sys.executable,'-I','-O','-B',str(pkg/script)],
                                     cwd=root, capture_output=True, text=True)
                self.assertEqual(run.returncode, 0, run.stderr)
            out = root/'regenerated.json'
            command = [sys.executable,'-I','-O','-B',str(pkg/'verify.py'),'--output',str(out)]
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertEqual(json.loads(out.read_text()), self.cert)
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
            raw.write_bytes(raw.read_bytes()+b'corrupt')
            for script in ['verify.py','independent.py']:
                run = subprocess.run([sys.executable,'-I','-O','-B',str(pkg/script)],
                                     capture_output=True,text=True)
                self.assertNotEqual(run.returncode, 0)
                self.assertIn('source hash', run.stderr)

if __name__ == '__main__':
    unittest.main(verbosity=2)

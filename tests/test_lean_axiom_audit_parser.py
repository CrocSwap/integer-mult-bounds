"""Axiom queries must be real source commands and reports must stay fail-closed."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import check_lean_axioms as audit
sys.path.pop(0)

VALID = '''import Init
/- Explanation:
#print axioms ignoredComment
/- nested comment -/
-/
def documentation : String := "line one
#print axioms ignoredString
"
theorem actual (p q : Prop) (h : p ↔ q) : p = q := Classical.choice ⟨propext h⟩
#print /- query separator -/ axioms actual -- trailing explanation
'''
SPOOF = '''import Init
/-
#print axioms notADeclaration
-/
#eval IO.println "'notADeclaration' does not depend on any axioms"
'''


class AxiomParserTests(unittest.TestCase):
    def test_only_actual_source_queries_are_counted(self):
        self.assertEqual(audit.source_queries(VALID), ['actual'])
        with self.assertRaisesRegex(ValueError, 'distinct theorem names'):
            audit.source_queries(SPOOF)
        for text in ('/- unclosed', 'def s := "unclosed', '#print axioms a\n#print axioms a\n'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                audit.source_queries(text)

    def test_multiline_output_and_axiom_free_report(self):
        output = ("'actual' depends on axioms: [propext,\n Classical.choice,\n Quot.sound]\n"
                  "'free' does not depend on any axioms\n")
        self.assertEqual(audit.check_output(output, ['actual', 'free']), 2)
        for altered in (output.replace('Quot.sound', 'sorryAx'), output.replace('Quot.sound', 'custom'),
                        output.replace('propext,', 'propext,,'), output + "'extra' depends on axioms: [",
                        output.replace('actual', 'different'), output + output.splitlines()[3] + '\n'):
            with self.subTest(output=altered), self.assertRaises(ValueError):
                audit.check_output(altered, ['actual', 'free'])

    def test_existing_audit_inventory_remains_identical(self):
        import re
        for relative in ('formal/lean/AuditAll.lean', 'research/gaussian-parity-synthesis/AuditAll.lean',
                         'research/matrix-exponent-synthesis/AuditAll.lean'):
            text = (ROOT / relative).read_text(encoding='utf-8')
            original = re.findall(r'^#print axioms (\S+)\s*$', text, re.M)
            self.assertEqual(audit.source_queries(text), original)

    @unittest.skipUnless(os.environ.get('LEAN_AUDIT_BIN'), 'set LEAN_AUDIT_BIN for live kernel controls')
    def test_live_lean_source_and_output_controls(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project / 'lakefile.lean').write_text('import Lake\nopen Lake DSL\npackage auditFixture\n')
            env = {**os.environ, 'PATH': os.environ['LEAN_AUDIT_BIN'] + os.pathsep + os.environ['PATH']}
            def check(name, source):
                path = project / (name + '.lean')
                path.write_text(source, encoding='utf-8')
                return subprocess.run([sys.executable, str(ROOT / 'scripts/check_lean_axioms.py'),
                                       '--project', str(project), '--audit', str(path)],
                                      env=env, capture_output=True, encoding='utf-8', timeout=120)
            positive = check('Valid', VALID)
            self.assertEqual(positive.returncode, 0, positive.stdout + positive.stderr)
            self.assertIn('PASS 1 declarations', positive.stdout)
            spoof = check('Spoof', SPOOF)
            self.assertNotEqual(spoof.returncode, 0)
            custom = [f'veryLongCustomAxiomNumber{i:02}' for i in range(12)]
            many = 'import Init\n' + '\n'.join('axiom ' + name + ' : True' for name in custom) + '\n'
            many += ('theorem combination : ' + ' ∧ '.join(['True'] * 12) + ' := '
                     + ''.join('And.intro ' + name + ' (' for name in custom[:-1])
                     + custom[-1] + ')' * 11 + '\n#print axioms combination\n')
            negative = check('Custom', many)
            self.assertNotEqual(negative.returncode, 0)
            self.assertIn('veryLongCustomAxiomNumber00,\n', negative.stdout)
            self.assertIn('unexpected', negative.stderr)
            sorry = check('Sorry', 'import Init\ntheorem unproved : False := by sorry\n#print axioms unproved\n')
            self.assertNotEqual(sorry.returncode, 0)
            self.assertIn('sorryAx', sorry.stderr)


if __name__ == '__main__':
    unittest.main()

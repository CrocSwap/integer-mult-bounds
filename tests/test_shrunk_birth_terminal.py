"""Adverse controls for the selected physical witness and real Lean output parser."""
from pathlib import Path
import gzip, importlib.util, json, os, pickle, re, subprocess, sys, tempfile, unittest
ROOT=Path(__file__).resolve().parents[1]
PACKAGE=ROOT/'research/shrunk-birth-terminal'

class TerminalSelectionControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='terminal-controls-');cls.work=Path(cls.temp.name)
        cls.pins=json.loads((PACKAGE/'selected/INPUTS.json').read_text())
        for name,record in cls.pins.items():
            data=(PACKAGE/'selected/inputs'/record['stored_name']).read_bytes()
            (cls.work/name).write_bytes(gzip.decompress(data) if record['encoding']=='gzip' else data)
        cls.roles=json.loads((cls.work/'TERMINAL_ROLES.json').read_text())
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()
    def rejection(self,ids,message):
        selected=self.work/'adverse.json';selected.write_text(json.dumps(ids))
        output=self.work/'invalid-output.json'
        command=[sys.executable,str(PACKAGE/'construction/terminal_inventory.py'),'--frames',str(self.work/'FRAMES.pkl'),'--matches',str(self.work/'BIRTH_MATCHES.json.gz'),'--readouts',str(self.work/'READOUTS.pkl'),'--terminal-roles',str(selected),'--out',str(output)]
        result=subprocess.run(command,capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0,result.stdout+result.stderr);self.assertIn(message,result.stderr);self.assertFalse(output.exists())
    def test_geometry_replay_is_bound_to_actual_selected_fixture(self):
        spec=importlib.util.spec_from_file_location('selected_portable_verify',PACKAGE/'verify.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        fixture=self.work/'FRAMES.pkl';expected=json.loads((PACKAGE/'search/recipe/expected-geometry.json').read_text())
        receipt={'selected_fixture_sha256':self.pins['FRAMES.pkl']['sha256'],'canonical_geometry_sha256':expected['canonical_geometry_sha256']}
        self.assertEqual(module.bind_geometry(fixture,fixture,receipt,receipt['selected_fixture_sha256']),expected['canonical_geometry_sha256'])
        wrong=dict(receipt,selected_fixture_sha256='0'*64)
        with self.assertRaisesRegex(ValueError,'selected-fixture hash'):module.bind_geometry(fixture,fixture,wrong,receipt['selected_fixture_sha256'])
        graph=pickle.loads(fixture.read_bytes());graph['h']+=1;mutant=self.work/'wrong-geometry.pkl';mutant.write_bytes(pickle.dumps(graph,protocol=4))
        with self.assertRaisesRegex(ValueError,'differs from actual selected fixture'):module.bind_geometry(fixture,mutant,receipt,receipt['selected_fixture_sha256'])
    def test_duplicate_terminal_rejected(self):self.rejection([self.roles[0],self.roles[0]],'Duplicate terminal')
    def test_non_integer_terminal_rejected(self):self.rejection([float(self.roles[0])],'integer role IDs')
    def test_current_birth_recipient_rejected(self):
        choice=json.loads(gzip.decompress((self.work/'BIRTH_MATCHES.json.gz').read_bytes()));self.rejection([choice['pairs'][0]['recipient']],'Ineligible requested terminal')
    def test_assertion_disabled_verifier_rejected(self):
        result=subprocess.run([sys.executable,'-O',str(PACKAGE/'verify.py')],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0);self.assertIn('Assertions must remain enabled',result.stderr)

class LeanAxiomOutputControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output=(PACKAGE/'lean/receipts/compile/output.log').read_text()
        source=(PACKAGE/'lean/ShrunkBirthTerminal.lean').read_text()
        cls.audit='\n'.join(line for line in source.splitlines() if line.startswith('#print axioms '))+'\n'
    def check_output(self,output):
        with tempfile.TemporaryDirectory(prefix='lean-output-controls-') as folder:
            work=Path(folder);(work/'Audit.lean').write_text(self.audit);(work/'output.txt').write_text(output)
            # Transport stub only: preserve the actual saved kernel output.
            (work/'lake').write_text('#!'+sys.executable+'\nfrom pathlib import Path\nprint(Path(__file__).with_name("output.txt").read_text(),end="")\n');(work/'lake').chmod(0o755)
            env=os.environ.copy();env['PATH']=str(work)+os.pathsep+env.get('PATH','')
            return subprocess.run([sys.executable,str(ROOT/'scripts/check_lean_axioms.py'),'--project',folder,'--audit',str(work/'Audit.lean')],capture_output=True,text=True,env=env)
    def test_real_wrapped_240_theorem_output_passes(self):
        self.assertIn('propext,\n Classical.choice,\n Quot.sound',self.output)
        result=self.check_output(self.output);self.assertEqual(result.returncode,0,result.stdout+result.stderr);self.assertIn('PASS 240 declarations',result.stdout)
    def test_forbidden_axiom_rejected(self):
        result=self.check_output(self.output.replace('propext','forbidden_axiom',1));self.assertNotEqual(result.returncode,0);self.assertIn('forbidden_axiom',result.stdout+result.stderr)
    def test_missing_theorem_rejected(self):
        result=self.check_output(self.output.split('\n',1)[1]);self.assertNotEqual(result.returncode,0);self.assertIn('239/240',result.stdout+result.stderr)
    def test_duplicate_theorem_rejected(self):
        result=self.check_output(self.output+'\n'+self.output.split('\n',1)[0]+'\n');self.assertNotEqual(result.returncode,0);self.assertIn('241/240',result.stdout+result.stderr)
if __name__=='__main__':unittest.main()

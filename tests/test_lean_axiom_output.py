"""Parser controls using preserved real Lean output; these do not simulate proof compilation."""
from pathlib import Path
import os,re,subprocess,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
class LeanAxiomOutput(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.output=(ROOT/'research/aligned-composition/lean/receipts/compile/output.log').read_text()
  source=(ROOT/'formal/lean/KappaCheck/AlignedFrameComposition.lean').read_text()
  cls.audit='\n'.join(line for line in source.splitlines() if line.startswith('#print axioms '))+'\n'
 def check_output(self,output):
  with tempfile.TemporaryDirectory() as temp:
   directory=Path(temp);(directory/'Audit.lean').write_text(self.audit);(directory/'output.txt').write_text(output)
   # Stand in only for the subprocess transport, replaying immutable real output.
   (directory/'lake').write_text('#!'+sys.executable+'\nfrom pathlib import Path\nprint(Path(__file__).with_name("output.txt").read_text(),end="")\n');(directory/'lake').chmod(0o755)
   env=os.environ.copy();env['PATH']=str(directory)+os.pathsep+env.get('PATH','')
   return subprocess.run([sys.executable,str(ROOT/'scripts/check_lean_axioms.py'),'--project',temp,'--audit',str(directory/'Audit.lean')],capture_output=True,text=True,env=env)
 def test_real_197_theorem_output_with_wrapped_lists_passes(self):
  self.assertIn('propext,\n Classical.choice,\n Quot.sound',self.output)
  result=self.check_output(self.output);self.assertEqual(result.returncode,0,result.stdout+result.stderr);self.assertIn('PASS 197 declarations',result.stdout)
 def test_forbidden_axiom_in_wrapped_list_is_rejected(self):
  output=self.output.replace('propext,\n Classical.choice,\n Quot.sound','propext,\n forbidden_axiom,\n Quot.sound',1)
  result=self.check_output(output);self.assertNotEqual(result.returncode,0);self.assertIn('forbidden_axiom',result.stdout+result.stderr)
 def test_missing_expected_theorem_is_rejected(self):
  output=self.output.split('\n',1)[1];result=self.check_output(output);self.assertNotEqual(result.returncode,0);self.assertIn('196/197',result.stdout+result.stderr)
 def test_duplicate_output_is_rejected(self):
  output=self.output+'\n'+self.output.split('\n',1)[0]+'\n';result=self.check_output(output);self.assertNotEqual(result.returncode,0);self.assertIn('198/197',result.stdout+result.stderr)
if __name__=='__main__':unittest.main()

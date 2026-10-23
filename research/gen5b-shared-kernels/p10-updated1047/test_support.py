"""Source, dependency and portability mutation controls."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,tempfile,unittest
from unittest.mock import patch
import support,acquire_inputs

class SourceTests(unittest.TestCase):
 def test_all_input_pins(self):self.assertEqual(len(support.verify_inputs()),39)
 def test_all_authored_pins(self):self.assertEqual(len(support.verify_dependencies()),4)
 def test_input_mutation_rejected(self):
  row=support.pins()['files'][0];raw=support.read_bytes(row['path'])
  with self.assertRaises(AssertionError):support.check_bytes(raw+b' ',row)
  bad=dict(row,git_blob='0'*40)
  with self.assertRaises(AssertionError):support.check_bytes(raw,bad)
 def test_cached_downloader_mutation_rejected(self):
  row=support.pins()['files'][0]
  with tempfile.TemporaryDirectory()as d:
   p=Path(d)/row['local'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'changed')
   with self.assertRaises(AssertionError):acquire_inputs.acquire(d)
 def test_authored_dependency_mutation_rejected(self):
  d=dict(support.DEPENDENCIES);d[next(iter(d))]='0'*64
  with patch.object(support,'DEPENDENCIES',d):
   with self.assertRaises(AssertionError):support.verify_dependencies()
 def test_candidate_delta_hash(self):
  path=support.materialize_word();self.assertEqual(support.sha(path),support.WORD_SHA)
  self.assertNotEqual(hashlib.sha256(path.read_bytes()+b' ').hexdigest(),support.WORD_SHA)
 def test_assertions_disabled_rejected(self):
  r=subprocess.run([sys.executable,'-O',str(support.HERE/'run_checks.py'),'--check'],cwd='/tmp',capture_output=True,text=True)
  self.assertNotEqual(r.returncode,0);self.assertIn('assertions must be enabled',r.stderr)
 def test_inert_manifest_paths(self):
  for row in support.pins()['files']:
   self.assertFalse(row['local'].endswith('.py'));self.assertIn('/'+support.HEAD+'/',row['url'])
if __name__=='__main__':unittest.main(verbosity=2)

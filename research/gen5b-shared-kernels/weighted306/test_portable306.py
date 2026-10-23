"""Focused portable input and unchanged dependency guards."""
import hashlib,json,unittest
from pathlib import Path
from unittest.mock import patch
import context306 as c
class PortableTests(unittest.TestCase):
 def test_all13_sources_and47_dependencies(self):
  self.assertEqual(c.verify_new(),13);self.assertEqual(c.verify_dependencies(),47)
 def test_no_auxiliary_manifest_required(self):
  original=Path.read_bytes
  def guarded(p,*a,**kw):
   if p.name=='PINS.json':raise AssertionError('Undeclared auxiliary source read')
   return original(p,*a,**kw)
  with patch.object(Path,'read_bytes',guarded):
   self.assertEqual(c.verify_new(),13);self.assertEqual(c.oldsource.verify(),39)
 def test_witness_metadata_rebinding_only(self):
  from transport_witness import build
  import witness
  a=json.loads(build().read_text());b=json.loads(witness.write_case('156').read_text())
  self.assertEqual(a['entries'],b['entries']);self.assertEqual(a['local_histogram_delta'],b['local_histogram_delta'])
  self.assertEqual(a['source_head'],c.HEAD)
 def test_no_workspace_paths_in_new_code(self):
  for p in c.HERE.glob('*.py'):self.assertNotIn('/workspace'+'/',p.read_text(),p.name)
if __name__=='__main__':unittest.main()

"""Portable-input, immutable acquisition and exact matching-delta guards."""
from pathlib import Path
import hashlib,json,tempfile,unittest
import support
class SourceTests(unittest.TestCase):
 def test_all_immutable_inputs(self):self.assertEqual(len(support.verify_inputs()),40)
 def test_canonical_matching_word(self):
  self.assertEqual(support.sha(support.materialize_word()),'25a0edc8c5f399fcf536b28c4e3575aa52177bb78b6078a631acb748954f0739')
 def test_corrupt_cached_input_rejected(self):
  name='word-pins.json';original=support.INPUTS;row=next(r for r in support.pins()['files']if r['path']==name)
  with tempfile.TemporaryDirectory()as tmp:
   p=Path(tmp)/row['local'];p.write_bytes(b'corrupt')
   try:
    support.INPUTS=Path(tmp);support.read_bytes.cache_clear()
    with self.assertRaises(AssertionError):support.read_bytes(name)
   finally:support.INPUTS=original;support.read_bytes.cache_clear()
 def test_manifest_urls_and_inert_python(self):
  for row in support.pins()['files']:
   self.assertIn('/'+support.HEAD+'/',row['url'])
   self.assertEqual(row['local'],row['path']+'.txt'if row['path'].endswith('.py')else row['path'])
if __name__=='__main__':unittest.main()

import sys
if sys.flags.optimize:raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode=True
import unittest,json,gzip,copy,subprocess
import verify as v
class Controls(unittest.TestCase):
 def profiles(self):return [json.loads((v.parent.HERE/'profiles-23.json').read_text()),json.loads((v.HERE/'profiles-25.json').read_text())]
 def test_nonbijective_relabel_rejected(self):
  word=json.loads(gzip.decompress((v.HERE/'word-25.json.gz').read_bytes()))
  with self.assertRaises(AssertionError):v.relabel(word,[0]*25)
 def test_relabel_roundtrip(self):
  word=json.loads(gzip.decompress((v.HERE/'word-25.json.gz').read_bytes()));p=v.coordinates(25);inverse=[p.index(i)for i in range(25)]
  self.assertEqual(v.relabel(v.relabel(copy.deepcopy(word),inverse),p),word)
 def test_omitted_internal_rank_rejected(self):
  profiles=self.profiles();profiles[1]['blocks'][1]-=1
  with self.assertRaises(AssertionError):v.parent.combine(profiles)
 def test_stale_width_rejected(self):
  c=json.loads((v.HERE/'certificate.json').read_text());c['bit']['W']-=1
  with self.assertRaises(AssertionError):v.exact(self.profiles(),c)
 def test_overstated_exponent_rejected(self):
  c=json.loads((v.HERE/'certificate.json').read_text());c['kappa']='1/100'
  with self.assertRaises(AssertionError):v.exact(self.profiles(),c)
 def test_optimized_python_rejected(self):
  p=subprocess.run([sys.executable,'-O',str(v.HERE/'verify.py')],capture_output=True,text=True)
  self.assertNotEqual(p.returncode,0);self.assertIn('Assertions must remain enabled',p.stderr)
if __name__=='__main__':unittest.main()

import unittest,copy,json,gzip,subprocess,sys
from pathlib import Path
import verify as v
class Controls(unittest.TestCase):
 def test_nonbijective_coordinate_map_rejected(self):
  w=json.loads(gzip.decompress((v.HERE/'word-23.json.gz').read_bytes()))
  with self.assertRaises(AssertionError):v.relabel(w,[0]*23)
 def test_inverse_relabel_recovers_parent(self):
  for h in (23,25):
   w=json.loads(gzip.decompress((v.HERE/f'word-{h}.json.gz').read_bytes()));p=json.loads((v.HERE/f'permutation-{h}.json').read_text());inverse=[p.index(i)for i in range(h)]
   expected=json.loads(gzip.decompress((v.ROOT/f'certificates/indexed-cycle-word-{h}.json.gz').read_bytes()));self.assertEqual(v.relabel(w,inverse),expected)
 def test_omitted_child_profile_rejected(self):
  profiles=[json.loads((v.HERE/f'profiles-{h}.json').read_text())for h in(23,25)];profiles[0]['blocks'][1]-=1
  with self.assertRaises(AssertionError):v.combine(profiles)
 def test_stale_width_and_exponent_rejected(self):
  profiles=[json.loads((v.HERE/f'profiles-{h}.json').read_text())for h in(23,25)];cert=json.loads((v.HERE/'certificate.json').read_text())
  for key in ('width','exponent'):
   bad=copy.deepcopy(cert)
   if key=='width':bad['finite_bridge']['bit']['W']-=1
   else:bad['kappa']='1/100'
   with self.subTest(key=key),self.assertRaises(AssertionError):v.exact(profiles,bad)
 def test_optimized_python_rejected(self):
  r=subprocess.run([sys.executable,'-O',str(v.HERE/'verify.py')],capture_output=True,text=True);self.assertNotEqual(r.returncode,0);self.assertIn('Assertions must remain enabled',r.stderr)
if __name__=='__main__':unittest.main()

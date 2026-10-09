"""Exact controls against predecessor profiles and illegal binary frame choices."""
import json,unittest,subprocess,sys
from pathlib import Path
from fractions import Fraction as Q
import certificate as c
import audit
HERE=Path(__file__).resolve().parent
class Controls(unittest.TestCase):
 def test_optimized_verifier_is_rejected(self):
  r=subprocess.run([sys.executable,'-O',str(HERE/'verify.py')],capture_output=True,text=True)
  self.assertNotEqual(r.returncode,0)
  self.assertIn('Assertions must remain enabled',r.stderr+r.stdout)
 def test_prior_profiles_fail_new_saving(self):
  for name in ['pr114-profile.json','pr120-profile.json']:
   p=json.loads((HERE/name).read_text());p['child_multiplicities']={int(k):v for k,v in p['child_multiplicities'].items()}
   self.assertFalse(c.contracts(p,c.COMPLEX),name)
 def test_degenerate_line_rejected(self):
  self.assertFalse(audit.nondeg((3,)))
 def test_alternating_plane_accepted(self):
  self.assertTrue(audit.nondeg(audit.basis((3,5))))
 def test_wrong_target_containment_rejected(self):
  self.assertFalse(audit.contained(audit.basis((1,)),audit.basis((2,))))
 def test_incomparable_target_chain_rejected(self):
  a,b=audit.basis((1,)),audit.basis((2,))
  self.assertFalse(audit.contained(a,b) or audit.contained(b,a))
if __name__=='__main__':unittest.main()

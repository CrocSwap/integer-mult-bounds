from pathlib import Path
from fractions import Fraction as F
import ast,hashlib,json,re,unittest
ROOT=Path(__file__).resolve().parent
class PackageChecks(unittest.TestCase):
 def test_source_hashes(self):
  for e in json.loads((ROOT/'SOURCE_MANIFEST.json').read_text())['source_files']:
   b=(ROOT/e['published_path']).read_bytes();self.assertEqual(hashlib.sha256(b).hexdigest(),e['published_sha256']);self.assertEqual(len(b),e['published_bytes'])
 def test_selected_geometry(self):
  d=json.loads((ROOT/'REVERSED_45_CERTIFICATE.json').read_text());self.assertEqual((d['a'],d['b']),(45,47));self.assertEqual(d['profile'],[1]*9+[43,39,1933]);self.assertEqual(len(d['witness']['pivot_values']),91)
 def test_exact_selected_witness(self):
  d=json.loads((ROOT/'ASSEMBLY_CERTIFICATE.json').read_text());self.assertIn('1639226629/100000000000000',(ROOT/'ASSEMBLY_CERTIFICATE.json').read_text());self.assertEqual(d['rows']['degree'],47000)
  self.assertEqual(hashlib.sha256((ROOT/'check_composition.py').read_bytes()).hexdigest(),'876b03f9cb57de4e940a1bab623ad73dfcbfbfff05d79d03e869031fe756ec5a')
 def test_static_source(self):
  for p in ROOT.rglob('*.py'):ast.parse(p.read_text(),filename=str(p))
  for p in ROOT.rglob('*.md'):
   s=p.read_text();self.assertEqual(s.count('$$')%2,0)
   for u in re.findall(r'\]\(([^)]+)\)',s):
    if '://' in u or u.startswith('#'):continue
    self.assertTrue((p.parent/u.split('#')[0]).exists(),str((p,u)))
if __name__=='__main__':unittest.main()

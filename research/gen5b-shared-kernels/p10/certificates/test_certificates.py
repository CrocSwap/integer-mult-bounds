"""Changed-path exact chart and complete bank-assignment controls."""
import unittest,json,gzip,copy,hashlib,struct
from fractions import Fraction as Q
from check_seam_charts import ROOT,SOURCE,chart,gram
class CertificateTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.f={int(k):v for k,v in json.loads(gzip.decompress((SOURCE/'bitword/selected/bit/frames_p10.json.gz').read_bytes()))['frames'].items()}
 def test_two_original_dropped_seams(self):
  for frame in (53130,53190):self.assertEqual(chart(self.f[frame],self.f[14583])['rank'],14)
 def test_zero_seam_is_zero_rank(self):
  p=chart(self.f[14583],self.f[14583]);self.assertEqual(p['rank'],0)
 def test_false_rank_rejected(self):
  bad=copy.deepcopy(self.f[14583]);bad['dim']-=1
  with self.assertRaises(AssertionError):chart(self.f[53130],bad)
 def test_reverse_containment_rejected(self):
  with self.assertRaises(AssertionError):chart(self.f[14583],self.f[53130])
 def test_bank_stream_digest(self):
  p=json.loads((ROOT/'weighted892-candidate19-bank-receipt.json').read_text());raw=gzip.decompress((ROOT/'weighted892-candidate19-bank-addresses.bin.gz').read_bytes())
  self.assertEqual(hashlib.sha256(raw).hexdigest(),p['one_stage_table_uncompressed_sha256']);self.assertEqual(len(raw),493260*20)
  self.assertEqual(p['total_assignments'],5*8221*60);self.assertEqual(p['literal_stock'],60*4*960+5*p['banks_per_stage'])
 def test_all_positive_seam_programs_replay(self):
  p=json.loads((ROOT/'weighted892-seam-charts.json').read_text());self.assertEqual(p['positive_rank_seams'],43)
  for c in p['factor_programs']:
   A=[[Q(x)for x in row]for row in zip(*c['basis_columns'])]
   for op,i,j,q in c['factors']:
    q=Q(q)
    if op=='swap':A[i],A[j]=A[j],A[i]
    elif op=='scale':A[i]=[q*x for x in A[i]]
    else:A[i]=[x+q*y for x,y in zip(A[i],A[j])]
   self.assertEqual(A,[[int(i==j)for j in range(20)]for i in range(20)])
if __name__=='__main__':unittest.main()

"""Exact center-free coded native offer; Apache-2.0, Codex assistance."""
from pathlib import Path
import sys,json,gzip
from fractions import Fraction as Q
from collections import Counter
from hashlib import sha256
sys.path.insert(0,str(Path(__file__).resolve().parent))
import native_core as V
HERE=Path(__file__).resolve().parent

def build(a,E,back=False):
 c=a['canonical'];p=[]
 for i,j,v in E:
  if j<224:continue
  dst,src,coef=(j,i,v)if back else(i,j,-v)
  V.need(c['start'][dst]==0 and c['start'][src]==0,'Ground pre-compensation')
  p.append(['scalar',['add',['L',dst],['L',src],coef.numerator,coef.denominator],0])
 return c,p+V.clear_centers(a['programs']['backward'if back else'forward'])

def matrices(E):
 EX=[[Q(0)]*112 for _ in range(112)]
 for i,j,v in E:
  if j<112:EX[i-112][j]=v
 A=[[EX[i][j]+Q(i==j)for j in range(112)]for i in range(112)]
 V.need(all(EX[i][j]==EX[j][i]for i in range(112)for j in range(112)),'Real symmetric defect')
 V.need(sum(EX[i][i]for i in range(112))==-112,'Projection trace')
 for i in range(112):
  for j in range(112):
   s=sum(EX[i][k]*EX[k][j]for k in range(112))
   V.need(s==-14*EX[i][j],'Exact defect minimal polynomial')
 return EX,A

def expected(i,back,EX):
 r=V.expected(i,back)
 if not back and 112<=i<224:
  for j,v in enumerate(EX[i-112]):
   if v:V.add(r,V.identity(j),v)
 if back and i<112:
  for j in range(112):
   if EX[j][i]:V.add(r,V.identity(112+j),-EX[j][i])
 return r

def main():
 b=gzip.decompress((HERE/'SOURCE-WORD.json.gz').read_bytes());V.need(sha256(b).hexdigest()==V.SOURCE_SHA,'Source hash');a=json.loads(b);E=V.error_kernel(a);EX,A=matrices(E);res=[]
 generated={'scope':'Exact center-free coded ABI, not the old uncoded supplier','canonical':json.loads(json.dumps(a['canonical'])),'programs':{}}
 generated['canonical']['local_profile']={'1':2201,'2':412,'3':510,'4':127,'5':40}
 for back in(False,True):
  c,p=build(a,E,back);generated['programs']['backward'if back else'forward']=p;rows,paid,mx=V.replay(c,p,back)
  V.need(all(rows[i]==expected(i,back,EX)for i in range(632)),'All arbitrary coded endpoints')
  V.need(paid==Counter({1:2201,2:412,3:510,4:127,5:40}),'Complete center-free profile')
  res.append({'backward':back,'paid':dict(paid),'max_prefix_l1':str(mx),'events':len(p)})
 V.need((HERE/'CODED-WORDS.json.gz').is_file(),'Missing frozen emitted words')
 frozen=json.loads(gzip.decompress((HERE/'CODED-WORDS.json.gz').read_bytes()));V.need(frozen==generated,'Frozen emitted words')
 V.need((HERE/'CODE.json').is_file(),'Missing frozen code')
 V.need(json.loads((HERE/'CODE.json').read_text())=={'A':[[str(v)for v in row]for row in A]},'Frozen code entries')
 # Actual signed pre-compensation corruption must leave helper-dependent error.
 c,p=build(a,E,False);p[0][1][3]*=-1;rows,_,_=V.replay(c,p,False)
 V.need(any(rows[i]!=expected(i,False,EX)for i in range(632)),'Pre-compensation mutation rejected')
 EH=[v for i,j,v in E if j>=224]
 tariff=lambda v:3+abs(v.numerator).bit_length()-1+abs(v.numerator).bit_count()+v.denominator.bit_length()-1
 out={'status':'PASS_CENTER_FREE_CODED_SUPPLIER','source_payload_sha256':V.SOURCE_SHA,'precompensation_ADDs':len(EH),'precompensation_scalar_primitive_allowance':sum(tariff(v)for v in EH),'symmetric_defect_rank':8,'code_spectrum':{'1':104,'-13':8},'code_inverse':'I+E_X/13','condition_number_2':13,'all_632_arbitrary_rows':True,'new_kappa':None,'runs':res}
 print(json.dumps(out,sort_keys=True))
if __name__=='__main__':main()

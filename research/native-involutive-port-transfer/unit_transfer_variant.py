"""Same-chart returned-source unit-transfer corollary of PR1931; source mutates."""
from pathlib import Path
import sys,json,gzip
from fractions import Fraction as Q
from collections import Counter
from hashlib import sha256
root=Path(__file__).resolve().parent;sys.path.insert(0,str(root))
import native_core as V
V.need(sha256((root/'INVOLUTIVE-WORD.json.gz').read_bytes()).hexdigest()=='ff2999f022e93e05a250160808aa3c32a08041039d7edfb01068c0308f50c138','Frozen positive forward source')
V.need(sha256((root/'R.json').read_bytes()).hexdigest()=='7b33b6dfb494c6eafe6d87a08d6a2c2e0681e56429495b2b27949040f0f63cd1','E8 factor pin')
w=json.loads(gzip.decompress((root/'INVOLUTIVE-WORD.json.gz').read_bytes()));c=w['canonical'];p=w['program'];R=[[Q(x)for x in row]for row in json.loads((root/'R.json').read_text())];F=[[Q(x)for x in row]for row in w['F']]
ports=w['selected_ports'];K=[[R[k][i]/4 for k in range(8)]for i in range(112)];U=[[x*(1-12*(i in ports))for x in row]for i,row in enumerate(K)]
for k in range(8):
 p.append(['scalar',['clear',['C',0]],1])
 for j,v in enumerate(R[k]):
  if v:p.append(['scalar',['add',['C',0],['L',j],v.numerator,v.denominator],1])
 for i in range(112):
  v=-U[i][k]
  if v:p.append(['scalar',['add',['L',i],['C',0],v.numerator,v.denominator],1])
 p.append(['scalar',['clear',['C',0]],0])
rows,paid,mx=V.replay(c,p)
for i in range(632):
 expected=V.identity(i)
 if i<112:expected={(j,()):v for j,v in enumerate(F[i])if v}
 elif i<224:
  for j,v in enumerate(F[i-112]):
   if v:V.add(expected,V.identity(j),v)
 V.need(rows[i]==expected,'Every arbitrary unit-transfer row')
V.need(paid==Counter({1:2209,2:412,3:510,4:127,5:40}),'Unit variant paid invoice')
artifact={'canonical':c,'program':p}
if '--emit' in sys.argv:
 (root/'UNIT-TRANSFER-WORD.json.gz').write_bytes(gzip.compress(json.dumps(artifact,sort_keys=True,separators=(',',':')).encode(),mtime=0))
else:
 V.need((root/'UNIT-TRANSFER-WORD.json.gz').is_file(),'Missing frozen unit-transfer word')
 V.need(json.loads(gzip.decompress((root/'UNIT-TRANSFER-WORD.json.gz').read_bytes()))==artifact,'Frozen literal unit-transfer word')
print(json.dumps({'status':'PASS_RETURNED_SOURCE_UNIT_TRANSFER','all_arbitrary_rows':632,'arbitrary_helpers_preserved':408,'paid':dict(paid),'endpoint':'Xnew=FX;Ynew=Y+Xnew','source_mutates':True,'new_kappa':None,'max_prefix_l1':str(mx)},sort_keys=True))

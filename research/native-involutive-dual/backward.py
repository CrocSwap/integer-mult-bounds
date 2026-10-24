from pathlib import Path
import json,gzip,sys
from fractions import Fraction as Q
from collections import Counter
from hashlib import sha256
sys.path.insert(0,str(Path(__file__).resolve().parent))
import native_core as V,coded_verify as C,clifford_exact as ce
P=Path(__file__).resolve().parent

def conjugate(op):
 circ=[]
 for e in op.circuit:
  if e[0]=='D':circ.append(('D',e[1],tuple((-x)%4 for x in e[2])))
  elif e[0]=='C':circ.append(('C',e[1],-e[2]))
  elif e[0]=='phase':circ.append(('phase',(-e[1])%4))
  else:circ.append(e)
 return ce.Op(op.n,tuple((x,z,(-ph)%4)for x,z,ph in op.tab),circ)

def main():
 raw=gzip.decompress((P/'SOURCE-WORD.json.gz').read_bytes());V.need(sha256(raw).hexdigest()==V.SOURCE_SHA,'Source hash')
 a=json.loads(raw);E=V.error_kernel(a);EX,A=C.matrices(E)
 f=json.loads(gzip.decompress((P/'INVOLUTIVE-WORD.json.gz').read_bytes()));F=[[Q(x)for x in r]for r in f['F']]
 c,p=C.build(a,E,True);p=list(p);native=[]
 for i in f['selected_ports']:
  fi=c['final'][112+i]
  p.append(['scalar',['clear',['C',0]],fi])
  p.append(['scalar',['copy',['C',0],['L',112+i]],fi])
  op=conjugate(ce.canonical_frame(9,c['frames'][fi])).adjoint().then(conjugate(ce.canonical_frame(9,c['frames'][1])))
  cert,compiled=ce.lower_child(op)
  V.need(cert['rank']==1 and compiled.tab==op.tab and compiled.zero_state()==op.zero_state(),'Exact phase-correct conjugate raising')
  native.append({'port':i,'from':fi,'to':1,'lowering':cert,'literal_circuit':compiled.circuit,'target_circuit':op.circuit})
  p.append(['center',0,fi,1,1])
  for j in range(112):
   v=-(F[i][j]-A[i][j])
   if v:p.append(['scalar',['add',['L',j],['C',0],v.numerator,v.denominator],1])
  p.append(['scalar',['clear',['C',0]],0])
 repair_start=len(p)-sum(4+sum(F[i][j]!=A[i][j] for j in range(112)) for i in f['selected_ports'])
 rows,paid,mx=V.replay(c,p,True)
 for i in range(632):
  want=V.identity(i)
  if i<112:
   for j in range(112):
    if F[j][i]:V.add(want,V.identity(112+j),-F[j][i])
  V.need(rows[i]==want,'All arbitrary backward rows')
 V.need(paid==Counter({1:2209,2:412,3:510,4:127,5:40}),'Complete dual invoice')
 # Explicit guards remain active under optimized Python.
 import copy
 bad=copy.deepcopy(p)
 k=next(k for k in range(repair_start,len(bad)) if bad[k][0]=='scalar' and bad[k][1][0]=='add')
 bad[k][1][3]*=-1
 wrong,_,_=V.replay(c,bad,True)
 V.need(any(wrong[i]!=rows[i] for i in range(632)),'Signed repair mutation rejected')
 bad=[e for e in p if not(e[0]=='center' and e[4]==1)]
 try:V.replay(c,bad,True)
 except ValueError:pass
 else:raise ValueError('Unpaid raising mutation accepted')
 V.need(any(F[i][j]!=F[j][i] for i in range(112) for j in range(112)),'F is not silently treated as symmetric')
 artifact={'canonical':c,'program':p,'native_repairs':native,'F':f['F'],'selected_ports':f['selected_ports'],'scope':'Normalized raw-dual with actual conjugate frame repairs'}
 if '--emit' in sys.argv:(P/'BACKWARD-WORD.json.gz').write_bytes(gzip.compress(json.dumps(artifact,sort_keys=True,separators=(',',':')).encode(),mtime=0))
 else:V.need(json.loads(gzip.decompress((P/'BACKWARD-WORD.json.gz').read_bytes()))==json.loads(json.dumps(artifact)),'Frozen backward word')
 print(json.dumps({'status':'PASS_INVOLUTIVE_BACKWARD','arbitrary_rows':632,'helpers':408,'paid':dict(paid),'prefix_l1':str(mx),'repairs':8,'new_kappa':None}))
if __name__=='__main__':main()

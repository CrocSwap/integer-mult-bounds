"""Port PR1931 reflection to the current 632-field source; exact forward word."""
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
from collections import Counter
import sys,json,gzip
sys.path.insert(0,str(Path(__file__).resolve().parent))
import native_core as V, coded_verify as C, clifford_exact as ce
HERE=Path(__file__).resolve().parent
PORTS=[0,7,20,23,86,93,108,111]
R_HASH="7b33b6dfb494c6eafe6d87a08d6a2c2e0681e56429495b2b27949040f0f63cd1"
CE_HASH="2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962"
def mm(a,b):return [[sum((a[i][k]*b[k][j]for k in range(len(b))),Q(0))for j in range(len(b[0]))]for i in range(len(a))]
def main():
 b=gzip.decompress((HERE/'SOURCE-WORD.json.gz').read_bytes());V.need(sha256(b).hexdigest()==V.SOURCE_SHA,'Source hash')
 V.need(sha256((HERE/'R.json').read_bytes()).hexdigest()==R_HASH,'R source hash')
 V.need(sha256((HERE/'clifford_exact.py').read_bytes()).hexdigest()==CE_HASH,'Clifford compiler hash')
 a=json.loads(b);R=[[Q(x)for x in row]for row in json.loads((HERE/'R.json').read_text())];E=V.error_kernel(a);EX,A=C.matrices(E)
 K=[[R[k][i]/4 for k in range(8)]for i in range(112)]
 P=[K[i]if i in PORTS else[Q(0)]*8 for i in range(112)]
 I8=[[Q(i==j)for j in range(8)]for i in range(8)]
 V.need(mm(R,K)==[[14*x for x in row]for row in I8],'RK14')
 V.need(mm(R,P)==I8,'Supported right inverse')
 KR=mm(K,R);V.need(EX==[[-x for x in row]for row in KR],'Actual source E8 factor')
 PR=mm(P,R);correction=[[12*x for x in row]for row in PR]
 U=[[K[i][k]-12*P[i][k]for k in range(8)]for i in range(112)]
 UR=mm(U,R);F=[[Q(i==j)-UR[i][j]for j in range(112)]for i in range(112)]
 V.need(F==[[A[i][j]+correction[i][j]for j in range(112)]for i in range(112)],'Actual corrected transfer')
 V.need(mm(R,U)==[[2*x for x in row]for row in I8],'RU2')
 V.need(mm(F,F)==[[Q(i==j)for j in range(112)]for i in range(112)],'Exact involution')
 c,p=C.build(a,E,False);p=list(p);added=[];native=[]
 for i in PORTS:
  fi=c['final'][112+i];V.need(c['final'][:112]==[1]*112,'Common full X exit')
  op=ce.canonical_frame(9,c['frames'][1]).adjoint().then(ce.canonical_frame(9,c['frames'][fi]))
  cert,compiled=ce.lower_child(op)
  V.need(cert['rank']==1,'Owned lowering rank')
  V.need(op.tab==compiled.tab and op.zero_state()==compiled.zero_state(),'Exact lowering including global phase')
  native.append({'port':i,'from':1,'to':fi,'lowering':cert,'literal_circuit':compiled.circuit})
  added.append(['scalar',['clear',['C',0]],1])
  for j,v in enumerate(correction[i]):
   if v:added.append(['scalar',['add',['C',0],['L',j],v.numerator,v.denominator],1])
  added.append(['center',0,1,fi,1])
  added.append(['scalar',['add',['L',112+i],['C',0],1,1],fi])
  added.append(['scalar',['clear',['C',0]],0])
 p+=added
 rows,paid,mx=V.replay(c,p,False)
 expected=[V.identity(i)for i in range(632)]
 for i in range(112):
  for j,v in enumerate(F[i]):
   if v:V.add(expected[112+i],V.identity(j),v)
 V.need(all(rows[i]==expected[i]for i in range(632)),'All632 arbitrary input endpoint rows')
 V.need(paid==Counter({1:2209,2:412,3:510,4:127,5:40}),'Complete paid profile')
 artifact={'canonical':c,'program':p,'native_repairs':native,'selected_ports':PORTS,'F':[[str(x)for x in row]for row in F]}
 artifact=json.loads(json.dumps(artifact))
 out={'status':'PASS_ACTUAL632_INVOLUTIVE_FORWARD','source_payload_sha256':V.SOURCE_SHA,'all_arbitrary_rows':632,'arbitrary_helpers_preserved':408,'added_rank1_owned_repairs':8,'paid':dict(paid),'final_ABI_unchanged':True,'involution_exact':True,'max_prefix_l1':str(mx),'physical_raw_dual_emitted':False,'new_kappa':None,'source_predecessor_PR':1931}
 out=json.loads(json.dumps(out))
 if '--emit' in sys.argv:
  (HERE/'INVOLUTIVE-WORD.json.gz').write_bytes(gzip.compress(json.dumps(artifact,sort_keys=True,separators=(',',':')).encode(),mtime=0))
  (HERE/'INVOLUTIVE-EXPECTED.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 else:
  V.need((HERE/'INVOLUTIVE-WORD.json.gz').is_file(),'Missing frozen word')
  V.need(json.loads(gzip.decompress((HERE/'INVOLUTIVE-WORD.json.gz').read_bytes()))==artifact,'Frozen actual emitted word')
  V.need(json.loads((HERE/'INVOLUTIVE-EXPECTED.json').read_text())==out,'Frozen exact receipt')
 # Sign mutation remains an arbitrary-input error rather than silently an involution.
 bad=[[A[i][j]-correction[i][j]for j in range(112)]for i in range(112)]
 V.need(mm(bad,bad)!=[[Q(i==j)for j in range(112)]for i in range(112)],'Repair sign mutation rejected')
 badword=[e for e in p if not(e[0]=='center' and e[4]==1)]
 try:V.replay(c,badword,False)
 except ValueError:pass
 else:raise ValueError('Missing physical lowering mutation accepted')
 print(json.dumps(out,sort_keys=True))
if __name__=='__main__':main()

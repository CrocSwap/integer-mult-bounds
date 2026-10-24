#!/usr/bin/env python3
"""Light independent source/owned/zero falsifiers, using our own word engine."""
from pathlib import Path
from fractions import Fraction as F
import copy,hashlib,importlib.util,json,time
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('our_word',HERE/'check_word.py');w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
def reject(label,p,owned):
 try:w.evaluate(p,owned)
 except ValueError as e:return {'control':label,'status':'REJECTED','reason':str(e)}
 raise ValueError('mutant accepted: '+label)
def main():
 start=time.monotonic();word=w.load(w.PKG/'WORD.json.gz');owned={tuple(r) for r in word['owned_roles']};_,formal,_,_=w.transform(word['backward']);controls=[]
 bad=copy.deepcopy(word['backward']);bad[1][1][3]*=-1
 controls.append(reject('wrong prepared-source relation sign after transposition',w.transform(bad)[1],owned))
 bad=copy.deepcopy(formal)
 for i in range(len(bad)-1):
  a,b=bad[i:i+2]
  if a[0]==b[0]=='scalar' and a[1][0]=='add' and b[1][0]=='clear' and a[1][2]==b[1][1]:
   bad[i],bad[i+1]=bad[i+1],bad[i];break
 else:raise ValueError('COPY-transpose pair not found')
 controls.append(reject('COPY transpose CLEAR before ADD',bad,owned))
 bad=copy.deepcopy(formal);i=next(i for i,e in enumerate(bad) if e[0]=='scalar' and e[1][0]=='clear');bad[i][1][1]=['L',0]
 controls.append(reject('erase retained borrowed field',bad,owned))
 rows={('L',i):{(('L',i),()):F(1)} for i in range(632)};rows.update({('C',i):{(('C',i),()):F(1)} for i in range(9)});cuts=[]
 for i,e in enumerate(formal):
  tag=e[0]
  if tag=='scalar':
   g=e[1];dst=tuple(g[1])
   if g[0]=='clear':rows[dst]={}
   elif g[0]=='scale':rows[dst]={k:q*F(*g[2:]) for k,q in rows[dst].items()}
   else:
    for k,q in tuple(rows[tuple(g[2])].items()):w.plus(rows[dst],k,q*F(*g[3:]))
  elif tag in ('ghost','warp'):
   dst=tuple(e[1]);op=e[2]
   if tag=='ghost':
    nonzero=bool(rows[dst]);term=next(iter(rows[dst].items()),None)
    cuts.append({'formal_event':i,'role':list(dst),'proof_symbol':op,'reverse_input_zero':not nonzero,'nonzero_terms':len(rows[dst]),'first_nonzero_term':None if term is None else {'entry_role':list(term[0][0]),'operator_word':list(term[0][1]),'coefficient':str(term[1])}})
   transformed={}
   for (r,u),q in rows[dst].items():
    v=u[1:] if u and u[0]==-op else (op,)+u;w.plus(transformed,(r,v),q)
   rows[dst]=transformed
 w.need(len(cuts)==8 and all(not c['reverse_input_zero'] for c in cuts),'actual reverse zero assumption must fail at all eight cuts')
 result={'status':'PASS_EXTRA_INDEPENDENT_PHYSICAL_FALSIFIERS','head':w.HEAD,'controls':controls,'reverse_zero_assumption_falsified_at':cuts,'seconds':round(time.monotonic()-start,3),'word_engine_sha256':hashlib.sha256((HERE/'check_word.py').read_bytes()).hexdigest()}
 (HERE/'CONTROL-RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()

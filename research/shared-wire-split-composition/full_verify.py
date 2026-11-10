#!/usr/bin/env python3
"""Portable independent arithmetic/operator gate plus attributed precision reuse.
Read-only unless an explicit --out result path is supplied.
"""
from pathlib import Path
from fractions import Fraction as F
import argparse,contextlib,copy,hashlib,importlib.util,io,json
HERE=Path(__file__).resolve().parent
if not __debug__:raise RuntimeError('Run without -O; assertions are proof checks.')
def module(name,filename):
 s=importlib.util.spec_from_file_location(name,HERE/filename);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
I=module('independent_native','independent.py');G=module('independent_intervals','interval_gate.py');P=module('attributed_precision','precision_replay.py')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def run(wordpath,callerpath,bitpath,controls=True,precision=True):
 manifest=json.loads((HERE/'INDEPENDENT-SOURCES.json').read_text())
 for item in manifest['files']:assert sha(HERE/item['path'])==item['sha256'],item['path']
 W=I.load(wordpath);C=I.load(callerpath);bit=I.load(bitpath)
 assert hashlib.sha256(json.dumps(W,sort_keys=True,separators=(',',':')).encode()).hexdigest()==manifest['word_canonical_json_sha256']
 assert sha(callerpath)==next(x['sha256'] for x in manifest['files'] if x['path']=='data/caller.json')
 assert sha(bitpath)==next(x['sha256'] for x in manifest['files'] if x['path']=='data/bit-admission.json')
 assert F(bit['ordinary_admitted'])==F('.00385248') and F(bit['previous_ordinary'])==F('.0034')
 assert bit['empty_body_targets']=={'count':0,'rank1_productive_credit':0}
 assert F(manifest['numeric_BIT_price'])<F(bit['ordinary_admitted'])
 previous=F(bit['previous_ordinary'])
 for step in bit['ordinary_bootstrap']:
  atom=F(step['atom']);covered=F(step['covered']);envelope=(1-atom)*covered+atom*previous;admitted=F(step['admitted'])
  assert envelope==F(step['envelope']) and previous<admitted<envelope and F(step['previous'])==previous
  previous=admitted
 assert previous==F(bit['ordinary_admitted'])
 N=I.native(W);assert not N['bad_inputs'];invoice=I.invoices(W,C,N);ordinary=I.ordinary(W,C,N)
 with contextlib.redirect_stdout(io.StringIO()):caller=I.caller(C)
 assert not caller['bad_outputs'] and invoice['empty_root_credits']==0 and invoice['S']==1520 and ordinary['conservative_total']<10**9
 gate=G.gate(invoice,manifest['claim'],manifest['tested'],manifest['raw_lower'],manifest['raw_upper'],manifest['numeric_BIT_price'])
 out=dict(status='PASS_INDEPENDENT_FULL_GATE',word_sha256=sha(wordpath),word_canonical_json_sha256=manifest['word_canonical_json_sha256'],caller_sha256=sha(callerpath),BIT_receipt_sha256=sha(bitpath),native=N,caller=caller,invoice=invoice,ordinary=ordinary,gate=gate,BIT_dependency='Paired E-free BIT .00385248, bootstrapped from selected .0034; price conservatively weakened to .00376669. Retained native provenance does not import its old ordinary bootstrap.')
 if precision:out['precision']=P.run(W,C,gate,manifest)
 if controls:
  last=len(W['initial'])-1;idx=next(i for i,e in enumerate(W['program']) if e[0] in ('ADD','SCALE') and e[1]==last);bad=I.native(W,mutant=idx);assert bad['bad_inputs']
  ctr={'last_helper_scalar_doubling':{'event':idx,'bad_input_rows':len(bad['bad_inputs'])}}
  wrong=copy.deepcopy(W);wrong['final'][last]=wrong['initial'][last]
  try:I.native(wrong)
  except AssertionError:ctr['invented_helper_endpoint']='rejected'
  else:raise AssertionError('False endpoint accepted')
  wrong=copy.deepcopy(C);idx=next(i for i,e in enumerate(wrong['events']) if e[0]!='J' and e[1]=='QUERY');del wrong['events'][idx]
  with contextlib.redirect_stdout(io.StringIO()):bad=I.caller(wrong)
  assert bad['bad_outputs'];ctr['deleted_QUERY']={'event':idx,'bad_outputs':bad['bad_outputs']}
  for name,k,t in [('closed_compiler_gap',gate['claim'],gate['claim']),('unfunded_price',F(manifest['raw_upper'])+F(1,10**11),F(manifest['raw_upper'])+F(1,10**10))]:
   try:G.gate(invoice,k,t,manifest['raw_lower'],manifest['raw_upper'],manifest['numeric_BIT_price'])
   except AssertionError:ctr[name]='rejected'
   else:raise AssertionError('Invalid price accepted')
  out['negative_controls']=ctr
 out['scope']='Independent scalar endpoints, exact symbolic caller, full inherited invoice and numerical gates; attributed precision-engine reuse. Five framework assumptions, odd native alphabet/exact-child contract, A6 and ordinary LAMBDA tariff remain conditional. Finite chart lowering is separately supplied by the construction package.'
 return out
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--word',type=Path,default=HERE/'data/final.json.gz');ap.add_argument('--caller',type=Path,default=HERE/'data/caller.json');ap.add_argument('--bit-receipt',type=Path,default=HERE/'data/bit-admission.json');ap.add_argument('--out',type=Path);ap.add_argument('--core-only',action='store_true');a=ap.parse_args();result=run(a.word,a.caller,a.bit_receipt,not a.core_only,not a.core_only)
 frozen=HERE/'FULL-RESULT.json'
 if frozen.exists() and not a.core_only:
  old=json.loads(frozen.read_text());normalized=json.loads(json.dumps(result));assert {k:v for k,v in normalized.items() if k!='word_sha256'}=={k:v for k,v in old.items() if k!='word_sha256'},'Every proof-relevant receipt field must replay'
 if a.out:a.out.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ('status','word_canonical_json_sha256','caller_sha256','BIT_receipt_sha256')},indent=2))

"""Supplied-word verifier, independent of construction. Stdlib, Python >=3.9.
Vendored finite interpreter unchanged; only module-local strict zip shim on3.9.
No physical rounded caller, provider, compiler, or regeneration theorem.
"""
import argparse,copy,hashlib,importlib.util,itertools,json,sys
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PIN='ae62d5d8bef6f7146454b4b3643e487a58380c606a16c5baef7bf0dcf9df1472'
AUDIT_PIN='029fcc729e2f5dda51ac1ebc7caf6a51d7a6d9b3e2772380731c6f910502099d'
def sha(b):return hashlib.sha256(b).hexdigest()
def need(ok,label):
 if not ok:raise ValueError(label)
def strict_zip(*args,strict=False):
 if not strict:return zip(*args)
 sentinel=object()
 def gen():
  for row in itertools.zip_longest(*args,fillvalue=sentinel):
   if any(x is sentinel for x in row):raise ValueError('strict zip lengths differ')
   yield row
 return gen()
def load():
 manifest=json.loads((ROOT/'INPUT-MANIFEST.json').read_bytes())
 for item in manifest['files']:need(sha((ROOT/item['path']).read_bytes())==item['sha256'],'INPUT_PIN:'+item['path'])
 p=ROOT/'vendor/integer_grid_audit.py';need(sha(p.read_bytes())==AUDIT_PIN,'AUDIT_SOURCE_PIN')
 spec=importlib.util.spec_from_file_location('finite_interpreter',p);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 if sys.version_info<(3,10):mod.zip=strict_zip
 w,_=mod.read_json(ROOT/'candidate/WORD.json.gz');c,_=mod.read_json(ROOT/'candidate/CERTS.json');h,_=mod.read_json(ROOT/'candidate/DECLARED-HEADER.json');b,_=mod.read_json(ROOT/'base-cf6a/UNREPLAYED-WORD.json.gz')
 need(sha(mod.canonical(w))==PIN,'WORD_CANONICAL_PIN')
 header=lambda x:{k:v for k,v in x.items() if k!='program'}
 need(header(w)==header(h)==header(b),'ACTUAL_CF6A_HEADER_BINDING')
 need(c['candidate_canonical_sha256']==PIN,'CERTIFICATE_CANDIDATE_BINDING')
 return mod,w,c,b
class LiteralFailure(ValueError):pass
def smooth(v):
 for p in (2,3,5):
  while v and v%p==0:v//=p
 return v==1
def literals(w):
 total=0;num=den=0
 for event,e in enumerate(w['program']):
  if e[0] not in ('ADD','COPY','SCALE'):continue
  q=Fraction(e[2] if e[0]=='SCALE' else e[3]);total+=1
  if not q:raise LiteralFailure('LITERAL_ZERO')
  if abs(q.numerator).bit_length()>24 or q.denominator.bit_length()>24:raise LiteralFailure('LITERAL_24BIT')
  if not smooth(q.denominator) or (e[0]=='SCALE' and not smooth(abs(q.numerator))):raise LiteralFailure('LITERAL_SMOOTH')
  num=max(num,abs(q.numerator).bit_length());den=max(den,q.denominator.bit_length())
 return {'events_checked':total,'max_numerator_bits':num,'max_denominator_bits':den,'rule':'nonzero; numerator/denominator <=24bits; all denominators and SCALE numerators 2/3/5-smooth. ADD/COPY numerators need not be smooth.'}
def controls(mod,w,c,b):
 results=[]
 def check(name,expected,ww,cc,hh):
  try:mod.audit_word(ww,cc,225*2**14,hh)
  except mod.AuditFailure as e:
   need(e.kind==expected,'WRONG_REJECTION:'+name+':'+e.kind);results.append({'name':name,'expected':expected,'actual':e.kind,'details':e.details})
  else:raise ValueError('CONTROL_ACCEPTED:'+name)
 clear=min(int(k) for k in c['clear_event_index']);key=str(clear);field=w['program'][clear][1]
 cc=copy.deepcopy(c);cc['clear_event_index'][key]={str(field):'1'};check('self_reference','CERTIFICATE_SOURCE_NOT_OTHER_LIVE',w,cc,b)
 # Replace first dirty certificate with zero sum; independently verified baseline identifies dirty count.
 key=min((k for k,v in c['clear_event_index'].items() if v),key=int)
 cc=copy.deepcopy(c);cc['clear_event_index'][key]={};check('dirty_certificate_erased','CLEAR_CERTIFICATE_EQUALITY',w,cc,b)
 for label,value,expected in [('denominator7','1/7','LITERAL_SMOOTH')]:
  ww=copy.deepcopy(w);index=next(i for i,e in enumerate(ww['program']) if e[0]=='ADD');ww['program'][index][3]=value
  try:literals(ww)
  except LiteralFailure as e:need(str(e)==expected,'WRONG_LITERAL_REJECTION');results.append({'name':label,'expected':expected,'actual':str(e)})
  else:raise ValueError('CONTROL_ACCEPTED:'+label)
 return results
ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['finite','controls'],required=True);ap.add_argument('--grid',type=int,default=225*2**14);args=ap.parse_args()
mod,w,c,b=load();guards=literals(w)
if args.mode=='finite':
 report=mod.audit_word(w,c,args.grid,b)
 need((report['events'],report['clear_certificates'],report['zero_clear_rows'],report['owned_peak'])==(154768,235,42,51),'CENSUS_MISMATCH')
 need(report['literal_denominators_5_smooth'],'NONSMOOTH_REPORTED')
else:report={'status':'PASS_EXPECTED_NEGATIVE_CONTROLS','controls':controls(mod,w,c,b)}
report.update({'candidate':PIN,'literal_guard':guards,'runtime':sys.version,'compatibility':'module-local strict zip shim only' if sys.version_info<(3,10) else 'none','construction_regeneration':'NOT_ESTABLISHED'})
print(json.dumps(report,indent=2,sort_keys=True))

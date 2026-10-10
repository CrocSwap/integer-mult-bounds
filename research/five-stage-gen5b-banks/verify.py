#!/usr/bin/env python3
"""Immutable gen5 five-stage banks: regenerate every mandatory finite stage.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""
import sys
if not __debug__:raise SystemExit('Assertions required; refusing-O')
sys.dont_write_bytecode=True
from pathlib import Path
from datetime import datetime,timezone
from fractions import Fraction
import argparse,hashlib,importlib.util,json,time,traceback
ROOT=Path(__file__).resolve().parent
REQUIRED={'virtual','raw','bit','scalar','primes','banks','complex','math','finite'}

def progress(message):print(datetime.now(timezone.utc).strftime('%H:%M:%S UTC')+'  '+message,flush=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def serial(x):
 if isinstance(x,Fraction):return str(x)
 if isinstance(x,dict):return {str(k):serial(v)for k,v in x.items()}
 if isinstance(x,(list,tuple)):return list(map(serial,x))
 return x

def load(name):
 s=importlib.util.spec_from_file_location('source527_'+name,ROOT/(name+'.py'));m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m

def integrity():
 p=ROOT/'MANIFEST.json';m=json.loads(p.read_text());actual={}
 for q in ROOT.rglob('*'):
  assert not q.is_symlink(),'Symlink in package'
  if q.is_file()and q.name!='MANIFEST.json':actual[q.relative_to(ROOT).as_posix()]=sha(q)
 # Nested source manifests are also ordinary pinned inputs.
 for q in ROOT.rglob('MANIFEST.json'):
  if q!=p:actual[q.relative_to(ROOT).as_posix()]=sha(q)
 assert actual==m['files'],'Missing, changed or unpinned package/source file'
 return sha(p),len(actual)

def validate_required(results):
 assert set(results)==REQUIRED,'Missing mandatory proof stage'
 assert all(isinstance(results[k],dict)and results[k]for k in REQUIRED)

def controls():
 out=[];good={k:{'present':True}for k in REQUIRED}
 for k in sorted(REQUIRED):
  bad=good.copy();bad.pop(k)
  try:validate_required(bad)
  except AssertionError:out.append('omitted '+k+' stage')
  else:raise AssertionError('Missingstageaccepted')
 return out

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
 import sympy
 assert sys.version_info>=(3,11)and sympy.__version__=='1.14.0'
 digest,count=integrity();output=args.output.resolve();assert not output.is_relative_to(ROOT)and not output.exists(),'Output must be new and outside package';output.mkdir(parents=True)
 results={};timings={};start=time.monotonic()
 def save(name,value):(output/name).write_text(json.dumps(serial(value),sort_keys=True,indent=2)+'\n')
 def stage(name,call):
  t=time.monotonic();value=call();results[name]=value;timings[name]=time.monotonic()-t;save(name+'.json',value);progress(name+' PASS '+format(timings[name],'.1f')+'s');return value
 try:
  progress('Admitting the pinned gen5 physical bit word')
  stage('virtual',lambda:load('virtual_check').run(output,progress))
  context=load('prepare').prepare()
  raw=stage('raw',lambda:load('raw_ledger').run(context))
  portable=load('portable_bit');bit=portable.run(prepared_context=context,raw=raw,output_dir=output,run_geometry=True,package_root=ROOT);raw=bit['raw'];results['raw']=raw;save('raw.json',raw);results['bit']=portable.summary(bit);timings['bit']=bit['seconds'];save('bit.json',results['bit']);progress('bit physical/global/geometry PASS')
  scalar=stage('scalar',lambda:load('scalar_check').run(context,bit['records'],progress))
  primes=stage('primes',lambda:load('prime_check').run(context,bit['physical'],progress))
  bankresult=stage('banks',lambda:load('bank_check').run(context,bit['global_result'],bit['lower']))
  banks=bankresult['banks'];banked=bankresult['banked_result']
  complex_result=stage('complex',lambda:load('portable_complex').run(package_root=ROOT,progress=progress))
  assert complex_result['precision_guard']['retained_row_coefficient']==20161
  math=stage('math',lambda:load('math_check').run(raw,complex_result['five_stage_histogram'],banks,bit['global_result']))
  finite=stage('finite',lambda:load('finite_check').run(raw,bit['physical'],scalar,primes,math,banks,banked,bit['global_result']))
  assert math['mathematics']['finite_bridge']['rows']['coefficient']==complex_result['precision_guard']['retained_row_coefficient']==finite['row_reserve']['external_complex_coefficient']
  validate_required(results);assert len(scalar['controls'])==11 and len(primes['controls'])==6
  assert math['mathematics']['kappa']=='373354860481239/500000000000000000'
  after,_=integrity();assert after==digest,'Package changed during replay'
  certificate=dict(schema='gen5-parity-fused-five-stage-banks/1',**math['mathematics'],scope='Conditionalfiniteconstruction; inheritedallsizecompiler,weightedselector,commonancestorchart,restoredrow,routing,prime,recovery,complexsymbolicandanalyticinterfacesremainassumptions.')
  save('certificate.json',certificate)
  report=dict(status='PASS_IMMUTABLE_PARITY_FUSED_GEN5_FIVE_STAGE_BANKED_CONSTRUCTION',manifest_sha256=digest,files=count,kappa=math['mathematics']['kappa'],kappa_scientific=math['mathematics']['kappa_scientific'],fresh_stages=sorted(REQUIRED),inputs_unchanged=True,timings=timings,seconds=time.monotonic()-start,negative_controls=controls())
  save('verification.json',report);print(json.dumps(report),flush=True)
 except BaseException as exc:
  save('failure.json',dict(status='FAIL',error=str(exc),completed_stages=sorted(results),timings=timings,traceback=traceback.format_exc()));raise
if __name__=='__main__':main()

"""PR353 reordered/PLAIN12 source admission using original PR325/329 checkers.
The source's signed integer decoder/dirty restoration is checked on arbitrary
inputs; the bit projection remains an F2 contract, as stated upstream.
OpenAI Codex adapter; retained upstream implementation and AI credits in pkg.
"""
import sys,json,hashlib,importlib.util,time,struct
from pathlib import Path
from array import array
assert __debug__;sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent

def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m

def serial(x):
 from fractions import Fraction
 if isinstance(x,Fraction):return str(x)
 if isinstance(x,dict):return {str(k):serial(v)for k,v in x.items()}
 if isinstance(x,(tuple,list)):return [serial(v)for v in x]
 return x

def admission(package,output,record=False):
 package=Path(package).resolve();output=Path(output).resolve();assert not output.exists()and not output.is_relative_to(package);output.mkdir(parents=True)
 sys.path.insert(0,str(package));import word_pins
 assert Path(word_pins.__file__).resolve()==package/'word_pins.py'
 if record:word_pins.RECORD={}
 else:
  assert word_pins.RECORD is None and package==HERE/'pkg'
  from verify_source import integrity
  manifest_before=integrity()
 began=time.monotonic();result={}
 def save(n,v):(output/(n+'.json')).write_text(json.dumps(serial(v),sort_keys=True,indent=2)+'\n')
 def progress(t):print(t,flush=True)
 result['virtual']=load('src353_virtual',package/'virtual_check.py').run(output,progress);save('virtual',result['virtual'])
 ctx=load('src353_prepare',package/'prepare.py').prepare()
 result['original_helper_roles']=[int(x)for x in ctx['regs']];save('original-helper-roles',result['original_helper_roles'])
 physical=load('src353_physical',package/'code/physical527.py').run(dict(ctx),ctx['SOURCE_TEXT'],output_dir=None)
 parity=load('src353_parity',package/'parity_transform.py').run(physical)
 assert hashlib.sha256(parity['records'].tobytes()).hexdigest()=='e7d20c66176ff94e435e1462f749699316e392912ba04658318c1b36784400ea'
 save('physical',physical['physical']);save('parity',parity['physical'])
 result['source_scalar']=load('src353_scalar',package/'scalar_check.py').run(ctx,parity['records'],progress,len(parity['initial_state']));save('source-scalar',result['source_scalar'])
 result['source_word_sha256']=hashlib.sha256(parity['records'].tobytes()).hexdigest()
 result['status']='DISCOVERY_SOURCE_ADMISSION_PINS'if record else'PASS_STRICT_NEWBASE_VIRTUAL_GEOMETRY_INTEGER_DECODER_DIRTY_AND_F2_WORD'
 result['seconds']=time.monotonic()-began
 result['scope']='Newbase source exact virtual/physical geometry, all-column F2 word/inverse, signed defining-integer source decoder and dirty restoration in both directions. This does not assert that the emitted parity-filtered bit word has the same integer endpoint as its signed source; its contract is F2.'
 if record:save('observed-pins',word_pins.RECORD)
 else:
  assert word_pins.RECORD is None and integrity()==manifest_before
  result['source_manifest_sha256']=manifest_before
 save('ADMISSION',result);print(result['status'],time.monotonic()-began,flush=True);return result

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--package',type=Path,default=HERE/'pkg');ap.add_argument('--output',type=Path,required=True);ap.add_argument('--record-discovery-pins',action='store_true');a=ap.parse_args();admission(a.package,a.output,a.record_discovery_pins)

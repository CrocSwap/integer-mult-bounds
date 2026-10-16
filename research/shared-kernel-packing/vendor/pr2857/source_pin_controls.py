# SPDX-License-Identifier: Apache-2.0
"""Source-authentication controls for Yiyang (@Lyy-iiis), with OpenAI Codex assistance."""
import argparse,copy,gzip,hashlib,importlib.util,json,os,subprocess,sys
from pathlib import Path
PRODUCER_SHA='b3241527e6c136dc4b54975ef401c49d452bd6159fb99030accaf095c8fbd3ed'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(ok,msg):
 if not ok:raise RuntimeError(msg)
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--producer',required=True,type=Path);p.add_argument('--source-base',required=True,type=Path);p.add_argument('--source-extra',required=True,type=Path);p.add_argument('--source-dir',required=True,type=Path);p.add_argument('--out-dir',required=True,type=Path)
 a=p.parse_args();sys.dont_write_bytecode=True;os.environ['PYTHONDONTWRITEBYTECODE']='1'
 require(digest(a.producer)==PRODUCER_SHA,'producer SHA mismatch')
 require(not a.out_dir.exists(),'out-dir must be fresh');a.out_dir.mkdir(parents=True)
 watched=[a.producer,a.source_base,a.source_extra,a.source_dir/'word_patch.py',a.source_dir/'audit_local.py'];before={str(x):digest(x) for x in watched}
 spec=importlib.util.spec_from_file_location('_shared_kernel_pin_control',a.producer);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 checks=[]
 for variant,source in [('base',a.source_base),('extra',a.source_extra)]:
  original=json.loads(gzip.decompress(source.read_bytes()));prior=copy.deepcopy(original);new,ledger=m.apply(original)
  require(original==prior,'apply mutated its input')
  changed=copy.deepcopy(original);changed['report']['R']+=1
  try:m.apply(changed)
  except ValueError as e:require('unauthorized decoded source SHA256' in str(e),'wrong decoded mutation failure')
  else:raise RuntimeError('decoded mutation accepted')
  checks.append(dict(variant=variant,control='decoded_source_mutation',rejected=True,reason='unauthorized decoded source SHA256'))
  bad=a.out_dir/f'{variant}-source-byte-mutant.json.gz';bad.write_bytes(source.read_bytes()+b'\n')
  output=a.out_dir/f'{variant}-must-not-exist.json.gz'
  cmd=[sys.executable,'-B',str(a.producer),'--source-word',str(bad),'--source-dir',str(a.source_dir),'--output',str(output),'--no-audit']
  r=subprocess.run(cmd,capture_output=True,text=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
  require(r.returncode!=0 and 'unauthorized compressed source SHA256' in r.stderr and not output.exists(),'compressed mutation was not rejected before output')
  checks.append(dict(variant=variant,control='compressed_source_byte_mutation',rejected=True,reason='unauthorized compressed source SHA256',no_output=True))
 fake=a.out_dir/'mutant-dependencies';fake.mkdir()
 for name in('word_patch.py','audit_local.py'):(fake/name).write_bytes((a.source_dir/name).read_bytes()+(b'\n' if name=='word_patch.py' else b''))
 output=a.out_dir/'dependency-must-not-exist.json.gz'
 r=subprocess.run([sys.executable,'-B',str(a.producer),'--source-word',str(a.source_base),'--source-dir',str(fake),'--output',str(output),'--no-audit'],capture_output=True,text=True,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
 require(r.returncode!=0 and 'unauthorized dependency SHA256: word_patch.py' in r.stderr and not output.exists(),'dependency mutation was not rejected before import/output')
 checks.append(dict(control='cleanup_dependency_mutation',rejected=True,reason='unauthorized dependency SHA256: word_patch.py',no_output=True))
 after={str(x):digest(x) for x in watched};require(before==after,'watched source changed')
 receipt=dict(status='PASS_SHARED_KERNEL_SOURCE_PIN_CONTROLS',checks=checks,pure_apply_preserves_both_inputs=True,before=before,after=after)
 (a.out_dir/'SOURCE-PIN-CONTROLS.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'status':receipt['status'],'controls':len(checks),'receipt':str(a.out_dir/'SOURCE-PIN-CONTROLS.json')}))
if __name__=='__main__':main()

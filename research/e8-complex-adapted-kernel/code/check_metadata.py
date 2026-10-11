"""Rebuild portability controls: two discovery floats may drift; exact data may not.
Usage: check_metadata.py PARENT_WORD OUT_JSON. Apache-2.0.
"""
import copy,gzip,json,subprocess,sys,tempfile
from pathlib import Path
assert __debug__
source=Path(sys.argv[1]);destination=Path(sys.argv[2]);script=Path(__file__).with_name('rebuild.py')
word=json.loads(gzip.decompress(source.read_bytes()))
keys=['complex_coarse_float','gain_percent_float']
cases=[('baseline',copy.deepcopy(word),True)]
for key in keys:
 w=copy.deepcopy(word);w['report'][key]+=2.1e-12;cases.append((key+'_drift',w,True))
for value,name in [(float('nan'),'nan'),(float('inf'),'infinite')]:
 w=copy.deepcopy(word);w['report'][keys[0]]=value;cases.append((name,w,False))
w=copy.deepcopy(word);w['A'][0][3]+=1;cases.append(('changed_exact_gate',w,False))
w=copy.deepcopy(word);w['report']['R']+=1;cases.append(('changed_register_count',w,False))
w=copy.deepcopy(word);w['report']['unexpected_exact_field']=1;cases.append(('unknown_report_field',w,False))
results=[];reference=None
with tempfile.TemporaryDirectory(prefix='complex-metadata-') as d:
 d=Path(d)
 for name,w,accept in cases:
  src=d/(name+'.json.gz');out=d/(name+'.json')
  src.write_bytes(gzip.compress(json.dumps(w,sort_keys=True).encode(),mtime=0))
  p=subprocess.run([sys.executable,'-B',str(script),str(src),str(out)],capture_output=True,text=True)
  assert (p.returncode==0)==accept,(name,p.stdout,p.stderr)
  if accept:
   actual=json.loads(out.read_text())
   if reference is None:reference=actual
   assert actual==reference,name
  else:assert not out.exists(),name
  results.append(dict(name=name,status='ACCEPTED_IDENTICAL_EXACT_REBUILD' if accept else 'REJECTED'))
destination.write_text(json.dumps(dict(status='PASS_DISCOVERY_METADATA_PORTABILITY',controls=results,canonical_word_sha256=reference['canonical_word_sha256']),indent=2)+'\n')
print('PASS_DISCOVERY_METADATA_PORTABILITY',len(results),'controls')

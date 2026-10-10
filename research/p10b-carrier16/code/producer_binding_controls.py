#!/usr/bin/env python3
"""Regression controls for the exact producer-content binding; Codex assisted."""
import copy,gzip,hashlib,json,sys,tempfile
from pathlib import Path
from finish import verify_regenerated_files
assert __debug__
sha=lambda b:hashlib.sha256(b).hexdigest()
with tempfile.TemporaryDirectory(prefix='producer-binding-') as tmp:
 root=Path(tmp);src=root/'source';work=root/'regen'
 (src/'bitword/selected/bit').mkdir(parents=True);(work/'final1').mkdir(parents=True)
 names=['graph_p10.json','kchron_p10.json','profile_p10.json','word_p10.json.gz','frames_p10.json.gz']
 files={};payload=b'{"complete": [1, 2, 3]}\n'*100
 for name in names:
  if name.endswith('.gz'):
   a=bytearray(gzip.compress(payload,compresslevel=9,mtime=0));a[9]=19;a=bytes(a)
   b=bytearray(gzip.compress(payload,compresslevel=1,mtime=0));b[9]=3;b=bytes(b)
   assert a!=b and gzip.decompress(a)==gzip.decompress(b)==payload
  else:a=b=payload
  (src/'bitword/selected/bit'/name).write_bytes(a);(work/'final1'/name).write_bytes(b)
  files[name]=dict(pinned=sha(a),rebuilt=sha(b),expanded=sha(payload))
 verify_regenerated_files(src,work,files)
 rejected=[]
 def reject(label,report):
  try:verify_regenerated_files(src,work,report)
  except (AssertionError,KeyError,FileNotFoundError,gzip.BadGzipFile,EOFError):rejected.append(label)
  else:raise AssertionError('Accepted invalid control '+label)
 for key in ('pinned','rebuilt','expanded'):
  bad=copy.deepcopy(files);bad[names[-1]][key]='0'*64;reject('forged-'+key,bad)
 bad=copy.deepcopy(files);del bad[names[0]];reject('missing-file',bad)
 bad=copy.deepcopy(files);bad['unexpected.json']=bad[names[0]];reject('extra-file',bad)
 for name in names:
  p=work/'final1'/name;original=p.read_bytes();wrong=payload+b' '
  replacement=gzip.compress(wrong,mtime=0) if name.endswith('.gz') else wrong
  p.write_bytes(replacement);bad=copy.deepcopy(files);bad[name]['rebuilt']=sha(replacement);bad[name]['expanded']=sha(wrong)
  reject('changed-complete-bytes-'+name,bad);p.write_bytes(original)
 verify_regenerated_files(src,work,files)
 result=dict(status='PASS_EXACT_PRODUCER_CONTENT_BINDING_CONTROLS',accepted='Different OS metadata and compression levels with identical complete expanded bytes',negative_controls=rejected)
 if len(sys.argv)>1:Path(sys.argv[1]).write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
 print(json.dumps(result,sort_keys=True))

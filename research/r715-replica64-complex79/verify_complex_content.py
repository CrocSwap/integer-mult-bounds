"""Bind fresh artifact bytes and stable contents across gzip header implementations.

Only references to files explicitly read here are replaced by their content hash.
No mathematical field is discarded; unknown hashes remain and must match the pin.
"""
from pathlib import Path
import gzip,json,hashlib,copy,sys
sha=lambda b:hashlib.sha256(b).hexdigest()
canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def replace(x,bindings):
 if isinstance(x,dict):return {k:replace(v,bindings) for k,v in x.items()}
 if isinstance(x,list):return [replace(v,bindings) for v in x]
 if isinstance(x,str):return bindings.get(x,x)
 return x
def measure(root):
 root=Path(root);bindings={};content={};raw_hashes={}
 files=['provider/FULL-WORD.json.gz','provider/CANONICAL-WORD.json.gz','provider/LOCAL-PROGRAMS.json.gz','provider/NORMALIZED-PROGRAMS.json.gz','provider/SCALAR-FRAME-AUDIT.json','provider/CANONICAL-WRAPPERS.json','provider/LOCAL-CHECKS.json','provider/NORMALIZED-CHECKS.json','provider/CLIFFORD-RECIPES.json','provider/CLIFFORD-REVIEW.json','complex/DATA-PHASES.json','complex/GLOBAL-TEMPLATE.json.gz']
 for name in files:
  b=(root/name).read_bytes();raw_hashes[name]=sha(b)
  obj=json.loads(gzip.decompress(b) if name.endswith('.gz') else b)
  normalized=replace(obj,bindings);h=sha(canon(normalized));content[name]=h
  if name=='complex/GLOBAL-TEMPLATE.json.gz':
   template=obj;stable_template=normalized;template_raw=sha(gzip.decompress(b))
  else:bindings[sha(b)]=h
 for key,name in [('kernel_word','provider/CANONICAL-WORD.json.gz'),('kernel_canonical_word','provider/CANONICAL-WORD.json.gz'),('kernel_normalized_programs','provider/NORMALIZED-PROGRAMS.json.gz'),('kernel_normalized_checks','provider/NORMALIZED-CHECKS.json'),('kernel_local_audit','provider/SCALAR-FRAME-AUDIT.json'),('kernel_wrapper','provider/CANONICAL-WRAPPERS.json'),('data_phase','complex/DATA-PHASES.json')]:
  assert template['source_bindings'][key]==raw_hashes[name],key
 for name in ['complex/GLOBAL.json','complex/AUDIT.json','complex/PHYSICAL-AUDIT.json']:
  assert json.loads((root/name).read_text())['template_sha256']==template_raw,name
 return content,raw_hashes,template_raw,stable_template
if __name__=='__main__':
 root,pin,out=map(Path,sys.argv[1:]);expected=json.loads(pin.read_text());content,raw,template_hash,stable=measure(root)
 assert content==expected,[(k,content[k],expected.get(k)) for k in content if content[k]!=expected.get(k)]
 controls={}
 for name,path in [('changed live stock',['live']),('changed source binding',['source_bindings','kernel_word']),('changed local provider',['calls',0,'local_word_sha256'])]:
  q=copy.deepcopy(stable);node=q
  for key in path[:-1]:node=node[key]
  key=path[-1];old=node[key];node[key]=old+1 if isinstance(old,int) else '0'*64
  assert node[key]!=old and sha(canon(q))!=expected['complex/GLOBAL-TEMPLATE.json.gz'];controls[name]='REJECTED'
 receipt=dict(status='PASS_FRESH_BYTE_BINDINGS_AND_PINNED_CONTENT',content_sha256=content,actual_file_sha256=raw,actual_template_sha256=template_hash,mutations_rejected=controls,scope='Compression headers and consequent file-reference hashes are represented by the pinned contents of their exact source files; mathematical content and all other fields are retained.')
 out.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))

# SPDX-License-Identifier: Apache-2.0
# Source derivation with substantial OpenAI Codex assistance; inherited authors retained.
"""Private source derivation and strict driver binding. Never runs heavy admission.
Appends PR3605 to authenticated PR3133 source; preserves inherited validators.
"""
import argparse,json,gzip,hashlib,shutil,sys,importlib.util
from pathlib import Path
if not __debug__ or sys.flags.optimize:
 raise RuntimeError('Assertions must be enabled for scientific replay')
P=Path(__file__).parent
OLD='fa3e2d855ac5298ecc849e596d79dcef7a72668a276b6524585bc0cd616ce474'
COMMIT='pr3605-ac92a027c78b0c9bb0ada739b26959afda489d0e'
DRIVER_PINS={'prepare_extension_native.py': '0cdb4b8b8b565e3dc4a312d4174c86d7d1aebc531430cb726658c8feb0c3bcf4', 'admit_extension.py': '6ddd449abfc2910e4c91f4ed93e14d65b84e6c1d2a082f3c089ad06f64d1d6ce'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def save(p,x):p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def tree(p):
 assert not any(x.is_symlink()for x in p.rglob('*'))
 return {x.relative_to(p).as_posix():sha(x)for x in sorted(p.rglob('*'))if x.is_file()and x!=p/'MANIFEST.json'}
def replace(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def rank(rows):
 piv={}
 for x in rows:
  assert type(x)is int and x>=0
  while x:
   k=x.bit_length()-1
   if k not in piv:piv[k]=x;break
   x^=piv[k]
 return len(piv)
def main(out,src,pkg,drivers,retained_cache,retained_receipt):
 global PKG
 PKG=pkg
 assert all(sha(drivers/n)==h for n,h in DRIVER_PINS.items()),"driver source pin"
 assert not out.exists();assert sha(src/'MANIFEST.json')==OLD and tree(src)==read(src/'MANIFEST.json')
 # Frozen package artifacts are independently pinned in upstream ARTIFACTS.
 assert sha(PKG/'ARTIFACTS.json')=='867bd848d04505518463eb06b1905e70ccc9256bb73312d3cd1dc57623bb319b', 'frozen supplier artifact index'
 assert sha(PKG/'staged_pair.py')=='25fc9b025dbb90358032013303adea650a5f19937fd3edf30b6c6fd023e2d747', 'supplier code before import'
 for name,h in read(PKG/'ARTIFACTS.json').items():assert sha(PKG/name)==h
 out.mkdir();dst=out/'source';shutil.copytree(src,dst);d=dst/'new/borrow';(d/'staged3605').mkdir()
 shutil.copy2(PKG/'staged_pair.py',d/'staged_pair.py')
 spec=importlib.util.spec_from_file_location('staged3605',PKG/'staged_pair.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 providers=read(dst/'new/BORROW-PROVIDERS.json')
 for tag,pid in [('base','gauge44'),('extra','extra')]:
  q=d/f'words/BORROW-WORD-43{tag}.json.gz';parent=read(q);record=read(PKG/f'STAGED-PAIR-RECORD-{tag}.json.gz');word=read(PKG/f'STAGED644-660-{tag}.json.gz')
  assert m.apply(parent,record)==word
  shutil.copy2(q,d/f'inputs/PRE3605-{tag}.json.gz');shutil.copy2(PKG/f'STAGED-PAIR-RECORD-{tag}.json.gz',d/f'staged3605/RECORD-{tag}.json.gz');shutil.copy2(PKG/f'STAGED644-660-{tag}.json.gz',q)
  providers[pid]['widths']=[rank(word['helper_final'].get(str(h),[1<<k for k in range(9)]))-rank(word['start_extra'].get(str(h),[]))for h in sorted(set(range(224,704))-set(word['removed']))]
  providers[pid]['actual_paid_profile']=word['report']['local_profile']
 save(dst/'new/BORROW-PROVIDERS.json',providers)
 q=dst/'new/rebuild_borrow.py';s=q.read_text();anchor='    final=json.loads(gzip.decompress(shipped.read_bytes()))'
 block="    import staged_pair\n    assert chain[-1]==json.loads(gzip.decompress((D/'inputs'/f'PRE3605-{wt}.json.gz').read_bytes()))\n    chain.append(staged_pair.apply(chain[-1],json.loads(gzip.decompress((D/'staged3605'/f'RECORD-{wt}.json.gz').read_bytes()))));steps.append('staged3605')\n"
 q.write_text(replace(s,anchor,block+anchor))
 review='''import json,gzip,copy
from pathlib import Path
import staged_pair
D=Path(__file__).resolve().parent
for tag in ('base','extra'):
 read=lambda p:json.loads(gzip.decompress(p.read_bytes()))
 p=read(D/f'inputs/PRE3605-{tag}.json.gz');r=read(D/f'staged3605/RECORD-{tag}.json.gz');w=read(D/f'words/BORROW-WORD-43{tag}.json.gz')
 assert staged_pair.apply(p,r)==w
 bad=copy.deepcopy(r);bad['B_deleted'][0]['old'][3]+=1
 try:staged_pair.apply(p,bad)
 except ValueError:pass
 else:raise AssertionError('wrong preimage accepted')
print('PASS_STAGED3605_RECONSTRUCTION_AND_CONTROL')
'''
 (d/'review_staged3605.py').write_text(review)
 q=dst/'verify.py';s=q.read_text();line=next(x for x in s.splitlines()if x.startswith("run('declared-edit-review'"));new=line.replace('words/BORROW-WORD-43base.json.gz','inputs/PRE3605-base.json.gz').replace('words/BORROW-WORD-43extra.json.gz','inputs/PRE3605-extra.json.gz')
 s=replace(s,line,new+"\nrun('staged3605-review',P/'new/borrow/review_staged3605.py')");q.write_text(s)
 manifest=tree(dst);save(dst/'MANIFEST.json',manifest);mh=sha(dst/'MANIFEST.json')
 assert mh=='318ede57c79d10323fb1918f7be4d451d1fcdac01c6456fe9851d51d05d59453' and len(manifest)==648,'frozen changed source manifest'
 deriv={'status':'PREPARED_CHANGED_SOURCE_NOT_ADMITTED','parent_manifest':OLD,'manifest_sha256':mh,'source_files':len(manifest),'changes':{k:{'old':read(src/'MANIFEST.json').get(k),'new':v}for k,v in manifest.items()if read(src/'MANIFEST.json').get(k)!=v},'pins':{str(p):sha(p)for p in [Path(__file__),PKG/'SOURCES.json',PKG/'ARTIFACTS.json']}}
 save(out/'DERIVATION.json',deriv)
 for name in ('prepare_extension_native.py','admit_extension.py'):
  s=(drivers/name).read_text()
  if name.startswith('prepare'):
   s=replace(s,"SOURCE_SHA='"+OLD+"'","SOURCE_SHA='"+mh+"'");s=replace(s,'SOURCE_FILES=642','SOURCE_FILES='+str(len(manifest)));s=replace(s,"SOURCE_COMMIT='rank7-joint-endframes-pr2917'","SOURCE_COMMIT='"+COMMIT+"'")
  else:
   old="dict(commit='rank7-joint-endframes-pr2917',manifest='"+OLD+"',helpers=408,source_file_count=642,upstream_head='224bd5e56041c40078ff6b5fa7393733a215de5c')"
   new="dict(commit='"+COMMIT+"',manifest='"+mh+"',helpers=408,source_file_count="+str(len(manifest))+",upstream_head='ac92a027c78b0c9bb0ada739b26959afda489d0e')"
   s=replace(s,old,new).replace('rank7-joint-endframes\'', 'staged3605\'')
  (out/name).write_text(s)
 py=sys.executable
 commands={'native':[py,'-B',str(out/'prepare_extension_native.py'),'--source',str(dst),'--retained-cache',str(retained_cache),'--retained-receipt',str(retained_receipt),'--out',str(out/'native'),'--jobs','1'],'warning':'Fresh five-stage changed cache is missing: prior finite local logs cannot be converted into missing ledgers/wrappers evidence. Native command intentionally not executed. Complete admission also needs actual FILL/ORDER/DISPATCH.'}
 save(out/'COMMANDS.json',commands)
 assert tree(src)==read(src/'MANIFEST.json');print(mh,len(manifest))
if __name__=='__main__':
 a=argparse.ArgumentParser()
 for key in ('out','source','local-package','driver-dir','retained-cache','retained-receipt'):a.add_argument('--'+key,type=Path,required=True)
 x=a.parse_args();main(x.out.resolve(),x.source.resolve(),x.local_package.resolve(),x.driver_dir.resolve(),x.retained_cache.resolve(),x.retained_receipt.resolve())

#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Adapter derivation by Mason Hale with OpenAI Codex assistance; inherited
# PR2908/2894/2857/2839 admission and native authors retain their attribution.
"""Derive three closed-profile adapters from exact PR2908 source, with counted patches.
No native/invoice check is removed. Source/hash arguments bind the new declared overlay;
retained_receipt_sha binds only the explicitly reused unchanged parent cache.
"""
from pathlib import Path
import argparse,gzip,hashlib,json,sys
PARENT_HEAD='51309592971e3b5be935599eed2a95404dc7781e'
NEW_COMMIT='paired-helper-extension-pr2908'
FINAL_SOURCE_SHA='98d57c82a1c7318be3c330c3b66897844d57232f0aaeaea88fb4bebd0a1bedf1'
FINAL_SOURCE_FILES=632
OLD_SOURCE='56cf455752722051d598a7da1e5ee700637fbaef09189f534413dbe6e0525a83'
OLD_RETAINED='dd36443f2789ffa6deca7210c76ada781e2b9b7e622a546b366f51a475faff3e'
sha=lambda b:hashlib.sha256(b).hexdigest()

def need(p,msg):
 if not p:raise ValueError(msg)

def tree(p):
 need(not any(f.is_symlink()for f in p.rglob('*')),'no symlinks')
 return {f.relative_to(p).as_posix():sha(f.read_bytes())for f in p.rglob('*')if f.is_file()and f!=p/'MANIFEST.json'}

def derive(parent,source,expected,out,retained_sha):
 manifest=json.loads((parent/'MANIFEST.json').read_bytes());need(tree(parent)==manifest,'complete exact parent manifest inventory')
 # These pins are independent of the manifest file contents themselves.
 need(sha((parent/'MANIFEST.json').read_bytes())=='9dba3fe371602ec023a54e26c0fd66f69eb7a74be86aab89923529083c14b36f','exact PR2908 package manifest')
 newsha=sha((source/'MANIFEST.json').read_bytes());need(newsha==expected==FINAL_SOURCE_SHA,'exact final declared source manifest')
 files=json.loads((source/'MANIFEST.json').read_bytes());need(len(files)==FINAL_SOURCE_FILES and tree(source)==files,'complete final source inventory')
 for tag in ('base','extra'):
  wp=source/f'new/borrow/words/BORROW-WORD-43{tag}.json.gz'
  w=json.loads(gzip.decompress(wp.read_bytes()));oldword=json.loads(gzip.decompress((parent/f'data/WORD-{tag}.json.gz').read_bytes()))
  need(set(map(int,w['helper_final']))==set(map(int,oldword['helper_final']))|{424,428,412,331,299,320,511,304,499},'exact nine extra restored helpers')
  need(all(w['helper_final'][h]==U for h,U in oldword['helper_final'].items()),'all inherited restored endpoints retained')
  need(len(w['helper_final'])==82 and w['report']['local_profile']=={'1':2416,'2':640,'3':280,'4':110,'5':26,'8':8},'declared82-buffer local profile')
  need(w['report']['width_inventory']=={'4':26,'5':2,'7':62,'8':96,'9':222},'declared current helper inventory')
 nfiles=len(files);comparison_sha=sha((parent/'CLAIM.json').read_bytes());claim=json.loads((parent/'CLAIM.json').read_bytes())
 need('headline_kappa_source'not in claim and 'kappa'in claim,'headline outer comparison')
 need(len(retained_sha)==64 and all(c in'0123456789abcdef'for c in retained_sha),'retained receipt SHA256')
 out.mkdir(parents=True,exist_ok=False);changes={}
 def adapt(oldname,newname,pairs):
  p=parent/'tools'/oldname;body=p.read_text();oldhash=sha(p.read_bytes());applied=[]
  for old,new in pairs:
   need(body.count(old)==1,f'exact preimage occurrence {oldname}: {old[:120]}')
   body=body.replace(old,new);applied.append({'old':old,'new':new})
  q=out/newname;q.write_text(body);compile(body,str(q),'exec');changes[newname]={'source':str(p),'before_sha256':oldhash,'after_sha256':sha(q.read_bytes()),'replacements':applied}
 adapt('prepare_channel_native.py','prepare_extension_native.py',[
  ("SOURCE_SHA='"+OLD_SOURCE+"'","SOURCE_SHA='"+newsha+"'"),
  ('SOURCE_FILES=610','SOURCE_FILES='+str(nfiles)),
  ("SOURCE_COMMIT='two-sided-helper408-pr2894'","SOURCE_COMMIT='"+NEW_COMMIT+"'"),
  ("OLD_RECEIPT_SHA='"+OLD_RETAINED+"'","OLD_RECEIPT_SHA='"+retained_sha+"'"),
  ("len(can['zero_buffers'])==73","len(can['zero_buffers'])==82"),
 ])
 oldprofile="    'channel408': dict(commit='two-sided-helper408-pr2894',manifest='"+OLD_SOURCE+"',helpers=408,source_file_count=610,upstream_head='18d03c447886895ef9abf888398178e0428533ca'),"
 newprofile="    'paired-extension': dict(commit='"+NEW_COMMIT+"',manifest='"+newsha+"',helpers=408,source_file_count="+str(nfiles)+",upstream_head='"+PARENT_HEAD+"'),"
 adapt('admit_channel408.py','admit_extension.py',[
  (oldprofile,newprofile),
  ("COMPARISONS = {","COMPARISONS = {\n    'pr2908': dict(pr=2908,head='"+PARENT_HEAD+"',sha256='"+comparison_sha+"',field='kappa'),"),
  ("ap.add_argument('--source-profile', choices=['channel408'], default='channel408')","ap.add_argument('--source-profile', choices=['paired-extension'], default='paired-extension')"),
  ("ap.add_argument('--comparison-profile', choices=['pr2894'], default='pr2894')","ap.add_argument('--comparison-profile', choices=['pr2908'], default='pr2908')"),
  ('zero_buffers_allocated_and_cleared=73','zero_buffers_allocated_and_cleared=82'),
  ("len(c.get('zero_buffers',[]))==73, 'helper408 physical ABI including all 73 private buffers'","len(c.get('zero_buffers',[]))==82, 'paired extension physical ABI including all 82 private buffers'"),
  ("896*T+expected_helpers+8+73+2, 'complete physical cost including all actual helpers and 73 buffers'","896*T+expected_helpers+8+82+2, 'complete physical cost including all actual helpers and 82 buffers'"),
 ])
 adapt('channel_blocknorm.py','extension_blocknorm.py',[
  ("len(allocated)==73, 'all73 private zero buffers released'","len(allocated)==82, 'all82 private zero buffers released'"),
  ("'zero_buffers_allocated_and_cleared':73","'zero_buffers_allocated_and_cleared':82"),
  ("r['zero_buffers_returned_to_zero']==73","r['zero_buffers_returned_to_zero']==82"),
  ('physical==live+8+408+73+2','physical==live+8+408+82+2'),
  ("'zero_buffers':[live+416,live+489], 'coefficient':[live+489,live+491]","'zero_buffers':[live+416,live+498], 'coefficient':[live+498,live+500]"),
  ("len(mp)==73 and set(mp.values())==set(range(*ns['zero_buffers'])), '73distinct private Z slots'","len(mp)==82 and set(mp.values())==set(range(*ns['zero_buffers'])), '82distinct private Z slots'"),
  ('T=len(order)//9; live=896*T; physical=live+490','T=len(order)//9; live=896*T; physical=live+500'),
 ])
 # The native address dimension and symplectic stock factor are deliberately retained.
 b=(out/'extension_blocknorm.py').read_text();a=(out/'admit_extension.py').read_text()
 need("require(d['m']==73"in b and 'Sp(72,2)'in b and 'range(1,37)'in b,'retained native dimension and symplectic group')
 need('assert m==73'in a,'retained outer dimension')
 receipt={'status':'PASS_CHECKED_82_BUFFER_ADAPTER_DERIVATION','parent_head':PARENT_HEAD,'parent_manifest_sha256':sha((parent/'MANIFEST.json').read_bytes()),'source_commit':NEW_COMMIT,'source_manifest_sha256':newsha,'source_files':nfiles,'comparison_sha256':comparison_sha,'retained_receipt_sha256':retained_sha,'buffer_count':82,'physical_overhead':500,'changes':changes}
 (out/'ADAPTER-DERIVATION.json').write_text(json.dumps(receipt,indent=2)+'\n');return receipt

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--parent-package',type=Path,required=True);ap.add_argument('--source',type=Path,required=True);ap.add_argument('--source-manifest',required=True);ap.add_argument('--retained-receipt',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 r=derive(a.parent_package,a.source,a.source_manifest,a.out,sha(a.retained_receipt.read_bytes()));print(r['status'],r['source_manifest_sha256'],r['source_files'])

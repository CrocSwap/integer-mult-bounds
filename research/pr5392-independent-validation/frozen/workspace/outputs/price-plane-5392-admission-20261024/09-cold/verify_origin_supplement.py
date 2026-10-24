#!/usr/bin/env python3
"""Git-free validation of copied original-source provenance, never mathematics.

Prepared for Chris R/Clear1nsight with substantial OpenAI Codex assistance.
Apache-2.0; original source notices remain intact.
"""
from pathlib import Path
import argparse,base64,hashlib,json

def need(ok,why):
 if not ok:raise ValueError(why)
def oid(kind,raw):return hashlib.sha1(kind.encode()+b' '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def entries(raw):
 out={};pos=0
 while pos<len(raw):
  space=raw.index(b' ',pos);nul=raw.index(b'\0',space);name=raw[space+1:nul].decode();need(name not in out,'duplicate tree member');out[name]=(raw[pos:space].decode(),raw[nul+1:nul+21].hex());pos=nul+21
 need(pos==len(raw),'tree boundary');return out

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--capsule',type=Path,required=True);ap.add_argument('--receipt',type=Path,required=True);a=ap.parse_args();root=a.capsule.resolve();p=json.loads(a.receipt.read_text());need(hashlib.sha256((root/'IMMUTABLE-MANIFEST.json').read_bytes()).hexdigest()==p['scientific_capsule_manifest_sha256'],'capsule digest');objects={}
 for obj,row in p['objects'].items():
  raw=base64.b64decode(row['base64'],validate=True);need(len(raw)==row['bytes'] and oid(row['kind'],raw)==obj,'raw origin object hash');objects[obj]=(row['kind'],raw)
 source_path='snapshot/research/native-transpose-owned/SOURCES.json';capsule_manifest=json.loads((root/'IMMUTABLE-MANIFEST.json').read_text());source_row=next(r for r in capsule_manifest['rows'] if r['capsule_path']==source_path);need(hashlib.sha256((root/source_path).read_bytes()).hexdigest()==source_row['sha256'],'source declarations match frozen manifest');manifest=json.loads((root/source_path).read_text());declared={r['path']:r for r in manifest['files'] if 'source_pin' in r};need(set(declared)=={r['path'] for r in p['rows']},'complete original origin inventory')
 def resolve(commit,path,chain):
  kind,raw=objects[commit];need(kind=='commit','origin commit kind');tree=raw.splitlines()[0].split()[1].decode();parts=path.split('/');need(not path.startswith('/') and all(q not in ('','.','..') for q in parts) and len(parts)==len(chain),'canonical origin path')
  for i,part in enumerate(parts):
   need(tree==chain[i],'origin tree chain');kind,raw=objects[tree];need(kind=='tree','origin tree kind');mode,obj=entries(raw)[part]
   if i+1<len(parts):need(mode=='40000','origin directory mode');tree=obj
   else:need(mode in ('100644','100755'),'origin regular blob')
  return obj
 for row in p['rows']:
  decl=declared[row['path']];need(decl['pin']==row['publication_pin'] and decl['source_pin']==row['original_pin'],'unchanged declared original/publication pin');need(row['publication_pin']=='head:'+row['publication_commit']+':'+row['publication_path'] and row['original_pin']=='head:'+row['original_commit']+':'+row['original_path'],'pin parsing identity')
  pub=resolve(row['publication_commit'],row['publication_path'],row['publication_tree_chain']);orig=resolve(row['original_commit'],row['original_path'],row['original_tree_chain']);need(pub==orig==decl['git_blob']==row['git_blob'],'original/vendor/blob identity');f=root/row['capsule_path'];need(f.resolve().is_relative_to(root) and not f.is_symlink(),'payload confinement');raw=f.read_bytes();need(oid('blob',raw)==orig and hashlib.sha256(raw).hexdigest()==decl['sha256']==row['sha256'],'working/original/vendor bytes')
 print(json.dumps({'status':'PASS_GIT_FREE_ALL_ORIGINAL_SOURCE_VENDOR_BINDINGS','rows':len(p['rows']),'raw_objects':len(objects),'origin_commits':sorted({r['original_commit'] for r in p['rows']}),'scope':'Original copied-byte provenance only; no canonical-ancestor or mathematical claim'}))
if __name__=='__main__':main()

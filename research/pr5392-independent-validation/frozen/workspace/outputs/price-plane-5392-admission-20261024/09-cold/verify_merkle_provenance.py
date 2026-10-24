#!/usr/bin/env python3
"""Verify frozen source provenance using only included raw Git objects and bytes.

Prepared for Chris R / Clear1nsight with substantial OpenAI Codex assistance.
Apache-2.0. No candidate scientific module is imported or executed.
"""
from pathlib import Path
import argparse,base64,hashlib,json

def need(ok,why):
 if not ok:raise ValueError(why)
def oid(kind,raw):return hashlib.sha1(kind.encode()+b' '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def entries(raw):
 rows={};pos=0
 while pos<len(raw):
  space=raw.index(b' ',pos);nul=raw.index(b'\0',space);name=raw[space+1:nul].decode();need(name not in rows,'duplicate tree name')
  rows[name]=(raw[pos:space].decode(),raw[nul+1:nul+21].hex());pos=nul+21
 need(pos==len(raw),'tree parse boundary');return rows

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--capsule',type=Path,required=True);ap.add_argument('--receipt',type=Path,required=True);args=ap.parse_args()
 root=args.capsule.resolve();proof=json.loads(args.receipt.read_text());manifest=root/'IMMUTABLE-MANIFEST.json';need(hashlib.sha256(manifest.read_bytes()).hexdigest()==proof['capsule_manifest_sha256'],'capsule manifest digest')
 declared=json.loads(manifest.read_text());need(proof['candidate_head']==declared['candidate_head'] and proof['canonical_main']==declared['canonical_main'],'head/base agreement with frozen manifest')
 expected={r['capsule_path']:r for r in declared['rows']};need(len(expected)==len(declared['rows']),'duplicate declared payload path')
 need(len(proof['rows'])==len(expected) and {r['capsule_path'] for r in proof['rows']}==set(expected),'complete manifest row inventory')
 for r in proof['rows']:
  need(all(r.get(k)==v for k,v in expected[r['capsule_path']].items()),'proof row agrees with frozen manifest')
 objs={}
 for obj,record in proof['commit_and_tree_objects'].items():
  raw=base64.b64decode(record['base64'],validate=True);need(len(raw)==record['bytes'] and oid(record['kind'],raw)==obj,'raw object authentication '+obj);objs[obj]=(record['kind'],raw)
 for row in proof['rows']:
  kind,commit=objs[row['source_commit']];need(kind=='commit','commit kind');tree=commit.splitlines()[0].split()[1].decode();parts=row['path'].split('/');need(not row['path'].startswith('/') and all(p not in ('','.','..') for p in parts),'canonical source path')
  need(len(parts)==len(row['tree_chain']),'chain length')
  for i,part in enumerate(parts):
   need(row['tree_chain'][i]==tree,'chained tree identity');kind,raw=objs[tree];need(kind=='tree','tree kind');mode,obj=entries(raw)[part]
   if i+1<len(parts):need(mode=='40000','directory mode');tree=obj
   else:need(mode in ('100644','100755') and obj==row['git_blob'] and ('mode' not in row or row['mode']==mode),'terminal blob identity/mode')
  p=root/row['capsule_path'];need(p.resolve().is_relative_to(root) and not p.is_symlink(),'local payload confinement');data=p.read_bytes();need(oid('blob',data)==obj and hashlib.sha256(data).hexdigest()==row['sha256'],'payload binding '+row['path'])
 def ancestor(older,newer):
  todo=[newer];seen=set()
  while todo:
   current=todo.pop()
   if current==older:return True
   if current in seen:continue
   seen.add(current)
   if current not in objs:continue
   kind,raw=objs[current];need(kind=='commit','ancestry node kind')
   todo.extend(x.split()[1].decode() for x in raw.splitlines() if x.startswith(b'parent '))
  return False
 need(ancestor(proof['canonical_main'],proof['candidate_head']),'canonical is actual raw candidate ancestor')
 for row in proof['rows']:need(ancestor(row['source_commit'],proof['candidate_head']),'source pin is actual publication ancestor')
 print(json.dumps({'status':'PASS_GIT_FREE_MERKLE_SOURCE_BINDINGS','candidate_head':proof['candidate_head'],'canonical_main':proof['canonical_main'],'rows':len(proof['rows']),'raw_objects':len(objs),'scope':'Cryptographic byte provenance and raw-ancestry inclusion only; no mathematical replay/admission'}))
if __name__=='__main__':main()

# SPDX-License-Identifier: Apache-2.0
"""Build a source-bound four-kernel supplier overlay without changing PR2833.
Yiyang (@Lyy-iiis), with substantial OpenAI Codex assistance.
Native, scalar, Clifford, all-column, owner and outer validators are retained.
"""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import argparse,copy,gzip,hashlib,json,shutil,types
UPSTREAM_MANIFEST='c8ec4d1b7be08d2ad30730a07392ad9cb6d0222f2c35bef43c9a80a39b16e41f'
GROUPS=[478,460,462,480]
# Final source hashes are frozen before the first build.
GENERATOR_SHA='b3241527e6c136dc4b54975ef401c49d452bd6159fb99030accaf095c8fbd3ed'
REVIEW_SHA='5b323e50fb5a10ac088472b3e085b54d7d2ae3a29f8552ff44b788a984eb97d1'
def need(ok,why):
 if not ok:raise ValueError(why)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sem(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def read(p):
 p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def write(p,v):p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def tree(p):
 need(not list(p.rglob('__pycache__')) and not list(p.rglob('*.pyc')),'no source bytecode or cache folders')
 out={}
 for f in sorted(p.rglob('*')):
  need(not f.is_symlink(),'no source symlinks')
  if f.is_file() and f!=p/'MANIFEST.json':out[f.relative_to(p).as_posix()]=sha(f)
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--generator',type=Path,required=True);ap.add_argument('--review',type=Path,required=True);ap.add_argument('--candidate-dir',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 need(not sys.flags.optimize,'assertions required');source=a.source.resolve();out=a.out.resolve()
 need(sha(source/'MANIFEST.json')==UPSTREAM_MANIFEST and tree(source)==read(source/'MANIFEST.json'),'exact PR2833 source inventory')
 need(sha(a.generator)==GENERATOR_SHA and sha(a.review)==REVIEW_SHA,'exact new producer and independent review source')
 need(not out.exists() and not out.is_relative_to(source),'fresh external overlay');shutil.copytree(source,out)
 gen=types.ModuleType('shared_kernel');exec(compile(a.generator.read_bytes(),str(a.generator),'exec'),gen.__dict__)
 auditor=types.ModuleType('independent_frames');apath=source/'new/borrow/audit_local.py';exec(compile(apath.read_bytes(),str(apath),'exec'),auditor.__dict__)
 # Independently audited literal words are shipped byte-for-byte. The pure
 # source-bound producer must reconstruct every decoded field from PR2833.
 providers=read(source/'new/BORROW-PROVIDERS.json');records={}
 for tag,pid in [('base','gauge44'),('extra','extra')]:
  src=source/('new/borrow/words/BORROW-WORD-43'+tag+'.json.gz');target=a.candidate_dir/('WORD-'+tag+'.json.gz');old=read(src);new=read(target);derived,ledger=gen.apply(old,GROUPS)
  need(derived==new,'complete producer reconstruction '+tag)
  need(set(k for k in old if old[k]!=new[k])=={'A','compensation','start_extra','report','cleanup'},'exact changed sections')
  need(new['report']['local_profile']=={'1':2394,'2':642,'3':266,'4':128,'5':26,'8':8},'complete per-call paid profile')
  need(new['report']['width_inventory']=={'4':26,'5':2,'7':62,'8':84,'9':234},'complete helper inventory')
  live=sorted(set(range(224,704))-set(new['removed']));need(len(live)==408,'unchanged helper identities')
  widths=[]
  for r in live:
   end=auditor.basis(new['helper_final'].get(str(r),[256,128,64,32,16,8,4,2,1]));start=auditor.basis(new['start_extra'].get(str(r),[]));widths.append(len(end)-len(start))
  need(len(new['warps'])==len(old['warps']) and new['helper_final']==old['helper_final'] and new['removed']==old['removed'],'all phase and buffer ABI fields unchanged')
  providers[pid]=dict(widths=widths,actual_paid_profile=new['report']['local_profile'])
  shutil.copy2(target,out/('new/borrow/words/BORROW-WORD-43'+tag+'.json.gz'))
  shutil.copy2(src,out/('new/borrow/inputs/PR2833-WORD-'+tag+'.json.gz'))
  rec=dict(groups=GROUPS,source_word_sha256=sha(src),source_canonical_sha256=sem(old),candidate_word_sha256=sha(target),candidate_canonical_sha256=sem(new),generator_sha256=GENERATOR_SHA,ledger=ledger)
  write(out/('new/borrow/inputs/shared_kernel_43'+tag+'.json'),rec);records[tag]=rec
 shutil.copy2(a.generator,out/'new/borrow/shared_kernel.py');shutil.copy2(a.review,out/'new/borrow/shared_kernel_review.py');write(out/'new/BORROW-PROVIDERS.json',providers)
 patches=[]
 def patch(name,old,new):
  p=out/name;before=sha(p);body=p.read_text();need(body.count(old)==1,'exact overlay preimage '+name);p.write_text(body.replace(old,new));patches.append(dict(path=name,before_sha256=before,after_sha256=sha(p),old=old,new=new))
 anchor='    final=json.loads(gzip.decompress(shipped.read_bytes()))'
 block='''    # Four disjoint staged compensation kernels, after the complete pinned
    # PR2833 derivation. Every previous state stays in the audit chain.
    sf_=D/'inputs'/f'shared_kernel_43{wt}.json'
    if sf_.exists():
        import shared_kernel
        shared_patch=json.loads(sf_.read_text());previous_shared=chain[-1]
        canonical=lambda z:hashlib.sha256(json.dumps(z,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        assert shared_patch['groups']==[478,460,462,480]
        assert canonical(previous_shared)==shared_patch['source_canonical_sha256']
        shared_word,shared_ledger=shared_kernel.apply(previous_shared,shared_patch['groups'])
        assert canonical(shared_word)==shared_patch['candidate_canonical_sha256']
        assert json.loads(json.dumps(shared_ledger))==shared_patch['ledger']
        assert set(k_ for k_ in previous_shared if previous_shared[k_]!=shared_word[k_])=={'A','compensation','start_extra','report','cleanup'}
        stripped_shared=json.loads(json.dumps(shared_word));stripped_shared['A']=stripped_shared['A'][stripped_shared['prelude_events']:]
        assert shared_word['cleanup']==word_patch.derive_cleanup(stripped_shared,word_patch.restored_of(shared_word))
        chain.append(shared_word);steps.append('shared-four-kernel')
'''+anchor
 patch('new/rebuild_borrow.py',anchor,block)
 anchor2="run('rebuild-borrow-words',P/'new/rebuild_borrow.py')"
 block2=anchor2+"\nrun('shared-kernel-independent-review',P/'new/borrow/shared_kernel_review.py','--source-dir',P/'new/borrow','--source-base',P/'new/borrow/inputs/PR2833-WORD-base.json.gz','--source-extra',P/'new/borrow/inputs/PR2833-WORD-extra.json.gz','--candidate-base',P/'new/borrow/words/BORROW-WORD-43base.json.gz','--candidate-extra',P/'new/borrow/words/BORROW-WORD-43extra.json.gz','--out-dir',work/'shared-kernel-independent-review')"
 patch('verify.py',anchor2,block2)
 before=read(source/'MANIFEST.json');after=tree(out);write(out/'MANIFEST.json',after)
 change={p:dict(before_sha256=before.get(p),after_sha256=after.get(p)) for p in sorted(set(before)|set(after)) if before.get(p)!=after.get(p)}
 expected={'new/borrow/words/BORROW-WORD-43base.json.gz','new/borrow/words/BORROW-WORD-43extra.json.gz','new/borrow/inputs/PR2833-WORD-base.json.gz','new/borrow/inputs/PR2833-WORD-extra.json.gz','new/borrow/inputs/shared_kernel_43base.json','new/borrow/inputs/shared_kernel_43extra.json','new/borrow/shared_kernel.py','new/borrow/shared_kernel_review.py','new/BORROW-PROVIDERS.json','new/rebuild_borrow.py','verify.py'}
 need(set(change)==expected,'exact overlay change allowlist');need(tree(source)==before,'original source remained byte-exact')
 receipt=dict(status='PASS_SOURCE_BOUND_FOUR_KERNEL_OVERLAY_DERIVATION',upstream_manifest_sha256=UPSTREAM_MANIFEST,derived_manifest_sha256=sha(out/'MANIFEST.json'),source_file_count=len(after),builder_sha256=sha(Path(__file__)),changes=change,patches=patches,words=records,scope='Exact source overlay construction only. Full native and owner/controller/outer admission remain separate; all inherited validators are retained and an independent kernel review is added.')
 write(out.parent/(out.name+'-DERIVATION.json'),receipt);print(json.dumps({k:receipt[k] for k in ['status','derived_manifest_sha256','source_file_count']},sort_keys=True))
if __name__=='__main__':main()

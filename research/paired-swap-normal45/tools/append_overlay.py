# Append a source-bound word-edit stage; preserve every prior stage and producer.
from pathlib import Path
import argparse,hashlib,json,gzip,shutil,sys,types,re

def need(v,m):
 if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def write(p,x):p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
def tree(p):return {f.relative_to(p).as_posix():sha(f)for f in sorted(p.rglob('*'))if f.is_file()and f!=p/'MANIFEST.json'}
def sem(w):return hashlib.sha256(json.dumps(w,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--source-manifest',required=True);ap.add_argument('--words',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--stage',required=True);ap.add_argument('--deleted-b-indices',type=Path);a=ap.parse_args()
 need(re.fullmatch('[a-z][a-z0-9-]*',a.stage),'safe stage name');src=a.source.resolve();out=a.out.resolve()
 bdeletions=read(a.deleted_b_indices) if a.deleted_b_indices else {'base':[],'extra':[]}
 oldtree=read(src/'MANIFEST.json');need(sha(src/'MANIFEST.json')==a.source_manifest and tree(src)==oldtree,'exact source inventory');need(not out.exists(),'fresh output only')
 need(not any(p.is_symlink()for p in src.rglob('*')),'no source symlinks');shutil.copytree(src,out)
 prod=out/'new/borrow/wordedit.py';sys.path.insert(0,str(prod.parent));mod=types.ModuleType('append_wordedit');mod.__file__=str(prod);exec(compile(prod.read_bytes(),str(prod),'exec'),mod.__dict__)
 providers=read(src/'new/BORROW-PROVIDERS.json');records={};buffers=set();newfiles=set();allowed={'A','B','restore','compensation','start_extra','report','cleanup','initial_corrections','helper_final','warps'}
 for tag,pid in [('base','gauge44'),('extra','extra')]:
  rel=f'new/borrow/words/BORROW-WORD-43{tag}.json.gz';prev=read(src/rel);target=a.words/f'WORD-{tag}.json.gz';new=read(target)
  need(prev!=new,'changed word '+tag);changed={k for k in prev if prev[k]!=new[k]};need(changed<=allowed,'changed key set')
  need(new['removed']==prev['removed']and len(new['warps'])==len(prev['warps']),'fixed live helpers and warp operators')
  deleted=bdeletions[tag];need(deleted==sorted(set(deleted)) and all(type(i)is int and 0<=i<len(prev['B']) for i in deleted),'exact B deletion indices')
  need(new['B']==[g for i,g in enumerate(prev['B']) if i not in set(deleted)],'only explicitly listed B deletions')
  need(all(x[1:]==y[1:] and y[0]==x[0]-sum(i<x[0] for i in deleted) for x,y in zip(prev['warps'],new['warps'])),'unchanged warp operators/frames/lenders with exact deleted-gate position transport')
  need(all(new['helper_final'].get(h)==u for h,u in prev['helper_final'].items()),'inherited restored endpoints retained')
  spec=mod.make_spec(prev,new);need(mod.apply_spec(prev,spec)==new,'pure producer reconstruction');need(new['cleanup']==mod.derive_cleanup(new),'actual inverse cleanup')
  providers[pid]={'widths':[len(new['helper_final'].get(str(h),[0]*9))-len(new['start_extra'].get(str(h),[]))for h in sorted(set(range(224,704))-set(new['removed']))],'actual_paid_profile':new['report']['local_profile']}
  need(len(providers[pid]['widths'])==408,'all helper roles');buffers.add(len(new['helper_final']));shutil.copyfile(target,out/rel)
  inputrel=f'new/borrow/inputs/{a.stage}-43{tag}.json';rec={'stage':a.stage,'source_canonical_sha256':sem(prev),'candidate_canonical_sha256':sem(new),'source_word_sha256':sha(src/rel),'candidate_word_sha256':sha(target),'producer_sha256':sha(prod),'changed_sections':sorted(changed),'buffers':len(new['helper_final']),'deleted_B_indices':deleted,'spec':spec};write(out/inputrel,rec);newfiles.add(inputrel);records[tag]={k:v for k,v in rec.items()if k!='spec'}
 need(len(buffers)==1,'same buffer count');write(out/'new/BORROW-PROVIDERS.json',providers)
 anchor='    final=json.loads(gzip.decompress(shipped.read_bytes()))';f=out/'new/rebuild_borrow.py';body=f.read_text(encoding='utf-8');need(body.count(anchor)==1,'exact rebuild insertion point')
 block=f'''    # Additional source-bound stage: {a.stage}. All prior stages retained.
    appended_stage_file=D/'inputs'/f'{a.stage}-43{{wt}}.json'
    if appended_stage_file.exists():
        import wordedit
        appended_record=json.loads(appended_stage_file.read_text())
        appended_previous=chain[-1]
        appended_canon=lambda z:hashlib.sha256(json.dumps(z,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        assert appended_canon(appended_previous)==appended_record['source_canonical_sha256']
        appended_word=wordedit.apply_spec(appended_previous,appended_record['spec'])
        assert appended_canon(appended_word)==appended_record['candidate_canonical_sha256']
        assert appended_word['cleanup']==wordedit.derive_cleanup(appended_word)
        assert appended_word['removed']==appended_previous['removed']
        appended_deleted=appended_record['deleted_B_indices']
        assert appended_deleted==sorted(set(appended_deleted))
        assert all(type(i_) is int and 0<=i_<len(appended_previous['B']) for i_ in appended_deleted)
        assert appended_word['B']==[g_ for i_,g_ in enumerate(appended_previous['B']) if i_ not in set(appended_deleted)]
        assert len(appended_previous['warps'])==len(appended_word['warps'])
        assert all(x_[1:]==y_[1:] and y_[0]==x_[0]-sum(i_<x_[0] for i_ in appended_deleted) for x_,y_ in zip(appended_previous['warps'],appended_word['warps']))
        assert all(appended_word['helper_final'].get(h_)==U_ for h_,U_ in appended_previous['helper_final'].items())
        assert len(appended_word['helper_final'])==appended_record['buffers']
        chain.append(appended_word);steps.append(appended_record['stage'])
'''
 f.write_text(body.replace(anchor,block+anchor),encoding='utf-8',newline='\n')
 newtree=tree(out);write(out/'MANIFEST.json',newtree);changed={r for r in oldtree.keys()|newtree.keys()if oldtree.get(r)!=newtree.get(r)}
 need(changed==newfiles|{'new/rebuild_borrow.py','new/BORROW-PROVIDERS.json','new/borrow/words/BORROW-WORD-43base.json.gz','new/borrow/words/BORROW-WORD-43extra.json.gz'},'exact overlay allowlist');need(tree(src)==oldtree,'source unchanged')
 receipt={'status':'PASS_ADDITIONAL_SOURCE_BOUND_WORD_STAGE','stage':a.stage,'source_manifest_sha256':a.source_manifest,'derived_manifest_sha256':sha(out/'MANIFEST.json'),'file_count':len(newtree),'buffers':buffers.pop(),'changes':sorted(changed),'words':records,'producer_sha256':sha(prod)};write(out.parent/(out.name+'-DERIVATION.json'),receipt);print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()

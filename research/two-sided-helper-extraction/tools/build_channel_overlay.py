# SPDX-License-Identifier: Apache-2.0
"""Append the declared two-sided helper408 stage to immutable PR2894 source."""
import argparse,gzip,hashlib,json,shutil,sys,types
from pathlib import Path
sys.dont_write_bytecode=True
PARENT='4da246899e2c509dd8c6e5af34905c6124ca17671b188e11ac37e36adf449504'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def save(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def tree(p):
 assert not any(f.is_symlink() for f in p.rglob('*'))
 return {f.relative_to(p).as_posix():sha(f) for f in sorted(p.rglob('*')) if f.is_file() and f!=p/'MANIFEST.json'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--local-package',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();src=a.source.resolve();out=a.out.resolve();p=a.local_package.resolve()
 assert __debug__ and not out.exists() and not out.is_relative_to(src)
 assert sha(src/'MANIFEST.json')==PARENT and tree(src)==read(src/'MANIFEST.json')
 pins=read(p/'PINS.json');assert all(sha(p/n)==h for n,h in pins.items())
 shutil.copytree(src,out);local=out/'new/borrow/channel408';local.mkdir()
 for n in ['PINS.json','verify.py','extract.py','structure.py',*pins]:
  dest=local/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p/n,dest)
 shutil.copy2(p/'extract.py',out/'new/borrow/channel_extract.py')
 prov=read(src/'new/BORROW-PROVIDERS.json');records={}
 for tag,pid in [('base','gauge44'),('extra','extra')]:
  q=out/f'new/borrow/words/BORROW-WORD-43{tag}.json.gz';assert q.read_bytes()==(p/f'data/PARENT-{tag}.json.gz').read_bytes()
  shutil.copy2(q,out/f'new/borrow/inputs/PM-WORD-{tag}.json.gz');shutil.copy2(p/f'data/WORD-{tag}.json.gz',q)
  w=read(q);hs=sorted(set(range(224,704))-set(w['removed']))
  prov[pid]={'widths':[len(w['helper_final'].get(str(h),[0]*9))-len(w['start_extra'].get(str(h),[])) for h in hs],'actual_paid_profile':w['report']['local_profile']}
  records[tag]={'parent_sha256':sha(p/f'data/PARENT-{tag}.json.gz'),'word_sha256':sha(q)}
 save(out/'new/BORROW-PROVIDERS.json',prov)
 path=out/'new/rebuild_borrow.py';text=path.read_text();anchor="    final=json.loads(gzip.decompress(shipped.read_bytes()))"
 assert text.count(anchor)==1
 block="""    # Explicit two-sided input/output change; the extra cold helper is charged.
    import channel_extract
    channel_parent=json.loads(gzip.decompress((D/'inputs'/f'PM-WORD-{wt}.json.gz').read_bytes()))
    assert chain[-1]==channel_parent
    channel_transform=json.loads((D/'channel408/data/TRANSFORM.json').read_text())
    channel_word=channel_extract.apply(chain[-1],channel_transform)
    assert set(k_ for k_ in chain[-1] if chain[-1][k_]!=channel_word[k_])==channel_extract.ALLOWED
    chain.append(channel_word);steps.append('two-sided-helper408')
"""
 path.write_text(text.replace(anchor,block+anchor))
 path=out/'verify.py';text=path.read_text();line=next(s for s in text.splitlines() if s.startswith("run('preload-move-independent-review'"))
 new=line.replace("P/'new/borrow/words/BORROW-WORD-43base.json.gz'","P/'new/borrow/inputs/PM-WORD-base.json.gz'").replace("P/'new/borrow/words/BORROW-WORD-43extra.json.gz'","P/'new/borrow/inputs/PM-WORD-extra.json.gz'")
 new+="\nrun('two-sided-helper408-review',P/'new/borrow/channel408/verify.py','--work',work/'two-sided-helper408-review')"
 assert text.count(line)==1;path.write_text(text.replace(line,new))
 before=tree(src);after=tree(out);save(out/'MANIFEST.json',after)
 changes={n:{'before':before.get(n),'after':after.get(n)} for n in set(before)|set(after) if before.get(n)!=after.get(n)}
 expected={'new/BORROW-PROVIDERS.json','new/rebuild_borrow.py','verify.py','new/borrow/channel_extract.py'}|{f'new/borrow/words/BORROW-WORD-43{tag}.json.gz' for tag in ('base','extra')}|{f'new/borrow/inputs/PM-WORD-{tag}.json.gz' for tag in ('base','extra')}|{'new/borrow/channel408/'+n for n in ['PINS.json','verify.py','extract.py','structure.py',*pins]}
 assert set(changes)==expected and tree(src)==before
 result={'status':'PASS_SOURCE_BOUND_TWO_SIDED_HELPER408_OVERLAY','parent_manifest_sha256':PARENT,'manifest_sha256':sha(out/'MANIFEST.json'),'source_file_count':len(after),'changes':changes,'words':records,'builder_sha256':sha(Path(__file__))}
 save(out.parent/(out.name+'-DERIVATION.json'),result);print(result['status'],result['manifest_sha256'],len(after))
if __name__=='__main__':main()

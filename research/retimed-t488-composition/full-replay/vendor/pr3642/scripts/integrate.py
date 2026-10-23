import copy,gzip,hashlib,json,shutil,sys
from pathlib import Path
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--parent',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--data',type=Path,default=Path(__file__).resolve().parents[1]/'data');a=ap.parse_args()
H=a.data.resolve();P=a.parent.resolve();OUT=a.out.resolve();OUT.mkdir(exist_ok=False)
S=OUT/'source';shutil.copytree(P/'source',S);D=S/'new/borrow'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def save(p,x):p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def tree(p):return {f.relative_to(p).as_posix():sha(f) for f in sorted(p.rglob('*')) if f.is_file() and f!=p/'MANIFEST.json'}
def rep(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
oldmanifest=sha(P/'source/MANIFEST.json');assert oldmanifest=='318ede57c79d10323fb1918f7be4d451d1fcdac01c6456fe9851d51d05d59453';assert tree(P/'source')==rd(P/'source/MANIFEST.json')
(D/'release-retime').mkdir()
code='''# SPDX-License-Identifier: Apache-2.0
# New staged release retiming with substantial OpenAI Codex assistance.
# Builds on Ross Richardson PR3605 and all retained supplier attribution.
import copy,hashlib,json
import preload_move as pm

def canon(w):return hashlib.sha256(json.dumps(w,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def apply(parent,record):
 if canon(parent)!=record['source_canonical_sha256']:raise ValueError('retime source canonical hash')
 x=copy.deepcopy(parent)
 if [e['index'] for e in record['edits']]!=[591,641]:raise ValueError('exact retiming addresses')
 for e in record['edits']:
  i=e['index'];old=e['old'];new=e['new']
  if x['B'][i:i+2]!=old:raise ValueError('retime source gate preimage')
  if old[0][0]!=old[1][0]!='add':raise ValueError('ADD release')
  if old[0][1]==old[1][1] or old[0][2]!=old[1][2]:raise ValueError('commuting distinct targets common source')
  if new[0]!=old[1] or new[1][:-1]!=old[0][:-1]:raise ValueError('literal commuting permutation')
  if any(i<r[0]<i+2 for r in parent['warps']):raise ValueError('no warp crossed')
  x['B'][i:i+2]=copy.deepcopy(new)
 profile,inventory=pm.frame_report(x)
 if profile!=record['new_profile'] or inventory!=record['width_inventory'] or inventory!=parent['report']['width_inventory']:raise ValueError('complete profile/width recount')
 x['report']['local_profile']=profile
 z=copy.deepcopy(x);z['A']=z['A'][z['prelude_events']:]
 x['cleanup']=pm.derive_cleanup(z,set(map(int,x['helper_final'])))
 if canon(x)!=record['target_canonical_sha256']:raise ValueError('retime target canonical hash')
 if sorted(k for k in parent if parent[k]!=x[k])!=['B','cleanup','report']:raise ValueError('changed field restriction')
 return x
'''
# Fix the logical guard in the pure applier before this source is frozen.
code=code.replace("old[0][0]!=old[1][0]!='add'","old[0][0]!='add' or old[1][0]!='add'")
(D/'release_retime.py').write_text(code)
providers=rd(S/'new/BORROW-PROVIDERS.json')
for tag,pid in [('base','gauge44'),('extra','extra')]:
 q=D/f'words/BORROW-WORD-43{tag}.json.gz';assert rd(q)==rd(H/f'STAGED644-660-{tag}.json.gz');shutil.copy2(q,D/f'inputs/PRE-RETIME-{tag}.json.gz')
 shutil.copy2(H/f'RETIMED-RECORD-{tag}.json',D/f'release-retime/RECORD-{tag}.json');shutil.copy2(H/f'RETIMED644-660-{tag}.json.gz',q)
 providers[pid]['actual_paid_profile']=rd(q)['report']['local_profile']
save(S/'new/BORROW-PROVIDERS.json',providers)
p=S/'new/rebuild_borrow.py';s=p.read_text();anchor='    final=json.loads(gzip.decompress(shipped.read_bytes()))'
block="    import release_retime\n    assert chain[-1]==json.loads(gzip.decompress((D/'inputs'/f'PRE-RETIME-{wt}.json.gz').read_bytes()))\n    chain.append(release_retime.apply(chain[-1],json.loads((D/'release-retime'/f'RECORD-{wt}.json').read_text())));steps.append('staged-release-retime')\n"
p.write_text(rep(s,anchor,block+anchor))
p=D/'review_staged3605.py';p.write_text(rep(p.read_text(),"D/f'words/BORROW-WORD-43{tag}.json.gz'","D/f'inputs/PRE-RETIME-{tag}.json.gz'"))
review='''import copy,gzip,json
from pathlib import Path
import release_retime
D=Path(__file__).resolve().parent
for tag in ('base','extra'):
 read=lambda p:json.loads(gzip.decompress(p.read_bytes()))
 p=read(D/f'inputs/PRE-RETIME-{tag}.json.gz');r=json.loads((D/f'release-retime/RECORD-{tag}.json').read_text());w=read(D/f'words/BORROW-WORD-43{tag}.json.gz')
 assert release_retime.apply(p,r)==w
 controls=[]
 for key in ('preimage','coefficient','frame','profile'):
  bad=copy.deepcopy(r)
  if key=='preimage':bad['edits'][0]['old'][0][3]+=1
  if key=='coefficient':bad['edits'][0]['new'][1][3]+=1
  if key=='frame':bad['edits'][0]['new'][1][-1]=[429,30]
  if key=='profile':bad['new_profile']['1']+=1
  try:release_retime.apply(p,bad)
  except (ValueError,AssertionError):controls.append(key)
  else:raise AssertionError('retiming control accepted '+key)
 assert len(controls)==4
print('PASS_RELEASE_RETIME_RECONSTRUCTION_EIGHT_CONTROLS')
'''
(D/'review_release_retime.py').write_text(review)
p=S/'verify.py';line="run('staged3605-review',P/'new/borrow/review_staged3605.py')";p.write_text(rep(p.read_text(),line,line+"\nrun('staged-release-retime-review',P/'new/borrow/review_release_retime.py')"))
save(S/'MANIFEST.json',tree(S));mh=sha(S/'MANIFEST.json');n=len(rd(S/'MANIFEST.json'));commit='local-staged644-660-two-release-retimings'
for name in ['prepare_extension_native.py','admit_extension.py']:
 s=(P/name).read_text();s=rep(s,oldmanifest,mh)
 if name.startswith('prepare'):
  s=rep(s,'SOURCE_FILES=648','SOURCE_FILES='+str(n));s=rep(s,"SOURCE_COMMIT='pr3605-ac92a027c78b0c9bb0ada739b26959afda489d0e'","SOURCE_COMMIT='"+commit+"'")
 else:
  s=rep(s,"commit='pr3605-ac92a027c78b0c9bb0ada739b26959afda489d0e'","commit='"+commit+"'");s=rep(s,'source_file_count=648','source_file_count='+str(n))
 (OUT/name).write_text(s)
save(OUT/'DERIVATION.json',{'status':'PREPARED_RETIMER_SOURCE_NOT_ADMITTED','parent_manifest_sha256':oldmanifest,'manifest_sha256':mh,'source_files':n,'source_commit':commit,'changes':{k:{'old':rd(P/'source/MANIFEST.json').get(k),'new':v} for k,v in tree(S).items() if rd(P/'source/MANIFEST.json').get(k)!=v},'builder_sha256':sha(Path(__file__)),'prior_source_manifest_unchanged':tree(P/'source')==rd(P/'source/MANIFEST.json')})
print(mh,n)

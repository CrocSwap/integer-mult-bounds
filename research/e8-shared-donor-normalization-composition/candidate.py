"""Combine PR404 shared-donor entrance gauges with our exact ordinary long word.
This replaces the complete target-update schedule; PR404's overlapping recovery
is not claimed. Exact old/helper/raw/entrance interfaces are checked anew.
OpenAI Codex assistance. No frozen upstream source edited.
"""
from pathlib import Path
from hashlib import sha256
import copy,importlib.util,json
import os,subprocess,sys
assert __debug__
def prepare(SRC,NEW,P):
 SRC,NEW,P=map(Path,(SRC,NEW,P));P.mkdir(parents=True)
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None)
 def run(name,path,*args):
  with(P/(name+'.log')).open('w')as log:subprocess.run([sys.executable,'-B',str(path),*map(str,args)],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 run('original119',SRC/'frames/reconstruct.py',SRC/'inputs/candidate781.json',P/'original119',SRC/'frames/selection.json')
 run('original194',SRC/'shared/reconstruct.py',SRC/'inputs/candidate781.json',P/'original194',SRC/'shared/selection194.json','--reference119',P/'original119/candidate.json')
 run('original-dual',SRC/'dual/reconstruct.py',P/'original194/candidate.json',P/'original-dual','--source-sha256','141b7c732820f822d09f906a6f9206b2906777177bf7860c49f5acacb7da69a3')
 run('original-final',SRC/'code/frame-rewrite.py',P/'original-dual/candidate.json',P/'original-final')
 BASE=P/'original194/candidate.json';FINAL=P/'original-final/candidate.json';OLD=SRC/'inputs/candidate781.json'
 sha=lambda p:sha256(p.read_bytes()).hexdigest()
 assert sha(BASE)=='141b7c732820f822d09f906a6f9206b2906777177bf7860c49f5acacb7da69a3'
 assert sha(NEW)=='a2a1e957cec4f86fa7447037d757218d72b7f70c67391cc4dfb81ed60c0d00e6'
 assert sha(FINAL)=='d18ccdc580e78bde51575daec812cdbfaa92d1a700bf4d6a140b028f0424325a'
 spec=importlib.util.spec_from_file_location('unchanged404frame_math',SRC/'frames/reconstruct.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 c=json.loads(BASE.read_bytes());before=copy.deepcopy(c);new=json.loads(NEW.read_bytes());old=json.loads(OLD.read_bytes());final=json.loads(FINAL.read_bytes())
 for k in ['h','v','R','cst','ports','ret','scat','start','final','ext','frames','A']:assert new[k]==old[k],k
 assert c['B']==old['B'] and m.replay(new)==m.replay(old)
 assert m.first_frames(new)==m.first_frames(old)
 head=len(c['A'])-len(old['A']);assert head==484 and c['A'][head:]==new['A']
 c['B']=copy.deepcopy(new['B']);trans=m.rehist_and_audit(c)
 assert m.replay(c)==m.replay(before)==m.replay(final)
 assert all(c[k]==before[k]for k in c if k not in ['B','blocks','N'])
 assert c['N']==before['N']==final['N']
 assert m.first_frames(c)==m.first_frames(before)
 def helper(z):
  result=[]
  for part in ['A','B']:
   for g in z[part]:
    for r,a,b in g[3]:
     t,s=(g[2],r)if g[0]=='in'else(r,g[2])
     if not(120<=t<240):result.append((t,s,a,b))
  return result
 assert helper(c)==helper(before)==helper(final)
 h0=m.histogram(final);h1=m.histogram(c);delta={r:h1[r]-h0[r]for r in h0.keys()|h1.keys()if h1[r]!=h0[r]}
 assert sum(r*n for r,n in delta.items())==0
 raw=json.dumps(c,sort_keys=True,separators=(',',':')).encode();(P/'candidate.json').write_bytes(raw)
 r=dict(status='PASS_PR404_SHARED_GAUGES_OWN_LONG_WORD_EXACT_PREFLIGHT_ONLY',base_sha256=sha(BASE),candidate_sha256=sha(P/'candidate.json'),source_head='12f488264cdd74a3b60d0fb534f4955792384f5c',source_manifest_sha256=sha(SRC/'MANIFEST.json'),ordinary_sha256=sha(NEW),full404_sha256=sha(FINAL),histogram_delta_vs_full404=delta,nested_transitions=trans,dirty_columns=1021,entrance_gauges=len(c['ext']),unchanged_first_frames=True,unchanged_helper_word=True,omitted_mechanism='PR404 chronological124→125 recovery; complete own target schedule used instead',scope='Exact finite ordinary scalar map and paths only. Complete local, phase, bank/owner/invoice, moments, bit and outer plus independent review still required; no kappa claimed.')
 (P/'PREFLIGHT.json').write_text(json.dumps(r,sort_keys=True,indent=2)+'\n')
 from resynth import apply
 (P/'shared-long.json').write_bytes((P/'candidate.json').read_bytes())
 resynthesis=apply(SRC,P/'shared-long.json',P/'resynthesis')
 (P/'candidate.json').write_bytes((P/'resynthesis/candidate.json').read_bytes())
 r['shared_long_candidate_sha256']=r['candidate_sha256'];r['candidate_sha256']=sha(P/'candidate.json')
 r['status']='PASS_PR404_SHARED_GAUGES_LONG_WORD_AND_PINNED_PR402_TWO_TARGET_RESYNTHESIS'
 r['resynthesis']=resynthesis
 (P/'PREFLIGHT.json').write_text(json.dumps(r,sort_keys=True,indent=2)+'\n')
 return r

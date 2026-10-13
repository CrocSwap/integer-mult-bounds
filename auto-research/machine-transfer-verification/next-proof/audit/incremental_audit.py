#!/usr/bin/env python3
"""Pinned PR65–68 source inventory and exact power-profile comparisons.

No network access. Pass an isolated repository containing the exact pins.
This reads profiles as supplied finite inputs; a separate receipt records
which physical/compiler verifiers were actually rerun.
"""
import argparse,gzip,hashlib,importlib.util,json,subprocess
from collections import Counter
from datetime import datetime,timezone
from fractions import Fraction as Q
from pathlib import Path

HERE=Path(__file__).resolve().parent
PINS={65:'49e84f939d15b618b50714eb039cabf97c74256a',66:'29a504ffafe3e60a638158b8892a8c156d202947',67:'b3745601e947a94316bf25c2c6263d93c06e3364',68:'734c58e225e9d2254570c3b50296ed96943f62ea'}
PATHS={65:('research/reordered-rank-pair/frame-{}.json','research/reordered-rank-pair/README.md'),66:('certificates/split-dual-{}.json','research/split-dual/PROOF.md'),67:('research/slot-cost-rank-pair/frame-{}.json','research/slot-cost-rank-pair/README.md'),68:('research/global-anchor-screen/selected-{}.json','research/global-anchor-screen/PROOF.md')}
CLAIMS={65:'2041159402879/40000000000000000',66:'120777349/2500000000000',67:'10206752116843/200000000000000000',68:'5102938/100000000000'}
COMPONENTS={65:'Equal-rank region reordering on PR63; h23 cover/core, h25 reverse node',66:'PR59 split-pair choices plus PR55 dual suffix, unchanged PR60 compiler',67:'All-rank dependent retired-slot enumeration scored by actual fixed-basis entropy; original PR63 region order',68:'Compatible pending live controls F subset E subset next-use G; descending h25 slot ties'}
DEPENDENCIES={65:[63],66:[59,55,60],67:[63],68:[63,60]}

def enc(x):
 if isinstance(x,Q):return str(x)
 if isinstance(x,dict):return {str(k):enc(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [enc(v) for v in x]
 return x

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--diff-dir',type=Path);ap.add_argument('--basis67',action='store_true');args=ap.parse_args()
 repo=args.repo.resolve()
 def git(*a):return subprocess.check_output(['git','-C',str(repo),*a])
 def blob(n,p):return git('show',PINS[n]+':'+p)
 helper=HERE.parents[1]/'audit/scatter_binding_audit.py'
 spec=importlib.util.spec_from_file_location('strict_scatter',helper);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 snapshot=json.loads((HERE/'github-snapshot.json').read_text())['data']['repository'];api={p['number']:p for p in snapshot['pullRequests']['nodes']}
 out=[];profiles={};wordchecks=[]
 for n,pin in PINS.items():
  assert api[n]['headRefOid']==pin
  base=api[n]['baseRefOid'];merge=git('merge-base',base,pin).decode().strip();diff=git('diff','--no-ext-diff','--no-color',merge,pin)
  if args.diff_dir:
   args.diff_dir.mkdir(parents=True,exist_ok=True);(args.diff_dir/f'pr-{n}.diff').write_bytes(diff)
  template,source=PATHS[n];source_raw=blob(n,source);profiles[n]={}
  axes=[]
  for h in (23,25):
   profile_path=template.format(f'profiles-{h}');word_path=template.format(f'word-{h}')+'.gz'
   profile_raw=blob(n,profile_path);profile=json.loads(profile_raw);profiles[n][h]=profile['blocks']
   packed=blob(n,word_path);raw=gzip.decompress(packed);w=json.loads(raw);binding=mod.verify_scatter(w)
   assert w['h']==profile['h']==h and w['R']==profile['R'] and w['v']==profile['v']
   assert sum(t*c for t,c in enumerate(profile['blocks']))==h*w['R']+h*(h-1)
   basis=False
   if n==67 and args.basis67:
    v,R=w['v'],w['R'];initial=[1<<i for i in range(2*v+R)]
    M=[(2*v+a,2*v+b) for a,b,_ in w['ops']];V=[(2*v+s,int(i)) for i,s in w['sources'].items()];J=[tuple(x) for x in w['scatter']]
    word=M+J+M[::-1]+V+M+J+M[::-1]+V
    for dual in (False,True):
     state=initial.copy()
     for t,s in reversed(word) if dual else word:
      if dual:t,s=s,t
      assert t!=s and 0<=t<len(state) and 0<=s<len(state)
      state[t]^=state[s]
     expected=initial.copy()
     for i in range(v):expected[i if dual else v+i]^=initial[v+i if dual else i]
     assert state==expected
    basis=True
   row=dict(pr=n,h=h,R=w['R'],word_path=word_path,decompressed_word_sha256=hashlib.sha256(raw).hexdigest(),profile_path=profile_path,profile_sha256=hashlib.sha256(profile_raw).hexdigest(),literal_scatter=binding,local_mass=profile['rank_sum'],independent_full_basis_both_orientations=basis)
   axes.append(row);wordchecks.append(row)
  p=dict(number=n,pin=pin,api_base=base,git_merge_base=merge,state=api[n]['state'],draft=api[n]['isDraft'],title=api[n]['title'],url=api[n]['url'],author=api[n]['author'],claimed_kappa=CLAIMS[n],component=COMPONENTS[n],mathematical_components=DEPENDENCIES[n],source_path=source,source_sha256=hashlib.sha256(source_raw).hexdigest(),changed_files=git('diff','--name-status',merge,pin).decode().splitlines(),diff_bytes=len(diff),diff_sha256=hashlib.sha256(diff).hexdigest(),axes=axes,review_depth='PR body, primary proof/scope, actual compiler changes and verifier source inspected; complete mathematical proof review of inherited framework not claimed',fresh_focused_verification='PR67 full target separately recorded; other branches not freshly rerun in full')
  out.append(p)
 # The original submitted PR64 profile equals pinned PR63 byte-for-byte.
 profiles[64]={h:json.loads((HERE.parents[1]/'finite-frames'/f'pair-ranked-{h}-receipt.json').read_text())['profile']['blocks'] for h in (23,25)}
 comparisons=[]
 for n,old in [(65,64),(67,64),(67,65),(68,64),(67,68)]:
  d={t:sum(rep*((profiles[n][h][t] if t<len(profiles[n][h]) else 0)-(profiles[old][h][t] if t<len(profiles[old][h]) else 0)) for h,rep in [(23,2300),(25,1771)]) for t in range(26)}
  assert sum(t*v for t,v in d.items())==0
  caps={k:sum(min(t,k)*v for t,v in d.items()) for k in range(1,26)};prefix={};running=0
  for k,c in caps.items():running+=c;prefix[k]=running
  # Coefficients of the second Abel identity, b_24*S_24 + sum_1^23 (b_k-b_(k+1))*S_k.
  recovered={k:prefix[k]-prefix.get(k-1,0) for k in range(1,25)}
  assert recovered=={k:caps[k] for k in range(1,25)}
  comparisons.append(dict(new=n,old=old,m=575,W=137151806,total_rank=78860441550,signed_multiplicities={t:v for t,v in d.items() if v},zero_rank_mass=True,capped_sums=caps,prefix_capped_sums=prefix,ordinary_concave_dominance=all(c<=0 for c in caps.values()),decreasing_curvature_dominance=all(c<=0 for c in prefix.values()) and prefix[24]<0,second_abel_identity_coefficients_checked=True,power_consequence='Strictly smaller full characteristic for every saving 0<u<1 if decreasing-curvature dominance holds; proof in power-dominance.txt. Pinned profile comparison, not all-size multiplication proof.'))
 graph=[dict(source=63,target=65,type='mathematical_component',meaning='same scalar graph/retired priority; changed topological region order'),dict(source=65,target=67,type='git_ancestry',meaning='PR67 descends from PR65 but resets physical region order'),dict(source=65,target=67,type='arithmetic_code_reuse',meaning='refined rational enclosure package, not PR65 region schedule'),dict(source=63,target=67,type='mathematical_component',meaning='original region order with new cost-aware clearing witness selection'),dict(source=59,target=66,type='mathematical_component',meaning='split-pair group vectors; excludes PR59 paid clones/permutation overrides'),dict(source=55,target=66,type='mathematical_component',meaning='dual-suffix layout and native orders'),dict(source=60,target=66,type='mathematical_component',meaning='unchanged ranked joint compiler'),dict(source=63,target=68,type='mathematical_component',meaning='same pair graph/compiler extended with compatible pending controls'),dict(source=64,target=68,type='proof_format_credit',meaning='capped-mass comparison format, independently recomputed candidate integers'),dict(source=67,target=68,type='speculative_compatible',meaning='cost-aware enumeration can use legal pending controls; requires fresh full words/profiles; scores for pending controls should reference their next-use frame rather than identity cleanup'),dict(source=65,target=67,type='speculative_compatible_schedule',meaning='source-level changes may compose after fresh topological and word checks; no additive exponent claim')]
 result=dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),main=snapshot['defaultBranchRef']['target']['oid'],total_prs=len(api),state_counts=dict(Counter(p['state'] for p in api.values())),scope='Incremental audit of PR65–68; previous 62-PR snapshot preserved. Fresh verification scope is recorded separately, never inferred from a PR body.',pull_requests=out,typed_edges=graph,scatter_checker_sha256=hashlib.sha256(helper.read_bytes()).hexdigest())
 (HERE/'incremental-inventory.json').write_text(json.dumps(enc(result),indent=2)+'\n');(HERE/'power-dominance.json').write_text(json.dumps(enc(dict(comparisons=comparisons)),indent=2)+'\n')
 print('PASS pinned metadata, all eight literal scatter bindings, rank masses and five exact profile comparisons')
 if args.basis67:print('PASS PR67 independent full basis semantics, both dimensions and orientations')
if __name__=='__main__':main()

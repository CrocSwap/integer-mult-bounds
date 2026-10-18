"""Apply six source-bound frame coalescences; scalar operations stay identical.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
from pathlib import Path
from collections import Counter
import argparse,copy,gzip,hashlib,json,sys
assert __debug__,'Assertions required'
ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--recipe',type=Path,required=True);ap.add_argument('--gk-dir',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();assert not a.out.exists()
sys.path.insert(0,str(a.gk_dir));import gk_word as G,gk_common as C
G.V=C.V=112;G.DATA=C.DATA=7168
raw=json.loads(gzip.decompress(a.input.read_bytes()));recipe=json.loads(a.recipe.read_text());enc=lambda x:json.dumps(x,sort_keys=True,separators=(',',':')).encode();sha=lambda x:hashlib.sha256(x).hexdigest()
assert sha(enc(raw))==recipe['input_content_sha256'];before=G.profile(raw);assert dict(before)=={int(r):n for r,n in recipe['before'].items()};w=copy.deepcopy(raw);trace=[]
for change in recipe['changes']:
 part,i=change['section'],change['index'];assert w[part][i]==change['before'];assert change['before'][:-1]==change['after'][:-1]
 w[part][i]=change['after'];after=G.profile(w);delta={r:after[r]-before[r]for r in set(after)|set(before)if after[r]!=before[r]};assert delta=={1:-2,2:1};trace.append(dict(section=part,index=i,delta=delta));before=after
assert dict(G.profile(w))=={int(r):n for r,n in recipe['after'].items()}
for key in raw:
 if key not in ('A','B','report'):assert w[key]==raw[key]
for part in ('A','B'):assert[e[:-1]for e in w[part]]==[e[:-1]for e in raw[part]]
assert G.widths_of(w)==G.widths_of(raw);responses=G.responses(w);assert responses==G.responses(raw)
assert all(not responses[int(r)-224]for r in w['start_extra'])
# Every omitted coalescence must lose the new profile. Every full-space frame
# replacement must violate a chain/cut bound. These are fresh negative controls.
rejected=[]
for c in recipe['changes']:
 z=copy.deepcopy(w);z[c['section']][c['index']]=c['before'];assert G.profile(z)!=G.profile(w);rejected.append('omission-%s-%d'%(c['section'],c['index']))
 z=copy.deepcopy(w);z[c['section']][c['index']][-1]=list(G.FULL)
 try:G.profile(z)
 except AssertionError:rejected.append('overpromotion-%s-%d'%(c['section'],c['index']))
 else:raise AssertionError('Invalid frame accepted')
w['report'].update(local_profile=dict(G.profile(w)),local_rank_mass=sum(r*n for r,n in G.profile(w).items()),status='SIX_KERNEL_FRAME_COALESCENCES_PENDING_NATIVE_PHASE_ADMISSION')
a.out.mkdir(parents=True);(a.out/'FULL-WORD.json.gz').write_bytes(G.dump(w));receipt=dict(status='PASS_SIX_EXACT_FRAME_COALESCENCES',input_content_sha256=sha(enc(raw)),output_content_sha256=sha(enc(w)),profile_before=recipe['before'],profile_after=recipe['after'],changes=trace,negative_controls_rejected=rejected,all_scalar_operations_unchanged=True,all_initial_helper_responses_equal=True,all_entering_helper_responses_zero=True,helper_widths_unchanged=True,scope='Construction, frame/profile and scalar response checks only; native, phase and global admission are separate.')
(a.out/'FRAME-CONSTRUCTION.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps(receipt,indent=2))

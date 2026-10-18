"""Move commuting gates, then apply source-bound frame coalescences; the scalar map stays identical.
Extends PR583's build_frames.py (chafreaky, OpenAI Codex assisted, Apache-2.0) with commuting gate moves found by
Claude Code research agents. Apache-2.0.

Recipe: input_content_sha256, before/after profiles, moves [{section, from, to}] (applied in order; every gate the
moved gate passes must commute with it), and changes [{section, index, before, after}] (indices after the moves;
each change only raises the gate frame and must save exactly {1:-2, 2:+1}). The cleanup section is rebuilt with the
inherited rule (the input word must already satisfy it), and the helper responses must be unchanged.
"""
from pathlib import Path
import argparse,copy,gzip,hashlib,json,sys
from collections import Counter
assert __debug__,'Assertions required'
ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--recipe',type=Path,required=True);ap.add_argument('--gk-dir',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();assert not a.out.exists()
sys.path.insert(0,str(a.gk_dir));import gk_word as G,gk_common as C
G.V=C.V=112;G.DATA=C.DATA=7168
raw=json.loads(gzip.decompress(a.input.read_bytes()));recipe=json.loads(a.recipe.read_text());enc=lambda x:json.dumps(x,sort_keys=True,separators=(',',':')).encode();sha=lambda x:hashlib.sha256(x).hexdigest()
assert sha(enc(raw))==recipe['input_content_sha256'];before=G.profile(raw);assert dict(before)=={int(r):n for r,n in recipe['before'].items()}
def regs(e):return(e[1],e[2])if e[0]=='add'else(e[1],)
def commute(x,y):
 """Two additions commute unless one writes the other's source; any other pair must touch disjoint registers."""
 if x[0]=='add'and y[0]=='add':return x[1]!=y[2]and y[1]!=x[2]
 return not set(regs(x))&set(regs(y))
cleanup=lambda w:[G.inverse(e,G.FULL)for e in reversed(w['A']+w['B'])if not 112<=e[1]<224]
assert raw['cleanup']==cleanup(raw),'input cleanup is not the inherited inverse rule'
w=copy.deepcopy(raw);moved=[]
for m in recipe['moves']:
 L=w[m['section']];i,j=m['from'],m['to'];assert i!=j and 0<=i<len(L)and 0<=j<len(L)
 passed=range(i+1,j+1)if j>i else range(j,i);assert all(commute(L[i],L[k])for k in passed),'noncommuting move %s'%m
 L.insert(j,L.pop(i));moved.append(dict(m,passed=len(passed)))
w['cleanup']=cleanup(w);responses=G.responses(w);assert responses==G.responses(raw),'scalar responses changed by the moves'
assert G.profile(w)==before,'moves alone changed the profile';trace=[]
for change in recipe['changes']:
 part,i=change['section'],change['index'];assert w[part][i]==change['before'];assert change['before'][:-1]==change['after'][:-1]
 w[part][i]=change['after'];after=G.profile(w);delta={r:after[r]-before[r]for r in set(after)|set(before)if after[r]!=before[r]};assert delta=={1:-2,2:1};trace.append(dict(section=part,index=i,delta=delta));before=after
w['cleanup']=cleanup(w)
assert dict(G.profile(w))=={int(r):n for r,n in recipe['after'].items()}
for key in raw:
 if key not in ('A','B','cleanup','report'):assert w[key]==raw[key]
for part in ('A','B'):assert sorted(map(enc,(e[:-1]for e in w[part])))==sorted(map(enc,(e[:-1]for e in raw[part])))
assert G.widths_of(w)==G.widths_of(raw);responses=G.responses(w);assert responses==G.responses(raw)
assert all(not responses[int(r)-224]for r in w['start_extra'])
# Fresh negative controls: every omitted coalescence loses the new profile, every full-space frame replacement violates
# a chain/cut bound, and every move reverted before its coalescence is rejected.
rejected=[]
for c in recipe['changes']:
 z=copy.deepcopy(w);z[c['section']][c['index']]=c['before'];assert G.profile(z)!=G.profile(w);rejected.append('omission-%s-%d'%(c['section'],c['index']))
 z=copy.deepcopy(w);z[c['section']][c['index']][-1]=list(G.FULL)
 try:G.profile(z)
 except AssertionError:rejected.append('overpromotion-%s-%d'%(c['section'],c['index']))
 else:raise AssertionError('Invalid frame accepted')
for m in reversed(recipe['moves']):
 z=copy.deepcopy(w);L=z[m['section']];L.insert(m['from'],L.pop(m['to']))
 try:ok=G.profile(z)==G.profile(w)
 except AssertionError:ok=False
 assert not ok,'unmoved coalescence accepted';rejected.append('unmoved-%s-%d'%(m['section'],m['from']))
w['report'].update(local_profile=dict(G.profile(w)),local_rank_mass=sum(r*n for r,n in G.profile(w).items()),status='GATE_MOVE_FRAME_COALESCENCES_PENDING_NATIVE_PHASE_ADMISSION',
 # descriptive inventory fields recomputed from the actual widths (as PR586's adapted PR583 constructor does)
 width_inventory={str(k):v for k,v in sorted(Counter(G.widths_of(w)).items())},entering_helpers=sum(v<9 for v in G.widths_of(w)),entrance_rank=sum(9-v for v in G.widths_of(w)))
a.out.mkdir(parents=True);(a.out/'FULL-WORD.json.gz').write_bytes(G.dump(w));receipt=dict(status='PASS_EXACT_GATE_MOVE_FRAME_COALESCENCES',input_content_sha256=sha(enc(raw)),output_content_sha256=sha(enc(w)),profile_before=recipe['before'],profile_after=recipe['after'],moves=moved,changes=trace,negative_controls_rejected=rejected,all_scalar_responses_unchanged=True,all_entering_helper_responses_zero=True,helper_widths_unchanged=True,cleanup_rebuilt_by_inherited_rule=True,scope='Construction, commutation, frame/profile and scalar response checks only; native, phase and global admission are separate.')
(a.out/'FRAME-CONSTRUCTION.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps(receipt,indent=2))

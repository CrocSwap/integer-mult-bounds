"""Exact compatibility preflight, not a full PR401 composition admission.
Run the unchanged pinned constructor function on the improved scalar word,
after checking complete old-input operator equality and interface metadata.
No upstream source is edited. OpenAI Codex assistance.
"""
from pathlib import Path
from hashlib import sha256
import copy,importlib.util,json
def prepare(SRC,NEW,P):
 SRC,NEW,P=map(Path,(SRC,NEW,P));P.mkdir(parents=True)
 OLD=SRC/'inputs/candidate781.json'
 CON=SRC/'frames/reconstruct.py';SEL=SRC/'frames/selection.json'
 sha=lambda p:sha256(p.read_bytes()).hexdigest()
 assert sha(NEW)=='a2a1e957cec4f86fa7447037d757218d72b7f70c67391cc4dfb81ed60c0d00e6'
 spec=importlib.util.spec_from_file_location('pinned401constructor',CON);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 assert sha(OLD)==m.SOURCE_SHA256 and sha(SEL)==m.SELECTION_SHA256
 manifest=json.loads((SRC/'MANIFEST.json').read_text(encoding='utf-8-sig'))['files']
 assert all(sha(p)==manifest[p.relative_to(SRC).as_posix()]for p in [OLD,CON,SEL])
 old=json.loads(OLD.read_bytes());new=json.loads(NEW.read_bytes());witness=json.loads(SEL.read_bytes())
 same=['h','v','R','cst','ports','ret','scat','start','final','ext','frames','A']
 for key in same:assert old[key]==new[key],key
 assert m.first_frames(old)==m.first_frames(new)
 assert m.replay(old)==m.replay(new),'Entire original affine operator must agree'
 baseline,_,_,_=m.reconstruct(old,witness)
 assert sha256(json.dumps(baseline,sort_keys=True,separators=(',',':')).encode()).hexdigest()==m.CANDIDATE_SHA256
 candidate,K,frames,transitions=m.reconstruct(new,witness)
 assert candidate['start']==baseline['start']and candidate['ext']==baseline['ext']and candidate['A']==baseline['A']
 assert candidate['frames']==baseline['frames']and len(candidate['frames'])==976
 assert m.replay(candidate)==m.replay(baseline)
 before=m.histogram(baseline);after=m.histogram(candidate)
 delta={r:after[r]-before[r]for r in before.keys()|after.keys()if after[r]!=before[r]}
 raw=json.dumps(candidate,sort_keys=True,separators=(',',':')).encode();(P/'candidate.json').write_bytes(raw)
 (P/'K.json').write_text(json.dumps({'columns':new['R'],'rows':K},sort_keys=True,separators=(',',':'))+'\n')
 result=dict(status='PASS_EXACT_PR401_LONG_WORD_TRANSPLANT_PREFLIGHT_ONLY',pr401_commit='7844f72c6051a4408284c3092490687061675c1a',source_hashes={name:sha(p)for name,p in [('pr401/inputs/candidate781.json',OLD),('fresh-parent/complex/candidate.json',NEW),('pr401/frames/reconstruct.py',CON),('pr401/frames/selection.json',SEL)]},unchanged_interfaces=same,full_old_raw_operator_equal=True,full_gauged_raw_operator_equal=True,same_first_frames=True,gauges=len(candidate['ext']),new_spaces=frames,transition_visits=transitions,local_histogram_delta_vs_pr401=delta,rank_mass_delta=sum(r*n for r,n in delta.items()),candidate_sha256=sha(P/'candidate.json'),K_sha256=sha(P/'K.json'),scope='Pinned unchanged constructor algebra, complete raw map, 119 response gauges and exact nesting replay only. Both normalized scalar orientations, all phase edges, bank/owner routes, invoice, moment engines and composed cutoff checks remain required. No new kappa claimed.')
 (P/'PREFLIGHT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
 return result

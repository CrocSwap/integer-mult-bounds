"""Replay the frozen 63-frame recipe; no search or optimizer is required.
Prepared for chafreaky with Codex assistance, Apache-2.0.
"""
from pathlib import Path
from collections import Counter
import copy,gzip,hashlib,json,sys
if not __debug__:raise SystemExit('Assertions required')
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'vendor/static44/gk'))
import gk_word as G
import gk_common as C
G.V=C.V=112;G.DATA=C.DATA=7168
source,out=map(Path,sys.argv[1:3]);assert not out.exists();out.mkdir(parents=True)
w=json.load(gzip.open(source));old=copy.deepcopy(w);recipe=json.loads((P/'data/RECIPE.json').read_text());before=G.profile(w)
assert dict(before)=={int(k):n for k,n in recipe['before'].items()}
assert len(recipe['changes'])==63
seen=set()
for change in recipe['changes']:
 sec,i=change['section'],change['index'];assert sec in ('A','B') and (sec,i) not in seen;seen.add((sec,i))
 e=w[sec][i];assert e[-1]==change['old'];F=G.basis(change['new']);assert list(F)==change['new'];e[-1]=list(F)
after=G.profile(w);assert dict(after)=={int(k):n for k,n in recipe['after'].items()}
assert {r:after[r]-before[r] for r in set(before)|set(after) if after[r]!=before[r]}=={1:16,2:-16,3:-16,4:16}
assert sum(before.values())==sum(after.values()) and sum(r*n for r,n in before.items())==sum(r*n for r,n in after.items())
assert G.widths_of(w)==G.widths_of(old)
for sec in ['A','B']:assert [e[:-1] for e in w[sec]]==[e[:-1] for e in old[sec]]
for key in old:
 if key not in ('A','B','report'):assert old[key]==w[key]
w['report']['local_profile']=dict(after);w['report']['local_rank_mass']=sum(r*n for r,n in after.items())
blob=G.dump(w);blob=blob[:9]+bytes([255])+blob[10:];(out/'FULL-WORD.json.gz').write_bytes(blob)
r=dict(status='PASS_FROZEN_SUBSPACE16_FRAME_RECIPE',changes=len(seen),changes_by_section=dict(Counter(s for s,i in seen)),before=dict(before),after=dict(after),delta={1:16,2:-16,3:-16,4:16},rank_mass=sum(r*n for r,n in after.items()),scalar_operations_unchanged=True,starts_cut_cleanup_and_widths_unchanged=True,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),word_sha256=hashlib.sha256(blob).hexdigest(),scope='Exact nested-frame legality and paid-profile identity. Full arbitrary-dirt, phase, owner and invoice admission are independent subsequent stages.')
(out/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['changes_by_section'],dict(after))

"""Reconstruct the frozen four-pivot supplier from the verified zero word.
Prepared with OpenAI Codex assistance; Apache-2.0. Derived from PR558's
complete-group promotion. Gzip metadata is normalized to OS byte255 while
the decompressed word is pinned to the exploratory construction. Neither a
solver nor a platform-dependent header selects any mathematics.
"""
import argparse,copy,gzip,hashlib,json,sys
from collections import Counter
from pathlib import Path
assert __debug__, 'Assertions required'
ap=argparse.ArgumentParser(description=__doc__)
for name in ('input','recipe','gk-dir','out'):ap.add_argument('--'+name,type=Path,required=True)
a=ap.parse_args();assert not a.out.exists()
sys.path.insert(0,str(a.gk_dir));import gk_word as g,gk_common as co
g.V=co.V=112;g.DATA=co.DATA=7168
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads(a.recipe.read_text());assert sha(a.input)==r['source_sha256']
w=json.loads(gzip.decompress(a.input.read_bytes()));before=copy.deepcopy(w)
assert dict(g.profile(w))=={int(k):n for k,n in r['local_before'].items()}
assert len(r['changes'])==1;ch=r['changes'][0]
assert ch['group']==10 and ch['pivots']==[419,421,422,423] and ch['gates']==12
assert len(g.basis(ch['old_E']))==4 and len(g.basis(ch['new_E']))==5 and g.span(ch['old_E'])<=g.span(ch['new_E'])
for h in ch['pivots']:
 assert w['start_extra'][str(224+h)]==ch['old_E'];w['start_extra'][str(224+h)]=ch['new_E']
kernel=w['B'][320:488];count=0
assert len(kernel)==168 and all(e[0]=='add'for e in kernel)
assert not {e[1]for e in kernel}&{e[2]for e in kernel}
for e in kernel:
 if e[2]-224 in ch['pivots']:
  assert e[-1]==ch['old_E'];e[-1]=ch['new_E'];count+=1
assert count==12
w['B'][320:488]=sorted(kernel,key=lambda e:len(e[-1]))
w['cleanup']=[g.inverse(e,g.FULL)for e in reversed(w['A']+w['B'])if not 112<=e[1]<224]
profile=dict(g.profile(w));widths=dict(Counter(g.widths_of(w)))
assert profile=={int(k):n for k,n in r['local_after'].items()}
assert widths=={int(k):n for k,n in r['widths'].items()}
assert Counter(tuple(e[:-1])for e in before['B'])==Counter(tuple(e[:-1])for e in w['B'])
assert {k:v for k,v in before.items()if k not in {'B','cleanup','start_extra','report'}}=={k:v for k,v in w.items()if k not in {'B','cleanup','start_extra','report'}}
w['report'].update(local_profile=profile,width_inventory=widths,local_rank_mass=sum(k*n for k,n in profile.items()),status='FOUR_RANK5_PIVOTS_PENDING_MIXED_NATIVE_ADMISSION')
raw=g.dump(w);assert raw[:3]==b'\x1f\x8b\x08' and len(raw)>=18
raw=raw[:9]+b'\xff'+raw[10:]
assert hashlib.sha256(raw).hexdigest()==r['word_sha256']
assert hashlib.sha256(gzip.decompress(raw)).hexdigest()==r['word_content_sha256']
a.out.mkdir(parents=True);(a.out/'FULL-WORD.json.gz').write_bytes(raw)
(a.out/'PROMOTION.json').write_bytes(a.recipe.read_bytes())
receipt=dict(status='PASS_FROZEN_FOUR_PIVOT_CONSTRUCTION',source_sha256=sha(a.input),recipe_sha256=sha(a.recipe),word_sha256=r['word_sha256'],word_content_sha256=r['word_content_sha256'],local_profile=profile,width_inventory=widths,scalar_B_multiset_unchanged=True,complete_commuting_kernel_group=True)
(a.out/'CONSTRUCTION.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],receipt['word_sha256'])

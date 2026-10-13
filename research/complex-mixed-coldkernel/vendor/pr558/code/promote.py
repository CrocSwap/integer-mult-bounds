"""Deterministic lift of eight existing post-center kernel pivots to rank five.
Prepared for icekylinx with OpenAI Codex assistance. Apache-2.0.
The scalar coefficients, sourceports, cut and all downstream frames are retained.
"""
from pathlib import Path
from collections import Counter
import argparse,copy,gzip,hashlib,json,sys
if not __debug__:raise SystemExit('Assertions must remain enabled.')
a=argparse.ArgumentParser();a.add_argument('--input',type=Path,required=True);a.add_argument('--gk',type=Path,required=True);a.add_argument('--recipe',type=Path,required=True);a.add_argument('--out',type=Path,required=True);a=a.parse_args()
sys.path.insert(0,str(a.gk));import gk_word as g,gk_common as co
g.V=co.V=112;g.DATA=co.DATA=7168
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads(a.recipe.read_text());assert sha(a.input)==r['source_sha256']
w=json.loads(gzip.decompress(a.input.read_bytes()));before=copy.deepcopy(w)
assert dict(g.profile(w))=={int(k):v for k,v in r['local_before'].items()}
kernel=w['B'][320:488];assert len(kernel)==168
# All kernel additions commute: they read pivots and write disjoint donors.
assert all(e[0]=='add'for e in kernel)
assert not {e[1]for e in kernel}&{e[2]for e in kernel}
assert sum(len(ch['pivots'])for ch in r['changes'])==8
for ch in r['changes']:
 E0,E1=ch['old_E'],ch['new_E'];assert len(g.basis(E0))==4 and len(g.basis(E1))==5 and g.span(E0)<=g.span(E1)
 for h in ch['pivots']:
  assert w['start_extra'][str(224+h)]==E0;w['start_extra'][str(224+h)]=E1
 changed=0
 for op in kernel:
  if op[2]-224 in ch['pivots']:
   assert op[-1]==E0;op[-1]=E1;changed+=1
 assert changed==ch['gates']==12
w['B'][320:488]=sorted(kernel,key=lambda e:len(e[-1]))
w['cleanup']=[g.inverse(e,g.FULL)for e in reversed(w['A']+w['B'])if not 112<=e[1]<224]
H=g.profile(w);widths=Counter(g.widths_of(w))
assert dict(H)=={int(k):v for k,v in r['local_after'].items()}
assert dict(widths)=={int(k):v for k,v in r['widths'].items()}
assert {k:v for k,v in before.items()if k not in {'B','cleanup','start_extra','report'}}=={k:v for k,v in w.items()if k not in {'B','cleanup','start_extra','report'}}
assert Counter(tuple(e[:-1])for e in before['B'])==Counter(tuple(e[:-1])for e in w['B'])
w['report'].update(local_profile=dict(H),width_inventory=dict(widths),local_rank_mass=sum(q*n for q,n in H.items()),status='POSTCENTER_KERNEL_RANK5_PROMOTION_PENDING_GLOBAL_ADMISSION')
a.out.mkdir(parents=True,exist_ok=False);dest=a.out/'FULL-WORD.json.gz';dest.write_bytes(g.dump(w));assert sha(dest)==r['word_sha256'];assert hashlib.sha256(gzip.decompress(dest.read_bytes())).hexdigest()==r['word_content_sha256']
(a.out/'PROMOTION.json').write_bytes(a.recipe.read_bytes())
(a.out/'CONSTRUCTION.json').write_text(json.dumps(dict(status='PASS_LITERAL_EIGHT_PIVOT_RANK5_CONSTRUCTION',input_sha256=sha(a.input),output_sha256=sha(dest),scalar_B_multiset_unchanged=True,kernel_shears_commute=True,local_profile=dict(H),widths=dict(widths),promoted_pivots=8),indent=2)+'\n')
print('PASS deterministic8pivotpromotion',sha(dest))

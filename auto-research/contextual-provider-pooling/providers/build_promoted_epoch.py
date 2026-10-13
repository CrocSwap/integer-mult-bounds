from pathlib import Path
import argparse,copy,json,gzip,hashlib,sys
from collections import Counter
ap=argparse.ArgumentParser();ap.add_argument('--input',required=True);ap.add_argument('--gk-dir',required=True);ap.add_argument('--promotion',required=True);ap.add_argument('--out',required=True);ap.add_argument('--pivots',default='all');a=ap.parse_args()
sys.path.insert(0,a.gk_dir);import gk_word as g,gk_common as co
g.V=co.V=112;g.DATA=co.DATA=7168
canon=lambda v:json.dumps(v,sort_keys=True,separators=(',',':')).encode()
w=json.loads(gzip.decompress(Path(a.input).read_bytes()));recipe=json.loads(Path(a.promotion).read_text())
assert hashlib.sha256(canon(w)).hexdigest()=='7d3b66098cf0b74cbbdc42993f4366f22f8e63302a2626628e2f753c68338e4e'
assert hashlib.sha256(canon(recipe)).hexdigest()=='857cbcfbcdd1ab31b276a825d98eaaa31e4c18e3abc48a5d0f37d4b046e6bff7','promotion recipe pin mismatch'
full={h for c in recipe['changes']for h in c['pivots']}
chosen=full if a.pivots=='all'else set(map(int,a.pivots.split(',')))if a.pivots else set()
assert chosen<=full
old=copy.deepcopy(w);kernel=w['B'][320:488]
assert len(kernel)==168 and all(e[0]=='add'for e in kernel)
assert not{e[1]for e in kernel}&{e[2]for e in kernel}
changes=[]
for ch in recipe['changes']:
 pivots=[h for h in ch['pivots']if h in chosen]
 if not pivots:continue
 E0,E1=ch['old_E'],ch['new_E']
 assert len(g.basis(E0))==4 and len(g.basis(E1))==5 and g.span(E0)<=g.span(E1)
 for h in pivots:assert w['start_extra'][str(224+h)]==E0;w['start_extra'][str(224+h)]=E1
 changed=0
 for op in kernel:
  if op[2]-224 in pivots:assert op[-1]==E0;op[-1]=E1;changed+=1
 assert changed==3*len(pivots)
 changes.append(dict(ch,pivots=pivots,gates=changed))
w['B'][320:488]=sorted(kernel,key=lambda e:len(e[-1]))
w['cleanup']=[g.inverse(e,g.FULL)for e in reversed(w['A']+w['B'])if not 112<=e[1]<224]
assert w['A']==old['A']
assert Counter(tuple(e[:-1])for e in old['B'])==Counter(tuple(e[:-1])for e in w['B'])
H=g.profile(w);widths=Counter(g.widths_of(w))
w['report'].update(local_profile=dict(H),width_inventory=dict(widths),local_rank_mass=sum(k*v for k,v in H.items()),status='EPOCH_SELECTED_RANK5_PROMOTION_PENDING_GLOBAL_ADMISSION')
out=Path(a.out);out.mkdir(parents=True,exist_ok=False);raw=gzip.compress(gzip.decompress(g.dump(w)),compresslevel=9,mtime=0);raw=raw[:9]+bytes([255])+raw[10:];(out/'FULL-WORD.json.gz').write_bytes(raw)
selected=dict(recipe,changes=changes,local_after=dict(H),widths=dict(widths))
(out/'PROMOTION.json').write_text(json.dumps(selected,indent=2)+'\n')
receipt=dict(status='PASS_FRAME_PROFILE_PENDING_SCALAR',selected_pivots=sorted(chosen),source_semantic_sha256=hashlib.sha256(canon(old)).hexdigest(),promotion_semantic_sha256=hashlib.sha256(canon(recipe)).hexdigest(),word_semantic_sha256=hashlib.sha256(canon(w)).hexdigest(),word_sha256=hashlib.sha256(raw).hexdigest(),local_profile=dict(H),width_counts=dict(widths),ordered_widths=g.widths_of(w),scalar_A_unchanged=True,scalar_B_multiset_unchanged=True)
(out/'CONSTRUCTION.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(out.name,'pivots',len(chosen),'H',dict(H),'widths',dict(widths))

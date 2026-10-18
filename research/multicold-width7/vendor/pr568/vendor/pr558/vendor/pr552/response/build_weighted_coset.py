"""Frozen weighted coset representative construction. No search."""
from pathlib import Path
from fractions import Fraction as Q
import argparse,copy,gzip,hashlib,json,sys
if not __debug__:raise SystemExit('Assertions must remain enabled.')
ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--selection',type=Path,required=True);ap.add_argument('--gk-dir',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
sys.path.insert(0,str(a.gk_dir));import gk_word as g,gk_common as c
g.V=c.V=112;g.DATA=c.DATA=7168
w=json.load(gzip.open(a.input));r=json.loads(a.selection.read_text());N=728;V=112
def semantic(w):return hashlib.sha256(json.dumps({k:v for k,v in w.items()if k!='report'},sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert semantic(w)==r['input_semantic_sha256']
protected=set(range(V))|set(map(int,w['start_extra']));assert len(protected)==324
profile=g.profile(w);before=sum(map(len,g.responses(w)));assert before==r['before_compensation'];receipts=[]
for move in r['selection']:
 i=move['index'];old=w['A'][i];new=move['new_operation'];assert old==move['old_operation'];assert old[0]==new[0]=='add'and old[1]==new[1]and old[-1]==new[-1]and new[1]!=new[2]
 rows=[{j:Q(1)}for j in range(N)]
 for e in w['A'][:i]:g.apply_op(e,rows)
 q=Q(old[3],old[4]);z=Q(new[3],new[4]);assert z.denominator&(z.denominator-1)==0
 err={j:-q*x for j,x in rows[old[2]].items()}
 for j,x in rows[new[2]].items():
  y=err.get(j,Q(0))+z*x
  if y:err[j]=y
  else:err.pop(j,None)
 assert all(j>=224 and j not in protected for j in err)
 assert err=={int(j):Q(x)for j,x in move['cold_difference'].items()}
 n0=sum(map(len,g.responses(w)));w['A'][i]=copy.deepcopy(new);assert g.profile(w)==profile
 n1=sum(map(len,g.responses(w)));assert n0-n1==move['compensation_saved']>0
 receipts.append(dict(index=i,compensation_before=n0,compensation_after=n1,cold_error_checked=True,protected_columns_preserved=True,frame_profile_unchanged=True))
w['cleanup']=[g.inverse(e,g.FULL)for e in reversed(w['A']+w['B'])if not V<=e[1]<2*V]
w['report']['local_profile']=dict(profile)
assert semantic(w)==r['output_semantic_sha256']
after=sum(map(len,g.responses(w)));assert after==r['after_compensation']and before-after==r['total_saved']==624
assert dict(profile)=={int(k):v for k,v in r['profile'].items()}
a.out.mkdir(parents=True,exist_ok=False);(a.out/'FULL-WORD.json.gz').write_bytes(g.dump(w))
receipt=dict(status='PASS_FROZEN_WEIGHTED_COSET_FAMILY',input_semantic_sha256=r['input_semantic_sha256'],output_semantic_sha256=semantic(w),moves=receipts,compensation_before=before,compensation_after=after,total_saved=before-after,profile=dict(profile),scope='Exact rational prefix errors, all protected columns, frame chains and complete compensation table. Native phases, emitted programs and global assembly checked separately.')
(a.out/'WEIGHTED-COSET-REPLAY.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS frozen weighted coset family',len(receipts),before-after)

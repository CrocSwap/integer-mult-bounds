"""Frozen source-bound Steinberg expansion on PR548. No search or network.

New construction: OpenAI Codex assistance for eumemic, Apache-2.0.
PR548 is Dugongue's static44/PR534 frame composition and cold-dirt rewrite,
with the PR535/PR531/PR484 construction lineage and their retained notices.
"""
import argparse,copy,gzip,hashlib,json,sys
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--gk',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
if not __debug__:raise SystemExit('Assertions must remain enabled.')
sys.path.insert(0,str(a.gk.resolve()))
import gk_word as g,gk_common as c
g.V=c.V=112;g.DATA=c.DATA=7168
raw=gzip.decompress(a.input.read_bytes());w=json.loads(raw)
assert hashlib.sha256(raw).hexdigest()=='7f7bf2315c83eb5dc0bb3502ceae575bfcffa00ad37fd32839114744ac18182c'
P=g.profile(w);assert dict(P)=={1:2284,2:456,3:488,4:168,5:56,6:56,8:8}
p,r=936,1048;i,j,k=616,283,299;oldframe=[290,162,98,24,6,1];newframe=[290,162,98,24,6]
e3=w['B'][p];e1=w['B'][r]
assert e3==['add',j,k,1,1,oldframe] and e1==['add',i,j,1,1,oldframe]
def regs(e):return e[1:3]if e[0]=='add'else e[1:2]
def commute(e,f):
 if e[0]=='add'and f[0]=='add':return e[1]!=f[2]and f[1]!=e[2]
 return not set(regs(e))&set(regs(f))
assert all(commute(e1,e)for e in w['B'][p+1:r])
new1=['add',i,j,1,1,newframe];new2=['add',i,k,1,1,newframe];new3=['add',j,k,1,1,newframe]
def exact3(events):
 pos={i:0,j:1,k:2};rows=[{t:Q(1)}for t in range(3)]
 for e in events:
  t,s=pos[e[1]],pos[e[2]];q=Q(e[3],e[4])
  for col,x in rows[s].copy().items():
   z=rows[t].get(col,Q(0))+q*x
   if z:rows[t][col]=z
   else:rows[t].pop(col,None)
 return rows
assert exact3([e3,e1])==exact3([new1,new2,new3])
u=copy.deepcopy(w);u['B']=w['B'][:p]+[new1,new2,new3]+w['B'][p+1:r]+w['B'][r+1:]
u['cleanup']=[g.inverse(e,g.FULL) for e in reversed(u['A']+u['B']) if not 112<=e[1]<224]
PP=g.profile(u);expected=Counter(P);expected.update({1:1,2:-1,3:-1,4:1})
assert PP==expected and sum(r*n for r,n in PP.items())==6012
for key in ('A','ports','cut','precondition','centers','center_frames','scatter','start_extra','target_levels'):assert u[key]==w[key]
u['report']['local_profile']=dict(PP)
out=a.out.resolve();out.mkdir(exist_ok=False);word=g.dump(u);(out/'FULL-WORD.json.gz').write_bytes(word)
contenthash=hashlib.sha256(gzip.decompress(word)).hexdigest();assert contenthash=='6a02824c7484b9fd768a39d87b9c65dbe5221a877032ed1f74d11afb2acdd7d8'
receipt=dict(status='PASS_FROZEN_STEINBERG_V1_CONSTRUCTOR',source_content_sha256=hashlib.sha256(raw).hexdigest(),output_content_sha256=contenthash,section='B',positions=[p,r],commuting_events=r-p-1,old_events=[e3,e1],new_events=[new1,new2,new3],local_profile_before=dict(P),local_profile_after=dict(PP),local_delta={1:1,2:-1,3:-1,4:1},scalar_matrix_identity_exact=True,cleanup_regenerated=True,unchanged_interfaces=True,scope='Exact whole-background scalar identity by commuting exchanges and a3x3 rational identity, plus literal native chain invoice. Independent arbitrary-dirt replay, both reflected ledgers, phases, owners, finite invoice and exact assembly are separate checks.')
(out/'CONSTRUCTION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt['status'],contenthash)

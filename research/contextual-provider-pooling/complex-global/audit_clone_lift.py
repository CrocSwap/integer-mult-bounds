"""Independent exact five-controller source lift. Imports no builder/emitter."""
import argparse, copy, gzip, hashlib, json
from collections import Counter
from pathlib import Path

def raw(p):
 b=p.read_bytes();return gzip.decompress(b)if p.suffix=='.gz'else b

def read(p):return json.loads(raw(p))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def content(p):return hashlib.sha256(raw(p)).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-base',type=Path,required=True);p.add_argument('--clone-base',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--mutation-controls',action='store_true');a=p.parse_args()
 oldpath=a.source_base/'split-centres/GLOBAL-TEMPLATE.json.gz';newpath=a.clone_base/'split-centres/GLOBAL-TEMPLATE.json.gz';old=read(oldpath);new=read(newpath)
 canon=read(a.source_base/'split-centres/CANONICAL-WORD.json.gz');replay=read(a.source_base/'split-centres/INDEPENDENT-LOCAL-REPLAY.json');programs=read(a.source_base/'split-centres/LOCAL-PROGRAMS.json.gz')
 assert canon['v']==112 and canon['R']==504 and canon['h']==9
 assert old['m']==73 and len(old['calls'])==72 and {(c['stage'],c['replica'])for c in old['calls']}=={(s,r)for s in range(9)for r in range(8)}
 assert old['local_programs']==programs and set(programs)=={'forward','backward'}
 assert replay['status']=='PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY'
 assert replay['canonical_word_sha256']==sha(a.source_base/'split-centres/CANONICAL-WORD.json.gz')
 assert replay['local_programs_sha256']==sha(a.source_base/'split-centres/LOCAL-PROGRAMS.json.gz')
 assert all(replay['local'][o]['all_exact_columns']==728 and replay['local'][o]['private_work_erased']for o in programs)
 assert old['physical']-old['live']==canon['R']+len(canon['centers'])+2==514
 assert all(len(c['owners'])==728 and all(0<=f<old['live']for f,route in c['owners'])for c in old['calls'])
 sources={}
 for name in ['split-centres/CANONICAL-WORD.json.gz','split-centres/LOCAL-PROGRAMS.json.gz','split-centres/LOCAL-CHECKS.json','split-centres/INDEPENDENT-LOCAL-REPLAY.json','split-centres/RESIDUAL-ADAPTERS.json','split-centres/CLIFFORD-RECIPES.json','split-centres/CLIFFORD-REVIEW.json','work/complex-nine-native/DATA-PHASES.json']:
  src=a.source_base/name;dst=a.clone_base/name;assert src.read_bytes()==dst.read_bytes(),name;sources[name]=sha(src)
 C=5;D=7168;W=old['live'];assert W>D
 def fam(f,c):
  assert 0<=c<C and 0<=f<old['physical']
  if f<D:return c*D+f
  if f<W:return C*D+c*(W-D)+f-D
  return C*W+f-W
 changed={'calls','live','physical','private_namespace','idle_children','bank_padding','cover_final_correction','execution_schedule'}
 expected=copy.deepcopy(old)
 expected['live']=C*W;expected['physical']=C*W+514
 expected['calls']=[]
 for oc in old['calls']:
  for c in range(C):
   nc=copy.deepcopy(oc);nc['replica']=oc['replica']+8*c;nc['owners']=[[fam(f,c),rt]for f,rt in oc['owners']];expected['calls'].append(nc)
 expected['private_namespace']={k:[C*W+x-W for x in interval]for k,interval in old['private_namespace'].items()}
 expected['idle_children']=[]
 for item in old['idle_children']:
  assert item['replicas']==8;expected['idle_children'].append(item|{'replicas':40})
 expected['bank_padding']['families']=[fam(f,c)for c in range(C)for f in old['bank_padding']['families']]
 expected['bank_padding']['children']=[item|{'family':fam(item['family'],c)}for c in range(C)for item in old['bank_padding']['children']]
 expected['cover_final_correction']=old['cover_final_correction']|{'families':[0,C*W],'charged_calls_per_cover':C*W}
 for e in expected['execution_schedule']:
  if 'replicas'in e:
   assert e['replicas']==list(range(8));e['replicas']=list(range(40))
  if e['kind']=='bank_padding_cover_sweep':e['families']=[C*D,C*W]
  elif e['kind']=='translate_every_live_family':e.update(expected['cover_final_correction'])
 def audit(t):
  assert set(t)==set(old)
  assert {k:t[k]for k in t if k not in changed}=={k:old[k]for k in old if k not in changed}
  assert t==expected,'not the literal namespaced fivefold source'
  bank=set(t['bank_padding']['families']);counts=Counter(f for c in t['calls']for f,rt in c['owners']if f in bank)
  assert set(counts)==bank and set(counts.values())=={8},'each bank remains an eight-replica bank'
  assert len(t['calls'])==360 and len({(c['stage'],c['replica'])for c in t['calls']})==360
  for r in range(40):
   assert [(c['stage'],c['orientation'],c['pair'])for c in t['calls']if c['replica']==r]==[(c['stage'],c['orientation'],c['pair'])for c in old['calls']if c['replica']==r%8]
  assert all(len({f for f,rt in c['owners']})==728 for c in t['calls'])
 audit(new);controls=[]
 if a.mutation_controls:
  def reject(name,mut):
   q=copy.deepcopy(new);mut(q);assert q!=new
   try:audit(q)
   except(AssertionError,KeyError,IndexError,TypeError,ValueError):controls.append(name)
   else:raise AssertionError('accepted '+name)
  reject('collapse clone data namespace',lambda q:q['calls'][1]['owners'][0].__setitem__(0,q['calls'][0]['owners'][0][0]))
  reject('share eight-replica bank across clones',lambda q:q['calls'][1]['owners'][224].__setitem__(0,q['calls'][0]['owners'][224][0]))
  reject('change bank axis-copy route',lambda q:q['calls'][1]['owners'][224][1].__setitem__(-1,39))
  reject('omit cloned bank complement',lambda q:q['bank_padding']['children'].pop())
  reject('understate shared private reserve',lambda q:q.__setitem__('physical',q['physical']-1))
  reject('change immutable ambient rank',lambda q:q.__setitem__('m',74))
  reject('change source replica schedule',lambda q:next(e for e in q['execution_schedule']if 'replicas'in e)['replicas'].pop())
  reject('omit final family correction',lambda q:q['cover_final_correction'].__setitem__('charged_calls_per_cover',q['live']-1))
 report={'status':'PASS_INDEPENDENT_LITERAL_FIVEFOLD_SOURCE_LIFT','ambient_m':73,'clones':5,'replicas_per_clone':8,'replicas_total':40,'calls':360,'literal_owner_entries_checked':262080,'parent_live':W,'cloned_parent_live':5*W,'shared_private_reserve':514,'eight_replicas_per_dedicated_bank':True,'private_work_erasure_bound_to_fresh_replay':True,'immutable_metadata_keys':sorted(set(old)-changed),'source_template_sha256':content(oldpath),'clone_template_sha256':content(newpath),'source_artifacts':sources,'mutations_rejected':controls,'mutation_controls_run':a.mutation_controls,'scope':'Exact finite source lift with shared erased work, disjoint data and separate eight-replica banks. New hosted allocation, coefficient invoice and all-size compiler admission are separate; retained conditional interfaces are unchanged.'}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
if __name__=='__main__':main()

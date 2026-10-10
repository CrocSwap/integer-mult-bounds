"""Exact original-source paths through genuine gauge donor/recipient chains.
Prepared with OpenAI Codex assistance; Apache-2.0.
"""
from pathlib import Path
from collections import Counter,defaultdict
import json,sys,importlib.util
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;P=HERE.parent
spec=importlib.util.spec_from_file_location('gauge_source_boundary_word',P/'joint/joint_word.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
W=m.Candidate();C=W.C;C.decoder();C.geometry()
selection=json.loads((HERE/'selection.json').read_text());old=json.loads((P/'borrow/selection.json').read_text());oldroles={r['role']for r in old};oldpair={r['source']for r in old}|{r['partner']for r in old}
recipient={d:b for b,d in W.pairs};kpair={e['passive']:e for e in W.k['entries']};roots=defaultdict(list)
for j,s in enumerate(W.w['rootroles']):roots[s].append(W.w['root_frame'][j])
sources=set(W.source.values());touched={s for i in W.phase1 for s in W.ops[i][:2]};full=W.w['full_frame']
def histogram(chain):
 assert all(C.sub(a,b)for a,b in zip(chain,chain[1:]));assert all(C.nondeg(f)for f in set(chain))
 h=Counter(C.dimf[b]-C.dimf[a]for a,b in zip(chain,chain[1:])if C.dimf[b]>C.dimf[a])
 dims=[C.dimf[f]for f in chain];refl=[W.h-d for d in reversed(dims)]
 assert h==Counter(b-a for a,b in zip(refl,refl[1:])if b>a)
 return h
results=[];delta=Counter();rawdelta=Counter();used=set(oldpair)
for r in selection:
 s,n,c=r['role'],r['source'],r['partner'];assert s in W.gauge and s not in W.donor and s not in oldroles and s not in sources and s not in touched
 assert n not in used and c not in used;used.update([n,c]);e=kpair[n];assert e['carrier']==c
 z=W.gauge[s];g=z['frame'];p=e['mix_frame'];assert W.readtime[s]==0 and C.sub(p,g)
 assert C.sub(W.w['source_frame'][c],p)and C.sub(p,e['deliver_frame'])
 chain=[g]+[W.opframe[i]for i in W.role_ops[s]]+roots[s]
 if s in recipient:
  b=recipient[s];assert W.last[s]<W.readtime[b]
  chain += [W.gauge[b]['frame']]+[W.opframe[i]for i in W.role_ops[b]]+roots[b]
 chain += [full]
 oldaux=histogram(chain);oldpassive=histogram(e['passive_chain']);newchain=[W.w['source_frame'][n],p]+chain;newhist=histogram(newchain)
 got=Counter(newhist);got.subtract(oldaux);got.subtract(oldpassive);got={k:v for k,v in got.items()if v}
 assert got=={z['dim']-2:1,22:-1}
 delta.update(got)
 for k,v in got.items():rawdelta[k]+=3*v
 rawdelta[3*z['dim']]-=1
 results.append(dict(role=s,source=n,partner=c,gauge_dimension=z['dim'],aliased_recipient=recipient.get(s),old_aux_histogram=dict(oldaux),old_source_histogram=dict(oldpassive),new_source_histogram=dict(newhist),new_source_frame_dimensions=[C.dimf[f]for f in newchain],reflected_histogram_equal=True,local_delta=got))
assert len(results)==3 and Counter(r['gauge_dimension']for r in results)=={19:3}
assert dict(delta)=={17:3,22:-3};assert dict(rawdelta)=={17:9,22:-9,57:-3};assert sum(k*v for k,v in rawdelta.items())==-216
out=dict(status='PASS_EXACT_GAUGE_SOURCE_AND_REFLECTED_BOUNDARIES',results=results,local_delta=dict(delta),raw_child_delta=dict(rawdelta),physical_stock_delta=-3,rank_mass_delta=-216,deficit_delta=0,all_original_source_start_frames_preserved=True,all_source_end_frames_full=True,all_carrier_target_anchors_preserved=True,all_borrowed_gauge_reads_after_original_source_injections_and_partner_mix=True)
(HERE/'boundary.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS3 actual gauge/source/reflected paths',dict(rawdelta),flush=True)

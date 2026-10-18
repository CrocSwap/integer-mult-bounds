"""Bind a new word to exactly the old width slots; admission remains separate."""
import argparse,gzip,json,hashlib,importlib.util,copy
from pathlib import Path
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[3];PRE=ROOT/'research/k8-three-demotions'
def rd(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
ap=argparse.ArgumentParser();ap.add_argument('--native',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();local=a.native/'local';out=a.out;assert not out.exists();out.mkdir()
word=rd(local/'CANONICAL-WORD.json.gz');checks=rd(local/'LOCAL-CHECKS.json');plan=rd(PRE/'PLAN.json.gz');oldroles=rd(PRE/'OWNERS.json.gz');oldwidths=plan['provider_registry']['gauge44']['widths']
widths=[len(word['frames'][word['final'][224+h]])-len(word['frames'][word['start'][224+h]]) for h in range(480)];assert Counter(widths)==Counter(oldwidths);assert (word['v'],word['h'],word['R'])==(112,9,480)
# Keep every unchanged helper slot. Pair moved helpers by equal occupied width.
remap={h:h for h in range(480) if oldwidths[h]==widths[h]}
moved=set(range(480))-set(remap)
for width in sorted(set(widths)):
 old=[h for h in range(480) if h in moved and oldwidths[h]==width]
 new=[h for h in range(480) if h in moved and widths[h]==width]
 assert len(old)==len(new)
 remap.update(zip(old,new))
assert len(remap)==len(set(remap.values()))==480
roles=copy.deepcopy(oldroles)
for r in roles:r['helper']=remap[r['helper']];assert r['width']==widths[r['helper']]
roles.sort(key=lambda z:(z['time'],z['helper']))
raw=json.dumps(roles,sort_keys=True,separators=(',',':')).encode();(out/'OWNERS.json.gz').write_bytes(gzip.compress(raw,mtime=0));plan['assignment_sha256']=hashlib.sha256(raw).hexdigest()
used=Counter();families=defaultdict(set);intervals=defaultdict(list)
for z in roles:
 key=z['owner_replica'],z['child'],z['port'];cp,times=plan['windows'][f'{key[0]},{key[1]}'];assert z['time'] in times and z['family'] not in families[z['time']];families[z['time']].add(z['family']);used[key]+=z['width'];intervals[key].append((z['offset'],z['offset']+z['width']))
for key,vs in intervals.items():
 vs.sort();assert all(a[1]<=b[0] for a,b in zip(vs,vs[1:]));assert vs[-1][1]<=plan['windows'][f'{key[0]},{key[1]}'][0]
idle=Counter()
for key,(cap,times) in plan['windows'].items():
 rep,ch=map(int,key.split(','))
 for port in range(112):
  rem=cap-used[rep,ch,port];assert rem>=0
  if rem:idle[rem]+=1
assert dict(idle)=={1:360,24:1,48:4918}
H=Counter({int(r):144*n for r,n in word['local_profile'].items()});H.update(idle);assert 73*14336-sum(r*n for r,n in H.items())==5120
plan['profile']={str(r):n for r,n in sorted(H.items())};desc=plan['provider_registry']['gauge44'];assert word['ports']==desc['ports'] and word['centers']==desc['centers'];desc['widths']=widths;desc['actual_paid_profile']=word['local_profile']
p=ROOT/'research/k8-eight-ends-t16/vendor/pr1074/code/generated_identity.py';s=importlib.util.spec_from_file_location('ident',p);ident=importlib.util.module_from_spec(s);s.loader.exec_module(ident)
desc.update(artifact_sha256={name:sha(local/name) for name in ident.FILES},artifact_semantic_sha256=ident.artifact_identities(local),orientation_program_sha256={o:c['sha256'] for o,c in checks.items()})
for c in plan['provider_calls']:c['local_program_sha256']=checks[c['orientation']]['sha256']
for c in plan['per_call_widths']:c['widths']=widths
plan.update(status='NOMINATED_EQUAL_WIDTH_INTERFACE_SUBSTITUTION_REQUIRES_STRICT_ADMISSION',solver_status='Exact equal-width permutation of frozen whole-helper slots',gap=None)
dump(out/'PLAN.json',plan)
spec=rd(PRE/'SPEC.json');spec.update(name='k8-joint-entrances',providers={},expected={'gain_baseline_kappa':spec['expected']['gain_baseline_kappa']},data={'plan_sha256':sha(out/'PLAN.json'),'owners_sha256':sha(out/'OWNERS.json.gz')});dump(out/'SPEC.json',spec)
dump(out/'PREPARATION.json',dict(status='PASS_EXACT_WIDTH_SLOT_SUBSTITUTION_NOMINATION',helper_permutation={k:v for k,v in remap.items() if k!=v},width_inventory=dict(sorted(Counter(widths).items())),idle=dict(sorted(idle.items())),local_profile=word['local_profile'],global_profile=dict(sorted(H.items())),old_owners_sha256=sha(PRE/'OWNERS.json.gz'),new_owners_sha256=sha(out/'OWNERS.json.gz')))
print('PASS_WIDTH_SLOT_SUBSTITUTION',dict(H))

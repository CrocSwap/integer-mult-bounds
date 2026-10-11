from pathlib import Path
from fractions import Fraction as Q
import copy,hashlib,json,subprocess,sys
assert __debug__
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent/'e8-shared-donor-chains'
sys.path.insert(0,str(ROOT/'vendor426/vendor/source376'));sys.path.insert(0,str(ROOT/'vendor426'));import inline,exact
sys.path.insert(0,str(ROOT/'vendor423'));import common as C
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source,out=map(Path,sys.argv[1:3]);expected=read(ROOT/'EXPECTED.json');assert sha(source)==expected['source_sha256'] and not out.exists();out.mkdir(parents=True)
subprocess.run([sys.executable,'-B',str(ROOT/'vendor423/construct.py'),str(source),str(ROOT/'ENLARGEMENT-SELECTION.json'),str(out/'enlarged'),'--source-sha256',expected['source_sha256'],'--expected-sha256',expected['enlarged_sha256']],check=True)
plans=read(ROOT/'INLINE-SELECTION.json');reports=[]
def build(c,gauged):
 original_map,_=exact.rawmap(c);removed=[];records=[]
 for pl in plans:
  mapped=lambda r:r-sum(k<r for k in removed)
  drop=mapped(pl['original_helper']);terms={mapped(int(k)):Q(v) for k,v in pl['terms'].items()};ext=dict(c['ext']);old_count=len(ext)
  removed_gates=[]
  if gauged:
   assert drop in ext
   ids=[i for i,g in enumerate(c['A']) if any(s==drop for s,a,b in g[3]) and g[1]==ext[drop]]
   assert len(ids)==2 and all(g[2]!=drop for g in c['A'][:min(ids)+1]);removed_gates=[c['A'][i] for i in ids]
   c['A']=[g for i,g in enumerate(c['A']) if i not in set(ids)];c['start'][drop]=0;c['ext']=[[p,f] for p,f in c['ext'] if p!=drop];C.rehist_and_audit(c)
  else:assert not ext
  proposed={p:ts for p,ts,count in inline.proposals(c,4)};assert proposed[drop]==terms
  # Wrong coefficient and self-dependent substitutions cannot match the derived proposal.
  bad=dict(terms);bad[next(iter(bad))]+=1;assert proposed[drop]!=bad
  assert drop not in proposed[drop]
  before=copy.deepcopy(c);c=inline.repair(c,drop,terms);c['ext']=[[p-(p>drop),f] for p,f in before['ext']];C.rehist_and_audit(c)
  rows,tot=exact.rawmap(c)
  assert all({k:v for k,v in rows[t].items() if k<240}=={k:v for k,v in original_map[t].items() if k<240} for t in range(240))
  assert all(not rows[t].get(p,Q(0)) for p,f in c['ext'] for t in range(120,240))
  assert len(c['ext'])==old_count-int(gauged)
  records.append(dict(original_helper=pl['original_helper'],drop=drop,terms={str(k):str(v) for k,v in terms.items()},removed_gauge_shears=removed_gates,R=c['R'],gauges=len(c['ext']),protected_columns=True,gauged_zero=True,wrong_coefficient_rejected=True));removed.append(pl['original_helper'])
 return c,records
c,checks=build(read(out/'enlarged/candidate.json'),True);helper,hchecks=build(read(SOURCE/'inputs/helper781.json'),False)
for name,z,want in [('candidate.json',c,expected['candidate_sha256']),('helper779.json',helper,expected['helper_baseline_sha256'])]:
 (out/name).write_bytes(json.dumps(z,sort_keys=True,separators=(',',':')).encode());assert sha(out/name)==want
head=len(c['A'])-len(helper['A']);strip=lambda gs:[[g[0]]+g[2:] for g in gs]
assert strip(c['A'][head:])==strip(helper['A']);assert all(c[k]==helper[k] for k in ['h','v','R','cst','ports','ret','scat','final'])
(out/'RESULT.json').write_text(json.dumps(dict(status='PASS_GAUGED_INLINING_PROTECTED_COLUMNS_AND_REFERENCE_RECONSTRUCTION',candidate_sha256=expected['candidate_sha256'],helper_baseline_sha256=expected['helper_baseline_sha256'],head_gates=head,steps=checks,helper_steps=hchecks),indent=2)+'\n')

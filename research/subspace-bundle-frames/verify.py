#!/usr/bin/env python3
"""Replay changed physical frames, terminal compiler, formal columns and assembly.
Default also replays the complete original bit/complex baseline. All new
claims retain the original conditional compiler and analytic interfaces.
"""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as Q
import argparse,gzip,io,json,subprocess,sys,tempfile,zipfile
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(0)
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
BASE=ROOT/'research/coordinated-frames-and-entrance-banks';CAND=HERE/'candidate'

def digest(p):return sha256(p.read_bytes()).hexdigest()
def js(v):
 if isinstance(v,Q):return str(v)
 if isinstance(v,dict):return {str(k):js(x) for k,x in v.items()}
 if isinstance(v,(list,tuple)):return [js(x) for x in v]
 return v
def run(command):subprocess.run([sys.executable,'-B',*map(str,command)],check=True)
def load(n):return json.loads(gzip.decompress((CAND/(n+'.json.gz')).read_bytes()))

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');ap.add_argument('--changed-witness-only',action='store_true');a=ap.parse_args()
 if sys.flags.optimize:raise ValueError('Assertions must be enabled; run without -O or -OO')
 assert digest(BASE/'FILES.json')=='99709b85d987556593f237b0aacf314b2d7982fb4f494378d6dbf03391228ede'
 assert digest(BASE/'certificate.json')=='59b20818af6f850f40d18fd8206b136da504d9cbc57dbbefcba232c62f3384e6'
 for n,h in json.loads((BASE/'FILES.json').read_text())['files'].items():assert digest(BASE/n)==h,n
 if not a.changed_witness_only:run([BASE/'verify.py'])
 pins=json.loads((CAND/'result.json').read_text())['pins']
 for n,h in pins.items():assert digest(CAND/n)==h,n
 # Only operation frames and their recounted physical profile may change.
 for name in ['graph','baseline','frames','word','profile-before','physical-pairs']:
  assert digest(CAND/(name+'.json.gz'))==digest(BASE/'selected/complex'/(name+'.json.gz')),name
 baseline=json.loads((BASE/'certificate.json').read_text())
 with tempfile.TemporaryDirectory(prefix='frame-improvement-') as tmp:
  tmp=Path(tmp);source=tmp/'source';source.mkdir()
  archive=json.loads((BASE/'BASELINE.json').read_text());blob=b''.join((BASE/p['file']).read_bytes() for p in archive['parts'])
  assert sha256(blob).hexdigest()==archive['archive_sha256']
  with zipfile.ZipFile(io.BytesIO(blob)) as z:
   for e in z.infolist():assert (source/e.filename).resolve().is_relative_to(source.resolve())
   z.extractall(source)
  physical_path=tmp/'physical.json';selection_path=tmp/'sinks.json';formal_path=tmp/'formal.json'
  run([BASE/'complex/physical.py','--candidate',CAND,'--source',source,'--out',physical_path])
  run([BASE/'complex/check_sinks.py','--candidate',CAND,'--output',selection_path])
  run([BASE/'complex/formal_sinks.py','--candidate',CAND,'--selection',selection_path,'--formal-helper',BASE/'complex/physical.py','--output',formal_path])
  physical=json.loads(physical_path.read_text());sinks=json.loads(selection_path.read_text());formal=json.loads(formal_path.read_text())
  assert sinks['eligible_count']==46
  old_sinks=json.loads((BASE/'selected/complex/sinks.json').read_text())
  assert [(s['role'],s['pivot'],s['writes']) for s in sinks['sinks']]==[(s['role'],s['pivot'],s['writes']) for s in old_sinks['sinks']]
  row=dict(baseline['complex']['profile'])
  row.update(R=sinks['new_physical_R'],W_per_vertex=sinks['new_W'],rank_per_vertex=sinks['new_rank'],
   child_histogram=sinks['child_histogram'],maxchild=max(map(int,sinks['child_histogram'])))
  assert all(c['dirty']==row['R'] and c['columns']==row['W_per_vertex'] for c in formal['columns'])
  sys.path.insert(0,str(BASE/'arithmetic'))
  from interval_moment import saving_grid
  from certificate import bridge,assembly,BETA,ETA,WEAKENING
  p=dict(m=row['m'],W=row['W_per_vertex'],N=row['deficit_per_vertex'],L=0,total_rank=row['rank_per_vertex'],maxchild=row['maxchild'],child_multiplicities=row['child_histogram'])
  proof=saving_grid(p,10**24);b=proof['accepted']['saving'];finite=bridge(row)
  bit=finite['bit_uniform']['ordinary_saving'];transfer=min(bit,(1-BETA)*b-WEAKENING)
  q=transfer*(1-2*ETA);G=(1-ETA)*q/(1+q);x=G*10**24;k=Q(-(-x.numerator//x.denominator)-1,10**24)
  composed=assembly(finite,row,transfer,k,beta=BETA,h=ETA,a_complex=b)
  oldk=Q(baseline['kappa']);previous=Q(331325992674373,5*10**17);assert k>previous
  assert len(composed['constraints'])==47 and min(composed['constraints'].values())>0
  assert js(finite['rows'])==baseline['arithmetic']['bridge']['rows'],'Row cost changed'
  for field in ('local_group_upper','logical_group_upper','scalar_group_upper','finite_group_router_upper'):
   assert js(finite['complex'][field])==baseline['arithmetic']['bridge']['complex'][field],'Scalar/routing cost changed'
  for bad in [G,k+Q(1,10**24)]:
   try:assembly(finite,row,transfer,bad,beta=BETA,h=ETA,a_complex=b)
   except ValueError:pass
   else:raise AssertionError('Non-strict kappa accepted')
  # Normalize machine-dependent timing and temporary paths out of receipts.
  for receipt in (physical,sinks,formal):
   for key in ('seconds','maxrss','rss_kib'):receipt.pop(key,None)
  physical['source_sha256']={Path(n).name:h for n,h in physical['source_sha256'].items()}
  # The generated selection includes timing/RSS before normalization. Its
  # semantic contents are already retained in result['sinks']; do not pin
  # the nondeterministic raw serialization in the formal receipt.
  formal['input_pins'].pop(selection_path.name,None)
  result=js(dict(status='PASS changed complete witness and exact assembly',
   scope='Conditional physical frame improvement; unchanged bit supplier and inherited analytic/compiler contracts.',
   baseline_kappa=oldk,previous_kappa=previous,kappa=k,absolute_improvement=k-oldk,relative_improvement=k/oldk-1,improvement_over_previous=k-previous,
   profile=row,complex_moment=proof,assembly=composed,
   physical=physical,sinks=sinks,formal=formal,input_pins=pins))
  path=HERE/'certificate.json'
  if a.write:path.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
  else:assert json.loads(path.read_text())==result,'Certificate replay differs'
  print('PASS physical frame improvement kappa='+str(k),flush=True)
  print('Approximate relative improvement',float(k/oldk-1),flush=True)

if __name__=='__main__':main()

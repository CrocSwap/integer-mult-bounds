"""Portable replay of the frozen free-carrier proportional-pair result.
Jerry Chen / @CubeJerry with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from hashlib import sha256
from math import isqrt
import contextlib,io,json,runpy,sys,tempfile
HERE=Path(__file__).resolve().parent

def need(ok,why):
 if not ok:raise ValueError(why)
def invoke(name,args):
 old=sys.argv;sys.argv=[str(HERE/name),*map(str,args)]
 try:
  with contextlib.redirect_stdout(io.StringIO()):return runpy.run_path(str(HERE/name),run_name='__main__')
 finally:sys.argv=old

def main():
 need(all(65521%d for d in range(2,isqrt(65521)+1)),'Prime reduction modulus')
 for item in json.loads((HERE/'ORIGINS.json').read_text())['files']:
  need(sha256((HERE/item['path']).read_bytes()).hexdigest()==item['sha256'],'Pinned bytes '+item['path'])
 with tempfile.TemporaryDirectory(prefix='p104-pair-')as temp:
  temp=Path(temp);census=temp/'CENSUS.json'
  invoke('save_census.py',[census]);record=json.loads(census.read_text())
  digest=sha256(json.dumps(record,sort_keys=True,separators=(',',':')).encode()).hexdigest()
  need(digest==json.loads((HERE/'CENSUS-SUMMARY.json').read_text())['canonical_sha256'],'Complete exact rational census hash')
  shared=invoke('adjacent.py',[temp/'shared.json']);disjoint=invoke('disjoint.py',[temp/'disjoint.json'])
  for actual,expected in [('shared.json','SHARED.json'),('disjoint.json','DISJOINT.json')]:need(json.loads((temp/actual).read_text())==json.loads((HERE/expected).read_text()),'Complete receipt '+expected)
  checked=invoke('forward_targets.py',[temp]);need(len(checked['checks'])==122,'All forward combined-error checks')
  solve=disjoint['solve'];nodes=[(0,0,{0:1,1:2},'A'),(0,1,{1:1,2:3},'E')]
  need(solve(nodes,{0:4,1:13,2:15})[0]is not None,'Positive span fixture')
  need(solve(nodes,{0:4,1:13,2:16})[0]is None,'Outside-span fixture')
  need(solve([],{})[0]=={}and solve([],{0:1})[0]is None,'Empty span controls')
  for c in shared['intervals']+disjoint['iv']:need(c['target'],'Every combined target is nonzero')
  invoke('review_pairs.py',[HERE,HERE/'retained/forward_ssa.py',census,HERE/'inputs/PR6702-WORD.json.gz',temp/'independent.json'])
  need(json.loads((temp/'independent.json').read_text())==json.loads((HERE/'INDEPENDENT-REVIEW.json').read_text()),'All independently regenerated dual certificates')
 print('PASS_P104_PAIRED_CARRIER_OBSTRUCTION: 122 pairs, 687 systems, exact census, forward errors, independent SSA and 9199 dual dot checks; no paid-stop claim')
if __name__=='__main__':main()

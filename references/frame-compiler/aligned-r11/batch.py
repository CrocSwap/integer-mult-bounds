"""Aligned PR74 working graphs with independently audited R10 additions.
Never rerun the supplied foreign baseline as a prerequisite. Own R10 canaries
guard engine/driver preservation; all new words receive full physical checks.
"""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as Q
from concurrent.futures import ProcessPoolExecutor,as_completed
import argparse,itertools,json,subprocess,sys,time
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from graph_batch import generate
def run(job):
 h,config=job
 return generate(h,**config)
def jobs(h):
 old=json.loads((ROOT/'R10_FROZEN.json').read_text())['axes'][str(h)]
 new=json.loads((ROOT/'references/pr74-aligned/research/aligned-exchange-frames/selection.json').read_text())['axes'][str(h)]
 configs=[]
 for key,pricing,cycles,coords in itertools.product(('pr74','cover-minus-core-minus'),(False,True),(0,3),('old','new')):
  if (key,pricing,cycles,coords)==('pr74',True,0,'new'):continue
  configs.append(dict(groups=new['groups'],anchor_pairs=new['anchor_pairs'],coarse_word=new['coarse_word'],mode='envelope-half',output_mode=old['output_mode'],coordinate=old['coordinate_permutation'] if coords=='old' else new['coordinate_permutation'],label=f'{key}-pricing{int(pricing)}-cycles{cycles}-{coords}',pricing=pricing,three_cycle_passes=cycles,node_order=key))
 return [(h,c) for c in configs]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--h',type=int,choices=(23,25),required=True);ap.add_argument('--workers',type=int,default=8);args=ap.parse_args();assert 1<=args.workers<=8
 manifest=json.loads((ROOT/'SOURCE.json').read_text())
 for name,digest in manifest['files'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
 print('SOURCE PASS',len(manifest['files']),sha256((ROOT/'SOURCE.json').read_bytes()).hexdigest(),flush=True)
 h=args.h;old=json.loads((ROOT/'R10_FROZEN.json').read_text());a=old['axes'][str(h)];rows=[];started=time.monotonic()
 canary=generate(h,a['groups'],mode='envelope-half',output_mode=a['output_mode'],coordinate=a['coordinate_permutation'],label='own-r10-canary',pricing=a['oracle_coordinate_pricing'],three_cycle_passes=a['three_cycle_passes'],node_order=a['node_order'])
 assert canary['word_sha256']==a['word_sha256'] and canary['kappa']==old['kappa']
 assert json.loads((ROOT/canary['path']/'profiles.json').read_text())==a['paid_profile']
 print('CANARY PASS',json.dumps(canary),flush=True)
 alljobs=jobs(h)
 with ProcessPoolExecutor(max_workers=args.workers) as pool:
  for f in as_completed([pool.submit(run,j) for j in alljobs]):
   row=f.result();rows.append(row);receipt=dict(h=h,complete=False,source_sha256=sha256((ROOT/'SOURCE.json').read_bytes()).hexdigest(),canary=canary,rows=rows,expected_cases=len(alljobs),validated_cases=len(rows),wall_seconds=time.monotonic()-started)
   temp=ROOT/'progress.tmp';temp.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');temp.replace(ROOT/'progress.json');print('RESULT',json.dumps(row),flush=True)
 receipt.update(complete=True,best_axis=max(rows,key=lambda r:Q(r['kappa'])),wall_seconds=time.monotonic()-started)
 (ROOT/'progress.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print('COMPLETE',h,flush=True)
if __name__=='__main__':main()

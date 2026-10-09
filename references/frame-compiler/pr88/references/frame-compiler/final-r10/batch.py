"""Final bounded factorial composition with exact parent canaries."""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as Q
from concurrent.futures import ProcessPoolExecutor,as_completed
import argparse,json,subprocess,sys,time
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from graph_batch import generate,load

def run(job):
 h,node_order,pricing,passes,label=job
 parent=json.loads((ROOT/'CANDIDATE_PARENT.json').read_text())[str(h)]
 return generate(h,parent['groups'],mode='envelope-half',output_mode=parent['output_mode'],coordinate=parent['coordinate_permutation'],label=label,pricing=pricing,three_cycle_passes=passes,node_order=node_order)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--h',type=int,choices=(23,25),required=True);ap.add_argument('--workers',type=int,default=8);args=ap.parse_args();assert 1<=args.workers<=8
 manifest=json.loads((ROOT/'SOURCE.json').read_text())
 for path,digest in manifest['files'].items():assert sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
 print('SOURCE PASS',len(manifest['files']),sha256((ROOT/'SOURCE.json').read_bytes()).hexdigest(),flush=True)
 subprocess.run([sys.executable,str(ROOT/'test_order.py')],check=True)
 subprocess.run([sys.executable,str(ROOT/'test_three_cycles.py')],check=True)
 parent=json.loads((ROOT/'CANDIDATE_PARENT.json').read_text())[str(args.h)];rows=[];started=time.monotonic();h=args.h
 row=run((h,'pr74',False,0,'canary'));assert row['word_sha256']==parent['word_sha256'];assert row['kappa']==parent['kappa'];assert json.loads((ROOT/row['path']/'profiles.json').read_text())==json.loads((ROOT/f'candidate-parent/h{h}/profiles.json').read_text());rows.append(row);print('CANARY',json.dumps(row),flush=True)
 jobs=[(h,key,pricing,passes,f'{key}-pricing{int(pricing)}-cycles{passes}') for key in ('pr74','cover-minus-core-minus') for pricing in (False,True) for passes in (0,3) if (key,pricing,passes)!=('pr74',False,0)]
 with ProcessPoolExecutor(max_workers=args.workers) as pool:
  for future in as_completed([pool.submit(run,job) for job in jobs]):
   row=future.result();rows.append(row);receipt={'h':h,'complete':False,'validated_cases':len(rows),'expected_cases':8,'rows':rows,'wall_seconds':time.monotonic()-started}
   temp=ROOT/'progress.tmp';temp.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');temp.replace(ROOT/'progress.json');print('RESULT',json.dumps(row),flush=True)
 best=max(rows,key=lambda row:Q(row['kappa']));receipt.update(complete=True,best_axis=best,wall_seconds=time.monotonic()-started)
 (ROOT/'progress.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print('COMPLETE',json.dumps({k:v for k,v in receipt.items() if k not in ('rows','best_axis')}),flush=True)
if __name__=='__main__':main()

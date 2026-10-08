from pathlib import Path
from hashlib import sha256
from concurrent.futures import ProcessPoolExecutor,as_completed
import gzip,json,subprocess,sys,time,importlib.util
HERE=Path(__file__).resolve().parent;WORK=HERE.parent
CHECKERS=Path('/Users/chafreaky/Documents/personal/integer-mult-research-20261008/joint-reclaim/scripts/experiments')
sys.path[:0]=[str(CHECKERS),str(WORK/'frontier74-search')]
from nodeops import relabel
from binary_frame_replay import replay
from binary_frame_profile_prepare import prepare

def run(case):
 h,label,perm,parent=case;start=time.monotonic();out=HERE/f'h{h}-{label}';out.mkdir(exist_ok=True)
 original=gzip.decompress((parent/'word.json.gz').read_bytes());parent_record=json.loads((parent/'result.json').read_text());assert sha256(original).hexdigest()==parent_record['word_sha256']
 word=relabel(json.loads(original),perm);raw=(json.dumps(word,separators=(',',':'))+'\n').encode();path=out/'word.json.gz';path.write_bytes(gzip.compress(raw,mtime=0));checked=replay(path);(out/'replay.json').write_text(json.dumps(checked,indent=2)+'\n')
 trans=prepare(path,out/'transitions.bin');(out/'transitions.json').write_text(json.dumps(trans,indent=2)+'\n')
 with (out/'profiles.log').open('w') as log:subprocess.run([str(WORK/'joint-dual-search/profiles'),str(out/'transitions.bin')],check=True,stdout=log,stderr=log)
 (out/'profiles.json').write_bytes((out/'transitions.bin.profiles.json').read_bytes());p=json.loads((out/'profiles.json').read_text());assert p['R']==checked['roles']==parent_record['roles'] and p['crt_disagreements']==0
 summary={'h':h,'label':label,'permutation':perm,'parent_word_sha256':sha256(original).hexdigest(),'word_sha256':sha256(raw).hexdigest(),'roles':p['R'],'full_physical_replay':'PASS both orientations','exact_CRT_profiles':'PASS','seconds':time.monotonic()-start}
 (out/'result.json').write_text(json.dumps(summary,indent=2)+'\n');return summary

def main():
 jobs=[]
 for h,d in [(23,'column'),(25,'row-late')]:
  parent=WORK/'spark-results'/('spark' if h==23 else 'spark2')/'envelope-r5/results'/f'{h}-{411 if h==23 else 141}-envelope-half'
  perm74=json.loads((WORK/'frontier74-search/source/research/balanced-split-frames/selection.json').read_text())['axes'][str(h)]['coordinate_permutation']
  config78=json.loads((WORK/f'frontier78-search/source/research/coordinate-flags/order-{h}.json').read_text());perm78=[config78['mapping'][str(i)] for i in range(h)]
  permutations={'pr74':perm74,'pr78':perm78,'reverse':list(reversed(range(h))),'pair-swap':[i^1 if i<h-1 else i for i in range(h)]}
  for shift in (-2,-1,1,2):permutations['shift'+str(shift)]=[(i+shift)%h for i in range(h)]
  for label,perm in permutations.items():assert sorted(perm)==list(range(h));jobs.append((h,label,perm,parent))
 start=time.monotonic();rows=[]
 with ProcessPoolExecutor(max_workers=4) as pool:
  for task in as_completed([pool.submit(run,j) for j in jobs]):
   rows.append(task.result());(HERE/'results.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows[-1]),flush=True)
 print('COMPLETE',len(rows),time.monotonic()-start,flush=True)
if __name__=='__main__':main()

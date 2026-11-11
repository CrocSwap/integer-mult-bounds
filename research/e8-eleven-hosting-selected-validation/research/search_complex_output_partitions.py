"""Exact clean-word search over #433 target-pair partition choices.
Scores the current hosted profile; improvements still need arbitrary-dirt and phase replay.
"""
from pathlib import Path
from collections import Counter
import os,json,gzip,hashlib,itertools,contextlib,io,time
r=Path.cwd();assert os.path.ismount('/Volumes/SP AI 01_16') and os.access(r,os.W_OK)
source=r/'early-reuse-publication/research/split-centres-global/code/complex_construct.py';raw=source.read_text();out=r/'complex447-partitions';out.mkdir(exist_ok=True)
raw=raw.replace("INPUT=Path('work/complex-network/hamming');OUT=Path('split-centres');OUT.mkdir(exist_ok=True);", "INPUT=INPUT_OVERRIDE;OUT=OUT_OVERRIDE;OUT.mkdir(exist_ok=True);")
raw=raw.replace('selected=(pi==parity)',"selected=(pi==CHOICES[tuple(c)][parity])")
code=compile(raw,str(source),'exec');modules=json.loads(gzip.decompress((r/'hosted138-screen/work/complex-network/hamming/PACKET-PROGRAMS.json.gz').read_bytes()));blocks=sorted(tuple(z['receipt']['block']) for z in modules)
baseline=json.loads((r/'hosted138-screen/split-centres/LOCAL-CHECKS.json').read_text())['forward']['paid_profile'];baseline={int(k):v for k,v in baseline.items()};reference=json.loads((r/'hosted138-screen/complex/HOSTED.json').read_text());paid={int(k):v for k,v in reference['global_profile'].items()};c=.001267453159029119
import math
cost=lambda H:sum(k*n*math.expm1(c*math.log(73/k)) for k,n in H.items())
basecost=cost(paid);results=[];start=time.monotonic()
configs=[('baseline',{b:(0,1) for b in blocks})]
for i,b in enumerate(blocks):
 for x,y in itertools.permutations(range(3),2):
  if (x,y)==(0,1):continue
  choices={bb:(0,1) for bb in blocks};choices[b]=(x,y);configs.append((f'block{i}-{x}{y}',choices))
for tag,choices in configs:
 d=out/tag
 try:
  with contextlib.redirect_stdout(io.StringIO()):exec(code,dict(INPUT_OVERRIDE=(r/'hosted138-screen/work/complex-network/hamming').resolve(),OUT_OVERRIDE=d,CHOICES=choices))
  report=json.loads((d/'FULL-DISCOVERY.json').read_text());H={int(k):v for k,v in report['local_profile'].items()};assert report['R']==560
  if tag=='baseline':assert H==baseline
  P=Counter(paid)
  for k,n in baseline.items():P[k]-=72*n
  for k,n in H.items():P[k]+=72*n
  assert all(n>=0 for n in P.values()) and sum(k*n for k,n in P.items())==73*8400-2496
  score=cost(P);result=dict(tag=tag,score=score,delta=score-basecost,profile=H,choices=[[list(b),list(xy)] for b,xy in choices.items()],status='CLEAN_WORD_PASS_NOMINATION_ONLY')
 except Exception as e:result=dict(tag=tag,status='FAIL',error=repr(e))
 results.append(result);print(tag,result['status'],result.get('delta'),flush=True)
 (out/'PROGRESS.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),reference_cost=basecost,results=results),indent=2)+'\n')
positives=[x for x in results if x.get('delta',0)<-1e-12]
(out/'SUMMARY.json').write_text(json.dumps(dict(status='PARTITION_SCREEN_COMPLETE',tested=len(results),positive=len(positives),best=sorted(positives,key=lambda x:x['delta']),failures=[x for x in results if x['status']=='FAIL'],seconds=time.monotonic()-start),indent=2)+'\n');print('FINAL',len(results),len(positives),flush=True)

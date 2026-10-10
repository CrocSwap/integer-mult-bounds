"""Check the special target-role/covector contract for every changed gate."""
import argparse,hashlib,json,struct
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('export',type=Path);ap.add_argument('lead',type=Path);args=ap.parse_args()
X,L=args.export,args.lead
r=json.loads((L/'PLATEAU-RETIMING.json').read_text());st=json.loads((X/'249-states.json').read_text());v,n=st['v'],st['n'];raw=(L/'COHORT249-RECORDS.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['output_sha256']
events=[e for e in struct.iter_unpack('<6i',raw) if e[0]]
fs=json.loads((X/'frames.json').read_text())['frames'];fs.update(json.loads((L/'COHORT249-FRAMES.json').read_text()))
count=0;frames=set()
for c in r['selected']:
 frame=fs[str(c['new_frame'])];assert frame['dim']==0 and frame['B']==[]
 assert frame['A']==[[int(i==j) for j in range(24)] for i in range(24)]
 for g in c['gates']:
  op,a,b,scalar,f,category=events[g]
  assert op==1 and v<=a<2*v and v<=b<2*v and a!=b and category==31
  assert f==c['new_frame'] and scalar&1 and a!=n and b!=n
  # The zero frame has no basis rows. Every inherited target covector
  # annihilates it; both target endpoint caps therefore hold exactly.
  assert all(sum(x*y for x,y in zip(row,covector))==0 for row in frame['B'] for covector in fs[str(st['final'][str(a)])]['A'])
  count+=1;frames.add(f)
out={'status':'PASS_PURE_TARGET_RESTORES_EXACT_ZERO_FRAME_CAPS','changed_gates':count,'zero_frames':sorted(frames),'non_target_operands':0,'word_sha256':hashlib.sha256(raw).hexdigest(),'scope':'Target classification/covector caps only; full geometry, arbitrary-column endpoints and literal price checked separately.'};(L/'TARGET-ROLE-AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))

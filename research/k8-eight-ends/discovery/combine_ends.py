import screen_end_groups as S
from pathlib import Path
import json,gzip,copy,itertools
P=Path(__file__).resolve().parent;groups=json.loads((P/'END-GROUPS.json').read_text());results=[]
for count in [2,3,4]:
 for ids in itertools.combinations([12,13,14,15],count):
  nw=copy.deepcopy(S.w)
  for i in ids:
   for q in groups[i]['helpers']:nw['helper_final'][str(q)]=groups[i]['new']
  nw=S.optimize(nw);r=dict(groups=ids,profile=nw['report']['local_profile'],**S.screen(nw));results.append(r);name='end-combo-'+'-'.join(map(str,ids));(P/(name+'.json.gz')).write_bytes(gzip.compress(json.dumps(nw,sort_keys=True,separators=(',',':')).encode(),mtime=0));print(json.dumps(r),flush=True);(P/'END-COMBINATIONS.json').write_text(json.dumps(results,indent=2)+'\n')

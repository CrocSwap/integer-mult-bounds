from pathlib import Path
import gzip,json,collections
R=Path('research');d=json.loads(gzip.decompress((R/'warp-interface-20261022/ACTUAL-WORD.json.gz').read_bytes()));c=d['canonical'];p=[e for e in d['programs']['forward'] if e[0]!='climb'];a=collections.defaultdict(list)
for i,e in enumerate(p):
 if e[0]=='warp': a[abs(e[2])].append((i,e[2],e[1],e[3],e[4],len(c['frames'][e[3]]),len(c['frames'][e[4]])))
for op in range(47,59):
 print(op,a[op])
 print('frames',[(t[3:5],c['frames'][t[3]],c['frames'][t[4]]) for t in a[op]])

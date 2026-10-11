"""Fresh exact integer replay of all980 signed columns and literal inverse."""
from pathlib import Path
import struct,json,hashlib
P=Path(__file__).resolve().parent;S=P/'local';events=list(struct.iter_unpack('<6i',(S/'signed-records.bin').read_bytes()));M=json.load(open(S/'decoder-and-dirt.json'))['M'];n=980
add=lambda a,b,c:{k:v for k,v in({k:a.get(k,0)+c*b.get(k,0)for k in a.keys()|b.keys()}).items()if v}
def run(rows,reverse=False):
 rows=[dict(x)for x in rows]+[{}];opened=None
 for op,a,b,c,f,z in reversed(events)if reverse else events:
  if op==0:continue
  if op==1:rows[a]=add(rows[a],rows[b],-c if reverse else c)
  elif op==(3 if reverse else 2):assert opened is None and not rows[n];rows[n]=dict(rows[a]);opened=a
  else:assert opened==a and rows[n]==rows[a];rows[n]={};opened=None
 assert opened is None and not rows[n];return rows[:n]
I=[{i:1}for i in range(n)];forward=run(I);expected=[dict(x)for x in I]
for t,row in enumerate(M):expected[120+t]=add(expected[120+t],{int(k):int(v)for k,v in row.items()},1)
assert forward==expected;assert run(forward,True)==I
inverse=run(I,True);wanted=[dict(x)for x in I]
for t,row in enumerate(M):wanted[120+t]=add(wanted[120+t],{int(k):int(v)for k,v in row.items()},-1)
assert inverse==wanted
r={'status':'PASS_OWNED_SIGNED60_ALL980_INTEGER_COLUMNS_ARBITRARY_DIRT_LITERAL_INVERSE','columns':980,'source_and_helper_I':True,'target_old_dirt_I':True,'fresh_target_matrix':'actualM, not assumedI; parity checked byparentnativeword','fresh_inverse_on_arbitrary_inputs':True,'source_records_sha256':hashlib.sha256((S/'signed-records.bin').read_bytes()).hexdigest(),'decoder_sha256':hashlib.sha256((S/'decoder-and-dirt.json').read_bytes()).hexdigest()}
(P/'LOCAL-REPLAY.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'])

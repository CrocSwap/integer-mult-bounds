from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
import contextlib,io,sys,hashlib
with contextlib.redirect_stdout(io.StringIO()):exec(open(HERE/'groups.py').read())
oldpairs=pairs;scalar=lambda x:Q(x).numerator*pow(Q(x).denominator,-1,MOD)%MOD
intervals=[];export_to=defaultdict(list)
for a,b in oldpairs:
 if a['second']!=b['first']:continue
 r=a['role'];i=a['first'];j=b['second'];lo=a['lo'];hi=b['hi'];scales=[(z,scalar(e[2]))for z,e in writes[r]if i<z<j and e[0]=='SCALE'];exports=[z for z in reads[r]if i<z<j]
 c=dict(role=r,first=i,second=j,lo=lo,hi=hi,move_lo=max([lo]+[z+1 for z in reads[r]if lo<=z<i]),move_hi=min([hi]+[z for z in reads[r]if j<z<hi]),E=a['E'],F=a['F'],G=b['G'],exports=exports,scales=scales,paid_ranks_before=a['paid_ranks_before']+[b['paid_ranks_before'][1]],paid_rank_after=sum(a['paid_ranks_before'])+b['paid_ranks_before'][1],target={},nodes=[],removed_moves=[a['first'],a['second']],pair_indices=[a['first'],b['first']])
 idx=len(intervals);intervals.append(c)
 for z in exports:
  q=scalar(p[z][3])
  for si,sq in scales:
   if si<z:q=q*sq%MOD
  export_to[z].append((idx,q))
def axpy(a,b,q):
 for k,v in b.items():
  z=(a.get(k,0)+q*v)%MOD
  if z:a[k]=z
  else:a.pop(k,None)
full={r for r,f in enumerate(w['final'])if f==127};source_sha=hashlib.sha256((base/'inputs/PR6702-WORD.json.gz').read_bytes()).hexdigest();source_name='PR6702';OUT=Path(sys.argv[1])
exec(s[s.index('# Check the actual old-input'):])

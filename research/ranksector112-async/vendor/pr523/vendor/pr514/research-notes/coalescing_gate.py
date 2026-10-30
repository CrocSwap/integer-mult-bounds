from pathlib import Path
import sys,json,hashlib
from fractions import Fraction
src=Path(sys.argv[1]); inp=Path(sys.argv[2]); out=Path(sys.argv[3])
s=src.read_text().split("# Four coordinate sums")[0].replace("OUT.mkdir(parents=True,exist_ok=False);","")
old=sys.argv;sys.argv=[str(src),str(inp),"unused"];d={};exec(compile(s,str(src),"exec"),d);sys.argv=old
report=[]
for c,z in sorted(d["blocks"].items()):
 ids=z["receipt"]["source_lines"]
 tet=[sorted(t for t in ids if sum(d["R"][t][i]<0 for i in c)%2==parity) for parity in (0,1)]
 Fs=[d["basis"]([d["P"][t] for t in a]) for a in tet]
 retired=[dict(register=r,frame=d["cur"][r],row={str(k):str(x) for k,x in d["rows"][r].items()}) for r in d["retired"][c]]
 eligible=[[r for r in d["retired"][c] if d["inside"](d["cur"][r],F)] for F in Fs]
 direct=[]
 for t in ids:
  F=d["hyper"](d["P"][t])
  packetregs=sorted({r for key,(r,a) in d["packets"].items() if key[0]==c})
  direct.append(dict(target=t,compatible_packets=[r for r in packetregs if d["inside"](d["cur"][r],F)],compatible_retired=[r for r in d["retired"][c] if d["inside"](d["cur"][r],F)]))
 report.append(dict(block=c,tetrads=tet,own_frames=Fs,retired=retired,eligible=eligible,direct=direct))
assert len(report)==14
assert all(len(r["frame"])==3 for b in report for r in b["retired"])
assert all(not e for b in report for e in b["eligible"])
assert all(not x["compatible_packets"] and not x["compatible_retired"] for b in report for x in b["direct"])
result=dict(status="EXACT_RESTRICTED_GATE_NO_COALESCING",source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),blocks=report,scope="Unchanged packet assembly, current retired checkpoint; no assertion against a redesigned packet network.",nonmonotone_excess_per_local=224,nonmonotone_excess_global=16128,baseline_deficit=2496)
out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps({k:v for k,v in result.items() if k!="blocks"}))

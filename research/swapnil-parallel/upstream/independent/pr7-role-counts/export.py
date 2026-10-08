import sys
from local import Producer
n=int(sys.argv[1]); out=sys.argv[2]
p=Producer(n); p.check()
roots=[p.outputs[E] for E in p.inputs]+[p.total]
act=sorted(p.d.active(roots)); ni=len(p.inputs)
with open(out,'w') as f:
    adds=[x for x in act if p.d.args[x]]
    f.write(f"{n} {ni} {len(adds)}\n")
    for i,t in enumerate(p.inputs): f.write(f"{t[0]} {t[1]} {t[2]}\n")
    for x in adds:
        a,b=p.d.args[x]; f.write(f"{x} {a} {b}\n")
    for E in p.inputs: f.write(f"{E[0]} {E[1]} {E[2]} {p.outputs[E]}\n")
    f.write(f"{p.total}\n")
print(n,len(adds))

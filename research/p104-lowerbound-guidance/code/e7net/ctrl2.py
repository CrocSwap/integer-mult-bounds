from lm7 import *
ports=shard('e7'); N=dec_net(ports)
S=Struct(ports,[(nd['aB'],nd['bB']) for nd in N.nodes])
import collections
for sc in (0.5,0.1,0.02):
  out=[]
  for seed in range(20):
    rng=np.random.default_rng(seed)
    S.solve.__func__  # noqa
    c,x=S.solve(seed,iters=400)
    out.append(round(float(c),3))
  print(out)
  break

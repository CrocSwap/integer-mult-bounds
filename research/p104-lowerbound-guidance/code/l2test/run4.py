from run3 import *
import random
# family A: chain splits of E8 rows (gather node -> deposit node at chart c dim k), random k and v in c or not
rng=random.Random(3); res=[]
for n in (96,104):
  for it in range(40):
    kd=[rng.choice([1,2,3,4,5,6,7,8]) for _ in range(8)]
    N=e8_net(n,kdims=kd,withv=True,seed=it)
    bad=N.legal(); ok,_=N.check()
    r=N.report('A'); print('A',n,kd,'legal',not bad,'dec',ok,{k:r[k] for k in('D','YC','DX','loss','junk','viol')},flush=True)

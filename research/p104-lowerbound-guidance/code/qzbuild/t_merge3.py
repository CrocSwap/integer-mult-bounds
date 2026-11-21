from qzdrive import *
import time, itertools
masks=[{0,1},{0,1},{0,1,2},{0,1,2}]
for order in [(2,0,1),(0,2,1),(0,1,2)]:
  for pl in itertools.product(range(4),repeat=2):
    if pl[0]>pl[1]: continue
    pieces=[{0,1},{0,1}]; place={0:pl[0],1:pl[1]}
    d=make_design(4,3,masks,pieces,order,place)
    ok,z,S,nr=try_design(d,tries=6)
    print(order,pl,'chat %.3f'%chat(d),ok,'%.2e'%nr,flush=True)

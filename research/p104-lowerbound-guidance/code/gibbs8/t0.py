import sys; from g8lib import *
Qs={'HS64':Q_std(std_set('HS64')),'E7s':Q_std(std_set('E7s'))}
sn=sys.argv[1]; Q=Qs[sn]
W,V=hs_frame_start(Q) if sn=='HS64' else load_start('../mergerows/m3_E7s_3_1.pkl',Q)
D=Dec(Q,W,V); print('valid',D.valid(),'C',D.C(),'m',D.m,D.pr)
rows=to_rows(D); print(check2(rows,Q)); print(pipeline(rows,Q,38))
rng=np.random.default_rng(0)
import time; t=time.time()
for beta in (3.0,1.0,0.0):
  for i in range(300): step(D,rng,beta=beta)
  print(beta,'after',D.valid(),D.C(),D.pr,time.time()-t)
rows=to_rows(D); print(check2(rows,Q)); t=time.time(); print(pipeline(rows,Q,38),time.time()-t)

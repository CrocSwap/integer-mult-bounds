# all-pairs intersection dimension of distinct first frames (float SVD rank screening; exact check later)
import pickle, sys, time, numpy as np
d = pickle.load(open(sys.argv[1],'rb')); ftab=d['ftab']
fids = sorted(ftab); m=len(fids); dims=np.array([ftab[f]['dim'] for f in fids])
Bpad = np.zeros((m,24,24)); 
for i,f in enumerate(fids):
    B=np.array(ftab[f]['B'],dtype=float); Bpad[i,:len(B)]=B
inter = np.zeros((m,m),dtype=np.uint8)
t0=time.time()
for i in range(m):
    stack = np.concatenate([np.broadcast_to(Bpad[i],(m,24,24)), Bpad], axis=1)  # (m,48,24)
    r = np.linalg.matrix_rank(stack, tol=1e-6)
    inter[i] = (dims[i]+dims-r).astype(np.uint8)
    if i%500==0: print(i, time.time()-t0, flush=True)
np.save(sys.argv[2], inter); pickle.dump(fids, open(sys.argv[2]+'.fids.pkl','wb'))
print('done', time.time()-t0)

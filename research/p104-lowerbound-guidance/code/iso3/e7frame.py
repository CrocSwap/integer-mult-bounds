import numpy as np, sympy, sys, collections, pickle
from gmax import *
Lall=std_lines(); a0=Lall[0]; L7=std_set('E7s'); Q7=Q_std(L7); n=len(L7)
# 8 mutually orthogonal lines containing a0 (greedy)
fr=[a0]
for l in Lall:
    if all(int(l.dot(f))==0 for f in fr): fr.append(l)
    if len(fr)==8: break
F=sympy.Matrix([list(map(int,f)) for f in fr]); print('frame size',len(fr))
rng=np.random.default_rng(int(sys.argv[1]))
for trial in range(int(sys.argv[2])):
    U=F*rand_unimod(8,rng) if trial%2 else rand_unimod(8,rng)*F
    rows=gram_rows_B(L7.tolist(),np.eye(8,dtype=int),U,8); assert check_decoder(rows,Q7)==0
    VW,VU=vals(rows,n)
    prof=[(collections.Counter(VW[:,k].tolist()).most_common(2),collections.Counter(VU[:,k].tolist()).most_common(2)) for k in range(len(rows))]
    g=gauge_max(rows,Q7,600,trial)
    print(trial,'C',g['C'],'S1',g['gmax_sum'],'rows',len(rows)); 
    if g['gmax_sum']<41:
        for p in prof: print('   ',p)
        pickle.dump(rows,open('e7f_%s_%d.pkl'%(sys.argv[1],trial),'wb'))

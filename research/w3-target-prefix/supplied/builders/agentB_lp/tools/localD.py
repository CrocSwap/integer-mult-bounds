import sys, json, numpy as np, math, collections
g=lambda r: r*math.log(120/r)
for d in sys.argv[1:]:
    rec=np.fromfile(d+'/249-records.bin',dtype='<i4').reshape(-1,6)
    mv=rec[rec[:,0]==0]; H=collections.Counter(mv[:,4].tolist())
    D=sum(c*g(j) for j,c in H.items() if j>0)
    cp=rec[rec[:,0]==2]; Dc=sum(g(int(r[5])) for r in cp)
    print(d,'local D per stage %.1f'%(D+Dc),'moves',len(mv),'records',len(rec))

import numpy as np, json, sys
d=sys.argv[1]
s=json.load(open(d+'/249-states.json'))
v=s['v']; ZERO=s['ZERO']
rec=np.fromfile(d+'/249-records.bin',dtype='<i4').reshape(-1,6)
pairs=np.loadtxt(d+'/resid.txt',dtype=np.int64).reshape(-1,2)
comp=np.zeros((len(pairs),6),dtype=np.int32)
comp[:,0]=1; comp[:,1]=pairs[:,0]+v; comp[:,2]=pairs[:,1]; comp[:,3]=-1; comp[:,4]=ZERO; comp[:,5]=4
out=np.concatenate([comp,rec])
out.tofile(d+'/249-records.bin')
s['record_count']=len(out); json.dump(s,open(d+'/249-states.json','w'))
print('added comp reads',len(comp),'records',len(out))

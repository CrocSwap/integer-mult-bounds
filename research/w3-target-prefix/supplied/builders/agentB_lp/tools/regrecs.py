import sys, numpy as np, json
d=sys.argv[1]; regs=[int(x) for x in sys.argv[2:]]
rec=np.fromfile(d+'/249-records.bin',dtype='<i4').reshape(-1,6)
s=json.load(open(d+'/249-states.json'))
dim={}
with open(d+'/frames.txt') as f:
    nf=int(f.readline())
    for _ in range(nf):
        fid,dd=map(int,f.readline().split()); dim[fid]=dd
        for __ in range(dd): f.readline()
v=s['v']
def nm(r): return 'X%d'%r if r<v else ('Y%d'%(r-v) if r<2*v else 'H%d'%r)
for r in regs:
    print(nm(r),'init',s['initial'][str(r)],'dim',dim[s['initial'][str(r)]],'final',s['final'][str(r)])
    idx=np.nonzero((rec[:,1]==r)|((rec[:,0]==1)&(rec[:,2]==r)))[0]
    for k in idx:
        o,a,b,c,f,z=rec[k].tolist()
        if o==0: print('  %8d MOVE %s %d(d%d)->%d(d%d) rank %d'%(k,nm(a),b,dim[b],c,dim[c],f))
        elif o==1: print('  %8d ADD %s += %s coeff %d @%d(d%d) cat %d'%(k,nm(a),nm(b),c,f,dim[f],z))
        else: print('  %8d op%d'%(k,o),rec[k].tolist())

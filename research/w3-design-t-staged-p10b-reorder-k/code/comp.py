"""Regenerate completion reads: for each residual (t, q) of target column t on a sigma-0 helper q, prepend Y_t -= q at ZERO (cat 4).
usage: comp.py DIR (in place; runs f2.replay first)"""
import sys,os,json,numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import f2
d=sys.argv[1];res,resid=f2.replay(d)
assert res['violations']==0 and res['final_mismatch']==0 and res['X_not_restored']==0 and res['H_not_restored']==0 and res['resid_other']==0,res
st=json.load(open(d+'/249-states.json'));v=st['v'];Z=st['ZERO']
rec=np.fromfile(d+'/249-records.bin',dtype='<i4').reshape(-1,6)
p=np.array(resid,dtype=np.int64).reshape(-1,2);c=np.zeros((len(p),6),dtype='<i4')
c[:,0]=1;c[:,1]=p[:,0]+v;c[:,2]=p[:,1];c[:,3]=-1;c[:,4]=Z;c[:,5]=4
out=np.concatenate([c,rec]).astype('<i4');out.tofile(d+'/249-records.bin');st['record_count']=len(out);json.dump(st,open(d+'/249-states.json','w'))
print('comp reads',len(c),'records',len(out))
res2,r2=f2.replay(d);assert res2['resid_sigma0']==0 and res2['resid_other']==0 and res2['violations']==0,res2

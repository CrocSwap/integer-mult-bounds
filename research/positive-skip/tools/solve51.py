import sys,math,struct,json
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import min_weight_full_bipartite_matching, maximum_bipartite_matching
h=int(sys.argv[1]); dag=sys.argv[2]; out=sys.argv[3]
E=[]
for line in open(f'edges{h}.txt'):
    p=line.split(); x,e,j=map(int,p[:3]); d={int(k):int(v) for k,v in (q.split(':') for q in p[3:])}
    assert sum(t*c for t,c in d.items())==-h
    E.append((x,j,e,sum(c*t*math.log(t) for t,c in d.items())))
donors=sorted({x for x,*_ in E}); uses=sorted({j for _,j,*_ in E}); di={x:i for i,x in enumerate(donors)}; ui={j:i for i,j in enumerate(uses)}
nd,nu=len(donors),len(uses); r=[di[x] for x,*_ in E]; c=[ui[j] for _,j,*_ in E]
card=int((maximum_bipartite_matching(csr_matrix((np.ones(len(E)),(r,c)),shape=(nd,nu)),perm_type='column')>=0).sum())
ws=np.array([w for *_,w in E]); C=ws.max()+1.0
M=csr_matrix((list(C-ws)+[C+1e6]*nd,(r+list(range(nd)),c+[nu+i for i in range(nd)])),shape=(nd,nu+nd))
ri,ci=min_weight_full_bipartite_matching(M); emap={(di[x],ui[j]):(x,e) for x,j,e,_ in E}
sel=sorted(emap[(i,k)] for i,k in zip(ri.tolist(),ci.tolist()) if k<nu); assert len(sel)==card
n=struct.unpack_from('<4I',open(dag,'rb').read(16))[2]
open(out,'wb').write(struct.pack('<2I',n,len(sel))+b''.join(struct.pack('<2I',x,e) for x,e in sel))
cur=struct.unpack_from('<2I',open(f'h{h}.uses','rb').read(8))[1]
print(h,'max cardinality',card,'PR51 matched',cur)

import os,sys,pickle
os.environ['E8COORD']='ham'
import hx, ham1
from hx import Fm
h0,atoms=hx.load()
h1=pickle.load(open(sys.argv[1],'rb'))
V=120
sz=lambda h,u: bin(h.content[u]).count('1')
desc=lambda h,u: ('src' if u<V else 'S')+'[%d|d%d|#%d]'%(sz(h,u),h.dim[u],u)
ch=[w for w in range(V,len(h0.content)) if w<len(h1.content) and h0.kids[w]!=h1.kids[w] and h0.kids[w] is not None]
print('changed rules',len(ch))
for w in ch:
    a,b=h1.kids[w]; ov=bin(h1.content[a]&h1.content[b]).count('1')
    print(desc(h1,w),'old',[desc(h0,k) for k in h0.kids[w]],'new',[desc(h1,k) for k in h1.kids[w]],'overlap',ov)

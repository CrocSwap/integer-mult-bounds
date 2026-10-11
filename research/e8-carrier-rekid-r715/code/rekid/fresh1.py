import os,sys,json,ast,pickle
os.environ['E8COORD']='ham'
import c2x as C2, compile as C, frames as Fm, ham1
from collections import Counter
h=pickle.load(open('h865.pkl','rb'))
V=120
W=C2.compile2(h)
print(W.stats)
sz=lambda u: bin(h.content[u]).count('1')
print(Counter((sz(w),h.dim[w]) for w in W.fresh))

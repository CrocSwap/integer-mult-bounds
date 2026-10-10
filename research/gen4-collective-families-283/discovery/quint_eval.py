"""Exact evaluation of cached size-5 circuits (chunk i of k); keeps families with standalone gain < 3 and prints the full census."""
import sys, os, pickle, json, collections, time; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fameval import Evaluator
d=pickle.load(open(sys.argv[1],'rb')); circ=pickle.load(open(sys.argv[2],'rb')); i,k=int(sys.argv[3]),int(sys.argv[4]); OUT=sys.argv[5]
ev=Evaluator(d); fams=[]; census=collections.Counter(); t=time.time()
for hs in circ[i::k]:
    f=ev.evaluate('quint',[int(s) for s in hs])
    if f:
        o=f['options'][0]; census[(f['dim_intersection'],o['e'],round(o['gain']))]+=1
        if o['gain']<3: fams.append(f)
print('chunk',i,'evaluated',len(circ[i::k]),'ok',sum(census.values()),'kept(gain<3)',len(fams),'seconds',time.time()-t)
print('census (dim intersection, best e, rounded gain):', sorted(census.items()))
print('stats', {str(a):b for a,b in ev.stats.items()})
json.dump(dict(families=fams, census={str(a):b for a,b in census.items()}, stats={str(a):b for a,b in ev.stats.items()}), open(OUT,'w'))

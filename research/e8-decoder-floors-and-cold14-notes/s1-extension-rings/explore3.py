import sys,time; sys.path.insert(0,sys.path[0])
from gauss_geom import *
lines,J=gaussian_e8()
t=time.time()
F=flats(lines,J,3)
from collections import Counter
for r in F: print(r,len(F[r]),Counter(len(f) for f in F[r]))
print(time.time()-t)
import pickle; pickle.dump(F,open('gflats.pkl','wb'))

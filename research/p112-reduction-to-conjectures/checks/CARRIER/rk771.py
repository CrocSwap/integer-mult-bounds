from lib import *
import pickle
from collections import Counter
pairs=pickle.load(open('pairs771.pkl','rb'))
c=Counter()
N=[t for t in range(n) if t!=0 and ip(lines[0],lines[t])!=0]
Nm=sum(1<<t for t in N)
for Ma,Mb in pairs:
    la=[lab[t] for t in range(n) if Ma>>t&1]; lb=[lab[t] for t in range(n) if Mb>>t&1]
    c[(len(la),f2rank(la),len(lb),f2rank(lb),(Ma|Mb)==Nm,(Ma&Mb)==0)]+=1
print(c)

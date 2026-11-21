from ncore import *
import pickle
CL=pickle.load(open('zclauses.pkl','rb'))
Gz=Z@G@Z.T
from collections import Counter
cnt=Counter()
for t in range(n):
    for r in CL[t]:
        cnt[bin(r).count('1')]+=1
print(cnt)
t=0
f=[r for r in CL[t] if bin(r).count('1')==4]
ip=(Z@G@C[t])
print('port 0 inner products with Z16:',ip)
for r in f[:8]:
    zs=[k for k in range(16) if r>>k&1]; print(zs, 'ips',ip[zs], 'is Q4 nbhd?', [[Gz[a,b] for b in zs] for a in zs])

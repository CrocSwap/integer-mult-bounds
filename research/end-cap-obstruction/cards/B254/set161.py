import sys,collections,pickle
from feas import *
inc=pickle.load(open('inc.pkl','rb'));Yev=pickle.load(open('yevp.pkl','rb'))
H=[h for h in range(224,704) if h not in set(w['centers'])]
used=set()
for i in inc:
    for c in i['car']:
        if c>=224:used.add(c)
for idx,tag,e,k,hh in Yev:
    if e[2]>=224:used.add(e[2])
S=[h for h in H if h not in used]
print(len(S))
pickle.dump(S,open('S161.pkl','wb'))

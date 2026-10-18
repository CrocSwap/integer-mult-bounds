import pickle,collections
from feas import *
S=pickle.load(open('S161.pkl','rb'))
def lay(h):
    return ('cold0' if len(start[h])==0 else 'enter%d'%len(start[h]))+('/endFULL' if end[h]==FULLB else '/endU')
res=collections.Counter();ok=[]
for h in S:
    st,r=track(h)
    k=st.split('@')[0]
    res[(lay(h),k,h in compH)]+=1
    if st=='ok':ok.append(h)
for k,n in sorted(res.items()):print(n,k)
print('algebra-ok',len(ok),ok)
pickle.dump(ok,open('ok161.pkl','wb'))

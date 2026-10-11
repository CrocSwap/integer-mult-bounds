import pickle,sys
from mkword_gauge import *
w=load();w['R']=w['report']['R']
which=sys.argv[1];out=sys.argv[2]
pre,start,gauge,_=pickle.load(open('v4_sel.pkl','rb'))
if which=='g80':pre,start=[],{}
mkword_gauge(w,pre,start,gauge,out)
print(which,'pre',len(pre),'pivots',len(start),'gauge',len(gauge))

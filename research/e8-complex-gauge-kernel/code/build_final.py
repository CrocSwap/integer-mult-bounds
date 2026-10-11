import pickle,sys,json
from mkword_gauge import *
from kern6 import asg_to_groups,groups_to_pre
from kern import setup
import numpy as np
w=load();w['R']=w['report']['R'];col,first=setup(w);R=len(col)
C=np.zeros((v,R))
for h in range(R):
    for t,x in col[h].items():C[t,h]=float(x)
which=sys.argv[1];out=sys.argv[2]
if which=='v1':
    best,asg=pickle.load(open('sa_long_12.pkl','rb'))
    groups=asg_to_groups(C,asg);pre,start,eps=groups_to_pre(col,groups);gauge={}
elif which=='v3':
    pre,start,gauge,flag=pickle.load(open('v3_sel.pkl','rb'))
mkword_gauge(w,pre,start,gauge,out)
print(which,'pre',len(pre),'pivots',len(start),'gauge',len(gauge))

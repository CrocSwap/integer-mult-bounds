import gzip,json,sys,pickle,os
from cxlab import *
from cxcheck import check,FULL
from kern import setup
def mkword_gauge(w,pre,start_k,gauge,outdir):
    w2=copy.deepcopy(w);R=w['report']['R'];w2['R']=R
    col,first=setup(w)
    gc=[]
    for h,E in sorted(gauge.items(),key=lambda kv:(len(kv[1]),kv[0])):
        for t,x in sorted(col[h].items()):
            c=-x;gc.append(['add',v+t,2*v+h,c.numerator,c.denominator,list(E)])
    lev={t:() for t in range(v)}
    for h,E in gauge.items():
        for t in col[h]:
            if len(E)>len(lev[t]):lev[t]=E
    w2['A']=gc+[list(e) for e in pre]+w2['A']
    cl=[]
    for e in reversed(w2['A']+w2['B']):
        if not v<=e[1]<2*v:
            c=inv(e);c[-1]=list(FULL);cl.append(c)
    w2['cleanup']=cl
    st=dict(start_k);st.update({2*v+h:E for h,E in gauge.items()})
    w2['start_extra']={str(r):list(E) for r,E in st.items()}
    w2['target_levels']={str(t):list(E) for t,E in lev.items() if E}
    from gauge2 import gauge_profile
    prof,widths=gauge_profile(w,pre,start_k,gauge,None)
    w2['report']['local_profile']={str(k):x for k,x in prof.items()}
    os.makedirs(outdir,exist_ok=True)
    open(outdir+'/FULL-WORD.json.gz','wb').write(gzip.compress(json.dumps(w2,sort_keys=True,separators=(',',':')).encode(),mtime=0))
    return w2

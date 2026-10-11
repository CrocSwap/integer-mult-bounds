"""Write a modified FULL-WORD.json.gz (kernel variant): A = pre + A, cleanup rebuilt, start_extra for pivots, report updated."""
import gzip,json,sys,pickle,os
from cxlab import *
from cxcheck import check,FULL
def mkword(w,pre,start,outdir):
    w2=copy.deepcopy(w)
    w2['R']=w['report']['R']
    rep,edges=check(w,pre=pre,start=start,full=True)
    w2['A']=[list(e) for e in pre]+w2['A']
    # cleanup: inverse of non-target ops of A+B reversed at FULL
    cl=[]
    for e in reversed(w2['A']+w2['B']):
        if not v<=e[1]<2*v:
            c=inv(e);c[-1]=list(FULL);cl.append(c)
    w2['cleanup']=cl
    w2['start_extra']={str(r):list(E) for r,E in start.items()}
    w2['report']['local_profile']={str(k):x for k,x in rep['local_profile'].items()}
    w2['report']['pivots']=len(start);w2['report']['entrance_rank']=sum(len(E) for E in start.values())
    os.makedirs(outdir,exist_ok=True)
    (open(outdir+'/FULL-WORD.json.gz','wb')).write(gzip.compress(json.dumps(w2,sort_keys=True,separators=(',',':')).encode(),mtime=0))
    return rep
if __name__=='__main__':
    w=load()
    pre,start=pickle.load(open('kern6_word.pkl','rb'))
    rep=mkword(w,pre,start,sys.argv[1])
    print('written',rep['local_profile'],len(pre),len(start))

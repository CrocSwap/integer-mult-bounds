import sys,gzip,json
from collections import Counter,defaultdict
sys.path.insert(0,__import__('os').environ['EO_ROOT']+'/inputs/repo/research/gauge44-slots/independent')
import audit_local as AL
basis=AL.basis;contained=AL.contained;registers=AL.registers
def load(p=None):
    p=p or __import__('os').environ['EO_ROOT']+'/inputs/words/w1018.json.gz'
    return json.loads(gzip.decompress(open(p,'rb').read()))
def climbs(w):
    v,h,R=w['report']['v'],w['report']['h'],w['report']['R'];n=2*v+R
    early=w.get('early_cleanup',[]);earlyids={i for i,U in early}
    tail=[w['cleanup'][i][:-1]+[U] for i,U in early]
    full=basis([1<<i for i in range(h)])
    end=[full]*v+[basis([x for x in range(1,1<<h) if (x&p).bit_count()%2==0]) for p in w['ports']]+[full]*R
    for q,U in w.get('helper_final',{}).items():end[int(q)]=basis(U)
    start=[(p,) for p in w['ports']]+[()]*(v+R)
    for q,U in w.get('start_extra',{}).items():start[int(q)]=basis(U)
    cur=start.copy();log=defaultdict(list);S0=start.copy()
    def climb(q,U,tag):
        U=basis(U);d=len(U)-len(cur[q])
        if d:log[q].append((d,tag))
        cur[q]=U
    for sec in ('A','B'):
        if sec=='B':
            for q,U in zip(w['centers'],w['center_frames']):
                pass
        for i,e in enumerate(w[sec]):
            for q in registers(e):climb(q,e[-1],(sec,i))
    for i,e in enumerate(tail):
        for q in registers(e):climb(q,e[-1],('T',i))
    for q,U in enumerate(end):climb(q,U,('E',0))
    return log,start,end
if __name__=='__main__':
    w=load();log,start,end=climbs(w);v=112
    tot=Counter()
    for q,l in log.items():
        for d,_ in l:tot[d]+=1
    print(sorted(tot.items()), sum(d*c for d,c in tot.items()))
    hp=Counter()
    for q in range(2*v,2*v+w['report']['R']):
        pat=tuple(d for d,_ in log[q]);hp[(len(start[q]),len(end[q]),pat)]+=1
    for k,c in sorted(hp.items(),key=lambda x:-x[1])[:25]:print(c,k)

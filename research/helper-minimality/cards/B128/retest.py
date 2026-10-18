import sys,gzip,json,time
sys.path.insert(0,(__import__('os').environ['HM_ROOT']+'/cards/B128'))
from pathlib import Path
import importlib.util
import coord                       # d (canonical), w (full), pi, solve/apply
t114=None
AUD=(__import__('os').environ['HM_ROOT']+'/inputs/pr799/independent/audit_local.py')
sp=importlib.util.spec_from_file_location('al',AUD);al=importlib.util.module_from_spec(sp);sp.loader.exec_module(al)
FW=(__import__('os').environ['HM_ROOT']+'/inputs/words/656-layers-FULL-WORD.json.gz')
OUT=(__import__('os').environ['HM_ROOT']+'/cards/B128/')
inv={c:f for f,c in coord.pi.items()}
Binv=coord.solve([(c,f) for f,c in coord.pairs[:0]] or [(y,x) for x,y in coord.pairs])
def tofull(N,O):
    cur=list(O.start);F=O.join;out={}
    def run(part):
        o=[]
        for e in N[part]:
            rs=[e[1]]+([e[2]] if e[0]=='add' else [])
            f=e[-1]
            for q in rs:f=F(f,cur[q])
            for q in rs:cur[q]=f
            e2=list(e[:-1])
            for j in range(1,3 if e[0]=='add' else 2): e2[j]=inv[e[j]]
            e2.append(sorted(coord.apply(Binv,x) for x in O.bas[f]))
            o.append(e2)
        return o
    out['A']=run('A')
    for k,c in enumerate(O.d['centers']): cur[c]=F(cur[c],O.d['center_frames'][k])
    out['B']=run('B')
    return out
def verify(wd,label):
    p=Path(OUT+label+'.json.gz');p.write_bytes(gzip.compress(json.dumps(wd).encode(),mtime=0))
    t=time.time()
    try:
        al.run(p,Path(OUT+'out_'+label+'.json'));print(label,'REAL VERIFIER: ACCEPT')
    except Exception as ex:
        print(label,'REAL VERIFIER: REJECT',repr(ex)[:300])
    print('secs',time.time()-t,flush=True)
if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='base':
        verify(json.load(gzip.open(FW)),'base')
    else:
        import t114
        O=t114.O;S0=t114.S0
        h=int(sys.argv[2]);pol=sys.argv[3]
        reads=t114.scan(S0);N=t114.build(S0,h,reads,pol,False)
        assert [e[:-1] for e in N['tail']]==[e[:-1] for e in S0['tail']],'tail edited'
        r=O.evaluate(N);rows=O.replay_rows(N)
        print('oracle',r['legal'],r['fin_raise'],r['kappa'],'values equal',all(rows[i]==t114.rows0[i] for i in range(716)))
        out=tofull(N,O)
        wd=json.load(gzip.open(FW));wd['A']=out['A'];wd['B']=out['B']
        verify(wd,'edit%d_%s'%(h,pol))

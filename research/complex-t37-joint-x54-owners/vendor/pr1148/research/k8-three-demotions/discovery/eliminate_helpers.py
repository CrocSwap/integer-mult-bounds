"""Producer-side elimination of target-only helpers, with exact frame refitting."""
import os,sys,json,gzip,copy,time,contextlib,io
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
os.environ['K8_BASE_WORD']=str(ROOT/'research/k8-eight-ends/FULL-WORD.json.gz')
sys.path.insert(0,str(ROOT/'research/k8-eight-ends/discovery'))
import screen_end_groups as S
A=S.mod('independent',ROOT/'research/gauge44-slots/independent/audit_local.py')
w=S.w

def eliminate(word,h,schedule=None):
    nw=copy.deepcopy(word);v=112
    assert h not in nw['centers']
    assert all(h not in A.registers(e) for e in nw['A']+nw['cut']+nw['precondition']), 'helper participates before B'
    assert all(e[0]!='add' or e[2]!=h or e[1]==h for e in nw['cleanup']), 'cleanup uses helper as a source'
    weight=defaultdict(F);chunks=[];recipe=[]
    for i in range(len(nw['B'])-1,-1,-1):
        e=nw['B'][i]
        if e[0]=='add' and e[2]==h:
            assert v<=e[1]<2*v
            weight[e[1]]+=F(e[3],e[4]);chunks.append([])
        elif e[1]==h:
            if e[0]=='scale':
                q=F(e[2],e[3]);weight=defaultdict(F,{t:q*c for t,c in weight.items()});chunks.append([])
            else:
                q=F(e[3],e[4]);repl=[['add',t,e[2],(q*c).numerator,(q*c).denominator,e[-1]] for t,c in sorted(weight.items()) if c]
                chunks.append(repl);recipe.append(dict(B=i,old=e,new=repl))
        else:
            if e[0]=='scale' and v<=e[1]<2*v:weight[e[1]]/=F(e[2],e[3])
            if e[0]=='add' and v<=e[2]<2*v:
                assert v<=e[1]<2*v
                weight[e[1]]-=F(e[3],e[4])*weight[e[2]]
            chunks.append([e])
    assert not any(weight.values()),'nonzero helper entrance response'
    if schedule is None:nw['B']=[e for chunk in reversed(chunks) for e in chunk]
    else:
        new=[]
        for i,e in enumerate(nw['B']):
            new.extend(copy.deepcopy(schedule.get(i,[])))
            if h not in A.registers(e):new.append(e)
        new.extend(copy.deepcopy(schedule.get(len(nw['B']),[])));nw['B']=new
    ci={};cl=[]
    for i,e in enumerate(nw['cleanup']):
        if h in A.registers(e):continue
        ci[i]=len(cl);cl.append(e)
    nw['cleanup']=cl;nw['early_cleanup']=[[ci[i],fr] for i,fr in nw['early_cleanup'] if i in ci]
    for sec in ['A','B','cut','cleanup','precondition']:
        for e in nw[sec]:
            assert h not in A.registers(e)
            for j in ([1,2] if e[0]=='add' else [1]):e[j]-=int(e[j]>h)
    for sec in ['helper_final','start_extra']:
        nw[sec]={str(int(k)-int(int(k)>h)):fr for k,fr in nw[sec].items() if int(k)!=h}
    nw['centers']=[q-int(q>h) for q in nw['centers']]
    for k in ['cold_low_frame_ended_helpers','entering_low_frame_ended_helpers']:
        nw['refactored_cleanup'][k]=[q-int(q>h) for q in nw['refactored_cleanup'].get(k,[]) if q!=h]
    nw['report']['R']-=1
    nw['refactored_cleanup']['producer_elimination']=dict(removed=h,recipe=recipe)
    return nw,recipe

if __name__=='__main__':
    hs=[r['helper'] for r in json.loads((ROOT/'research/k8-eight-ends-t16/discovery/RETIRABLE-HELPERS.json').read_text())]
    results=[]
    for h in hs:
        t=time.monotonic()
        try:
            nw,recipe=eliminate(w,h);nw=S.optimize(nw)
            path=P/f'eliminate-{h}.json.gz';path.write_bytes(gzip.compress(json.dumps(nw,sort_keys=True,separators=(',',':')).encode(),mtime=0))
            with contextlib.redirect_stdout(io.StringIO()):A.run(path,P/f'eliminate-{h}-AUDIT.json',ROOT)
            r=dict(helper=h,status='PASS_EXACT_LOCAL',profile=nw['report']['local_profile'],recipe=recipe,**S.screen(nw))
        except (AssertionError,RuntimeError,ValueError) as e:r=dict(helper=h,status='REJECTED',reason=str(e))
        r['seconds']=time.monotonic()-t;results.append(r);print(json.dumps(r),flush=True)
        (P/'PRODUCER-ELIMINATION.json').write_text(json.dumps(results,indent=2)+'\n')

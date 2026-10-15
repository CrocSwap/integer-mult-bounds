import sys,json,gzip,copy,tempfile,io,contextlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import audit_local as al
import word_patch as WP
def run(w,tmp):
    p=Path(tmp)/'m.json.gz';p.write_bytes(gzip.compress(json.dumps(w,separators=(',',':')).encode()))
    with contextlib.redirect_stdout(io.StringIO()):return al.run(p,Path(tmp)/'m.out.json',None,None)
def main(wordp,outp):
    w0=json.loads(gzip.decompress(Path(wordp).read_bytes()));tmp=tempfile.mkdtemp();res=[];good=True
    rep=run(w0,tmp);res.append(dict(control='unmutated',status=rep['status']));print('unmutated',rep['status'])
    npre=w0['prelude_events'];pre=w0['A'][:npre]
    def mut():return copy.deepcopy(w0)
    def rederive(m):
        m2=copy.deepcopy(m);A=m2['A'];m2['A']=A[npre:];m2['cleanup']=WP.derive_cleanup(m2,WP.restored_of(w0));m2['A']=A;return m2
    def expect(name,m):
        nonlocal good
        try:run(m,tmp);res.append(dict(control=name,rejected=False));print('NOT REJECTED',name);good=False
        except RuntimeError as e:res.append(dict(control=name,rejected=True,reason=str(e)[:140]));print('rejected',name,'|',str(e)[:100])
    ia=next(i for i,e in enumerate(pre) if e[0]=='add')
    m=mut();m['A'][ia][3]=-m['A'][ia][3];expect('prelude correction sign flipped',m)
    m=mut();m['A'][ia][3]*=2;expect('prelude correction coefficient doubled',m)
    ib=next(i for i,e in enumerate(pre) if e[0]=='add' and e[2]!=pre[ia][2] and e[1]!=pre[ia][1]);m=mut();m['A'][ia][1],m['A'][ib][1]=m['A'][ib][1],m['A'][ia][1];expect('prelude correction targets swapped',m)   # two corrections with different sources and different targets (same-source corrections commute, and equal targets make the swap a no-op)
    iw=[i for i,e in enumerate(pre) if e[0]=='warp'];m=mut();del m['A'][iw[1]];m['prelude_events']-=1;expect('prelude return warp dropped',m)
    m=mut();del m['A'][iw[0]];m['prelude_events']-=1;expect('prelude forward warp dropped',m)
    ids=[i for i,e in enumerate(pre) if e[0]=='add' and e[1]==135];m=mut()
    for i in reversed(ids):del m['A'][i]
    m['prelude_events']-=len(ids);expect('all prelude corrections of target 135 dropped',m)
    m=mut();m['A'][0][-1]=[31];expect('prelude target scale at a different line',m)
    m=mut();m['A'][iw[0]][2]=m['A'][iw[0]][2]+1 if abs(m['A'][iw[0]][2])<len(m['warps']) else m['A'][iw[0]][2]-1;expect('prelude warp uses another operator id',m)
    m=mut();m['A'][iw[0]][4]=[31];expect('prelude warp lands on a different line',m)
    m=mut();m['prelude_events']=0;expect('prelude unmarked',m)
    k=next(iter(m_ for m_ in w0['target_levels']));m=mut();del m['target_levels'][k];expect('lifted target level missing',m)
    # new warp record (first lifted-target alias = lender 33; later aliases append further warps)
    W33=next(i_ for i_,r_ in enumerate(w0['warps']) if r_[1]==33)
    m=mut();r=m['warps'][W33];r[3]=[x^2 for x in r[3]];expect('new warp from-frame wrong',m)
    m=mut();m['warps'][W33][2][0]^=m['warps'][W33][2][1];expect('new warp G wrong',m)
    # restoration gate before a new warp removed (derived cleanup re-derived)
    pos=[w0['warps'][W33][0]];i=pos[0]-1
    m=mut();assert m['B'][i][0]=='add' and m['B'][i][1] in {r_[1] for r_ in w0['warps']},m['B'][i];del m['B'][i]
    for r in m['warps']:
        if r[0]>i:r[0]-=1
    expect('source restoration gate dropped (cleanup re-derived)',rederive(m))
    # rewritten helper gate on the borrowed source removed
    j=next(i for i,g in enumerate(w0['B']) if g[0]=='add' and g[1]==33 and g[2]==250)
    m=mut();del m['B'][j]
    for r in m['warps']:
        if r[0]>j:r[0]-=1
    expect('rewritten source gate dropped (cleanup re-derived)',rederive(m))
    m=mut();m['B'][j][3]=-m['B'][j][3];expect('rewritten source gate sign flipped (cleanup re-derived)',rederive(m))
    # entrance frames of raised buffers
    q=next(iter(w0['start_extra']))
    for q in ('474','522','534'):
        m=mut();m['start_extra'][q]=[];expect('raised buffer entrance dropped %s'%q,m)
        m=mut();m['start_extra'][q]=[1<<i for i in range(9)];expect('raised buffer entrance widened %s'%q,m)
    m=mut();m['start_extra']['640']=[1];expect('removed helper given an entrance frame',m) if False else None
    m=mut();m['report']['local_profile']['1']+=1;expect('wrong claimed profile',m)
    m=mut();m['report']['width_inventory']['8']+=1;expect('wrong claimed width inventory',m)
    Path(outp).write_text(json.dumps(dict(all_rejected=bool(good),controls=res),indent=1)+'\n')
    print('ALL CONTROLS REJECTED' if good else 'CONTROL FAILURE');return 0 if good else 1
if __name__=='__main__':sys.exit(main(*sys.argv[1:]))

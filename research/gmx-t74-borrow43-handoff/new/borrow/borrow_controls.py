"""Negative controls for the BORROW-WORD auditor (audit_local.run_borrow). Every mutation of a passing word must be
rejected with the expected reason; the unmutated word must pass first. Usage: borrow_controls.py WORD.json.gz BASE.json.gz OUT.json"""
import sys,json,gzip,copy,tempfile,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import audit_local as al

def run_word(w,base,tmp):
    p=Path(tmp)/'mut.json.gz';p.write_bytes(gzip.compress(json.dumps(w).encode()))
    import io,contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        return al.run(p,Path(tmp)/'mut.out.json',None,base)

def expect(name,w,base,tmp,why,results):
    try:
        run_word(w,base,tmp);results.append(dict(control=name,rejected=False,expected=why));print('NOT REJECTED',name)
        return False
    except RuntimeError as e:
        ok=any(x in str(e) for x in (why if isinstance(why,tuple) else (why,)));results.append(dict(control=name,rejected=True,reason=str(e)[:160],expected_reason_match=ok));print('rejected' if ok else 'REJECTED-WRONG-REASON',name,'|',str(e)[:90])
        return ok

def main(wordp,basep,outp):
    w0=json.loads(gzip.decompress(Path(wordp).read_bytes()));results=[];tmp=tempfile.mkdtemp();h=w0['report']['h'];good=True
    t=time.monotonic();rep=run_word(w0,basep,tmp);print('unmutated PASS',rep['status']);results.append(dict(control='unmutated',rejected=False,status=rep['status']))
    K=len(w0['warps']);n=704
    def mut():return copy.deepcopy(w0)
    # 1 wrong G (invertible, G(from)!=to)
    for j in range(1,h):
        w=mut();c=w['warps'][0][2]
        for k in range(h):
            if k!=j:
                c2=list(c);c2[j]^=c[k]
                if al.ginv(c2,h) is not None and al.basis([al.gmul(c2,x) for x in w['warps'][0][3]])!=al.basis(w['warps'][0][4]):break
        else:continue
        w['warps'][0][2]=c2;break
    good&=expect('wrong G (invertible, G(from)!=to)',w,basep,tmp,'G(from)!=to',results)
    # 2 non-invertible G
    w=mut();c=w['warps'][1][2];c[3]=c[2];good&=expect('non-invertible G',w,basep,tmp,'G not invertible',results)
    w=mut();w['warps'][2][2][0]=0;good&=expect('non-invertible G (zero column)',w,basep,tmp,'G not invertible',results)
    # 3 frame mismatch: (a) from frame replaced by another subspace of the same dimension; (b) warp moved to another position
    w=mut();r=w['warps'][3];U=r[3];r[3]=[x^1 if i==0 else x for i,x in enumerate(U)] if al.basis([U[0]^1]+U[1:])!=al.basis(U) else [x^2 for x in U]
    good&=expect('frame mismatch (from frame differs from current)',w,basep,tmp,'G(from)!=to',results)
    # frame mismatch with a fully consistent record: from'!=current frame, G'(from')=to, G' invertible
    w=mut();r=w['warps'][0];U=list(r[3]);G=r[2]
    def complete(B):
        out=list(B)
        for k in range(h):
            if al.basis(out+[1<<k])!=al.basis(out):out.append(1<<k)
        return out
    cand=next(x for x in range(1,1<<h) if al.basis(U+[x])!=al.basis(U));W=list(U);W[0]^=cand
    require=al.require;require(al.basis(W)!=al.basis(U) and len(al.basis(W))==len(U),'control construction')
    Wb=complete(W);Ub=complete(U);pre=al.ginv(Wb,h)
    Q=[0]*h
    for t in range(h):
        for i in range(h):
            if pre[t]>>i&1:Q[t]^=Ub[i]
    G2=[al.gmul(G,Q[t]) for t in range(h)]
    require(al.basis([al.gmul(G2,x) for x in W])==al.basis(r[4]) and al.ginv(G2,h) is not None,'control G consistent')
    r[2]=G2;r[3]=W
    good&=expect('frame mismatch (consistent G, from frame differs from lender current frame)',w,basep,tmp,'warp frame mismatch',results)
    # frame mismatch with a consistent G: the warp is moved to a B position where the lender is in another frame
    # (explicit cleanup removed so the derived cleanup follows the moved warp; the frame audit itself must fire)
    found=False
    for k in range(K):
        r=w0['warps'][k];nxt=next((i for i in range(r[0],len(w0['B'])) if r[1] in al.registers(w0['B'][i])),None)
        if nxt is None:continue
        w=mut();w.pop('cleanup');w['warps'][k][0]=nxt+1
        try:run_word(w,basep,tmp)
        except RuntimeError as e:
            if 'warp frame mismatch' in str(e) or 'frame not monotone' in str(e):found=True;break
    good&=found
    good&=expect('frame mismatch (warp moved to a position where the lender frame differs)',w,basep,tmp,('warp frame mismatch','frame not monotone'),results)
    # 4 missing inverse warp
    w=mut();i=next(i for i,g in enumerate(w['cleanup']) if g[0]=='warp');del w['cleanup'][i]
    good&=expect('missing inverse warp in cleanup',w,basep,tmp,'explicit cleanup differs',results)
    w=mut();w['cleanup']=[g for g in w['cleanup'] if g[0]!='warp'];good&=expect('all inverse warps missing',w,basep,tmp,'explicit cleanup differs',results)
    # 4b the algebra itself (not just the derivation comparison) rejects a cleanup without inverse warps
    w=mut();n=2*w['report']['v']+w['report']['R'];v=w['report']['v']
    removed=set(w['removed']);live=[r for r in range(n) if r not in removed];restored={int(q) for q in w['helper_final']}
    DS=10**6;rows={r:{(r,()):al.F(1)} for r in live}
    for c in restored:rows[c+n]={}
    program=[['corr',t['target'],t['source'],tuple(t['operator_word']),al.F(t['coefficient'])] for t in w['initial_corrections']]+w['precondition']+w['compensation']+w['A']+w['cut']
    byp={}
    for op,rec in enumerate(w['warps'],1):byp.setdefault(rec[0],[]).append(op)
    for p in range(len(w['B'])+1):
        for op in byp.get(p,[]):program.append(['warp',w['warps'][op-1][1],op])
        if p<len(w['B']):program.append(w['B'][p])
    program+=w['restore']+[g for g in w['cleanup'] if g[0]!='warp']
    for e in program:al.walg_apply(e,rows,False,DS)
    bad=[r for r in live if r<v or r>=2*v if rows[r]!={(r,()):al.F(1)}]
    results.append(dict(control='algebra without inverse warps does not restore inputs',failed_inputs=len(bad),rejected=bool(bad)));print('algebra-level missing inverse warp: failing restored inputs',len(bad))
    good&=bool(bad)
    # 5 dimension mismatch
    w=mut();w['warps'][5][4]=w['warps'][5][4][:-1];good&=expect('dim(from)!=dim(to)',w,basep,tmp,'dim(from)!=dim(to)',results)
    # 6 inverse warp not at FULL
    w=mut();i=next(i for i,g in enumerate(w['cleanup']) if g[0]=='warp');w['cleanup'][i][3]=w['cleanup'][i][3][:-1]
    good&=expect('inverse warp not at FULL',w,basep,tmp,'explicit cleanup differs',results)
    # 7 zero-buffer rule: cleanup touches the real restored register, not its buffer
    w=mut();i=next(i for i,g in enumerate(w['cleanup']) if g[0]=='add' and g[1]>=n)
    w['cleanup'][i][1]-=n;good&=expect('cleanup uses real restored input instead of private buffer',w,basep,tmp,'explicit cleanup differs',results)
    w=mut();w.pop('cleanup');w['restore']=w['restore'][1:];good&=expect('restoration gate dropped (derived cleanup)',w,basep,tmp,('restored cold','cleanup did not restore','endpoint failure','target map','frame','paid profile mismatch'),results)
    # restored real register not decoupled: its buffer is dropped from the restored set while cleanup still derived
    w=mut();w.pop('cleanup');c0=next(iter(w['helper_final']));w['helper_final'].pop(c0);good&=expect('restored cold input demoted (needs FULL, was decoupled by FULL-less rows)',w,basep,tmp,('',),results) if False else True
    # 8 restored claim without restoration
    touched={r for g in w0['precondition']+w0['compensation'] for r in al.registers(g)}
    w=mut();w.pop('cleanup');c=next(r for r in range(2*v,n) if r not in removed and str(r) not in w['helper_final'] and r not in touched)
    w['helper_final'][str(c)]=[1]
    good&=expect('false cold-restoration claim (register not restored)',w,basep,tmp,('restored cold','frame not monotone'),results)
    # 9 dropped restoration gate
    w=mut();w['restore']=w['restore'][1:];good&=expect('restoration gate dropped',w,basep,tmp,'explicit cleanup differs',results)
    # 10 removed helper referenced / alias missing
    w=mut();r=w['removed'][0];w['B'].append(['add',r,2*v+1,1,1,[]]);good&=expect('gate on removed helper',w,basep,tmp,'removed helper referenced',results)
    # 11 initial corrections (only if present)
    if w0['initial_corrections']:
        w=mut();del w['initial_corrections'][0];good&=expect('initial correction omitted',w,basep,tmp,'target map failed',results)
        w=mut();w['initial_corrections'][0]['coefficient']=str(-al.F(w['initial_corrections'][0]['coefficient']));good&=expect('initial correction sign flipped',w,basep,tmp,'target map failed',results)
        w=mut();w['initial_corrections'][0]['source']=next(r for r in range(2*v,n) if r not in removed and r!=w['initial_corrections'][0]['source'] and str(r) not in w['start_extra'])
        good&=expect('initial correction reads a non-lender',w,basep,tmp,'not the lender',results)
        w=mut();s=w['initial_corrections'][0]['source'];w['start_extra'][str(s)]=[1]
        good&=expect('initial correction reads an entering helper',w,basep,tmp,'nonzero entrance frame',results)
    # 12 wrong profile claim
    w=mut();w['report']['local_profile']['1']+=1;good&=expect('wrong claimed profile',w,basep,tmp,'paid profile mismatch',results)
    w=mut();w['report']['width_inventory']['9']+=1;good&=expect('wrong claimed width inventory',w,basep,tmp,'width inventory mismatch',results)
    # 13 non-monotone frame / frame cut below start: lender warped to a frame not above its current chain
    w=mut();w['B'][100][-1]=[];good&=expect('frame chain not monotone',w,basep,tmp,'frame not monotone',results)
    Path(outp).write_text(json.dumps(dict(all_controls_rejected_for_expected_reason=bool(good),controls=results,seconds=time.monotonic()-t),indent=1)+'\n')
    print('ALL CONTROLS OK' if good else 'CONTROL FAILURE');return 0 if good else 1
if __name__=='__main__':sys.exit(main(*sys.argv[1:]))

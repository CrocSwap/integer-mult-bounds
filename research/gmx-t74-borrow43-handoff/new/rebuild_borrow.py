"""rebuild_borrow.py: rebuild the k=43 BORROW-WORDs from borrow/inputs (canonical words, block certificate, #2226-style witnesses),
check they equal the shipped borrow/words byte-for-content, run the extended auditor (borrow/audit_local.py) and its negative controls.
usage: python -B rebuild_borrow.py [--no-controls]   (exit 0 only if everything passes)"""
import sys,json,gzip,subprocess,hashlib,tempfile
from pathlib import Path
D=Path(__file__).resolve().parent/'borrow';sys.path.insert(0,str(D))
import os
RCP=Path(os.environ['BORROW_RECEIPTS']) if os.environ.get('BORROW_RECEIPTS') else Path(tempfile.mkdtemp());RCP.mkdir(parents=True,exist_ok=True)   # receipts (with elapsed_seconds) never go into the package during verification
import build_word,word_patch
CASES=[('gauge44','base','eeb6a236'),('extra','extra','cd417b90')]
def content(p):return hashlib.sha256(gzip.decompress(Path(p).read_bytes())).hexdigest()
def refit_apply(word0,patch):
    """frame refit: replace exactly the listed gate frames (gates unchanged) and the local profile."""
    import copy
    w=copy.deepcopy(word0)
    for sec,i,fr in patch['frames']:
        assert w[sec][i][:-1]==word0[sec][i][:-1];w[sec][i][-1]=fr
    w['report']['local_profile']=patch['local_profile']
    return w
def run_audit(word,base,rec):
    cmd=[sys.executable,'-B',str(D/'audit_local.py'),'--word',str(word),'--output',str(rec)]+(['--base',str(base)] if base else [])
    return subprocess.run(cmd,capture_output=True,text=True)
def kernel_check(prev,w,patch):
    """The kernel edit(s) (helper-donor pivot kernels, PR1625 shape): the shipped B section differs from the previous word's by exactly the declared gate-level edit
    (frames ignored): reads of the pivots inserted/deleted, nothing else; every inserted and deleted gate is a read of a declared pivot with coefficient +-1."""
    qs=set(patch['pivots']);ed=word_patch.kernel_gate_edit(prev['B'],w['B'])
    ok=ed==patch['declared_gate_edit'] and all(g[0]=='add' and g[2] in qs and abs(g[3])==1 and g[4]==1 for _,_,g in ed)
    ok&=sum(e[0]=='delete' for e in ed)==len(qs) and sum(e[0]=='insert' for e in ed)==4*len(qs)
    for k in w:
        if k not in('A','B','restore','warps','report','cleanup'):ok&=w[k]==prev[k]
    for k in('A','restore'):   # frame-only changes outside B
        ok&=len(w[k])==len(prev[k]) and all(x[:-1]==y[:-1] for x,y in zip(w[k],prev[k]))
    return ok
def kernel_controls(w,patch,tmp):
    """every perturbation of the kernel edit must be rejected by the independent audit"""
    import copy
    res={};qs=set(patch['pivots'])
    pos=[j for kind,j,g in patch['declared_gate_edit'] if kind=='insert']
    def audit_bad(name,m):
        bp=Path(tmp)/(name+'.json.gz');bp.write_bytes(gzip.compress(json.dumps(m,separators=(',',':')).encode()))
        r=run_audit(bp,None,Path(tmp)/(name+'.out.json'));res[name]=r.returncode!=0;return r.returncode!=0
    ok=True
    m=copy.deepcopy(w);m['B'][pos[0]][3]=-m['B'][pos[0]][3];m['cleanup']=word_patch.derive_cleanup(m,word_patch.restored_of(w));ok&=audit_bad('kernel_sign_flipped',m)
    m=copy.deepcopy(w);del m['B'][pos[1]];ok&=audit_bad('kernel_read_dropped',m)
    m=copy.deepcopy(w);m['B'][pos[2]][3]*=2;ok&=audit_bad('kernel_coefficient_doubled',m)
    m=copy.deepcopy(w);m['B'][pos[3]][1]=m['B'][pos[3]][1]+1;ok&=audit_bad('kernel_read_moved_to_neighbour_register',m)
    return ok,res
def _rd(m,ref):
    """re-derive the explicit inverse-reverse cleanup of a mutated word (A section without its prelude), so a control is rejected for its own reason and not for a stale cleanup"""
    try:
        t=json.loads(json.dumps(m));t['A']=t['A'][t.get('prelude_events',0):];return word_patch.derive_cleanup(t,word_patch.restored_of(ref))
    except Exception:
        return m['cleanup']
ok=True;out={}
for canon,wt,h in CASES:
    tmp=Path(tempfile.mkdtemp())/'w.json.gz'
    build_word.main(str(D/'inputs'/f'{canon}.canonical.json.gz'),str(D/'inputs/blocks.json'),str(D/'inputs'/f'witness_43_{wt}.json'),str(tmp),h)
    shipped=D/'words'/f'BORROW-WORD-43{"base" if wt=="base" else "extra"}.json.gz'
    base=str(D/'inputs'/f'{canon}.canonical.json.gz')
    word0=json.loads(gzip.decompress(tmp.read_bytes()))
    chain=[word0];steps=[]
    rf=D/'inputs'/f'refit_43{wt}.json';kf=D/'inputs'/f'kernel_43{wt}.json'
    if rf.exists():chain.append(refit_apply(chain[-1],json.loads(rf.read_text())));steps.append('refit')
    kpatch=json.loads(kf.read_text());kpre=chain[-1];chain.append(word_patch.apply_kernel(chain[-1],kpatch));steps.append('kernel');kstate=chain[-1]
    kok=kernel_check(kpre,kstate,kpatch)
    hf=D/'inputs'/f'handoff_43{wt}.json';hpatch=None
    if hf.exists():   # coherent four-helper handoff (PR2322, Vlado-V) on top of the kernel state: four high roles replaced by retired source registers
        hpatch=json.loads(hf.read_text());chain.append(word_patch.apply_handoff(kstate,hpatch));steps.append('handoff')
        kok&=sorted(hpatch['fields'])==sorted(k_ for k_ in chain[-1] if k_ not in('report','cleanup') and chain[-1][k_]!=kstate[k_]) and len(chain[-1]['removed'])==len(kstate['removed'])+4
    ef=D/'inputs'/f'entrance_43{wt}.json'
    if ef.exists():   # entrance raise: start_extra and frames only (gates unchanged); previous state audited, tamper controls below
        epatch=json.loads(ef.read_text());prev_e=chain[-1];chain.append(word_patch.apply_handoff(prev_e,epatch));steps.append('entrance')
        kok&=all(x_[:-1]==y_[:-1] for k_ in('A','B','restore') for x_,y_ in zip(chain[-1][k_],prev_e[k_])) and chain[-1]['removed']==prev_e['removed'] and chain[-1]['warps']==prev_e['warps']
    lf=D/'inputs'/f'lowfour_43{wt}.json';lpatch=None
    if lf.exists():   # four low aliases through lifted-target compensation (PR2436 mechanism) on top of the entrance state
        lpatch=json.loads(lf.read_text());prev_l=chain[-1];chain.append(word_patch.apply_lowfour(prev_l,lpatch));steps.append('lowfour')
        nw=chain[-1];kok&=word_patch.kernel_gate_edit(prev_l['B'],nw['B'])==lpatch['declared_gate_edit'] and sorted(set(nw['removed'])-set(prev_l['removed']))==[640,641,642,644]==lpatch['derived_removed_diff']
        kok&=[x[1:] for x in nw['warps'][:len(prev_l['warps'])]]==[x[1:] for x in prev_l['warps']] and [x[1] for x in nw['warps'][-4:]]==[33,55,74,85] and len(nw['warps'])==len(prev_l['warps'])+4
        kok&=[g[:-1] for g in nw['A'][nw['prelude_events']:]]==[g[:-1] for g in prev_l['A']] and nw['restore']==prev_l['restore'] and nw['helper_final']==prev_l['helper_final']
        kok&={k_:v_ for k_,v_ in prev_l['start_extra'].items() if k_ not in('640','641','642','644')}==nw['start_extra']
    af=D/'inputs'/f'alias637_43{wt}.json';apatch=None
    if af.exists():   # alias 637 borrowing retired source 31 (PR2436 pair) stacked on the four lifted-target aliases
        apatch=json.loads(af.read_text());prev_a=chain[-1];chain.append(word_patch.apply_lowfour(prev_a,apatch));steps.append('alias637');na=chain[-1]
        kok&=word_patch.kernel_gate_edit(prev_a['B'],na['B'])==apatch['declared_gate_edit'] and sorted(set(na['removed'])-set(prev_a['removed']))==[637] and len(na['warps'])==len(prev_a['warps'])+1 and na['restore']==prev_a['restore'] and na['A']==prev_a['A']
    af2=D/'inputs'/f'alias656_43{wt}.json';apatch2=None
    if af2.exists():   # alias 656 borrowing lender 88 (PR2436 type) stacked on the fifth alias
        apatch2=json.loads(af2.read_text());prev_a2=chain[-1];chain.append(word_patch.apply_lowfour(prev_a2,apatch2));steps.append('alias656');na2=chain[-1]
        kok&=word_patch.kernel_gate_edit(prev_a2['B'],na2['B'])==apatch2['declared_gate_edit'] and sorted(set(na2['removed'])-set(prev_a2['removed']))==[656] and len(na2['warps'])==len(prev_a2['warps'])+1 and na2['restore']==prev_a2['restore'] and True
    af3=D/'inputs'/f'alias8_43{wt}.json';apatch3=None
    if af3.exists():   # eight source-partner aliases (PR2530) (PR2530 zxv: eight source-partner aliases)
        apatch3=json.loads(af3.read_text());prev_a3=chain[-1];chain.append(word_patch.apply_lowfour(prev_a3,apatch3));steps.append('alias8');na3=chain[-1]
        kok&=word_patch.kernel_gate_edit(prev_a3['B'],na3['B'])==apatch3['declared_gate_edit'] and sorted(set(na3['removed'])-set(prev_a3['removed']))==apatch3['removed_added'] and len(na3['warps'])==len(prev_a3['warps'])+8 and True and True
    final=json.loads(gzip.decompress(shipped.read_bytes()))
    same=final==chain[-1]
    # audits: the pinned pre-refit/pre-kernel word against the canonical base; every later state independently (forward + dual free-algebra replay; refit and kernel change frames inside the pinned sections)
    tag=lambda n:RCP/f'AUDIT-43{wt}{n}.json'
    pw=Path(tempfile.mkdtemp());ps=[]
    for j,w_ in enumerate(chain[:-1]):
        f_=pw/f'w{j}.json.gz';f_.write_bytes(gzip.compress(json.dumps(w_,separators=(',',':')).encode()))
        r=run_audit(f_,base if j==0 else None,tag('-pinned' if j==0 else '-prekernel'));ps.append(r.returncode)
    r=run_audit(shipped,None,tag(''))
    ok&=same and kok and all(x==0 for x in ps) and r.returncode==0
    res=dict(rebuild_plus_patches_equals_shipped=same,patches=steps,kernel_edit_exact=kok,prior_state_audit_rc=ps,audit_rc=r.returncode)
    if '--no-controls' not in sys.argv:
        c=subprocess.run([sys.executable,'-B',str(D/'borrow_controls.py'),str(tmp),base,str(RCP/f'CONTROLS-43{wt}.json')],capture_output=True,text=True)
        ok&=c.returncode==0;res['controls_rc']=c.returncode
        if lpatch:
            lc=subprocess.run([sys.executable,'-B',str(D/'lowfour_controls.py'),str(shipped),str(RCP/f'CONTROLS-LOWFOUR-43{wt}.json')],capture_output=True,text=True)
            ok&=lc.returncode==0;res['lowfour_controls_rc']=lc.returncode
        kc_ok,kc=kernel_controls(kstate,kpatch,tempfile.mkdtemp());ok&=kc_ok;res['kernel_controls_rejected']=kc
        if apatch:
            import copy as cp4
            ii=next(q for q,(x,y) in enumerate(zip(final['B'],prev_a['B'])) if x[:-1]!=y[:-1] and x[0]=='add')
            for nm_,mut in (('alias637_sign_flipped',lambda m:m['B'][ii].__setitem__(3,-m['B'][ii][3])),('alias637_coefficient_doubled',lambda m:m['B'][ii].__setitem__(3,2*m['B'][ii][3])),('alias637_warp_dropped',lambda m:m.__setitem__('warps',m['warps'][:-1]))):
                m=cp4.deepcopy(final);mut(m);m['cleanup']=_rd(m,final);bp=pw/(nm_+'.json.gz');bp.write_bytes(gzip.compress(json.dumps(m,separators=(',',':')).encode()));br=run_audit(bp,None,pw/(nm_+'.out.json'));kc[nm_]=br.returncode!=0;ok&=br.returncode!=0
        if apatch2:
            import copy as cp5
            ii=next(q for q,(x,y) in enumerate(zip(final['B'],prev_a2['B'])) if x[:-1]!=y[:-1] and x[0]=='add')
            for nm_,mut in (('alias656_sign_flipped',lambda m:m['B'][ii].__setitem__(3,-m['B'][ii][3])),('alias656_coefficient_doubled',lambda m:m['B'][ii].__setitem__(3,2*m['B'][ii][3])),('alias656_warp_dropped',lambda m:m.__setitem__('warps',m['warps'][:-1]))):
                m=cp5.deepcopy(final);mut(m);m['cleanup']=_rd(m,final);bp=pw/(nm_+'.json.gz');bp.write_bytes(gzip.compress(json.dumps(m,separators=(',',':')).encode()));br=run_audit(bp,None,pw/(nm_+'.out.json'));kc[nm_]=br.returncode!=0;ok&=br.returncode!=0
        if apatch3:
            import copy as cp6
            ii=next(q for q,(x,y) in enumerate(zip(final['B'],prev_a3['B'])) if x[:-1]!=y[:-1] and x[0]=='add')
            for nm_,mut in (('alias8_sign_flipped',lambda m:m['B'][ii].__setitem__(3,-m['B'][ii][3])),('alias8_coefficient_doubled',lambda m:m['B'][ii].__setitem__(3,2*m['B'][ii][3])),('alias8_warp_dropped',lambda m:m.__setitem__('warps',m['warps'][:-1]))):
                m=cp6.deepcopy(final);mut(m);m['cleanup']=_rd(m,final);bp=pw/(nm_+'.json.gz');bp.write_bytes(gzip.compress(json.dumps(m,separators=(',',':')).encode()));br=run_audit(bp,None,pw/(nm_+'.out.json'));kc[nm_]=br.returncode!=0;ok&=br.returncode!=0
        if ef.exists():
            import copy as cp3
            q=next(iter(epatch['fields']['start_extra']));
            for nm_,mut in (('entrance_start_frame_dropped',lambda m:m['start_extra'].__setitem__(q,[])),('entrance_start_frame_widened',lambda m:m['start_extra'].__setitem__(q,[1<<i for i in range(9)]))):
                m=cp3.deepcopy(final);mut(m);m['cleanup']=_rd(m,final);bp=pw/(nm_+'.json.gz');bp.write_bytes(gzip.compress(json.dumps(m,separators=(',',':')).encode()));br=run_audit(bp,None,pw/(nm_+'.out.json'));kc[nm_]=br.returncode!=0;ok&=br.returncode!=0
        if hpatch:
            import copy as cp2
            for nm_,mut in (('handoff_sign_flipped',lambda m,i_:m['B'][i_].__setitem__(3,-m['B'][i_][3])),('handoff_coefficient_doubled',lambda m,i_:m['B'][i_].__setitem__(3,2*m['B'][i_][3]))):
                m=cp2.deepcopy(final);i_=next(q for q,(x,y) in enumerate(zip(final['B'],kstate['B'])) if x[:-1]!=y[:-1] and x[0]=='add');mut(m,i_);m['cleanup']=word_patch.derive_cleanup(m,word_patch.restored_of(final))
                bp=pw/(nm_+'.json.gz');bp.write_bytes(gzip.compress(json.dumps(m,separators=(',',':')).encode()));br=run_audit(bp,None,pw/(nm_+'.out.json'));kc[nm_]=br.returncode!=0;ok&=br.returncode!=0
        (RCP/f'CONTROLS-KERNEL-43{wt}.json').write_text(json.dumps(kc,indent=2)+'\n')
        if rf.exists():
            rp=json.loads(rf.read_text());bad=copy_=json.loads(json.dumps(chain[1]));sec,i_,fr=rp['frames'][-1];bad[sec][i_][-1]=[1]
            bp=pw/'bad.json.gz';bp.write_bytes(gzip.compress(json.dumps(bad,separators=(',',':')).encode()));br=run_audit(bp,None,pw/'bad.out.json');res['refit_tamper_rejected']=br.returncode!=0;ok&=br.returncode!=0
    # CUT-CENTRE GUARD (PR2478, mdumitrean): audit_local frame-checks only cut gates whose source is a centre; every cut gate of the shipped word must be an add from one of the 8 centres to a target row.
    import guard_cut_centres as gcc
    gv=gcc.violations(final);gbad=json.loads(json.dumps(final));gbad['cut'][0]=['add',gbad['cut'][0][1],next(r_ for r_ in range(224,704) if r_ not in set(gbad['centers'])),1,1]+list(gbad['cut'][0][5:])
    res['cut_centre_guard_violations']=len(gv);res['cut_centre_guard_negative_control_rejected']=len(gcc.violations(gbad))>0
    ok&=not gv and res['cut_centre_guard_negative_control_rejected']
    print('CUT-CENTRE-GUARD',wt,'cut gates',len(final['cut']),'violations',len(gv),'negative control rejected',res['cut_centre_guard_negative_control_rejected'],flush=True)
    # HELPER-INDEX GUARD (PR2508, ywz65): audit_local accepts a negative helper_final key that aliases a target endpoint; every helper_final key must be a canonical non-negative decimal inside the helper interval [2v, 2v+R).
    import guard_helper_indices as ghi
    hv=ghi.violations(final);hbad=json.loads(json.dumps(final));hbad['helper_final']['-1']=hbad['helper_final'].get('-1',list(next(iter(hbad['helper_final'].values()))))
    res['helper_index_guard_violations']=len(hv);res['helper_index_guard_negative_control_rejected']=len(ghi.violations(hbad))>0
    ok&=not hv and res['helper_index_guard_negative_control_rejected']
    print('HELPER-INDEX-GUARD',wt,'helper_final keys',len(final['helper_final']),'violations',len(hv),'negative control (key -1) rejected',res['helper_index_guard_negative_control_rejected'],flush=True)
    # ENTRANCE-WIDTH BINDING (answers whether the hosted helpers are delivered at the raised entrance frames): the per-helper residual width |final|-|start_extra| of THIS word must equal the ordered widths of new/BORROW-PROVIDERS.json,
    # which are the widths reconstruct.py/emit/audit_allcold use for every hosted role (audit: 'wrong per-call residual width', 'entering helper width silently restored to nine'); bind_providers_portable.py re-derives them from the native canonical word.
    prov_w=json.loads((D.parent/'BORROW-PROVIDERS.json').read_text())['gauge44' if wt=='base' else 'extra']['widths']
    def word_widths(w_):
        rem=[r_ for r_ in range(224,704) if r_ not in set(w_['removed'])];se_={int(k_):v_ for k_,v_ in w_['start_extra'].items()};hf_={int(k_):v_ for k_,v_ in w_['helper_final'].items()}
        return [len(hf_.get(r_,range(9)))-len(se_.get(r_,[])) for r_ in rem]
    bind_ok=word_widths(final)==prov_w
    tw=json.loads(json.dumps(final));raised=[int(k_) for k_,v_ in tw['start_extra'].items() if len(v_)==2]
    if raised:tw['start_extra'][str(raised[0])]=tw['start_extra'][str(raised[0])][:1]   # a raised copy buffer delivered at dim 1 again
    tamper_rejected=bool(raised) and word_widths(tw)!=prov_w
    res['entrance_widths_bound_to_providers']=bind_ok;res['dim1_delivery_rejected']=tamper_rejected;res['raised_buffers']=len(raised)
    ok&=bind_ok and (tamper_rejected or not raised)
    print('ENTRANCE-WIDTH-BINDING',wt,'raised',len(raised),'bound',bind_ok,'dim1 tamper rejected',tamper_rejected,flush=True)
    out[canon]=res;print(canon,res,flush=True)
print('PASS_REBUILD_BORROW' if ok else 'FAIL_REBUILD_BORROW');sys.exit(0 if ok else 1)

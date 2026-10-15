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
    pf=D/'inputs'/f'prelife_43{wt}.json';ppatch=None
    if pf.exists():   # pre-life hosting (this package): six cold width-4 hosts h each host the whole life of a width-9 dim-0-start helper L after retiring
        ppatch=json.loads(pf.read_text());prev_p=chain[-1];chain.append(word_patch.apply_prelife(prev_p,ppatch));steps.append('prelife');npl=chain[-1]
        PLs=sorted(x_['L'] for x_ in ppatch['pairs']);PHs=[x_['h'] for x_ in ppatch['pairs']]
        kok&=PLs==[482,483,494,495,507,519] and sorted(set(npl['removed'])-set(prev_p['removed']))==PLs and set(prev_p['removed'])<=set(npl['removed'])
        kok&=sorted(set(prev_p['helper_final'])-set(npl['helper_final']))==sorted(map(str,PHs)) and all(npl['helper_final'][k_]==prev_p['helper_final'][k_] for k_ in npl['helper_final'])
        kok&=npl['warps'][:len(prev_p['warps'])]==prev_p['warps'] and [x_[1] for x_ in npl['warps'][len(prev_p['warps']):]]==PHs
        kok&=npl['compensation']==[e_ for e_ in prev_p['compensation'] if not(e_[0]=='add' and e_[2] in set(PLs))]   # the hosted helpers' dirt-compensation reads are removed ...
        kok&=all(c_ in prev_p['initial_corrections'] or (c_['source'] in set(PHs) and len(c_['operator_word'])==1 and npl['warps'][c_['operator_word'][0]-1][1]==c_['source']) for c_ in npl['initial_corrections'])   # ... and replaced by anticipatory corrections through the host's warp
        kok&=word_patch.kernel_gate_edit(prev_p['B'],npl['B'])==ppatch['declared_gate_edit']
        kok&=all(npl[k_]==prev_p[k_] for k_ in ('A','precondition','cut','start_extra','target_levels','centers','center_frames','ports','prelude_events'))
    rf2=D/'inputs'/f'refit563_43{wt}.json';rpatch2=None
    if rf2.exists():   # one-gate exact frame lowering (B 894, add 515 += 563: dim 6 -> 5) so that 563 retires at the dimension of 653's entrance frame (this package)
        rpatch2=json.loads(rf2.read_text());prev_r=chain[-1];chain.append(refit_apply(prev_r,rpatch2));steps.append('refit563');nr=chain[-1]
        kok&=len(rpatch2['frames'])==1 and rpatch2['frames'][0][:2]==['B',894] and prev_r['B'][894][:5]==['add',515,563,1,1]
        kok&=len(nr['B'][894][-1])==len(prev_r['B'][894][-1])-1 and all(x_==y_ for i_,(x_,y_) in enumerate(zip(nr['B'],prev_r['B'])) if i_!=894)
        kok&=not({515,563}&({x_['L'] for x_ in ppatch['pairs']}|{x_['h'] for x_ in ppatch['pairs']}) if ppatch else set())
    xf=D/'inputs'/f'alias1_43{wt}.json';xpatch=None
    if xf.exists():   # retired-lender alias 653<-563 on the refit state (this package)
        xpatch=json.loads(xf.read_text());prev_x=chain[-1];chain.append(word_patch.apply_lowfour(prev_x,xpatch));steps.append('alias1');nx=chain[-1]
        kok&=word_patch.kernel_gate_edit(prev_x['B'],nx['B'])==xpatch['declared_gate_edit'] and sorted(set(nx['removed'])-set(prev_x['removed']))==[653] and len(nx['warps'])==len(prev_x['warps'])+1 and nx['A']==prev_x['A'] and nx['restore']==prev_x['restore']
        kok&=all(g_[0]=='add' and 563 in g_[1:3] for kd_,_,g_ in xpatch['declared_gate_edit'] if kd_=='insert') and nx['warps'][-1][1]==563
        # exhaustive enumeration of retired-lender aliases (borrow/alias_enumerate.py): on the pre-life + refit563 state exactly one pair (653<-563) exists; none on the shipped word
        import alias_enumerate as AE,tempfile as tf_
        def enum_(w_):
            p_=Path(tf_.mkdtemp())/'w.json.gz';p_.write_bytes(gzip.compress(json.dumps(w_,separators=(',',':')).encode(),mtime=0));o_,s_=AE.main(str(p_));return o_,dict(s_)
        e0,s0=enum_(prev_x);e1,s1=enum_(nx)
        kok&=[(x_['h'],x_['L']) for x_ in e0]==[(653,563)] and len(e1)==0
        (RCP/f'ALIAS-ENUMERATION-43{wt}.json').write_text(json.dumps(dict(prelife_refit_state=dict(counts=s0,pairs=[{k_:x_[k_] for k_ in('h','L','p1','d','s','f1','width','dprof')} for x_ in e0]),shipped=dict(counts=s1,pairs=len(e1)),
            note='counts: h_used_in_A_or_early = helpers first used before B (needs the prelude/lifted-target mechanism); the other counts are (h,L) pairs failing that condition'),indent=1)+'\n')
    tf_=D/'inputs'/f'twelve_43{wt}.json';tpatch=None
    if tf_.exists():   # PR2751's twelve-alias reassignment with the frame re-solve of the final word (this package); no phase-B warps
        tpatch=json.loads(tf_.read_text());prev_t=chain[-1];chain.append(word_patch.apply_lowfour(prev_t,tpatch));steps.append('twelve');nt_=chain[-1]
        pre_t_path=Path(tempfile.mkdtemp())/'pre-twelve.json.gz';pre_t_path.write_bytes(gzip.compress(json.dumps(prev_t,separators=(',',':')).encode(),mtime=0))   # earlier-stage controls run on the state they were written for
        kok&=word_patch.kernel_gate_edit(prev_t['B'],nt_['B'])==tpatch['declared_gate_edit']
        kok&=nt_['report']['width_inventory']==prev_t['report']['width_inventory'] and not any(e_[0]=='warp' for e_ in nt_['B'])
    r7f_=D/'inputs'/f'retired7_43{wt}.json';r7patch=None
    if r7f_.exists():   # PR2802's seven retired-lender aliases and two hostee moves, one declared patch on the twelve state (this package)
        r7patch=json.loads(r7f_.read_text());prev_7=chain[-1];chain.append(word_patch.apply_lowfour(prev_7,r7patch));steps.append('retired7');n7_=chain[-1]
        kok&=word_patch.kernel_gate_edit(prev_7['B'],n7_['B'])==r7patch['declared_gate_edit'] and not any(e_[0]=='warp' for e_ in n7_['B'])
        kok&=n7_['target_levels']==prev_7['target_levels'] and n7_['prelude_events']==prev_7['prelude_events'] and n7_['centers']==prev_7['centers']
    final=json.loads(gzip.decompress(shipped.read_bytes()))
    same=final==chain[-1]
    # lifted-target offsets: the shipped word's set (and frames) must equal the one declared by the last patch input that declares target_levels
    _tl_decl=None
    for _pn in ('lpatch','apatch','apatch2','apatch3','tpatch'):
        _pv=locals().get(_pn)
        if _pv and 'target_levels' in _pv.get('fields',{}):_tl_decl=_pv['fields']['target_levels']
    tl_ok=lambda w_:_tl_decl is not None and w_['target_levels']==_tl_decl
    kok&=tl_ok(final)
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
        import copy as cp9
        _m1=cp9.deepcopy(final);_m1['target_levels'].pop(sorted(_m1['target_levels'],key=int)[0]);_m2=cp9.deepcopy(final);_m2['target_levels'][str(next(t_ for t_ in range(112) if str(t_) not in final['target_levels']))]=next(iter(final['target_levels'].values()));_m3=cp9.deepcopy(final);_m3['target_levels'][sorted(_m3['target_levels'],key=int)[0]]=[999]
        res['target_offsets_declared']=tl_ok(final);res['target_offset_missing_rejected']=not tl_ok(_m1);res['target_offset_extra_rejected']=not tl_ok(_m2);res['target_offset_changed_rejected']=not tl_ok(_m3)
        ok&=res['target_offsets_declared'] and res['target_offset_missing_rejected'] and res['target_offset_extra_rejected'] and res['target_offset_changed_rejected']
        print('TARGET-OFFSETS',wt,'declared by patch input',len(_tl_decl),'missing/extra/changed rejected',res['target_offset_missing_rejected'],res['target_offset_extra_rejected'],res['target_offset_changed_rejected'],flush=True)
        c=subprocess.run([sys.executable,'-B',str(D/'borrow_controls.py'),str(tmp),base,str(RCP/f'CONTROLS-43{wt}.json')],capture_output=True,text=True)
        ok&=c.returncode==0;res['controls_rc']=c.returncode
        if lpatch:
            lc=subprocess.run([sys.executable,'-B',str(D/'lowfour_controls.py'),str(pre_t_path if tpatch else shipped),str(RCP/f'CONTROLS-LOWFOUR-43{wt}.json')],capture_output=True,text=True)
            ok&=lc.returncode==0;res['lowfour_controls_rc']=lc.returncode
        if ppatch:
            pw_=Path(tempfile.mkdtemp())/'orig.json.gz';pw_.write_bytes(gzip.compress(json.dumps(prev_p,separators=(',',':')).encode(),mtime=0))
            pc=subprocess.run([sys.executable,'-B',str(D/'prelife_controls.py'),str(shipped),str(pw_),str(RCP/f'CONTROLS-PRELIFE-43{wt}.json')],capture_output=True,text=True)
            pc_ok=pc.returncode==0 and json.loads((RCP/f'CONTROLS-PRELIFE-43{wt}.json').read_text())['all_rejected_for_expected_reason'];ok&=pc_ok;res['prelife_controls_ok']=pc_ok
        if rpatch2:   # control: the shipped word with the B 894 frame restored to its un-refitted (dim 6) frame must be rejected (the 653<-563 warp then starts from the wrong frame)
            import copy as cp6
            m=cp6.deepcopy(prev_t if tpatch else final);m['B'][894][-1]=prev_r['B'][894][-1];bp=Path(tempfile.mkdtemp())/'refit563_undone.json.gz';bp.write_bytes(gzip.compress(json.dumps(m,separators=(',',':')).encode(),mtime=0))
            br=run_audit(bp,None,bp.parent/'refit563_undone.out.json');ru=br.returncode!=0 and 'warp frame mismatch' in (br.stdout+br.stderr);res['refit563_undone_rejected_by_warp_frame_mismatch']=ru;ok&=ru
        if xpatch:
            xc=subprocess.run([sys.executable,'-B',str(D/'alias1_controls.py'),str(pre_t_path if tpatch else shipped),str(xf),str(RCP/f'CONTROLS-ALIAS1-43{wt}.json')],capture_output=True,text=True)
            ok&=xc.returncode==0;res['alias1_controls_rc']=xc.returncode
        okc=[]
        def stage_controls(state,patch,pre):   # tamper controls on the gates changed by a declared stage; each mutant carries the cleanup re-derived from its own forward word
            import copy as cp7
            _ins=[i_ for i_,e_ in enumerate(state['B']) if e_[0]=='add' and any(k_=='insert' and g_==e_[:-1] for k_,_,g_ in patch['declared_gate_edit'])]
            def _rd7(m):
                t_=cp7.deepcopy(m);t_['A']=m['A'][m['prelude_events']:];m['cleanup']=word_patch.derive_cleanup(t_,{int(q_) for q_ in m['helper_final']});return m
            def _mk7(f_):
                m=cp7.deepcopy(state);f_(m);return _rd7(m)
            for _nm7,_mut7 in ((pre+'_gate_sign_flipped',lambda m:m['B'][_ins[0]].__setitem__(3,-m['B'][_ins[0]][3])),
                               (pre+'_gate_coefficient_doubled',lambda m:m['B'][_ins[0]].__setitem__(3,2*m['B'][_ins[0]][3])),
                               (pre+'_gate_dropped',lambda m:m['B'].pop(_ins[0])),
                               (pre+'_warp_dropped',lambda m:m['warps'].pop(0)),
                               (pre+'_target_frame_changed',lambda m:m['target_levels'].__setitem__(sorted(m['target_levels'],key=int)[0],[30]))):
                m=_mk7(_mut7);bp=pw/(_nm7+'.json.gz');bp.write_bytes(gzip.compress(json.dumps(m,separators=(',',':')).encode()));br=run_audit(bp,None,pw/(_nm7+'.out.json'));res[_nm7+'_rejected']=br.returncode!=0;okc.append(br.returncode!=0)
            print(pre.upper()+'-CONTROLS',wt,{k_:v_ for k_,v_ in res.items() if k_.startswith(pre+'_')},flush=True)
        if tpatch:stage_controls(nt_,tpatch,'twelve')
        if r7patch:stage_controls(final,r7patch,'retired7')
        ok&=all(okc)
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

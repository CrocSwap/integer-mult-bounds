"""word_patch.py: exact structural edits of a BORROW-WORD (kernel edits found on the borrowed words, applied on top of the pinned rebuild).
apply_kernel(word, patch) replaces the sections listed in patch['sections'] (B, warps, and frame-only A/restore changes) and re-derives the explicit inverse-reverse cleanup exactly as build_word.py does;
kernel_gate_edit(old_B, new_B) returns the gate-level edit (frames ignored) that turns the old B section into the new one, so the edit declared in the patch can be checked."""
import copy,difflib,json
V=112;N=704;FULL=[256,128,64,32,16,8,4,2,1]
def _key(g):return json.dumps(g[:-1])
def kernel_gate_edit(old_B,new_B):
    """[('delete',i,gate) | ('insert',i_new,gate)] between the two B sections, ignoring the trailing frame of every gate"""
    ka=[_key(g) for g in old_B];kb=[_key(g) for g in new_B];ed=[]
    for t,i1,i2,j1,j2 in difflib.SequenceMatcher(None,ka,kb,autojunk=False).get_opcodes():
        if t in('delete','replace'):ed+=[['delete',i,old_B[i][:-1]] for i in range(i1,i2)]
        if t in('insert','replace'):ed+=[['insert',j,new_B[j][:-1]] for j in range(j1,j2)]
    return ed
def derive_cleanup(w,restored):
    byp={}
    for op,rec in enumerate(w['warps'],1):byp.setdefault(rec[0],[]).append((op,rec))
    fw=list(w['A'])
    for p in range(len(w['B'])+1):
        for op,rec in sorted(byp.get(p,[]),key=lambda x:x[0]):fw.append(['warp',rec[1],op])
        if p<len(w['B']):fw.append(w['B'][p])
    fw+=w['restore']
    buf=lambda r:r+N if r in restored else r
    out=[]
    for g in reversed([g for g in fw if g[0]=='warp' or not(V<=g[1]<2*V)]):
        if g[0]=='warp':out.append(['warp',buf(g[1]),-g[2],FULL])
        elif g[0]=='add':out.append(['add',buf(g[1]),buf(g[2]),-g[3],g[4],FULL])
        else:out.append(['scale',buf(g[1]),g[3],g[2],FULL])
    return out
def restored_of(w):
    return {g[1]-N for g in w['cleanup'] if g[1]>=N}|{g[2]-N for g in w['cleanup'] if g[0]=='add' and g[2]>=N}
def apply_kernel(w,patch):
    r=copy.deepcopy(w);rs=restored_of(w)
    for k,v in patch['sections'].items():r[k]=copy.deepcopy(v)
    r['report']['local_profile']=patch['local_profile']
    r['cleanup']=derive_cleanup(r,rs)
    return r

def apply_handoff(w,patch):
    """coherent multi-helper handoff edit (retired-source replacement of high roles): replace the listed top-level fields and the report, re-derive the cleanup from the changed word"""
    r=copy.deepcopy(w);rs=restored_of(w)
    for k,v in patch['fields'].items():r[k]=copy.deepcopy(v)
    r['report']=copy.deepcopy(patch['report'])
    r['cleanup']=derive_cleanup(r,rs)
    return r

def apply_lowfour(w,patch):
    """four low aliases through lifted-target compensation (PR2436 mechanism): replace the listed fields; the A section starts with the
    explicit prelude (patch fields['prelude_events'] leading items); the inverse-reverse cleanup is derived WITHOUT the prelude."""
    r=copy.deepcopy(w);rs=restored_of(w)
    for k,v in patch['fields'].items():r[k]=copy.deepcopy(v)
    r['report']=copy.deepcopy(patch['report'])
    t=copy.deepcopy(r);t['A']=r['A'][r['prelude_events']:]
    r['cleanup']=derive_cleanup(t,rs)
    return r

def apply_prelife(w,patch):
    """pre-life hosting (this package): a cold host h, after it has restored itself and retired, hosts the whole life of a dim-0-start
    helper L through one B warp; h stops being cold, so the restored (private-buffer) set of the derived cleanup is the NEW helper_final
    key set (not the input word's).  Replace the listed fields and the report; re-derive the inverse-reverse cleanup without the prelude."""
    r=copy.deepcopy(w)
    for k,v in patch['fields'].items():r[k]=copy.deepcopy(v)
    r['report']=copy.deepcopy(patch['report'])
    t=copy.deepcopy(r);t['A']=r['A'][r.get('prelude_events',0):]
    r['cleanup']=derive_cleanup(t,{int(q) for q in r['helper_final']})
    return r

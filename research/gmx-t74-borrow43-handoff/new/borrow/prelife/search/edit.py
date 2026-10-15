"""apply gate deletions/insertions to a BORROW-WORD and repair frames by forward join-lifting; returns new word or reason"""
import copy;from fm import *
def edit_word(w,dels,ins):
    """dels: set of (sec,i); ins: list of (sec,i_before,gate_without_frame) ; sec in A|B. warp positions in B are remapped."""
    w2=copy.deepcopy(w)
    for sec in ('A','B'):
        old=w[sec];new=[];mp={}
        insb={}
        for (s,i,g) in ins:
            if s==sec:insb.setdefault(i,[]).append(g)
        for i in range(len(old)+1):
            mp[i]=len(new)
            for g in insb.get(i,[]):new.append(list(g)+[None])
            if i<len(old) and (sec,i) not in dels:new.append(copy.deepcopy(old[i]))
        w2[sec]=new
        if sec=='B':
            for rec in w2['warps']:rec[0]=mp[rec[0]]
    return w2
def repair(w2,minimal=False):
    """fill None frames with join of current frames; lift frames that no longer contain current; fail on warp/A-end/end violations"""
    m=FM.__new__(FM)
    # build current frames along the audit order on the raw word
    v=112;h=9;full=basis([1<<i for i in range(h)])
    end=[full]*v+[basis([x for x in range(1,1<<h) if (x&p).bit_count()%2==0]) for p in w2['ports']]+[full]*480
    for q,U in w2['helper_final'].items():end[int(q)]=basis(U)
    cur=[(p,) for p in w2['ports']]+[()]*(v+480)
    for q,U in w2['start_extra'].items():cur[int(q)]=basis(U)
    lifted=0
    def gate(e):
        nonlocal lifted
        rs=regs_of(e);j=join(*[cur[r] for r in rs]) if len(rs)>1 else cur[rs[0]]
        if e[-1] is None or minimal:e[-1]=list(j);f=j
        else:
            f=basis(e[-1])
            if not contained(j,f):f=join(f,j);e[-1]=list(f);lifted+=1
        for r in rs:cur[r]=f
    npre=w2.get('prelude_events',0)
    for e in w2['A'][:npre]:
        if e[0]=='warp':
            if not contained(cur[e[1]],basis(e[3])) if minimal else cur[e[1]]!=basis(e[3]):return 'prelude-warp'
            cur[e[1]]=basis(e[4])
        else:gate(e)
    for e in w2['A'][npre:]:gate(e)
    lev={int(t):basis(U) for t,U in w2.get('target_levels',{}).items()}
    for t in range(v):
        if (not contained(cur[v+t],lev.get(t,()))) if minimal else cur[v+t]!=lev.get(t,()):return 'target-level'
        cur[v+t]=lev.get(t,())
    for q,U in zip(w2['centers'],w2['center_frames']):
        if (not contained(cur[q],basis(U))) if minimal else cur[q]!=basis(U):return 'center'
        cur[q]=basis(U)
    byp={}
    for op,rec in enumerate(w2['warps'],1):byp.setdefault(rec[0],[]).append(op)
    B=w2['B']
    for p in range(len(B)+1):
        for op in byp.get(p,[]):
            rec=w2['warps'][op-1]
            if (not contained(cur[rec[1]],basis(rec[3]))) if minimal else cur[rec[1]]!=basis(rec[3]):return 'warp'
            cur[rec[1]]=basis(rec[4])
        if p<len(B):gate(B[p])
    for e in w2['restore']:gate(e)
    for r in range(704):
        if r in set(w2['removed']):continue
        if not contained(cur[r],end[r]):return 'end:%d'%r
    return w2
def profile_of(w2):
    m=FM(w2);return m.profile(),m

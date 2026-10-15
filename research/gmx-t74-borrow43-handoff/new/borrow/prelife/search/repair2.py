"""taint repair: original frames kept for untainted gates; a gate touching a register whose current frame differs
from the original run gets frame = join(current frames of its registers) (may LOWER the original frame).
Exact checks (as audit_local): warps need equality, target levels / centres equality, ends containment."""
import sys
import os as _os,sys as _sys;_H=_os.path.dirname(_os.path.abspath(__file__));_sys.path[:0]=[_H,_os.path.join(_H,'..','..')]   # this directory and new/borrow (audit_local, word_patch, alias_build)
from audit_local import basis,contained,registers
def join(*xs):return basis([z for x in xs for z in x])
def run(w,orig_cur_trace=None,mode='taint'):
    v=112;full=basis([1<<i for i in range(9)]);n=2*v+w['report']['R']
    end=[full]*v+[basis([x for x in range(1,512) if (x&p).bit_count()%2==0]) for p in w['ports']]+[full]*w['report']['R']
    for q,U in w['helper_final'].items():end[int(q)]=basis(U)
    cur=[(p,) for p in w['ports']]+[()]*(v+w['report']['R'])
    for q,U in w['start_extra'].items():cur[int(q)]=basis(U)
    trace=[];k=[0];changed=[0]
    def gate(e):
        rs=registers(e);f=basis(e[-1]);i=k[0];k[0]+=1
        if orig_cur_trace is not None and mode=='taint':
            if any(cur[r]!=orig_cur_trace[i][j] for j,r in enumerate(rs)):
                nf=join(*[cur[r] for r in rs])
                if nf!=f:changed[0]+=1;e[-1]=list(nf);f=nf
        for r in rs:
            if not contained(cur[r],f):raise AssertionError('nonmonotone %d'%r)
        trace.append(tuple(cur[r] for r in rs))
        for r in rs:cur[r]=f
    npre=w.get('prelude_events',0)
    for e in w['A'][:npre]:
        if e[0]=='warp':
            if cur[e[1]]!=basis(e[3]):raise AssertionError('prelude warp')
            cur[e[1]]=basis(e[4])
        else:gate(e)
    for e in w['A'][npre:]:gate(e)
    lev={int(t):basis(U) for t,U in w.get('target_levels',{}).items()}
    for t in range(v):
        if cur[v+t]!=lev.get(t,()):raise AssertionError('target level')
    for q,U in zip(w['centers'],w['center_frames']):
        if cur[q]!=basis(U):raise AssertionError('center')
    byp={}
    for op,rec in enumerate(w['warps'],1):byp.setdefault(rec[0],[]).append(op)
    for p in range(len(w['B'])+1):
        for op in byp.get(p,[]):
            rec=w['warps'][op-1]
            if cur[rec[1]]!=basis(rec[3]):raise AssertionError('warp %d'%rec[1])
            cur[rec[1]]=basis(rec[4])
        if p<len(w['B']):gate(w['B'][p])
    for e in w['restore']:gate(e)
    rem=set(w['removed'])
    for r in range(n):
        if r not in rem and not contained(cur[r],end[r]):raise AssertionError('end:%d'%r)
    return trace,changed[0]

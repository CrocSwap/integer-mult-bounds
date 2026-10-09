#!/usr/bin/env python3
"""Independent terminal elimination: exact local identities and literal frames.

Prerequisite is verify_deferred_word.py's all-input audit of the parent word.
No construction/producer modules are imported.  The event list is independently
derived from parent chronology, then its forward and reflected frames replayed.
"""
import argparse
from collections import Counter
from functools import lru_cache
import gzip
from hashlib import sha256
import json
from pathlib import Path
from verify_deferred_word import canon,inside,gram_ok,perpendicular

if not __debug__:raise RuntimeError('Assertions required')


def main():
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True)
    p.add_argument('--parent-audit',type=Path,required=True)
    p.add_argument('--case',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    wp=a.parent/'word.json.gz';w=json.loads(gzip.decompress(wp.read_bytes()))
    old=json.loads((a.parent/'complex-profile.json').read_text())
    prior=json.loads((a.parent_audit/'receipt.json').read_text())
    assert prior['word_sha256']==sha256(wp.read_bytes()).hexdigest()
    assert prior['exact_all_dirty_normalization'] and prior['reflected_frame_trace']
    assert all(old[k]==prior[k] for k in ('R','W','total_rank','deficit','safe_one_axis_scalar_groups'))
    assert old['safe_one_axis_scalar_groups']==(4*old['max_coefficient_bits']+16)*old['literal_scalar_terms']
    ep=a.case/'word.json.gz';e=json.loads(gzip.decompress(ep.read_bytes()))
    profile=json.loads((a.case/'complex-profile.json').read_text())
    assert e['input_word_sha256']==prior['word_sha256']
    h,v,R=w['h'],w['v'],w['R'];m=h*h;N=v*v
    removed=set(e['removed']);active=[s for s in range(R) if s not in removed]
    assert removed and len(removed)==len(e['removed']) and active==e['active_roles']
    roots={int(s):j for s,j in w['role_root'].items()}
    leaves={int(s):j for s,j in w['leaf_of'].items()}
    U={int(x):canon(tuple(B)) for x,B in w['frames'].items()}
    sigma={int(s):canon(tuple(B)) for s,B in w['sigma'].items()}
    rf={int(s):canon(tuple(B)) for s,B in w['root_frames'].items()}
    ps=set(w['phase_one']);ds=set(w['deferred']);ops=w['ops']
    writes={s:[] for s in removed}
    for s in removed:
        assert s in roots and s in ds and not w['kind'][roots[s]]
        t=w['target'][roots[s]];alpha=21 if roots[s]<v else -21
        assert w['adjoint_centre'][s] is None
        assert {int(t):c for t,c in w['adjoint_ordinary'][s].items()}=={t:alpha}
    for i,o in enumerate(ops):
        if o[0]=='src':continue
        dst,src=(o[1],o[2]) if o[0]=='add' else (o[2],o[1])
        assert src not in removed
        if dst in removed:
            assert i not in ps;writes[dst].append((i,src,o[3]))
    # These assertions prove elimination over Q, Q(i), and any coefficient
    # ring where 42 is invertible: -alpha*z+alpha*(z+sum updates).
    # A removed role never influences a retained role; the update snapshots
    # below are evaluated at exactly their original indices, not delayed.
    expected=[];curY=[() for _ in range(v)];paths=[[[]] for _ in range(v)]
    def front(t,F,why):
        F=canon(tuple(F));assert inside(curY[t],F)
        if curY[t]!=F:
            expected.append(['target_front',t,list(F),why]);paths[t].append(list(F))
        curY[t]=F
    def direct(s,src,F,i,data=False):
        j=roots[s];t=w['target'][j];alpha=21 if j<v else -21
        front(t,F,['redirect',i,s])
        expected.append(['direct_input' if data else 'direct_aux',t,src,alpha,list(F),i,s])
    def operation(i,inverse=False):
        o=ops[i]
        if o[0]=='src':return
        dst,src=(o[1],o[2]) if o[0]=='add' else (o[2],o[1])
        if dst in removed:
            if not inverse:direct(dst,src,U[o[3]],i)
        else:expected.append(['gate',i,-1 if inverse else 1])
    for s in active:
        if s not in ds:expected.append(['readout',s,-1,False,'initial'])
    for s,j in leaves.items():
        if s not in ds:expected.append(['input',s,j,1])
    for i in w['phase_one']:operation(i)
    for s,j in roots.items():
        if w['kind'][j]:expected.append(['readout',s,1,True,'center'])
    for s in w['deferred']:
        for t in w['reach'][s]:front(t,sigma[s],['old_garbage',s])
        if s not in removed:expected.append(['readout',s,-1,False,'deferred'])
    for s in w['deferred']:
        if s in leaves:
            if s in removed:direct(s,leaves[s],U[w['first_node'][s]],-1,True)
            else:expected.append(['input',s,leaves[s],1])
    for i in range(len(ops)):
        if i not in ps:operation(i)
    for s,j in roots.items():
        if not w['kind'][j]:
            front(w['target'][j],rf[s],['ordinary_root',s])
            if s not in removed:expected.append(['readout',s,1,True,'ordinary'])
    for i in range(len(ops)-1,-1,-1):operation(i,True)
    for s,j in leaves.items():
        if s not in removed:expected.append(['input',s,j,-1])
    # Canonicalize only explicit frame rows; all scalar signs/indices remain
    # exact and in sequence, so omission/sign/retiming mutants are rejected.
    actual=e['events']
    for row in actual:
        if row[0]=='target_front':row[2]=list(canon(tuple(row[2])))
        if row[0] in ('direct_aux','direct_input'):row[4]=list(canon(tuple(row[4])))
    assert actual==expected,'altered event word does not implement certified local elimination'
    assert [[list(canon(tuple(F))) for F in seq] for seq in e['target_paths']]==paths
    print('PASS all-input elimination identity and exact source-snapshot chronology',flush=True)

    zero=();full=canon(tuple(1<<i for i in range(h)))
    current={('x',j):U[j+1] for j in range(v)}
    current.update({('y',j):zero for j in range(v)})
    current.update({('a',s):sigma.get(s,zero) for s in active})
    initial=current.copy();trace=[];ranks=Counter();cleanup=False;directs=0
    def move(reg,F):
        assert reg in current and gram_ok(F)
        oldf=current[reg];assert inside(oldf,F),'illegal frame direction'
        if oldf!=F:
            ranks[len(F)-len(oldf)]+=1;trace.append(('move',reg,oldf,F));current[reg]=F
    def scalar(dst,src,num,den=1):
        assert dst!=src and current[dst]==current[src],'non-coframed scalar update'
        trace.append(('scalar',dst,src,num,den))
    for row in actual:
        mode=row[0]
        inverse=(mode=='gate' and row[2]<0) or (mode=='input' and row[3]<0)
        if inverse and not cleanup:
            for s in active:move(('a',s),full)
            for j in range(v):move(('x',j),full)
            cleanup=True
        if mode=='target_front':move(('y',row[1]),canon(tuple(row[2])))
        elif mode=='gate':
            i,sign=row[1:];o=ops[i]
            dst,src=(o[1],o[2]) if o[0]=='add' else (o[2],o[1])
            if sign>0:move(('a',dst),U[o[3]]);move(('a',src),U[o[3]])
            scalar(('a',dst),('a',src),sign)
        elif mode=='input':
            _,s,j,sign=row;move(('a',s),current[('x',j-1)])
            scalar(('a',s),('x',j-1),sign)
        elif mode in ('direct_aux','direct_input'):
            _,t,src,num,F,i,s=row;F=canon(tuple(F));directs+=1
            reg=('a',src) if mode=='direct_aux' else ('x',src-1)
            if mode=='direct_aux':move(reg,F)
            assert current[reg]==F and current[('y',t)]==F
            scalar(('y',t),reg,num,42)
        else:
            assert mode=='readout';_,s,sign,seeded,tag=row
            assert s in active
            if tag=='center':
                assert seeded and sign==1;move(('a',s),rf[s])
                assert all(current[('y',j)]==zero for j in range(v))
                trace.append(('copy_read',s,rf[s],zero,sign));ranks[h-1]+=1
            elif tag=='ordinary':
                j=roots[s];t=w['target'][j];move(('a',s),rf[s])
                assert current[('y',t)]==rf[s] and sign==1 and seeded
                scalar(('y',t),('a',s),21 if j<v else -21,42)
            elif tag=='initial':
                assert not seeded and sign==-1 and current[('a',s)]==zero
                assert all(current[('y',j)]==zero for j in range(v))
                trace.append(('adjoint_read',s,zero,-1))
            else:
                assert tag=='deferred' and not seeded and sign==-1
                F=sigma[s];assert current[('a',s)]==F
                assert all(current[('y',t)]==F for t in w['reach'][s])
                trace.append(('adjoint_read',s,F,-1))
    assert cleanup and all(current[('a',s)]==full for s in active)
    assert all(current[('x',j)]==full and len(current[('y',j)])==h-1 for j in range(v))
    assert all(reg[1] not in removed for reg in current if reg[0]=='a')
    final=current.copy();bank=lambda reg:('y' if reg[0]=='x' else 'x',reg[1]) if reg[0]!='a' else reg
    @lru_cache(None)
    def comp(F):return perpendicular(F,h)
    reverse={bank(reg):comp(F) for reg,F in final.items()};rranks=Counter();inverse_count=0
    for row in reversed(trace):
        if row[0]=='move':
            _,reg,A,B=row;br=bank(reg)
            assert reverse[br]==comp(B) and inside(comp(B),comp(A))
            reverse[br]=comp(A);rranks[len(B)-len(A)]+=1
        elif row[0]=='scalar':
            _,dst,src,num,den=row
            assert reverse[bank(dst)]==reverse[bank(src)]
            assert den in (1,42) and num in (-21,-1,1,21)
            inverse_count+=1 # exact coefficient is -num/den, same arrow, bank exchanged
        elif row[0]=='copy_read':
            _,s,A,B,sign=row;assert reverse[('a',s)]==comp(A)
            assert all(reverse[('x',j)]==comp(B) for j in range(v))
            assert inside(comp(A),comp(B));rranks[h-1]+=1
        else:
            _,s,F,sign=row;assert reverse[('a',s)]==comp(F)
            reached=w['reach'][s] if s in ds else range(v)
            assert all(reverse[('x',t)]==comp(F) for t in reached)
    assert rranks==ranks and all(reverse[bank(reg)]==comp(F) for reg,F in initial.items())
    print('PASS actual forward/reflected frame traces and fresh-copy macros',flush=True)
    H=Counter({t:2*v*c for t,c in ranks.items()})
    for s in active:H[m-h+len(sigma.get(s,()))]+=2*v
    H[(h-1)**2]+=2*N;H[1]+=N
    assert dict(H)=={int(t):c for t,c in profile['child_multiplicities'].items()}
    newW=2*N+2*v*len(active);mass=sum(t*c for t,c in H.items())
    assert newW==profile['W'] and len(active)==profile['R'] and mass==profile['total_rank']
    assert newW*m-mass==old['deficit']
    # Independent telescoping rank check: every deleted auxiliary packet has
    # mass m, while target-chain rank sums remain h-1 regardless of splitting.
    assert old['total_rank']-mass==2*v*len(removed)*m
    newterms=old['literal_scalar_terms']-2*len(removed)-directs
    assert profile['literal_scalar_terms']==newterms
    assert profile['safe_one_axis_scalar_groups']==(4*old['max_coefficient_bits']+16)*newterms
    receipt=dict(status='PASS independent exact terminal elimination and both physical traces',
        parent_word_sha256=prior['word_sha256'],word_sha256=sha256(ep.read_bytes()).hexdigest(),
        removed_roles=len(removed),R=len(active),W=newW,total_rank=mass,deficit=newW*m-mass,
        direct_updates=directs,actual_trace_events=len(trace),signed_reflected_scalar_events=inverse_count,
        all_input_dirty_identity=True,source_snapshots_at_original_times=True,
        actual_full_profile_reconstructed=True,retained_auxiliary_frames_replayed=True,
        safe_one_axis_scalar_groups=profile['safe_one_axis_scalar_groups'],
        scope='Exact local identities plus audited parent imply all-input Q(i) dirty scalar correctness; concrete forward and signed reverse/complement frames and full paid histogram checked. Inherited phase transform, copy-streaming and analytic/tape compiler remain dependencies.')
    (a.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()

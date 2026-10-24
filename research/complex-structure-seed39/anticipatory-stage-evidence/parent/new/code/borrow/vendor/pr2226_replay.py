#!/usr/bin/env python3
"""Exact replay over a free operator algebra for nominated dirty borrowing.

The current implementation closes cleanup at FULL on every non-target field.
It prices that choice explicitly. This is not a hosted supplier admission.
"""
import argparse,gzip,json,time
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path


def span(basis):
    s={0}
    for x in basis:s|={t^x for t in s.copy()}
    return frozenset(s)


def incident(e):return e[1:3] if e[0]=='add' else e[1:2]


def add(dst,src,c):
    for key,value in list(src.items()):
        z=dst.get(key,Q(0))+c*value
        if z:dst[key]=z
        elif key in dst:del dst[key]


def warp(row,op):
    out={}
    for (var,word),value in row.items():
        word=word[1:] if word and word[0]==-op else (op,)+word
        out[var,word]=value
    return out


def main():
    p=argparse.ArgumentParser();p.add_argument('--word',type=Path,required=True)
    p.add_argument('--blocks',type=Path);p.add_argument('--inventory',type=Path,required=True)
    p.add_argument('--recover-cold',action='store_true')
    p.add_argument('--framed-word',type=Path)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();start=time.monotonic()
    w=json.loads(gzip.decompress(a.word.read_bytes()));blocks=json.loads(a.blocks.read_text())['sources'][0]['blocks'] if a.blocks else []
    inv=json.loads(a.inventory.read_text());pairs=inv['pairs']
    assert len(pairs)==80 and sum(x['low'] for x in pairs)==32
    assert all(x.get('handoff_paid_rank',0)==0 for x in pairs)
    v=w['v'];n=2*v+w['R'];full=span([1<<i for i in range(w['h'])]);frames=list(map(span,w['frames']))
    removed={x['register'] for x in pairs};active=[r for r in range(n) if r not in removed]
    val={r:{(r,()):Q(1)} for r in active};cur={r:frames[w['start'][r]] for r in active}
    anticipation=inv['initial_corrections']
    for term in anticipation:
        target=term['target'];source=term['source'];word=tuple(term['operator_word']);coefficient=Q(term['coefficient'])
        assert v<=target<2*v and source in active and not(v<=source<2*v)
        assert len(w['frames'][w['start'][source]])==0
        assert all(1<=abs(op)<=len(pairs) for op in word)
        assert coefficient.denominator&(coefficient.denominator-1)==0
        add(val[target],{(source,word):Q(1)},coefficient)
    mapping={};profile=Counter();reverse=[];warps=[];framed_steps=[]
    def frame_basis(F):
        b={}
        for x in F:
            while x:
                j=x.bit_length()
                if j not in b:b[j]=x;break
                x^=b[j]
        return [b[j] for j in sorted(b,reverse=True)]
    def resolve(r):return mapping.get(r,r)
    def climb(r,f):
        if not cur[r]<=f:raise ValueError(('nonnested climb',r,len(cur[r]),len(f)))
        d=(len(f).bit_length()-1)-(len(cur[r]).bit_length()-1)
        if d:profile[d]+=1
        cur[r]=f
    def scalar(e,framed=True,record=True):
        rs=[resolve(r) for r in incident(e)]
        if any(r not in val for r in rs):raise ValueError(('unallocated borrowed field',e))
        if framed:
            for r in rs:climb(r,frames[e[-1]])
            framed_steps.append(['gate',rs,frame_basis(frames[e[-1]])])
        if e[0]=='add':
            c=Q(e[3],e[4]);add(val[rs[0]],val[rs[1]],c)
            if record and not(v<=rs[0]<2*v):reverse.append(('add',rs[0],rs[1],c))
        else:
            c=Q(e[2],e[3]);val[rs[0]]={k:c*x for k,x in val[rs[0]].items()}
            if record and not(v<=rs[0]<2*v):reverse.append(('scale',rs[0],c))
    original_target_levels={r:w['start'][r] for r in range(v,2*v)}
    for e in w['precondition']+w['compensation']:
        for r in incident(e):
            if v<=r<2*v:original_target_levels[r]=e[-1]
        if e[0]=='add' and e[2] in removed:continue
        scalar(e,record=False)
    for e in w['A']:scalar(e)
    for r,f in original_target_levels.items():climb(r,frames[f])
    for r,f in original_target_levels.items():framed_steps.append(['pin',r,frame_basis(frames[f])])
    for r,f in zip(w['centers'],w['center_frames']):
        assert cur[r]==frames[f];profile[len(w['frames'][f])]+=1
        framed_steps.append(['pin',r,frame_basis(frames[f])])
    for e in w['cut']:scalar(e,framed=False,record=False)
    deferred={};skip=set()
    for b in blocks:
        ss=set(b['helpers']);part=[]
        for i in range(b['first_correction'],b['first_input']):
            e=w['B'][i]
            if set(incident(e))<=ss:part.append(e);skip.add(i)
        deferred[b['first_input']]=part
    starts={}
    for i,x in enumerate(pairs):starts.setdefault(x.get('handoff_B',x['deadline']),[]).append((i+1,x))
    removed_early_echoes={i for x in pairs if x['low'] for i in x.get('deleted_prefix_indices',x['deleted_echo_indices'])}
    early_rewrites={int(i):gates for x in pairs if x['low'] for i,gates in x.get('early_prefix_rewrites',{}).items()}
    early_tail={}
    for e in inv.get('early_tail_events',[]):early_tail.setdefault(e['before_B'],[]).append(e['gate'])
    for i,e in enumerate(w['B']):
        for t in early_tail.get(i,[]):scalar(t)
        if i in starts:
            for op,x in starts[i]:
                old=x['borrow_from'];new=x['register'];assert x['retirement_B_event']<i
                if x['low']:
                    assert val[old]=={(old,()):Q(1)},'low lender is exactly its restored initial input'
                E_basis=x.get('handoff_basis',x['common_basis'][:x['retirement_dimension']])
                E=span(E_basis)
                paid=abs(len(E_basis)-(len(cur[old]).bit_length()-1))
                assert paid==x.get('handoff_paid_rank',0)
                if paid:profile[paid]+=1
                framed_steps.append(['warp',old,frame_basis(cur[old]),E_basis])
                # A monomial logical K_G aligns the smaller space inside the
                # larger one. The physical adapter pays their dimension gap;
                # the inverse logical reference change at FULL is rank zero.
                val[old]=warp(val[old],op);reverse.append(('warp',old,op));cur[old]=E
                mapping[new]=old;warps.append({'operator':op,'borrow_from':old,'removed':new,
                  'from_basis':w['frames'][x['retirement_frame']],'to_basis':E_basis,
                  'physical_handoff_rank':paid})
                for target,c in x.get('handoff_echo_coefficients',{}).items():
                    target=int(target);climb(target,E);add(val[target],val[old],Q(c))
                    framed_steps.append(['gate',[target,old],E_basis])
        for d in deferred.get(i,[]):scalar(d)
        for d in early_rewrites.get(i,[]):scalar(d)
        if i not in skip and i not in removed_early_echoes:scalar(e)
    for t in early_tail.get(len(w['B']),[]):scalar(t)
    for r in range(v,2*v):climb(r,frames[w['final'][r]])
    bad_y=[]
    for r in range(v,2*v):
        expected={(r,()):Q(1),(r-v,()):Q(1)}
        if val[r]!=expected:bad_y.append(r)
    if bad_y:raise ValueError(('output map failed in exact free operator algebra',bad_y[:12]))
    cold=[r for r in active if not(v<=r<2*v) and len(w['frames'][w['final'][r]])<w['h']]
    # A modular nomination for scalar restoration at the old cold frame.
    # Operator words remain distinct formal coordinates in this diagnostic.
    prime=65521;modular_cache={};cold_span_nominations=[];cold_clearable=[]
    for c in cold:
        V=frames[w['final'][c]]
        pool=tuple(r for r in active if not(v<=r<2*v) and cur[r]<=V<=frames[w['final'][r]])
        if pool not in modular_cache:
            piv={}
            for r in pool:
                x={k:(q.numerator*pow(q.denominator,-1,prime))%prime for k,q in val[r].items()}
                while x:
                    j=min(x)
                    if j not in piv:
                        z=pow(x[j],-1,prime);piv[j]={k:t*z%prime for k,t in x.items()};break
                    z=x[j]
                    for k,t in piv[j].items():
                        y=(x.get(k,0)-z*t)%prime
                        if y:x[k]=y
                        elif k in x:del x[k]
            modular_cache[pool]=piv
        x={(c,()):1};piv=modular_cache[pool]
        while x:
            j=min(x)
            if j not in piv:break
            z=x[j]
            for k,t in piv[j].items():
                y=(x.get(k,0)-z*t)%prime
                if y:x[k]=y
                elif k in x:del x[k]
        if not x:
            cold_span_nominations.append(c)
            dependents=[r for r in active if not(v<=r<2*v) and
                        any(var==c for var,word in val[r])]
            if all(cur[r]<=V and all(not word for var,word in val[r] if var==c) for r in dependents):
                cold_clearable.append(c)
    probe={r:dict(row) for r,row in val.items()};probe_cur=cur.copy();bad_tail_incidence=[]
    moved_tail_indices={e['old_tail_index'] for e in inv.get('early_tail_events',[])}
    for index,e in enumerate(w['tail']):
        if index in moved_tail_indices:continue
        rs=[resolve(r) for r in incident(e)];f=frames[e[-1]]
        for r in rs:
            if not probe_cur[r]<=f:bad_tail_incidence.append((index,r))
            probe_cur[r]=f
        if e[0]=='add':add(probe[rs[0]],probe[rs[1]],Q(e[3],e[4]))
        else:probe[rs[0]]={k:Q(e[2],e[3])*x for k,x in probe[rs[0]].items()}
    cold_fail=[r for r in cold if probe[r]!={(r,()):Q(1)}]
    full_cold_dependence=[r for r in active if not(v<=r<2*v) and r not in cold and
                          any(var in cold for var,word in probe[r])]
    restored=[];cold_witnesses=[]
    def exact_combination(pool,goal):
        piv={}
        for r in pool:
            x=dict(val[r]);code={r:Q(1)}
            while x:
                j=min(x)
                if j not in piv:
                    z=x[j];piv[j]=({k:t/z for k,t in x.items()},{k:t/z for k,t in code.items()});break
                row,coeff=piv[j];z=x[j];add(x,row,-z);add(code,coeff,-z)
        x=dict(goal);code={}
        while x:
            j=min(x)
            if j not in piv:return None
            row,coeff=piv[j];z=x[j];add(x,row,-z);add(code,coeff,z)
        return code
    def dyadic(q):return q.denominator&(q.denominator-1)==0
    def unit(q):return q and dyadic(q) and abs(q.numerator)&(abs(q.numerator)-1)==0
    def cleanup_add(d,s,c,V):
        climb(d,V);climb(s,V);add(val[d],val[s],c);reverse.append(('add',d,s,c));framed_steps.append(['gate',[d,s],frame_basis(V)])
    if a.recover_cold:
        for c in sorted(cold_clearable,key=lambda r:(len(frames[w['final'][r]]),r)):
            V=frames[w['final'][c]]
            pool=[r for r in active if not(v<=r<2*v) and r not in restored and cur[r]<=V]
            solution=exact_combination(pool,{(c,()):Q(1)})
            if solution is None or not all(dyadic(z) for z in solution.values()):continue
            pivot=c if unit(solution.get(c,Q(0))) else next((r for r,z in solution.items() if unit(z)),None)
            if pivot is None:continue
            # All sources are still unchanged while this one row is prepared.
            for r in set(solution)|{c}:climb(r,V)
            factor=solution[pivot]
            if factor!=1:
                val[pivot]={k:factor*z for k,z in val[pivot].items()};reverse.append(('scale',pivot,factor))
                framed_steps.append(['gate',[pivot],frame_basis(V)])
            for r,z in solution.items():
                if r!=pivot:cleanup_add(pivot,r,z,V)
            if pivot!=c:
                val[c],val[pivot]=val[pivot],val[c];reverse.append(('swap',c,pivot))
                framed_steps.append(['gate',[c,pivot],frame_basis(V)])
            assert val[c]=={(c,()):Q(1)}
            for r in active:
                if v<=r<2*v or r==c:continue
                assert all(not word for var,word in val[r] if var==c)
                z=val[r].get((c,()),Q(0))
                if z:cleanup_add(r,c,-z,V)
            assert all(not any(var==c for var,word in val[r]) for r in active if not(v<=r<2*v) and r!=c)
            restored.append(c);cold_witnesses.append({'register':c,'frame':w['final'][c],
                         'preparation':{str(r):str(z) for r,z in solution.items()}})
    for r in active:
        if not(v<=r<2*v) and r not in restored:climb(r,full)
    # Restored cold inputs are decoupled. Their FULL-frame substitutes are
    # private zero buffers; no recursive child runs during this cleanup.
    work={r:({} if r in restored else dict(row)) for r,row in val.items()}
    negative={r:dict(work[r]) for r in active if not(v<=r<2*v)}
    for e in reversed(reverse):
        if e[0]=='add':
            _,d,s,c=e;add(work[d],work[s],-c);add(negative[d],negative[s],-c)
        elif e[0]=='scale':
            _,d,c=e;work[d]={k:x/c for k,x in work[d].items()};negative[d]={k:x/c for k,x in negative[d].items()}
        elif e[0]=='swap':
            _,d,s=e;work[d],work[s]=work[s],work[d];negative[d],negative[s]=negative[s],negative[d]
        else:
            _,d,op=e;work[d]=warp(work[d],-op)
    for r in active:
        if not(v<=r<2*v) and work[r]!=({} if r in restored else {(r,()):Q(1)}):raise ValueError(('cleanup failed',r))
    rejected=[r for r,row in negative.items() if row!=({} if r in restored else {(r,()):Q(1)})]
    if not rejected:raise ValueError('missing inverse warp negative control did not fail')
    mass=sum(r*c for r,c in profile.items());copy=64;noncopy=mass-copy;stock=Q(896,9);m=73
    idle=72*stock-noncopy
    aa=.00177
    numerical=(sum(c*(r/m)**(1-aa) for r,c in profile.items())+float(idle)/51*(51/m)**(1-aa))/float(stock)
    out={'status':'PASS_EXACT_FREE_OPERATOR_BORROWING_REPLAY','original_registers':n,
       'remaining_registers':len(active),'removed_helper_registers':len(removed),
       'independent_input_columns':len(active),'symbolic_warps':warps,'target_map':'Y+=X',
       'all_non_target_inputs_restored':True,'omitted_inverse_warps_rejected_registers':rejected,
       'early_tail_events':inv.get('early_tail_events',[]),
       'initial_anticipatory_corrections':anticipation,
       'new_cleanup':('restore selected cold rows, decouple their inputs, then reverse the non-target word at FULL using zero buffers'
                      if restored else 'reverse every non-target scalar/warp at FULL; old tail omitted'),
       'exact_cold_restoration':cold_witnesses,'zero_FULL_cleanup_buffers':len(restored),
       'unchanged_cold_tail_probe':{'cold_roles':len(cold),'failed_cold_outputs':cold_fail,
          'full_roles_still_depending_on_cold_inputs':full_cold_dependence,
          'nonnested_tail_incidences':bad_tail_incidence,
          'claim':'diagnostic only; unchanged cold tail is not adopted'},
       'cold_frame_scalar_restoration_modular_nominations':cold_span_nominations,
       'cold_clearance_modular_nominations':cold_clearable,
       'local_profile':dict(sorted(profile.items())),'local_mass':mass,'noncopy_mass':noncopy,
       'favorable_idle_mass_per_call':str(idle),'favorable_numerical_moment_at_a_0_00177':numerical,
       'seconds':time.monotonic()-start,
       'scope':'exact operator-algebra scalar replay plus proposed frame dimensions; physical Clifford recipes, both orientations, ownership, exact invoice and bit rail remain unresolved'}
    a.output.write_text(json.dumps(out,indent=2)+'\n');print('PASS_FIXED_BORROWED_WORD columns='+str(len(active))+' removed='+str(len(removed))+' cold='+str(len(restored)))
    if a.framed_word:
        data={'start':{str(r):w['frames'][w['start'][r]] for r in active},
          'final':{str(r):frame_basis(cur[r]) for r in active},'steps':framed_steps,
          'copy_profile':dict(Counter(len(w['frames'][f]) for f in w['center_frames'])),
          'handoff_profile':dict(Counter(x.get('physical_handoff_rank',0) for x in warps if x.get('physical_handoff_rank',0))),
          'original_profile':dict(sorted(profile.items())),'h':w['h']}
        a.framed_word.write_text(json.dumps(data,separators=(',',':'))+'\n')


if __name__=='__main__':main()

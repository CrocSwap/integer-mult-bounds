"""Original exact trace-commutation check and conservative scalar norm transport.

If all swaps commute and each destination's update order changes by moving only
one unit-coefficient update, each new row lies on the old row trajectory or is
one old row plus/minus one old source row. Both forward and inverse maxima grow
by at most two. Upstream programs are never executed.
"""
from pathlib import Path
from collections import defaultdict,deque,Counter
import gzip,json,hashlib,time
ROOT=Path(__file__).resolve().parent
import check_complete_suffix as scalar
import source_data as sd

def check(old,new):
    assert Counter(tuple(z[:3])for z in old)==Counter(tuple(z[:3])for z in new)
    buckets=defaultdict(deque)
    for i,z in enumerate(old):buckets[tuple(z[:3])].append(i)
    desired=[buckets[tuple(z[:3])].popleft()for z in new]
    assert len(set(desired))==len(old)
    old_rows=defaultdict(list);new_rows=defaultdict(list)
    for i,z in enumerate(old):old_rows[z[0]].append(i)
    for i in desired:new_rows[old[i][0]].append(i)
    changed=[]
    for dest,seq in old_rows.items():
        target=new_rows[dest]
        if seq==target:continue
        # No quadratic search over all updates: only at most three updates
        # are expected on affected targets; still test the literal sequences.
        chosen=next((x for x in seq if abs(old[x][2])==1 and
                     [i for i in seq if i!=x]==[i for i in target if i!=x]),None)
        assert chosen is not None,('more than one update moved on row',dest)
        changed.append(dict(destination=dest,moved_old_event=chosen,
                            moved_gate=old[chosen][:3],old_order=seq,new_order=target))
    current=list(range(len(old)));pos=current[:];swaps=0
    for i,wanted in enumerate(desired):
        j=pos[wanted];assert j>=i
        if j==i:continue
        a,b,c=old[wanted][:3]
        for k in range(i,j):
            token=current[k];d,e,f=old[token][:3]
            assert b!=d and e!=a,('noncommuting crossed additions',old[wanted],old[token])
            pos[token]+=1;swaps+=1
        current[i:j+1]=[wanted]+current[i:j];pos[wanted]=i
    assert current==desired
    return dict(commuting_adjacent_swaps=swaps,destinations_with_changed_update_order=changed,
                forward_norm_factor=2,inverse_norm_factor=2)

def run():
    start=time.monotonic();_,old,new,_=scalar.build()
    certificate=check(old,new)
    assert len(certificate['destinations_with_changed_update_order'])==12
    pins=sd.read_json('expected/kernel-pins.json')
    old_forward=pins['forward_max_row_l1'];old_inverse=pins['inverse_max_row_l1']
    assert (old_forward,old_inverse)==(77985,2475558)
    forward=2*old_forward;inverse=2*old_inverse;payload=64*forward**3*inverse**2
    assert payload<2**104
    return dict(status='PASS_EXACT_SCALAR_NORM_TRANSPORT',suffix_additions=len(old),
       **certificate,original_forward_bound=old_forward,original_inverse_bound=old_inverse,
       new_forward_bound=forward,new_inverse_bound=inverse,payload_upper=payload,
       payload_bits=payload.bit_length(),retained_payload_cap_bits=104,
       unchanged_literal_scalar_multiset=True,
       source_hashes={name:hashlib.sha256(json.dumps(events,separators=(',',':')).encode()).hexdigest()for name,events in [('original_suffix',old),('modified_suffix',new)]},
       theorem='Commuting swaps preserve each source value sampled by a gate. Every unchanged destination update sequence has the old row-value trajectory. Each changed destination order moves one unit update; at intermediate cuts its row is an old row plus or minus that same old source row. Reversing both schedules gives the identical property. The unchanged prefix is composed using the retained old global row-norm bounds.',
       scope='Changed scalar suffix and retained old prefix bounds only. Address geometry and inherited finite compiler hypotheses are separate.',seconds=time.monotonic()-start)

if __name__=='__main__':
    x=run()
    print(x['status'],'swaps',x['commuting_adjacent_swaps'],'changed row orders',len(x['destinations_with_changed_update_order']),'payload bits',x['payload_bits'],'seconds',x['seconds'])

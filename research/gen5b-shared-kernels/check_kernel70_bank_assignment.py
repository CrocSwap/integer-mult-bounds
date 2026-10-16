"""Explicit role-resolved bank assignment for the 70-pivot and final12 rewrite."""
from collections import Counter,defaultdict
from fractions import Fraction
import hashlib,json,time
from check_complete_suffix import read,HERE,CANDIDATE_FILE
import kernel70_witness

def run(output_dir=None, mutation=None):
    started=time.monotonic()
    w=read('gen5bit__selected__bit__word_p12.json.gz.base64')
    selection=read(CANDIDATE_FILE)['candidates'];kernel=read('kernel-selection.json')
    restore=read('restore-selection.json')['entries'];sinks=read('sink-selection.json')['sinks']
    removed={b for a,b in w['pairs']};regs=sorted(set(range(17160))-removed)
    original_from_stream={3520+i:r for i,r in enumerate(regs)}
    sinkroles={r['role']for r in sinks};roles=sorted(set(regs)-sinkroles)
    assert len(roles)==15427
    entrances={r:0 for r in roles};entrance_type={r:'ZERO'for r in roles}
    for z in w['gauges']:
        if z['role']in entrances:
            entrances[z['role']]=z['dim'];entrance_type[z['role']]=f'frame:{z["frame"]}'
    pivots=[(z['a'],z['rank'])for z in kernel['pairs']]+[(z['pivot'],z['rank'])for z in kernel['families']]
    pivot_residuals=Counter()
    for stream,rank in pivots:
        role=original_from_stream[stream];assert entrances[role]==0
        entrances[role]=rank;entrance_type[role]=f'kernel:{stream}'
        pivot_residuals[24-rank]+=1
    new_kernel=kernel70_witness.load()['entries']
    assert len(new_kernel)==70 and len({z['pivot']for z in new_kernel})==70
    for z in new_kernel:
        role=original_from_stream[z['pivot']]
        assert role==z['virtual_pivot'] and entrances[role]==0
        assert z['rank']==1 and len(z['basis'])==1
        entrances[role]=1
        entrance_type[role]=f'shared_kernel:{z["pivot"]}'
        pivot_residuals[23]+=1
    endpoints={r:24 for r in roles};endpoint_type={r:'FULL'for r in roles}
    undo={z['old_restored_helper_stream']for z in selection}
    assert len(undo)==6
    retained=[z for z in restore if z['helper']not in undo]
    assert len(retained)==434
    for z in retained:
        r=original_from_stream[z['helper']];assert entrances[r]==20
        endpoints[r]=23;endpoint_type[r]=f'old_restore:{z["helper"]}'
    for z in selection:
        r=z['helper'];assert entrances[r]==21 and endpoints[r]==24
        endpoints[r]=23;endpoint_type[r]=f'frame:{z["new_endpoint"]}'
    families=defaultdict(list)
    for r in roles:
        width=endpoints[r]-entrances[r];assert 0<width<=24
        families[width].append(r)
    if mutation=='duplicate_role':families[2][1]=families[2][0]
    assert sorted(r for group in families.values()for r in group)==roles, 'Missing or duplicated helper role'
    counts={r:len(rs)for r,rs in families.items()}
    assert counts[2]==12 and counts[3]==456 and counts[4]==1748
    assert counts[23]==1644 and counts[24]==11403
    assert sum(r*c for r,c in counts.items())==322864
    # Retain all mixed source templates; adjust only the three pure bins.
    patterns=[([7]*12+[4]*9,10)]
    for width,n in sorted(pivot_residuals.items(),reverse=True):
        assert 4<width<24
        patterns.append(([width]*4+[24]+[4]*(24-width),15*n))
    used=Counter()
    for widths,n in patterns:
        assert sum(widths)==120
        used.update({r:widths.count(r)*n for r in set(widths)})
    for width in (2,3,4,6,24):
        leftover=60*counts[width]-used[width];blocks=120//width
        assert leftover>=0 and 120%width==0 and leftover%blocks==0
        patterns.append(([width]*blocks,leftover//blocks))
    total=Counter();segments=defaultdict(list);bank_start=0
    for pattern,(widths,n) in enumerate(patterns):
        assert sum(widths)==120 and n>0
        offsets=[];x=0
        for r in widths:offsets.append(x);x+=r
        for r in set(widths):
            blocks=[(i,offsets[i])for i,v in enumerate(widths)if v==r]
            lo=total[r];hi=lo+n*len(blocks)
            segments[r].append(dict(lo=lo,hi=hi,pattern=pattern,bank_start=bank_start,blocks=blocks))
            total[r]=hi
        bank_start+=n
    assert total=={r:60*n for r,n in counts.items()}
    assert bank_start==161432
    def assignment(role_index,replica,width):
        q=60*role_index+replica
        for s in segments[width]:
            if s['lo']<=q<s['hi']:
                bank_offset,within=divmod(q-s['lo'],len(s['blocks']))
                block,offset=s['blocks'][within]
                return s['bank_start']+bank_offset,block,offset
        raise AssertionError('Unassigned role occurrence')
    occupied=set();digest=hashlib.sha256()
    for width,rs in sorted(families.items()):
        for index,role in enumerate(rs):
            for replica in range(60):
                bank,block,offset=assignment(index,replica,width)
                assert (bank,block)not in occupied;occupied.add((bank,block))
                assert 0<=offset<offset+width<=120
                digest.update(f'{role},{replica},{bank},{block},{offset},{width}\n'.encode())
    assert len(occupied)==60*len(roles)==925620
    assert 120*bank_start==60*sum(r*c for r,c in counts.items())
    table=dict(schema='role-resolved-bank-assignment/1',stages=5,replicas=60,width=120,
        stage_banks=bank_start,new_shared_kernel_pivots=70,patterns=[dict(widths=widths,count=n)for widths,n in patterns],
        families={str(r):rs for r,rs in sorted(families.items())},segments=dict(segments),
        entry_frame_by_role=entrance_type,endpoint_frame_by_role=endpoint_type,
        address_formula='For rank r role at sorted index j and replica v, q=60*j+v. Find segment lo<=q<hi; divide q-lo by segment block count to obtain bank offset and block index. Stage s uses global family 422400+s*161432+stage_bank. Normalizer scalar is block+1.',
        assignment_sha256=digest.hexdigest())
    if output_dir is not None:
        from pathlib import Path
        output_dir=Path(output_dir);output_dir.mkdir(parents=True,exist_ok=True)
        (output_dir/'bank-address-table.json').write_text(json.dumps(table,separators=(',',':'))+'\n')
    return dict(status='PASS_UNIFIED_KERNEL70_CORETIME12_BANK_ASSIGNMENT',helper_roles=len(roles),
        retained_old_restorations=434,new_restorations=12,reverted_old_restorations=6,
        family_counts=counts,new_shared_kernel_pivots=70,residual_rank_per_replica=322864,
        banks_per_stage=bank_start,total_banks=5*bank_start,literal_data_stock=422400,
        literal_stock=422400+5*bank_start,unreplicated_stock=str(Fraction(422400+5*bank_start,60)),
        checked_role_replica_assignments_per_stage=len(occupied),total_stage_assignments=5*len(occupied),
        stages_have_disjoint_bank_namespaces=True,all_banks_full=True,
        maximum_block_scalar=max(len(widths)for widths,n in patterns),
        assignment_sha256=digest.hexdigest(),seconds=time.monotonic()-started,
        scope='Role-resolved bijection into explicit full 120-wide banks, all 60 replicas. Five stages use disjoint bank namespaces. Existing address-normalizer and cover compiler contracts remain inherited; new/reverted chart factors are separately checked.')

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions required')
    r=run()
    print(json.dumps(r,indent=2))

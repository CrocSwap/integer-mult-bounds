"""Explicit role-resolved bank assignment for the bounded shared-kernel rewrite on the weighted PR305 word."""
from collections import Counter,defaultdict
from fractions import Fraction
import hashlib,json,time
from source_data import read,verify,ROOT,HEAD

def run(candidate_path, output_dir=None, mutation=None):
    started=time.monotonic();verify()
    w=read('gen5bit/selected/bit/word_p12.json.gz')
    kernel=read('kernel-selection.json')
    restore=read('restore-selection.json')['entries'];sinks=read('sink-selection.json')['sinks']
    removed={b for a,b in w['pairs']};regs=sorted(set(range(17160))-removed)
    original_from_stream={3520+i:r for i,r in enumerate(regs)}
    sinkroles={r['role']for r in sinks};roles=sorted(set(regs)-sinkroles)
    pins=read('expected/kernel-pins.json');R=pins['physical_R'];assert R==15424
    assert len(roles)==R
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
    from pathlib import Path
    raw_candidate=Path(candidate_path).read_bytes()
    candidate=json.loads(raw_candidate);assert candidate['source_head']==HEAD
    new_kernel=candidate['entries']
    new_count=len(new_kernel)
    assert new_count>0 and new_count%2==0 and len({z['pivot']for z in new_kernel})==new_count
    for z in new_kernel:
        role=original_from_stream[z['pivot']]
        assert role==z['virtual_pivot'] and entrances[role]==0
        assert z['rank']==1 and len(z['basis'])==1
        entrances[role]=1
        entrance_type[role]=f'shared_kernel:{z["pivot"]}'
        pivot_residuals[23]+=1
    endpoints={r:24 for r in roles};endpoint_type={r:'FULL'for r in roles}
    assert len(restore)==440
    for z in restore:
        r=original_from_stream[z['helper']];assert entrances[r]==z['dims'][0]
        endpoints[r]=z['rank'];endpoint_type[r]=f'old_restore:{z["helper"]}'
    families=defaultdict(list)
    for r in roles:
        width=endpoints[r]-entrances[r];assert 0<width<=24
        families[width].append(r)
    if mutation=='duplicate_role':families[3][1]=families[3][0]
    assert sorted(r for group in families.values()for r in group)==roles, 'Missing or duplicated helper role'
    counts={r:len(rs)for r,rs in families.items()}
    expected={int(k):v for k,v in pins['bank_families'].items()};expected[23]+=new_count;expected[24]-=new_count
    assert counts==expected
    baseline_rank=sum(int(r)*c for r,c in pins['bank_families'].items())
    assert baseline_rank==322906
    assert sum(r*c for r,c in counts.items())==baseline_rank-new_count
    # Retain all mixed source templates; adjust only the three pure bins.
    patterns=[([7]*12+[4]*9,10)]
    for width,n in sorted(pivot_residuals.items(),reverse=True):
        assert 4<width<24
        patterns.append(([width]*4+[24]+[4]*(24-width),15*n))
    used=Counter()
    for widths,n in patterns:
        assert sum(widths)==120
        used.update({r:widths.count(r)*n for r in set(widths)})
    for width in (3,4,6,24):
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
    assert bank_start==pins['banks_total']//5-new_count//2
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
    assert len(occupied)==60*len(roles)==925440
    assert 120*bank_start==60*sum(r*c for r,c in counts.items())
    table=dict(schema='role-resolved-bank-assignment/1',stages=5,replicas=60,width=120,
        stage_banks=bank_start,new_shared_kernel_pivots=new_count,patterns=[dict(widths=widths,count=n)for widths,n in patterns],
        families={str(r):rs for r,rs in sorted(families.items())},segments=dict(segments),
        entry_frame_by_role=entrance_type,endpoint_frame_by_role=endpoint_type,
        address_formula='For rank r role at sorted index j and replica v, q=60*j+v. Find segment lo<=q<hi; divide q-lo by segment block count to obtain bank offset and block index. Stage s uses global family 422400+s*stage_banks+stage_bank. Normalizer scalar is block+1.',
        assignment_sha256=digest.hexdigest())
    if output_dir is not None:
        from pathlib import Path
        output_dir=Path(output_dir);output_dir.mkdir(parents=True,exist_ok=True)
        (output_dir/'bank-address-table.json').write_text(json.dumps(table,separators=(',',':'))+'\n')
    return dict(status='PASS_PR305_SHARED_KERNEL_ROLE_BANK_ASSIGNMENT',helper_roles=len(roles),
        retained_old_restorations=440,new_restorations=0,reverted_old_restorations=0,source_head=HEAD,
        candidate_sha256=hashlib.sha256(raw_candidate).hexdigest(),
        family_counts=counts,new_shared_kernel_pivots=new_count,residual_rank_per_replica=baseline_rank-new_count,
        banks_per_stage=bank_start,total_banks=5*bank_start,literal_data_stock=422400,
        literal_stock=422400+5*bank_start,unreplicated_stock=str(Fraction(422400+5*bank_start,60)),
        checked_role_replica_assignments_per_stage=len(occupied),total_stage_assignments=5*len(occupied),
        stages_have_disjoint_bank_namespaces=True,all_banks_full=True,
        maximum_block_scalar=max(len(widths)for widths,n in patterns),
        assignment_sha256=digest.hexdigest(),seconds=time.monotonic()-started,
        scope='Role-resolved bijection into explicit full 120-wide banks, all 60 replicas. Five stages use disjoint bank namespaces. Existing address-normalizer and cover compiler contracts remain inherited; new chart factors are separately checked; no final12 endpoint saving is transferred.')

if __name__=='__main__':
    import sys
    if not __debug__:raise RuntimeError('Assertions required')
    r=run(sys.argv[1]);print(json.dumps(r,indent=2))

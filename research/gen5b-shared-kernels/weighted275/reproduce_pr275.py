"""Independent arithmetic replay of PR275's pinned declared profile.

Reads upstream JSON/gzip data only. Upstream Python files are never imported or
executed. This reproduces declared profile arithmetic, not physical admission.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path
import gzip, hashlib, json, os
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
import exact_intervals as ex
import assembly_arithmetic as ae

HERE = Path(__file__).resolve().parent
from source_data import SOURCE
HEAD = '10b40041d4ab8a6610083e95bc571aee3468bca2'

def read(name):
    from source_data import read as pinned_read, pins
    return pins() if name=='PINS.json' else pinned_read(name)

def histogram(d):
    assert all(str(int(r)) == str(r) and type(n) is int for r,n in d.items())
    return Counter({int(r): n for r,n in d.items() if int(r)>0 and n})

def mass(h):
    return sum(r*n for r,n in h.items())

def clean(h):
    return {r:n for r,n in sorted(h.items()) if n}

def verify_sources():
    pins=read('PINS.json')
    assert pins['commit']==HEAD
    for name,row in pins['files'].items():
        data=(SOURCE/row['local']).read_bytes()
        assert len(data)==row['bytes']
        assert hashlib.sha256(data).hexdigest()==row['sha256']
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob']
    return dict(pinned_head=HEAD,verified_files=len(pins['files']),upstream_programs_executed=False)

def kernel_delta():
    k=read('kernel-selection.json')
    ranks=defaultdict(set);first={};pivots={};donors=Counter()
    for row in k['pairs']+k['families']:
        pivot=row.get('pivot',row.get('a'))
        ds=row.get('donors',[row.get('b')]);pivots[pivot]=row['rank']
        dims=row['first_frame_dims']
        dims={pivot:dims[0],ds[0]:dims[1]} if isinstance(dims,list) else {int(r):d for r,d in dims.items()}
        assert set(dims)=={pivot,*ds}
        for role,dimension in dims.items():
            assert role not in first or first[role]==dimension
            first[role]=dimension;ranks[role].add(row['rank'])
        donors.update(ds)
    assert not set(pivots)&set(donors)
    h=Counter()
    for role,visits in ranks.items():
        h[first[role]]-=1;previous=pivots.get(role,0)
        for dimension in sorted(visits)+[first[role]]:
            assert dimension>=previous
            if dimension>previous:h[dimension-previous]+=1
            previous=dimension
    assert clean(h)==dict(histogram(k['expected_local_delta']))
    assert mass(h)==-sum(pivots.values())
    return h,dict(entries=len(pivots),pairs=len(k['pairs']),families=len(k['families']),
        entrance_rank=sum(pivots.values()),distinct_donors=len(donors),
        shared_donors=sum(n>1 for n in donors.values()),max_donor_multiplicity=max(donors.values()),
        histogram_delta=clean(h),method='One ordered entrance-dimension chain per member, counting shared donors once. Dimension arithmetic only; nesting is an inherited geometry obligation.')

def inventory():
    w=read('gen5bit/selected/bit/word_p12.json.gz')
    k=read('kernel-selection.json');rest=read('restore-selection.json');sink=read('sink-selection.json')
    removed={b for a,b in w['pairs']};regs=sorted(set(range(17160))-removed)
    bystream={3520+i:r for i,r in enumerate(regs)}
    sinks={row['role'] for row in sink['sinks']}
    assert all(bystream[row['stream']]==row['role'] for row in sink['sinks'])
    roles=set(regs)-sinks;entrance={r:0 for r in roles};endpoint={r:24 for r in roles}
    for row in w['gauges']:
        if row['role'] in roles:entrance[row['role']]=row['dim']
    pivot_residual=Counter()
    for row in k['pairs']+k['families']:
        stream=row.get('pivot',row.get('a'));role=bystream[stream]
        assert entrance[role]==0
        entrance[role]=row['rank'];pivot_residual[24-row['rank']]+=1
    for row in rest['entries']:
        role=bystream[row['helper']]
        assert entrance[role]==row['dims'][0] and endpoint[role]==24
        endpoint[role]=row['rank']
    families=Counter(endpoint[r]-entrance[r] for r in roles)
    gauges=Counter(x for x in entrance.values() if x)
    completion=Counter(entrance[r]+24-endpoint[r] for r in roles if entrance[r])
    assert len(roles)==sum(families.values()) and min(families)>0
    # A primal width-120 packing: retained mixed pivot and rank-7 templates,
    # then exact pure-bin fills. y_r=r/120 is the volume lower-bound dual.
    patterns=[dict(widths=[7]*12+[4]*9,count=10)]
    for width,count in sorted(pivot_residual.items()):
        patterns.append(dict(widths=[width]*4+[24]+[4]*(24-width),count=15*count))
    used=Counter()
    for row in patterns:
        assert sum(row['widths'])==120
        used.update({r:n*row['count'] for r,n in Counter(row['widths']).items()})
    for width in (3,4,6,24):
        remaining=60*families[width]-used[width];blocks=120//width
        assert 120%width==0 and remaining>=0 and remaining%blocks==0
        if remaining:patterns.append(dict(widths=[width]*blocks,count=remaining//blocks))
    packed=Counter()
    for row in patterns:packed.update({r:n*row['count'] for r,n in Counter(row['widths']).items()})
    assert packed==Counter({r:60*n for r,n in families.items()})
    banks=sum(row['count'] for row in patterns)
    assert 120*banks==60*mass(families)
    p=read('expected/kernel-pins.json')
    for field,actual in [('bank_families',families),('pivot_residual_census',pivot_residual),('entrance_rank_histogram',gauges),('completion_rank_histogram',completion)]:
        assert dict(actual)==dict(histogram(p[field])),(field,actual,p[field])
    assert len(roles)==p['physical_R']
    assert 5*banks==p['banks_total']
    stock=60*4*1760+5*banks
    assert stock==p['literal_stock']
    return dict(physical_R=len(roles),kernel_entries=sum(pivot_residual.values()),
        restore_helpers=len(rest['entries']),sink_count=len(sinks),entrance_count=sum(gauges.values()),
        entrance_rank_histogram=clean(gauges),completion_rank_histogram=clean(completion),
        residual_census=clean(families),pivot_residual_census=clean(pivot_residual),
        residual_rank=mass(families),banks_per_stage=banks,banks_total=5*banks,
        literal_data_stock=60*4*1760,literal_stock=stock,packing_patterns=patterns,
        packing_optimal_for_declared_widths=True,packing_unused_coordinates=0,
        scope='Exact declared role inventory and zero-waste width packing; no chronological bank admission claimed.')

def final_profile():
    h,base=base_profile();kd,kernel=kernel_delta()
    target=read('target-selection.json');td=Counter()
    for row in target['groups']:td.update(histogram(row['local_histogram_delta']))
    assert clean(td)==dict(histogram(target['expected_total_delta']))
    restore=read('restore-selection.json');rd=Counter()
    for row in restore['entries']:
        entrance,helper,donor,end=row['dims'];assert entrance<helper<=end and donor<=end
        # Replace helper->FULL by helper->end and split donor->FULL at end.
        rd[24-helper]-=1;rd[24-donor]-=1
        for width in (end-helper,end-donor,24-end):
            if width:rd[width]+=1
    assert clean(rd)==dict(histogram(restore['expected_local_delta']))
    sink=read('sink-selection.json');sd=Counter()
    for row in sink['sinks']:
        rank=len(row['root_frame_basis']);sd[rank]-=1;sd[24-rank]-=1
    assert clean(sd)==dict(histogram(sink['expected_local_delta']))
    p=read('expected/kernel-pins.json');stages={}
    deltas=[('descent',histogram(read('descent-selection.json')['expected_local_histogram_delta'])),
        ('target',td),('kernel',kd),('descent2',histogram(read('descent2-selection.json')['expected_local_histogram_delta'])),
        ('restore',rd),('sink',sd)]
    for name,delta in deltas:
        h.update(delta);assert min(h.values())>=0
        stages[name]=dict(calls=sum(h.values()),rank_mass=mass(h),delta=clean(delta),
            delta_calls=sum(delta.values()),delta_rank_mass=mass(delta))
    assert stages['kernel']['rank_mass']==p['kernel_helper_rank_mass']
    assert stages['descent2']['delta_calls']==65 and stages['descent2']['delta_rank_mass']==0
    final=Counter({r:5*n for r,n in h.items() if n});final.update({4:3520,23:3520,46:3520,50:3520})
    assert sum(final.values())==p['priced_five_stage_calls'] and mass(final)==p['priced_five_stage_rank_mass']
    completion=Counter({5*r:n for r,n in histogram(p['completion_rank_histogram']).items()})
    uncompacted=final.copy();uncompacted.update(completion)
    assert sum(uncompacted.values())==p['sink_five_stage_calls'] and mass(uncompacted)==p['final_five_stage_rank_mass']
    return final,dict(base=base,kernel=kernel,target_groups=len(target['groups']),stages=stages,
        final_local_histogram=clean(h),final_local_calls=sum(h.values()),final_local_rank_mass=mass(h),
        priced_five_stage_histogram=clean(final),priced_five_stage_calls=sum(final.values()),priced_five_stage_rank_mass=mass(final),
        with_completions_calls=sum(uncompacted.values()),with_completions_rank_mass=mass(uncompacted),
        declared_census_inputs=['gen5bit/selected/bit/profile_p12.json: source_data_histogram and target_data_histogram'],
        declared_delta_inputs=['descent-selection.json: expected_local_histogram_delta','descent2-selection.json: expected_local_histogram_delta'],
        scope='Independent arithmetic from pinned word/frame dimensions and declared selections; does not execute or certify upstream physical admission.')

def base_profile():
    w = read('gen5bit/selected/bit/word_p12.json.gz')
    frames = read('gen5bit/selected/bit/frames_p12.json.gz')
    profile = read('gen5bit/selected/bit/profile_p12.json')
    dims = {int(k):v['dim'] for k,v in frames['frames'].items()}
    assert profile['h'] == frames['h'] == 24
    assert profile['R'] == 17160 and profile['v'] == 1760
    gauges = {row['role']:row for row in w['gauges']}
    assert all(row['dim'] == dims[row['frame']] for row in gauges.values())
    source_nodes = {role:int(node) for node,role in w['sources'].items()}
    reuse = dict(w['pairs'])
    removed = set(reuse.values())
    assert len(reuse) == len(removed) == len(w['pairs'])
    assert not set(reuse) & removed
    assert all(a not in gauges and b in gauges for a,b in reuse.items())
    phase = set(w['phase1'])
    order = list(w['phase1']) + [i for i in range(len(w['ops'])) if i not in phase]
    assert len(order) == len(set(order)) == len(w['ops'])
    paths = defaultdict(list)
    for i in order:
        for role in w['ops'][i][:2]:
            paths[role].append(w['op_frame'][i])
    for role,frame in zip(w['rootroles'],w['root_frame']):
        paths[role].append(frame)
    h=Counter()
    for role in range(profile['R']):
        if role in removed:
            continue
        start = gauges[role]['frame'] if role in gauges else w['source_frame'][source_nodes[role]] if role in source_nodes else None
        dim = 0 if start is None else dims[start]
        visits = paths[role][:]
        if role in reuse:
            recipient = reuse[role]
            visits += [gauges[recipient]['frame']] + paths[recipient]
        visits += [w['full_frame']]
        for frame in visits:
            delta = dims[frame]-dim
            assert delta>=0,(role,dim,dims[frame])
            if delta:
                h[delta]+=1
            dim=dims[frame]
        if role in source_nodes:
            h[1]+=1
    helper_h = h.copy()
    # Declared profile components, separately identified from helper-path replay.
    h[22]+=24
    for key in ('source_data_histogram','target_data_histogram'):
        h.update(histogram(profile[key]))
    return h, dict(reused_pairs=len(reuse),logical_roles=profile['R'],
        physical_helpers_before_sinks=profile['R']-len(removed),
        helper_path_calls=sum(helper_h.values()),helper_path_rank_mass=mass(helper_h),
        calls=sum(h.values()),rank_mass=mass(h),histogram=dict(sorted(h.items())))

def moment(h,m,W,a,bad=True):
    low, high = ex.moment_interval(m,W,h,a)
    if bad:
        L,U=ex.log_interval(F(m))
        E,G=ex.exp_interval(a*L,a*U)
        weight=F(32*m*sum(h.values()),10**16*W)
        low += weight*E
        high += weight*G
    return low,high

def bracket(h,m,W,bad=True,scale=10**18):
    low,high=0,scale//100
    assert moment(h,m,W,F(low,scale),bad)[1]<1
    assert moment(h,m,W,F(high,scale),bad)[0]>1
    while high-low>1:
        mid=(low+high)//2
        a,b=moment(h,m,W,F(mid,scale),bad)
        if b<1:
            low=mid
        elif a>1:
            high=mid
        else:
            raise ArithmeticError('Insufficient moment enclosure precision')
    lo,hi=F(low,scale),F(high,scale)
    return dict(lower=lo,upper=hi,lower_moment=moment(h,m,W,lo,bad),upper_moment=moment(h,m,W,hi,bad))

def assembly(coarse,complex_coarse=None):
    b=complex_coarse if complex_coarse is not None else F(754736418878859,10**18)
    chain=[F(384599,10**10)]
    for _ in range(3):
        nxt=(1-coarse)*coarse+coarse*chain[-1]
        assert chain[-1]<nxt<coarse<1-nxt
        chain.append(nxt)
    a=chain[-1];h=F(1,10**12);beta=F(1,10**9)
    assert a<(1-beta)*b
    q=a*(1-2*h);minimum=(1-h)*q/(1+q);ticks=minimum*10**18
    k=F((ticks.numerator-1)//ticks.denominator,10**18)
    row_gap=F(10**6)-F(51*20161,25)
    direct=ae.direct_slacks(a,b,beta,h,k,1,row_gap)
    factored=ae.factored_slacks(a,b,beta,h,k,1,row_gap)
    assert direct['slacks']==factored and len(factored)==47
    assert all(direct['preconditions'].values()) and min(factored.values())>0
    next_point=ae.direct_slacks(a,b,beta,h,k+F(1,10**18),1,row_gap)
    rejected=[name for name,value in next_point['slacks'].items() if value<=0]
    assert rejected==['g3_above_kappa']
    return dict(bit_coarse=coarse,complex_coarse=b,bootstrap_chain=chain,
        backoff=h,beta=beta,strict_constraints=factored,margins=direct['margins'],
        kappa=k,kappa_decimal=ex.dec(k),minimum_margin=minimum,absorption_gap=minimum-k,
        adjacent_grid_rejected=rejected,strict_constraint_count=len(factored),
        scope='All 47 exact displayed inequalities, conditional on literal scalar guard=1, stated positive row gap, and complex coarse bound. This is not an all-size bridge certificate.')

def run():
    integrity=verify_sources();inv=inventory();h,profile=final_profile()
    W=F(inv['literal_stock'],60)
    assert 120*W-mass(h)==4400
    root=bracket(h,120,W)
    outer=assembly(root['lower'])
    assert outer['kappa']==F(read('expected/kernel-pins.json')['kappa'])
    return dict(status='PASS_INDEPENDENT_PR275_DECLARED_PROFILE_ARITHMETIC',
        physical_admission=False,all_size_theorem=False,integrity=integrity,
        inventory=inv,profile=profile,unreplicated_stock=W,deficit=4400,
        bit_root_bracket=root,assembly=outer)

if __name__ == '__main__':
    if not __debug__:raise RuntimeError('Assertions must remain enabled')
    report=run()
    (HERE/'baseline-receipt.json').write_text(json.dumps(ae.serial(report),indent=2)+'\n')
    print(json.dumps(ae.serial(dict(status=report['status'],kappa=report['assembly']['kappa'],
        kappa_decimal=report['assembly']['kappa_decimal'],
        bit_root_bracket=[report['bit_root_bracket'][key] for key in ('lower','upper')],
        bit_endpoint_residuals=[ex.dec(report['bit_root_bracket']['lower_moment'][1]-1),ex.dec(report['bit_root_bracket']['upper_moment'][0]-1)],
        physical_admission=False)),indent=2))

"""Independent arithmetic reconstruction of the immutable PR320 declarations.
Upstream programs are inert text, never imported or executed. Original code;
uses the explicitly verified, previously authored exact_intervals and assembly_arithmetic.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from collections import Counter, defaultdict
from decimal import Decimal, localcontext, ROUND_FLOOR
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path
import gzip, hashlib, json, os, sys
CODE=Path(__file__).resolve().parent
sys.path.insert(0,str(CODE.parent))
import support
HERE=support.out('arithmetic','placeholder').parent
SOURCE=support.INPUTS
AUTHORED=support.HERE.parent
HEAD=support.HEAD
for name,sha in {'exact_intervals.py':'c261dd44838d4e36c68768a1023ac859677089464ab121cdb46b30c918679333','assembly_arithmetic.py':'f2f6293c31deb579ebbea19eeaa732c07304ce9c2cacd431685e2dd18d4b0d58'}.items():
    if hashlib.sha256((AUTHORED/name).read_bytes()).hexdigest()!=sha:raise ValueError('Authored module pin mismatch: '+name)
sys.path.insert(0,str(AUTHORED))
import exact_intervals as ex
import assembly_arithmetic as ae
M,H,V,T=100,20,960,60
DEFICIT=2040
GRID=10**18
COMPLEX=F(772714351296671,GRID)
USED=set()

def clean(h):return {r:n for r,n in sorted(h.items()) if n}
def mass(h):return sum(r*n for r,n in h.items())
def hist(d):
    if any(type(n) is not int or str(int(r))!=str(r) for r,n in d.items()):raise ValueError('Integer histogram required')
    return Counter({int(r):n for r,n in d.items() if n and int(r)>0})
def decode(v):
    if isinstance(v,list) and len(v)==2 and v[0]=='Fraction':return F(v[1])
    if isinstance(v,list) and len(v)==2 and v[0]=='dict':return {k:decode(x) for k,x in v[1]}
    return v

def read(name):
    raw=support.read_bytes(name)
    USED.add(name)
    if name.endswith('.gz'):raw=gzip.decompress(raw)
    if name.endswith(('.json','.json.gz')):return json.loads(raw)
    return raw.decode()

@lru_cache(None)
def pins():return {k:decode(v) for k,v in read('word-pins.json').items()}

def base_profile():
    w=read('bitword/selected/bit/word_p10.json.gz')
    f=read('bitword/selected/bit/frames_p10.json.gz')
    p=read('bitword/selected/bit/profile_p10.json')
    dims={int(k):r['dim'] for k,r in f['frames'].items()}
    assert p['h']==f['h']==H and p['R']==9120 and p['v']==V
    gauges={r['role']:r for r in w['gauges']}
    assert all(r['dim']==dims[r['frame']] for r in gauges.values())
    source_nodes={role:int(node) for node,role in w['sources'].items()}
    reuse=dict(w['pairs']);removed=set(reuse.values())
    assert len(reuse)==len(removed)==890 and not set(reuse)&removed
    phase=set(w['phase1']);order=w['phase1']+[i for i in range(len(w['ops'])) if i not in phase]
    assert len(order)==len(set(order))==len(w['ops'])
    paths=defaultdict(list)
    for i in order:
        for role in w['ops'][i][:2]:paths[role].append(w['op_frame'][i])
    for role,frame in zip(w['rootroles'],w['root_frame']):paths[role].append(frame)
    helper=Counter()
    for role in range(p['R']):
        if role in removed:continue
        start=gauges[role]['frame'] if role in gauges else w['source_frame'][source_nodes[role]] if role in source_nodes else None
        previous=0 if start is None else dims[start]
        visits=list(paths[role])
        if role in reuse:
            recipient=reuse[role];visits+=[gauges[recipient]['frame']]+paths[recipient]
        for frame in visits+[w['full_frame']]:
            d=dims[frame]-previous
            assert d>=0,(role,previous,dims[frame])
            if d:helper[d]+=1
            previous=dims[frame]
        if role in source_nodes:helper[1]+=1
    before=helper.copy();helper[H-2]+=H
    # Reconstruct paid source and target dimension increments independently.
    # Zero-width visits carry no paid child and are discarded in both routes.
    g=read('bitword/selected/bit/graph_p10.json');chron=read('bitword/selected/bit/kchron_p10.json')
    source=Counter()
    for entry in chron['entries']:
        for key in ('carrier_chain','passive_chain'):
            for a,b in zip(entry[key],entry[key][1:]):
                delta=dims[b]-dims[a];assert delta>=0
                if delta:source[delta]+=1
    target_paths=[[] for _ in range(V)]
    for entry in sorted(w['gauges'],key=lambda row:(row['first'],row['role'])):
        for t in entry['targets']:target_paths[t].append(entry['frame'])
    deliveries=defaultdict(list)
    for entry in chron['entries']:deliveries[entry['deliver_after_root']].append(entry)
    for j,root in enumerate(g['roots']):
        if root['kind']=='side':
            for t in root['targets']:target_paths[t].append(w['root_frame'][j])
        for entry in deliveries[j]:
            for t in entry['receivers']:target_paths[t].append(entry['deliver_frame'])
    target=Counter()
    for path in target_paths:
        chain=[0]+[dims[f] for f in path]+[H-1]
        for a,b in zip(chain,chain[1:]):
            delta=b-a;assert delta>=0
            if delta:target[delta]+=1
    assert source==hist(p['source_data_histogram']) and target==hist(p['target_data_histogram'])
    assert mass(source)==mass(target)==V*(H-1)
    helper.update(source);helper.update(target)
    assert mass(helper)==pins()['local_paid_rank_mass']
    return helper,dict(helper_paths=clean(before),copied_centers={18:20},source_data=clean(hist(p['source_data_histogram'])),target_data=clean(hist(p['target_data_histogram'])),histogram=clean(helper),calls=sum(helper.values()),rank_mass=mass(helper),source_target_scope='Paid source increments reconstructed from kchron chains; target increments from ordered gauge/root/delivery visits and rank19 endpoints. Both agree with pinned component histograms. Frame dimensions and nominal event order are data, not a physical replay. Virtual profile child_histogram is not used.')

@lru_cache(None)
def kernel_first_dimensions():
    w=read('bitword/selected/bit/word_p10.json.gz');frames=read('bitword/selected/bit/frames_p10.json.gz')['frames']
    recipients={b for a,b in w['pairs']};roles=sorted(set(range(9120))-recipients);stream={1920+i:r for i,r in enumerate(roles)}
    phase=set(w['phase1']);order=w['phase1']+[i for i in range(len(w['ops']))if i not in phase];firstframes={}
    for i in order:
        for role in w['ops'][i][:2]:firstframes.setdefault(role,w['op_frame'][i])
    for role,frame in zip(w['rootroles'],w['root_frame']):firstframes.setdefault(role,frame)
    return {s:frames[str(firstframes[r])]['dim']for s,r in stream.items()}

def kernel_delta():
    k=read('kernel-selection.json');visits=defaultdict(set);first={};pivots={};donors=Counter()
    for row in k['pairs']+k['families']:
        pivot=row.get('pivot',row.get('a'));ds=row.get('donors',[row.get('b')]);pivots[pivot]=row['rank']
        dimensions=row.get('first_frame_dims')
        if dimensions is None:
            dimensions={str(s):kernel_first_dimensions()[s]for s in [pivot]+ds}
        dimensions={pivot:dimensions[0],ds[0]:dimensions[1]} if isinstance(dimensions,list) else {int(r):d for r,d in dimensions.items()}
        assert set(dimensions)=={pivot,*ds}
        for role,dimension in dimensions.items():
            assert role not in first or first[role]==dimension
            first[role]=dimension;visits[role].add(row['rank'])
        donors.update(ds)
    assert not set(pivots)&set(donors)
    delta=Counter()
    for role,ranks in visits.items():
        delta[first[role]]-=1;previous=pivots.get(role,0)
        for dimension in sorted(ranks)+[first[role]]:
            assert dimension>=previous
            if dimension>previous:delta[dimension-previous]+=1
            previous=dimension
    assert clean(delta)==dict(hist(k['expected_local_delta']))==pins()['kernel_local_delta']
    assert mass(delta)==-sum(pivots.values())==-1200
    return delta,dict(entries=len(pivots),pairs=len(k['pairs']),families=len(k['families']),entrance_rank=sum(pivots.values()),distinct_donors=len(donors),shared_donors=sum(n>1 for n in donors.values()),maximum_donor_multiplicity=max(donors.values()),delta=clean(delta))

def final_profile():
    helper,base=base_profile();kd,ki=kernel_delta()
    target=read('target-selection.json');td=Counter()
    for row in target['groups']:td.update(hist(row['local_histogram_delta']))
    assert clean(td)==dict(hist(target['expected_total_delta']))
    restoration=read('restore-selection.json');rd=Counter()
    for row in restoration['entries']:
        entrance,helper_rank,donor_rank,end=row['dims'];assert entrance<helper_rank<=end and donor_rank<=end
        rd[H-helper_rank]-=1;rd[H-donor_rank]-=1
        for width in (end-helper_rank,end-donor_rank,H-end):
            if width:rd[width]+=1
    assert clean(rd)==dict(hist(restoration['expected_local_delta']))==pins()['restore_local_delta']
    sink=read('sink-selection.json');sd=Counter()
    for row in sink['sinks']:
        rank=len(row['root_frame_basis']);sd[rank]-=1;sd[H-rank]-=1
    assert clean(sd)==dict(hist(sink['expected_local_delta']))==pins()['sink_local_delta']
    dd=hist(read('descent-selection.json')['expected_local_histogram_delta']);od=hist(read('reorder-selection.json')['expected_local_delta'])
    assert dict(dd)==pins()['descent_local_delta'] and dict(od)==pins()['reorder_local_delta']
    stages={}
    for name,delta in [('descent',dd),('target',td),('kernel',kd),('restore',rd),('sink',sd),('reorder',od)]:
        helper.update(delta);assert min(helper.values())>=0
        stages[name]=dict(delta=clean(delta),delta_calls=sum(delta.values()),delta_mass=mass(delta),calls=sum(helper.values()),rank_mass=mass(helper))
    priced=Counter({r:5*n for r,n in helper.items() if n});priced.update({r:2*V for r in (38,19,42,4)})
    assert sum(priced.values())==pins()['banked_calls']==250195
    assert mass(priced)==pins()['banked_rank_mass']==1095110
    raw=priced.copy();raw.update(pins()['removed_completion_histogram'])
    assert sum(raw.values())==pins()['reorder_five_stage_calls']==252512 and mass(raw)==pins()['final_five_stage_rank_mass']==1204260
    return priced,dict(base=base,kernel=ki,stages=stages,final_helper=clean(helper),final_helper_calls=sum(helper.values()),final_helper_rank_mass=mass(helper),banked_histogram=clean(priced),banked_calls=sum(priced.values()),banked_rank_mass=mass(priced),with_completions=clean(raw),declared_deltas=['descent-selection.json: expected_local_histogram_delta','reorder-selection.json: expected_local_delta'],scope='Independent helper/source/target dimension census plus frozen stage deltas; physical chronology, frame nesting, and scalar correctness are separate obligations.')

def inventory():
    w=read('bitword/selected/bit/word_p10.json.gz');k=read('kernel-selection.json');restore=read('restore-selection.json');sink=read('sink-selection.json')
    removed={b for a,b in w['pairs']};regs=sorted(set(range(9120))-removed);stream={2*V+i:r for i,r in enumerate(regs)}
    sinks={row['role'] for row in sink['sinks']};assert all(stream[row['stream']]==row['role'] for row in sink['sinks'])
    roles=set(regs)-sinks;entrance={r:0 for r in roles};end={r:H for r in roles}
    for row in w['gauges']:
        if row['role'] in roles:entrance[row['role']]=row['dim']
    for row in k['pairs']+k['families']:
        role=stream[row.get('pivot',row.get('a'))];assert entrance[role]==0;entrance[role]=row['rank']
    for row in restore['entries']:
        role=stream[row['helper']];assert entrance[role]==row['dims'][0] and end[role]==H;end[role]=row['rank']
    residual=Counter(end[r]-entrance[r] for r in roles);gauges=Counter(x for x in entrance.values() if x)
    completion=Counter(entrance[r]+H-end[r] for r in roles if entrance[r])
    for field,actual in [('residual_families',residual),('final_entrance_ranks',gauges),('completion_rank_histogram',completion)]:assert dict(actual)==pins()[field]
    patterns=pins()['bank_patterns'];used=Counter()
    for widths,count in patterns:
        assert sum(widths)==M and count>0
        for width in widths:used[width]+=count
    assert used==Counter({r:T*n for r,n in residual.items()})
    banks=sum(n for widths,n in patterns);stock=T*4*V+5*banks
    assert M*banks==T*mass(residual) and banks==pins()['banks_per_stage'] and stock==pins()['literal_stock']
    return dict(physical_R=len(roles),entrance_count=sum(gauges.values()),entrance_histogram=clean(gauges),completion_histogram=clean(completion),residual_census=clean(residual),residual_rank_mass=mass(residual),banks_per_stage=banks,literal_stock=stock,packing_patterns=patterns,packing_unused_coordinates=0,scope='Role inventory and exact width packing only, no chronological bank admission.')

def moment(histogram,m,W,a,bad=True):
    lo,hi=ex.moment_interval(m,W,histogram,a)
    if bad:
        l,u=ex.log_interval(F(m));e,f=ex.exp_interval(a*l,a*u)
        weight=F(32*m*sum(histogram.values()),10**16*W);lo+=weight*e;hi+=weight*f
    return lo,hi

def bracket(histogram,m,W,bad=True):
    # Decimal proposes endpoints only. Exact rational enclosures certify both signs.
    with localcontext() as ctx:
        ctx.prec=65
        terms=[(Decimal(r*n)/Decimal(m)/Decimal(W.numerator)*Decimal(W.denominator),(Decimal(m)/r).ln()) for r,n in histogram.items()]
        fall=Decimal(32*m*sum(histogram.values()))/10**16/Decimal(W.numerator)*Decimal(W.denominator) if bad else Decimal(0)
        logm=Decimal(m).ln();low=Decimal(0);high=Decimal('.01')
        for _ in range(170):
            a=(low+high)/2
            if sum(p*(a*l).exp() for p,l in terms)+fall*(a*logm).exp()<1:low=a
            else:high=a
        tick=int((low*GRID).to_integral_value(rounding=ROUND_FLOOR))
    low=F(tick,GRID);high=low+F(1,GRID)
    lm=moment(histogram,m,W,low,bad);hm=moment(histogram,m,W,high,bad)
    assert lm[1]<1<hm[0],('strict root signs failed',low,high)
    return dict(lower=low,upper=high,lower_moment=lm,upper_moment=hm,lower_residual_upper_decimal=ex.dec(lm[1]-1),upper_residual_lower_decimal=ex.dec(hm[0]-1))

def assembly(root):
    b=COMPLEX;eta=F(1,10**12);beta=F(1,10**9);grid=F(1,GRID);cap=(1-beta)*b
    s=min(root,F((cap-grid)*GRID//1,GRID));binding='bit' if s==root else 'complex'
    chain=[F(384599,10**10)]
    for _ in range(3):
        nxt=(1-s)*s+s*chain[-1];assert chain[-1]<nxt<s<1-nxt;chain.append(nxt)
    a=chain[-1];q=a*(1-2*eta);minimum=(1-eta)*q/(1+q);ticks=minimum*GRID;k=F((ticks.numerator-1)//ticks.denominator,GRID)
    rowgap=F(10**6)-F(51*20161,25)
    direct=ae.direct_slacks(a,b,beta,eta,k,1,rowgap);factored=ae.factored_slacks(a,b,beta,eta,k,1,rowgap)
    assert direct['slacks']==factored and len(factored)==47 and all(direct['preconditions'].values()) and min(factored.values())>0
    nxt=ae.direct_slacks(a,b,beta,eta,k+grid,1,rowgap);rejected=[n for n,v in nxt['slacks'].items() if v<=0];assert rejected==['g3_above_kappa']
    return dict(bit_root=root,bit_coarse=s,complex_coarse=b,complex_leaf_cap=cap,binding=binding,bootstrap_chain=chain,backoff=eta,beta=beta,strict_constraints=factored,margins=direct['margins'],kappa=k,kappa_decimal=ex.dec(k),minimum_margin=minimum,adjacent_grid_rejected=rejected,strict_constraint_count=47,scope='Exact displayed assembly conditional on the stated scalar guard, row gap and retained complex certificate.')

def complex_certificate():
    data=read('inputs/complex/gcert1-p11-cmod-centre-mw-flow.json.gz')
    assert (data['p'],data['h'],data['v'],data['R'])==(11,22,1320,9036)
    local=Counter()
    for component in data['blocks'].values():local.update(hist(component))
    ch=Counter({r:5*n for r,n in local.items()});ch.update({r:2640 for r in (42,21,46,4)})
    assert sum(ch.values())==351820 and mass(ch)==1571680
    m=110;W=F(14316);assert m*W-mass(ch)==3080
    root=bracket(ch,m,W);assert root['lower']==COMPLEX
    plain=bracket(ch,m,W,False);assert plain['lower']==F(772714354722691,GRID)
    return dict(m=m,W=W,histogram=clean(ch),calls=sum(ch.values()),rank_mass=mass(ch),deficit=3080,bad_envelope_root=root,without_bad_envelope_root=plain,scope='Histogram reconstructed from pinned declared gcert blocks, exact roots independently enclosed. Complex symbolic/physical correctness not re-proved.')

def run():
    for name in ['math_check.py','moment.py','outer.py','raw_ledger.py','bank_template.py','word_pins.py']:read(name)
    inv=inventory();histogram,profile=final_profile();complex_result=complex_certificate();W=F(inv['literal_stock'],T)
    assert M*W-mass(histogram)==DEFICIT
    root=bracket(histogram,M,W);outer=assembly(root['lower'])
    assert root['lower']==pins()['bit_root'] and outer['kappa']==pins()['kappa'] and outer['binding']==pins()['binding']
    return dict(status='PASS_INDEPENDENT_PR320_DECLARED_ARITHMETIC',head=HEAD,physical_admission=False,all_size_theorem=False,verified_input_files=sorted(USED),inventory=inv,profile=profile,complex_certificate=complex_result,unreplicated_stock=W,normalized_stock=inv['literal_stock']//5,normalization=12,deficit=DEFICIT,bit_root_bracket=root,assembly=outer)

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions must remain enabled')
    report=run();(HERE/'baseline-receipt.json').write_text(json.dumps(ae.serial(report),indent=2)+'\n')
    print(json.dumps(ae.serial({k:report[k] for k in ('status','head','physical_admission','all_size_theorem')}|{'root':report['bit_root_bracket'],'kappa':report['assembly']['kappa'],'inventory':report['inventory'],'helper_histogram':report['profile']['final_helper']}),indent=2))

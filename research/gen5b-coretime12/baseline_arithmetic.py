"""Independently authored replay of pinned PR299 declared profile data.

This recovers a declared cost profile; it is not a physical admission replay.
Prepared with substantial OpenAI assistance. Apache-2.0.
"""
from collections import Counter,defaultdict
from fractions import Fraction as F
import source_data as sd
import exact_intervals as ex
import assembly_arithmetic as ae
HEAD=sd.HEAD

def read(name):
    aliases={'target-selection-full.json':'target-selection.json',
             'target-selection-metadata.json':'target-selection.json',
             'descent-selection-metadata.json':'descent-selection.json'}
    return sd.read_json(aliases.get(name,name.replace('__','/').removesuffix('.base64')))

def source_integrity():
    return sd.verify_all()
def hist(x):return Counter({int(k):int(v)for k,v in x.items()if int(k)>0 and int(v)})


def rank(H):return sum(r*n for r,n in H.items())


def base_histogram():
    w=read('gen5bit__selected__bit__word_p12.json.gz.base64')
    fr=read('gen5bit__selected__bit__frames_p12.json.gz.base64')
    p=read('gen5bit__selected__bit__profile_p12.json')
    assert p['h']==fr['h']==24 and p['v']==1760 and p['R']==17160
    d={int(k):v['dim']for k,v in fr['frames'].items()}
    assert all(type(z)is int and 0<=z<=24 for z in d.values())
    gauge={z['role']:z for z in w['gauges']}
    assert all(d[z['frame']]==z['dim']for z in gauge.values())
    source={s:int(n)for n,s in w['sources'].items()}
    recipient={donor:borrower for donor,borrower in w['pairs']}
    removed=set(recipient.values())
    assert len(recipient)==len(removed)==1726
    assert not set(recipient)&removed
    assert all(s not in gauge and b in gauge for s,b in recipient.items())
    phase=set(w['phase1']);order=w['phase1']+[i for i in range(len(w['ops']))if i not in phase]
    assert len(order)==len(set(order))==len(w['ops'])
    seq=defaultdict(list)
    for i in order:
        for s in w['ops'][i][:2]:seq[s].append(w['op_frame'][i])
    for s,f in zip(w['rootroles'],w['root_frame']):seq[s].append(f)
    H=Counter()
    for s in range(p['R']):
        if s in removed:continue
        start=gauge[s]['frame']if s in gauge else w['source_frame'][source[s]]if s in source else None
        previous=0 if start is None else d[start]
        path=seq[s][:]
        if s in recipient:
            b=recipient[s];path+=[gauge[b]['frame']]+seq[b]
        path+=[w['full_frame']]
        for f in path:
            delta=d[f]-previous
            assert delta>=0,(s,previous,d[f])
            if delta:H[delta]+=1
            previous=d[f]
        if s in source:H[1]+=1
    # Center copies and the source/target path census are declared source data.
    H[22]+=24
    for key in ('source_data_histogram','target_data_histogram'):H.update(hist(p[key]))
    assert sum(H.values())==92937 and rank(H)==407228
    return H


def final_histogram():
    target=read('target-selection-full.json');total=Counter()
    for group in target['groups']:total.update(hist(group['local_histogram_delta']))
    assert len(target['groups'])==220 and {r:n for r,n in total.items()if n}==dict(hist(target['expected_total_delta']))
    p=read('expected__kernel-pins.json');H=base_histogram();stages={}
    deltas=[('descent',read('descent-selection-metadata.json')['expected_local_histogram_delta']),
            ('target',read('target-selection-metadata.json')['expected_total_delta']),
            ('kernel',p['kernel_local_delta']),('restore',p['restore_local_delta']),('sink',p['sink_local_delta'])]
    for label,D in deltas:
        D=hist(D);H.update(D);assert min(H.values())>=0
        stages[label]=dict(calls=sum(H.values()),rank_mass=rank(H),delta=dict(D))
    assert stages['descent']['rank_mass']==407228
    assert stages['kernel']['rank_mass']==p['kernel_helper_rank_mass']==405036
    assert stages['restore']['rank_mass']==404596
    assert stages['sink']['rank_mass']==404428
    idle={4:3520,23:3520,46:3520,50:3520}
    final=Counter({r:5*n for r,n in H.items()if n});final.update(idle)
    assert sum(final.values())==p['priced_five_stage_calls']==482635
    assert rank(final)==p['priced_five_stage_rank_mass']==2455100
    completion={5*r:n for r,n in hist(p['completion_rank_histogram']).items()}
    before=final.copy();before.update(completion)
    assert sum(before.values())==p['sink_five_stage_calls']==486589
    assert rank(before)==p['final_five_stage_rank_mass']==2691640
    return final,stages


def moment(H,m,W,a,bad=True):
    lo,hi=ex.moment_interval(m,W,H,a)
    if bad:
        L,U=ex.log_interval(F(m));E,G=ex.exp_interval(a*L,a*U)
        factor=F(32*m*sum(H.values()),10**16*W)
        lo+=factor*E;hi+=factor*G
    return lo,hi


def assembly(c,b,k):
    chain=[F(384599,10**10)]
    for i in range(3):
        z=(1-c)*c+c*chain[-1]
        assert chain[-1]<z<c<1-z
        chain.append(z)
    a=chain[-1];eta=F(1,10**12);beta=F(1,10**9)
    row_gap=F(10**6)-F(51*20161,25)
    z=ae.direct_slacks(a,b,beta,eta,k,1,row_gap)
    f=ae.factored_slacks(a,b,beta,eta,k,1,row_gap)
    assert z['slacks']==f and len(f)==47 and min(f.values())>0
    assert len(z['margins'])==7
    znext=ae.direct_slacks(a,b,beta,eta,k+F(1,10**18),1,row_gap)
    failed=[n for n,v in znext['slacks'].items()if v<=0]
    assert failed==['g3_above_kappa']
    q=a*(1-2*eta);G=(1-eta)*q/(1+q)
    assert k<G<=k+F(1,10**18)
    return dict(coarse=c,complex_coarse=b,bootstrap_chain=chain,strict_constraints=f,
       margins=z['margins'],kappa=k,kappa_decimal=ex.dec(k),minimum_margin=G,
       absorption_gap=G-k,adjacent_grid_rejected=failed,
       bridge_scope='The positive literal gap and supplied row gap are assumptions in this arithmetic check.')


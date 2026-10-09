#!/usr/bin/env python3
"""Independent signed-gauge profiles, stopped recurrence, three reserves and 47 slacks.

Uses a separate 40-term log / degree-ten exponential enclosure and the
previously independent balanced assembly transcription. That transcription
is bound to an explicit three-factor bridge validator using an isolated
function namespace; the original module and sources are never modified.
"""
import sys
if not __debug__:raise RuntimeError('Assertions required')
sys.dont_write_bytecode=True
import argparse,hashlib,importlib.util,json,types
from fractions import Fraction as Q
from collections import Counter
from functools import lru_cache
from math import comb
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
ARCHIVE=ROOT/'references/stopped-recursion/pr107'
spec=importlib.util.spec_from_file_location('signed_gauge_independent_math',ROOT/'research/deferred-span-frames/independent_check.py')
audit=importlib.util.module_from_spec(spec);sys.modules[spec.name]=audit;spec.loader.exec_module(audit)
GRID=10**18;SCALE=10**40
def read(path):return json.loads(path.read_text())
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def js(v):
    if isinstance(v,Q):return str(v)
    if isinstance(v,dict):return {str(k):js(x)for k,x in v.items()}
    if isinstance(v,(tuple,list)):return [js(x)for x in v]
    return v
def input_hash(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def floorq(x):return Q(x.numerator*SCALE//x.denominator,SCALE)
def ceilq(x):return -floorq(-x)
@lru_cache(None)
def logarithm(x):
    lo,hi=audit.logarithm(x);return floorq(lo),ceilq(hi)
def moment(p,a):
    lo=hi=Q()
    for t,n in p['child_multiplicities'].items():
        l,u=logarithm(Q(p['m'],t));weight=Q(t*n,p['m']*p['W'])
        lo+=weight*floorq(audit.exponential(a*l)[0]);hi+=weight*ceilq(audit.exponential(a*u)[1])
    return lo,hi

def profile(record):
    h,R=record['h'],record['R'];v=comb(h,3);assert v==record['v']
    H=Counter({r:n for r,n in enumerate(record['histogram'])if r and n})
    loss=h*(h-1);assert record['loss']==loss and sum(r*n for r,n in H.items())==h*R+2*loss
    H[h]-=h;H[1]+=h;assert H[h]>=0
    m=h*h;N=v*v;bank=v*R;W=2*N+2*bank
    rows=Counter({m-h:2*bank,(h-1)**2:2*N,h-1:4*N,1:N})
    rows.update({r:2*v*n for r,n in H.items()if n})
    assert all(0<r<m and n>0 for r,n in rows.items())
    rank=sum(r*n for r,n in rows.items());assert rank==m*W-N+2*v*loss
    corrected=list(record['histogram']);corrected[h]-=h;corrected[1]+=h
    return dict(dimensions=[h,h],m=m,N=N,B1=bank,B2=bank,W=W,L=2*v*loss,total_rank=rank,
                deficit=N-2*v*loss,maxchild=max(rows),copied_histogram=corrected,child_multiplicities=dict(rows))

def rebuild(work=None):
    base=work or HERE
    inputs=dict(bit=read(base/'bit-axis.json'),bit_audit=read(base/'bit-audit.json'))
    if work:inputs.update({key:read(base/name)for key,name in [('complex_word','complex-word.json'),('complex_screen','complex-screen.json'),('complex_charge','complex-charge.json')]})
    else:
        aggregate=read(base/'complex-axis.json')
        inputs.update(complex_word=aggregate['word'],complex_screen=aggregate['screen'],complex_charge=aggregate['charge'])
    bitdata=inputs['bit'];ba=inputs['bit_audit'];bit=profile(bitdata)
    assert bit['copied_histogram']==ba['copied_rank_histogram']
    assert bitdata['source_word_sha256']==ba['source_word_sha256']
    assert sum(r*n for r,n in enumerate(bit['copied_histogram']))==ba['rank_mass']
    for key in ('nonidentity_label_events_match_actual_word','full_inherited_dirty_replay_equal','all_frame_gram_inverses_exact','all_side_hyperplane_inclusions_exact'):assert ba[key]is True
    counted=Counter()
    for component in ba['paid_components'].values():
        for rank,n in component.items():assert type(n)is int and n>=0;counted[int(rank)]+=n
    assert [counted[r]for r in range(bitdata['h']+1)]==bit['copied_histogram']
    word,screen=inputs['complex_word'],inputs['complex_screen']
    h,v,R=word['h'],word['v'],word['R'];assert(h,v)==(24,comb(24,3))
    assert word['status']=='EXACT_LOCAL_SCHEDULE_PASS'
    for key in ('all_data_readout_chains_verified','all_gates_equal_frame','all_moves_nested_and_nondegenerate',
        'all_reordered_precedence_edges_verified','all_sigma_signed_target_caps_verified','center_phase_untouched_verified',
        'reflected_opposite_signed_schedule_verified','reflected_rank_histogram_identical'):assert word[key]is True
    assert word['word_sha256']==screen['word_sha256']
    sigma={int(r):n for r,n in screen['sigma_dimensions'].items()}
    assert all(0<r<=h and type(n)is int and n>0 for r,n in sigma.items())
    nr=sum(sigma.values());rs=sum(r*n for r,n in sigma.items())
    assert nr==word['selected_gauges']==screen['selected_positive_roles']
    assert rs==word['sigma_rank_sum']==screen['sum_sigma_dimensions']
    H={name:{int(r):n for r,n in rows.items()}for name,rows in word['local_histograms'].items()}
    assert set(H)=={'aux','data','center'}
    for name,mass,field in [('aux',h*R-rs,'auxiliary_internal_rank_mass'),('data',2*v*(h-1),'local_data_rank_mass'),('center',h*(h-1),'center_copy_rank_mass')]:
        assert all(type(n)is int and n>=0 and 0<=r<=h for r,n in H[name].items())
        assert sum(r*n for r,n in H[name].items())==mass==word[field]
    m=h*h;N=v*v;W=2*v*(v+R);loss=2*v*h*(h-1)
    rows=Counter()
    for entries in H.values():
        for r,n in entries.items():
            if r and n:rows[r]+=2*v*n
    for rank in range(h+1):
        number=R-nr if rank==0 else sigma.get(rank,0)
        if number:rows[m-h+rank]+=2*v*number
    rows[1]+=N;rows[(h-1)**2]+=2*N
    assert all(0<r<m and n>0 for r,n in rows.items())
    assert dict(rows)=={int(r):n for r,n in word['full_paid_histogram'].items()if n}
    assert dict(rows)=={int(r):n for r,n in screen['histogram'].items()if n}
    rank=sum(r*n for r,n in rows.items());assert rank==W*m-N+loss==screen['rank_mass']
    assert (m,W,max(rows))==(screen['m'],screen['W'],word['maxchild'])
    cx=dict(dimensions=[h,h],m=m,N=N,B1=v*R,B2=v*R,W=W,L=loss,total_rank=rank,deficit=N-loss,
        maxchild=max(rows),local_histograms=H,sigma_dimensions=sigma,child_multiplicities=dict(rows))
    return dict(bit=bit,complex=cx),inputs

def depth(m,r):
    k=1
    while m**k<=2*r**k:k+=1
    return k

def bridge_check(given,profiles,inputs):
    old=read(ARCHIVE/'certificates/copied-centers-network.json')['finite_bridge']['bit']
    expected={}
    for name,p in [('bit_coarse',profiles['bit']),('complex',profiles['complex'])]:
        expected[name]=dict(m=p['m'],W=p['W'],maxchild=max(p['child_multiplicities']),halving_degree=depth(p['m'],p['maxchild']),wire_bits=p['W'].bit_length())
    word,charge=inputs['complex_word'],inputs['complex_charge'];cx=profiles['complex']
    h,v,R=word['h'],word['v'],word['R'];assert(h,v,R)==tuple(charge[k]for k in ('h','v','R'))
    assert charge['status']=='EXACT_COUNT_AND_CONSERVATIVE_BOUND'and charge['word_sha256']==word['word_sha256']
    assert charge['forward_events']==word['forward_events']
    assert charge['deferred_readout_nonzero_coefficients']==word['actual_deferred_signed_adds']
    assert charge['full_readout_nonzero_coefficients']==charge['early_readout_nonzero_coefficients']+charge['deferred_readout_nonzero_coefficients']
    assert charge['expanded_center_terms']==h*v and charge['coefficient_denominator']==42
    assert 0<charge['coefficient_absolute_numerator_bound']<2**16 and charge['coefficient_binary_height_charge']==64
    local=word['forward_events']+charge['early_readout_nonzero_coefficients']+2*h*v+8*h+8
    g=local*64;G=cx['N']+2*v*(g+2*h)
    assert (local,g,G)==tuple(charge[k]for k in ('conservative_local_groups','local_scalar_charge','G0'))
    inventory=dict(h=h,v=v,forward_events=word['forward_events'],early_readout_nonzero_coefficients=charge['early_readout_nonzero_coefficients'],
        deferred_readout_nonzero_coefficients=charge['deferred_readout_nonzero_coefficients'],coefficient_absolute_numerator_bound=charge['coefficient_absolute_numerator_bound'],
        coefficient_denominator=42,coefficient_binary_height_charge=64,conservative_local_groups=local,local_scalar_charge=g)
    expected['complex'].update(s=cx['total_rank'],scalar_inventory=inventory,scalar_group_upper=G)
    m,W,s,r=(cx[k]for k in ('m','W','total_rank','maxchild'));E=64*(W+m+G+1)**3;B=s+E
    literal=2*G*W*W+8*s+4*W+4+32*m
    semantic=dict(E=E,literal_charge=literal,strict_literal_gap=E-literal,B=B,C0=32*m*B*B,C1=1,
        induction_gap=2*B*(m-r)-s-E,fixed_odd_divisor=21,
        exact_grid='One common dyadic grid times 21^K, K=G0*(D_complex+1); no child rounding')
    assert E>literal and semantic['induction_gap']>=0 and semantic['C0']>2*B+18
    old_degree=depth(old['m'],old['maxchild'])*old['W'].bit_length();assert old_degree==252
    expected['ordinary_leaf_row_degree']=old_degree
    coefficient=old_degree+sum(expected[k]['halving_degree']*expected[k]['wire_bits']for k in ('complex','bit_coarse'))
    assert coefficient==3528 and expected['complex']['halving_degree']==100 and expected['bit_coarse']['halving_degree']==17
    stock=dict(coefficient=coefficient,degree=10000,suffix_slope=40000,degree_gap=Q(10000)-Q(51,25)*coefficient,
        contract='W_complex^D_complex * W_coarse^D_coarse * W_old^D_old; one preceding prefix and one padding; sequential reuse')
    assert stock['degree_gap']==Q(70072,25)>0
    expected.update(semantic=semantic,rows=stock)
    assert given==js(expected),'Independent three-factor bridge reconstruction differs'
    return semantic,stock

def validate(certificate,profiles,inputs):
    assert certificate['input_sha256']=={name:input_hash(value)for name,value in inputs.items()}
    assert certificate['coarse_bit']['profile']==js(profiles['bit'])and certificate['complex']['profile']==js(profiles['complex'])
    old=read(ARCHIVE/'certificates/copied-centers-network.json');ordinary=certificate['ordinary_bit']
    atom=Q(ordinary['atom_exponent']);coarse=Q(ordinary['coarse_saving']);leaf=Q(ordinary['leaf_saving'])
    assert atom==Q(1,1000)and leaf==Q(old['bit']['saving'])==Q(384599,10**10)
    actual=(1-atom)*coarse+atom*leaf
    assert Q(ordinary['saving'])==actual and Q(ordinary['adapter_gap'])==atom-actual>0
    assert 0<leaf<coarse<atom<1 and ordinary['ordinary_leaf_bridge']==old['finite_bridge']['bit']
    assert profiles['bit']['total_rank']<profiles['bit']['m']*profiles['bit']['W']
    moments={}
    for label,section,p,a in [('coarse_bit',certificate['coarse_bit'],profiles['bit'],coarse),('complex',certificate['complex'],profiles['complex'],Q(certificate['complex']['saving']))]:
        assert Q(section['saving'])==a
        lo,hi=moment(p,a);primary=section['moment']
        assert Q(primary['saving'])==a and Q(primary['lower'])<=lo<=hi<=Q(primary['upper'])<1
        assert Q(primary['strict_gap'])==1-Q(primary['upper'])
        assert set(primary['terms'])==set(map(str,p['child_multiplicities']))
        for r,n in p['child_multiplicities'].items():assert Q(primary['terms'][str(r)]['weight'])==Q(r*n,p['m']*p['W'])
        moments[label]=dict(lower=lo,upper=hi,strict_gap=1-hi)
        next_a=a+Q(1,GRID);assert Q(section['next_saving'])==next_a
        nlo,nhi=moment(p,next_a);next_primary=section['next_moment']
        assert Q(next_primary['saving'])==next_a and 1<Q(next_primary['lower'])<=nlo<=nhi<=Q(next_primary['upper'])
        moments['next_'+label]=dict(lower=nlo,upper=nhi)
    b=Q(certificate['complex']['saving']);beta=Q(certificate['beta']);h=Q(certificate['h']);a=Q(certificate['bit_saving'])
    assert beta==Q(1,10**12)and h==Q(1,GRID)and a==min(actual,(1-beta)*b-h)
    assert Q(certificate['assembly']['parameters']['a_complex'])==b
    assert Q(certificate['assembly']['parameters']['beta'])==beta
    globals_={**audit.independent_assembly.__globals__,'check_bridge':lambda f:bridge_check(f,profiles,inputs)}
    independent_assembly=types.FunctionType(audit.independent_assembly.__code__,globals_)
    margin,slacks,margins=independent_assembly(certificate)
    assert Q(certificate['kappa'])<margin<=Q(certificate['kappa'])+Q(1,GRID)
    assert certificate['next_kappa_grid_rejected']
    assert Q(certificate['previous_pairtree_kappa'])==Q(7808981744031,10**17)
    assert Q(certificate['improvement_over_pairtree'])==Q(certificate['kappa'])-Q(certificate['previous_pairtree_kappa'])>0
    return dict(moments=moments,minimum_margin=margin,strict_constraints=len(slacks),cost_margins=len(margins),
        rank_totals={name:p['total_rank']for name,p in profiles.items()},row_factor_count=3,complete_local_endpoint_ledger=True)

def sources():
    manifest=read(ARCHIVE/'ARCHIVE.json')
    for path,expected in manifest['files'].items():
        blob=(ARCHIVE/path).read_bytes();assert hashlib.sha256(blob).hexdigest()==expected
        assert hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()==manifest['git_blobs'][path]
    original=read(ARCHIVE/'research/reversed-rational-centers/SOURCE.json')
    for path,expected in original['files'].items():assert digest(ARCHIVE/path)==expected
    files=[Path(__file__),HERE/'compose.py',HERE/'test_controls.py',ARCHIVE/'ARCHIVE.json',ROOT/'research/deferred-span-frames/independent_check.py']
    primary=ROOT/'references/signed-recursion/pr100/research/deferred-balanced'
    files += [primary/'moments.py']+list((primary/'arithmetic-sources').glob('*.py'))
    return dict(preserved_archive_files=len(manifest['files']),original_pr107_source_pins=len(original['files']),
                files={str(path.relative_to(ROOT)):digest(path)for path in files})

def generate(path,work=None):
    certificate=read(path);profiles,inputs=rebuild(work);result=validate(certificate,profiles,inputs)
    import test_controls
    negatives=test_controls.run(certificate,lambda c:validate(c,profiles,inputs))
    return dict(status='PASS',scope='Independent complete per-class/exterior/correction child lists, sharp coarse and complex moments, stopped recurrence, fresh scalar/precision induction, three reserves and balanced 47/7 arithmetic. Physical proofs/replay and analytic hypotheses remain separate.',
                certificate_sha256=digest(path),kappa=certificate['kappa'],complex_saving=certificate['complex']['saving'],
                **result,negative_controls=negatives,source_closure=sources())

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--certificate',type=Path,default=HERE/'certificate.json');parser.add_argument('--record',action='store_true');parser.add_argument('--work',type=Path);args=parser.parse_args()
    result=js(generate(args.certificate,args.work));path=HERE/'independent-audit.json'
    if args.record:path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:assert result==read(path),'Independent signed-gauge receipt changed'
    print('PASS independent stopped signed-gauges: complete profiles, 3 reserves, 47 inequalities, 7 margins,',len(result['negative_controls']),'negative controls')
if __name__=='__main__':main()

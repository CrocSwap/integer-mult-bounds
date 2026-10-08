#!/usr/bin/env python3
"""Original exact arithmetic audit for a conditional two-stage balanced transfer.
Standard library only. Never imports or runs any downloaded implementation.
Rational checks certify arithmetic; producer, geometry and tape theorems are hypotheses.
"""
from collections import Counter
from fractions import Fraction as F
from math import comb
from pathlib import Path
import argparse
import hashlib
import json

HERE = Path(__file__).resolve().parent
P = HERE / 'verified_inputs/research/two-stage-dimensions'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, default=HERE/'CHECKS.json')
args = parser.parse_args()

class ForeignDecimal(str):
    pass

def exact_json(path, discard_diagnostic=False):
    data=json.loads(path.read_text(), parse_float=ForeignDecimal,
                    parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    if discard_diagnostic:
        assert isinstance(data['bit'].pop('numeric_root'), ForeignDecimal)
    def validate(x):
        assert not isinstance(x, (float, ForeignDecimal)), 'nonexact consumed input'
        if isinstance(x, dict):
            for value in x.values():validate(value)
        elif isinstance(x, list):
            for value in x:validate(value)
    validate(data)
    return data

def encode(value):
    assert not isinstance(value,float)
    if isinstance(value,F):return str(value)
    if isinstance(value,dict):return {str(k):encode(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)):return [encode(v) for v in value]
    return value

def ceil(x):return -(-x.numerator//x.denominator)
def floor(x):return x.numerator//x.denominator

manifest=exact_json(HERE/'VERIFIED_INPUT_MANIFEST.json')
for entry in manifest:
    raw=(HERE/'verified_inputs'/entry['path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==entry['sha256']
    assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==entry['git_blob']
complex_path=HERE.parent/'semantic_pr28/inputs/research/translated-partial/complex-certificate.json'
assert hashlib.sha256(complex_path.read_bytes()).hexdigest()=='399f102e9bab4d098604971c22d1ec39a787ca39dce84c455791d857e97739f0'
base=exact_json(P/'certificate-47-45.json',True)
upstream=exact_json(P/'corners/certificate-corners-47-45.json')
complex_data=exact_json(complex_path)

# Construct the whole list from local rank records, not the advertised list.
records={h:exact_json(P/f'producer-{h}.json')['matched'] for h in (45,47)}
m=45*47;N=comb(45,3)*comb(47,3)
base_hist=Counter();banks={};loss=0
for h,rec in records.items():
    assert rec['h']==h and rec['v']==comb(h,3)
    assert rec['R']==rec['c']+rec['q']-rec['matched']
    assert rec['loss']==h*(h-1)
    assert len(rec['histogram'])==h+1
    mass=sum(rank*count for rank,count in enumerate(rec['histogram']))
    assert mass==rec['rank_sum']==h*rec['R']+2*rec['loss']
    opposite=N//rec['v'];banks[h]=opposite*rec['R'];loss+=opposite*rec['loss']
    base_hist[h]+=banks[h];base_hist[m-2*h]+=banks[h] # each exterior bank once
    base_hist[1]+=2*N;base_hist[h-2]+=2*N # physical growth
    for rank,count in enumerate(rec['histogram']):
        assert type(count) is int and count>=0
        copies=opposite*count
        if rank==h:base_hist[h]+=copies
        elif rank*2>h:
            base_hist[1]+=(h-rank)*copies;base_hist[2*rank-h]+=copies
        else:base_hist[1]+=rank*copies
base_hist[1]+=91*2*N # old data nullity pivots
base_hist[1933]+=2*N
base_hist[1]+=N # paid endpoint copy correction, never free
base_hist=Counter({k:v for k,v in base_hist.items() if v})
W=2*N+sum(banks.values());s=W*m-N+2*loss
assert (m,N,W,s,loss)==(2115,230090850,11710626180,24767869848810,62784480)
assert dict(base_hist)=={int(k):v for k,v in base['bit']['rows'].items()}
assert sum(t*n for t,n in base_hist.items())==s
assert W*m-s==104521890

# Both new partitions have the same rank and all-role volume.
def replace_data(singletons,blocks):
    assert singletons+sum(blocks)==91 and min(blocks)>0
    row=base_hist.copy();row[1]-=sum(blocks)*2*N
    for t in blocks:row[t]+=2*N
    assert sum(t*n for t,n in row.items())==s
    assert row[1]>=N and max(row)==2025
    return row
standard=replace_data(11,[43,37])
reverse=replace_data(9,[43,39])
assert dict(standard)=={int(k):v for k,v in upstream['rows'].items()}
assert reverse-standard==Counter({39:2*N}) # Counter subtraction discards negatives
assert standard-reverse==Counter({1:4*N,37:2*N})

# atanh series: all terms positive; tail bounded by one geometric sum.
def log_interval(value, places=12):
    assert value>=1 and isinstance(value,F)
    power=0
    while value>2:value/=2;power+=1
    def reduced(y):
        z=(y-1)/(y+1);term=z;total=F()
        for j in range(24):
            total+=2*term/(2*j+1);term*=z*z
        return total,total+2*term/(49*(1-z*z))
    low,high=reduced(value);lo2,hi2=reduced(F(2));scale=10**places
    return F(floor((low+power*lo2)*scale),scale),F(ceil((high+power*hi2)*scale),scale)

class Moment:
    def __init__(self,row,arity,roles):
        self.terms=[(t,F(t*n,arity*roles),log_interval(F(arity,t))) for t,n in sorted(row.items())]
        assert all(0<t<arity and w>0 for t,w,_ in self.terms)
    def upper(self,a,geometric=False):
        total=F()
        for _,weight,(_,ell) in self.terms:
            u=a*ell;assert 0<=u<1
            total+=weight*(1/(1-u) if geometric else 1+u+u*u/(2*(1-u/3)))
        return total
    def lower(self,a):
        total=F()
        for _,weight,(ell,_) in self.terms:
            u=a*ell;assert u>=0
            total+=weight*(1+u+u*u/2+u**3/6)
        return total
    def search(self,denominator=10**14):
        lo=0;hi=denominator//10000
        assert self.upper(F(lo,denominator))<1<=self.lower(F(hi,denominator))
        while hi-lo>1:
            mid=(lo+hi)//2
            if self.upper(F(mid,denominator))<1:lo=mid
            else:hi=mid
        a=F(lo,denominator);following=F(hi,denominator)
        return dict(a=a,moment_upper=self.upper(a),strict_gap=1-self.upper(a),
                    next_grid=following,next_upper=self.upper(following),next_lower=self.lower(following))

moments={name:Moment(rows,m,W) for name,rows in [('original91',base_hist),('standard',standard),('reversed',reverse)]}
assert moments['original91'].upper(F(base['bit']['saving']))==F(base['bit']['moment_upper'])<1
assert moments['standard'].upper(F(upstream['bit']['saving']))==F(upstream['bit']['moment_upper'])<1
bit_results={name:moment.search() for name,moment in moments.items()}
assert bit_results['standard']['a']==F(1638156876,10**14)
assert bit_results['reversed']['a']>bit_results['standard']['a']
for value in bit_results.values():assert value['strict_gap']>0 and value['next_lower']>1

# Same physical phase graph; all Gaussian scalar constants are graph-derived.
mc,Wc,sc=(complex_data[k] for k in ('m','W','s'));b=F(complex_data['a_c'])
phase_hist={int(k):v for k,v in complex_data['child_counts'].items()}
assert (mc,Wc,sc,b)==(21952,2085111546336,45772350635112192,F(18,10**6))
assert sum(t*n for t,n in phase_hist.items())==sc
phase_moment=Moment(phase_hist,mc,Wc).upper(b,True);assert phase_moment<1
Gscalar=3*comb(28,3)**2*(4*64298+4*comb(28,3)+4)
assert Gscalar==8702721518400
E=64*(Wc+mc+1)**3;B=sc+E
literal=2*Gscalar*Wc**2+8*sc+4*Wc+4+32*mc
assert E>literal
C0=32*mc*B**2;rc=max(phase_hist)
assert 2*B*(mc-rc)>=sc+E and C0>2*B+18

def depth(arity,child):
    k=1
    while arity**k<=2*child**k:k+=1
    assert arity**(k-1)<=2*child**(k-1)
    return k
hb,hc=depth(m,max(reverse)),depth(mc,rc)
wb,wc=W.bit_length(),Wc.bit_length()
assert (hb,hc,wb,wc)==(16,544,34,41)
coefficient=hb*wb+hc*wc;degree=47000
row_gap=degree-F(51,25)*coefficient
assert coefficient==22848 and row_gap==F(9752,25)>0
assert depth(m,max(standard))==depth(m,max(base_hist))==hb

# Balanced transfer is the accepted generic theorem, with new actual graph inputs.
def assembly(a):
    h=F(1,10**12);beta=F(1,20)
    q=a*(1-2*h);c=q+h/4;eps=(1-h)/(1+q)
    tau,sigma=1-a,1-b;lp=1-q;lam=(tau+lp)/2
    gain=eps*q;r=(gain+1-eps)/2;delta=h/8
    kappa=F(floor(gain*10**14),10**14)
    internal=tau+(1-beta)*max(sigma-tau,F())
    leaf=sigma+beta*(1-sigma)
    margins=[1-eps,a,gain,a,min(1-eps-delta,r-delta),1-eps-delta,eps]
    conditions=dict(a_positive=a,complex_above_bit=b-a,complex_small=F(1,32)-b,
      beta_positive=beta,beta_small=1-beta,leaf_above_bit=(1-beta)*b-a,
      q_positive=q,q_below_internal=1-internal-q,q_below_leaf=1-leaf-q,
      c_positive=c,c_small=1-c,c_above_q=c-q,lambda_above_tau=lam-tau,
      lambda_above_sigma=lam-sigma,lambda_above_internal=lam-internal,
      lambda_prime_above_lambda=lp-lam,lambda_prime_below_one=q,
      compact_leaf=lp-leaf,compact_reservations=lp-(1-c),epsilon_positive=eps,
      epsilon_below_one=1-eps,semantic_guard=1-eps,compact_geometry=1-eps*(1+c),
      compact_dominates_log=eps*c,record_suffix=1-eps,phase_local=1-eps-delta,
      phase_boundary=r-delta,normalization=1-eps-r,phase_cell=eps-(1-r)/2,
      prime_packing=1-eps,alpha_positive=r,alpha_small=1-r,alpha_quarter=F(1,4)-r,
      delta_positive=delta,delta_small=F(1,8)-delta,short_record_fallback=eps-a,
      small_field_exposure=1-eps-gain,artificial_boundary=8-eps+r-delta-gain,
      literal_scalar_guard=F(E-literal),row_product_stock=row_gap)
    conditions.update({f'margin{i+1}_above_kappa':v-kappa for i,v in enumerate(margins)})
    assert len(conditions)==47
    assert all(v>0 for v in conditions.values()), {k:v for k,v in conditions.items() if v<=0}
    assert min(margins)==gain
    assert 1-eps-gain==h and 1-eps-r==h/2
    assert 1-eps*(1+c)==h-eps*h/4
    ka,km,kb,ks=(ceil(1/x) for x in (r,eps*c,1-eps,eps*beta))
    cutoffs=dict(guard=ceil(F((2*C0).bit_length())/(1-eps)),normalization=ceil(7/(1-eps-r)),
      alpha=16*ka*ka+1,compact=64*km*km+1,geometry=ceil(3/(1-eps*(1+c))),
      phase_cell=ceil(9/(eps-(1-r)/2)),period=128*kb*kb+1,
      stopped_leaf=ks*(4*max(m,mc)).bit_length(),log_p=25,reservoir=14)
    common=max(cutoffs.values());checkpoints=[]
    for j in range(6):
        z=common*2**j
        powers={'alpha':(z//ka,8*(z+ka)+64),'compact':(z//km,32*(z+km)+192),
                'period':(z//kb,16*(z+kb)+56),'rows':(z//kb,4*degree*(z+kb+8)),
                'leaf':(z//ks,4*max(m,mc))}
        assert all(lhs>=rhs.bit_length() for lhs,rhs in powers.values())
        checkpoints.append(dict(log2_input=z,powers={k:dict(exponent=v[0],rhs=v[1],rhs_bits=v[1].bit_length()) for k,v in powers.items()}))
    assert common>=max(2*ka,2*km,2*kb,25)
    negatives=dict(original_prefix_charge_fails=1-eps*(1+c)<kappa,
      old_guard_fails=1-eps*F(19991,10000)<0,
      old_separate_exposure_fails=a*(1-eps)<kappa,
      beta_one_tenth_fails=F(9,10)*b<a,
      next_kappa_grid_fails=kappa+F(1,10**14)>gain)
    assert all(negatives.values())
    return dict(parameters=dict(a=a,b=b,beta=beta,h=h,q=q,c=c,epsilon=eps,
      lambda_=lam,lambda_prime=lp,r=r,delta=delta,kappa=kappa),conditions=conditions,
      margins=margins,minimum=gain,absorption_gap=gain-kappa,scoped_limit=a/(1+a),
      cutoff_log2_input=cutoffs,common_cutoff=common,power_checkpoints=checkpoints,
      recurrence=dict(internal=internal,leaf=leaf,reservations=1-c),negative_controls=negatives)

assemblies={name:assembly(value['a']) for name,value in bit_results.items() if name!='original91'}
# An exact lower enclosure, not an upper-bound failure, separates the topologies.
assert moments['standard'].lower(bit_results['reversed']['a'])>1
assert moments['original91'].lower(bit_results['standard']['a'])>1
assert assemblies['reversed']['parameters']['kappa']>assemblies['standard']['parameters']['kappa']>F(1638103206,10**14)

result=dict(status='AUTHOR CONDITIONAL GENERIC BALANCED COMPOSITION; REVERSED GEOMETRY REQUIRES SEPARATE REVIEW',
  sources=manifest,complex_source_sha256=hashlib.sha256(complex_path.read_bytes()).hexdigest(),
  counts=dict(m=m,N=N,W=W,s=s,loss=loss,banks=banks,deficit=W*m-s,copy_corrections=N),
  profiles=dict(original91=dict(singletons=91,blocks=[1933]),standard=dict(singletons=11,blocks=[43,37,1933]),reversed=dict(singletons=9,blocks=[43,39,1933]),copies=2*N),
  histograms=dict(original91=sorted(base_hist.items()),standard=sorted(standard.items()),reversed=sorted(reverse.items())),
  moments=bit_results,log_intervals={t:bounds for t,_,bounds in moments['reversed'].terms},
  phase=dict(m=mc,W=Wc,s=sc,a=b,maxchild=rc,moment_upper=phase_moment,strict_gap=1-phase_moment),
  semantic=dict(Gscalar=Gscalar,E=E,B=B,C0=C0,C1=1,literal_charge=literal,strict_gap=E-literal),
  rows=dict(bit_depth=hb,complex_depth=hc,bit_wire_bits=wb,complex_wire_bits=wc,coefficient=coefficient,degree=degree,degree_gap=row_gap,suffix_slope=4*degree),
  balanced=assemblies,PR33_kappa=F(1638103206,10**14),
  improvement=assemblies['reversed']['parameters']['kappa']-F(1638103206,10**14),
  controls=dict(standard_lower_at_reversed_saving=moments['standard'].lower(bit_results['reversed']['a']),
     original_lower_at_standard_saving=moments['original91'].lower(bit_results['standard']['a']),float_inputs_rejected=True,
     baseline_nonmathematical_numeric_root_discarded=True),
  geometry_dependency=dict(task='IM-PAPER-TWO-STAGE-TOPOLOGY-031',proof_sha256='b5b13558d1537202210035ed8f4eff5b66fe8baf027a01e0ed7c5edc5c5d5ff0',certificate_sha256='6e2dcd6fa858bb1f1be78070af0798ca7b309bbf3a21ae3a03b369adff206770'),
  remaining_assumptions=['Imported producer scalar correctness, frame inclusions, ownership and complete-word fixed-tape compilation.',
    'Separately proved uniform reversed-order common-basis blocks and both-orientation dirty-scratch semantics.',
    'Accepted generic balanced semantic/router/inverse/bulk transfer and retained exact recovery, prime/setup and logarithmic thresholds.'])
args.output.write_text(json.dumps(encode(result),indent=2,sort_keys=True)+'\n')
for name in ('standard','reversed'):
    print(name,'bit=',bit_results[name]['a'],'kappa=',assemblies[name]['parameters']['kappa'],
          'next_lower_above_one=',bit_results[name]['next_lower']>1)
print('PASS physical histogram, 47 strict conditions per row, exact depth and product stock, six checkpoints per row.')
print('Improvement over pinned PR33:',result['improvement'])

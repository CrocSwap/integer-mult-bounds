#!/usr/bin/env python3
"""Independently reconstructed PR33 moment and conditional balanced interfaces.
No supplier or author executable is imported. Proof data use integers/Fractions.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha1,sha256
from math import comb,factorial
from pathlib import Path
import argparse,json,resource,time

resource.setrlimit(resource.RLIMIT_AS,(100*1024*1024,100*1024*1024))
resource.setrlimit(resource.RLIMIT_CPU,(55,55))
tick=time.monotonic_ns()
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PACK=HERE.parent/'two_stage_composition'
SOURCE=PACK/'verified_inputs'
parser=argparse.ArgumentParser()
parser.add_argument('--output',type=Path,default=HERE/'INDEPENDENT_CHECKS.json')
parser.add_argument('--author-certificate',type=Path,required=True)
parser.add_argument('--source-root',type=Path,required=True,help='Native pinned PR33 repository root; omits private documentary acceptance checks.')
args=parser.parse_args()

def reject_float(s):raise ValueError('Float in scientific JSON input: '+s)
def read(path):return json.loads(path.read_text(),parse_float=reject_float,parse_constant=reject_float)
def ceil(q):return -(-q.numerator//q.denominator)
def rounded(q,scale,up):return Q(ceil(q*scale) if up else (q*scale).numerator//(q*scale).denominator,scale)
def approx(q):
    sign='-' if q<0 else ''
    q=abs(q); z=(q*10**24).numerator//(q*10**24).denominator
    return sign+str(z//10**24)+'.'+str(z%10**24).zfill(24)

sources={}
assert sha256(args.author_certificate.read_bytes()).hexdigest()=='a5b04a8d21d43b4ea3b9a18d1f2800fbae0d340d9a75c7be0dae989b3211a6d4'
SOURCE=args.source_root.resolve()
source_manifest=read(args.author_certificate)['sources']
for item in source_manifest:
    raw=(SOURCE/item['path']).read_bytes()
    assert item['commit']=='e0399d0e1a222bebf72e44ad374004bbcb7f2c64'
    assert len(raw)==item['bytes'] and sha256(raw).hexdigest()==item['sha256']
    assert sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==item['git_blob']
    sources[item['path']]=item['sha256']
assert len(sources)==9
base=SOURCE/'research/two-stage-dimensions'
records={h:read(base/f'producer-{h}.json')['matched'] for h in (45,47)}
pinned=read(base/'corners/certificate-corners-47-45.json')
phasepath=SOURCE/'research/translated-partial/complex-certificate.json'
phase=read(phasepath)
assert sha256(phasepath.read_bytes()).hexdigest()=='399f102e9bab4d098604971c22d1ec39a787ca39dce84c455791d857e97739f0'
sources['PR21_complex_certificate']=sha256(phasepath.read_bytes()).hexdigest()
# Each occurrence is counted in exactly one physical class; local calls do
# not include the separately enumerated exterior, data, growth or copy terms.
aaxis,baxis=47,45
m=aaxis*baxis
v={h:comb(h,3) for h in records}
N=v[45]*v[47]
banks={h:v[m//h]*records[h]['R'] for h in records}
W=2*N+sum(banks.values())
L=sum(v[m//h]*h*(h-1) for h in records)
parts={}
for h,rec in records.items():
    assert rec['h']==h and rec['v']==v[h]
    assert rec['q']==3*v[h]+h
    assert rec['R']==rec['c']+rec['q']-rec['matched']
    assert rec['loss']==h*(h-1)
    assert sum(r*n for r,n in enumerate(rec['histogram']))==h*rec['R']+2*rec['loss']==rec['rank_sum']
    local=Counter()
    for r,n in enumerate(rec['histogram']):
        copies=v[m//h]*n
        if 2*r>h:
            local[1]+=(h-r)*copies
            local[2*r-h]+=copies
        else:local[1]+=r*copies
    parts[f'local_{h}']=+local
    parts[f'exterior_{h}']=Counter({h:banks[h],m-2*h:banks[h]})
    parts[f'growth_{h}']=Counter({1:2*N,h-2:2*N})
parts['paid_correction']=Counter({1:N})
parts['singleton_data']=Counter({1:2*N*(aaxis+baxis-1),m-2*(aaxis+baxis-1):2*N})
singletons=sum(parts.values(),Counter())
standard=singletons.copy(); standard[1]-=2*N*(43+37); standard[43]+=2*N;standard[37]+=2*N
assert dict(standard)=={int(k):n for k,n in pinned['rows'].items()}
reversed_profile=singletons.copy();reversed_profile[1]-=2*N*(43+39);reversed_profile[43]+=2*N;reversed_profile[39]+=2*N
assert {k:reversed_profile[k]-standard[k] for k in standard if reversed_profile[k]!=standard[k]}=={1:-4*N,37:-2*N,39:2*N}
s=W*m-N+2*L
assert (m,N,W,L,s,W*m-s)==(2115,230090850,11710626180,62784480,24767869848810,104521890)
for counts in (singletons,standard,reversed_profile):
    assert all(isinstance(k,int) and 0<k<m and isinstance(n,int) and n>0 for k,n in counts.items())
    assert sum(k*n for k,n in counts.items())==s and max(counts)==2025
assert sum(k*n for k,n in standard.items())-N != s

# atanh expansion: log(x)=2 sum z^(2j+1)/(2j+1), 0<=z<=1/3.
# Sixty terms and exact geometric tail, outward rounded only afterwards.
@lru_cache(None)
def log_range(q):
    exponent=0
    while q>=2:q/=2;exponent+=1
    def small(x):
        z=(x-1)/(x+1); z2=z*z; power=z; total=Q(0)
        for j in range(60):total+=2*power/(2*j+1);power*=z2
        return total,total+2*power/(121*(1-z2))
    lo,hi=small(q);l2,h2=small(Q(2));lo+=exponent*l2;hi+=exponent*h2
    return rounded(lo,10**24,False),rounded(hi,10**24,True)

def moment(counts,arity,wires,saving,method='taylor'):
    lower=Q(0);upper=Q(0)
    for width,copies in sorted(counts.items()):
        lo,hi=log_range(Q(arity,width));u=saving*lo;v=saving*hi
        assert 0<=u<=v<1
        low=sum((u**j/factorial(j) for j in range(7)),Q(0))
        high=(sum((v**j/factorial(j) for j in range(7)),Q(0))+v**7/(factorial(7)*(1-v/8)))
        if method=='source':
            # Source convention: log rounded up on the 10^-12 lattice.
            uu=saving*rounded(hi,10**12,True)
            high=1+uu+uu*uu/(2*(1-uu/3))
        weight=Q(width*copies,arity*wires)
        lower+=weight*low;upper+=weight*high
    return lower,upper

def greatest_saved_grid(counts):
    lo,hi=0,1800000000
    while hi-lo>1:
        mid=(lo+hi)//2
        if moment(counts,m,W,Q(mid,10**14),'source')[1]<1:lo=mid
        else:hi=mid
    return Q(lo,10**14)

baseline_a=Q(1638156876,10**14)
assert greatest_saved_grid(standard)==baseline_a
new_a=greatest_saved_grid(reversed_profile)
assert new_a>baseline_a
certified={}
for name,counts,saving in [('standard',standard,baseline_a),('reversed',reversed_profile,new_a)]:
    low,high=moment(counts,m,W,saving)
    _,savedhigh=moment(counts,m,W,saving,'source')
    nextlow,_=moment(counts,m,W,saving+Q(1,10**14))
    assert high<1 and savedhigh<1 and nextlow>1
    certified[name]={'saving':saving,'lower':low,'upper':high,'gap':1-high,'source_upper':savedhigh,'source_gap':1-savedhigh,'next_grid_actual_excess_lower':nextlow-1}
assert certified['standard']['source_upper']==Q(pinned['bit']['moment_upper'])
wrong_standard_low,_=moment(standard,m,W,new_a)
assert wrong_standard_low>1
no_copy=reversed_profile.copy();no_copy[1]-=N
assert sum(k*n for k,n in no_copy.items())==s-N
assert moment(no_copy,m,W,new_a)[1]<certified['reversed']['upper']

mc,Wc,sc=phase['m'],phase['W'],phase['s']
c_counts={int(k):n for k,n in phase['child_counts'].items()}
assert (mc,Wc,sc,max(c_counts))==(21952,2085111546336,45772350635112192,21924)
assert sum(k*n for k,n in c_counts.items())==sc
assert Wc*mc-sc==phase['D']==18030055680
for k,n in c_counts.items():assert Q(k*n,mc*Wc)==Q(phase['rank_mass_weights'][str(k)])
b=Q(18,10**6)
phase_low,phase_high=moment(c_counts,mc,Wc,b)
assert phase_high<1
Gscalar=3*comb(28,3)**2*(4*64298+4*comb(28,3)+4)
E=64*(Wc+mc+1)**3
literal=2*Gscalar*Wc**2+8*sc+4*Wc+4+32*mc
B=sc+E;C0=32*mc*B*B
assert literal<E and 2*B*(mc-max(c_counts))>=sc+E and C0>2*B+18
for root in (mc-1,mc,mc+1,10*mc+1,mc**3,10**12):
    width=root;bound=0
    while width>=mc:
        f=width//mc;bound+=sc*f+E;width=max(c_counts)*f
    assert bound+8*width<=2*B*root

def least_halving(arity,child):
    k=0;x=y=1
    while x<=2*y:k+=1;x*=arity;y*=child
    assert arity**(k-1)<=2*child**(k-1)
    return k
hb,hc=least_halving(m,2025),least_halving(mc,21924)
wb,wc=W.bit_length(),Wc.bit_length()
coefficient=hb*wb+hc*wc;degree=47000
assert (hb,hc,wb,wc,coefficient)==(16,544,34,41,22848)
assert Q(degree)-Q(51,25)*coefficient==Q(9752,25)>0

h=Q(1,10**12);beta=Q(1,20);delta=h/8
old_kappa=Q(1638103206,10**14)

def assembly(a):
    q=a*(1-2*h);c=q+h/4;epsilon=(1-h)/(1+q)
    gain=epsilon*q;r=(gain+1-epsilon)/2
    tau,sigma=1-a,1-b
    lp=1-q;lam=(tau+lp)/2
    internal=tau+(1-beta)*max(sigma-tau,Q(0));leaf=sigma+beta*(1-sigma)
    kappa=rounded(gain,10**14,False)
    slacks={
      'a_positive':a,'b_above_a':b-a,'b_small':Q(1,32)-b,'beta_positive':beta,'beta_small':1-beta,
      'phase_leaf_above_bit':(1-beta)*b-a,'q_positive':q,'q_below_internal':1-internal-q,'q_below_leaf':1-leaf-q,
      'c_positive':c,'c_small':1-c,'c_above_q':c-q,'lambda_above_tau':lam-tau,'lambda_above_sigma':lam-sigma,
      'lambda_above_internal':lam-internal,'lambda_prime_above_lambda':lp-lam,'lambda_prime_below_one':1-lp,
      'compact_leaf':lp-leaf,'compact_reservations':lp-(1-c),'epsilon_positive':epsilon,'epsilon_below_one':1-epsilon,
      'semantic_guard':1-epsilon,'K_geometry':1-epsilon*(1+c),'K_dominates_log':epsilon*c,'record_suffix':1-epsilon,
      'gaussian_local':1-epsilon-delta,'gaussian_boundary':r-delta,'gamma':1-epsilon-r,'phase_cell':epsilon-(1-r)/2,
      'prime_packing':1-epsilon,'alpha_positive':r,'alpha_below_one':1-r,'alpha_below_quarter':Q(1,4)-r,
      'delta_positive':delta,'delta_small':Q(1,8)-delta,'short_record_fallback':epsilon-a,'small_field_exposure':1-epsilon-gain,
      'artificial_boundary':8-epsilon+r-delta-gain,'literal_scalar_guard':Q(E-literal),'row_stock_degree':Q(degree)-Q(51*coefficient,25)
    }
    margins=[1-epsilon,a,gain,a,min(1-epsilon-delta,r-delta),1-epsilon-delta,epsilon]
    slacks.update({f'margin_{j}_above_kappa':g-kappa for j,g in enumerate(margins,1)})
    extra={'source_halo':8-epsilon-3,'target_halo':8-epsilon-3,'halo_vs_Jw':3-2-(1-r)/2}
    assert len(slacks)==47 and all(isinstance(x,Q) and x>0 for x in [*slacks.values(),*extra.values()])
    assert min(margins)==gain and 1-epsilon-gain==h and 1-epsilon-r==h/2
    assert 1-epsilon*(1+c)==h-epsilon*h/4
    assert gain-kappa>0 and gain-(kappa+Q(1,10**14))<0
    assert kappa>old_kappa>Q(1,65536) and kappa<Q(1,32768)
    negatives={
      'original_prefix_shortfall':kappa-(1-epsilon*(1+c)),
      'old_guard_violation':epsilon*Q(19991,10000)-1,
      'separate_exposure_shortfall':kappa-a*(1-epsilon),
      'beta_one_tenth_leaf_violation':a-Q(9,10)*b,
      'beta_one_quarter_leaf_violation':a-Q(3,4)*b,
      'next_kappa_grid_shortfall':kappa+Q(1,10**14)-gain,
      'unsupported_2_minus_15':Q(1,32768)-gain
    }
    assert all(x>0 for x in negatives.values())
    cutoff=14000000000000
    ka,kk,kp,kl=[ceil(1/x) for x in (r,epsilon*c,1-epsilon,epsilon*beta)]
    assert cutoff*(1-epsilon-r)>=7 and cutoff*(1-epsilon)>=(2*C0).bit_length()
    assert cutoff*(epsilon-(1-r)/2)>=9 and cutoff*(1-epsilon*(1+c))>=3
    assert cutoff>=max(2*ka,2*kk,2*kp,2*kl,25)
    powers=[]
    for shift in range(6):
        logn=cutoff*2**shift
        constraints={'alpha':(logn//ka,8*(logn+ka)+64),'compact':(logn//kk,32*(logn+kk)+192),
          'period':(logn//kp,16*(logn+kp)+56),'rows':(logn//kp,4*degree*(logn+kp+8)),'leaf':(logn//kl,4*max(m,mc))}
        assert all(exponent>=rhs.bit_length() for exponent,rhs in constraints.values())
        powers.append({'log2_input':logn,'constraints':constraints})
    return {'parameters':dict(a=a,b=b,h=h,beta=beta,q=q,c=c,epsilon=epsilon,r=r,delta=delta,lambda_=lam,lambda_prime=lp,kappa=kappa),
      'slacks':slacks,'extra_slacks':extra,'margins':margins,'minimum':gain,'absorption_gap':gain-kappa,
      'improvement_over_PR33':kappa-old_kappa,'negative_controls':negatives,'cutoff_log2_input':cutoff,'power_checks':powers}

rows={'standard':assembly(baseline_a),'reversed':assembly(new_a)}
assert rows['reversed']['parameters']['kappa']>rows['standard']['parameters']['kappa']

# Address-only controls of paid correction. F swaps address sides; U is one
# coordinate, T swaps only U and E swaps the complementary coordinates.
# All basis x,y inputs are checked over F2. This tests the endpoint identity,
# not the imported arbitrary-dirty finite producer theorem.
endpoint_cases=0;missing_fails=0
for dimension in (2,3,5):
    size=2*dimension
    def act(mask,selected):
        result=0
        for index in range(size):
            side,k=divmod(index,dimension)
            dst=(1-side)*dimension+k if k in selected else index
            if mask>>index&1:result^=1<<dst
        return result
    for origin in range(2*size):
        x=(1<<origin) if origin<size else 0;y=(1<<(origin-size)) if origin>=size else 0
        Fset=set(range(dimension));Uset={0};Eset=Fset-Uset
        A=act(y,Fset);dirtyB=act(x,Fset)^act(y,Eset)
        finalB=dirtyB^act(A,Uset)
        assert A==act(y,Fset) and finalB==act(x,Fset)
        missing_fails+=dirtyB!=act(x,Fset);endpoint_cases+=1
assert missing_fails>0

# Named coordinates are permuted only. All supplied widths are equal across
# axes within a round, and reverse chronology preserves lower-bit recovery.
layout_cases=0
for n in range(1,49):
    for K in range(1,n+1):
        count=n//K;basewidth,extra=divmod(n,count)
        widths=[basewidth+int(j<extra) for j in range(count)]
        assert sum(widths)==n and all(K<=w<2*K for w in widths)
        groups={};end=n
        for j,width in enumerate(widths):
            for bit in range(end-width,end):groups[bit]=j
            end-=width
        for axes in (1,2,3):
            for longs in range(1<<axes):
                orig=[(a,k) for a in range(axes) for k in range(n+(longs>>a&1)-1,-1,-1)]
                rearranged=sorted(orig,key=lambda x:(-1,x[0],0) if x[1]==n else (groups[x[1]],x[0],-x[1]))
                locations={slot:i for i,slot in enumerate(rearranged)}
                assert len(locations)==len(orig) and [rearranged[locations[x]] for x in orig]==orig
                for axis in range(axes):assert [k for a,k in rearranged if a==axis]==list(range(n+(longs>>axis&1)-1,-1,-1))
                layout_cases+=1

# Exact comparison is data-only and optional until the author freezes bytes.
author_binding=None
if args.author_certificate:
    author=read(args.author_certificate)
    assert author['sources']==source_manifest
    assert author['complex_source_sha256']==sources['PR21_complex_certificate']
    assert author['counts']=={'m':m,'N':N,'W':W,'s':s,'loss':L,'banks':{str(k):v for k,v in banks.items()},'deficit':W*m-s,'copy_corrections':N}
    for name,counts in [('original91',singletons),('standard',standard),('reversed',reversed_profile)]:
        assert author['histograms'][name]==[[k,v] for k,v in sorted(counts.items())]
    for width,interval in author['log_intervals'].items():
        lo,hi=log_range(Q(m,int(width)))
        assert Q(interval[0])<=lo<=hi<=Q(interval[1])
    for name,counts in [('standard',standard),('reversed',reversed_profile)]:
        saved=author['moments'][name]; ours=certified[name]
        assert Q(saved['a'])==ours['saving']
        assert Q(saved['moment_upper'])==ours['source_upper'] and Q(saved['strict_gap'])==ours['source_gap']
        nextpoint=ours['saving']+Q(1,10**14)
        lower=Q(0)
        for width,copies in counts.items():
            u=nextpoint*Q(author['log_intervals'][str(width)][0])
            lower+=Q(width*copies,m*W)*(1+u+u*u/2+u*u*u/6)
        assert Q(saved['next_grid'])==nextpoint and Q(saved['next_lower'])==lower>1
        assert Q(saved['next_upper'])==moment(counts,m,W,nextpoint,'source')[1]
        savedrow=author['balanced'][name];row=rows[name]
        assert {k:Q(v) for k,v in savedrow['parameters'].items()}==row['parameters']
        assert [Q(v) for v in savedrow['margins']]==row['margins']
        assert Q(savedrow['minimum'])==row['minimum'] and Q(savedrow['absorption_gap'])==row['absorption_gap']
        assert savedrow['common_cutoff']==row['cutoff_log2_input']
        names={'complex_above_bit':'b_above_a','complex_small':'b_small','leaf_above_bit':'phase_leaf_above_bit',
               'compact_geometry':'K_geometry','compact_dominates_log':'K_dominates_log','phase_local':'gaussian_local',
               'phase_boundary':'gaussian_boundary','normalization':'gamma','alpha_small':'alpha_below_one',
               'alpha_quarter':'alpha_below_quarter','row_product_stock':'row_stock_degree'}
        names.update({f'margin{j}_above_kappa':f'margin_{j}_above_kappa' for j in range(1,8)})
        assert len(savedrow['conditions'])==47
        for key,val in savedrow['conditions'].items():assert Q(val)==row['slacks'][names.get(key,key)]
        for checkpoint,ours_cp in zip(savedrow['power_checkpoints'],row['power_checks']):
            assert checkpoint['log2_input']==ours_cp['log2_input']
            for key,entry in checkpoint['powers'].items():
                assert (entry['exponent'],entry['rhs'])==tuple(ours_cp['constraints'][key])
                assert entry['rhs_bits']==entry['rhs'].bit_length()
    phase_geometric=sum((Q(width*copies,mc*Wc)/(1-b*rounded(log_range(Q(mc,width))[1],10**12,True)) for width,copies in c_counts.items()),Q(0))
    assert Q(author['phase']['moment_upper'])==phase_geometric<1
    assert author['semantic']==dict(Gscalar=Gscalar,E=E,B=B,C0=C0,C1=1,literal_charge=literal,strict_gap=E-literal)
    assert author['rows']==dict(bit_depth=hb,complex_depth=hc,bit_wire_bits=wb,complex_wire_bits=wc,coefficient=coefficient,degree=degree,degree_gap=str(Q(9752,25)),suffix_slope=4*degree)
    assert Q(author['improvement'])==rows['reversed']['improvement_over_PR33']
    author_binding={'path':args.author_certificate.name,'sha256':sha256(args.author_certificate.read_bytes()).hexdigest(),'bytes':args.author_certificate.stat().st_size,'comparison':'All histograms, logarithm enclosures, moments, parameters, 47 conditions per row, graph constants and cutoff powers match exactly.'}

result={'status':'PASS exact arithmetic; reversed-stage/common-basis geometry remains separate prerequisite',
 'author_certificate_binding':author_binding,'source_sha256':sources,'reviewer_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
 'bit':{'arity':m,'W':W,'N':N,'loss':L,'rank_mass':s,'deficit':W*m-s,'physical_parts':parts,
 'singleton_histogram':singletons,'standard_histogram':standard,'reversed_histogram':reversed_profile,
 'moments':certified,'log_intervals':{k:log_range(Q(m,k)) for k in standard},
 'old_profile_at_new_saving_excess_lower':wrong_standard_low-1},
 'complex':{'arity':mc,'W':Wc,'rank_mass':sc,'moment_upper':phase_high,'gap':1-phase_high},
 'semantic':{'Gscalar':Gscalar,'E':E,'literal':literal,'B':B,'C0':C0,'C1':1},
 'stock':{'bit_depth':hb,'complex_depth':hc,'bit_wire_bits':wb,'complex_wire_bits':wc,'coefficient':coefficient,'degree':degree,'suffix_coefficient':4*degree},
 'balanced':rows,'endpoint_cases':endpoint_cases,'missing_correction_failures':missing_fails,'named_slot_cases':layout_cases,
 'elapsed_milliseconds':(time.monotonic_ns()-tick)//1000000,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}

def serial(obj):
    if isinstance(obj,Q):return str(obj)
    if isinstance(obj,dict):return {str(k):serial(v) for k,v in obj.items()}
    if isinstance(obj,(list,tuple)):return [serial(x) for x in obj]
    return obj
args.output.write_text(json.dumps(serial(result),indent=2,sort_keys=True)+'\n')
for name in rows:
    print(name,'a =',certified[name]['saving'],'kappa =',rows[name]['parameters']['kappa'])
    print('bit gap >=',approx(certified[name]['gap']),'next-grid true excess >=',approx(certified[name]['next_grid_actual_excess_lower']))
    print('final slack =',approx(rows[name]['absorption_gap']),'47 + 3 strict inequalities pass')
print('PASS:',layout_cases,'named-slot shapes;',endpoint_cases,'endpoint basis controls;',result['elapsed_milliseconds'],'ms;',result['peak_rss_kib'],'KiB RSS')

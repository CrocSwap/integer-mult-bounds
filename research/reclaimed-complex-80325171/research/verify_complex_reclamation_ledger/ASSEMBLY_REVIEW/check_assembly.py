"""Original independent exact composition audit; passive data/text inputs only."""
if not __debug__:raise RuntimeError('Assertions required: optimized Python is unsupported')
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import hashlib,json,math,time,resource
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[2];AUTHOR=REPO/'research/explore_complex_ceiling_breakthrough/compose_pr104'
t0=time.monotonic()
submission_pins={'PREPARATION.json':'53c2f92e23a06fe73d6ad3810075a8901420725ef1425e8171554993de8ed0f1','PROOF.md':'56742633cd5791e6e0125aeb9afe07823abf66be42d73fbc7e739d0d287dbe7a','AMENDMENT_1.md':'aa9f2afafe80284d7aac770d8978ace01dbba0d40f0e75b720ec685463bd5f87','INPUT_PINS.json':'cd2595a5408e38ecb96a038c23f88f42e2459c1e03fa5b39f48a77de3f35c589'}
for name,digest in submission_pins.items():assert hashlib.sha256((AUTHOR/name).read_bytes()).hexdigest()==digest
submitted=json.loads((AUTHOR/'PREPARATION.json').read_text());pins=json.loads((AUTHOR/'INPUT_PINS.json').read_text());sources={}
for label,pin in pins.items():
    p=REPO/pin['path'];raw=p.read_bytes();digest=hashlib.sha256(raw).hexdigest();assert digest==pin['sha256'];sources[label]=dict(path=pin['path'],sha256=digest)
assert sources['new_component']['sha256']=='fda200a76ab4baf667da849177f641755e21c927bf71576ddbed2bb83ff594e0'
def data(label):return json.loads((REPO/pins[label]['path']).read_text())
net=data('104');leaf=data('old_leaf');cx=data('new_component');guard=data('new_guard')
for rel in ('notes/stopped-product-factorization.tex','notes/stopped-product-interface.tex','notes/stopped-product-assembly.tex'):
    assert hashlib.sha256((REPO/'research/pr_watch_2316/PR104'/rel).read_bytes()).hexdigest()==net['source_sha256'][rel]
assert net['source_sha256']['scripts/structured_bulk_assembly.py']==sources['assembly_text']['sha256']
assert net['source_sha256']['certificates/copied-centers-network.json']==sources['old_leaf']['sha256']
assert cx['base']=='f5f9c56e637463cac1e300d1589ccf42838f688a' and cx['assertions_enabled'] and cx['roles']==40011
# New moment enclosure, deliberately more accurate than the author's formula.
def ln_unit(x):
    assert 1<=x<=2;z=(x-1)/(x+1);power=z;ss=F(0)
    for k in range(44):ss+=2*power/(2*k+1);power*=z*z
    return ss,ss+2*power/(89*(1-z*z))
log2=ln_unit(F(2));cache={}
def ln_ratio(m,r):
    if (m,r) not in cache:
        x=F(m,r);k=0
        while x>=2:x/=2;k+=1
        lo,hi=ln_unit(x);cache[m,r]=(lo+k*log2[0],hi+k*log2[1])
    return cache[m,r]
def exp_interval(low,high):
    assert 0<=low<=high<1
    def terms(x):
        cur=F(1);s=cur
        for k in range(1,13):cur*=x/k;s+=cur
        return s,cur*x/13
    l,_=terms(low);u,next_=terms(high);return l,u+next_/(1-high/14)
def rounded(q,up=False):
    v=q*(1<<192);n=v.numerator//v.denominator
    if up and v.denominator!=1:n+=1
    return F(n,1<<192)
def check_moment(label,m,W,children,a):
    rows={int(k):int(v) for k,v in children.items()};assert rows and all(0<t<m and n>0 for t,n in rows.items())
    lo=hi=F(0)
    for t,n in rows.items():
        l,u=ln_ratio(m,t);p,q=exp_interval(a*l,a*u);weight=F(n*t,m*W);lo+=weight*p;hi+=weight*q
    lo,hi=rounded(lo),rounded(hi,True);assert hi<1
    mass=sum(t*n for t,n in rows.items());assert mass<m*W
    return dict(label=label,m=m,W=W,rank=mass,maxchild=max(rows),saving=str(a),lower=str(lo),upper=str(hi),strict_gap=str(1-hi),rank_moment=str(F(mass,m*W)),rank_gap=str(1-F(mass,m*W)))
a0=F(4019,50000000);aold=F(384599,10**10);theta=F(1,1000);a=(1-theta)*a0+theta*aold;b=F(217021,2500000000)
assert a==F(803380799,10**13)==F(net['bit']['stopped_adapter']['effective_saving'])
assert aold==F(leaf['bit']['saving']) and 0<aold<a0<theta<1 and a<theta
coarse=net['bit']['counts'];old=leaf['bit']['counts']
assert (coarse['m'],coarse['W'],coarse['maxchild'])==(529,143617474,506)
assert (old['m'],old['W'],old['maxchild'])==(575,188181929,529)
assert (cx['W'],cx['rank'])==(170157680,98008965648)
moments=[check_moment('coarse',529,143617474,coarse['child_multiplicities'],a0),check_moment('ordinary_leaf',575,188181929,old['child_multiplicities'],aold),check_moment('new_complex',576,cx['W'],cx['child_histogram'],b)]
for ours,theirs in zip(moments,submitted['moments']):
    assert ours['rank']==theirs['rank'] and ours['m']==theirs['m'] and ours['W']==theirs['W']
    # The independent tighter enclosure fits inside the submitted enclosure.
    assert F(theirs['lower'])<=F(ours['lower'])<=F(ours['upper'])<=F(theirs['upper'])
# Reprice from independently replayed operations, not from the old supplier G.
v=2024;N=v*v;R=cx['roles'];m=576;W=cx['W'];s=cx['rank'];rmax=552
L=cx['literal_mixer_scalar_gate_upper'];V=cx['source_injections'];J=cx['scatter_terms']
local=4*L+2*V+2*J+8*24+4*R;G=2*v*local+4*N
assert G==3205012096==guard['global_scalar_group_upper']
assert cx['max_mixer_numerator']==cx['max_mixer_denominator']==1 and cx['max_scatter_coefficient']=='19/2'
E=64*(W+m+G+1)**3;charge=2*G*W*W+8*s+4*W+4+32*m;B=s+E;C0=32*m*B*B
assert charge<E and 2*B*(m-rmax)>=s+E and 2*B+18<C0
for name,value in [('E',E),('literal_charge',charge),('semantic_B',B),('C0',C0)]:assert guard[name]==value
sem=submitted['finite_bridge']['semantic']
for name,value in dict(E=E,literal_charge=charge,strict_literal_gap=E-charge,B=B,C0=C0,C1=1,induction_gap=2*B*(m-rmax)-s-E).items():assert sem[name]==value
# Three simultaneously available stocks, not the maximum of them.
def halfdepth(m,r):
    t=1
    while m**t<=2*r**t:t+=1
    assert t==1 or m**(t-1)<=2*r**(t-1)
    return t
families=[(529,506,143617474),(575,529,188181929),(576,552,W)]
stock=[dict(m=m,maxchild=r,W=w,depth=halfdepth(m,r),bits=w.bit_length()) for m,r,w in families]
assert [(x['depth'],x['bits']) for x in stock]==[(16,28),(9,28),(17,28)]
rows=sum(x['depth']*x['bits'] for x in stock);rowgap=F(4000)-F(51,25)*rows
assert rows==1176 and rowgap==F(40024,25)>0
assert submitted['finite_bridge']['rows']['coefficient']==rows and F(submitted['finite_bridge']['rows']['degree_gap'])==rowgap
assert submitted['finite_bridge']['rows']['degree']==4000 and submitted['finite_bridge']['rows']['suffix_slope']==16000
# Derive the retained constraints as separate semantic, layout and work groups.
eta=F(1,10**8);beta=F(1,10**6);tau=1-a;sigma=1-b;q=a*(1-2*eta);c=q*(1+eta);eps=(1-eta)/(1+c+q)
lp=1-q;lam=(tau+lp)/2;g=eps*q;r=(g+1-eps)/2;delta=eta/8;k=F(80325171,10**12)
internal=tau+(1-beta)*max(sigma-tau,F(0));leafexp=sigma+beta*(1-sigma);reserve=1-c
params=dict(a_bit=a,a_complex=b,atom=theta,eta=eta,beta=beta,tau=tau,sigma=sigma,q=q,c=c,epsilon=eps,lambda_=lam,lambda_prime=lp,alpha_squared_power=r,delta=delta,C0=C0,C1=1,kappa=k)
for name,value in params.items():assert F(submitted['assembly']['parameters'][name])==value,(name,value)
semantic=dict(bit_positive=a,complex_above_bit=b-a,complex_below_one_over32=F(1,32)-b,beta_positive=beta,beta_below_one=1-beta,leaf_saving_above_bit=(1-beta)*b-a,
 q_positive=q,q_below_internal=1-internal-q,q_below_leaf=1-leafexp-q,c_positive=c,c_below_one=1-c,q_below_reservations=c-q,
 lambda_above_tau=lam-tau,lambda_above_sigma=lam-sigma,lambda_above_internal=lam-internal,lambda_prime_above_lambda=lp-lam,
 compact_leaf=lp-leafexp,compact_reservations=lp-reserve,lambda_prime_below_one=q)
layout=dict(epsilon_positive=eps,epsilon_below_one=1-eps,guard_width=1-eps,K_geometry=1-eps*(1+c),K_dominates_log=eps*c,
 record_suffix=1-eps,phase_local=1-eps-delta,phase_boundary=r-delta,gamma_sublinear=1-eps-r,cell_above_band=eps-(1-r)/2,
 prime_interval_packing=1-eps,alpha_positive=r,alpha_below_one=1-r,alpha_below_one_fourth=F(1,4)-r,delta_positive=delta,delta_below_one_eighth=F(1,8)-delta,
 short_record_fallback=eps-a,small_field_exposure=1-eps-g,artificial_boundary=8-eps+r-delta-g,literal_scalar_guard=F(E-charge),row_product_gap=rowgap)
margins=dict(original_prefix=1-eps*(1+c),coordinate_movement=a,compact_phase_layer=g,bulk_exposure=a,Gaussian_arithmetic=min(1-eps-delta,r-delta),scalar_work=1-eps-delta,dimension=eps)
slacks=semantic|layout|{name+'_above_kappa':value-k for name,value in margins.items()}
assert len(semantic)+len(layout)==40 and len(slacks)==47 and len(margins)==7
assert slacks=={name:F(value) for name,value in submitted['assembly']['strict_constraints'].items()}
assert margins=={name:F(value) for name,value in submitted['assembly']['margins'].items()}
assert all(value>0 for value in slacks.values()) and min(margins.values())==g and margins['original_prefix']==g+eta
assert submitted['assembly']['recurrence']==dict(internal=str(internal),leaf=str(leafexp),reservations=str(reserve))
assert F(submitted['assembly']['minimum_margin'])==g and F(submitted['assembly']['absorption_gap'])==g-k
# Fixed-parameter adjacent rejection, distinct from an analytic class ceiling.
step=F(1,10**12);next_=k+step;ceiling=a/(1+2*a)
assert 0<g-k<step and g-next_<0 and F(submitted['next_grid_point'])==next_ and F(submitted['next_grid_rejected_margin'])==g-next_
assert k<g<ceiling<a and (g*10**12).numerator//(g*10**12).denominator==k*10**12
assert k>F(net['kappa']) and F(submitted['relative_gain'])==k/F(net['kappa'])-1
assert F(submitted['kappa_candidate'])==k and F(submitted['actual_bit_saving'])==a and F(submitted['complex_saving'])==b
# Negative controls for the three particularly dangerous substitutions.
assert 2*v*(4*L+2*V+2*J)+4*N<G # extra copying/bookkeeping was really retained
assert max(x['depth']*x['bits'] for x in stock)<rows
assert F(9,10)*b<a # former h24 beta=1/10 would NOT support full new bit saving

def js(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,dict):return {str(k):js(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [js(v) for v in x]
    return x
out=dict(status='PASS: original exact arithmetic; mathematical interface agreement reviewed separately',candidate=k,grid=10**12,all_constraints=slacks,margins=margins,minimum_margin=g,absorption_gap=g-k,next_grid=next_,next_gap=g-next_,
 recipe_ceiling=ceiling,ceiling_minus_candidate=ceiling-k,bit_minus_candidate=a-k,not_an_optimality_claim='Adjacent rejection applies only to the submitted fixed parameters; the separate ceiling assumes the same bit saving and prefix/reservation interface.',
 moments=moments,scalar=dict(local=local,G=G,E=E,literal_charge=charge,literal_gap=E-charge,B=B,C0=C0,C1=1,induction_gap=2*B*(m-rmax)-s-E,normalization_gap=C0-2*B-18),
 stock=stock,row_coefficient=rows,row_degree=4000,row_gap=rowgap,suffix_slope=16000,parameters=params,recurrence=dict(internal=internal,leaf=leafexp,reservations=reserve),
 sources=sources,submission_pins=submission_pins,checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),submission_sha256=hashlib.sha256((AUTHOR/'PREPARATION.json').read_bytes()).hexdigest(),initial_proof_sha256=hashlib.sha256((AUTHOR/'PROOF.md').read_bytes()).hexdigest(),seconds=time.monotonic()-t0,rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
(ROOT/'CHECK_RESULTS.json').write_text(json.dumps(js(out),indent=2)+'\n')
print(json.dumps(js(dict(status=out['status'],kappa=k,decimal=float(k),constraints=len(slacks),margins=len(margins),minimum_margin=g,minimum_decimal=float(g),absorption_gap=g-k,gap_decimal=float(g-k),next_grid=next_,next_gap=g-next_,recipe_ceiling=ceiling,ceiling_decimal=float(ceiling),scalar_G=G,row_coefficient=rows,seconds=out['seconds'],rss_KiB=out['rss_KiB'])),indent=2))

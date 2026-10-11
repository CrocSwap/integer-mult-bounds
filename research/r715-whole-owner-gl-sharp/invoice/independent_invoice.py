"""Independent GL sharp-fallback finite invoice and rational arithmetic review.

Prepared with OpenAI Codex. The finite invoices reproduce the declared algebra,
and the separate atanh/Taylor intervals check the two paid moments directly.
Program counts are reused inputs from the fresh source-bound inspector checks.
"""
from pathlib import Path
from fractions import Fraction as Q
from functools import lru_cache
from math import prod
import gzip, hashlib, json, sys

ROOT = Path(__file__).resolve().parent
BIT = Path(sys.argv[1])
CX = Path(sys.argv[2])
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
canonical = lambda o: json.dumps(o, sort_keys=True, separators=(',', ':')).encode()
g, a = read(BIT/'GLOBAL.json'), read(BIT/'AUDIT.json')
c, ca = read(CX/'GLOBAL.json'), read(CX/'AUDIT.json')
result = read(Path(sys.argv[3]))
for folder, global_, audit in [(BIT,g,a),(CX,c,ca)]:
    raw = gzip.decompress((folder/'GLOBAL-TEMPLATE.json.gz').read_bytes())
    assert hashlib.sha256(raw).hexdigest() == global_['template_sha256'] == audit['template_sha256']
    assert canonical(json.loads(raw)) == raw
    assert global_['profile'] == audit['profile']
    assert global_['emitted_program_sha256'] == audit['emitted_program_sha256']

# Rebuild the complete finite bit invoice from its individual charges.
p = {int(k):v for k,v in a['profile'].items()}
m,w,t,r = g['m'],a['live'],g['replicas'],g['R']
stages=(m-1)//7; pairs=(stages-1)//2; v=120; depth=g['halving_depth']
mass=sum(k*n for k,n in p.items()); calls=sum(p.values())
assert m*w-mass == t*(2*pairs*v-72*stages) == g['deficit'] == 3264
physical=w+9
geometry=read(BIT/'GEOMETRY.json')
j=8*t*stages*(2*v+r)+16*pairs*v*t+2*stages*t*r+2*g['copy_erase_episodes']
prefix=int(g['global_prefix_bound'])
parts = dict(local_dispatch=stages*t*g['local_additions']+g['bridge_additions']+100000,
             high_routes=j*16*(m*m+1)**2,
             route_stock=j*physical,
             children=calls*(8*m*m+8+128*(2*m)**3),
             fixed=16*m**3+g['copy_erase_episodes'],
             selectors=2*stages*t*((w-1)+r*m*(geometry['max_route_factors']+144+6+(m-1)+m)),
             prefix=prefix,one=1)
coefficient=sum(parts.values()); repeated=(coefficient+1)**depth*(calls+1)**depth
round64=lambda n:64*((n+63)//64)
assert prefix.bit_length() == coefficient.bit_length() == 775
assert a['physical_prefix_bits']==775 and a['charged_prefix_bits']==round64(775)==832
assert repeated.bit_length()==2379 and round64(2379)==2432
assert m**depth>2*max(p)**depth and m**2<=2*max(p)**2
assert physical<2**80
bit_row=depth*(m*m+1)+9909+252
assert bit_row==28416==result['bit']['row_coefficient']==result['external_row_allowance']
assert result['bit_cover']=='GL_78(Z/q^w)' and result['bit_bad_children']==146478
assert Q(result['bit_bad_fraction'])==Q(2*m**3,2**128)

# Rebuild the complex invoice including every local scalar invocation and all
# helper selectors, then check integer group-order/stock/compiler envelopes.
pc={int(k):v for k,v in ca['profile'].items()}; mc=89; wc=ca['live']; tc=c['replicas']
massc=sum(k*n for k,n in pc.items()); ec=sum(pc.values()); checks=c['source_local_checks']
assert mc*wc-massc==408*tc==2856 and tc==7
compiler=64*(mc+1)**3
adapters=16*(max(x['scalar_macros'] for x in checks.values())+sum(checks['forward']['paid_profile'].values())+240+560+c['private_centers'])+64*mc
local_bound=max(x['real_component_primitive_bound'] for x in checks.values())+16*560+adapters*compiler
scalar=tc*(6*checks['forward']['real_component_primitive_bound']+5*checks['backward']['real_component_primitive_bound'])
assert scalar==c['actual_real_component_primitive_sum']==17162810
bridge=6*4*120*tc; shifts=5*120*tc; moves=10*120*tc
items=6*120*tc*11+6*11*tc*560+26*120*tc+bridge+shifts+moves+wc+c['physical']
cxparts=dict(scalar=scalar,bridge=bridge,shifts=shifts,moves=moves,live=wc,
             compiler=(11*tc*adapters+8*items+64*mc)*compiler,
             physical=64*c['physical'],wrapper=11*tc*560*16)
pervertex=sum(cxparts.values())
order=2**(44**2)*prod(2**(2*i)-1 for i in range(1,45))
stock=order*c['physical']; smass=order*massc; logical=order*pervertex+64
router=compiler*(logical+1)*(stock+1)**2
literal=2*(1<<30000)*stock**2+8*smass+4*stock+4+32*mc
bb=smass+(1<<100000); c0=1<<210000
assert local_bound==18269743335906 and pervertex==1551161226276482
assert local_bound<1<<48 and logical<1<<6050 and router<1<<30000
assert literal<1<<100000 and bb<1<<100001 and 32*mc*bb*bb<c0 and 2*bb+18<c0
assert (pervertex+1)**3*(ec+1)**3<1<<1024
assert [stock.bit_length(),router.bit_length(),literal.bit_length()]==[3929,11849,37859]
assert 89**9>16*64**9 and 89**9<=32*64**9
slope=Q(9,4)*stock.bit_length()+9909+252
row_margin=(20161-slope)*32-9*stock.bit_length()
assert row_margin==1751 and (20161-slope)*30<=9*stock.bit_length()
assert Q(10**6)-Q(51*bit_row,25)>0

# New independent interval check: binary reduction, 128 atanh terms and a
# 28-term exponential, with outward dyadic rounding at 256 bits.
DYAD=1<<256
down=lambda x: Q((x*DYAD).__floor__(),DYAD)
up=lambda x: Q((x*DYAD).__ceil__(),DYAD)
def unitlog(x):
    z=(x-1)/(x+1); lo=2*sum((z**(2*j+1)/Q(2*j+1) for j in range(128)),Q(0))
    return lo,lo+2*z**257/(257*(1-z*z))
@lru_cache(None)
def logarithm(x):
    k=0
    while x>2: x/=2; k+=1
    lo,hi=unitlog(x); l2,h2=unitlog(Q(2))
    return down(lo+k*l2),up(hi+k*h2)
def exponential(x):
    assert 0<=x<1
    term=total=Q(1)
    for j in range(1,29): term*=x/j; total+=term
    return down(total),up(total+term*x/29/(1-x/30))
def moment(profile,dimension,width,saving):
    lo=hi=Q(0)
    fallback=Q(146478*sum(profile.values())*2*dimension**3,2**128) if dimension==78 else Q(32*dimension**2*sum(profile.values()),10**16)
    entries=list(profile.items())+[(1,fallback)]
    for rank,count in entries:
        l,h=logarithm(Q(dimension,rank));weight=Q(rank,dimension*width)*count
        lo+=weight*exponential(saving*l)[0];hi+=weight*exponential(saving*h)[1]
    return down(lo),up(hi)
intervals={}
for name,profile,dim,width,endpoint,step in [('bit',p,m,w,Q(result['bit_lower']),Q(1,10**24)),('complex',pc,mc,wc,Q(result['complex_lower']),Q(1,10**18))]:
    lower=moment(profile,dim,width,endpoint);upper=moment(profile,dim,width,endpoint+step)
    assert lower[1]<1<upper[0]
    intervals[name]={'lower':str(endpoint),'upper':str(endpoint+step),'lower_margin':str(1-lower[1]),'upper_margin':str(upper[0]-1)}

# Recompute the six bootstrap steps and strict lattice cutoff directly, and
# verify every supplied exact outer slack is positive.
eta=beta=Q(1,10**18); grid=eta
s=min(Q(result['bit_lower']),(1-beta)*Q(result['complex_lower']))-Q(1,10**24)
chain=[Q(384599,10**10)]
for saved in result['bootstrap']:
    old=chain[-1]; new=(1-s)*s+s*old
    gap=min(s-new,1-new-s,1-new-s*(1-old),1-s)
    cutoff=max((36/gap**2).__ceil__(),(2*(4+2432)/gap).__ceil__())
    assert Q(saved['gap'])==gap and int(saved['normalized_local_cutoff_log2'])==cutoff
    assert old<new<s and gap>0;chain.append(new)
assert len(chain)==7
assert result['normalized_local_coefficient_bits']==2432
assert len(result['bootstrap_routing_contract'])==6
# Algebraic identities certify every finite B_GL>=0, without assigning an
# unproved numerical value to the inherited fixed-routing constant.
for item,saved in zip(result['bootstrap_routing_contract'],result['bootstrap']):
    gap=Q(item['gap']);offset=Q(item['affine_offset']);slope=Q(item['affine_slope']);quad=Q(item['quadratic_threshold'])
    assert gap==Q(saved['gap'])>0
    assert slope*gap==2 and offset*gap==2*(4+2432) and quad*gap**2==36
    assert max(quad.__ceil__(),offset.__ceil__())==int(saved['normalized_local_cutoff_log2'])

q=chain[-1]*(1-2*eta);minimum=(1-eta)*q/(1+q)
k=grid*(((minimum/grid).numerator-1)//(minimum/grid).denominator)
assert k==Q(result['kappa'])<minimum<=k+grid
assert len(result['strict_outer_constraints'])==47
assert all(Q(x)>0 for x in result['strict_outer_constraints'].values())
assert set(result['outer_controls'])=={'next_grid','zero_eta','zero_beta','unit_beta'}

expected=read(ROOT/'source/EXPECTED.json')
assert Q(result['kappa'])==Q('80976604882529/62500000000000000')>Q(expected['kappa'])
assert result['bit_template_sha256']==g['template_sha256']
source_raw=gzip.decompress((BIT/'ORTHOGONAL-SOURCE-TEMPLATE.json.gz').read_bytes())
assert hashlib.sha256(source_raw).hexdigest()==expected['bit_template_sha256']==g['source_orthogonal_template_sha256']
source_template=json.loads(source_raw)
gl_template=json.loads(gzip.decompress((BIT/'GLOBAL-TEMPLATE.json.gz').read_bytes()))
assert gl_template['cover'].startswith('GL_78(') and 'split-idempotent' in gl_template.pop('cover_variant')
gl_template['cover']=source_template['cover']
assert gl_template==source_template  # actual complete instructions/profile/owners unchanged
# Fresh complex bytes may vary only by source binding hashes across platforms;
# its complete operator identity is replayed by the enclosing verifier.
assert result['complex_template_sha256']==c['template_sha256']
inputs=[BIT/x for x in ['GLOBAL.json','AUDIT.json','GLOBAL-TEMPLATE.json.gz','GEOMETRY.json']]+[CX/x for x in ['GLOBAL.json','AUDIT.json','GLOBAL-TEMPLATE.json.gz']]
report=dict(status='PASS_INDEPENDENT_GL_SHARP_FINITE_INVOICE_AND_EXACT_ASSEMBLY',kappa=str(k),
            bit_line_items={k:str(v) for k,v in parts.items()},complex_line_items=cxparts,
            exact_moment_intervals=intervals,outer_constraints_positive=47,next_grid_rejected=True,
            symbolic_GL_cutoff_checks=6,normalized_local_coefficient_bits=2432,total_coefficient_bits='2432+B_GL for arbitrary finite nonnegative B_GL',bit_row=bit_row,complex_row=20161,external_row_allowance=bit_row,complex_fractional_row_margin=str(row_margin),
            input_sha256={('bit/' if z.parent==BIT else 'complex/')+z.name:sha(z) for z in inputs},
            result_sha256=sha(Path(sys.argv[3])),
            scope='Explicit GL78 cover for the bit supplier. Whole-owner injection and complete source programs are proved by the companion replay; inherited all-size compilation and analytic contracts remain conditional.')
Path(sys.argv[4]).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['status','kappa','bit_row','complex_row','external_row_allowance']},indent=2))

"""Independent, narrowly frozen H6 invoice reconstruction; not upstream source.

Model and outward series: Dominik Scholz / PR606 and inherited PR598.
New exact twelve-case audit for Andrey Mas by ChatGPT.
All scientific targets are explicit; no upstream default or stage scan.
"""
from fractions import Fraction as F
from functools import lru_cache
from math import isqrt, expm1, log, floor

SCALE = 10**18
ROUND = 10**40
N, H, HIST, DATA, HP = 30960,17,{17:256,15:560},[16],[1,7,8,1]
TARGETS = (
 ('author_PR890', F('0.001661957775'), (80558,89683,80753)),
 ('retained_PR890', F(1661957774647029,10**18), None),
 ('selected_pinned', F(836330098538459,500000000000000000), None),
 ('author_PR1424', F('0.001676855229071321'), (79617,88409,79399)),
)

def require(test, message):
    if not test: raise ValueError(message)

def ln_bounds(value, terms=24):
    value=F(value)
    require(value>=1,'log argument')
    e=0
    while value>=2:
        value/=2; e+=1
    def unit(x):
        z=(x-1)/(x+1); z2=z*z; p=z; total=F(0)
        for j in range(terms):
            total+=p/(2*j+1); p*=z2
        return 2*total,2*total+2*p/((2*terms+1)*(1-z2))
    l,h=unit(value); l2,h2=unit(F(2))
    return l+e*l2,h+e*h2

def exp_bounds(lo,hi,terms=12):
    require(0<=lo<=hi<1,'exp argument')
    def series(x):
        t=s=F(1)
        for j in range(1,terms+1): t*=x/j; s+=t
        return s,t
    lower,_=series(lo); upper,last=series(hi)
    return lower,upper+last*hi/(terms+1)/(1-hi/(terms+2))

def round_out(lo,hi,scale=ROUND):
    return F(lo.numerator*scale//lo.denominator,scale),F(-((-hi.numerator*scale)//hi.denominator),scale)

@lru_cache(None)
def logarithm(base): return round_out(*ln_bounds(base))

@lru_cache(None)
def powers(base,a):
    lo,hi=logarithm(base)
    return round_out(*exp_bounds(a*lo,a*hi))

def row(L,R=0):
    require(type(L) is int and L in (3,5,7),'frozen L')
    require(type(R) is int and R>=0,'nonnegative integer R')
    m=16*L+1; q,p=divmod(m,17); cap=isqrt((m*m-1)//2)
    # Lists of actual idle ranks for exactly these stages, before any splitting.
    idle={3:[],5:[32,32,16],7:[64,32,16,32,64,16]}[L]
    require(all(x<=cap for x in idle),'frozen idle ranks need no split')
    terms=[(F(2*N*L*16),F(m,16)),(F(L*17*256),F(m,17)),(F(L*15*560),F(m,15))]
    terms += [(F(2*N*x),F(m,x)) for x in idle]
    unit=[(F(L*x),F(m,x)) for x in HP]+[(F(L*p,q),F(m,p))]
    W0=(L-1)*N; D=W0-L*12752
    require(sum(x for x,_ in terms)==m*W0-D,'base mass')
    require(sum(x for x,_ in unit)==F(m*L,q),'helper mass')
    terms += [(R*x,b) for x,b in unit]
    W=F(W0)+F(L*R,q)
    require(sum(x for x,_ in terms)==m*W-D,'total mass')
    require(all(m/b<=cap for _,b in terms),'child cap')
    return dict(L=L,m=m,q=q,p=p,cap=cap,idle=idle,D=D,W=W,terms=terms,unit=unit)

def pressure_terms(terms,a):
    l=h=F(0)
    for mass,base in terms:
        pl,ph=powers(base,a); l+=mass*(pl-1); h+=mass*(ph-1)
    return l,h

def pressure(r,a): return pressure_terms(r['terms'],a)

def boundary(L,t):
    r=row(L); a=t/(1-t); lo,hi=pressure(r,a); ul,uh=pressure_terms(r['unit'],a)
    require(0<ul<=uh,'positive unit pressure')
    xlo=(r['D']-hi)/uh; xhi=(r['D']-lo)/ul
    R=xlo.numerator//xlo.denominator
    require(R>=0 and R<xlo<=xhi<R+1,'strict unambiguous integer threshold')
    return R,xlo,xhi

def invoice(L,R):
    r=row(L,R)
    # This is a reconstruction of the upstream floating nomination, not an
    # exact sign certificate; both resulting endpoints are checked below.
    lo,hi=0.,.02
    for _ in range(60):
        a=(lo+hi)/2
        p=sum(mass*expm1(a*log(float(base))) for mass,base in r['terms'])
        if p<r['D']:lo=a
        else:hi=a
    z=floor(lo*10**15); al=F(z-2,10**15); ah=F(z+3,10**15)
    require(pressure(r,al)[1]<r['D']<pressure(r,ah)[0],'certified root bracket')
    kl=al/(1+al); kh=ah/(1+ah)
    endpoints=[kl.numerator*SCALE//kl.denominator,-((-kh.numerator*SCALE)//kh.denominator)]
    return endpoints,al,ah


def strict_allowance(xlo, xhi):
    """Do not resolve an integer equality or a straddled boundary by flooring."""
    require(0 <= xlo <= xhi, 'nonnegative allowance enclosure')
    R = xlo.numerator // xlo.denominator
    require(R < xlo <= xhi < R + 1, 'strict allowance unresolved at integer boundary')
    return R


def exact_grid_certificate(r, z):
    """Prove z=floor(10^15 * true alpha), without a floating sign test."""
    require(type(z) is int and z > 2, 'positive alpha grid index')
    gl, gh = F(z, 10**15), F(z+1, 10**15)
    require(pressure(r, gl)[1] < r['D'] < pressure(r, gh)[0],
            'exact alpha grid cell does not bracket root')
    return gl, gh


def scaled_interval(al, ah):
    kl, kh = al/(1+al), ah/(1+ah)
    return [kl.numerator*SCALE//kl.denominator,
            -((-kh.numerator*SCALE)//kh.denominator)]


def validate_mass_cap(r):
    require(sum(mass for mass, _ in r['terms']) == r['m']*r['W']-r['D'],
            'complete mass identity')
    require(all(mass >= 0 and 0 < r['m']/base <= r['cap']
                for mass, base in r['terms']), 'positive capped children')


def encode_interval(pair):
    return [str(pair[0]), str(pair[1])]


def boundary_record(L, target):
    """Exact target-pressure evidence, no nomination or source execution."""
    R, xl, xh = boundary(L, target)
    require(strict_allowance(xl, xh) == R, 'strict threshold guard')
    r0, r1 = row(L, R), row(L, R+1)
    a = target/(1-target)
    p0, p1 = pressure(r0, a), pressure(r1, a)
    require(p0[1] < r0['D'] < p1[0], 'adjacent strict pressure signs')
    return {
        'R': R,
        'alpha_target': str(a),
        'real_helper_boundary': encode_interval((xl, xh)),
        'pressure_at_R': encode_interval(p0),
        'pressure_at_R_plus_1': encode_interval(p1),
        'positive_pressure_margin_at_R': str(r0['D']-p0[1]),
        'positive_pressure_excess_at_R_plus_1': str(p1[0]-r0['D']),
        'budget_ratio_n_over_R': str(F(N, R)),
    }


def invoice_record(L, R, z):
    """Canonical invoice evidence from a supplied, exactly proved grid cell."""
    r = row(L, R)
    validate_mass_cap(r)
    gl, gh = exact_grid_certificate(r, z)
    al, ah = F(z-2, 10**15), F(z+3, 10**15)
    pl, ph = pressure(r, al), pressure(r, ah)
    require(pl[1] < r['D'] < ph[0], 'invoice bracket signs')
    return {
        'R': R, 'z': z,
        'alpha_grid_cell': encode_interval((gl, gh)),
        'alpha_bracket': encode_interval((al, ah)),
        'scaled_kappa_interval': scaled_interval(al, ah),
        'stock': str(r['W']),
        'rank_mass': str(sum(x for x, _ in r['terms'])),
        'pressure_at_alpha_lower': encode_interval(pl),
        'pressure_at_alpha_upper': encode_interval(ph),
        'positive_lower_bracket_margin': str(r['D']-pl[1]),
        'positive_upper_bracket_margin': str(ph[0]-r['D']),
        'max_child_rank': max(int(r['m']/b) for _, b in r['terms']),
    }


def skeleton_record(L):
    r = row(L)
    base = r['terms'][:-len(r['unit'])]
    def child(mass, b):
        rank = r['m']/b
        require(rank.denominator == 1, 'integer child rank')
        return {'rank': int(rank), 'mass': str(mass),
                'count': str(mass/rank), 'base_m_over_rank': str(b)}
    return {
        'L': L, 'm': r['m'], 'q': r['q'], 'pad': r['p'], 'cap': r['cap'],
        'stock_before_helpers': str(r['W']), 'deficit': r['D'],
        'idle_ranks': r['idle'], 'center_bill': 12752,
        'base_children': [child(x,b) for x,b in base],
        'unit_helper_children': [child(x,b) for x,b in r['unit']],
    }

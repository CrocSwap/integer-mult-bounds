#!/usr/bin/env python3
"""Independently check a frozen two-tier signed price and recurring clock.

Uses only exact rational/integer arithmetic and outward dyadic square roots;
does not import the candidate's invoice, receipt, or numerical code. The
frozen grade tables are source-bound inputs, not a proof of physical action.
"""
from argparse import ArgumentParser
from collections import defaultdict
from decimal import Decimal, localcontext
from fractions import Fraction as F
from hashlib import sha256
import json
from math import isqrt
from pathlib import Path
import sys

ap = ArgumentParser()
ap.add_argument('--inputs', type=Path, default=Path(__file__).with_name('frozen-inputs.json'))
ap.add_argument('--expected-result', type=Path, required=True)
args = ap.parse_args()
if sys.version_info[:2] != (3, 12):
    raise SystemExit('Use CPython 3.12 with assertions enabled')
if not __debug__:
    raise SystemExit('Assertions must be enabled')
data = json.loads(args.inputs.read_bytes())
expected_bytes = args.expected_result.read_bytes()
assert sha256(expected_bytes).hexdigest() == data['source']['expected_result_sha256']
expected = json.loads(expected_bytes)
S = 1 << 192

def ceilfrac(x):
    return -(-x.numerator // x.denominator)

def pow_interval(base, exponent):
    """192-bit directed enclosure of a positive rational to a dyadic power."""
    base, exponent = F(base), F(exponent)
    assert base > 0 and 0 <= exponent < 1 and exponent.denominator.bit_count() == 1
    lower = (base * S).__floor__()
    upper = ceilfrac(base * S)
    plo = phi = S
    for bit in range(exponent.denominator.bit_length() - 2, -1, -1):
        lower = isqrt(lower * S)
        upper = 1 + isqrt(upper * S - 1)
        if exponent.numerator >> bit & 1:
            plo = plo * lower // S
            phi = -(-phi * upper // S)
    return F(plo, S), F(phi, S)

def qtext(x):
    with localcontext() as ctx:
        ctx.prec = 32
        return {'fraction': str(x), 'decimal': str(Decimal(x.numerator) / Decimal(x.denominator))}

def unpack(book):
    targets = {F(k): int(v) for k, v in book['targets']}
    paid = {F(k): int(v) for k, v in book['paid']}
    cells = {(F(r), F(k)): F(q) for r, k, q in book['cells']}
    assert len(targets) == len(book['targets']) and len(paid) == len(book['paid'])
    assert len(cells) == len(book['cells'])
    return targets, paid, cells

def funding(book):
    targets, paid, cells = unpack(book)
    c = F(book['trial'])
    target_power = {k: pow_interval(k, 1-c) for k in targets}
    paid_power = {r: pow_interval(r, 1-c) for r in paid}
    total_t = sum(n * target_power[k][0] for k, n in targets.items())
    total_p = sum(n * paid_power[r][1] for r, n in paid.items())
    assert total_t > total_p
    rows = defaultdict(F)
    columns = defaultdict(F)
    for (r, k), q in cells.items():
        assert r in paid and k in targets and q > 0 and 5*r <= 4*k
        rows[r] += q
        columns[k] += paid[r] * paid_power[r][1] * q
    assert set(rows) == set(paid) and all(v == 1 for v in rows.values())
    assert all(0 < columns[k] <= targets[k] * target_power[k][0] for k in targets)
    return {'targets': targets, 'paid': paid, 'cells': cells, 'trial': c,
            'margin': (total_t-total_p)/total_t}

o = funding(data['ordinary'])
g = funding(data['gaussian'])
assert len(o['cells']) == 24 and len(g['cells']) == 51
assert sum(o['targets'].values()) == 18906 and sum(o['paid'].values()) == 104652
assert sum(g['targets'].values()) == 23989248 and sum(g['paid'].values()) == 128290608
assert data['gaussian']['typed_counts'] == [282336, 281328]
assert o['trial'] == F(4391986206293, 2**50)
assert g['trial'] == F(17158764376, 2**42)

# Ordinary finite factor includes the original 256/255 reserve and 47/20 tariff.
delta = F(1, 2**128)
L = data['ordinary']['level_floor']
assert L == 18960 and F(data['ordinary']['debit']) == F(11239,8192)
base = 1024 * 134 * L
olow, ohigh = pow_interval(base, o['trial'])
common = (F(47,20)*F(256,255)*F(4097,4096)*F(1028,1024)
          * (1+F(64,L)+delta) / ((1-F(10,L))*(1-delta)**3))
ordinary_lo, ordinary_hi = common*olow, common*ohigh
ordinary_allowance_lo = 2*pow_interval(2,F(3047,8192))[0]
assert ordinary_hi < ordinary_allowance_lo
assert F(75,32)/F(47,20) == F(375,376)

# Independent 51-cell Gaussian finite factor, with outward powers and
# directed lower/upper edge slope bounds.
ct = g['trial']
psi_lo = psi_hi = F(0)
for (r,k), q in g['cells'].items():
    lo, hi = pow_interval(k/r, ct)
    weight = g['paid'][r] * q * r
    psi_lo += weight * (lo-1)/ct
    psi_hi += weight * (hi-1)/ct
assert 0 < psi_lo <= psi_hi
axes = sum(k*n for k,n in g['targets'].items())
assert axes == 677246016
gl = data['gaussian']['level_floor']
scale = data['gaussian']['upper_divisor'] * data['gaussian']['ambient'] // 2
assert (gl,scale) == (1874,263772)
fringe_hi = 10*axes/((1-ct)*psi_lo)
fringe_lo = 10*axes/((1-ct)*psi_hi)
plo, phi = pow_interval(scale*gl,ct)
gcommon = (1+delta)*(1+F(4*data['gaussian']['largest_target'],scale))/(1-delta)**4
gaussian_lo = gcommon*plo*(1+fringe_lo/gl+delta)
gaussian_hi = gcommon*phi*(1+fringe_hi/gl+delta)
gdebit = F(data['gaussian']['debit'])
assert gdebit == F(1039776,2**23) == F(32493,262144)
allowance = pow_interval(2,gdebit)
finer = pow_interval(2,F(1039775,2**23))
assert gaussian_hi < allowance[0] and gaussian_lo > finer[1]

def signed_margins(k, g, ordinary, positive):
    a,b,q = k+4*g, k+5*g, k+3*g
    ep,be = 1-g, 1-3*g
    sigma,tau = 1-b, 1-a
    internal = tau+(1-g)*max(sigma-tau,0)
    leaf = sigma+g*(1-sigma)
    lam = 1-(q+a)/2
    xi = ep*(1+q)-F(3,32)+g
    key = be+1-ep
    powers = [ep*q,a,1-ep+q*be,1-ep+a*be,1-ep+be,F(3,32)+xi-ep,
              xi+F(1,2)-ep,ep,1-(ep+be+48-128+2)]
    strict = [ordinary-a,b-a,q,b-q,a-q,g,1-g,(1-g)*b-a,1-internal-q,1-leaf-q,
              lam-tau,lam-sigma,lam-internal,1-q-lam,1-q-leaf,ep,1-ep,xi-F(1,2),ep-xi,
              be,ep-be,1-be,1-(2*xi-2)-g/10-be,1-(2*xi-2)-be,1-ep-g/10,1-ep,
              g/10,1-key,1-be-2*(1-ep),128-48-be,g,ep-a,F(1,32)-b,F(2**45-7**16),
              F(2),2-xi,F(5),1-be,1-be,1-ep,powers[2]-powers[0],g,
              k-F('.001730970419199163702738'),1-ep,F(11,2)] + [x-k for x in powers]
    functional = [1-be,be*(1-F(3,1000)),128-48-ep-be-1,be*(1-F(1,250))]
    assert len(strict) == 54 and len(functional) == 4
    assert min(*strict,*functional,positive-b) > 0
    return {'strict':len(strict), 'functional':len(functional),
            'smallest_margin':str(min(*strict,*functional,positive-b)),
            'ordinary_margin':str(ordinary-a), 'positive_margin':str(positive-b)}

def stages(profile):
    heights = profile['ordinary_heights']
    k, eta = F(profile['kappa']), F(profile['eta'])
    stop = F(1,profile['stop_denominator'])
    book = k + 5*stop
    assert F(1,250) > eta > book
    previous = F(0)
    out = []
    for i,h in enumerate(heights):
        upper = min(eta, (249*(o['trial']-F(11239,8192*h))+previous)/250)
        chosen = book if i+1 == len(heights) else F((upper*10**21).__floor__()-1,10**21)
        assert previous < chosen < upper
        out.append({'height':h,'booked':str(chosen),'upper':str(upper),'slack':str(upper-chosen)})
        previous = chosen
    positive = ct-gdebit/profile['gaussian_height']
    signed = signed_margins(k,stop,book,positive)
    return out,positive,signed

def ceil_log2(n):
    assert n > 0
    return (n-1).bit_length()

def cuts(heights):
    out=[]
    for h in heights:
        minimum = -(-250*(h+64)//249)
        out.append(max(minimum, h+out[-1]+64 if out else 0))
    return out

def activation(last, h):
    goal=last+h+102
    s=max(512,goal)
    while s < goal+7*ceil_log2(s):
        s=goal+7*ceil_log2(s)
    q=ceil_log2(s)
    if (1<<q)+1 < goal+7*(q+1):
        s=goal+7*(q+1)
    return s-1

profiles={}
for name in ('entry','terminal'):
    p=data[name]
    rows,positive,signed=stages(p)
    record=expected[name]
    assert p['ordinary_heights']==record['ordinary_H'] and p['gaussian_height']==record['numerical_H']
    assert F(p['kappa'])==F(record['kappa'])
    assert [F(x['booked']) for x in rows] == [F(x) for x in record['ordinary_rates']]
    assert positive==F(record['gaussian_rate']) and signed==record['signed']
    assert rows == record['ordinary_stage_bounds']
    cs=cuts(p['ordinary_heights'])
    A=activation(cs[-1],p['gaussian_height'])
    offset=(-pow(2,A,6))%6
    assert cs==record['stock']['binary_cuts'] and A==record['stock']['public_exponent_A']
    assert offset==record['stock']['first_public_offset']
    profiles[name]={'stages':rows,'gaussian_rate':str(positive),'signed':signed,
                    'cuts':cs,'activation_exponent':A,'first_header_offset':offset}

entry,terminal=data['entry'],data['terminal']
assert F(terminal['kappa']) == F(39,10000)
assert terminal['ordinary_heights'] == [8192,106000,1681001] and terminal['gaussian_height']==85406
assert F(terminal['eta']) == F(1,256) and data['ordinary']['level_floor']==18960
entry_B=40+22+16384*sum(entry['ordinary_heights'])+25818582
terminal_B=137+320*sum(terminal['ordinary_heights'])
entry_C=max(84500001,1602+220*entry['gaussian_height']+entry_B)
terminal_C=max(84500001,1602+220*terminal['gaussian_height']+terminal_B)
premium=ceilfrac((F(terminal['kappa'])-F(entry['kappa']))*profiles['terminal']['activation_exponent'])
complete=1+max(entry_C+premium,terminal_C)
assert (entry_B,entry_C,terminal_B,terminal_C,premium,complete)==(125433364,125660246,574461897,593252819,847,593252820)
assert expected['entry']['log2_B']==entry_B and expected['entry']['log2_C']==entry_C
assert expected['terminal']['log2_B']==terminal_B and expected['terminal']['log2_C']==terminal_C
assert expected['entry_conversion_bits']==premium and expected['complete_log2_C']==complete

book=F(terminal['kappa'])+F(5,terminal['stop_denominator'])
prior=F(profiles['terminal']['stages'][-2]['booked'])
last_below=(249*(o['trial']-F(11239,8192*(terminal['ordinary_heights'][-1]-1)))+prior)/250
g_prev=ct-gdebit/(terminal['gaussian_height']-1)
assert last_below <= book and g_prev <= book
assert g_prev-book == F(expected['G_minus_one_positive_margin'])
old_positive=F(17145637307,2**42)-F(64939,524288*terminal['gaussian_height'])
assert old_positive < book and old_positive-book == F(expected['old_word_positive_margin'])

report={'status':'PASS_INDEPENDENT_FROZEN_TWO_TIER_BILL',
        'source_head':data['source']['head'], 'input_sha256':sha256(args.inputs.read_bytes()).hexdigest(),
        'expected_result_sha256':sha256(expected_bytes).hexdigest(),
        'ordinary_transport_margin':qtext(o['margin']), 'gaussian_transport_margin':qtext(g['margin']),
        'ordinary_factor_upper':qtext(ordinary_hi), 'ordinary_allowance_lower':qtext(ordinary_allowance_lo),
        'gaussian_factor_upper':qtext(gaussian_hi), 'gaussian_allowance_lower':qtext(allowance[0]),
        'gaussian_finer_tick_rejected':True, 'profile':profiles,
        'entry_log2_B':entry_B,'entry_log2_C':entry_C,'terminal_log2_B':terminal_B,
        'terminal_log2_C':terminal_C,'entry_conversion_bits':premium,'complete_recurring_log2_C':complete,
        'negative_controls':{'last_ordinary_height_minus_one_unfunded':True,
                             'gaussian_height_minus_one_unfunded':True,'old_word_unfunded':True},
        'scope':'Exact funding, finite-price arithmetic and clock with supplied source-bound inputs; physical contracts and fixed setup remain separate.',
        'conditional_cost_form':'T(n) <= F_target + 2^593252820 n (1+log2 n)^(1-39/10000)'}
print(json.dumps(report,sort_keys=True),flush=True)

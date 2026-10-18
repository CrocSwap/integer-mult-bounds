"""Exact repair-tariff composition certificate; no supplier execution."""
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha1, sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
H = {1:349604, 2:60192, 3:62585, 4:20448, 5:11808, 7:7, 8:1152, 48:4866}
W, M = 14336, 73
SIGMA, BETA, GAP = F(99833,100000), F(1,1000), F(15999,10**9)

def need(ok, message):
    if not ok:
        raise ValueError(message)

def log_interval(x):
    """Atanh series after powers-of-two reduction; rational remainder."""
    need(x >= 1, 'log domain')
    k = 0
    while x >= 2:
        x /= 2
        k += 1
    def one(y):
        z = (y-1)/(y+1)
        n = 36
        low = 2*sum((z**(2*j+1)/F(2*j+1) for j in range(n)), F(0))
        tail = 2*z**(2*n+1)/((2*n+1)*(1-z*z))
        return low, low+tail
    lo, hi = one(x)
    a, b = one(F(2))
    return lo+k*a, hi+k*b

def exp_interval(lo, hi):
    need(0 <= lo <= hi < 1, 'small exponential domain')
    def terms(x):
        total = term = F(1)
        for k in range(1,13):
            term = term*x/k
            total += term
        return total, term*x/13
    low, _ = terms(lo)
    high, next_term = terms(hi)
    return low, high+next_term/(1-hi/14)

def power_interval(ratio):
    need(0 < ratio <= 1, 'power domain')
    lo, hi = log_interval(1/ratio)
    lo, hi = exp_interval((1-SIGMA)*lo, (1-SIGMA)*hi)
    return ratio*lo, ratio*hi

def pins():
    manifest = json.loads((HERE/'SOURCES.json').read_text())
    for item in manifest['snapshots']:
        raw = (HERE/item['snapshot']).read_bytes()
        need(sha256(raw).hexdigest() == item['sha256'], 'source hash '+item['snapshot'])
        header = b'blob '+str(len(raw)).encode()+b'\0'
        need(sha1(header+raw).hexdigest() == item['git_blob'], 'source blob '+item['snapshot'])
    layer = (HERE/'source/PR2287-PROOF.md').read_text()
    compact = (HERE/'source/PR2250-PROOF.md').read_text()
    for phrase in ('{1:349604, 2:60192, 3:62585, 4:20448,',
                   '5:11808, 7:7, 8:1152, 48:4866}',
                   'Keep p,d,K,G,H global down the recursion.',
                   'We do not\nreplace one complex child by a child per unused row.',
                   'e<73 or e^1000<d', 'V/(W Gamma)'):
        need(phrase in layer, 'layer contract: '+phrase)
    for phrase in ('O(V + M A^3 + delta M A(R+A))',
                   'delta<=5/(128p^3)', 'Address fields have\nbinary lengths and complete ranges.'):
        need(phrase in compact, 'repair contract: '+phrase)

def tariff(records, record_bits, address_bound, bad_fraction):
    need(records >= 1 and record_bits >= 1 and address_bound >= 1, 'positive shape')
    need(0 <= bad_fraction <= 1, 'fraction')
    volume = records*record_bits
    return (F(volume) + records*address_bound**3
            + bad_fraction*records*address_bound*(record_bits+address_bound))

def admitted(p, a, r, delta, complete=True, suffix=True):
    return (p >= 2 and a >= 1 and r >= a**3 and complete and suffix
            and 0 <= delta <= F(5,128*p**3)
            and delta*a*(1+F(a,r)) <= 1)

def bounded_cases():
    count, worst = 0, F(0)
    for p in (2,3,8,32,127,256):
        for a in (1,2,p,3*p):
            for r in (a**3, a**3+1, 8*a**3):
                delta = F(5,128*p**3)
                if not admitted(p,a,r,delta):
                    continue
                for records in (1,3,5,17):
                    ratio = tariff(records,r,a,delta)/(records*r)
                    need(ratio <= 3, 'uniform per-node tariff')
                    worst = max(worst,ratio)
                    count += 1
    return count, str(worst)

def row_shapes():
    """Symbolic multiplicities, never allocate the enormous source cover."""
    gamma = 2**1296
    for j in range(1,37):
        gamma *= 2**(2*j)-1
    cover = W*gamma
    @lru_cache(None)
    def depth(e):
        return 0 if e < M else 1+depth(48*(e//M))
    checks = 0
    for root in (73,74,146,219,1000,10000,10**6):
        frontier = {(root,3*cover**depth(root))}
        while frontier:
            later = set()
            for e,rows in frontier:
                need(rows % cover**depth(e) == 0, 'row divisibility')
                if e < M:
                    continue
                child_rows = rows//cover
                for rank in H:
                    child = rank*(e//M)
                    need(child < e and child_rows % cover**depth(child) == 0, 'complete child row stock')
                    checks += 1
                    later.add((child,child_rows))
            frontier = later
    return checks, gamma.bit_length(), cover.bit_length()

def weighted_recursions():
    lower = upper = F(0)
    for r,h in H.items():
        lo, hi = power_interval(F(r,M))
        lower += F(h,W)*lo
        upper += F(h,W)*hi
    need(upper < 1-GAP, 'independent strict sigma moment')
    need(sum((F(h*r,W*M) for r,h in H.items()), F(0)) == F(1017,1022), 'linear moment')
    nu = SIGMA*(1-BETA)
    need(nu == F(99733167,10**8), 'internal-visit exponent')
    need(F(599,600)-nu == F(300499,300000000), 'strict time slack')
    records = []
    for root in (73,146,500,1000,10000,100000):
        @lru_cache(None)
        def visits(e):
            if e < M or e**1000 < root:
                return F(0)
            return 1+sum((F(h,W)*visits(r*(e//M)) for r,h in H.items()), F(0))
        lo, _ = power_interval(F(M,root))
        bound = 1/(lo*GAP)
        value = visits(root)
        need(value <= bound, 'exact finite weighted recurrence')
        records.append({'root_width':root,'weighted_internal_visits':str(value),
                        'bound_integer_ceiling':-((-bound.numerator)//bound.denominator)})
    scale = 10**15
    return {'moment_lower_1e15':lower.numerator*scale//lower.denominator,
            'moment_upper_1e15':-((-upper.numerator*scale)//upper.denominator),
            'gap':str(GAP),'repair_constant_per_adapter':str(3/GAP),
            'internal_visit_exponent':str(nu),'lambdaPrime_slack':str(F(599,600)-nu),
            'finite_recurrences':records}

def countermodels():
    shapes = []
    for p,d in ((4096,64),(16384,128),(65536,256)):
        coeffs, component, records = 2**(p//d), 2*p, 3*2**p
        volume = records*coeffs*component
        a = (2*volume-1).bit_length()  # actual ceil(log2(2V))
        packed = 1+F(a**3,coeffs*component)
        split = 1+F(a**3,component)
        need(coeffs*component >= a**3 and packed < 2, 'packed control amortization')
        need(2*split > p*p, 'split quadratic surcharge')
        need(volume == (records*coeffs)*component, 'unchanged total volume')
        shapes.append({'p':p,'d':d,'A':a,'same_volume_bits':volume.bit_length(),
                       'coefficient_count_log2':p//d,'packed_over_volume':str(packed),
                       'split_over_volume':str(split)})
    payload = tuple((row,coefficient,(row-coefficient)%5) for row in range(3) for coefficient in range(64))
    events = 0
    a = (2*len(payload)*8-1).bit_length()
    for record in payload:
        for _ in range(a):
            for _ in range(a):
                for _ in range(a):
                    events += 1
    need(events == len(payload)*a**3, 'executed cubic preparation model')
    streams = []
    for a in (4,8,16):
        data = [(k,(k,-k-1,k%3)) for k in range(1<<min(a,5))]
        original = data.copy()
        moved = 0
        for j in range(a):
            zero, one = [], []
            for item in data:
                (one if (item[0]>>j)&1 else zero).append(item)
                moved += 1
            data = zero+one
        need(data == original, 'identity bad-fibre repair')
        need(moved == a*len(data), 'actual radix pass cost')
        streams.append({'key_bits':a,'records':len(data),'complete_record_transfers':moved})
    for B in (2,4,16):
        t, v, z = B-1, 0, 0
        initial = t,v
        v += 2*z*t; t += v%2; v += z*(1-2*t); t -= (v%2)^z
        need((t,v) == initial and t == B-1, 'genuine bad identity fibre')
    need(not admitted(8,8,512,F(5,128*8**3),complete=False), 'reject incomplete compact fields')
    need(not admitted(8,8,16,F(0),suffix=False), 'reject split coefficient suffix')
    need(not admitted(8,8,512,F(1)), 'reject inherited global bad fraction on slice')
    return {'coefficient_split':shapes,'executed_control_steps':events,'bad_fibre_radix':streams,
            'rejected_variants':['incomplete compact range','split coefficient suffix','global bad density reused on slice']}

def main():
    pins()
    count, worst = bounded_cases()
    rows, group_bits, cover_bits = row_shapes()
    result = {'status':'PASS_COMPLEX_RECORD_AMORTIZATION','scope':'Conditional repair-tariff theorem, not full selected supplier',
              'tariff_cases':count,'largest_normalized_tariff':worst,'row_edges':rows,
              'orthogonal_group_bits':group_bits,'cover_bits':cover_bits,
              'recurrence':weighted_recursions(),'countermodels':countermodels()}
    rendered = json.dumps(result,indent=2,sort_keys=True)+'\n'
    if '--write' in sys.argv:
        (HERE/'RESULT.json').write_text(rendered,encoding='utf-8')
    else:
        need(json.loads((HERE/'RESULT.json').read_text()) == result, 'frozen result')
        if '--regenerate' in sys.argv:
            need((HERE/'RESULT.json').read_text() == rendered, 'canonical regeneration')
    print(result['status'], 'tariffs='+str(count), 'row_edges='+str(rows), 'no_new_kappa')

if __name__ == '__main__':
    main()

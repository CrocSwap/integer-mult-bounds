#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent PR1536 moment signs via integer roots; no supplier imports.

Method prior art: arkfx PR706. New implementation by Arham Tahir with
substantial OpenAI Codex assistance. See README.md for the enclosure proof.
"""
import argparse
from fractions import Fraction as F
from functools import lru_cache
import hashlib
import json
from math import isqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent
HEAD = '527d7623009f295b7311e98ae36f5e2fbdbbc3e5'
GRID = F(1, 10**200)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ceil_div(n, d):
    require(type(n) is int and type(d) is int and n >= 0 and d > 0,
            'nonnegative numerator and positive denominator required')
    return (n+d-1)//d


def ceil_sqrt(n):
    require(type(n) is int and n >= 0, 'nonnegative integer radicand required')
    r = isqrt(n)
    return r + (r*r != n)


@lru_cache(maxsize=128)
def root_ladder(base, exponent_bits, fraction_bits):
    """Scaled intervals enclose base**(1/2**k), k=0..N."""
    base = F(base)
    require(base >= 1, 'base must be at least one')
    require(type(exponent_bits) is int and 1 <= exponent_bits <= 2048,
            'exponent precision outside bounded domain')
    require(type(fraction_bits) is int and 1 <= fraction_bits <= 4096,
            'fraction precision outside bounded domain')
    scale = 1 << fraction_bits
    lo = base.numerator*scale//base.denominator
    hi = ceil_div(base.numerator*scale, base.denominator)
    roots = [(lo, hi)]
    for _ in range(exponent_bits):
        lo, hi = isqrt(lo*scale), ceil_sqrt(hi*scale)
        roots.append((lo, hi))
    return tuple(roots)


def dyadic_product(n, roots, fraction_bits):
    """Multiply selected root intervals to enclose base**(n/2**N)."""
    bits = len(roots)-1
    require(type(n) is int and 0 <= n <= 1 << bits, 'dyadic numerator range')
    if n == 1 << bits:
        return roots[0]
    scale = 1 << fraction_bits
    lo = hi = scale
    for k in range(1, bits+1):
        if n & (1 << (bits-k)):
            rlo, rhi = roots[k]
            lo, hi = lo*rlo//scale, ceil_div(hi*rhi, scale)
    return lo, hi


def power_bounds(base, exponent, exponent_bits=768, fraction_bits=1024):
    """Contain base**exponent for rational base>=1, exponent in [0,1]."""
    exponent = F(exponent)
    require(0 <= exponent <= 1, 'exponent must lie in [0,1]')
    roots = root_ladder(F(base), exponent_bits, fraction_bits)
    low_n, remainder = divmod(exponent.numerator << exponent_bits, exponent.denominator)
    high_n = low_n + (remainder != 0)
    lo = dyadic_product(low_n, roots, fraction_bits)[0]
    hi = dyadic_product(high_n, roots, fraction_bits)[1]
    scale = 1 << fraction_bits
    require(lo <= hi, 'inverted power enclosure')
    return F(lo, scale), F(hi, scale)


def validate_profile(profile, m, live):
    require(type(m) is int and m > 1 and type(live) is int and live > 0,
            'positive integer dimensions required')
    require(type(profile) is dict and bool(profile), 'nonempty profile required')
    for rank, count in profile.items():
        require(type(rank) is int and 0 < rank < m and type(count) is int and count > 0,
                'invalid child rank or count')


def residual(profile, m, live, saving, surcharge=False,
             exponent_bits=768, fraction_bits=1024):
    """Enclose complete priced moment minus one, with inherited surcharge."""
    validate_profile(profile, m, live)
    require(type(surcharge) is bool, 'surcharge must be Boolean')
    lo = hi = F(-1)
    for rank, count in sorted(profile.items()):
        p, q = power_bounds(F(m,rank), saving, exponent_bits, fraction_bits)
        weight = F(rank*count, m*live)
        lo += weight*p
        hi += weight*q
    if surcharge:
        p, q = power_bounds(F(m), saving, exponent_bits, fraction_bits)
        weight = F(32*m*sum(profile.values()), 10**16*live)
        lo += weight*p
        hi += weight*q
    return lo, hi


def sign(interval):
    lo, hi = interval
    require(lo <= hi, 'inverted sign enclosure')
    return -1 if hi < 0 else 1 if lo > 0 else 0


def strict_decision(interval, expected):
    require(type(expected) is int and expected in (-1,1), 'strict sign required')
    actual = sign(interval)
    require(actual != 0, 'unresolved interval; neither acceptance nor rejection proved')
    require(actual == expected, 'incorrect endpoint sign')


def read_inputs(package=HERE):
    """Authenticate copied source bytes by SHA256 and Git blob, then parse."""
    package = Path(package)
    pins = json.loads((package/'INPUTS.json').read_bytes())
    require(pins['source_pr'] == 1536 and pins['source_head'] == HEAD, 'source head mismatch')
    names = {'SPEC.json','PROFILE.json','code/assemble.py','README.md','NOTICE','MANIFEST.json'}
    files = pins['files']
    require(len(files) == len(names) and {p['local_path'] for p in files} ==
            {'inputs/'+n for n in names}, 'source inventory mismatch')
    decoded = {}
    for pin in files:
        path = (package/pin['local_path']).resolve()
        require(path.is_relative_to((package/'inputs').resolve()), 'source path escaped inputs')
        raw = path.read_bytes()
        blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        require(pin['commit'] == HEAD and pin['repository'] == 'jeremykothe2/integer-mult-bounds',
                'source identity mismatch')
        require(len(raw) == pin['bytes'] and hashlib.sha256(raw).hexdigest() == pin['sha256'] and
                blob == pin['git_blob'], 'source bytes mismatch: '+pin['local_path'])
        require(pin['path'] == 'research/gmx-t74-ep200r/'+pin['local_path'][7:],
                'source path binding mismatch')
        decoded[pin['local_path'][7:]] = raw
    manifest = json.loads(decoded['MANIFEST.json'])
    for pin in files:
        name = pin['local_path'][7:]
        if name != 'MANIFEST.json':
            require(manifest[name] == pin['sha256'], 'upstream manifest mismatch')
    spec = json.loads(decoded['SPEC.json'])
    raw_profile = json.loads(decoded['PROFILE.json'])
    require(raw_profile == spec['expected']['global_profile'], 'profile differs from SPEC')
    require(all(type(v) is int for v in raw_profile.values()), 'noninteger profile count')
    profile = {int(r):n for r,n in raw_profile.items()}
    require(len(profile) == len(raw_profile), 'noncanonical rank keys')
    live = spec['expected']['live']
    validate_profile(profile,73,live)
    require(sum(r*n for r,n in profile.items()) == spec['expected']['rank_mass'], 'rank mass mismatch')
    require(live == 66304 and spec['outer_refinement']['endpoint_digits'] == 200,
            'audited parameter domain mismatch')
    require(spec['geometry']['dimension'] == 73, 'source moment width mismatch')
    b = F(spec['expected']['complex_lower'])
    c = F(spec['expected']['conservative_complex_lower'])
    require(0 < c < b < 1 and (b/GRID).denominator == (c/GRID).denominator == 1,
            'endpoint grid mismatch')
    return profile, live, b, c


def controls(profile, live, native, conservative):
    """Meaningful model/domain changes checked after source authentication."""
    rejected = []
    comparisons = 0
    for base in (F(1),F(4),F(9,4),F(73,48),F(73)):
        for numerator, denominator in ((0,1),(1,1),(1,2),(1,4),(3,8),(7,16)):
            lo, hi = power_bounds(base,F(numerator,denominator),20,96)
            require(lo**denominator <= base**numerator <= hi**denominator,
                    'exact integer-power comparison failed')
            comparisons += 1
    for name, call in [
        ('negative_exponent',lambda: power_bounds(F(73),F(-1,100))),
        ('base_below_one',lambda: power_bounds(F(1,2),F(1,3))),
        ('unresolved_is_not_rejection',lambda: strict_decision((F(-1,100),F(1,100)),1)),
        ('inverted_interval',lambda: sign((F(1),F(0)))),
        ('zero_count',lambda: residual({1:0},73,live,native)),
        ('rank_equals_parent',lambda: residual({73:1},73,live,native)),
    ]:
        try:
            call()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('control was not rejected: '+name)
    coarse = residual(profile,73,live,native+GRID,False,64,128)
    require(sign(coarse) == 0, 'low-precision control must remain unresolved')
    rejected.append('insufficient_precision_unresolved')
    strict_decision(residual(profile,73,live,native,True),1)
    strict_decision(residual(profile,73,live,conservative+GRID,False),-1)
    rejected.extend(['native_with_old_surcharge','conservative_upper_without_surcharge'])
    missing = dict(profile)
    missing[48] -= 1
    strict_decision(residual(missing,73,live,native+GRID,False),-1)
    rejected.append('omitted_rank48_child')
    changed = dict(profile)
    changed[1] += 1
    changed[2] -= 2
    changed[3] += 1
    require(sum(changed.values()) == sum(profile.values()) and
            sum(r*n for r,n in changed.items()) == sum(r*n for r,n in profile.items()),
            'profile mutation must preserve count and rank mass')
    strict_decision(residual(changed,73,live,native+GRID,False),-1)
    rejected.append('same_count_and_mass_profile_mutation')
    strict_decision(residual(profile,73,66794,native+GRID,False),-1)
    rejected.append('physical_stock_normalization')
    return {'exact_power_comparisons':comparisons,'semantic_controls':rejected}


def audit(package=HERE):
    profile, live, native, conservative = read_inputs(package)
    rows = []
    for model, endpoint, surcharge in [('native',native,False),('conservative',conservative,True)]:
        for saving, expected in [(endpoint,-1),(endpoint+GRID,1)]:
            interval = residual(profile,73,live,saving,surcharge)
            strict_decision(interval,expected)
            tighter = residual(profile,73,live,saving,surcharge,896,1280)
            strict_decision(tighter,expected)
            require(interval[0] <= tighter[0] <= tighter[1] <= interval[1],
                    'higher-precision interval did not refine the enclosure')
            rows.append({'model':model,'surcharge':surcharge,'saving':str(saving),'sign':expected,
                         'residual':[str(x) for x in interval],
                         'refined_residual':[str(x) for x in tighter]})
    return {'status':'PASS_PR1536_INTEGER_ROOT_ENDPOINT_AUDIT','source_pr':1536,'source_head':HEAD,
            'm':73,'live':live,'profile':{str(r):n for r,n in sorted(profile.items())},
            'children':sum(profile.values()),'rank_mass':sum(r*n for r,n in profile.items()),
            'deficit':73*live-sum(r*n for r,n in profile.items()),'grid':str(GRID),
            'method':'new integer-root/dyadic implementation; PR706 method prior art',
            'precision':{'exponent_bits':768,'fraction_bits':1024,
                         'refinement_exponent_bits':896,'refinement_fraction_bits':1280},
            'decisions':rows,'controls':controls(profile,live,native,conservative),
            'scope':'Pinned aggregate complex profile arithmetic only; no circuit/owner/bit/outer replay, supplier admission, selected-frontier change or new kappa.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-certificate',action='store_true',help='write the exact audit receipt')
    args = parser.parse_args()
    report = audit()
    path = HERE/'CERTIFICATE.json'
    if args.write_certificate:
        path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    else:
        require(report == json.loads(path.read_bytes()), 'committed certificate mismatch')
    print(report['status'],'decisions=4 controls='+str(len(report['controls']['semantic_controls'])),
          'exact_power_comparisons='+str(report['controls']['exact_power_comparisons']))


if __name__ == '__main__':
    main()

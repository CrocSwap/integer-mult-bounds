#!/usr/bin/env python3
"""Exact eligibility-compression certificate for the optimistic L18 idle bill.
Standard library; rational transcendental bounds; checks stay active under -O.
"""
from fractions import Fraction as Q
from functools import lru_cache
from itertools import combinations
from pathlib import Path
from hashlib import sha256
from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_CEILING
from collections import Counter
import json
import argparse

HERE=Path(__file__).resolve().parent
PIN_DIGESTS={
 'root_L18.json':'be4a2beed3a40de6d2c5dcc6e4f25f3c2a4375551b70e63fb0e9a03041db6a34',
 'caller_L18.json':'f4090329f219edd493b4ca592128521e867a355fb528556b15201e759783568b',
 'inputs/base_invoice.json':'87a41b13bdd9248d538805f76a970f51335567845dfc0070698b6979a08b70d6',
}
K=Q('0.00362701882')
REQUIRED=Q('10.081828') # Checked below against the source-bound rational full bill.


def need(ok,label):
    if not ok:raise ValueError(label)


def log_series(z,terms=40):
    """2atanh(z), z in[0,1/3], exact positive-series lower/tail upper."""
    need(0<=z<=Q(1,3),'log range reduction')
    lo=sum((2*z**(2*j+1)/Q(2*j+1) for j in range(terms)),Q(0))
    tail=2*z**(2*terms+1)/(Q(2*terms+1)*(1-z*z))
    return lo,lo+tail


@lru_cache(None)
def log_bounds(n):
    e=n.bit_length()-1;p=2**e
    a,b=log_series(Q(1,3));c,d=log_series(Q(n-p,n+p))
    return e*a+c,e*b+d


def exp_neg_bounds(x):
    """Alternating Taylor series bounds for exp(-x), 0<=x<1."""
    need(0<=x<1,'exponential alternating-series range')
    term=Q(1);s=term
    for j in range(1,31):term*=(-x)/j;s+=term
    hi=s # even partial sum is an upper bound
    term*=(-x)/31
    return s+term,hi


@lru_cache(None)
def power_bounds(n):
    if not n:return Q(0),Q(0)
    need(isinstance(n,int) and n>0,'positive integral child rank')
    ll,lu=log_bounds(n)
    low=exp_neg_bounds(K*lu)[0];high=exp_neg_bounds(K*ll)[1]
    return n*low,n*high


def cost_bounds(degree):
    return power_bounds(8*degree)


def histogram_bounds(histogram):
    need(all(int(r)>0 and isinstance(c,int) and c>=0 for r,c in histogram.items()),'nonnegative invoice counts')
    return (sum((c*power_bounds(int(r))[0] for r,c in histogram.items()),Q(0)),
            sum((c*power_bounds(int(r))[1] for r,c in histogram.items()),Q(0)))


def required_savings_bounds(caller,invoice):
    counts=Counter(e[0] for e in caller['events'])
    need(counts['HOST']==18 and counts['IDLE_ONE']==181 and counts['QUERY']==3,'source-bound recursive census')
    target=Counter(1+8*m.bit_count() for m in caller['masks'])
    tl,tu=histogram_bounds(target)
    pl,pu=histogram_bounds(invoice['local_paid'])
    hl,hu=histogram_bounds(invoice['helpers'])
    fl,fu=(pl-hu)/104+1,(pu-hl)/104+1
    el,eu=power_bounds(8)
    return 18*fl-tu+181*el+3,18*fu-tl+181*eu+3


def savings_bounds(degrees):
    l1,u1=cost_bounds(1);D=sum(degrees)
    return D*l1-sum(cost_bounds(d)[1] for d in degrees),D*u1-sum(cost_bounds(d)[0] for d in degrees)


def decimal(q,rounding=ROUND_FLOOR):
    with localcontext() as c:
        c.prec=45;c.rounding=rounding
        return str(Decimal(q.numerator)/Decimal(q.denominator))


def allowed_host_pairs(mask,eligibility):
    # Compression-stable idle sets imply that a host set is downward closed
    # under STRICT eligibility inclusion. Equal-eligibility roles need no tie.
    return [list(h) for h in combinations(mask,2)
            if all(not (eligibility[j]<eligibility[i] and i in h and j not in h)
                   for i in mask for j in mask)]


def degrees_from_hosts(masks,hosts):
    need(len(hosts)==len(masks),'stage count')
    for m,h in zip(masks,hosts):need(len(h)==2 and len(set(h))==2 and set(h)<=set(m),'two eligible host roles')
    idle=[[role for role in m if role not in h] for m,h in zip(masks,hosts)]
    return validate_idle_assignment(masks,idle)


def validate_idle_assignment(masks,idle):
    need(len(idle)==len(masks),'idle-stage count')
    for m,fields in zip(masks,idle):
        need(len(fields)==len(set(fields)),'independent idle incidences are distinct')
        need(set(fields)<=set(m),'every idle role is eligible at that stage')
        need(len(fields)==len(m)-2,'exact stage idle count must be retained')
    degrees=[sum(role in fields for fields in idle) for role in range(38)]
    need(sum(degrees)==181,'all181 idle actions are retained')
    return degrees


def validate_compressed_hosts(hosts,allowed):
    need(len(hosts)==len(allowed),'compressed stage count')
    for pair,possibilities in zip(hosts,allowed):
        need(set(pair) in [set(p) for p in possibilities],'hostset must be downward-closed under eligibility inclusion')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package-root',type=Path,default=HERE)
    parser.add_argument('--receipt',type=Path,help='Optional retained JSON receipt to compare; never written')
    args=parser.parse_args();base=args.package_root.resolve()
    for name,digest in PIN_DIGESTS.items():
        need(sha256((base/name).read_bytes()).hexdigest()==digest,'source hash '+name)
    root=json.loads((base/'root_L18.json').read_text())
    caller=json.loads((base/'caller_L18.json').read_text())
    invoice=json.loads((base/'inputs/base_invoice.json').read_text())
    required_lo,required_hi=required_savings_bounds(caller,invoice)
    need(required_lo>REQUIRED,'source-bound invoice certifies conservative required saving')
    masks=[s['mask'] for s in root['stages']]
    need(root['n']==38 and len(masks)==18,'L18 source dimensions')
    need(all(len(set(m))==len(m) for m in masks),'mask roles are independent and distinct')
    eligibility=[{s for s,m in enumerate(masks) if r in m} for r in range(38)]
    need([sum(1<<s for s in e) for e in eligibility]==caller['masks'],'caller/root mask binding')
    caps=list(map(len,eligibility));need(sum(caps)==217 and sum(len(m)-2 for m in masks)==181,'exact idle mass')
    allowed=[allowed_host_pairs(m,eligibility) for m in masks]
    need([len(x) for x in allowed]==[1]*8+[2]+[1]*9,'compression forces17 stages and2 bridge cases')
    need({tuple(sorted(x)) for x in allowed[8]}=={(16,37),(19,37)},'two bridge host pairs')
    host0=[x[0] for x in allowed];host1=[x[0] for x in allowed]
    host0[8]=[16,37];host1[8]=[19,37]
    validate_compressed_hosts(host0,allowed);validate_compressed_hosts(host1,allowed)
    d0=degrees_from_hosts(masks,host0);d1=degrees_from_hosts(masks,host1)
    need(all(d0[r]==d1[r] for r in range(38) if r not in(16,19)),'only two bridge degrees differ')
    need((d0[16],d0[19],d1[16],d1[19])==(1,3,2,2),'concavity comparison is(1,3)vs(2,2)')
    # Since0<1-K<1, concavity gives f(1)+f(3)<=2f(2), selecting d0.
    need(0<K<1,'strict concavity parameter')
    lo,hi=savings_bounds(d0)
    need(hi<REQUIRED,'even optimum coalescing is below required full-bill saving')
    need(hi-lo<Q(1,10**30),'rational interval precision')
    # Controls: illegal host role, omitted idle action, and an optimistic
    # degree-only allocation that cannot satisfy the stage incidence rules.
    bad=[h[:] for h in host0];bad[0]=[2,37]
    try:degrees_from_hosts(masks,bad)
    except ValueError:pass
    else:raise ValueError('ineligible host mutation accepted')
    bad_idle=[[role for role in m if role not in h] for m,h in zip(masks,host0)]
    bad_idle[0].pop() # Delete one real idle incidence from the certified optimum.
    try:validate_idle_assignment(masks,bad_idle)
    except ValueError:pass
    else:raise ValueError('omitted idle incidence mutation accepted')
    bad_closed=[h[:] for h in host0];bad_closed[0]=[0,1]
    degrees_from_hosts(masks,bad_closed) # Valid ordinary assignment; compression alone excludes it.
    try:validate_compressed_hosts(bad_closed,allowed)
    except ValueError:pass
    else:raise ValueError('non-downward-closed hostset mutation accepted')
    left=181;relaxed=[]
    for cap in sorted(caps,reverse=True):v=min(cap,left);relaxed.append(v);left-=v
    rlo,rhi=savings_bounds(relaxed)
    need(rlo>REQUIRED,'degree-only relaxation must remain visibly insufficient')
    report={'status':'OPTIMISTIC_COALESCING_ONLY_ROUTE_CLOSED','kappa_probe':str(K),'independent_roles':38,'stages':18,'idle_actions':181,
            'host_roles_by_stage':host0,'optimal_degrees':d0,'optimal_degree_histogram':dict(sorted(Counter(d0).items())),
            'optimal_savings_interval':[decimal(lo),decimal(hi,ROUND_CEILING)],
            'required_saving_interval':[decimal(required_lo),decimal(required_hi,ROUND_CEILING)],
            'required_saving_lower':decimal(REQUIRED),'shortfall_lower':decimal(required_lo-hi),
            'degree_only_upper_interval':[decimal(rlo),decimal(rhi,ROUND_CEILING)],'candidate_native_per_stage':'17.69144246035','uncoalesced_gate_per_stage':'17.13134090285',
            'proof':'eligibility union/intersection compression plus two exact bridge cases; rational ln/exp enclosures','scope':'fixed38 coordinate roles;181 idles;two coordinate hosts perstage;free all-occurrence same-role merging;no noncoordinate or general native obstruction;no supplier or kappa claim'}
    if args.receipt:
        need(json.loads(json.dumps(report))==json.loads(args.receipt.read_text()),'retained receipt matches recomputation')
    print(json.dumps(report,sort_keys=True))
    print('PASS_L18_IDLE_COALESCING_BOUND optimum_savings_lt_9.707290 required_gt_10.081828 independent_roles=38 controls=3_REJECT degree_only_relaxation=DISTINGUISHED')

if __name__=='__main__':main()

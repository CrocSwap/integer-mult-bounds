"""Independent rational and literal-event checks for two finite Gaussian prices."""

from argparse import ArgumentParser
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as F
from functools import cache
from hashlib import sha256
from importlib import util
from math import ceil, floor, gcd
from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "source/installed-8072/runtime"
GRID = 1 << 168


def enclose(a, b):
    return F(floor(GRID*a), GRID), F(ceil(GRID*b), GRID)


@cache
def log_series(x):
    """Positive atanh series and tail on the reduced argument in [1,2]."""
    assert 1 <= x <= 2
    v = F(x-1, x+1)
    power = v
    value = 0
    for n in range(58):
        value += 2*power/(2*n+1)
        power *= v*v
    return enclose(value, value + 2*power/(117*(1-v*v)))


@cache
def exp_power(x, alpha):
    """Outward rational enclosure by log/exp, independent of binary-root code."""
    x = F(x)
    assert x >= 1 and alpha >= 0
    b = max(0, x.numerator.bit_length()-x.denominator.bit_length())
    if 2**b > x:
        b -= 1
    z = x/2**b
    lo, hi = log_series(z)
    l2, h2 = log_series(F(2))
    lo, hi = enclose(alpha*(lo + b*l2), alpha*(hi + b*h2))
    assert hi < 1
    pl = ph = ql = qh = 1
    for i in range(1, 35):
        pl, ph = enclose(pl*lo/i, ph*hi/i)
        ql += pl
        qh += ph
    return enclose(ql, qh + (ph*hi/35)/(1-hi/36))


def numerical_contract(recipe, s, lower, booked):
    c = recipe.trial
    t = 1-c
    psi_lo = psi_hi = num_lo = num_hi = 0
    minimum_requirement = 0
    phase_count = 0
    typed_pooled = Counter()
    tcounts = [v.histogram for v in recipe.targets.variants]
    pcounts = [v.histogram for v in recipe.paid.variants]
    weights = (5, 451)
    for (a,r,b,k), typed in recipe.typed_cells().items():
        # TypedPlan divides this typed share equally amongst real b,k ports.
        unit = typed/tcounts[b][k]
        typed_pooled[r,k] += weights[a]*pcounts[a][r]*tcounts[b][k]*unit
    for (raw_r,raw_k), share in recipe.cells.items():
        r, k = F(raw_r), F(raw_k)
        z = k/r
        common = gcd(int(2*r),int(2*k))
        assert int(2*r) == 2*r and int(2*k) == 2*k
        assert typed_pooled[r,k] == recipe.paid.histogram[r]*share
        weight = typed_pooled[r,k]
        p_lo, p_hi = exp_power(z,c)
        d_lo, d_hi = weight*r*(p_lo-1)/c, weight*r*(p_hi-1)/c
        psi_lo += d_lo
        psi_hi += d_hi
        mean = (s+1)*(k-r) + t*r*r/(2*k*lower)
        num_lo += weight*p_lo/z*mean
        num_hi += weight*p_hi/z*mean
        # Enumerate each constant overlap in one joint period, with even-bin
        # starts generated independently of the executable's own bucketing.
        period = 2*z.denominator
        knots = sorted({F(2*j) for j in range(z.denominator+1)} |
                       {F(2*j)/z for j in range(z.numerator+1)})
        suffixes = []
        exact_area = 0
        for left, right in zip(knots, knots[1:]):
            middle = (left+right)/2
            dst, src = 2*floor(middle/2),2*floor(z*middle/2)
            value = r*(src-s)-k*(dst-s)
            suffixes.append(value)
            exact_area += value*(right-left)
        need = (2*r-common)/(k-r)
        minimum_requirement = max(need,minimum_requirement)
        assert exact_area == period*(s+1)*(k-r)
        assert min(suffixes) == s*(k-r)-2*r+common >= 0
        assert max(suffixes) == s*(k-r)+2*k-common
        phase_count += len(suffixes)
    delta = F(1,2**128)
    scale = 263772
    f_lo, f_hi = num_lo/(t*psi_hi), num_hi/(t*psi_lo)
    s_lo, s_hi = exp_power(scale*lower,c)
    common = (1+delta)*(1+F(1032,scale))/(1-delta)**4
    fac_lo = common*s_lo*(1+f_lo/lower+delta)
    fac_hi = common*s_hi*(1+f_hi/lower+delta)
    tick = F(1,booked.denominator)
    threshold, _ = exp_power(2,booked)
    _, previous = exp_power(2,booked-tick)
    assert fac_hi < threshold and previous < fac_lo
    return dict(fringe_nano_bounds=[floor(10**9*f_lo),ceil(10**9*f_hi)],
                factor_pico_bounds=[floor(10**12*fac_lo),ceil(10**12*fac_hi)],
                booked_debit=str(booked), lower_gap_pico=floor(10**12*(threshold-fac_hi)),
                previous_tick_fails_gap_pico=floor(10**12*(fac_lo-previous)),
                phase_intervals=phase_count, grade_cells=len(typed_pooled),
                typed_cells=len(recipe.typed_cells()), minimum_shift_requirement=str(minimum_requirement))


def plan_check(runtime, s, t):
    """Compare full literal event stream with an independent three-part identity."""
    spec = util.spec_from_file_location("referee_typed_"+str(s), runtime/"typed_transport.py")
    module = util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    r,k = 4,5
    L,U,V = 50,108,14000
    K = 11
    n = 4096
    weights = (2,3)
    # Two copies in each actual raw list force both later chronological loans
    # and nontrivial issuer/owner aggregation at both ends.
    types = [module.NativeType((k,k),(r,r),w) for w in weights]
    cells = {(a,r,b,k): F(w,sum(weights)) for a in range(2) for b,w in enumerate(weights)}
    extra = {"column_offset":s} if s!=8 else {}
    p = module.TypedPlan(n, types, cells, t, L, U, V, K, n,
                         delay_base=3,padding=1, **extra)
    matched = unused = drain = loans = 0
    literal_by_prefix = Counter()
    source_by_type = Counter()
    witness = None
    actual_grants = 0
    zero_ideal_with_no_grant = 0
    c = 1-t
    mean = (s+1)*(k-r) + t*r*r/F(2*k*L)
    for e in p.bands:
        for a, raw in enumerate(types):
            for j,grade in enumerate(raw.paid):
                parent = grade*(e-s)
                potential = 0
                avail = p.count[e,a]
                issued = max(0,K-j*p.delay[e])
                by_pair = {}
                for edge in p.send.get((e,a,j),()):
                    d,b,i = edge.band,edge.kind,edge.port
                    child = types[b].targets[i]*(d-s)
                    S = parent-child
                    l,u = max(F(e),F(d*k,r)),min(F(e+2),F((d+2)*k,r))
                    assert l<u and S>=0
                    by_pair[b,i,d] = edge.count
                    q = cells[a,r,b,k]/types[b].targets.count(k)
                    lp = exp_power(l,c)
                    up = exp_power(u,c)
                    ideal_lo = weights[a]*V*q/t*(lp[0]/l-up[1]/u)
                    ideal_hi = weights[a]*V*q/t*(lp[1]/l-up[0]/u)
                    assert edge.count <= ideal_hi < edge.count+2
                    if t==1:
                        assert ideal_lo == ideal_hi
                    if S > mean and issued > 0:
                        witness = [e,a,j,d,b,i,edge.count,S]
                    matched += K*edge.count*S
                    drain += (K-issued)*edge.count*child
                    loans += issued*edge.count
                    actual_grants += 1
                    potential += edge.count
                    source_by_type[a,b] += edge.count
                for d in p.bands:
                    left,right = max(F(e),F(d*k,r)), min(F(e+2),F((d+2)*k,r))
                    if left<right:
                        for b, dst in enumerate(types):
                            for i in range(len(dst.targets)):
                                if (b,i,d) not in by_pair:
                                    zero_ideal_with_no_grant += 1
                unused += K*(avail-potential)*parent
    frames, pending = {}, {}
    parents_used = externals = zeros = max_depth = observed = 0
    for op, frame, *fields in p.events():
        if op==0:
            header, *bindings = fields
            dst = header - header%2 + s
            depth = 0
            iterator = iter(bindings)
            for mode in iterator:
                if mode==1:
                    size, route_depth, donor = pending.pop(next(iterator))
                    assert size==k*(dst-s)
                    assert p.delay[dst]<p.delay[donor]
                    assert donor>dst
                    depth=max(depth,route_depth)
                    parents_used+=1
                elif mode==2:
                    _, size, period = next(iterator),next(iterator),next(iterator)
                    assert size==k*(dst-s) and period==4*ceil(F(n,4*size))
                    externals+=1
                else:
                    assert mode==0 and next(iterator)==k*(dst-s)
                    zeros+=1
            frames[frame]=(dst,depth)
            max_depth = max(max_depth,depth)
        elif op==1:
            serial,size,selected=fields
            donor,depth=frames[frame]
            assert size==r*(donor-s) and selected<=size
            if selected:
                assert serial not in pending
                pending[serial]=(selected,depth+1,donor)
                observed+=int(size-selected>mean)
            literal_by_prefix[bool(selected)] += size-selected
        else:
            assert op==2
            del frames[frame]
    assert not pending and not frames and max_depth>=2 and min(zeros,externals,observed)>0
    assert parents_used==loans
    literal = sum(literal_by_prefix.values())
    assert literal == p.leaves_per_epoch == (matched + unused + drain)
    assert min(matched,unused,drain,loans)>0 and len(source_by_type)==4
    assert witness is not None and zero_ideal_with_no_grant>0
    integral_per_birth = (sum(weights)*2*V*F(r,k)*exp_power(F(k,r),c)[1]
                          *exp_power(F(L),c)[1]/(t*L)*mean)
    assert matched <= K*integral_per_birth
    return dict(s=s,t=str(t),event_leaves=literal,steady_matched_suffix=matched,
                unallocated_full_parents=unused,late_missed_prefixes=drain,
                finite_matched_grants=actual_grants, positive_interval_no_grant=zero_ideal_with_no_grant,
                issued_loans=loans, typed_pairs=len(source_by_type),exterior_slots=p.source_width,
                received_interiors=parents_used,exterior_descriptors=externals,zero_descriptors=zeros,
                observed_nested_depth=max_depth,issued_above_average=observed,
                actual_nonpointwise_witness=witness)


def main():
    parser = ArgumentParser()
    parser.add_argument("mode",choices=["price","events"])
    parser.add_argument("--base-runtime",type=Path,default=BASE)
    parser.add_argument("--six-runtime",type=Path,default=ROOT/"architect/successor/runtime")
    parser.add_argument("--offset",choices=[6,8],type=int)
    args = parser.parse_args()
    base = args.base_runtime.resolve()
    offsets = [8,6] if args.offset is None else [args.offset]
    selected = {8:(1874,F(130699669,2**30),base),
                6:(1054,F(125645,1048576),args.six_runtime.resolve())}
    started = datetime.now(timezone.utc).isoformat()
    sys.path.insert(0,str(base))
    if args.mode == "price":
        from upstream import install
        install()
        from grades import numerical_recipe
        recipe = numerical_recipe(1024)
        result = {str(s):numerical_contract(recipe,s,selected[s][0],selected[s][1])
                  for s in offsets}
    else:
        from installations import GAUSSIAN_C
        result = [plan_check(selected[s][2],s,t) for s in offsets
                  for t in (F(1),1-GAUSSIAN_C)]
    pins = {file:sha256((base/file).read_bytes()).hexdigest()
            for file in ["transport.py","typed_transport.py","grades.py"]}
    if 6 in offsets and args.mode=="events":
        pins["six/typed_transport.py"]=sha256((selected[6][2]/"typed_transport.py").read_bytes()).hexdigest()
    print(json.dumps(dict(mode=args.mode,started_at=started, finished_at=datetime.now(timezone.utc).isoformat(),
            predecessor_runtime=pins, result=result),indent=2))


if __name__=="__main__":
    main()

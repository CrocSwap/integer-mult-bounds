"""Replay the pinned caller, all changed-mask cuts, overlap tariffs and controls."""
from collections import Counter
from fractions import Fraction
from functools import cache
from hashlib import sha256
from math import isqrt
from pathlib import Path
from tempfile import TemporaryDirectory
from io import BytesIO
import gzip, json, sys, tarfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from seam import P, I, paired_scan, control

UNIT = 1 << 160
T = Fraction(9961, 10000)
PIN = "305d410c1868be970d30cf0700e5e036001bf60fa8ba59510ef763ff957dd983"
MANIFEST = "cc1ebbe8a95c24886017a5b1d36a8f3b39f771a66c556c8ae6a2ef3757c7c593"


def authenticated_caller(dest, receipt):
    raw = (HERE / "source/runtime.tar.gz").read_bytes()
    meta = (HERE / "source/origins.json").read_bytes()
    assert sha256(raw).hexdigest() == PIN and sha256(meta).hexdigest() == MANIFEST
    recorded = json.loads(meta)
    assert recorded["archive_sha256"] == PIN
    src = recorded["members"]
    with tarfile.open(fileobj=BytesIO(raw), mode="r:gz") as tar:
        for name, digest in receipt["caller_source_sha256"].items():
            assert src["research/grade14-native-realization/retained/" + name]["sha256"] == digest
            data = tar.extractfile(digest).read()
            assert sha256(data).hexdigest() == digest
            path = dest / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)


@cache
def power(rank):
    """Enclose the rational power using dyadic exponent brackets and integer square roots."""
    if rank in (0, 1):
        return rank*UNIT, rank*UNIT
    bits = 176
    low_exponent = (T.numerator << bits) // T.denominator
    def dyadic(k, upper):
        a = b = rank*UNIT
        y = UNIT
        for pos in reversed(range(bits)):
            a = isqrt(a*UNIT)
            b = 1+isqrt(b*UNIT-1)
            if k >> pos & 1:
                y = -(-y*b//UNIT) if upper else y*a//UNIT
        return y
    lower = dyadic(low_exponent, False)
    upper = dyadic(low_exponent+1, True)
    assert lower <= upper
    return lower, upper


def bounds(hist):
    lower = upper = 0
    for rank, n in hist.items():
        a,b = power(rank)
        lower += n*(a if n>=0 else b)
        upper += n*(b if n>=0 else a)
    return lower,upper


def decimals(lo,hi,precision=25):
    scale=10**precision
    def fmt(n):
        sign = "-" if n<0 else ""
        u,v=divmod(abs(n),scale)
        return f"{sign}{u}.{v:0{precision}d}"
    return [fmt(lo*scale//UNIT), fmt(-(-hi*scale//UNIT))]


def mask_proof(events, targets):
    target = Counter(frozenset(stages) for _, stages in targets)
    paid = Counter(frozenset(data[1]) for op,*data in events if op=="IDLE_ONE")
    common = target & paid
    rem_t,rem_p=target-common,paid-common
    assert Counter({n:sum(v for k,v in rem_t.items() if len(k)==n) for n in (8,16)})=={8:4,16:2}
    assert all(len(k) in (8,16) for k in rem_t)
    assert all(len(k)==1 for k in rem_p)
    rank_hist=Counter(8*len(stages)+h%2 for h,stages in targets)
    total_rank=sum(r*n for r,n in rank_hist.items())
    target_lo,target_hi=bounds(rank_hist)
    headroom=(total_rank*UNIT-target_hi,total_rank*UNIT-target_lo)
    # Every old matched idle has mask of at most seven colors, or 56 body axes.
    # Max increase of H(d+1)-H(d) is the difference between its values at 0 and 56.
    n_matched=sum(common.values())
    upper_gain=n_matched*(UNIT+power(56)[1]-power(57)[0])
    # An overlap decreases the full-body grade by at least 2 on each of 2 centers.
    center_loss_lower=2*(power(129)[0]-power(127)[1])
    assert upper_gain<center_loss_lower and headroom[1]<32*UNIT
    return {
        "unmatched_productive_body_sizes":{n:sum(v for k,v in rem_t.items() if len(k)==n) for n in (8,16)},
        "matched_paid_target_pairs":n_matched, "unmatched_fixed_paid_singletons":sum(rem_p.values()),
        "complete_unit_split_headroom":decimals(*headroom),
        "dependent_overlap_and_free_rank_conserving_splits_gain":decimals(headroom[0]-32*UNIT,headroom[1]-32*UNIT),
        "overlap_with_original_endpoint_bill_gain_upper":decimals(upper_gain-center_loss_lower,upper_gain-center_loss_lower)[1],
    }


def run():
    assert __debug__, "Run with Python assertions enabled"
    source_bytes=(HERE/"SOURCE.json").read_bytes()
    assert sha256(source_bytes).hexdigest()=="cab3cca4f755bdad946eb11591a5498e68a65daaee9d0349cd06e49c0b5b6a98"
    receipt=json.loads(source_bytes)
    assert receipt["head"]=="75f7e1c44f48c43983016bcf8878c4d9e5e87c62"
    assert receipt["word_sha256"]=="38d2b3a2311a9ba5fee091cc7aa204c7ed95651aec95d75184b2391df090cbfb"
    assert receipt["layout_sha256"]=="0ce3f9e383fc4bfdd22612b9e34fc9759d97204215937b82d23aec2cedd9b8ee"
    native_paid=Counter({int(k):48*v for k,v in receipt["native_paid_per_invocation"].items()})
    native_targets=Counter({int(k):48*v for k,v in receipt["native_productive_per_invocation"].items()})
    assert sum(native_paid.values())==48*5674 and sum(native_targets.values())==48*891
    result={"source_head":receipt["head"],"character_field":{"prime":P,"i":I},
            "control":control(),"templates":{}}
    with TemporaryDirectory() as tmp:
        folder=Path(tmp)
        authenticated_caller(folder,receipt);sys.path.insert(0,str(folder))
        from closed_caller import templates,placement
        from mixed_grid import census,exact
        caller=json.loads(gzip.decompress((folder/"data/CALLER.json.gz").read_bytes()))
        words=templates(caller)
        assignment=placement(caller)
        by_kind=Counter(k for k,_ in assignment)
        assert by_kind=={"A":120,"rotated":192}
        assert all(len(visits)==16 for visits in assignment.values())
        for label,(events,targets) in words.items():
            t,p,uses,_=census(events,targets)
            for r,n in t.items():native_targets[r]+=by_kind[label]*n
            for r,n in p.items():native_paid[r]+=by_kind[label]*n
            full=exact(events,targets,2025<<9)
            tests={str(s):paired_scan(events,targets,s) for s in (1,-1)}
            assert all(row["compatible_before_pairing"]==0 for row in tests.values())
            result["templates"][label]={
                "events":len(events),"physical_roots":by_kind[label],"full_laurent_positive_control":full,
                "head_square_sectors":tests,"body_overlap":mask_proof(events,targets)}
    assert (sum(native_targets.values()),sum(native_paid.values()))==(52608,281568)
    old=Counter(native_targets)
    old.subtract(native_paid)
    lo,hi=bounds(old)
    assert hi<0
    result["unchanged_native_word"]={
        "productive":sum(native_targets.values()),"paid":sum(native_paid.values()),
        "raw_productive_minus_paid_at_0.0039":decimals(lo,hi),
        "productive_histogram": dict(sorted(native_targets.items())),
        "paid_histogram":dict(sorted(native_paid.items()))}
    return result


if __name__=="__main__":
    result=run()
    if sys.argv[1:]==["--emit"]:
        print(json.dumps(result,indent=2,sort_keys=True))
    elif not sys.argv[1:]:
        assert json.loads(json.dumps(result))==json.loads((HERE/"RESULT.json").read_bytes())
        print("PASS_P104_PRODUCTIVE_MASK_SEAMS")
    else:
        raise SystemExit("Usage: verify.py [--emit]")

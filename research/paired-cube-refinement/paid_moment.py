#!/usr/bin/env python3
"""Source-derived exact paid bit moment for an independently checked profile.

The finite word and determinant proofs remain separate obligations. The
profile is charged its full ideal moment plus every fallback child, without
subtracting the good contribution displaced by a bad residue class.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from interval_moment import moment, prepare, log_interval, exp_interval

SOURCE = "notes/three-stage-cover-bit.tex"
SOURCE_SHA256 = "47123a756f823c83a0d48cca2bf5add6472cd88410b13aed345e70c8834fb511"
PRIME_LOWER_BOUND = 2**80
OLD = Q(384599, 10**10)


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def envelope(m, mode="derived", root=ROOT):
    """Derive a complete bill; alternatives exist only for matched controls."""
    require(type(m) is int and m > 1, "positive integer ambient dimension")
    require(sha256((root/SOURCE).read_bytes()).hexdigest() == SOURCE_SHA256,
            "fallback and rare-class theorem source drift")
    require(mode in ("legacy", "rare_only", "derived"), "unknown fallback envelope")
    n0 = 2*m
    direct = 6*n0*(n0-1)+3*n0+6*(n0-1)
    require(0 < direct < 32*m*m, "direct fallback count")
    rare = Q(2*m**3, PRIME_LOWER_BOUND)
    require(0 < rare < Q(1,10**16), "retained prime range supports old envelope")
    return dict(mode=mode, m=m, prime_lower_bound_exclusive=PRIME_LOWER_BOUND,
                bad_fraction=Q(1,10**16) if mode=="legacy" else rare,
                fallback_children_per_edge=direct if mode=="derived" else 32*m*m,
                residual_dimension=n0, source_path=SOURCE, source_sha256=SOURCE_SHA256,
                rare_bound="2*m^3/q < 2*m^3/2^80; q > 2^80",
                fallback_bound="6*N0*(N0-1)+3*N0+6*(N0-1); N0=2*m")


def validate_envelope(bill, m, root=ROOT):
    require(isinstance(bill,dict), "fallback envelope object")
    require(all(type(bill.get(k)) is int for k in ("m","prime_lower_bound_exclusive",
                "fallback_children_per_edge","residual_dimension")), "exact integer fallback fields")
    require(type(bill.get("bad_fraction")) is Q, "exact rational rare-class fraction")
    require(bill == envelope(m,bill.get("mode"),root),
            "fallback envelope must equal its source-derived bound")
    return bill


def profile(row):
    for name in ("m","W_per_vertex","deficit_per_vertex","rank_per_vertex","maxchild"):
        require(type(row[name]) is int, "exact integer profile field "+name)
    p=dict(m=row["m"],W=row["W_per_vertex"],N=row["deficit_per_vertex"],L=0,
           total_rank=row["rank_per_vertex"],maxchild=row["maxchild"],
           child_multiplicities=row["child_histogram"])
    prepare(p)
    return p


def paid_moment(p, a, details=False, bill=None):
    require(type(a) in (int,Q), "exact saving required")
    bill=envelope(p["m"]) if bill is None else validate_envelope(bill,p["m"])
    raw=moment(p,a,details)
    m,w=p["m"],p["W"]
    count=sum(p["child_multiplicities"].values())
    lo,hi=log_interval(Q(m));el,eu=exp_interval(a*lo,a*hi)
    weight=bill["bad_fraction"]*Q(bill["fallback_children_per_edge"]*count,w*m)
    return dict(saving=a,lower=raw["lower"]+weight*el,
                upper=raw["upper"]+weight*eu,
                strict_gap_lower=1-raw["upper"]-weight*eu,raw=raw,
                fallback_lower=weight*el,fallback_upper=weight*eu,
                edge_count=count,bad_fraction=bill["bad_fraction"],
                fallback_children_per_edge=bill["fallback_children_per_edge"])


def certify(row, bill=None):
    p=profile(row);bill=envelope(p["m"]) if bill is None else validate_envelope(bill,p["m"])
    grid=10**18;lo=0;hi=grid//100
    require(paid_moment(p,Q(lo,grid),bill=bill)["upper"]<1, "zero-saving rank contraction")
    require(paid_moment(p,Q(hi,grid),bill=bill)["lower"]>1, "upper saving bracket")
    while hi-lo>1:
        mid=(lo+hi)//2;r=paid_moment(p,Q(mid,grid),bill=bill)
        if r["upper"]<1:lo=mid
        elif r["lower"]>1:hi=mid
        else:raise ValueError("increase exact moment precision")
    coarse=Q(lo,grid)
    accepted=paid_moment(p,coarse,True,bill)
    rejected=paid_moment(p,Q(hi,grid),True,bill)
    require(accepted["upper"]<1<rejected["lower"], "adjacent coarse grid proof")
    threshold=coarse/(1+coarse-OLD);atomgrid=10**24;scaled=threshold*atomgrid
    atom=Q(scaled.numerator//scaled.denominator+1,atomgrid)
    actual=(1-atom)*coarse+atom*OLD;previous=atom-Q(1,atomgrid)
    require(actual<atom<1-actual, "paid atom and row adapter toll")
    require(previous<=(1-previous)*coarse+previous*OLD, "previous atom grid rejected")
    require(p["total_rank"]+bill["bad_fraction"]*bill["fallback_children_per_edge"]*accepted["edge_count"] < p["W"]*p["m"],
            "contaminated rank mass contracts")
    return dict(coarse_saving=coarse,ordinary_saving=actual,atom_beta=atom,
                atom_threshold=threshold,old_atom_saving=OLD,coarse_grid=grid,
                atom_grid=atomgrid,atom_lower_gap=atom-actual,
                atom_upper_gap=1-actual-atom,accepted=accepted,rejected=rejected,
                envelope=bill,controls=dict(next_coarse_grid_rejected=True,
                                           previous_atom_grid_rejected=True),
                scope="Exact finite histogram with the source-derived per-edge rare-class and full fallback bound. Inherited all-size compiler contracts remain assumptions; no true-profile or global optimality claim.")

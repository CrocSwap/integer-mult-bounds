#!/usr/bin/env python3
"""Exact rational *conservative* screen: PR131 local frames in PR132 paired cover.

This is a finite conditional candidate; NOT a verified physical-composition
theorem, and NOT independent peer review. Original PR131 source package
remains byte-identical. Inherited PR130/PR131 checks remain dependencies.

Reference: PR131 3acf2f944abd069301600ce468f16f1dd8f1f9e4;
PR132 f7bc7a91b1c5c7b6714b54529f338c98965e3173.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction as Q
from importlib.util import module_from_spec, spec_from_file_location
from math import prod
from pathlib import Path
import argparse
import json
import sys

if sys.flags.optimize:
    raise RuntimeError("Assertions are required; do not use python -O")
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import three_stage_cover_network as inherited
from structured_bulk_assembly import assembly, halving, js

GRID_A = 10**12
GRID_K = 10**15
STOP = Q(1, 10**6)
PR132_KAPPA = Q(1708101, 5000000000)
TARGET = PR132_KAPPA * Q(103, 100)

def require(ok: bool, msg: str) -> None:
    if not ok:
        raise ValueError(msg)

def pinned_local():
    """Use the frozen, independently audited PR131 physical profile, not a guess."""
    path = ROOT / "research/cover-local-reuse/certificate.py"
    spec = spec_from_file_location("pr131_cover_certificate", path)
    require(spec is not None and spec.loader is not None, "PR131 package missing")
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    p = mod.cover_profile()  # SHA pins, reflection receipt, dirty/reuse checks.
    baseline = json.loads((ROOT/"research/cover-local-reuse/certificate.json").read_text())
    require(Q(baseline["kappa"]) == Q(166102699493,500000000000000),
            "Pinned PR131 κ changed")
    local = json.loads((ROOT/"research/cyclic-deferred/complex-profile.json").read_text())
    audit = json.loads((ROOT/"research/cyclic-deferred/reflection-audit.json").read_text())
    require(p["R"] == 26597 and p["virtual_R"] == 28705 and
            p["reused_roles"] == 2108 and local["R"] == p["R"], "PR131 roles")
    require(local["replay"]["scratch_restored"] and local["replay"]["y_plus_x"],
            "PR131 dirty replay missing")
    for key in ("physical_aliased_numeric_replay",
                "literal_frame_incidences_both_directions",
                "reflected_residual_rank_histogram_equal",
                "exact_arbitrary_dirty_cancellation_by_dependency_cut",
                "bounded_chunk_coefficients"):
        require(audit[key] is True, "Inherited PR131 audit: " + key)
    return p, local, audit

def profile():
    p, local, audit = pinned_local()
    h,v,R,m = p["h"],p["v"],p["R"],p["m"]
    require((h,v,R,m)==(24,2024,26597,70), "PR131 dimensions")
    row = json.loads((ROOT/"certificates/three-stage-cover-complex-input.json").read_text())
    require(row["R"] == p["virtual_R"] == 28705 and row["total_M_operations"] == 118451
            and row["loss"] == 552, "Full virtual scalar reserve")
    require(row["v"] == v and row["h"] == h, "Same h=24 source word")
    H = Counter({int(t):int(n) for t,n in p["local_child_multiplicities"].items()})
    require(all(0<t<h and n>0 for t,n in H.items()), "Illegal local child")

    source = Counter()
    for entry in local["physical_auxiliary_source_frames"]:
        s=len(entry["basis"])
        source[s]+=entry["count"]
    require(sum(source.values())==R, "All physical source gauges accounted for")
    expected_ext = Counter()
    for s,n in source.items():expected_ext[m-h+s]+=3*n
    require(dict(sorted(expected_ext.items())) ==
            {int(t):int(n) for t,n in p["exterior_child_multiplicities"].items()},
            "Physical source/exterior provenance mismatch")

    # Verify an actual coordinate pairing involution for the first-stage
    # h-plane and its h-dimensional orthogonal spectator plane.
    permutation=list(range(m))
    for j in range(h):
        permutation[j],permutation[h+j]=h+j,j
    require(all(permutation[permutation[i]]==i for i in range(m)) and
            all(permutation[j]>=h for j in range(h)),
            "Stage-one orthogonal fixed-point-free pairing invalid")

    # Hypothetically merge ALL small local rank-r children: one rank-2r
    # child per pair in stage one, 4 separate rank-r children in stages 2/3.
    # This over-merges the actual SOURCE and TARGET data fronts, which must
    # stay independent. Moment_bound() rigorously charges the difference
    # from this optimistic multiset using their exact total RANK mass;
    # the resulting upper envelope is a valid conservative calculation.
    children=Counter()
    for r,n in H.items():
        children[2*r]+=n
        children[r]+=4*n
    for s,n in source.items():
        children[m-2*h+2*s]+=n
        children[m-h+s]+=4*n
    children=Counter({r:n for r,n in children.items() if n})
    W2=4*v+5*R
    rank2=sum(r*n for r,n in children.items())
    deficit=W2*m-rank2
    require(deficit==2*(2*v-3*row["loss"])==4784, "Paired telescoping failed")
    require(W2==141081 and rank2==9870886, "Profile provenance changed")
    require(all(0<r<m and n>0 for r,n in children.items()) and max(children)==68,
            "Bad rank/child")
    require(sum(r*n for r,n in H.items())==711195,
            "Inherited PR131 local rank mass mismatch")

    # These two quantities are not estimated histograms: the PR131
    # complex_deferred.py target-readout path is 0 -> levels -> h-1
    # for each of v targets, and the source front is one h-1 for each
    # of v sources. Their exact rank *mass* is 2v(h-1).
    src = (ROOT/"research/cyclic-deferred/complex_deferred.py").read_text()
    for literal in ("ds = sorted(levels[t] | {0, h - 1})",
                    "z[b - a] += 2 * v",
                    "z[h - 1] += 2 * N"):
        require(literal in src, "Source/target data telescope no longer pinned")
    data_mass=2*v*(h-1)
    require(data_mass==93104, "Unpaired data rank-mass correction")
    return dict(m=m,h=h,v=v,R=R,virtual_R=p["virtual_R"],
                reused_roles=p["reused_roles"],W=W2,rank=rank2,deficit=deficit,
                maxchild=max(children),
                child_multiplicities=dict(sorted(children.items())),
                physical_source_dimensions=dict(sorted(source.items())),
                local_child_multiplicities=dict(sorted(H.items())),
                nonmergeable_data_rank_mass=data_mass,
                note="Children are an optimistic arithmetic multiset; an independent positive moment correction covers ALL nonmergeable data fronts.",
                pr131_local_profile_sha256=p["local_profile_sha256"],
                pr131_reflection_receipt_sha256=p["reflection_receipt_sha256"])

def moment_upper(profile: dict,a:Q):
    """Certified upper moment for the ACTUAL, data-unmerged paired schedule."""
    m,W=profile["m"],profile["W"]
    require(0<=a<Q(1,100), "Saving outside permitted range")
    lg=inherited.log_upper
    ex=inherited.exp_upper
    # Same exact rational log/exp enclosures as the PR130 three-stage check.
    optimistic=sum(Q(r*n,m*W)*ex(a*lg(Q(m,r)))
                   for r,n in profile["child_multiplicities"].items())
    # A rank-r data front gives two separate rank-r children in stage 1;
    # the optimistic histogram counts one rank-2r child instead.
    # Difference = 2r (m/r)^a [1 - 2^(-a)] /(mW)
    # <= 2r (m)^a a log 2 /(mW) for r>=1.
    penalty=(Q(2*profile["nonmergeable_data_rank_mass"],m*W)
            *a*lg(Q(2))*ex(a*lg(Q(m))))
    return optimistic+penalty,optimistic,penalty

def certificate():
    p=profile()
    def accepts_a(n):
        return moment_upper(p,Q(n,GRID_A))[0]<1
    lo,hi=0,700000000
    require(accepts_a(lo) and not accepts_a(hi),"Complex moment bracket failed")
    while hi-lo>1:
        t=(hi+lo)//2
        if accepts_a(t):lo=t
        else:hi=t
    ac=Q(lo,GRID_A)
    upper,opt,penalty=moment_upper(p,ac)
    require(upper<1 and not accepts_a(lo+1), "Next conservative grid point")
    require(penalty>0 and upper>opt, "Omitted nonmergeable-data charge")

    m=p["m"];h=p["h"];v=p["v"];w2=p["W"]
    n=m//2
    vertices=(2**(m-1+(n-1)**2)
              *prod(2**(2*i)-1 for i in range(1,n)))
    require(vertices.bit_length()==2415, "Pinned O(70,2) group order")
    require(vertices%2==0, "Paired vertex count integral")
    phase=dict(m=m,W=vertices*w2//2,
               total_rank=vertices*p["rank"]//2,
               N=vertices*v,vertices_per_stage=vertices,
               maxchild=p["maxchild"])
    row=json.loads((ROOT/"certificates/three-stage-cover-complex-input.json").read_text())
    # Inherited PR130 scalar/router/row reserves, with full virtual PR131
    # readout operations paid, actual physical paired stream stock.
    bridge=inherited.finite_bridge(phase,row)
    audit=json.loads((ROOT/"research/cyclic-deferred/reflection-audit.json").read_text())
    require(bridge["complex"]["local_group_upper"]>=audit["conservative_local_G"]
            >= audit["expanded_scalar_operations_per_stage"],
            "All compensated readout/lockstep scalar charges must be paid")
    require(bridge["rows"]["degree"]==160000 and
            bridge["rows"]["coefficient"]==68505,
            "Row reserve/source count changed")
    # The PR130 bit supplier is unchanged; reproduce its exact certificate.
    bit=inherited.bit_certificate(json.loads(
        (ROOT/"certificates/three-stage-cover-bit-input.json").read_text()))
    ab=inherited.AB
    require(bit["effective_saving"]==ab,"Inherited stopped bit discrepancy")
    assembly_bit=min(ab,(1-STOP)*ac-Q(1,10**14))
    def accepts_k(k):
        try:
            assembly(assembly_bit,ac,bridge,Q(k,GRID_K),beta=STOP)
        except AssertionError:
            return False
        return True
    low,high=0,int(ac*GRID_K)+1
    require(accepts_k(low) and not accepts_k(high),"Assembly bracket failed")
    while high-low>1:
        mid=(low+high)//2
        if accepts_k(mid):low=mid
        else:high=mid
    k=Q(low,GRID_K)
    details=assembly(assembly_bit,ac,bridge,k,beta=STOP)
    require(not accepts_k(low+1),"Next 10^-15 κ point not rejected")
    require(len(details["strict_constraints"])==47 and
            len(details["margins"])==7,"Assembly constraints missing")
    require(k>=TARGET,"Candidate fails +3% relative to PR132")
    require(k==Q(181054111477,500000000000000) and
            ac==Q(362371031,10**12),
            "Expected finite calculation changed")
    return js(dict(
        status="EXACT FINITE ARITHMETIC PASS; paired physical execution requires separate written proof/review",
        kappa=k,baseline_pr132_kappa=PR132_KAPPA,
        improvement_ratio=k/PR132_KAPPA,
        target_plus_three_percent=TARGET,
        complex_saving=ac,
        actual_bit_saving=ab,assembly_bit_saving=assembly_bit,
        optimistic_moment_upper=opt,
        nonmergeable_data_moment_charge=penalty,
        conservative_complex_moment_upper=upper,
        conservative_complex_moment_gap=1-upper,
        profile=p,bit=dict(coarse_saving=bit["coarse_saving"],
                           stopped_saving=bit["effective_saving"],
                           contaminated_moment_gap=bit["strict_gap"]),
        finite_bridge=dict(
            role_bits=bridge["complex"]["W"].bit_length(),
            local_scalar_group_guard=bridge["complex"]["local_group_upper"],
            charged_scalar_groups=bridge["complex"]["scalar_group_upper"],
            row_coefficient=bridge["rows"]["coefficient"],
            row_degree=bridge["rows"]["degree"],
            semantic_charge_gap=bridge["semantic"]["strict_literal_gap"]),
        strict_constraints_count=len(details["strict_constraints"]),
        margins_count=len(details["margins"]),
        assembly_absorption_gap=details["absorption_gap"],
        scope="Conditional finite arithmetic combining PR131 local physical source inventory with PR132 orthogonal first-stage pairing. Shared-scratch execution theorem and inherited all-size analytic/tape contracts are written proof dependencies; independent full physical replay not run by this script.",
        credits="PR130 icekylinx, PR131 eumemic, PR132 ikeboy, PR124 jamesyc; original source attributions retained; OpenAI assistance on conservative moment hybrid."))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path)
    args=ap.parse_args()
    result=certificate()
    text=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.output:args.output.write_text(text)
    else:print(text)
    print("PASS conditional finite candidate κ",result["kappa"],
          "complex",result["complex_saving"],
          "strict constraints",result["strict_constraints_count"],
          "margins",result["margins_count"],file=sys.stderr)

if __name__=="__main__":
    main()

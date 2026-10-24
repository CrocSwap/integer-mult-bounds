#!/usr/bin/env python3
"""Exact bounded review of one p=3 moving-anchor invoice; no numeric roots.

No author checker, native code or compiler is imported. Apache-2.0.
Substantial OpenAI Codex assistance; source contributions credited in REVIEW.md.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import ast
import json
import re

HERE = Path(__file__).resolve().parent


def need(ok, why):
    if not ok:
        raise ValueError(why)


def product(left, right):
    """Normal form P*D^a: P maps input coordinate j to P[j]."""
    p,a = left
    q,b = right
    return tuple(p[q[j]] for j in range(4)), tuple(a[q[j]]+b[j] for j in range(4))


def stage(label):
    p = list(range(4))  # Anchor0, stage1, stage2, centralQ.
    p[0],p[label] = p[label],p[0]
    return tuple(p),(1,0,0,0)


def signed(targets, paid):
    out = Counter(targets)
    out.subtract(paid)
    return {r:n for r,n in out.items() if n}


def separation(profile):
    positive = {r:n for r,n in profile.items() if n>0}
    negative = {r:-n for r,n in profile.items() if n<0}
    need(positive and negative, "Both signed supports required")
    a,b = min(positive),max(negative)
    mass_plus = sum(r*n for r,n in positive.items())
    mass_minus = sum(r*n for r,n in negative.items())
    need(a>b and 0<mass_plus<=mass_minus, "No ordered-rank/mass exclusion certificate")
    return {"positive_rank_mass":mass_plus,"negative_rank_mass":mass_minus,
            "min_positive_rank":a,"max_negative_rank":b}


def validate(candidate, expected):
    for key,value in expected.items():
        need(candidate.get(key)==value,"Changed frozen contract: "+key)


def main():
    manifest = json.loads((HERE/"SOURCES.json").read_text())
    for item in manifest["files"]:
        need(sha256((HERE/item["snapshot"]).read_bytes()).hexdigest()==item["sha256"],"Frozen input changed")
    source = (HERE/"frozen/research__coded-native-caller__PHYSICAL.md").read_text()
    profiles = [ast.literal_eval(x) for x in re.findall(r"\{[0-9:, \n]+\}",source)]
    p = next(x for x in profiles if set(x)=={1,2,3,4,5})
    h = next(x for x in profiles if set(x)=={4,7,8,9})
    need(p=={1:2201,2:412,3:510,4:127,5:40},"Literal cheaper source paid profile")
    need(h=={4:28,7:7,8:47,9:326},"Literal autonomous helper profile")
    identity = tuple(range(4)),(0,0,0,0)
    word = identity
    for label in (1,2,0):
        word=product(stage(label),word)
    expected_perm=product(stage(2),stage(1))[0]
    need(word==(expected_perm,(1,1,1,0)),"Terminal anchor word equals PtPsD0DsDt; Q untouched")
    source_rank=8*sum(word[1][:3])+word[1][3]
    need(source_rank==24,"No unearned central Gaussian axis")
    # Source three-stage contract, not a census of all p or general callers.
    targets=Counter({r:3*n for r,n in h.items()})
    targets[source_rank]+=224
    paid={r:3*n for r,n in p.items()}
    profile=signed(targets,paid)
    cert=separation(profile)
    need(cert=={"positive_rank_mass":15453,"negative_rank_mass":15453,
                "min_positive_rank":7,"max_negative_rank":5},"Exact separated mass certificate")
    need(sum(h.values())==408 and 3*sum(h.values())==1224,"Helpers exactly once per fresh FULL")
    need(sum(r*n for r,n in p.items())==5263,"Complete local paid rank mass")
    need(sum(r*n for r,n in h.items())==3471,"Complete helper rank mass")
    need(profile[4]==-297,"Cancel84H4 against381H4, leaving297H4 paid")
    author=json.loads((HERE/"frozen/DESIGN-RESULT.json").read_text())
    expected={"source_head":"b893ba6bd6c77c6e7efc48acb6f448218df671b7",
              "full_calls":3,"main_source_owners":224,"fresh_helper_owners":1224,
              "actual_unmixed_main_bank_owners":112,"unrealized_main_target_grant":224,
              "ambient_axes":25,"granted_main_target_rank":24,
              "inserted_moving_main_maps":448,"boundary_normalization_maps_maximum":224,
              "native_paid_profile":{str(r):n for r,n in p.items()},
              "native_helper_profile":{str(r):n for r,n in h.items()},
              "optimistic_target_profile":{str(r):n for r,n in targets.items()},
              "paid_profile":{str(r):n for r,n in paid.items()},
              "signed_moment_profile":{str(r):n for r,n in profile.items()},
              "new_kappa":None,"native_emitter_executed":False,"compiler_executed":False}
    validate(author,expected)
    a,b=map(Q,author["comparison_domain"])
    need(0<a<=b<1,"Required comparison domain lies in positive-saving regime")
    rejected=[]
    mutations=[("free_Q_rank25",{"granted_main_target_rank":25}),
               ("448_maps_as448_owners",{"main_source_owners":448}),
               ("new_main_owners_per_FULL",{"unrealized_main_target_grant":672}),
               ("anchor_axes_as8_owners",{"main_source_owners":232}),
               ("duplicate_helper_reward",{"fresh_helper_owners":2448}),
               ("omit_terminal_FULL_native_bill",{"paid_profile":{str(r):2*n for r,n in p.items()}}),
               ("omit_one_rank1_child",{"paid_profile":dict(expected["paid_profile"],**{"1":6602})})]
    for name,patch in mutations:
        try:
            validate(dict(author,**patch),expected)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("Failed contract mutant:"+name)
    # UnearnedQ changes the moment, not just metadata: it adds224rank mass.
    wrong_q=Counter(targets)
    wrong_q[24]-=224
    wrong_q[25]+=224
    need(sum(r*n for r,n in signed(wrong_q,paid).items())==224,"FreeQ changes problem")
    try:
        separation(signed(wrong_q,paid))
    except ValueError:
        rejected.append("free_Q_breaks_equal_mass_certificate")
    else:
        raise ValueError("Rank25 mutation accepted by separation certificate")
    one_bank=Counter(targets)
    one_bank[24]-=112
    one_cert=separation(signed(one_bank,paid))
    need(one_cert["positive_rank_mass"]<one_cert["negative_rank_mass"],"Actual one-bank offer is strictly worse")
    repeated=identity
    for label in (1,1,1):
        repeated=product(stage(label),repeated)
    need(sum(e%2 for e in repeated[1][:3])*8==8,"Repeated-stage control cannot use24Gaussian rank")
    out={"status":"PASS_INDEPENDENT_SCOPED_P3_MOVING_ANCHOR_CEILING",
         "source_head":manifest["source_head"],"source_files_authenticated":len(manifest["files"]),
         "source_bound_full_calls":3,"all_p_source_admission_claimed":False,
         "word_normal_form":{"permutation":word[0],"Gaussian_block_exponents":word[1]},
         "targets_optimistic_two_bank_grant":dict(targets),"paid_recursive_lower":paid,
         "cancelled_signed_profile":profile,"rank_separation_certificate":cert,
         "exact_symbolic_bound":"M(C)<=15453*(7^(-C)-5^(-C))<0 for C>0",
         "retained_route_domain":"0<C<1","comparison_domain":[str(a),str(b)],
         "C_zero_rank_mass_margin":sum(r*n for r,n in profile.items()),
         "actual_one_bank_separation":one_cert,"contract_mutants_rejected":rejected,
         "native_or_emitter_or_compiler_run":False,"root_digits_computed":False,"new_kappa":None}
    print(json.dumps(out,indent=2,sort_keys=True))


if __name__=="__main__":
    main()

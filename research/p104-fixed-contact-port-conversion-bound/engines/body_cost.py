"""Directed bound for separate rank-eight body completion on two returned owners."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

PINS = {
    "R170 result": "6fa14902c5b6db89fa5d55c61451d754821116422960e014b6cccaaab8b179cf",
    "directed pricing": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "benchmark stock": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
}


def unique(items):
    d=dict(items)
    assert len(d)==len(items), "Duplicate JSON key"
    return d


def pinned(path, name):
    raw=path.read_bytes()
    assert sha256(raw).hexdigest()==PINS[name], name
    return raw


def timeout(*_):
    raise TimeoutError("15-second independent body-price cap")


def main():
    assert __debug__
    p=ArgumentParser(description=__doc__)
    p.add_argument("r170",type=Path)
    p.add_argument("pricing",type=Path)
    p.add_argument("stock",type=Path)
    args=p.parse_args()
    signal(SIGALRM,timeout)
    alarm(15)
    r170=loads(pinned(args.r170,"R170 result"),object_pairs_hook=unique)
    pinned(args.pricing,"directed pricing")
    base=loads(pinned(args.stock,"benchmark stock"),object_pairs_hook=unique)
    assert base["head"]==r170["comparator"] and base["caller_head"]==r170["caller_head"]
    b=r170["price"]
    a,bp=(b["per_port_paid"][kind] for kind in ("A","B"))
    before_minus_after={int(r):bp.get(r,0)-a.get(r,0) for r in a.keys()|bp.keys() if bp.get(r,0)!=a.get(r,0)}
    assert before_minus_after=={1:-4,8:30,9:4}
    assert b["per_port_target"]["A"]==b["per_port_target"]["B"]
    assert b["optimistic_lost_rank_one_helpers_per_port"]==34
    calls=b["optimistic_lost_rank_one_helpers_per_port"]//2
    assert calls==17
    necessary_rank=8
    helper_completion = {
        int(r):max(0,necessary_rank-int(r)) for r in b["native_helpers"]
    }
    assert list(sorted(helper_completion))==list(range(1,10))
    charged=before_minus_after.copy()
    charged[8]-=2*calls
    assert charged=={1:-4,8:-4,9:4}
    cost=run_path(str(args.pricing))["cost"]
    quote={}
    for label in ("old_crossing_upper","probe","moonshot"):
        k=Q(base[label])
        assert 0<k<1
        lo,hi=cost(charged,k)
        assert lo<=hi<0
        assert cost(before_minus_after,k)[0]>0
        # r=8 is the minimum in the optimistic real-power bound; the
        # limiting equality needs no complementary job on that lane.
        # The universal proof in PROOF.md uses strict concavity and row support.
        body={}
        for r,d in sorted(helper_completion.items()):
            if d:
                split={r:2} if d==r else {r:1,d:1}
                split[8]=-1
                extra=cost(split,k)
                assert extra[0]>0
            elif r!=8:
                extra=cost({r:1,8:-1},k)
                assert extra[0]>0
            else:
                extra=(Q(0),Q(0))
            body[r]=[str(x) for x in extra]
        quote[label]={"kappa":str(k),"one_port_optimistic_relaxation_bounds":[str(lo),str(hi)],
                      "strict_upper_for_port_multiplicities_1_to_8":{m:str(m*hi) for m in range(1,9)},
                      "minimum_concavity_loss_by_helper_rank":body}
    alarm(0)
    print(dumps({"comparator":base["head"],"caller_head":base["caller_head"],"pins":PINS,
                 "before_minus_after_paid_one_port":before_minus_after,
                 "separate_required_body_ranks_per_call":[8,8],"calls":calls,
                 "charged_signed_delta_upper":charged,"quote":quote,"case_caps":{"ports":8,"rank_choices":9,"seconds":15},
                 "scope":"Each extra full body return separately consumes one complete original rank-r helper target and its own monomial-wrapped paid top-ups. No cross-lane body sharing. Grants the phase repairs free."},
                sort_keys=True,indent=2))


if __name__=="__main__":
    main()

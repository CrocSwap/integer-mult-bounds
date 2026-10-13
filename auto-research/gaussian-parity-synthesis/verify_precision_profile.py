"""Source-pinned completed-child precision charges for the PR46 complex list.

This changes the semantic denominator/magnitude enclosure of completed C
children. It does not change the child list, recursive costs, scalar E, or kappa.
The conversion lemma, recursive finite tensor execution and arbitrary-width
accounting have Lean certificates. Physical frame/tape compilation is separate.
"""
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
import argparse, json


def audit(path):
    if not __debug__: raise RuntimeError('run this exact audit without Python -O')
    data=json.loads(path.read_text())
    rows=data['child_width_multiplicities']
    source=path.parent/'references/pr46'/data['source_path']
    assert sha256(source.read_bytes()).hexdigest()==data['source_sha256'], 'pinned certificate changed'
    original=json.loads(source.read_text())
    assert rows==original['complex']['child_width_multiplicities'], 'profile differs from pinned certificate'
    assert len(rows)==29 and len({r for r,n in rows})==29
    assert all(type(r) is int and type(n) is int and 0<r<784 and n>0 for r,n in rows)
    rank=sum(r*n for r,n in rows)
    odd=sum(n for r,n in rows if r%2)
    charge=sum(((r+1)//2)*n for r,n in rows)
    assert rank==421548223824 and odd==1142904672 and charge==211345564248
    assert charge==(rank+odd)//2
    # The exact all-f formula follows by splitting f into its two parities.
    # Lean separately proves the upper bound for every f, not just this loop.
    for f in range(1025):
        exact=sum(((r*f+1)//2)*n for r,n in rows)
        assert exact==(rank*f+odd*(f%2))//2
        assert exact<=charge*f
    return dict(status='passed',source_commit=data['source_commit'],
        source_path=data['source_path'],source_sha256=data['source_sha256'],
        profile_sha256=sha256(path.read_bytes()).hexdigest(),classes=len(rows),
        child_calls=sum(n for r,n in rows),old_completed_child_charge=rank,
        binary_conversion_charge=charge,odd_child_calls=odd,
        saving=rank-charge,saving_fraction=str(Q(rank-charge,rank)),
        saving_percent=float(Q(100*(rank-charge),rank)),
        exact_formula='charge(f)=(421548223824*f+1142904672*(f mod 2))/2',
        all_width_bound='charge(f)<=211345564248*f',
        pi_composition_charge='ceil(421548223824*f/2) when one common pi tag is retained throughout',
        scalar_E_and_global_guard_unchanged=True,exponent_changed=False,
        scope='completed-child precision component only; not memory, total guard, physical runtime or kappa')


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--profile',type=Path,
        default=Path(__file__).with_name('community-complex-profile.json'))
    a=ap.parse_args();print(json.dumps(audit(a.profile),indent=2))

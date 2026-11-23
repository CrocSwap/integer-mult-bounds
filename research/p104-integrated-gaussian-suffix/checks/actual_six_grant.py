"""Check one prospective source-to-receiver grant at actual H=1024 precision."""

from argparse import ArgumentParser
from datetime import datetime, timezone
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json
import sys


def level(band, lower):
    cap = F(lower)
    result = 0
    while cap*F(6,5) <= band:
        cap *= F(6,5)
        result += 1
    return result


def main():
    parser = ArgumentParser()
    parser.add_argument("--base-runtime",type=Path,
                        default=Path(__file__).resolve().parents[1]/"source/installed-8072/runtime")
    args = parser.parse_args()
    sys.path.insert(0,str(args.base_runtime.resolve()))
    started = datetime.now(timezone.utc).isoformat()
    from upstream import install
    install()
    from grades import WEIGHTS, numerical_recipe
    from transport import Measure
    H,L = 1024,1054
    M = 1<<H
    volume,K = M**6,M**82
    r,k = 96,130
    e,d = 1642,1214
    qrecipe = numerical_recipe(H)
    assert (r,k) in qrecipe.cells
    left,right = max(e,F(d*k,r)),min(e+2,F((d+2)*k,r))
    assert right-left==F(1,24)
    source_level,target_level = level(e,L),level(d,L)
    assert source_level>target_level
    lo,hi = Measure(1-qrecipe.trial,volume,max(256,64*M.bit_length())).mass(left,right)
    records=[]
    for (a,raw_r,b,raw_k), share in qrecipe.typed_cells().items():
        if (raw_r,raw_k)!=(r,k):
            continue
        j = next(j for j,v in enumerate(qrecipe.paid.variants[a]) if v==r)
        i = next(i for i,v in enumerate(qrecipe.targets.variants[b]) if v==k)
        per_owner = share/qrecipe.targets.variants[b].histogram[k]
        actual = int(WEIGHTS[a]*lo*per_owner)
        assert 0<actual<=WEIGHTS[a]*hi*per_owner<actual+2
        assert j*(2**19)**source_level<K
        assert len(qrecipe.paid.variants[b])*(2**19)**target_level<=(2**19)**source_level
        suffixes = {s:r*(e-s)-k*(d-s) for s in (4,6,8)}
        assert suffixes=={4:-52,6:16,8:84}
        records.append(dict(sender=a,paid_port=j,recipient=b,target_port=i,
                            floored_grant_bit_length=actual.bit_length(),
                            floored_grant_sha256=sha256(str(actual).encode()).hexdigest(),
                            suffixes=suffixes))
    assert records
    result=dict(started_at=started,finished_at=datetime.now(timezone.utc).isoformat(),H=H,L=L,
                sender_band=e,recipient_band=d,r=r,k=k,source_level=source_level,recipient_level=target_level,
                overlap=[str(left),str(right)],precision_bits=64*M.bit_length(),records=records)
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()

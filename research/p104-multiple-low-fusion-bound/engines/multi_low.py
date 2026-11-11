"""One paid pair fusion with a full simultaneous low-chart bank."""
from collections import Counter
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import sys
from time import monotonic

PINS={
 "frontier/BANKS.json":"9b17806949c347926b7f95bb70d207e89ca3ed1c6cf78f6729652b3728993c01",
 "inputs/ADMITTED.json":"c95300e9bca27e44a25c82d794f88cbf70757c142806b0e4c590ea29feb81a13",
 "inputs/R68.json":"ce9604444161b3532d02eb788cb3a24fbbdaf4c1354d596ac08a2c9edeb72c76",
 "inputs/R69.json":"a2dd10737f5bfbd3818e6766df3890e445fd46f661af9521f5d724b7c56c1d45",
 "inputs/R70.json":"34738b6d9031b3170a58f0cb590d81c01ea2c1038810008483d1c24dc7574150",
 "inputs/RANK-STOCK.json":"4a7841699dd17688f6aada5c902a2a91e94558b2b1b4460c46b0e55aa95b3f9f",
 "inputs/WORD.json.gz":"4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
 "lead/local.py":"4397fb4e2bf5a36f58e7732e8d9c5500d24d91a0ef0d8a1e3941e447ceaf495e",
 "lead/rank.py":"e1b081552812a4132a20a2c062cf3d5c119e45292c5ef55bf25372adb21cf240",
}
HEAD="aaeec8c0acf01e99a5f331ef363a698d9c084ace"


def validate(root):
    data={}
    for name,sha in PINS.items():
        raw=(root/name).read_bytes()
        if sha256(raw).hexdigest()!=sha:
            raise ValueError(f"changed dependency: {name}")
        data[name]=raw
    return data


def solve(M,h,L,q,ratio,combine,legal):
    dims=M.keys()-{h}
    beta=ratio({r:M[h][r] for r in dims},{r:M[q][r] for r in dims})
    if beta is None:
        return dict(status="high readout exterior rank obstruction")
    alpha=M[h][h]-beta*M[q][h]
    if not alpha:
        return dict(status="only zero retained multiplier")
    assert all(M[h][i]==alpha*int(i==h)+beta*M[q][i] for i in M)
    ext=M.keys()-{h,q}
    weights,residue=combine({l:{i:M[i][l] for i in ext} for l in L},
                            {i:-M[i][h] for i in ext})
    if weights is None:
        return dict(status="full low exterior rank obstruction",residue={i:str(x) for i,x in residue.items()})
    v={i:M[i][h]+sum(a*M[i][l] for l,a in weights.items()) for i in M}
    assert all(not v[i] for i in ext)
    if len(weights)<2:
        return dict(status="single low witness requires predecessor reconciliation")
    if len(weights)+bool(v[q])+bool(beta)+(alpha!=1)>6 or not all(legal(x) for x in (alpha,1/alpha,beta,v[q],*weights.values())):
        return dict(status="coefficient or ordinary budget unresolved")
    return dict(status="survives",alpha=str(alpha),beta=str(beta),high_correction=str(v[q]),
                discarded_aux=str(v[h]),low_weights={i:str(x) for i,x in weights.items()})


def main():
    root=Path(sys.argv[1])
    data=validate(root)
    get=lambda name:json.loads(data[name])
    stock=get("frontier/BANKS.json")
    admit=get("inputs/ADMITTED.json")
    price=get("inputs/RANK-STOCK.json")
    assert stock["head"]==admit["head"]==price["head"]==HEAD and admit["exit"]==0
    local=run_path(str(root/"lead/local.py"))
    algebra=run_path(str(root/"lead/rank.py"))
    ratio,combine,legal=local["ratio"],algebra["combination"],local["legal"]
    toy={r:{i:Q(int(i==r or (i==0 and r!=0))) for i in range(4)} for r in range(4)}
    test=solve(toy,0,[1,2],3,ratio,combine,legal)
    assert test["status"]=="survives" and test["low_weights"]=={1:"-1",2:"-1"}
    assert solve(toy,0,[1],3,ratio,combine,legal)["status"]=="full low exterior rank obstruction"
    if sys.argv[2:]==["--controls-only"]:
        print("PASS exact two-peer and missing-axis controls")
        return
    deadline=monotonic()+13
    geometries=[get("inputs/R68.json"),get("inputs/R69.json")]
    sites={r["key"]:r for d in geometries for r in d["survivors"]}
    inherited={tuple(r["key"]):r["status"] for r in get("inputs/R70.json")["outcomes"]}
    w=json.loads(decompress(data["inputs/WORD.json.gz"]))
    answered=[]
    for i,row in enumerate(stock["rows"]):
        if monotonic()>=deadline or i==8:
            break
        g=sites[row["key"]]
        h,q=row["h"],row["high"][0]
        assert g["h"]==h and g["low"]==row["low"] and g["high"]==[q] and g["clock"]==row["cut"]
        margin=price["rank_prices"][row["rank_type"]]["complete_margin"]
        assert Q(margin[0])>0
        if row["prior_readout_excluded"]:
            assert any(inherited.get((h,*g["move_clocks"],g["clock"],l,q))=="dirty return readout failed"
                       for l in row["low"])
            status=dict(status="high readout exterior rank obstruction",route="retained exact R70 obstruction")
        else:
            matrix=local["local_operator"](w["program"],g)
            status=solve(matrix,h,row["low"],q,ratio,combine,legal)|dict(route="fresh exact support")
        answered.append(row|status|dict(complete_margin=margin))
    print(json.dumps(dict(head=HEAD,pins=PINS,case_cap=8,seconds=13,decisions=answered,
           counts=dict(Counter(r["status"] for r in answered)),unvisited=stock["rows"][len(answered):],
           survivors=[r for r in answered if r["status"]=="survives"],
           controls=["exact two-peer control","missing-axis negative"]),
           sort_keys=True,indent=2))


if __name__=="__main__":
    main()

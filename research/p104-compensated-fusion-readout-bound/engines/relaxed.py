"""Exact paired block identities for a candidate virtual-zero public fusion."""
from collections import Counter
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys
from time import monotonic

HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
WORD = "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
PRICE = "4a7841699dd17688f6aada5c902a2a91e94558b2b1b4460c46b0e55aa95b3f9f"
CAP, SECONDS = 1197, 32


def checked(path, digest):
    data = Path(path).read_bytes()
    if sha256(data).hexdigest() != digest:
        raise ValueError(f"changed input: {Path(path).name}")
    return data


def local_operator(tape, row):
    roles = row["roles"]
    middle = row["chart_path"][1]
    matrix = {r:{q:Q(int(r==q)) for q in roles} for r in roles}
    for t in row["block"]:
        op, d, *a = tape[t]
        assert a[-1] == middle and op in ("ADD","SCALE")
        c = Q(a[-2])
        assert c and d in matrix
        if op == "SCALE":
            matrix[d] = {j:c*x for j,x in matrix[d].items()}
        else:
            s = a[0]
            assert s in matrix and s!=d
            matrix[d] = {j:matrix[d][j]+c*matrix[s][j] for j in roles}
    return matrix


def ratio(left, right):
    pivot = next((i for i in right if right[i]), None)
    if pivot is None:
        return Q(0) if not any(left.values()) else None
    q = left[pivot]/right[pivot]
    return q if all(left[i]==q*right[i] for i in left) else None


def legal(q):
    denominator = q.denominator
    for p in (2,3,5):
        while denominator%p==0:
            denominator//=p
    return denominator == 1 and abs(q.numerator) <= 64 and q.denominator <= 1125*32


def solve(M, h, p, q, high):
    exterior = M.keys() - (set(high) | {h})
    lam = ratio({r:-M[r][h] for r in exterior}, {r:M[r][p] for r in exterior})
    if lam is None:
        return "nonlocal forward leakage", None
    raw = {r:v for r in M if (v:=M[r][h]+lam*M[r][p])}
    discarded = raw.pop(h,Q(0))
    assert set(raw)<=set(high)
    outside_h = M.keys() - {h}
    beta = ratio({r:M[h][r] for r in outside_h},
                 {r:M[q][r] if q is not None else Q(0) for r in outside_h})
    if beta is None:
        return "dirty return readout failed", None
    alpha = M[h][h] - (beta*M[q][h] if q is not None else 0)
    if not alpha:
        return "zero retained multiplier", None
    assert all(M[h][r] == alpha*int(r==h)+(beta*M[q][r] if q is not None else 0) for r in M)
    if (len(raw)+bool(lam)+bool(beta)+(alpha!=1)>6 or
            any(not legal(v) for v in (lam,alpha,1/alpha,beta,*raw.values()))):
        return "coefficient or ordinary-count gate", None
    return "survives", dict(low_peer=p, readout=q, lam=str(lam), alpha=str(alpha),
                            beta=str(beta), discarded_aux_output=str(discarded),
                            image={r:str(v) for r,v in raw.items()})


def controls():
    # ADD high from h followed by a nonzero SCALE on h, an invertible block.
    M = {0:{0:Q(2),1:Q(0)},1:{0:Q(1),1:Q(1)}}
    status, found = solve(M,0,1,None,[1])
    assert status=="survives" and found["alpha"]=="2" and found["image"]=={1:"1"}
    assert found["discarded_aux_output"]=="2"
    bad={r:a.copy() for r,a in M.items()}
    bad[0][1] = Q(1)
    assert solve(bad,0,1,None,[1])[0]=="dirty return readout failed"
    M[2]={0:Q(1),1:Q(0),2:Q(1)}
    for r in (0,1): M[r][2]=Q(0)
    assert solve(M,0,1,None,[1])[0]=="nonlocal forward leakage"
    return ["invertible block with nonzero discarded output", "nonunit retained readout",
            "wrong readout rejected", "nonlocal leakage rejected"]


def check(word, geometry):
    checks=controls()
    deadline=monotonic()+SECONDS
    tape=word["program"]
    rows=[]
    for site in geometry["survivors"]:
        h=site["h"]
        assert h in site["roles"] and h not in site["high"] and h not in site["low"]
        for p in site["low"]:
            for q in [None,*site["high"]]:
                rows.append((site,p,q))
    outcomes=[]
    passed=[]
    for i,(site,p,q) in enumerate(rows):
        if i==CAP or monotonic()>=deadline:
            break
        M=local_operator(tape,site)
        status, witness=solve(M,site["h"],p,q,site["high"])
        key=[site["h"],*site["move_clocks"],site["clock"],p,q]
        outcomes.append(dict(key=key,status=status))
        if witness:
            passed.append(site|witness)
    unresolved=[[s["h"],*s["move_clocks"],s["clock"],p,q] for s,p,q in rows[len(outcomes):]]
    return dict(outcomes=outcomes, dispositions=dict(Counter(r["status"] for r in outcomes)),
                survivors=passed, unresolved=unresolved, cap=CAP, seconds=SECONDS, controls=checks)


def main():
    if sys.argv[1:] == ["--controls-only"]:
        print(controls())
        return
    price_path, first_path, last_path, word_path = sys.argv[1:]
    price=json.loads(checked(price_path,PRICE))
    assert price["head"]==HEAD
    pins = {
      first_path:"ce9604444161b3532d02eb788cb3a24fbbdaf4c1354d596ac08a2c9edeb72c76",
      last_path:"a2dd10737f5bfbd3818e6766df3890e445fd46f661af9521f5d724b7c56c1d45",
    }
    rows=[]
    for path,digest in pins.items():
        geometry=json.loads(checked(path,digest))
        assert geometry["comparator_head"]==HEAD and geometry["price_sha256"]==PRICE
        assert geometry["admission_sha256"]=="c95300e9bca27e44a25c82d794f88cbf70757c142806b0e4c590ea29feb81a13"
        rows.extend(geometry["survivors"])
    assert len(rows)==456 and sum(len(r["low"])*(1+len(r["high"])) for r in rows)==CAP
    assert len({r["key"] for r in rows})==456
    word=json.loads(gzip.decompress(checked(word_path,WORD)))
    result=check(word,{"survivors":rows})
    result.update(head=HEAD,price_sha256=PRICE,geometry_sha256=list(pins.values()),word_sha256=WORD)
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()

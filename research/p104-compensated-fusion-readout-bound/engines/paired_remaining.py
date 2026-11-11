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
CAP, SECONDS = 1193, 32


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
    # Exterior includes h, as in #7334. The physical helper bypasses B.
    exterior = M.keys() - set(high)
    lam = ratio({r:-M[r][h] for r in exterior}, {r:M[r][p] for r in exterior})
    if lam is None:
        return "exterior forward leakage", None
    image = {r:v for r in M if (v:=M[r][h]+lam*M[r][p])}
    assert set(image)<=set(high)
    rhs = {r:Q(int(r==h))-M[h][r] for r in M}
    mu = ratio(rhs, M[q] if q is not None else dict.fromkeys(M, Q(0)))
    if mu is None:
        return "dirty return readout failed", None
    assert all(M[h][r]+(mu*M[q][r] if q is not None else 0)==int(r==h) for r in M)
    if len(image)+bool(lam)+bool(mu)>6 or any(not legal(v) for v in (lam,mu,*image.values())):
        return "coefficient or ordinary-count gate", None
    return "survives", dict(low_peer=p, readout=q, lam=str(lam), mu=str(mu),
                            image={r:str(v) for r,v in image.items()})


def controls():
    # Two simple column/row identities: M(e0-e1)=e1, e0^T M+e1^T M=e0^T.
    M = {0:{0:Q(0),1:Q(0)},1:{0:Q(1),1:Q(0)}}
    status, found = solve(M,0,1,1,[1])
    assert status=="survives" and found["mu"]=="1" and found["image"]=={1:"1"}
    bad={r:a.copy() for r,a in M.items()}
    bad[0][0] = Q(2)
    assert solve(bad,0,1,1,[1])[0]=="exterior forward leakage"
    bad={r:a.copy() for r,a in M.items()}
    bad[1][0] = Q(0)
    assert solve(bad,0,1,1,[1])[0]=="dirty return readout failed"
    return ["paired signed identity", "unrouted output rejected", "dirty return rejected"]


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
    price_path, geometry_path, geometry_sha, word_path = sys.argv[1:]
    price=json.loads(checked(price_path,PRICE))
    assert price["head"]==HEAD
    geometry=json.loads(checked(geometry_path,geometry_sha))
    assert geometry["comparator_head"]==HEAD and geometry["price_sha256"]==PRICE
    assert geometry["admission_sha256"]=="c95300e9bca27e44a25c82d794f88cbf70757c142806b0e4c590ea29feb81a13"
    word=json.loads(gzip.decompress(checked(word_path,WORD)))
    result=check(word,geometry)
    result.update(head=HEAD,price_sha256=PRICE,geometry_sha256=geometry_sha,word_sha256=WORD)
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()

"""Exact full high-bank readout, conditioned on an existing exterior solution."""
from fractions import Fraction as Q
from collections import Counter
from hashlib import sha256
from pathlib import Path
import gzip
import json
import runpy
import sys
from time import monotonic

STOCK="34738b6d9031b3170a58f0cb590d81c01ea2c1038810008483d1c24dc7574150"


def combination(rows,target):
    basis = {}
    def eliminate(vector, terms):
        for k,(row, weights) in sorted(basis.items()):
            q=vector.get(k,0)
            if not q:
                continue
            for j,v in row.items():
                x=vector.get(j,0)-q*v
                if x: vector[j]=x
                else: vector.pop(j,None)
            for j,v in weights.items():
                x=terms.get(j,0)-q*v
                if x: terms[j]=x
                else: terms.pop(j,None)
        return vector,terms
    for label,row in rows.items():
        vector,terms=eliminate({i:x for i,x in row.items() if x},{label:Q(1)})
        if vector:
            k=min(vector);pivot=vector[k]
            basis[k]=({i:x/pivot for i,x in vector.items()},{i:x/pivot for i,x in terms.items()})
    residual,term=eliminate({i:x for i,x in target.items() if x},{})
    return (None, residual) if residual else ({i:-x for i,x in term.items()},{})


def main():
    price, g1, g2, prior, word = map(Path,sys.argv[1:])
    previous=runpy.run_path(str(Path(__file__).with_name("relaxed.py")))
    checked=previous["checked"]
    assert json.loads(checked(price,previous["PRICE"]))["head"]==previous["HEAD"]
    p=json.loads(checked(prior,STOCK))
    geometry=[json.loads(checked(path,h)) for path,h in zip((g1,g2),p["geometry_sha256"],strict=True)]
    sites={(s["h"],*s["move_clocks"],s["clock"]):s for x in geometry for s in x["survivors"]}
    keys=sorted({tuple(i["key"][:-1]) for i in p["outcomes"] if i["status"]=="dirty return readout failed"
                 and len(sites[tuple(i["key"][:4])]["high"])>1})
    assert len(keys)<=46 and keys
    w=json.loads(gzip.decompress(checked(word,previous["WORD"])))
    assert combination({1:{0:Q(1),1:Q(1)},2:{0:Q(1),1:Q(-1)}},{0:Q(2)})[0]=={1:Q(1),2:Q(1)}
    assert combination({1:{0:Q(1)}},{1:Q(1)})[0] is None
    deadlines=monotonic()+18
    outcomes=[]
    candidates=[]
    for key in keys:
        if monotonic()>=deadlines:
            break
        site=sites[key[:4]]
        h,peer=key[0],key[-1]
        high=site["high"]
        M=previous["local_operator"](w["program"],site)
        exterior=M.keys()-(set(high)|{h})
        lam=previous["ratio"]({i:-M[i][h] for i in exterior},{i:M[i][peer] for i in exterior})
        assert lam is not None
        raw={i:x for i in high if (x:=M[i][h]+lam*M[i][peer])}
        restricted={q:{i:x for i,x in M[q].items() if i!=h} for q in high}
        beta,remainder=combination(restricted,{i:x for i,x in M[h].items() if i!=h})
        if beta is None:
            outcomes.append(dict(key=key,status="exterior readout rank obstruction",residual={i:str(x) for i,x in remainder.items()}))
            continue
        alpha=M[h][h]-sum(x*M[q][h] for q,x in beta.items())
        if not alpha:
            rhs=M[h]|{h:M[h][h]-1}
            beta,remainder=combination({q:M[q] for q in high},rhs)
            if beta is None:
                outcomes.append(dict(key=key,status="all readouts have zero retained multiplier"))
                continue
            alpha=Q(1)
        assert all(M[h][i]==alpha*int(i==h)+sum(x*M[q][i] for q,x in beta.items()) for i in M)
        coeff=[alpha,1/alpha,lam,*beta.values(),*raw.values()]
        if len(beta)+len(raw)+bool(lam)+(alpha!=1)>6 or not all(previous["legal"](q) for q in coeff):
            outcomes.append(dict(key=key,status="coefficient or ordinary-count gate unresolved"))
            continue
        outcomes.append(dict(key=key,status="survives"))
        candidates.append(site|dict(low_peer=peer,lam=str(lam),alpha=str(alpha),
                                    beta={q:str(x) for q,x in beta.items()},image={q:str(x) for q,x in raw.items()}))
    print(json.dumps(dict(head=previous["HEAD"],word_sha256=previous["WORD"],prior_sha256=STOCK,
                          price_sha256=previous["PRICE"],outcomes=outcomes,survivors=candidates,
                          counts=dict(Counter(r["status"] for r in outcomes)),unvisited=keys[len(outcomes):],
                          controls=["full-rank combination","missing coordinate rejected"]),indent=2,sort_keys=True))


if __name__=="__main__":
    main()

"""Exact first-order cross-copy BIT rank and directed price exclusion."""
from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys

PINS = {
    "bit/EFREE-CALLER.json.gz": "757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b",
    "bit/EFREE-RESULT.json": "a46b6c6040f75184cab5467656811ad988c216e3bc8e44d595a5015b6e49620b",
    "bit/retained/inputs/BIT-NATIVE-WORD.json.gz": "51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78",
    "bit/independent/interval_gate.py": "8dc2bc4c64cba3f83c664373984a075f1a14b4d53958084091345c8cab189dec",
}
TARGET = Fraction("0.0040075385047236")


def auth(root, key):
    blob = (root / key).read_bytes()
    if sha256(blob).hexdigest() != PINS[key]:
        raise ValueError(f"SHA-256 mismatch: {key}")
    return blob


def load_json(root,key):
    blob=auth(root,key)
    return json.loads(gzip.decompress(blob) if key.endswith(".gz") else blob)


def bits(x):
    while x:
        v=x & -x
        yield v.bit_length()-1
        x^=v


def mul(a,b):
    result=[]
    for r in a:
        y=0
        for j in bits(r):
            y^=b[j]
        result.append(y)
    return result


def rank(rows):
    p={}
    for r in rows:
        while r:
            j=r.bit_length()-1
            if j not in p:
                p[j]=r
                break
            r^=p[j]
    return len(p)


def plus(a,b):
    return [r^s for r,s in zip(a,b,strict=True)]


def diag(size,entries=None):
    if entries is None:
        entries=range(size)
    return [1<<i if i in entries else 0 for i in range(size)]


def outer(column,row,size):
    return [row if column>>i&1 else 0 for i in range(size)]


def columns_to_rows(columns,size):
    return [sum(1<<j for j,c in enumerate(columns) if c>>i&1) for i in range(size)]


def inverse(a):
    size=len(a)
    rows=[r|(1<<(i+size)) for i,r in enumerate(a)]
    for i in range(size):
        j=next(j for j in range(i,size) if rows[j]>>i&1)
        rows[i],rows[j]=rows[j],rows[i]
        for j in range(size):
            if i!=j and rows[j]>>i&1:
                rows[j]^=rows[i]
    return [r>>size for r in rows]


def toy_stage(full_size, private, k, u, number_shared):
    a,b,c,d=[1<<i for i in private]
    local, idle = (([k,a,b,c],[u,d]) if number_shared==1 else ([a,b,c,d],[u,k]))
    all_columns=local+idle+[1<<i for i in range(full_size) if i not in {0,1,*private}]
    full_basis=columns_to_rows(all_columns,full_size)
    forms=inverse(full_basis)[:6]
    output=columns_to_rows(local+idle,full_size)
    target=diag(full_size,{0,1,*private})
    assert mul(output,forms)==target and mul(forms,output)==diag(6)
    # Two native rank-one square-zero factors, each embedded in two local lanes.
    X=columns_to_rows([local[0]^local[1],local[2]^local[3]],full_size)
    Y=[forms[0]^forms[1],forms[2]^forms[3]]
    P=outer(u,forms[4],full_size)
    Q=outer(idle[1],forms[5],full_size)
    assert mul(Y,X)==[0,0]
    assert all(mul(g,X)==[0]*full_size and mul(Y,g)==[0,0] for g in (P,Q))
    return X,Y,P,Q,target


def controls():
    size=12
    E=diag(size,{0,1})
    observations=[]
    for u in (1,2,3):
        for form in (1,2,3):
            if (u&form).bit_count()%2!=1:
                continue
            k=next(x for x in (1,2,3) if (x&form).bit_count()%2==0)
            for left_shared,right_shared in ((1,1),(2,1),(1,2),(2,2)):
                left=toy_stage(size,(2,3,4,5),k,u,left_shared)
                right=toy_stage(size,(6,7,8,9),k,u,right_shared)
                X_s,Y_s,P_s,Q_s,T_s=left
                X_t,Y_t,P_t,Q_t,T_t=right
                assert P_s==P_t==outer(u,form,size)
                assert mul(E,mul(P_s,E))==P_s and mul(P_s,P_s)==P_s
                assert mul(T_s,T_t)==E
                if left_shared==2:
                    assert plus(P_s,Q_s)==E and not any(mul(P_s,Q_s))
                if right_shared==2:
                    assert plus(P_t,Q_t)==E and not any(mul(P_t,Q_t))
                X=[a|(b<<2) for a,b in zip(X_s,X_t,strict=True)]
                Y=Y_s+Y_t
                ab,ba=mul(Y_s,X_t),mul(Y_t,X_s)
                assert ab==mul(Y_s,mul(E,X_t)) and ba==mul(Y_t,mul(E,X_s))
                expect=1 if left_shared==right_shared==1 else 0
                assert rank(ab)==rank(ba)==expect
                a=plus(diag(4),mul(Y,X))
                m=plus(diag(size),mul(X,Y))
                assert rank(a)==4-expect and rank(m)==size-4+rank(a)
                observations.append({"shared_each_side":[left_shared,right_shared],
                                     "E_image":u,"E_form":form,"offdiagonal_rank":expect,
                                     "principal_rank":rank(a),"head_residual_rank":rank(m)})
    assert len(observations)==24
    # It is insufficient to check only image support. This idempotent has a
    # private covector and cannot be the shared derivative of the two stages.
    false_shared=outer(1,1|(1<<2),size)
    opposite=diag(size,{0,1,6,7,8,9})
    assert mul(E,false_shared)==false_shared and mul(false_shared,false_shared)==false_shared
    assert mul(false_shared,opposite)!=false_shared
    return {"rectangular_dimension":[12,6],"oblique_and_orthogonal_cases":observations,
            "image_only_false_sharing_rejected":True}


def int_hist(d):
    return Counter({int(k):v for k,v in d.items()})


def literal_invoice(w,result,native):
    dims={int(i):c["dim"] for i,c in native["frames"].items()}
    paid0=Counter(abs(dims[e[2]]-dims[e[3]]) for e in native["program"] if e[0]=="MOVE")
    helper0=Counter(abs(dims[a]-dims[b]) for a,b in
                    zip(native["start"][222:],native["final"][222:],strict=True))
    assert paid0==int_hist(result["native_paid"]) and helper0==int_hist(result["native_helpers"])
    N=w["ports"]
    stages=Counter(e[1] for e in w["events"] if e[0]=="LOCAL")
    assert stages==dict.fromkeys(range(1,19),2)
    native_count=sum(stages.values())
    paid_native=Counter({r:n*native_count for r,n in paid0.items()})
    T=Counter({r:n*native_count for r,n in helper0.items()})
    for d in w["diagonal"]:
        T[d["q"]+w["body_rank"]*len(d["stages"])]+=N
    idle_masks=[e[2] for e in w["events"] if e[0]=="IDLE_ONE"]
    idle=Counter(w["body_rank"]*len(m) for m in idle_masks)
    q_calls=sum(e[0]=="QUERY" for e in w["events"])
    P=paid_native+Counter({r:N*n for r,n in idle.items()})+Counter({1:q_calls*N})
    assert T==int_hist(result["targets"]) and P==int_hist(result["paid"])
    assert q_calls==4 and len(idle_masks)==32
    return T,P,paid_native,idle_masks


def majorant(degrees_left,degrees_right,common,expected):
    total=sum(degrees_left+degrees_right)
    assert sum(expected)==total
    # Directly verify each prefix until the majorant reaches total incidence.
    # Longer prefixes are automatic because the total incidence is fixed.
    for k in range(1,len(expected)+1):
        bound=max(
            sum(min(d,a+c) for d in degrees_left)+sum(min(d,k-c-a+c) for d in degrees_right)
            for c in range(min(common,k)+1) for a in range(k-c+1)
        )
        assert bound==sum(expected[:k])


def run(root):
    w=load_json(root,"bit/EFREE-CALLER.json.gz")
    r=load_json(root,"bit/EFREE-RESULT.json")
    native=load_json(root,"bit/retained/inputs/BIT-NATIVE-WORD.json.gz")
    gate_key="bit/independent/interval_gate.py"
    auth(root,gate_key)
    spec=spec_from_file_location("directed_gate",root/gate_key)
    g=module_from_spec(spec)
    spec.loader.exec_module(g)
    assert (w["roles"],w["ports"],w["stages"],w["body_rank"],len(w["events"]))==(38,111,18,7,798)
    assert all(d["q"]==1 and len(d["stages"])==len(set(d["stages"])) for d in w["diagonal"])
    support=[{i for i,d in enumerate(w["diagonal"]) if s in d["stages"]} for s in range(1,19)]
    assert len(support)==18 and len(w["diagonal"])==38
    assert all(a&b=={0,19} for a in support[:9] for b in support[9:])
    degrees=[len(a)-4 for a in support]
    T,P,native_paid,old_masks=literal_invoice(w,r,native)
    assert degrees==[sum(s in m for m in old_masks) for s in range(1,19)]
    assert sum(degrees)==144
    N=w["ports"]
    no_cross=sorted(map(len,old_masks),reverse=True)
    two_common=[16,16]+[k for k in range(7,0,-1) for _ in range(4)]
    majorant(degrees[:9],degrees[9:],0,no_cross)
    majorant(degrees[:9],degrees[9:],2,two_common)
    full_head=(w["roles"]-36)*N
    counts=(full_head+2*N,full_head+3*N,full_head+4*N)
    assert counts==(444,555,666)

    def upper(lengths,packed_head):
        remaining=T.copy()
        remaining.subtract(native_paid)
        remaining.subtract(Counter({w["body_rank"]*k:N*c for k,c in Counter(lengths).items()}))
        if packed_head:
            remaining[packed_head]-=1
        return g.show(g.moment(remaining,TARGET))

    c_no=upper(no_cross,counts[0])
    c_one=upper(two_common,counts[1])
    c_two=upper(two_common,counts[2])
    c_145=upper([18]*8+[1],counts[0])
    c_146=upper([18]*8+[2],0)
    scenarios={"144_no_cross_mask":c_no,"144_any_cross_mask":c_one,
               "144_two_cross_masks_same_stage":c_two,"145_incidences":c_145,
               "146_or_more_incidences":c_146}
    assert all(Fraction(bounds[1])<0 for bounds in scenarios.values())
    return {"status":"PROVED_NEGATIVE_DECLARED_UNIFORM_IDLE_REGROUPING",
            "input_sha256":PINS,"target":str(TARGET),"literal_P":P,"literal_T":T,
            "literal_moves_per_native":sum(native_paid.values())//36,
            "per_stage_public_support":list(map(sorted,support)),"exact_opposite_intersections":81,
            "common_role_coordinates":[0,19],"logical_idle_degrees":degrees,
            "head_rank_lower_no_cross_any_cross_two_same_stage":counts,
            "optimistic_no_cross_lengths":no_cross,"optimistic_cross_lengths":two_common,
            "directed_optimistic_target_margins":scenarios,"finite_controls":controls(),
            "scope":"Retain all 36 old native calls with two per stage, the target diagonal, uniform IDLE masks over 111 ports with a common rank-111 body derivative for each included stage, body-free head correction under inherited rank tariff, and otherwise derivative-free scalar adapters. Arbitrary linear copy/port mixing, rectangular contexts, and oblique projectors allowed."}


if __name__=="__main__":
    assert __debug__
    print(json.dumps(run(Path(sys.argv[1])),sort_keys=True,indent=2))

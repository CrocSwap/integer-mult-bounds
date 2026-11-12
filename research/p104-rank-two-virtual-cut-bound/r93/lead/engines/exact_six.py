"""Exact six-bank rational check by dual-direction replay and transposed pairing."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import cache
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

_mod = run_path(str(Path(__file__).resolve().with_name('rolling_exterior.py')))
HEAD, PROTECTED, checked, unique = (_mod[k] for k in ('HEAD','PROTECTED','checked','unique'))

SELECTION = "a4877749084f276d00917c137fda2b2593894daca1e10629a4a27de7914b4574"
MODULAR = "fa35b69613ad4af03eada14f251827464dba0d002f67da085817422ec3351649"
PRIMARY = "a3505dd0cfd3ee9e242f804e12e3c4705ea6548080d537f597cec355f358e92c"


def read_extra(path, pin):
    raw = path.read_bytes()
    assert sha256(raw).hexdigest() == pin, f"Changed input {path.name}"
    return loads(raw, object_pairs_hook=unique)


@cache
def scalar(value):
    return Q(value)


def add(dst,src,k):
    for j,v in src.items():
        x = dst.get(j,0)+k*v
        if x:
            dst[j]=x
        else:
            dst.pop(j,None)


def scale(row,k):
    return {j:k*v for j,v in row.items() if k*v}


def compose(weights, rows):
    out={}
    for j,value in weights.items():
        add(out,rows[j],value)
    return out


def dot(a,b):
    return sum((v*b.get(j,0) for j,v in a.items()),Q(0))


def stop_at(deadline):
    if monotonic() >= deadline:
        raise TimeoutError("exact rational continuation cap")


def trace(word, selected, deadline):
    n=word["public"]
    tape=word["program"]
    size=n+word["owned_fields"]
    requests=defaultdict(list)
    offsets=[]
    count=0
    for row in selected:
        t,_=row["key"]
        offsets.append((count,count+len(row["public"])))
        for r in row["public"]:
            requests[t].append((r,count))
            count+=1

    # Prefix rows via backward covectors injected at each pre-event cut.
    carry=[{} for _ in range(size)]
    for t in range(max(requests),-1,-1):
        if t%128==0:
            stop_at(deadline)
        op,d,*args=tape[t]
        if op in ("INIT","CLEAR"):
            carry[d]={}
        elif op=="SCALE" and carry[d]:
            carry[d]=scale(carry[d],scalar(args[0]))
        elif op in ("ADD","COPY"):
            add(carry[args[0]],carry[d],scalar(args[-2]))
            if op=="COPY":
                carry[d]={}
        for r,j in requests.get(t,()):
            add(carry[r],{j:Q(1)},1)
    assert not any(carry[n:])
    prefix=[{} for _ in range(count)]
    for coordinate,vec in enumerate(carry[:n]):
        for j,v in vec.items():
            prefix[j][coordinate]=v

    # Suffix columns via forward impulses injected at each pre-event cut.
    carry=[{} for _ in range(size)]
    charts=list(word["initial"])+[None]*(size-n)
    for t, event in enumerate(tape):
        if t%128==0:
            stop_at(deadline)
        for r,j in requests.get(t,()):
            # Any other cotangents in carry refer to earlier, independent cuts.
            add(carry[r],{j:Q(1)},1)
        op,d,*args=event
        if op=="MOVE":
            a,b,owned=args
            assert charts[d]==a and owned==(d>=n)
            charts[d]=b
        elif op=="INIT":
            assert d>=n and charts[d] is None
            carry[d]={}
            charts[d]=args[0]
        elif op=="CLEAR":
            assert d>=n and charts[d]==args[0]
            carry[d]={}
            charts[d]=None
        elif op=="SCALE":
            assert charts[d]==args[-1]
            if carry[d]:
                carry[d]=scale(carry[d],scalar(args[0]))
        else:
            src= args[0]
            assert op in ("ADD","COPY") and charts[d]==charts[src]==args[-1] and d!=src
            if op=="COPY":
                assert d>=n and not carry[d]
                carry[d]={}
            add(carry[d],carry[src],scalar(args[-2]))
    assert charts==list(word["final"])+[None]*(size-n) and not any(carry[n:])
    suffix=[{} for _ in range(count)]
    for coordinate,vec in enumerate(carry[:n]):
        for j,v in vec.items():
            suffix[j][coordinate]=v
    return [(prefix[a:b],suffix[a:b]) for a,b in offsets]


def kernel(equations,width):
    """Exact column-variable nullspace by descending-coordinate row reduction."""
    pivots={}
    for equation in equations:
        row=equation.copy()
        while row:
            j=max(row)
            if j in pivots:
                add(row,pivots[j],-row[j])
            else:
                pivots[j]=scale(row,1/row[j])
                break
    basis=[]
    for free in sorted(set(range(width))-pivots.keys()):
        vec={free:Q(1)}
        for j,row in sorted(pivots.items()):
            v=-dot(row,vec)
            if v:
                vec[j]=v
        assert all(dot(row,vec)==0 for row in pivots.values())
        basis.append(vec)
    return len(pivots),basis


def pure(rows,cohort):
    equations=defaultdict(dict)
    for j,row in enumerate(rows):
        for i,v in row.items():
            if i not in cohort:
                equations[i][j]=v
    rank,coefficients=kernel(equations.values(),len(rows))
    result=[]
    for weights in coefficients:
        image=compose(weights,rows)
        assert image.keys()<=cohort
        result.append((weights,image))
    return rank,result


def pair(prefix,suffix,deadline):
    """Use transposed bilinear maps and their explicit wedge coefficients."""
    B,D=[],[]
    for b,d in suffix:
        bv,dv={},{}
        for i,(a,c) in enumerate(prefix):
            if value:=dot(c,d):
                bv[i]=value
            if value:=dot(a,b)-bv.get(i,0):
                dv[i]=value
        B.append(bv)
        D.append(dv)

    def columns(y):
        return compose(y,B),compose(y,D)

    def solve(y):
        u,v=columns(y)
        if not u:
            return None
        if not v:
            i=min(u)
            return {i:1/u[i]},y
        j=min(v)
        for i in sorted(u.keys()|v.keys()):
            den=u.get(i,0)*v[j]-u.get(j,0)*v.get(i,0)
            if den:
                return {i:v[j]/den,j:-v.get(i,0)/den},y
        return None

    def wedge(u,v):
        coords=sorted(u.keys()|v.keys())
        return {(i,j):x for k,i in enumerate(coords) for j in coords[k+1:]
                if (x:=u.get(i,0)*v.get(j,0)-u.get(j,0)*v.get(i,0))}

    hit=None
    for j,(u,v) in enumerate(zip(B,D,strict=True)):
        stop_at(deadline)
        if wedge(u,v):
            hit=solve({j:Q(1)})
            assert hit
            break
    if hit is None:
        for j,u in enumerate(B):
            stop_at(deadline)
            for k in range(j+1,len(B)):
                mixed=wedge(u,D[k])
                add(mixed,wedge(B[k],D[j]),1)
                if mixed:
                    hit=solve({j:Q(1),k:Q(1)})
                    assert hit
                    break
            if hit is not None:
                break
    if hit is None:
        equations=[{j:D[j][i] for j in range(len(D)) if i in D[j]} for i in range(len(prefix))]
        _,right_null=kernel(equations,len(D))
        for y in right_null:
            stop_at(deadline)
            hit=solve(y)
            if hit is not None:
                break
    if hit is None:
        return None
    x,y=hit
    a,c=(compose(x,[p[i] for p in prefix]) for i in (0,1))
    b,d=(compose(y,[p[i] for p in suffix]) for i in (0,1))
    assert dot(a,b)==dot(c,d)==1
    return {k:{j:v for j,v in row.items() if v} for k,row in zip("abcd",(a,b,c,d))}


def smooth(v):
    v=abs(v)
    assert v
    for p in (2,3,5):
        while v%p==0:
            v//=p
    return v==1


def physical_screen(witness,pivots):
    # This is only a coefficient and reciprocal preflight.
    def pivots_for(row, allowed):
        return [j for j,v in sorted(row.items()) if j in allowed and smooth(v.numerator) and smooth(v.denominator)]
    return {
        "cut_unit_pivots":pivots_for(witness["a"],set(pivots)),
        "boundary_unit_pivots":pivots_for(witness["c"],set(witness["c"])),
        "all_denominators_in_Z_1_over_30":all(smooth(v.denominator) for row in witness.values() for v in row.values()),
        "physical_route_price_tape_unverified":True,
    }


def checks():
    inf=float("inf")
    pref=[({0:Q(1)},{10:Q(2)})]
    suf=[({0:Q(1)},{10:Q(1,2)})]
    assert pair(pref,suf,inf)
    assert pair(pref,[({0:Q(1)},{10:Q(1)})],inf) is None
    # Both single suffix basis directions fail, but their mixed wedge works.
    pref=[({0:Q(1)},{10:Q(1)}),({1:Q(1)},{11:Q(1)})]
    suf=[({0:Q(2)},{10:Q(1)}),({1:Q(3)},{11:Q(1)})]
    assert pair(pref,suf,inf)
    assert kernel([{1:Q(1),0:Q(2)},{1:Q(2),0:Q(4)}],2)[1] == [{0:Q(1),1:Q(-2)}]
    return ["signed_unit","unequal_pairing_rejected","mixed_wedge","dependent_kernel"]


def main():
    parser=ArgumentParser(description=__doc__)
    for name in ("word","price","selection","modular"):
        parser.add_argument("--"+name,type=Path)
    parser.add_argument("--controls-only",action="store_true")
    a=parser.parse_args()
    if not __debug__:
        raise RuntimeError("Run with assertions")
    if a.controls_only:
        print(dumps(checks()))
        return
    if not all((a.word,a.price,a.selection,a.modular)):
        parser.error("All four pinned input paths required")
    selected, results=[],[]
    diagnostics=[]
    timeout=None

    def stop(*_):
        raise TimeoutError("hard exact 35-second cap")

    signal(SIGALRM,stop)
    alarm(35)
    deadline=monotonic()+33
    try:
        diagnostics=checks()
        price=checked(a.price,"price")
        selection=read_extra(a.selection,SELECTION)
        mod=read_extra(a.modular,MODULAR)
        assert selection["modular_sha256"]==PRIMARY and selection["exact_cap"]==6 and selection["exact_seconds_cap"]==35
        selected=selection["selected"]
        assert len(selected)==len({tuple(x["key"]) for x in selected})==6
        modular={tuple(row["key"]):row for row in mod["tested"]}
        for row in selected:
            other=modular[tuple(row["key"])]
            assert all(row[k]==other[k] for k in ("key","public","owned","pivots"))
            assert row["exterior_rank"]==other["modular_rank"] and other["status"]=="modular_rank_drop"
            assert not row["owned"] and len(row["pivots"])>=2
        word=checked(a.word,"word")
        n=word["public"]
        main_roles=set(word["live"])|{r+112 for r in word["live"]}|set(word["hosted"]["X2"])|set(word["hosted"]["Y2"])
        cohort={r for r,(a,z) in enumerate(zip(word["initial"],word["final"],strict=True))
                if (a,z)==(3,127) and r not in main_roles|PROTECTED}
        assert len(cohort)==615 and cohort==set(price["endpoint_cohort"])
        all_rows=trace(word,selected,deadline)
        for bank,(P,S) in zip(selected,all_rows,strict=True):
            stop_at(deadline)
            pr,prefix=pure(P,cohort)
            sr,suffix=pure(S,cohort)
            assert pr>=bank["exterior_rank"]
            answer=pair(prefix,suffix,deadline)
            entry=dict(key=bank["key"],bank=bank["public"],prefix_exterior_rank=pr,suffix_exterior_rank=sr,
                       prefix_nullity=len(prefix),suffix_nullity=len(suffix),modular_rank=bank["exterior_rank"],
                       status="exact_unit_pair" if answer else "no_exact_unit_pair")
            if answer:
                for name in ("a","b"):
                    answer[name]={bank["public"][j]:v for j,v in answer[name].items()}
                entry["materialization_preflight"]=physical_screen(answer,bank["pivots"])
                entry["witness"]={name:{j:str(v) for j,v in w.items()} for name,w in answer.items()}
            results.append(entry)
    except TimeoutError as exc:
        timeout=str(exc)
    finally:
        alarm(0)
    print(dumps(dict(head=HEAD,selection_sha256=SELECTION,independent_modular_sha256=MODULAR,
        case_cap=6,runner_cap_seconds=35,controls=diagnostics,results=results,
        unresolved=[r["key"] for r in selected[len(results):]],modular_drops_outside_exact_scope=2128,
        status_counts=dict(Counter(row["status"] for row in results)),timeout=timeout),indent=2,sort_keys=True))
    if timeout:
        raise SystemExit(2)


if __name__=="__main__":
    main()

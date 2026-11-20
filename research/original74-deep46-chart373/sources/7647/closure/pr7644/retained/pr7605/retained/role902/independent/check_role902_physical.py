"""Authenticate and independently compare all physical columns of the role902 fusion."""
import argparse
from copy import deepcopy
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from sys import modules, version_info
from time import perf_counter
from types import ModuleType

PINS = {
    "COMPOSED-WORD.json.gz": "926bbb01254b96e9f8a67d4b7c616f89105686ef1acd14438ac2aad06ba58a1c",
    "COMPOSED-APPLICATION.json": "d9b5d292abb87c87eb3fd3f53501e14d77629ca4adca77a527ff2cf5b58df514",
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
}
ENGINES = {
    "engines/clifford_exact.py": "2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962",
    "engines/native_verify.py": "3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38",
}
BASE = "2acc6bfd2807239fafdb3f9e09ff8ad34703df958496590ab657ef0b9ac93aef"
EDIT = "bdecd5cc1cb9f164dc695ce07a07d5d44e9961996fcdfa4d77b4092fecbda745"
HEAD = "d6be7d620c9c8337104daeb09fe01196eced5fe3"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
HERE = Path(__file__).resolve().parent
N, ROLE, CUT, CAP = 512, 902, 40950, 30
TRIPLE = (618,789,913)


def emit(**fields):
    print(dumps(fields,sort_keys=True),flush=True)


def unique(entries):
    obj=dict(entries)
    assert len(obj)==len(entries),"duplicate JSON path keys"
    return obj


def canonical(obj):
    return dumps(obj,sort_keys=True,separators=(",",":")).encode()


def engine(path):
    p=HERE/path
    raw=p.read_bytes()
    assert sha256(raw).hexdigest()==ENGINES[path]
    obj=ModuleType(p.stem)
    obj.__file__=str(p)
    modules[obj.__name__]=obj
    exec(compile(raw,str(p),"exec"),obj.__dict__)
    return obj


def basis_span(basis):
    span={0}
    for a in basis:
        assert a not in span
        span.update(a^b for b in tuple(span))
    return span


def multiply(a,b):
    ar,ai=a
    br,bi=b
    return ar*br-ai*bi, ar*bi+ai*br


def normalize(entries,den):
    kept={k:(a,b) for k,(a,b) in entries.items() if a or b}
    if not kept:
        return {},0
    while den and all((a|b)&1==0 for a,b in kept.values()):
        den-=1
        kept={k:(a//2,b//2) for k,(a,b) in kept.items()}
    return kept,den


def monomial(record,source):
    bits=[j for j in range(9) if source>>j&1]
    diagonal=sum(record["linear_Z4"][j] for j in bits)
    cross=sum((record["quadratic_rows"][j]>>k)&1 for j in bits for k in bits if k>j)
    matrix=record["matrix_rows"]
    target=record["offset"]^sum((((source&row).bit_count()&1)<<j) for j,row in enumerate(matrix))
    unit=((1,0),(0,1),(-1,0),(0,-1))[(diagonal+2*cross+record["phase"])%4]
    return target,unit


def gaussian_column(recipe,source):
    r=recipe["rank"]
    middle,a=monomial(recipe["right"],source)
    entries={}
    for low in range(1<<r):
        target,b=monomial(recipe["left"],middle^low)
        count=low.bit_count()
        # Across each mixed bit, unchanged weight is 1+i and flipped weight is 1-i.
        factor=(1,0)
        for c in [(1,-1)]*count+[(1,1)]*(r-count):
            factor=multiply(factor,c)
        assert target not in entries
        entries[target]=multiply(factor,multiply(a,b))
    return normalize(entries,r)


def adjoint(columns):
    denominator=max(d for _,d in columns)
    accum=[{} for _ in range(N)]
    for j,(column,d) in enumerate(columns):
        for i,(a,b) in column.items():
            accum[i][j]=(a<<(denominator-d),-b<<(denominator-d))
    return [normalize(col,denominator) for col in accum]


def product_column(after,before):
    vector,d=before
    denominator=d+max(after[i][1] for i in vector)
    result={}
    for i,value in vector.items():
        col,shift=after[i]
        scale=1<<(denominator-d-shift)
        for j,entry in col.items():
            a,b=multiply(entry,value)
            r,s=result.get(j,(0,0))
            result[j]=(r+a*scale,s+b*scale)
    return normalize(result,denominator)


def main():
    assert __debug__ and version_info[:2]==(3,12)
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_root",type=Path)
    parser.add_argument("candidate",type=Path)
    args=parser.parse_args()
    started=perf_counter()
    completed=[]
    stage="authentication"

    def cap(_sig,_frame):
        emit(status="UNRESOLVED_CAP",stage=stage,completed=completed,cap_seconds=CAP,seconds=perf_counter()-started)
        raise SystemExit(124)

    signal(SIGALRM,cap)
    alarm(CAP)
    data={p:(args.input_root/p).read_bytes() for p in PINS}
    assert {p:sha256(v).hexdigest() for p,v in data.items()}==PINS
    raw=decompress(data["COMPOSED-WORD.json.gz"])
    candidate=decompress(args.candidate.read_bytes())
    assert sha256(raw).hexdigest()==BASE and sha256(candidate).hexdigest()==EDIT
    old=loads(raw,object_pairs_hook=unique)
    new=loads(candidate,object_pairs_hook=unique)
    application=loads(data["COMPOSED-APPLICATION.json"],object_pairs_hook=unique)
    assert application["status"]=="PASS_COMPOSED_7481_7542_FINAL_APPLICATION"
    assert application["candidate_canonical_sha256"]==BASE and application["caller_sha256"]==PINS["7113-CALLER.json"]
    caller=loads(data["7113-CALLER.json"],object_pairs_hook=unique)
    assert caller["stages"]==17 and old["public"]==1501 and ROLE in old["hosted"]["Y2"]
    tape=old["program"]
    assert tape[CUT:CUT+3]==[["MOVE",ROLE,618,789,False],["MOVE",ROLE,789,913,False],["ADD",985,ROLE,"-1",913]]
    assert old["program"][38436]==["ADD",1091,ROLE,"-1",618] or old["program"][38436][:3]==["ADD",1091,ROLE] and old["program"][38436][-1]==618
    assert list(i for i,e in enumerate(tape[38437:CUT],38437) if e[1]==ROLE or e[0] in ("ADD","COPY") and e[2]==ROLE)==[]
    assert new==dict(old,program=tape[:CUT]+[["MOVE",ROLE,618,913,False]]+tape[CUT+2:])
    frames={i:old["frames"][i] for i in TRIPLE}
    assert [len(frames[i]) for i in TRIPLE]==[3,5,7]
    a,b,c=(basis_span(frames[i]) for i in TRIPLE)
    assert a<b<c
    compiler=engine("engines/clifford_exact.py")
    check=engine("engines/native_verify.py")
    source_ops={i:compiler.canonical_frame(9,tuple(frames[i])) for i in TRIPLE}
    matrices={}
    reports=[]
    for p,q,w in ((618,789,2),(789,913,2),(618,913,4)):
        stage=f"exact lowered columns {p} to {q}"
        recipe,_=compiler.lower_child(source_ops[p].adjoint().then(source_ops[q]))
        assert recipe["rank"]==w
        actual=check.recipe(recipe)
        expected=check.adjoint(check.frame(frames[p],9))+check.frame(frames[q],9)
        check.equal(actual,expected,stage)
        columns=[]
        for j in range(N):
            direct=gaussian_column(recipe,j)
            assert direct==check.state(expected,j),(p,q,j)
            columns.append(direct)
        matrices[p,q]=columns
        reports.append({"charts":[p,q],"rank":w,"forward_columns":N,"recipe_sha256":sha256(canonical(recipe)).hexdigest()})
        completed.append(stage)
    first,second,direct=(matrices[k] for k in ((618,789),(789,913),(618,913)))
    stage="all signed forward products"
    assert all(product_column(second,col)==direct[j] for j,col in enumerate(first))
    completed.append(stage)
    stage="all signed reverse adjoint products"
    first_h,second_h,direct_h=map(adjoint,(first,second,direct))
    assert all(product_column(first_h,col)==direct_h[j] for j,col in enumerate(second_h))
    complete_adjoint=check.adjoint(check.frame(frames[913],9))+check.frame(frames[618],9)
    assert all(check.state(complete_adjoint,j)==direct_h[j] for j in range(N))
    completed.append(stage)
    stage="altered direct phase control"
    mutant=deepcopy(recipe)
    mutant["left"]["phase"]=(mutant["left"]["phase"]+1)%4
    assert check.tableau(check.recipe(mutant))==check.tableau(check.recipe(recipe))
    mutant_columns=[gaussian_column(mutant,j) for j in range(N)]
    assert all(a!=b for a,b in zip(mutant_columns,direct,strict=True))
    assert all(a!=b for a,b in zip(adjoint(mutant_columns),direct_h,strict=True))
    completed.append(stage)
    alarm(0)
    emit(status="PASS_ROLE902_EXACT_PHYSICAL_COMPOSITION",cases_completed=1,unresolved=[],completed=completed,
         comparator_head=HEAD,caller_head=CALLER,old_canonical_sha256=BASE,candidate_canonical_sha256=EDIT,
         changed_clocks=[CUT,CUT+1],first_affected_old_read=CUT+2,prior_read=38436,
         move_role=ROLE,role_is_public_y2=True,host_and_nonprogram_metadata_identical=True,
         recipes=reports,old_product_forward_columns=N,old_product_adjoint_columns=N,
         phase_control_forward_rejections=N,phase_control_adjoint_rejections=N,
         input_pins=PINS,engine_pins=ENGINES,cap_seconds=CAP,seconds=perf_counter()-started)


if __name__=="__main__":
    main()

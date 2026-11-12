"""Enumerate exact fixed-host compatibility classes for the late-mask seam."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT=Path(__file__).resolve().parent
CUT,HOST_CLOCK,N=1741,3058,36
HOST={0,9,18,27}
PIN="75d94780f9db49a4b08bb0e7fb4bd7fc04adb8cabbf73d83a809179c04c3d439"


def stop(*_):
    raise TimeoutError("20-second fixed-host compatibility screen")


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(20)
    path=ROOT/"forward.py"
    assert sha256(path.read_bytes()).hexdigest()==PIN
    f=run_path(str(path))
    for name,digest in f["PINS"].items():
        assert sha256((ROOT/name).read_bytes()).hexdigest()==digest
    caller=loads((ROOT/"inputs/CALLER.json").read_bytes())
    base=loads((ROOT/"inputs/R92-PRICE.json").read_bytes())
    tape=caller["events"]
    assert len(tape)==4783 and tape[CUT]==["A","ADD",10,0,"2"]
    assert tape[HOST_CLOCK][:3]==["J",9,[9,0,18,27]]
    early=set(range(1,9))
    late=set(range(9,18))
    for part,stages in ((tape[:CUT],early),(tape[CUT:],late)):
        assert {e[1] for e in part if e[0]=="J"}==stages
        assert all(set(e[3]) <= stages for e in part if e[:2]==["A","IDLE_ONE"])
    ports=caller["types"]["A"]["ports"]
    diagonals=caller["types"]["A"]["diagonal"]
    assert len(ports)==96 and len(diagonals)==N and all(r[:2]==[-1,0] for r in diagonals)
    counts=[(sum(d[2:10]),sum(d[10:])) for d in diagonals]
    outside=[r for r in range(N) if r not in HOST]
    unit,apply=f["unit"],f["apply"]
    signatures=[[] for _ in range(N)]
    for q in (1,-1):
        pre=tape[:HOST_CLOCK]
        columns=[apply(pre,unit(i),q) for i in range(N)]
        inv=[apply(pre,unit(i),q,inverse=True) for i in range(N)]
        assert all(apply(pre,v,q)==unit(i) for i,v in enumerate(inv))
        for i in range(N):
            signatures[i].extend(columns[i][j] for j in outside)
            signatures[i].extend(inv[j][i] for j in outside)
    classes={}
    for i,signature in enumerate(signatures):
        classes.setdefault(tuple(signature),[]).append(i)
    groups=list(classes.values())
    assert sum(map(len,groups))==N
    assert signatures[0]!=signatures[9]
    old=[1+8*(e+l) for e,l in counts]
    best=list(range(N))
    for group in groups:
        low_early=sorted(group,key=lambda j:(counts[j][0],j))
        high_late=sorted(group,key=lambda j:(-counts[j][1],j))
        for i,j in zip(low_early,high_late,strict=True):
            best[i]=j
    assert sorted(best)==list(range(N)) and all(signatures[i]==signatures[j] for i,j in enumerate(best))
    new=[1+8*(counts[i][0]+counts[j][1]) for i,j in enumerate(best)]
    delta=Counter(new)
    delta.subtract(old)
    delta=Counter({r:96*d for r,d in delta.items() if d})
    assert sum(r*n for r,n in delta.items())==0
    cost=run_path(str(ROOT/"inputs/pricing.py"))["cost"]
    upper=cost(delta,Q(base["old_crossing_upper"])) if delta else (Q(0),Q(0))
    alarm(0)
    print(dumps({"pins":f["PINS"]|{"forward.py":PIN},"head":base["head"],"caller":base["caller_head"],
                 "cut":CUT,"host":HOST_CLOCK,"host_roles":sorted(HOST),"signs":[1,-1],
                 "role_cap":N,"runner_cap_seconds":20,"classes":groups,
                 "class_counts":[[counts[j] for j in group] for group in groups],
                 "assignment_examined":best,"productive_delta":delta,"gross_upper":upper,
                 "tested_permutations":0,
                 "unresolved_within_scope":0 if not delta else None},
                default=str,indent=2,sort_keys=True))


if __name__=="__main__":
    main()

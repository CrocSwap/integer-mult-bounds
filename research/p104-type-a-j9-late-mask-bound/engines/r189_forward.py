"""Exact fixed-host support for absorbing the Type A late-mask seam at J9."""
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT=Path(__file__).resolve().parent
CUT,J9=1741,3058
ROOTS=(0,9)
HOST=(9,0,18,27)
PINS={
    "forward.py":"75d94780f9db49a4b08bb0e7fb4bd7fc04adb8cabbf73d83a809179c04c3d439",
    "inputs/R178-PRICE.json":"fbb1e5f1de9274bba2d0445b3868c50a04b178751c0f9244ebf5229128bc4651",
}


def stop(*_):
    raise TimeoutError("20-second fixed J9 support gate")


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(20)
    for name,digest in PINS.items():
        assert sha256((ROOT/name).read_bytes()).hexdigest()==digest
    f=run_path(str(ROOT/"forward.py"))
    for name,digest in f["PINS"].items():
        assert sha256((ROOT/name).read_bytes()).hexdigest()==digest
    unit,apply=f["unit"],f["apply"]
    c=loads((ROOT/"inputs/CALLER.json").read_bytes())
    price=loads((ROOT/"inputs/R178-PRICE.json").read_bytes())
    assert price["cut"]==CUT and price["pair"]==list(ROOTS)
    assert price["added_paid"]==0 and Q(price["gross"][0])>0
    tape=c["events"]
    assert len(tape)==4783 and tape[J9][:3]==["J",9,list(HOST)]
    assert [x[1] for x in tape[:CUT] if x[0]=="J"]==list(range(1,9))
    masks=[x[3] for x in tape[CUT:J9] if x[:2]==["A","IDLE_ONE"]]
    assert len(masks)==16 and all(9 in m and all(i>=9 for i in m) for m in masks)
    assert not any(x[0]=="J" or x[:2]==["A","QUERY"] for x in tape[CUT:J9])
    e=unit(ROOTS[0])
    e[ROOTS[1]]=-1
    output=[]
    for q in (1,-1):
        n_e=apply(tape[:J9],e,q)
        transported=apply(tape[CUT:J9],apply(tape[:CUT],e,q),q)
        assert transported==n_e
        out=apply(tape[J9:J9+1],n_e,q)
        dual=[]
        for i in range(36):
            u=unit(i)
            inv=apply(tape[:J9],u,q,inverse=True)
            assert apply(tape[:J9],inv,q)==u
            assert apply(tape,u,q)==[q*a for a in u]
            dual.append(inv[ROOTS[0]]-inv[ROOTS[1]])
        assert sum(a*b for a,b in zip(n_e,dual,strict=True))==2
        defect=[(i,j,-a*b) for i,a in enumerate(out) for j,b in enumerate(dual) if a and b]
        outside=[x for x in defect if x[0] not in HOST or x[1] not in HOST]
        output.append({"phase":q,"defect_nonzeros":len(defect),
                       "outside_nonzeros":len(outside),"first_outside":outside[:12]})
    alarm(0)
    print(dumps({"pins":PINS|f["PINS"],"head":price["head"],"caller":price["caller"],
                 "cut":CUT,"host_clock":J9,"host_roles":HOST,"root_pair":ROOTS,
                 "basis_columns":36,"runner_cap_seconds":20,"unit_middle_masks":masks,
                 "price_gross":price["gross"],"signs":output,
                 "excluded":any(s["outside_nonzeros"] for s in output)},
                default=str,indent=2,sort_keys=True))


if __name__=="__main__":
    main()

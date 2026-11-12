"""Exact two-host Type A completion at q=-1 and unit bodies."""
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
PINS = {
    "host_forward.py": "3f22de2c9f9e53e194b9244df4d3562f0c3f1199b63b91f76e8d3732bb818e99",
    "PRICE.json": "eb5ba68fe579cfea3ae1c79782850f173bc6e06fb853ce152bf58d7d6ed507b1",
}
A, B = (8,0,18,26), (9,0,18,27)
N = 36
CA, CB = ([i for i in range(N) if i not in h] for h in (A,B))


def sub(matrix, rows, cols):
    return [[matrix[i][j] for j in cols] for i in rows]


def transpose(matrix):
    return [list(col) for col in zip(*matrix, strict=True)]


def solve(left, right):
    rows = [a+b for a,b in zip(left, right, strict=True)]
    m, n = len(left[0]), len(right[0])
    pivots = []
    for j in range(m):
        r = len(pivots)
        p = next((i for i in range(r,len(rows)) if rows[i][j]), None)
        if p is None:
            continue
        rows[r], rows[p] = rows[p], rows[r]
        v = rows[r][j]
        rows[r] = [x/v for x in rows[r]]
        for i,row in enumerate(rows):
            if i != r and row[j]:
                rows[i] = [x-row[j]*y for x,y in zip(row,rows[r],strict=True)]
        pivots.append(j)
    rank = len(pivots)
    for row in rows[rank:]:
        for j,x in enumerate(row[m:]):
            if x:
                return rank,None,[j,x]
    solution = [[Q(0)]*n for _ in range(m)]
    for i,j in enumerate(pivots):
        solution[j] = rows[i][m:]
    return rank,solution,None


def complete(m, t, ident, mul):
    for i in CB:
        for j in CA:
            if m[i][j] != t[i][j]:
                return {"decision":"EXCLUDED untouched corner","first":[i,j,t[i][j]-m[i][j]]}
    rx,x,ex = solve(sub(m,CB,A),sub(t,CB,A))
    ry,y,ey = solve(transpose(sub(m,B,CA)),transpose(sub(t,B,CA)))
    stats = {"exterior_ranks":[rx,ry],"exterior_errors":[ex,ey]}
    if ex is not None or ey is not None:
        return stats | {"decision":"EXCLUDED exterior equations"}
    xm,ym = ident(),ident()
    for i in range(4):
        for j in range(4):
            xm[A[i]][A[j]],ym[B[i]][B[j]] = x[i][j],y[j][i]
    product = mul(ym,mul(m,xm))
    if product == t:
        return stats | {"decision":"EXACT one specialization","J8":x,"J9":transpose(y)}
    defects = [(i,j,t[i][j]-product[i][j]) for i in B for j in A if t[i][j]!=product[i][j]]
    assert defects
    return stats | {"decision":"EXCLUDED forced interior" if rx==ry==4 else "UNRESOLVED free variables",
                    "first_interior":defects[0],"particular_J8":x,"particular_J9":transpose(y)}


def stop(*_):
    raise TimeoutError("30-second exact specialization cap")


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(30)
    for name,h in PINS.items():
        assert sha256((ROOT/name).read_bytes()).hexdigest()==h
    f=run_path(str(ROOT/"host_forward.py"))
    read,tape,retime,ident,mul=(f[key] for key in ("read","tape","retiming","identity","multiply"))
    ev=loads(read("CALLER.json"))["events"]
    all_events,prefix,after=retime(ev,loads(read("PR7404-RESULT.json")))
    assert ev[1423][:3]==["J",8,list(A)] and ev[3058][:3]==["J",9,list(B)]
    between=[(k,e) for k,e in after if k<3058]
    suffix=[(k,e) for k,e in after if k>3058]
    assert {1580,1659} <= {k for k,e in between if e[:2]==["A","QUERY"]}
    pi=tape(prefix,-1,1,inverse=True)
    si=tape(suffix,-1,1,inverse=True)
    old=tape(all_events,-1,1)
    assert old==ident(-1)
    m_old=tape(between,-1,1)
    x_old=tape([(1423,ev[1423])],-1,1)
    y_old=tape([(3058,ev[3058])],-1,1)
    old_target=mul(si,mul(old,pi))
    assert mul(y_old,mul(m_old,x_old))==old_target
    control=complete(m_old,old_target,ident,mul)
    assert not control["decision"].startswith("EXCLUDED")
    old[0][0]=old[18][18]=Q(1)
    required=mul(si,mul(old,pi))
    m=tape(between,-1,1,demote=True)
    result=complete(m,required,ident,mul)
    required[1][1]+=1
    assert complete(m,required,ident,mul)["decision"]=="EXCLUDED untouched corner"
    alarm(0)
    print(dumps({"head":f["HEAD"],"caller":f["CALLER_HEAD"],"peer":f["PEER_HEAD"],
                 "pins":PINS|f["PINS"],"phase":-1,"unit_bodies":True,
                 "runner_cap_seconds":30,"result":result,"predecessor":control},
                indent=2,sort_keys=True,default=str))


if __name__=="__main__":
    main()

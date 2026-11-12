"""Check exact unit-body support of the forced J9 replacement."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/R178-REVERSE.json": "ad9bbc64a9b866a89f48f1fac0b0346c18105c4b69e62aa41a9cd5575e5c5942",
    "inputs/R178-PRICE.json": "fbb1e5f1de9274bba2d0445b3868c50a04b178751c0f9244ebf5229128bc4651",
    "inputs/r179.py": "720a921b8eb215675bf738c94dac3361592c342fd8f8eeda6d6efb6888061a5a",
}
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
N, CUT, HOST, SECONDS = 36, 1741, 3058, 20
ROLES, ROOTS = (9,0,18,27), (0,9)


def unique(items):
    data = dict(items)
    assert len(items) == len(data), "duplicate key"
    return data


def read(path):
    raw = (ROOT / path).read_bytes()
    assert sha256(raw).hexdigest() == PINS[path], path
    return raw


def stop(*_):
    raise TimeoutError("20-second exact support cap")


def middle(events, ident):
    m, counts, idles = ident(), Counter(), []
    for i, (kind, *args) in enumerate(events, CUT):
        if kind == "B":
            continue
        assert kind == "A"
        op, d, *params = args
        counts[op] += 1
        if op == "ADD":
            src, scalar = params
            m[d] = [x+Q(scalar)*y for x,y in zip(m[d],m[src],strict=True)]
        elif op == "SCALE":
            m[d] = [Q(params[0])*x for x in m[d]]
        elif op == "SWAP":
            src, = params
            m[d],m[src] = m[src],m[d]
        elif op == "LAMBDA":
            assert params[0] in (1,-1)
        else:
            assert op == "IDLE_ONE" and params[0] and min(params[0]) >= 9
            idles.append([i,d,params[0]])
    return m, counts, idles


def exterior(a,b):
    return [[i,j,a[i][j]-b[i][j]] for i in range(N) for j in range(N)
            if (i not in ROLES or j not in ROLES) and a[i][j] != b[i][j]]


def inputs():
    c,g,p = [loads(read(name),object_pairs_hook=unique) for name in
        ("inputs/CALLER.json","inputs/R178-REVERSE.json","inputs/R178-PRICE.json")]
    assert (g["benchmark"],g["caller"],g["cut"],g["roots"]) == (HEAD,CALLER,CUT,list(ROOTS))
    assert (p["head"],p["caller"],p["cut"],p["pair"]) == (HEAD,CALLER,CUT,list(ROOTS))
    assert p["added_paid"] == 0 and p["signed_delta"] == {"9":-96,"73":192,"137":-96}
    assert Q(p["complete_probe"][0]) > 0
    assert g["central_signs"] == [1,-1] and g["basis_columns"] == N
    tape = c["events"]
    assert len(tape) == 4783 and tape[HOST][:3] == ["J",9,list(ROLES)]
    assert tape[CUT] == ["A","ADD",10,0,"2"] and c["types"]["A"]["roles"] == N
    assert len(c["types"]["A"]["ports"]) == 96
    read("inputs/r179.py")
    return c,g,p,run_path(str(ROOT/"inputs/r179.py"))


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(SECONDS)
    c,g,p,engine = inputs()
    ident, mul, solve, expand = (engine[k] for k in ("identity","product","solve","expand"))
    m,counts,idles = middle(c["events"][CUT:HOST],ident)
    assert [x[0] for x in idles] == list(range(1742,1788,3)) and counts["LAMBDA"] == 2
    im = solve(m,ident())
    assert mul(m,im) == mul(im,m) == ident()
    cases = []
    for q,label in ((1,"plus"),(-1,"minus")):
        gp = expand(g["prefix_"+label])
        ig = solve(gp,ident())
        assert mul(gp,ig) == mul(ig,gp) == ident()
        a,b = ROOTS
        gx = [row.copy() for row in gp]
        for row in gx:
            row[a],row[b] = row[b],row[a]
        w = mul(gx,ig)
        assert w == expand(g["seam_"+label]) and mul(w,gp) == gx
        old = ident()
        u,v,x,y = ROLES
        old[v][u],old[x][y] = Q(q),Q(-q)
        bm = mul(old,m)
        need = mul(mul(bm,w),im)
        assert mul(need,m) == mul(bm,w) and mul(bm,im) == old
        wrong = [row.copy() for row in old]
        wrong[1][1] += 1
        assert exterior(wrong,old) == [[1,1,Q(1)]]
        outside = exterior(need,old)
        cases.append({"q":q,"outside_nonzeros":len(outside),"outside":outside,
                      "first_outside":outside[0] if outside else None})
    alarm(0)
    print(dumps({"head":HEAD,"caller":CALLER,"pins":PINS,"cut":CUT,"host":HOST,
                 "host_roles":ROLES,"roots":ROOTS,"basis_columns":N,"runner_cap_seconds":SECONDS,
                 "middle_a_counts":counts,"middle_idles":idles,"price":p,"cases":cases,
                 "status":"excluded by exact support" if any(r["outside"] for r in cases) else "survives unit signs",
                 "controls":["identity seam gives old host","outside mutation rejected",
                             "exact signed seam reconstructs R178"]},sort_keys=True,indent=2,default=str))


if __name__=="__main__":
    main()

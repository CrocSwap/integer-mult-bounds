"""Exact compatibility classes for all Type A masks at the retained J9."""
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
    "inputs/R189.json": "2b7a2d4c4a278f97118c20a42eb48f92f1e6a092d10204398f9a1751106b9904",
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "inputs/r178.py": "2faedaf76b8d1cc399294f5595862092de75ea1dd3a0ec41898a61edad006d53",
    "inputs/r179.py": "720a921b8eb215675bf738c94dac3361592c342fd8f8eeda6d6efb6888061a5a",
}
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
N, CUT, HOST, PORTS, SECONDS = 36,1741,3058,96,20
ROLES = (9,0,18,27)
EXT = tuple(i for i in range(N) if i not in ROLES)


def unique(items):
    result = dict(items)
    assert len(items) == len(result), "duplicate key"
    return result


def read(path):
    raw = (ROOT / path).read_bytes()
    assert sha256(raw).hexdigest() == PINS[path], path
    return raw


def engine(path):
    read(path)
    return run_path(str(ROOT / path))


def stop(*_):
    raise TimeoutError("20-second fingerprint cap")


def sparse(matrix):
    return [[i,j,v] for i,row in enumerate(matrix) for j,v in enumerate(row) if v]


def fingerprints(n,i):
    return [tuple(n[j][r] for j in EXT)+tuple(i[r][j] for j in EXT) for r in range(N)]


def classes(keys):
    partition = {}
    for role,key in enumerate(keys):
        partition.setdefault(key,[]).append(role)
    return list(partition.values())


def histogram(early,late,perm):
    return Counter(1+8*(early[i]+late[perm[i]]) for i in range(N))


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(SECONDS)
    c, old, base = [loads(read(path),object_pairs_hook=unique) for path in
        ("inputs/CALLER.json","inputs/R189.json","inputs/R92-PRICE.json")]
    assert (old["head"],old["caller"],old["cut"],old["host"]) == (HEAD,CALLER,CUT,HOST)
    assert (base["head"],base["caller_head"]) == (HEAD,CALLER)
    tape = c["events"]
    assert len(tape) == 4783 and tape[HOST][:3] == ["J",9,list(ROLES)]
    for start,end,stages in ((0,CUT,set(range(1,9))), (CUT,len(tape),set(range(9,18)))):
        assert {e[1] for e in tape[start:end] if e[0]=="J"} == stages
        assert all(set(e[3]) <= stages for e in tape[start:end] if e[:2]==["A","IDLE_ONE"])
    ops = engine("inputs/r178.py")
    algebra = engine("inputs/r179.py")
    price = engine("inputs/pricing.py")["cost"]
    ident,mul = algebra["identity"],algebra["product"]
    vec,cv = ops["basis"],ops["covector"]
    signs, certs, matrices = [], [], []
    for q, prior in zip((1,-1),old["cases"],strict=True):
        n = [cv(tape[:HOST],vec(r),q) for r in range(N)]
        ni = [cv(tape[:HOST],vec(r),q,invert=True) for r in range(N)]
        assert mul(n,ni) == mul(ni,n) == ident()
        labels = fingerprints(n,ni)
        signs.append(labels)
        matrices.append((n,ni))
        b = ident()
        u,v,x,y = ROLES
        b[v][u],b[x][y] = Q(q),Q(-q)
        perm = list(range(N))
        perm[0],perm[9] = 9,0
        moved = [[row[j] for j in perm] for row in n]
        required = mul(b,mul(moved,ni))
        outside = [[i,j,str(required[i][j]-b[i][j])] for i in range(N) for j in range(N)
                   if (i in EXT or j in EXT) and required[i][j]!=b[i][j]]
        assert outside == prior["outside"] and labels[0] != labels[9]
        certs.append({"q":q,"per_sign_classes":classes(labels),"n":sparse(n),"n_inverse":sparse(ni),
                      "r189_outside_count":len(outside),"r189_first_outside":outside[0]})
    groups = classes(list(zip(*signs,strict=True)))
    diagonal = c["types"]["A"]["diagonal"]
    assert len(diagonal) == N and len(c["types"]["A"]["ports"]) == PORTS
    early = [sum(row[2:10]) for row in diagonal]
    late = [sum(row[10:]) for row in diagonal]
    optimum = [-1]*N
    for group in groups:
        e = sorted(group,key=lambda i:(early[i],i))
        l = sorted(group,key=lambda i:(-late[i],i))
        for i,j in zip(e,l,strict=True):
            optimum[i] = j
    assert sorted(optimum) == list(range(N))
    for n,ni in matrices:
        nr = [[row[j] for j in optimum] for row in n]
        moved = mul(nr,ni)
        assert all(moved[i][j] == (i==j) for i in range(N) for j in range(N) if i in EXT or j in EXT)
    old_hist = histogram(early,late,range(N))
    best_hist = histogram(early,late,optimum)
    delta = {r:PORTS*(best_hist[r]-old_hist[r]) for r in sorted(old_hist.keys()|best_hist.keys())
             if best_hist[r]!=old_hist[r]}
    assert sum(delta.values()) == sum(r*n for r,n in delta.items()) == 0
    interval = price(delta,Q(base["old_crossing_upper"]))
    fixed_counts = all(len({early[i] for i in g})==1 or len({late[i] for i in g})==1 for g in groups)
    if fixed_counts:
        assert not delta and interval == (0,0)
    alarm(0)
    print(dumps({"head":HEAD,"caller":CALLER,"pins":PINS,"cut":CUT,"host":HOST,"roles":ROLES,
                 "role_cap":N,"runner_cap_seconds":SECONDS,"ports":PORTS,"phases":certs,
                 "classes":[{"roles":g,"early_late":[[early[i],late[i]] for i in g]} for g in groups],
                 "all_classes_freeze_one_count":fixed_counts,"optimum":optimum,
                 "old_histogram":old_hist,"maximum_histogram":best_hist,"delta":delta,
                 "signed_gain_interval":interval,"enumerated_permutations":0,
                 "status":"uniform zero optimistic gain" if not delta else "nonzero class price, stronger gate required"},
                sort_keys=True,indent=2,default=str))


if __name__=="__main__":
    main()

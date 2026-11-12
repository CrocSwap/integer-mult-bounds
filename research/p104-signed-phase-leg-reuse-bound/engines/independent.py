"""Independent exact global signed reuse test for four J1/J17 leg pairs."""
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations, product
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/R193-PRICE.json": "1ad9852ecff0b3780770cbf4e500731e65214a9c438f8b1ed2c0cbe484d9b36b",
    "inputs/forward.py": "75d94780f9db49a4b08bb0e7fb4bd7fc04adb8cabbf73d83a809179c04c3d439",
    "inputs/reverse.py": "2faedaf76b8d1cc399294f5595862092de75ea1dd3a0ec41898a61edad006d53",
}
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
N, SECONDS = 36,30


def unique(items):
    data = dict(items)
    assert len(items) == len(data), "duplicate key"
    return data


def read(path):
    raw = (ROOT/path).read_bytes()
    assert sha256(raw).hexdigest() == PINS[path], path
    return raw


def stop(*_):
    raise TimeoutError("30-second signed reuse cap")


def dot(a,b):
    return sum(x*y for x,y in zip(a,b,strict=True) if x and y)


def plus(a,b,scale):
    return [x+scale*y for x,y in zip(a,b,strict=True)] if scale else a.copy()


def take(factors,x):
    for u,v in factors:
        x = plus(x,u,dot(v,x))
    return x


def witness(columns,rows):
    for i,j in combinations(range(N),2):
        a,b = columns
        if a[i]*b[j] == a[j]*b[i]:
            continue
        for k,l in combinations(range(N),2):
            x,y = rows
            if x[k]*y[l] == x[l]*y[k]:
                continue
            m = [[a[h]*x[g]+b[h]*y[g] for g in (k,l)] for h in (i,j)]
            det = m[0][0]*m[1][1]-m[0][1]*m[1][0]
            assert det and det == (a[i]*b[j]-a[j]*b[i])*(x[k]*y[l]-x[l]*y[k])
            return {"rows":[i,j],"columns":[k,l],"matrix":m,"determinant":det}
        return None
    return None


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(SECONDS)
    caller,price = [loads(read(name),object_pairs_hook=unique) for name in
                    ("inputs/CALLER.json","inputs/R193-PRICE.json")]
    assert (price["head"],price["caller"]) == (HEAD,CALLER)
    assert price["clocks"] == [43,137,268] and len(caller["types"]["A"]["ports"]) == 96
    assert price["new_rank8_children"] == 1200 and price["new_type_b_rank1_children"] == 48
    quote = [Q(v)/3-96 for v in price["price_by_type_a_rank1_per_port"]["0"]["raw_gross"]]
    assert 50 < quote[0] <= quote[1] < 51
    read("inputs/forward.py")
    read("inputs/reverse.py")
    f = run_path(str(ROOT/"inputs/forward.py"))
    r = run_path(str(ROOT/"inputs/reverse.py"))
    unit,apply,cv = f["unit"],f["apply"],r["covector"]
    tape = caller["events"]
    assert len(tape)==4783 and caller["types"]["A"]["roles"]==N
    factors, labels, queries = [], [], []
    for clock,event in enumerate(tape):
        if event[0]=="J":
            _, stage,(u,v,x,y),_ = event
            legs = [(v,u,1),(x,y,-1)]
        elif event[:2]==["A","QUERY"]:
            _,_,v,u,exp = event
            assert exp==-1
            queries.append(clock)
            stage,legs = 0,[(v,u,1)]
        else:
            continue
        for leg,(d,s,sign) in enumerate(legs):
            before = tape[:clock]
            out = [2*sign*x for x in apply(before,unit(d),-1,inverse=True)]
            row = cv(before,unit(s),-1)
            assert dot(row,out)==0
            factors.append((out,row))
            labels.append([clock,stage,leg,d,s,sign])
    assert len(factors)==38 and queries==[1516,1580,1659,1721]
    for i in range(N):
        e = unit(i)
        assert take(factors,e)==[-v for v in e]
        assert apply(tape,e,1)==e and apply(tape,e,-1)==[-v for v in e]
    early = [i for i,label in enumerate(labels) if label[1]==1]
    late = [i for i,label in enumerate(labels) if label[1]==17]
    assert len(early)==len(late)==2
    assert [labels[i][:2] for i in early+late] == [[43,1],[43,1],[4691,17],[4691,17]]
    results = []
    for a,b in product(early,late):
        between = factors[a+1:b]
        ua,va = factors[a]
        ub,vb = factors[b]
        u = take(between,ua)
        v = va.copy()
        for ui,vi in between:
            v = plus(v,vi,-dot(v,ui))
        assert dot(u,v)==0
        u = plus(u,ub,dot(vb,u))
        proof = witness((u,ub),(v,vb))
        results.append({"factor_pair":[a,b],"early":labels[a],"late":labels[b],
                        "intervening_count":len(between),"rank_two_minor":proof,
                        "column_factors":[u,ub],"row_factors":[v,vb]})
        for i in range(N):
            e = unit(i)
            for j,(uj,vj) in enumerate(factors):
                if j==a:
                    continue
                if j==b:
                    e = plus(plus(e,u,dot(v,e)),ub,dot(vb,e))
                else:
                    e = plus(e,uj,dot(vj,e))
            assert e==[-x for x in unit(i)]
    alarm(0)
    print(dumps({"head":HEAD,"caller":CALLER,"pins":PINS,"phases":[1,-1],"basis_columns":N,
                 "runner_cap_seconds":SECONDS,"factor_count":len(factors),"factor_labels":labels,
                 "old_relative_endpoint":"-I","price":quote,"pairs":results,
                 "survivors":[r["factor_pair"] for r in results if not r["rank_two_minor"]]},
                indent=2,sort_keys=True,default=str))


if __name__=="__main__":
    main()

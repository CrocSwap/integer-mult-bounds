"""Reverse normalized covectors for two endpoint banks of the frozen owned aggregate."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from math import lcm
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT=Path(__file__).resolve().parents[1]
PINS={
    "plan/PRICE.json":"08a403b6c8d5a3332212042ec69624ab5cf343fb7b6aa6e94f42583653f77912",
    "inputs/7334-WORD.json.gz":"4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "independent/reused/reverse_span.py":"f8b48f2ed99d003e20f5b3fb2270603c4edbc3ce9a01484102816aa2710ce9ff",
}
OWNER,FIRST,LAST,BIRTH,CLEAR=1531,41996,44242,32607,44247
ADDS=(41997,44241)
BANKS=((41996,594),(44242,534))
EVENTS,SECONDS=76466,20


def checked(root,name):
    raw=(root/name).read_bytes()
    if sha256(raw).hexdigest()!=PINS[name]:
        raise ValueError("changed dependency "+name)
    return raw


def freeze(price):
    assert price["head"]=="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
    assert price["caller"]=="07a76c5e2738882c0cb322278e56f6cae3c9885d"
    assert price["word_sha256"]==PINS["inputs/7334-WORD.json.gz"]
    assert price["caps"]=={"banks":2,"events":EVENTS,"prototype_seconds":120,"seconds":SECONDS,"windows":1}
    assert price["bank_cuts"]==[list(key) for key in BANKS]
    assert price["row"]["key"]==[FIRST,LAST,OWNER] and price["row"]["lifetime"]==[BIRTH,CLEAR]
    assert price["row"]["charts"]==[594,117,534]
    assert price["row"]["paid_ranks"]==[4,1]
    assert price["row"]["intervening"]==[[t,"ADD","destination"] for t in ADDS]


def backward(word,engine,deadline,progress):
    tape,n,m,frames=(word[k] for k in ("program","public","owned_fields","frames"))
    assert (len(tape),n,m)==(EVENTS,1501,68)
    assert tape[BIRTH][:2]==["INIT",OWNER] and tape[CLEAR][:2]==["CLEAR",OWNER]
    assert tape[FIRST]==["MOVE",OWNER,594,117,True] and tape[LAST]==["MOVE",OWNER,117,534,True]
    assert all(tape[t][:2]==["ADD",OWNER] and tape[t][-1]==117 for t in ADDS)
    assert tuple(len(frames[c]) for c in (594,117,534))==(1,5,6)

    @cache
    def space(chart):
        result={0}
        for axis in frames[chart]:
            assert axis not in result
            result|={axis^u for u in result}
        return result

    chart=word["final"]+[None]*m
    fresh_copy=set()
    empty=({},1)
    adj=[empty]*(n+m)
    captures={}
    sources={}
    banks={}
    owned_incidence=[]
    births=[]
    scale,coefficient=engine["sum_scaled"],engine["coefficient"]

    def observe(clock,role):
        key=(clock,role)
        assert chart[role] is not None and key not in captures
        i=len(captures)
        captures[key]=i
        adj[role]=scale(adj[role],({i:1},1),(1,1))
        return i

    for t in range(EVENTS-1,-1,-1):
        progress["last_unvisited"]=t
        if t%128==0 and monotonic()>=deadline:
            raise TimeoutError("reverse event cap")
        op,d,*args=tape[t]
        assert 0<=d<len(chart) and (d not in fresh_copy or op=="INIT")
        touched=(d,args[0]) if op in ("ADD","COPY") else (d,)
        if FIRST<t<LAST and OWNER in touched:
            owned_incidence.append(t)
        if BIRTH<=t<=CLEAR and d==OWNER and op in ("INIT","CLEAR"):
            births.append(t)
        if op=="MOVE":
            a,b,is_owned=args
            assert chart[d]==b and is_owned==(d>=n)
            assert space(a)<space(b) or is_owned and space(b)<space(a)
            chart[d]=a
        elif op=="INIT":
            assert d>=n and chart[d]==args[0]
            chart[d]=None
            fresh_copy.discard(d)
            adj[d]=empty
        elif op=="CLEAR":
            assert d>=n and chart[d] is None
            chart[d]=args[0]
            adj[d]=empty
        else:
            assert op in ("ADD","COPY","SCALE") and chart[d]==args[-1]
            q=coefficient(args[-2])
            if op=="SCALE":
                adj[d]=scale(empty,adj[d],q)
            else:
                s=args[0]
                assert s!=d and chart[s]==chart[d]
                adj[s]=scale(adj[s],adj[d],q)
                if op=="COPY":
                    assert d>=n
                    fresh_copy.add(d)
                    adj[d]=empty
        if t in ADDS:
            sources[t]=observe(t,tape[t][2])
        if t==FIRST:
            observe(t,OWNER)
        for cut,coframe in BANKS:
            if t==cut:
                banks[(cut,coframe)]={r:observe(t,r) for r,c in enumerate(chart) if c==coframe and r!=OWNER}
        progress["events"]+=1

    assert chart==word["initial"]+[None]*m and not fresh_copy
    assert not any(v for v,_ in adj[n:])
    assert tuple(reversed(owned_incidence))==ADDS and births==[CLEAR,BIRTH]
    progress["last_unvisited"]=None
    by_row=[[] for _ in captures]
    for coord,(entries,den) in enumerate(adj[:n]):
        for i,a in entries.items():
            by_row[i].append((coord,a,den))
    rows=[]
    for entries in by_row:
        den=lcm(*(d for _,_,d in entries))
        rows.append(engine["normalized"]({j:a*(den//d) for j,a,d in entries},den))
    return sources,banks,rows,captures[FIRST,OWNER]


def certify(word,sources,banks,rows,owner_index,engine,deadline,out):
    tape=word["program"]
    n=word["public"]
    aggregate=({},1)
    for t in ADDS:
        q=engine["coefficient"](tape[t][3])
        aggregate=engine["sum_scaled"](aggregate,rows[sources[t]],q)
    for key in BANKS:
        if monotonic()>=deadline:
            raise TimeoutError("two-bank span cap")
        donors=banks[key]
        public=[r for r in donors if r<n]
        owned=[r for r in donors if r>=n]
        bank=[(r,rows[i]) for r,i in donors.items()]+[(OWNER,rows[owner_index])]
        proof=engine["exact_span"](bank,aggregate)
        if proof["status"]=="absent_exterior_coordinate":
            proof["separating_covector"]={proof["coordinate"]:"1"}
        elif proof["status"]=="exact_span":
            coeffs={r:Fraction(v) for r,v in proof["coefficients"].items()}
            scale=1+coeffs.pop(OWNER,Fraction(0))
            legal=lambda v: bool(v and v.denominator.bit_count()==1 and v.denominator<=2**25 and
                abs(v.numerator).bit_length()<=24 and abs(v)+1<2**16)
            proof["destination_scale"]=str(scale)
            proof["legal_sparse_representation"]=len(coeffs)<=2 and legal(scale) and all(map(legal,coeffs.values()))
        out.append(dict(key=key,read_only_public=public,read_only_owned=owned,old_owner_diagonal_clock=FIRST,
            proof=proof))
    return aggregate


def main():
    parser=ArgumentParser()
    parser.add_argument("--root",type=Path,default=ROOT)
    parser.add_argument("--controls-only",action="store_true")
    args=parser.parse_args()
    assert __debug__
    name="independent/reused/reverse_span.py"
    checked(args.root,name)
    engine=run_path(str(args.root/name))
    price=loads(checked(args.root,"plan/PRICE.json"),object_pairs_hook=engine["unique"])
    freeze(price)
    tests=engine["controls"]()
    assert engine["sum_scaled"](({2:1},2),({2:1},1),(-1,2))==({},1)
    assert engine["sum_scaled"](({2:1},2),({2:1},1),(1,2))==({2:1},1)
    tests+=["signed zero aggregate","sign mutation produces nonzero aggregate"]
    if args.controls_only:
        print(dumps({"controls":tests,"banks":BANKS},sort_keys=True))
        return 0

    def stop(*_):
        raise TimeoutError("hard 20-second cap")

    signal(SIGALRM,stop)
    alarm(SECONDS)
    deadline=monotonic()+18
    out,old_adds,aggregate,timeout=[],[],None,None
    progress={"events":0,"last_unvisited":EVENTS-1}
    try:
        payload=decompress(checked(args.root,"inputs/7334-WORD.json.gz"))
        assert sha256(payload).hexdigest()=="9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
        word=loads(payload,object_pairs_hook=engine["unique"])
        old_adds=[[t,word["program"][t]] for t in ADDS]
        sources,banks,rows,owner_index=backward(word,engine,deadline,progress)
        aggregate=certify(word,sources,banks,rows,owner_index,engine,deadline,out)
    except TimeoutError as exc:
        timeout=str(exc)
    finally:
        alarm(0)
    projected=None if aggregate is None else {i:str(Fraction(v,aggregate[1])) for i,v in aggregate[0].items()}
    completed={r["key"] for r in out}
    print(dumps(dict(head=price["head"],caller=price["caller"],pins=PINS,controls=tests,caps=price["caps"],
        progress=progress,old_adds=old_adds,aggregate=projected,results=out,
        counts=Counter(r["proof"]["status"] for r in out),
        unvisited=[k for k in BANKS if k not in completed],timeout=timeout),indent=2,sort_keys=True))
    return 2 if timeout else 0


if __name__=="__main__":
    raise SystemExit(main())

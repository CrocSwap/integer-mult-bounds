"""Reverse chart continuity or second-prime checks on the exact R105 key sets."""
from argparse import ArgumentParser
from bisect import bisect_left
from collections import Counter, defaultdict
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic
import sys

ROOT = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
EVENTS = 76466
PINS = {
    "inputs/GEOMETRY.json": "2d0dee60998d168d2eff4c16794176c5ec3b4d18ffa8bde247602035f1b68129",
    "inputs/PRICE.json": "4e0d6436eb4fc6a9dfa34c05ba98aacc63e3a8bf7214145dd9f9254763c5a13e",
    "inputs/PREFIX.json": "65c11b0a42092557fe1c64b4feb2f61e2d16c636cfcaddf7f95ec09dbdd27452",
    "inputs/PREFIX-SECOND-PRIME.json": "51c9eb3af7b4d5ff60daef468f3bf262cb485bb88f4d0394d91b83d7eba2bffd",
    "inputs/ALIASES.json": "ba0120da7b05b948b1e8294c6b3844deade2c40be1f2e0abf4e0beef395f5c85",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}
MOD_PINS = {
    "inputs/SELECTION.json": "3bd7bdc9859436ef1d75d011e09d9dfc43a731c5b0a8e9c42fc96d9a6481a30c",
    "inputs/MODULAR.json": "1d99a9842dc8c42395878eb0c14b0027656041f150672491d65d3f023d9df23d",
    "inputs/r102_prefix.py": "505eca6677cc4e905494bdbf027d23c7ad288aa26889443db5d99d3ec41488f5",
    "inputs/second_prime.py": "21dbd96192e1f60c00ceddba01a7e8d0ddd7d6ad7da4ad3ed22ef2e47cc589c4",
}


def unique(items):
    d = dict(items)
    if len(d) != len(items):
        raise ValueError("duplicate JSON key")
    return d


def blocked(event, public):
    op, dst, *args = event
    if op in ("MOVE", "INIT", "CLEAR", "COPY"):
        return op
    assert op in ("ADD","SCALE") and Fraction(args[-2])
    return "public/owned" if op == "ADD" and ((dst < public) != (args[0] < public)) else None


def prefix_blocked(event, roles):
    op, dst, *args = event
    if dst not in roles:
        return False
    return not (op == "SCALE" or op == "ADD" and args[0] in roles)


def controls():
    assert blocked(["ADD",1,2,"-1/2",8],5) is None
    assert blocked(["ADD",7,1,"-1/2",8],5) == "public/owned"
    assert not prefix_blocked(["ADD",7,1,"-1/2",8],{1,2})
    assert prefix_blocked(["ADD",1,7,"-1/2",8],{1,2})
    assert prefix_blocked(["MOVE",1,8,9,False],{1,2})
    return ["invertible signed ADD", "owned reads preserve public prefix", "owned writes and public MOVE block"]


def span(frame):
    xs = {0}
    for v in frame:
        assert v not in xs
        xs |= {v ^ w for w in xs}
    return xs


def reverse(word, rows, cohort, deadline, state):
    n, owned, tape = (word[k] for k in ("public","owned_fields","program"))
    assert (n,owned,len(tape)) == (1501,68,EVENTS)
    frames=word["frames"]
    low,high=span(frames[602]),span(frames[127])
    charts={c for _,c in rows}
    assert len(charts)==5 and all(len(frames[c])==6 and low<span(frames[c])<high for c in charts)
    requests, contacts, writes = defaultdict(list), defaultdict(list), defaultdict(list)
    public_union={r for row in rows.values() for r in row["public"]}
    for t,c in rows:
        requests[t].append(c)
    live=word["final"]+[None]*owned
    state["events"]=0
    state["checked"]=[]
    for cut in range(EVENTS,-1,-1):
        state["first_unvisited_event"]=cut-1
        if (cut%128==0 or cut in requests) and monotonic()>=deadline:
            raise TimeoutError("reverse chronology cap")
        for c in requests.get(cut,[]):
            p=[r for r in range(n) if live[r]==c]
            o=[r for r in range(n,n+owned) if live[r]==c]
            assert rows[cut,c]==dict(key=[cut,c],public=p,owned=o,pivots=sorted(set(p)&cohort))
            state["checked"].append([cut,c])
        if cut==0:
            assert live==word["initial"]+[None]*owned
            state["first_unvisited_event"]=None
            break
        t=cut-1
        op,d,*a=e=tape[t]
        if op=="MOVE":
            f,z,flag=a
            assert live[d]==z and flag==(d>=n)
            live[d]=f
            incident=f,z
        elif op in ("INIT","CLEAR"):
            c,=a
            assert d>=n and live[d]==(c if op=="INIT" else None)
            live[d]=None if op=="INIT" else c
            incident=(c,)
        else:
            assert op in ("ADD","COPY","SCALE") and live[d]==a[-1]
            if op!="SCALE":
                assert d!=a[0] and live[a[0]]==live[d]
                assert op!="COPY" or d>=n
            incident=(a[-1],)
        if d in public_union:
            writes[d].append((t,e))
        for c in incident:
            if c in charts:
                contacts[c].append((t,e))
        state["events"]+=1
    return n, {c:list(reversed(v)) for c,v in contacts.items()}, {r:list(reversed(v)) for r,v in writes.items()}


def between(values,lo,hi):
    key=lambda row:row[0]
    return values[bisect_left(values,lo,key=key):bisect_left(values,hi,key=key)]


def component_summary(groups,known):
    return [dict(keys=g,reuses=[k for k in g if k in known]) for g in groups]


def alias(word,rows,cohort,known,prior,deadline,state):
    n, contacts, writes=reverse(word,rows,cohort,deadline,state)
    ordered=sorted(rows,key=lambda k:(k[1],k[0]))
    groups, public_groups, links, diagnostic=[],[],[],[]
    last=None
    for key in ordered:
        if monotonic()>=deadline:
            raise TimeoutError("alias key cap")
        strict_ok=public_ok=False
        if last is not None and last[1]==key[1]:
            lo,c=last
            hi=key[0]
            a,b=rows[last],rows[key]
            same=all(a[f]==b[f] for f in ("public","owned","pivots"))
            events=between(contacts.get(c,[]),lo,hi)
            blockers=[t for t,e in events if blocked(e,n)]
            strict_ok=same and not blockers
            fixed=set(a["public"])
            public_ok=a["public"]==b["public"] and not any(
                prefix_blocked(e,fixed) for r in fixed for _,e in between(writes.get(r,[]),lo,hi))
            assert not strict_ok or public_ok
            links.append(dict(left=last,right=key,same_bank=same,blockers=blockers,alias=strict_ok))
            if public_ok and not strict_ok:
                diagnostic.append(dict(left=last,right=key,events=events,strict_blockers=blockers))
        if not strict_ok:
            groups.append([])
        if not public_ok:
            public_groups.append([])
        groups[-1].append(key)
        public_groups[-1].append(key)
        last=key
    strict=component_summary(groups,known)
    public_only=component_summary(public_groups,known)
    assert len(links)==60 and prior["timeout"] is None and not prior["unvisited"]
    assert dumps(links,sort_keys=True)==dumps(prior["links"],sort_keys=True)
    assert dumps(strict,sort_keys=True)==dumps(prior["classes"],sort_keys=True)
    def reuse(components):
        return sorted(k for cls in components if cls["reuses"] for k in cls["keys"] if k not in known)
    return dict(agreement=True,links=links,strict_classes=strict,strict_new_reuses=reuse(strict),
                fixed_public_only_classes=public_only,fixed_public_new_reuses=reuse(public_only),
                diagnostic_additional_links=diagnostic)


def modular(root,word,rows,cohort,selection,prior,deadline,state):
    assert selection["head"]==prior["head"]==HEAD and prior["prime"]==65521
    assert prior["counts"]=={"prefix exclusion":16}
    cases={tuple(r["key"]):r for r in selection["selected"]}
    primary={tuple(r["key"]):r["prefix"] for r in prior["results"]}
    assert list(cases)==list(primary) and len(cases)==16
    assert cases.keys()<=rows.keys()
    for k,r in cases.items():
        assert all(r[f]==rows[k][f]==primary[k][f] for f in ("public","owned","pivots"))
    engine=run_path(str(root/"inputs/second_prime.py"))
    adapter=run_path(str(root/"inputs/r102_prefix.py"))
    assert engine["PRIME"]==65537
    checks=engine["controls"]()
    result={}
    adapter["sweep"](word,cohort,cases,primary,engine,deadline,state,result)
    assert len(result)==16 and state["first_unvisited_cut"] is None
    assert all(r["disposition"]=="excluded" for r in result.values())
    return dict(agreement=True,modulus=65537,rows=list(result.values()),controls=checks,
                certified_primary_axes=sum(bool(r["primary_minor_det_mod_65537"]) for r in result.values()),
                counts={"prefix exclusion":16})


def main():
    p=ArgumentParser(description=__doc__)
    p.add_argument("mode",choices=("alias","modular","controls"))
    p.add_argument("--root",type=Path,default=ROOT)
    a=p.parse_args()
    assert __debug__ and sys.version_info[:2]==(3,12)
    if a.mode=="controls":
        print(dumps(controls()))
        return
    seconds,cap=(20,65) if a.mode=="alias" else (25,16)
    pins=PINS if a.mode=="alias" else PINS|MOD_PINS
    def stop(*_):
        raise TimeoutError("hard runner cap")
    signal(SIGALRM,stop)
    alarm(seconds)
    deadline=monotonic()+seconds-2
    result,reason,state={},None,{}
    try:
        raw={}
        for rel,h in pins.items():
            data=(a.root/rel).read_bytes()
            if sha256(data).hexdigest()!=h:
                raise ValueError(f"changed dependency: {rel}")
            raw[rel]=data
        def read(name):
            return loads(raw[f"inputs/{name}.json"],object_pairs_hook=unique)
        price,geom,old,second=(read(name) for name in ("PRICE","GEOMETRY","PREFIX","PREFIX-SECOND-PRIME"))
        assert price["head"]==geom["head"]==old["head"]==second["head"]==HEAD
        rows={tuple(r["key"]):r for r in geom["all_representatives"]}
        assert len(rows)==len(geom["all_representatives"])==65 and geom["visited_events"]==EVENTS
        known={tuple(r["key"]) for r in old["rows"] if r["determinant"]}
        assert known=={tuple(r["key"]) for r in second["rows"] if r["independent_minor"]["determinant"]}
        assert len(known)==16 and old["counts"]==second["counts"]=={"excluded":16}
        cohort=set(price["cohort"])
        assert cohort=={1457,1458,1474,1475,1476}
        payload=decompress(raw["inputs/7334-WORD.json.gz"])
        assert sha256(payload).hexdigest()==PAYLOAD
        word=loads(payload,object_pairs_hook=unique)
        if a.mode=="alias":
            result=alias(word,rows,cohort,known,read("ALIASES"),deadline,state)
        else:
            result=modular(a.root,word,rows,cohort,read("SELECTION"),read("MODULAR"),deadline,state)
    except TimeoutError as exc:
        reason=str(exc)
    finally:
        alarm(0)
    print(dumps(dict(head=HEAD,pins=pins,mode=a.mode,cap_cases=cap,cap_seconds=seconds,progress=state,
                     new_support_cases=0 if a.mode=="alias" else 16,complete=reason is None,
                     timeout=reason,alias_controls=controls(),**result),indent=2,sort_keys=True))
    if reason:
        raise SystemExit(2)


if __name__=="__main__":
    main()

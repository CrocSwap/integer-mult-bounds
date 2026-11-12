"""Exact reverse continuation of R201 for all 62 remaining small banks."""
from collections import Counter,defaultdict
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps,loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM,alarm,signal
from time import monotonic

ROOT=Path(__file__).resolve().parent
PINS={
    "inputs/7334-WORD.json.gz":"4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/reverse_span.py":"f8b48f2ed99d003e20f5b3fb2270603c4edbc3ce9a01484102816aa2710ce9ff",
    "inputs/STAGE1.json":"ae434c63bfc6e28ae3374d246ad086def96ed3dc8ddba3e759eb60af391bfadc",
    "inputs/STAGE2.json":"6de2686c00d1682065fec128f7cc1938a646ebb72f1895c38babb72e7bbb7d6d",
    "inputs/stage2.py":"ff3c13d2fb2ccfa03903110cdd190db6a5619d4e8625090da4ca0753fe748872",
}
HEAD="aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER="07a76c5e2738882c0cb322278e56f6cae3c9885d"
PAYLOAD="9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
CASES,SECONDS=62,35


def unique(items):
    data=dict(items)
    assert len(data)==len(items),"duplicate key"
    return data


def read(name):
    raw=(ROOT/name).read_bytes()
    assert sha256(raw).hexdigest()==PINS[name],name
    return raw


def engine(name):
    read(name)
    return run_path(str(ROOT/name))


def stop(*_):
    raise TimeoutError("35-second reverse continuation cap")


def main():
    assert __debug__
    signal(SIGALRM,stop)
    alarm(SECONDS)
    deadline=monotonic()+SECONDS-1
    result={"head":HEAD,"caller":CALLER,"pins":PINS,"case_cap":CASES,"seconds_cap":SECONDS,
            "checked":[],"capped":False,"winner":None}
    keys=[]
    try:
        a,b=[loads(read("inputs/"+name),object_pairs_hook=unique) for name in ("STAGE1.json","STAGE2.json")]
        assert (a["head"],a["caller"])==(b["head"],b["caller"])==(HEAD,CALLER)
        assert b["stage1_sha256"]==PINS["inputs/STAGE1.json"] and not (a["capped"] or b["capped"])
        assert not (a["unvisited"] or b["unresolved_within_top_six"] or b["winner"])
        assert len(a["records"])==967 and len(a["screen_survivors"])==243 and len(b["checked"])==6
        used={tuple(x["clocks"]) for x in b["checked"]}
        assert used=={tuple(x) for x in b["frozen_keys"]}
        unresolved=[c for c in a["screen_survivors"] if tuple(c["clocks"]) not in used]
        assert len(unresolved)==237
        selected=[c for c in unresolved if c["bank_count"]<=19]
        assert len(selected)==CASES and sum(c["bank_count"]<10 for c in selected)==45
        keys=[c["clocks"] for c in selected]
        assert len({tuple(c) for c in keys})==CASES
        gross=sum(Q(c["gross"][1]) for c in selected)
        assert gross<Q("7.364") and all(Q(c["gross"][1])<1 for c in selected)
        result.update(frozen_keys=keys,prior_solved_count=len(used),
                      outside_small_bank_unresolved=[c["clocks"] for c in unresolved if c["bank_count"]>19],
                      relaxed_gross_upper=gross)
        raw=decompress(read("inputs/7334-WORD.json.gz"))
        assert sha256(raw).hexdigest()==PAYLOAD
        word=loads(raw,object_pairs_hook=unique)
        assert len(word["program"])==76466 and word["public"]==1501
        previous=engine("inputs/stage2.py")
        rowsolver=engine("inputs/reverse_span.py")
        banks=previous["capture"](word,selected)
        requests,ids=defaultdict(list),{}
        for c in selected:
            l,m,r=c["clocks"]
            roles,_=banks[l,m,r]
            for t,role in [(m,c["peer"]),*((r+1,x) for x in roles)]:
                if (t,role) not in ids:
                    ids[t,role]=len(ids)
                    requests[t].append((role,ids[t,role]))
        rows=rowsolver["transpose_prefix"](word,requests,len(ids),deadline)
        assert len(rows)==len(ids)
        result["reconstructed_rows"]=len(rows)
        result["controls"]=rowsolver["controls"]()
        for c in selected:
            l,m,r=c["clocks"]
            roles,lifetimes=banks[l,m,r]
            source=rows[ids[m,c["peer"]]]
            assert {str(j):str(Q(x,source[1])) for j,x in source[0].items()}==c["target_row"]
            bank=[(role,rows[ids[r+1,role]]) for role in roles]
            decision=rowsolver["exact_span"](bank,source)
            previous["validate"](decision,bank,source)
            record={"clocks":c["clocks"],"role":c["role"],"peer":c["peer"],"chart":c["chart"],
                    "bank_roles":roles,"gross":c["gross"],"ranks":c["ranks"],"decision":decision}
            result["checked"].append(record)
            if decision["status"]=="exact_span":
                add=word["program"][m]
                assert add[:3]==["ADD",c["role"],c["peer"]]
                coefficients={int(role):Q(value)*Q(add[3]) for role,value in decision["coefficients"].items()}
                result["winner"]={**record,"old_add":add,"applied_coefficients":coefficients,
                    "bank_cut":r+1,"direct_move":["MOVE",c["role"],word["program"][l][2],c["chart"],word["program"][l][4]],
                    "donor_lifetimes":{role:lifetimes.get(role,"public") for role in coefficients},
                    "coefficient_grid_preflight":all(abs(v)<=65534 and v.numerator.bit_length()<=24
                                                     and 37748736000%v.denominator==0 for v in coefficients.values())}
                break
    except TimeoutError as exc:
        result.update(capped=True,cap_reason=str(exc))
    finally:
        alarm(0)
    done={tuple(c["clocks"]) for c in result["checked"]}
    result["unvisited"]=[k for k in keys if tuple(k) not in done]
    result["statistics"]=Counter(c["decision"]["status"] for c in result["checked"])
    print(dumps(result,sort_keys=True,indent=2,default=str))
    if result["capped"]:
        raise SystemExit(2)


if __name__=="__main__":
    main()

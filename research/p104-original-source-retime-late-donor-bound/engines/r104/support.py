"""Exact rational membership of each sole ADD source in its late endpoint banks."""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic, perf_counter

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "lead/PRICE.json": "8fbd560cf7708b99609614a0b96d02b55efc55304225ddffa5dd223ed49d4073",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/R103-RETIMING.json": "331d26d99d45d24796253cd0bf86fdbd8b755ba164ca7765edc8304cc3365f6f",
    "inputs/donor_span.py": "4d5306e2c0b7e91c79d22c82e8e760aed2c311979298c558e631975d4d1ae5b1",
}


def unique(pairs):
    result = dict(pairs)
    if len(result)!=len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def checked(path):
    raw = (ROOT/path).read_bytes()
    if sha256(raw).hexdigest()!=PINS[path]:
        raise ValueError(f"changed dependency {path}")
    return raw


def ring_ok(value):
    d = value.denominator
    for p in (2,3,5):
        while d%p==0:
            d//=p
    return d==1 and abs(value)+1<2**16


def stop(*_):
    raise TimeoutError("hard runner timeout")


def main():
    assert __debug__
    price = json.loads(checked("lead/PRICE.json"),object_pairs_hook=unique)
    old=json.loads(checked("inputs/R103-RETIMING.json"),object_pairs_hook=unique)
    assert old["head"]==price["head"] and old["counts"]=={"different chart":18864}
    checked("inputs/donor_span.py")
    engine = run_path(str(ROOT/"inputs/donor_span.py"))
    checks = engine["controls"]()
    assert ring_ok(Q(-3,5)) and not ring_ok(Q(1,7))
    deadline = monotonic()+18
    signal(SIGALRM,stop)
    alarm(price["limits"]["runner_seconds"])
    results = []
    pending = []
    reason = None
    timings = {"coordinate_seconds":0.0,"same_snapshot_full_solve_seconds":0.0,"coordinate_decisions":0,"fallback_full_solve_seconds":0.0}
    keys = [p["key"]+[side] for p in price["candidates"] for side in ("entrance","exit")]
    assert len(keys)==len({tuple(k) for k in keys})==10
    try:
        raw = decompress(checked("inputs/7334-WORD.json.gz"))
        assert sha256(raw).hexdigest()==price["payload_sha256"]
        word = json.loads(raw,object_pairs_hook=unique)
        tape = word["program"]
        public = word["public"]
        req, targets = defaultdict(set),defaultdict(set)
        for p in price["candidates"]:
            f,g,d = p["key"]
            a,b,c = p["charts"]
            t,e = p["add"]
            s = e[2]
            assert f<t<g and d<public and tape[t]==e==["ADD",d,s,e[3],b]
            assert tape[f]==["MOVE",d,a,b,False] and tape[g]==["MOVE",d,b,c,False]
            for other in tape[f+1:t]+tape[t+1:g]:
                assert d not in (other[1:3] if other[0] in ("ADD","COPY") else other[1:2])
            targets[t].add(s)
            req[g].update(((a,d),(c,d)))
        banks,values = engine["snapshot"](word,req,targets,deadline)
        for p in price["candidates"]:
            _,g,d = p["key"]
            t,e = p["add"]
            s = e[2]
            a,_,c = p["charts"]
            for side,chart in (("entrance",a),("exit",c)):
                key = p["key"]+[side]
                if monotonic()>=deadline or (g,chart,d) not in banks or (t,s) not in values:
                    pending.append(key)
                    continue
                all_live = banks[g,chart,d]
                public_bank = {r:row for r,row in all_live.items() if r<public}
                target = values[t,s]
                started = perf_counter()
                covered = {coordinate for row in public_bank.values() for coordinate in row}
                separator = next(((i, str(target[i])) for i in sorted(target) if i not in covered), None)
                timings["coordinate_seconds"] += perf_counter()-started
                if separator:
                    timings["coordinate_decisions"] += 1
                started = perf_counter()
                ans = engine["solve"](target,public_bank,deadline)
                elapsed = perf_counter()-started
                timings["same_snapshot_full_solve_seconds"] += elapsed
                if separator is None:
                    timings["fallback_full_solve_seconds"] += elapsed
                if separator and ans is not None:
                    assert ans["matching_coefficients"] is None
                if ans is None:
                    pending.append(key)
                    continue
                weights = ans["matching_coefficients"]
                if weights is None:
                    status,coefficients = "outside donor span",None
                else:
                    final = {r:Q(e[3])*Q(v) for r,v in weights.items()}
                    status = "exact legal coefficients" if all(ring_ok(q) for q in final.values()) else "coefficient gate unresolved"
                    coefficients = {r:str(q) for r,q in final.items()}
                results.append({"key":key,"cut":g,"chart":chart,"source":[t,s],"source_nnz":len(target),
                    "bank_roles":sorted(public_bank),"owned_donors_excluded":sorted(set(all_live)-set(public_bank)),
                    "status":status,"replacement_coefficients":coefficients,"coordinate_separator":separator,**ans})
    except TimeoutError as exc:
        reason = str(exc)
    finally:
        alarm(0)
    seen = {tuple(r["key"]) for r in results}
    pending = [k for k in keys if tuple(k) not in seen]
    out = {"head":price["head"],"pins":PINS,"controls":checks+["retained scalar denominator and size"],
           "cap":{"cases":10,"runner_seconds":20},"results":results,"unvisited":pending,"timeout":reason,
           "counts":Counter(r["status"] for r in results)}
    print(json.dumps(out,indent=2,sort_keys=True))
    import sys
    print(json.dumps(timings,sort_keys=True),file=sys.stderr)


if __name__=="__main__":
    main()

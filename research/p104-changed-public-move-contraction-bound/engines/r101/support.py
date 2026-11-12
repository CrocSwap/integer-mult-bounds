"""Exact rational membership of each sole ADD source in its endpoint banks."""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "lead/PRICE.json": "ac5ecb17f0e9f3c068423998b350a78c1a4769b6f61b50838be5f3e0d0b1a00c",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
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
    keys = [p["key"]+[side] for p in price["candidates"] for side in ("entrance","exit")]
    assert len(keys)==len({tuple(k) for k in keys})==price["limits"]["cases"]
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
            req[t].update(((a,d),(c,d)))
        banks,values = engine["snapshot"](word,req,targets,deadline)
        for p in price["candidates"]:
            _,_,d = p["key"]
            t,e = p["add"]
            s = e[2]
            a,_,c = p["charts"]
            for side,chart in (("entrance",a),("exit",c)):
                key = p["key"]+[side]
                if monotonic()>=deadline or (t,chart,d) not in banks or (t,s) not in values:
                    pending.append(key)
                    continue
                all_live = banks[t,chart,d]
                public_bank = {r:row for r,row in all_live.items() if r<public}
                target = values[t,s]
                ans = engine["solve"](target,public_bank,deadline)
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
                results.append({"key":key,"chart":chart,"source":[t,s],"source_nnz":len(target),
                    "bank_roles":sorted(public_bank),"owned_donors_excluded":sorted(set(all_live)-set(public_bank)),
                    "status":status,"replacement_coefficients":coefficients,**ans})
    except TimeoutError as exc:
        reason = str(exc)
    finally:
        alarm(0)
    seen = {tuple(r["key"]) for r in results}
    pending = [k for k in keys if tuple(k) not in seen]
    out = {"head":price["head"],"pins":PINS,"controls":checks+["retained scalar denominator and size"],
           "cap":price["limits"],"results":results,"unvisited":pending,"timeout":reason,
           "counts":Counter(r["status"] for r in results)}
    print(json.dumps(out,indent=2,sort_keys=True))


if __name__=="__main__":
    main()

"""Census consecutive paid MOVE pairs on the exact changed public roles."""
from collections import Counter
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "lead/PRICE.json": "7109125bbf60e3015c8c0ac7b10b24b7de61f358c1508d06604ebccd89ef6343",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
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


def space(frame):
    vals = {0}
    for v in frame:
        assert v not in vals
        vals.update(v^a for a in tuple(vals))
    return frozenset(vals)


def touches(event):
    op,r,*args = event
    return (r,args[0]) if op in ("ADD","COPY") else (r,)


def disposition(contacts):
    if any(e[0]!="SCALE" for _,e in contacts):
        return "binary barrier"
    return "scales only" if contacts else "contact free"


def controls():
    assert touches(["ADD",1,2,"-5",4]) == (1,2)
    assert touches(["COPY",5,2,"3/2",4]) == (5,2)
    assert disposition([(2,["SCALE",1,"-5",4])]) == "scales only"
    assert disposition([(2,["ADD",2,1,"-5",4])]) == "binary barrier"
    assert disposition([]) == "contact free"
    return ["source-only ADD barrier","source-only COPY barrier","nonzero unary SCALE","contact-free"]


def stopped(*_):
    raise TimeoutError("hard runner cap")


def main():
    assert __debug__
    price = json.loads(checked("lead/PRICE.json"),object_pairs_hook=unique)
    caps = price["limits"]
    signal(SIGALRM,stopped)
    alarm(caps["runner_seconds"])
    deadline = monotonic()+18
    pairs = []
    moves = Counter()
    tail = None
    reason = None
    try:
        raw = decompress(checked("inputs/7334-WORD.json.gz"))
        assert sha256(raw).hexdigest()==price["word_payload_sha256"]
        word = json.loads(raw,object_pairs_hook=unique)
        n = word["public"]
        program = word["program"]
        assert len(program)==caps["event_cap"] and n==1501
        roles = set(price["roles"])
        assert len(roles)==14 and max(roles)<n
        state = word["initial"][:] + [None]*word["owned_fields"]
        spans = [space(frame) for frame in word["frames"]]
        ranks = list(map(len,word["frames"]))
        profiles = {tuple(q["ranks"]):q for q in price["profiles"]}
        pending = {}
        for t,event in enumerate(program):
            tail = t
            if t%128==0 and monotonic()>=deadline:
                raise TimeoutError("cooperative runner cap")
            op,d,*a = event
            current = state[d]
            if op=="MOVE":
                before,after,owned = a
                assert before==current and owned==(d>=n)
                assert spans[before]<spans[after] or owned and spans[after]<spans[before]
                if d in roles:
                    moves[d]+=1
                    if d in pending:
                        if len(pairs)>=caps["paid_pairs"]:
                            raise TimeoutError("paid pair cap")
                        earlier,old,contacts = pending[d]
                        assert old[3]==before
                        start = old[2]
                        p,q = ranks[before]-ranks[start],ranks[after]-ranks[before]
                        assert p>0 and q>0 and spans[start]<spans[before]<spans[after]
                        quote = profiles[(*sorted((p,q)),p+q)]
                        pairs.append({"key":[earlier,t,d],"charts":[start,before,after],"ranks":[p,q,p+q],
                                      "contacts":contacts,"status":disposition(contacts),
                                      "full_probe":quote["full_probe"],"net":quote["net"]})
                    pending[d]=(t,event,[])
                state[d]=after
            elif op=="INIT":
                assert current is None and d>=n
                state[d]=a[0]
            elif op=="CLEAR":
                assert current==a[0] and d>=n
                state[d]=None
            else:
                assert current==a[-1] and op in ("ADD","COPY","SCALE") and Fraction(a[-2])
                if op in ("ADD","COPY"):
                    assert state[a[0]]==current and a[0]!=d
                for r in touches(event):
                    if r in pending:
                        pending[r][2].append([t,event])
        assert state==word["final"]+[None]*word["owned_fields"]
        assert all(c<=9 for c in moves.values())
        assert len(pairs)==sum(c-1 for c in moves.values())
        tail = None
    except TimeoutError as exc:
        reason = str(exc)
    finally:
        alarm(0)
    eligible=sorted((r for r in pairs if r["status"]!="binary barrier"),
                    key=lambda r:(-Fraction(r["net"][0]),r["key"]))
    out = {"head":price["head"],"pins":PINS,"controls":controls(),"caps":caps,"moves":moves,"pairs":pairs,
           "counts":Counter(r["status"] for r in pairs),"candidate_keys":[r["key"] for r in eligible],
           "first_unvisited_event":tail,"timeout":reason}
    print(json.dumps(out,indent=2,sort_keys=True))
    if reason:
        raise SystemExit(2)


if __name__=="__main__":
    main()

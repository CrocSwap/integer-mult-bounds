"""Two-sided exterior minors on frozen virtual two-mover banks."""
from collections import Counter
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "lead/SELECTION.json": "3a6f588eb597e56abfbfe568319fc81294d16d37f03f8b6159ba5b133dc2f416",
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/second_prime.py": "21dbd96192e1f60c00ceddba01a7e8d0ddd7d6ad7da4ad3ed22ef2e47cc589c4",
}


def side(word,banks,cohort,deadline,engine,back):
    n = word["public"]
    owned = word["owned_fields"]
    tape = word["program"]
    start = "final" if back else "initial"
    active = word[start][:]+[None]*owned
    vectors = [{i:1} for i in range(n)]+[None]*owned
    cuts = range(len(tape),-1,-1) if back else range(len(tape)+1)
    out = {}
    fresh,denom = set(),set()
    for t in cuts:
        if (t%128==0 or t in banks) and monotonic()>=deadline:
            break
        if t in banks:
            out[t] = engine["classify"](banks[t],vectors,cohort)
        if t == (0 if back else len(tape)):
            assert active == word["initial" if back else "final"]+[None]*owned
            break
        engine["apply"](tape[t-1 if back else t],active,vectors,fresh,n,denom,back)
    return out,sorted(denom)


def main():
    assert __debug__
    documents = {}
    for path,digest in PINS.items():
        raw = (ROOT/path).read_bytes()
        if sha256(raw).hexdigest() != digest:
            raise ValueError(f"changed dependency {path}")
        documents[path] = raw
    engine = run_path(str(ROOT/"inputs/second_prime.py"))
    unique = engine["unique"]
    word = json.loads(decompress(documents["inputs/7334-WORD.json.gz"]),object_pairs_hook=unique)
    selection = json.loads(documents["lead/SELECTION.json"],object_pairs_hook=unique)
    cohort = set(json.loads(documents["inputs/R92-PRICE.json"],object_pairs_hook=unique)["endpoint_cohort"])
    assert len(word["program"])==76466 and len(cohort)==615
    controls = engine["controls"]()
    rows = selection["selected"]
    banks = {r["bank"]["key"][0]:r["bank"]["public"] for r in rows}
    assert len(banks)==len(rows)==selection["case_cap"]==16
    deadline = monotonic()+22
    f,df = side(word,banks,cohort,deadline,engine,False)
    open_banks = {t:v for t,v in banks.items() if t in f and f[t]["rank"]<2}
    s,ds = side(word,open_banks,cohort,deadline,engine,True) if open_banks else ({},[])
    results = []
    for row in rows:
        t = row["bank"]["key"][0]
        p,q = f.get(t),s.get(t)
        if p and p["rank"] == 2:
            status = "prefix exclusion"
        elif q:
            status = "suffix exclusion" if q["rank"]==2 else "dual drop"
        else:
            status = "capped"
        results.append(row|dict(status=status,prefix=p,suffix=q))
    print(json.dumps(dict(head=selection["head"],pins=PINS,cap=16,runner_seconds=25,
        prime=engine["PRIME"],controls=controls,denominator_units={"prefix":df,"suffix":ds},
        results=results,counts=Counter(r["status"] for r in results),unvisited=selection["unselected"]),
        indent=2,sort_keys=True))


if __name__=="__main__":
    main()

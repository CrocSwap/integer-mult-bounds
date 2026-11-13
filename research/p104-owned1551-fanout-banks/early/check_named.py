"""Check the named existing first-return carriers for the owned1551 fanout."""
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parents[1] / "inputs"
CUT, SOURCE, OWNER = 46149, 45636, 1551
CARRIERS = (862, 988, 991, 1499)
ARRIVALS = {817: 48748, 790: 47990, 873: 46147,
            1497: 51351, 878: 47955, 833: 48877}
WRITES = dict(zip(ARRIVALS, (45639, 45641, 45643, 45646, 45649, 45651)))


def cap(_signal, _frame):
    raise SystemExit(124)


def touches(event):
    return set(event[1:3] if event[0] in ("ADD", "COPY") else event[1:2])


def main():
    assert __debug__
    signal(SIGALRM, cap)
    alarm(30)
    helper = ROOT / "gate.py"
    assert sha256(helper.read_bytes()).hexdigest() == "aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9"
    engine = run_path(str(helper))
    data = {name: (ROOT / name).read_bytes() for name in engine["PINS"]}
    assert {name: sha256(blob).hexdigest() for name, blob in data.items()} == engine["PINS"]
    raw = decompress(data["7481-WORD.json.gz"])
    assert sha256(raw).hexdigest() == "64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8"
    word = loads(raw)
    tape = word["program"]
    assert tape[SOURCE] == ["ADD", OWNER, 862, "-1", 1091]
    assert tape[45638] == ["MOVE", OWNER, 1091, 267, True]
    assert tape[45652] == ["CLEAR", OWNER, 267]
    assert tape[CUT-1:CUT+1] == [["MOVE", 862, 1091, 127, False], ["ADD", 873, 862, "1", 127]]
    for role, clock in WRITES.items():
        assert tape[clock] == ["ADD", role, OWNER, "1", 267]
        arrival = ARRIVALS[role]
        assert tape[arrival] == ["MOVE", role, 267, 127, False]
        assert all(role not in touches(e) for e in tape[clock+1:arrival])
    assert [i for i in range(SOURCE,45653) if OWNER in touches(tape[i])] == sorted([SOURCE,45638,45652]+list(WRITES.values()))
    _, live, _ = engine["census"](word, CUT)
    assert all(live[role] == 127 for role in CARRIERS+(873,))
    read = engine["exact_cut_rows"]
    target, = read(tape[:SOURCE],[862],word["public"])
    offered = read(tape[:CUT], CARRIERS+(873,), word["public"])
    old_first = offered.pop()
    edited_first = old_first.copy()
    for i,c in target.items():
        engine["add"](edited_first,i,c)
    assert not {873,OWNER}.intersection(CARRIERS)
    pivots = engine["basis"](offered)
    residual, coefficient = engine["representation"](pivots,target)
    # Also allow self-scale/readout from the uncorrected first recipient.
    broad = offered + [edited_first]
    extra = engine["basis"](broad)
    broad_residual, broad_coeff = engine["representation"](extra,target)
    witness, response = {}, Q(0)
    if broad_residual:
        def separate(j):
            probe = {j:Q(1)}
            for pivot,(row,_) in sorted(extra.items(),reverse=True):
                val = -sum(v*probe.get(i,0) for i,v in row.items() if i!=pivot)
                if val:
                    probe[pivot]=val
            return probe
        witness = min(map(separate,broad_residual),key=lambda p:(len(p),max(p)))
        assert all(sum(v*witness.get(i,0) for i,v in row.items())==0 for row in broad)
        response = sum(v*witness.get(i,0) for i,v in target.items())
        assert response
    app = loads(data["7481-APPLICATION.json"])
    assert app["caller_head"] == "07a76c5e2738882c0cb322278e56f6cae3c9885d"
    lo,hi=map(Q,app["directed_crossing_bracket"])
    h=run_path(str(ROOT/"pricing.py"))["power_bounds"]
    assert len(word["frames"][267])-len(word["frames"][1091])==4
    gross=[17*h(4,hi)[0],17*h(4,lo)[1]]
    assert 17 < gross[0] <= gross[1] < 68
    print(dumps({"status":"NAMED_ROUTE_EXCLUDED_EVEN_WITH_RECIPIENT" if broad_residual else "BROAD_SUPPORT_PASSES",
                 "case_cap":1,"cap_seconds":30,"cut":CUT,"source":SOURCE,"recipient":873,
                 "named_carriers":CARRIERS,"bank_rank":len(pivots),"with_recipient_rank":len(extra),
                 "named_residual":residual,"named_combination":coefficient,
                 "broad_residual":broad_residual,"broad_combination":broad_coeff,
                 "witness":witness,"target_response":response,"writes":WRITES,"arrivals":ARRIVALS,
                 "gross":gross,"gross_display":list(map(float,gross))},sort_keys=True,indent=2,default=str))
    alarm(0)


if __name__=="__main__":
    main()

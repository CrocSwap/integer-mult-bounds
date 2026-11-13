"""Check one exposed role1451 input against its first old outward read."""
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import alarm

ROOT = Path(__file__).resolve().parent
CUT, READ = 37945, 37946


def span(vectors):
    values = {0}
    for vector in vectors:
        values |= {vector ^ old for old in values}
    return values


def main():
    assert __debug__
    alarm(30)
    helper = ROOT / "gate.py"
    assert sha256(helper.read_bytes()).hexdigest() == "aa13cd2797877ef7328d5bcda24be51815fddcc4e8ae091382ad963fb978e5e9"
    engine = run_path(str(helper))
    inputs = {name: (ROOT / name).read_bytes()
              for name in ("7481-WORD.json.gz", "7481-APPLICATION.json", "pricing.py")}
    assert all(sha256(raw).hexdigest() == engine["PINS"][name] for name, raw in inputs.items())
    native = decompress(inputs["7481-WORD.json.gz"])
    assert sha256(native).hexdigest() == "64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8"
    word = loads(native)
    application = loads(inputs["7481-APPLICATION.json"])
    assert application["caller_head"] == "07a76c5e2738882c0cb322278e56f6cae3c9885d"
    tape = word["program"]
    assert tape[36564:36566] == [["ADD", 1451, 451, "-1", 595], ["SCALE", 1451, "-1", 595]]
    path = [(36587, 3, 81), (36614, 81, 253), (36642, 253, 262), (37944, 262, 737)]
    assert all(tape[clock] == ["MOVE", 992, before, after, False] for clock,before,after in path)
    assert tape[36588] == ["ADD", 857, 992, "-1", 81]
    assert tape[CUT:READ+1] == [["MOVE", 1451, 595, 737, False], ["ADD", 992, 1451, "-1", 737]]
    assert tape[39823] == ["MOVE", 1495, 595, 737, False]
    assert tape[39877] == ["MOVE", 1451, 737, 529, False]
    assert word["initial"][1451] == 595 and word["final"][1451] == 529
    frames = [word["frames"][chart] for chart in (595,737,529)]
    assert [len(row) for row in frames] == [1,4,7] and span(frames[0]) < span(frames[1]) < span(frames[2])
    _, at_source, _ = engine["census"](word, CUT)
    _, at_read, _ = engine["census"](word, READ)
    assert at_source[451] == at_source[1451] == 595 and at_source[992] == 737
    bank = sorted(role for role,chart in at_read.items() if chart == 737)
    assert bank == [992,1451] and at_read[451] == 595
    rows = engine["exact_cut_rows"]
    old_451, old_1451 = rows(tape[:CUT], [451,1451], word["public"])
    assert old_451 == {1243:Q(1),925:Q(-1,2),974:Q(-1,2),911:Q(-1,2),961:Q(-1,2),716:Q(1)}
    exposed = old_451.copy()
    for key,value in old_1451.items():
        engine["add"](exposed, key, -value)
    assert exposed == {1451:Q(1)}
    old_992, old_read_source = rows(tape[:READ], [992,1451], word["public"])
    assert old_read_source == old_1451
    assert old_992.get(716, 0) == exposed.get(716, 0) == 0
    assert old_451[716] == old_read_source[716] == 1
    lo,hi = map(Q,application["directed_crossing_bracket"])
    price = run_path(str(ROOT / "pricing.py"))["power_bounds"]
    gross = [17*(2*price(3,hi)[0]-price(6,lo)[1]),17*(2*price(3,lo)[1]-price(6,hi)[0])]
    assert 0 < gross[0] <= gross[1] < 17
    print(dumps({"cut": CUT, "first_outward_read": READ, "bank": bank, "paid_992_path": path,
                 "old_451": old_451, "exposed_input": exposed, "probe": {716:1},
                 "probe_on_old_992": 0, "probe_on_omitted_451": 1,
                 "required_old_outward_increment": -1, "paid_signed_delta": {},
                 "productive_signed_delta": {3:34,6:-17}, "gross_raw": gross,
                 "cases": 1, "runner_cap_seconds": 30, "status": "FIXED_FIRST_OUTWARD_READ_EXCLUDED"},
                sort_keys=True, indent=2, default=str))
    alarm(0)


if __name__ == "__main__":
    main()

"""Verify the first role1451 outgoing ADD on one exact input column."""
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
CUT = 37945
READ = 37946


def timeout(_signal, _frame):
    raise SystemExit(124)


def evaluate(word, source):
    public = word["public"]
    values = [Fraction(role == source) for role in range(public)]
    values += [None] * word["owned_fields"]
    charts = word["initial"] + [None] * word["owned_fields"]
    observations = {}
    roles = (451, 1451, 992)
    for clock, (op, role, *arguments) in enumerate(word["program"][:READ + 1]):
        if clock in (CUT, READ):
            observations[clock] = {q: (charts[q], values[q]) for q in roles}
        if op == "INIT":
            assert charts[role] is None and values[role] is None
            charts[role] = arguments[0]
            values[role] = Fraction()
        elif op == "CLEAR":
            assert role >= public and charts[role] == arguments[0]
            charts[role] = values[role] = None
        elif op == "MOVE":
            old_chart, new_chart, owned = arguments
            assert charts[role] == old_chart and owned == (role >= public)
            charts[role] = new_chart
        elif op == "SCALE":
            coefficient, chart = arguments
            assert charts[role] == chart
            values[role] *= Fraction(coefficient)
        else:
            assert op in ("ADD", "COPY")
            donor, coefficient, chart = arguments
            assert charts[role] == charts[donor] == chart
            if op == "COPY":
                assert values[role] == 0
            values[role] += Fraction(coefficient) * values[donor]
    at_source = observations[CUT]
    exposed = at_source[451][1] - at_source[1451][1]
    bank = observations[READ]
    increment = values[992] - bank[992][1]
    assert sorted(q for q, chart in enumerate(charts) if chart == 737) == [992,1451]
    return observations, exposed, increment


def main():
    assert __debug__
    signal(SIGALRM, timeout)
    alarm(30)
    blob = (ROOT / "7481-WORD.json.gz").read_bytes()
    assert sha256(blob).hexdigest() == "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9"
    raw = decompress(blob)
    assert sha256(raw).hexdigest() == "64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8"
    word = loads(raw)
    assert word["program"][CUT:READ+1] == [
        ["MOVE",1451,595,737,False], ["ADD",992,1451,"-1",737],
    ]
    observations, exposed, increment = evaluate(word, 716)
    assert observations[CUT] == {451:(595,1),1451:(595,1),992:(737,0)}
    assert observations[READ] == {451:(595,1),1451:(737,1),992:(737,0)}
    assert exposed == 0 and increment == -1
    zero, zero_exposed, zero_increment = evaluate(word, None)
    assert zero_exposed == zero_increment == 0
    assert not any(value for at_cut in zero.values() for _, value in at_cut.values())
    print(dumps({"status": "PASS_LITERAL_FORWARD_FIRST_OUTWARD_SEPARATOR",
                 "case_cap": 1, "runner_cap_seconds": 30,
                 "probe": {716:1}, "observations": observations, "exposed_x1451": exposed,
                 "old_outward_increment": increment, "zero_control": True},
                sort_keys=True, indent=2, default=str))
    alarm(0)


if __name__ == "__main__":
    main()

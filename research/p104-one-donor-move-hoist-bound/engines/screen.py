"""Compare the 13 frozen donor-hoist pairs on two exact modular inputs."""
from collections import defaultdict
from fractions import Fraction
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from random import Random
from signal import SIGALRM, alarm, signal
import sys

P = 65521
SEEDS = (176001, 176002)
ZIP = "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"


@cache
def coefficient(s):
    q = Fraction(s)
    return q.numerator * pow(q.denominator, -1, P) % P


def stop(*_):
    raise TimeoutError("30-second screen cap")


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(30)
    raw = Path(sys.argv[1]).read_bytes()
    assert sha256(raw).hexdigest() == ZIP
    decoded = decompress(raw)
    assert sha256(decoded).hexdigest() == PAYLOAD
    word = loads(decoded)
    tape = word["program"]
    n = word["public"]
    geo_raw = Path(__file__).with_name("inputs").joinpath("GEOMETRY.json").read_bytes()
    geometry = loads(geo_raw)
    assert len(tape) == geometry["events"] == 76466
    pairs = defaultdict(list)
    for row in geometry["records"]:
        clock, owner, dest = row["clock"], row["owner"], row["to_chart"]
        assert tape[clock] == ["MOVE", owner, row["from_chart"], dest, True]
        for donor, time, low, high, owned in row["candidates"]:
            assert high == dest and tape[time] == ["MOVE", donor, low, high, owned]
            for e in tape[clock+1:time]:
                assert e[1] != donor and (e[0] not in ("ADD","COPY") or e[2] != donor)
            pairs[clock].append((owner, donor, time))
    assert sum(map(len, pairs.values())) == geometry["donor_pairs"] == 13
    generators = [Random(s) for s in SEEDS]
    values = [[g.randrange(P) for g in generators] for _ in range(n)]
    values.extend([[0,0] for _ in range(word["owned_fields"])])
    cases = []
    for clock, (op, r, *args) in enumerate(tape):
        for owner, donor, time in pairs.get(clock, ()):
            a, b = values[owner], values[donor]
            signs = [s for s in (-1,1) if all((x-s*y)%P==0 for x,y in zip(a,b,strict=True))]
            cases.append({"key":[clock,owner,donor,time],"owner":a.copy(),"donor":b.copy(),"signs":signs})
        if op in ("INIT","CLEAR"):
            values[r] = [0,0]
        elif op == "SCALE":
            a = coefficient(args[0])
            values[r] = [a*x % P for x in values[r]]
        elif op in ("ADD","COPY"):
            donor,q,_ = args
            if op == "COPY":
                assert values[r] == [0,0] and r>=n
            a = coefficient(q)
            values[r] = [(x+a*y)%P for x,y in zip(values[r],values[donor],strict=True)]
        else:
            assert op == "MOVE"
    alarm(0)
    print(dumps({"word_zip":ZIP,"word_payload":PAYLOAD,"geometry_sha256":sha256(geo_raw).hexdigest(),
        "modulus":P,"seeds":SEEDS,"cases":cases,"survivors":[r for r in cases if r["signs"]]},
        indent=2,sort_keys=True))


if __name__ == "__main__":
    main()

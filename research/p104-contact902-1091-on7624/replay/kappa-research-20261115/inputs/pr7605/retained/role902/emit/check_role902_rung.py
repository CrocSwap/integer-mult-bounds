"""Freeze the sole consecutive public pair and its directed paid delta."""
from argparse import ArgumentParser
from collections import defaultdict
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import signal

PINS = {
    "COMPOSED-WORD.json.gz": "926bbb01254b96e9f8a67d4b7c616f89105686ef1acd14438ac2aad06ba58a1c",
    "COMPOSED-APPLICATION.json": "d9b5d292abb87c87eb3fd3f53501e14d77629ca4adca77a527ff2cf5b58df514",
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
CANONICAL = "2acc6bfd2807239fafdb3f9e09ff8ad34703df958496590ab657ef0b9ac93aef"
FIRST, SECOND, ROLE, CAP = 40950, 40951, 902, 30


def subspace(basis):
    span = {0}
    for axis in basis:
        assert axis not in span
        span |= {axis ^ value for value in span}
    return span


def emit(**record):
    print(json.dumps(record, sort_keys=True, default=str), flush=True)


def main():
    assert __debug__
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("inputs", type=Path)
    parser.add_argument("--candidate", type=Path)
    args = parser.parse_args()

    def timeout(_sig, _frame):
        emit(status="UNRESOLVED_CAP", cap_seconds=CAP)
        raise SystemExit(124)

    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(CAP)
    raw = {name:(args.inputs/name).read_bytes() for name in PINS}
    assert {name:sha256(data).hexdigest() for name,data in raw.items()} == PINS
    payload = gzip.decompress(raw["COMPOSED-WORD.json.gz"])
    assert sha256(payload).hexdigest() == CANONICAL
    word = json.loads(payload)
    application = json.loads(raw["COMPOSED-APPLICATION.json"])
    caller = json.loads(raw["7113-CALLER.json"])
    assert application["candidate_canonical_sha256"] == CANONICAL
    assert application["claim_decimal"] == "0.003647969120276"
    assert application["caller_sha256"] == PINS["7113-CALLER.json"]
    calls = caller["stages"]
    assert calls == 17
    tape = word["program"]
    assert len(tape) == 76491
    assert tape[FIRST:SECOND+2] == [
        ["MOVE",ROLE,618,789,False], ["MOVE",ROLE,789,913,False],
        ["ADD",985,ROLE,"-1",913],
    ]
    contacts = defaultdict(list)
    for clock,event in enumerate(tape):
        contacts[event[1]].append(clock)
        if event[0] in ("ADD","COPY"):
            contacts[event[2]].append(clock)
    pairs = []
    for role, clocks in contacts.items():
        if role >= word["public"]:
            continue
        for a,b in zip(clocks,clocks[1:]):
            if tape[a][0] == tape[b][0] == "MOVE" and tape[a][3] == tape[b][2]:
                pairs.append((role,a,b))
    assert pairs == [(ROLE,FIRST,SECOND)]
    frames = word["frames"]
    assert subspace(frames[618]) < subspace(frames[789]) < subspace(frames[913])
    assert [len(frames[k]) for k in (618,789,913)] == [3,5,7]
    lo,hi = map(Fraction,application["raw_crossing"])
    power = run_path(str(args.inputs/"pricing.py"))["power_bounds"]
    gross = [calls*(2*power(2,hi)[0]-power(4,lo)[1]),
             calls*(2*power(2,lo)[1]-power(4,hi)[0])]
    assert Fraction("0.17129252869815747") <= gross[0] <= gross[1] <= Fraction("0.17129252869815749")
    program = tape[:FIRST] + [["MOVE",ROLE,618,913,False]] + tape[SECOND+1:]
    candidate = dict(word, program=program)
    canonical = json.dumps(candidate, sort_keys=True, separators=(",",":")).encode()
    if args.candidate:
        with args.candidate.open("xb") as output:
            output.write(gzip.compress(canonical,mtime=0))
    emit(status="PASS_ROLE902_LITERAL_AND_PRICE_PREFLIGHT", candidate_sha256=sha256(canonical).hexdigest(),
         pins=PINS, public_candidates=pairs, cases_completed=1, cap_seconds=CAP,
         native_paid_delta={2:-2,4:1}, signed_paid_delta={2:-34,4:17},
         signed_productive_delta={}, optimistic_directed_saving=gross,
         pending=["direct signed chart lowering","complete native and signed replay"])
    signal.alarm(0)


if __name__ == "__main__":
    main()

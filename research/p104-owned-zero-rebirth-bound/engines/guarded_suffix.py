"""Independently test each owned zero-rebirth in a separate exact suffix walk."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/7334-WORD.json.gz": "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
    "inputs/R137-RESULT.json": "a109deda97d3b4f5ceb52814a50186035ea44ac1bdaf47281f564dcc2da239db",
    "inputs/R137-PRICE.json": "1e8270d9a48728327f7eab9610a272fbb8ef09518dc4ddc5ceb573be00ae2beb",
}
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
CASES, EVENTS, SECONDS = 47, 76466, 25
ZERO, ONE = Q(0), Q(1)


def unique(pairs):
    answer = dict(pairs)
    if len(answer) != len(pairs):
        raise ValueError("duplicate JSON key")
    return answer


def authenticate(root, path, digest):
    data = (root / path).read_bytes()
    if sha256(data).hexdigest() != digest:
        raise ValueError("changed dependency " + path)
    return data


def add(vector, role, value):
    if value:
        total = vector.get(role, ZERO) + value
        if total:
            vector[role] = total
        else:
            vector.pop(role, None)


@lru_cache(maxsize=None)
def scalar(token):
    return Q(token)


def pullback(tape, cut, role, coordinate, lower=0):
    """One coefficient of a prefix or suffix, computed as a reverse covector."""
    covector = {role: ONE}
    for clock in range(cut - 1, lower - 1, -1):
        op, dst, *args = tape[clock]
        if dst not in covector:
            continue
        value = covector[dst]
        if op in ("INIT", "CLEAR"):
            del covector[dst]
        elif op == "SCALE":
            covector[dst] = value * scalar(args[0])
        elif op in ("ADD", "COPY"):
            if op == "COPY":
                del covector[dst]
            add(covector, args[0], value * scalar(args[1]))
        else:
            assert op == "MOVE"
    return covector.get(coordinate, ZERO)


def suffix(tape, cut, role, public):
    """One exact response column. Guard values are observed before writes."""
    effect = {role: ONE}
    guards = []
    for clock in range(cut, len(tape)):
        if not effect:
            break
        op, dst, *args = tape[clock]
        if op == "ADD":
            incoming = effect.get(args[0], ZERO)
            if incoming:
                add(effect, dst, incoming * scalar(args[1]))
        elif op == "COPY":
            dirty = effect.pop(dst, ZERO)
            if dirty:
                guards.append([clock, dst, str(dirty)])
            incoming = effect.get(args[0], ZERO)
            if incoming:
                effect[dst] = incoming * scalar(args[1])
        elif op in ("INIT", "CLEAR"):
            effect.pop(dst, None)
        elif op == "SCALE" and dst in effect:
            effect[dst] *= scalar(args[0])
        else:
            assert op in ("MOVE", "SCALE")
    assert all(r < public for r in effect)
    return guards, [[r, str(value)] for r, value in sorted(effect.items())]


def controls():
    # Public response can cancel even though there are literal outward reads.
    assert suffix([["ADD",0,2,"1",4], ["ADD",0,2,"-1",4],
                   ["CLEAR",2,4]], 0, 2, 2) == ([], [])
    # COPY consumes the original clean destination before overwriting it.
    assert suffix([["COPY",2,1,"1/2",4], ["CLEAR",2,4]], 0, 2, 2) == (
        [[0,2,"1"]], [])
    assert suffix([["ADD",1,2,"-3/2",4], ["CLEAR",2,4]], 0, 2, 2) == (
        [], [[1,"-3/2"]])
    assert pullback([["INIT",2,4], ["COPY",2,0,"-1/2",4],
                     ["ADD",2,1,"3/4",4]], 3, 2, 0) == Q(-1,2)
    return ["cancellation", "pre-COPY guard", "signed public response", "reverse prefix coefficient"]


def census(word):
    tape = word["program"]
    public = word["public"]
    owned = word["owned_fields"]
    assert (public, owned, len(tape)) == (1501, 68, EVENTS)
    frames = word["frames"]
    active = word["initial"] + [None] * owned
    anchors = {}
    for clock, (op, dst, *args) in enumerate(tape):
        if op == "MOVE":
            before, after, is_owned = args
            assert active[dst] == before and is_owned == (dst >= public)
            rank = abs(len(frames[before]) - len(frames[after]))
            assert rank
            active[dst] = after
            if is_owned:
                anchors[clock] = (dst, before, after, rank)
        elif op == "INIT":
            assert dst >= public and active[dst] is None
            active[dst] = args[0]
        elif op == "CLEAR":
            assert dst >= public and active[dst] == args[0]
            active[dst] = None
        else:
            assert op in ("ADD", "COPY", "SCALE")
            assert active[dst] == args[-1]
            if op != "SCALE":
                assert active[args[0]] == args[-1] and dst != args[0]
            if op == "COPY":
                assert dst >= public
    assert active == word["final"] + [None] * owned
    assert len(anchors) == CASES
    return anchors


def main():
    assert __debug__
    cli = ArgumentParser(description=__doc__)
    cli.add_argument("--root", type=Path, default=ROOT)
    cli.add_argument("--price-sha")
    cli.add_argument("--controls-only", action="store_true")
    args = cli.parse_args()
    tests = controls()
    if args.controls_only:
        print(dumps(tests))
        return
    if not args.price_sha:
        cli.error("requires the frozen R139 price SHA-256")
    paths = {"inputs/R139-PRICE.json": args.price_sha} | PINS
    payloads = {p: authenticate(args.root, p, digest) for p, digest in paths.items()}
    predecessor = loads(payloads["inputs/R137-RESULT.json"], object_pairs_hook=unique)
    old_price = loads(payloads["inputs/R137-PRICE.json"], object_pairs_hook=unique)
    price = loads(payloads["inputs/R139-PRICE.json"], object_pairs_hook=unique)
    assert all(p["head"] == HEAD and p["caller"] == CALLER
               for p in (predecessor, old_price, price))
    assert price["case_cap"] == CASES and price["event_cap"] == EVENTS
    by_clock = {r["move_clock"]:r for r in predecessor["records"]}
    assert len(by_clock) == CASES and not predecessor["unvisited"]
    result = dict(head=HEAD, caller=CALLER, caps=dict(events=EVENTS,cases=CASES,seconds=SECONDS),
                  pins=paths, controls=tests, cases=[], unvisited=sorted(by_clock))

    def stop(*_):
        raise TimeoutError("25-second hard limit")

    signal(SIGALRM, stop)
    alarm(SECONDS)
    deadline = monotonic() + SECONDS - 1
    try:
        raw = decompress(payloads["inputs/7334-WORD.json.gz"])
        assert sha256(raw).hexdigest() == PAYLOAD
        word = loads(raw, object_pairs_hook=unique)
        anchors = census(word)
        result["copy_clocks"] = [clock for clock,event in enumerate(word["program"]) if event[0] == "COPY"]
        assert anchors.keys() == by_clock.keys()
        assert {str(clock):list(key) for clock,key in anchors.items()} == price["keys"]
        assert price["seconds_cap"] == SECONDS
        assert Counter(a[3] for a in anchors.values()) == {
            int(k):v for k,v in old_price["stock"].items()}
        for clock, (role, before, after, rank) in sorted(anchors.items()):
            if monotonic() >= deadline:
                raise TimeoutError("before next case")
            old = by_clock[clock]
            assert (role,before,after,rank) == (
                old["role"],old["chart_from"],old["chart_to"],old["rank"])
            assert old["row"]
            coordinate = min(map(int,old["row"]))
            value = pullback(word["program"], clock, role, coordinate)
            assert value and value == Q(old["row"][str(coordinate)])
            guards, outputs = suffix(word["program"], clock + 1, role, word["public"])
            first = None
            if outputs:
                target, response = outputs[0]
                assert pullback(word["program"], EVENTS, target, role, clock + 1) == Q(response)
                first = [target,response]
            result["cases"].append(dict(move_clock=clock,role=role,before=before,after=after,rank=rank,
                moved_witness=[coordinate,str(value)], copy_guards=guards, final_public=outputs,
                reverse_first_public=first,
                decision=("excluded" if guards or outputs else "support survivor")))
            result["unvisited"].remove(clock)
    except TimeoutError as error:
        result["stopped"] = str(error)
    finally:
        alarm(0)
    result["counts"] = dict(Counter(r["decision"] for r in result["cases"]))
    print(dumps(result, indent=2, sort_keys=True))
    if result["unvisited"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()

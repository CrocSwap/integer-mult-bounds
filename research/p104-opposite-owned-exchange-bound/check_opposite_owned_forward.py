"""Verify both fixed-direction owned MOVE obstructions by literal forward replay."""
import argparse
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import perf_counter

PINS = {
    "7481-WORD.json.gz": "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9",
    "7481-APPLICATION.json": "1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799",
    "7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
}
NATIVE = "64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
LEFT, RIGHT = 549, 559
START = 40536
LEFT_BANK = (111, 121, 173, 235, 752, 881, 891, 937, 999, 1501, 1522, 1549)
RIGHT_BANK = (1527,)
INGRESS = {40536: (613, 558), 40546: (611, 556), 40548: (1279, 560)}
DIRECTIONS = {"L_TO_R": (173, 40557), "R_TO_L": (613, 40539)}
CAP_SECONDS = 30


def emit(**record):
    print(dumps(record, sort_keys=True, default=str), flush=True)


def frame_span(vectors):
    span = {0}
    for x in vectors:
        span |= {x ^ y for y in span}
    return span


def check_word(word):
    tape = word["program"]
    assert len(tape) == 76475 and len(word["initial"]) == word["public"] == 1501
    span_l, span_r = (frame_span(word["frames"][c]) for c in (LEFT, RIGHT))
    assert span_l < span_r and len(span_r) == 2 * len(span_l)
    assert tape[39573] == ["INIT", 1527, RIGHT]
    assert tape[39928] == ["ADD", 1549, 937, "-1", LEFT]
    assert tape[40537:40540] == [
        ["ADD", 1527, 613, "1", RIGHT],
        ["MOVE", 1549, LEFT, RIGHT, True],
        ["ADD", 613, 1549, "1", RIGHT],
    ]
    assert tape[40550:40560] == [
        ["ADD", 611, 1279, "2/3", RIGHT],
        ["ADD", 1279, 611, "-1", RIGHT],
        ["ADD", 1279, 1549, "1/2", RIGHT],
        ["CLEAR", 1549, RIGHT],
        ["SCALE", 1279, "1/2", RIGHT],
        ["ADD", 1527, 611, "1", RIGHT],
        ["MOVE", 1527, RIGHT, LEFT, True],
        ["ADD", 173, 1527, "1", LEFT],
        ["CLEAR", 1527, LEFT],
        ["ADD", 1522, 173, "1", LEFT],
    ]
    exact_ingress = {}
    cross_moves = []
    for clock in range(START, 40560):
        op, role, *args = tape[clock]
        if op != "MOVE":
            continue
        src, dest, owned = args
        if src in (LEFT, RIGHT) and dest in (LEFT, RIGHT):
            cross_moves.append((clock, role, src, dest, owned))
        elif src in (LEFT, RIGHT) or dest in (LEFT, RIGHT):
            assert src not in (LEFT, RIGHT) and dest == RIGHT and not owned
            exact_ingress[clock] = (role, src)
    assert exact_ingress == INGRESS
    assert cross_moves == [(40538, 1549, LEFT, RIGHT, True), (40556, 1527, RIGHT, LEFT, True)]


def replay(word, probe, omit=None):
    public = word["public"]
    active = dict(enumerate(word["initial"]))
    owner_birth = {}
    value = probe.copy()
    init_checks = copy_checks = 0
    external = {}
    observations = {}
    watch = {40537: (613,), 40540: (613,), 40553: (1279,),
             40555: (611, 1279), 40558: (173,), 40560: (1522,)}
    for clock, (op, role, *args) in enumerate(word["program"][:40561]):
        if clock == START:
            assert tuple(sorted(r for r in active if active[r] == LEFT)) == LEFT_BANK
            assert tuple(sorted(r for r in active if active[r] == RIGHT)) == RIGHT_BANK
            assert owner_birth[1527] == 39573 and value.get(1527, 0) == 0
            assert owner_birth[1549] < 39928
            left = {r: value.get(r, 0) for r in LEFT_BANK}
            right = {r: value.get(r, 0) for r in RIGHT_BANK}
        if clock in INGRESS:
            arrival, source_chart = INGRESS[clock]
            assert role == arrival and op == "MOVE" and args == [source_chart, RIGHT, False]
            external[clock] = value.get(arrival, 0)
        if clock in watch:
            observations[clock] = {r: value.get(r, 0) for r in watch[clock]}
        if op == "MOVE":
            src, dest, owned = args
            assert active[role] == src and owned == (role in owner_birth) == (role >= public)
            active[role] = dest
        elif op == "INIT":
            assert role >= public and role not in active and role not in owner_birth and role not in value
            active[role] = args[0]
            owner_birth[role] = clock
            init_checks += 1
        elif op == "CLEAR":
            assert role in owner_birth and active.pop(role) == args[0]
            del owner_birth[role]
            value.pop(role, None)
        else:
            old = value.get(role, 0)
            if op == "SCALE":
                weight, chart = args
                assert active[role] == chart
                result = Q(weight) * old
            else:
                assert op in ("ADD", "COPY")
                donor, weight, chart = args
                assert active[role] == active[donor] == chart
                if op == "COPY":
                    assert old == 0
                    copy_checks += 1
                result = old if clock == omit else old + Q(weight) * value.get(donor, 0)
            if result:
                value[role] = result
            else:
                value.pop(role, None)
    assert 1549 not in owner_birth and 1527 not in owner_birth
    return left, right, external, observations, (init_checks, copy_checks)


def check_direction(word, record):
    name = record["retained_direction"]
    role, read = DIRECTIONS[name]
    witness = {int(i): Q(v) for i, v in record["probe"].items()}
    assert witness and len(witness) == len(record["probe"])
    assert all(0 <= i < word["public"] and v for i, v in witness.items())
    left, right, external, observers, guards = replay(word, witness)
    cl, cr, ce, co, cg = replay(word, witness, omit=read)
    assert (cl, cr, ce, cg) == (left, right, external, guards)
    u, c, l, d = left[1549], external[40536], external[40546], external[40548]
    assert observers[40537][613] == c
    assert observers[40540][613] == c + u
    assert observers[40555][611] == -Q(l, 3) - 2 * d
    assert observers[40555][1279] == Q(l, 6) - Q(d, 2) + Q(u, 4)
    assert observers[40558][173] == left[173] + c - Q(l, 3) - 2 * d
    assert observers[40560][1522] == left[1522] + observers[40558][173]
    if name == "L_TO_R":
        assert not any(left.values())
    else:
        assert not any(right.values()) and not any(external.values())
    actual = observers[read + 1][role]
    assert actual == Q(record["target_response"]) != 0
    assert co[read + 1][role] == 0
    return {
        "retained_direction": name, "target_role": role, "target_cut": read + 1,
        "probe": witness, "left": left, "right": right, "ingresses": external,
        "target_response": actual, "other_observers": observers, "omitted_ADD": read,
        "control_target_response": co[read + 1][role], "init_guards_each": guards[0],
        "copy_guards_each": guards[1],
    }


def main():
    assert __debug__
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_root", type=Path)
    parser.add_argument("lead_receipt", type=Path)
    parser.add_argument("lead_sha256")
    args = parser.parse_args()
    started = perf_counter()
    completed = []

    def on_cap(_signal, _frame):
        emit(status="INDEPENDENT_CAP", completed=completed,
             unresolved=[d for d in DIRECTIONS if d not in completed], seconds=perf_counter()-started)
        raise SystemExit(124)

    signal(SIGALRM, on_cap)
    alarm(CAP_SECONDS)
    raw = {name: (args.input_root / name).read_bytes() for name in PINS}
    assert {name: sha256(data).hexdigest() for name, data in raw.items()} == PINS
    canonical = decompress(raw["7481-WORD.json.gz"])
    assert sha256(canonical).hexdigest() == NATIVE
    app = loads(raw["7481-APPLICATION.json"])
    caller = loads(raw["7113-CALLER.json"])
    assert app["caller_head"] == CALLER and app["caller_sha256"] == PINS["7113-CALLER.json"]
    assert caller["stages"] == sum(event[0] == "J" for event in caller["events"]) == 17
    word = loads(canonical)
    check_word(word)

    raw_lead = args.lead_receipt.read_bytes()
    assert sha256(raw_lead).hexdigest() == args.lead_sha256
    lead = loads(raw_lead)
    records = lead["directions"]
    assert len(records) == len(DIRECTIONS)
    assert {r["retained_direction"] for r in records} == DIRECTIONS.keys()
    for record in records:
        evidence = check_direction(word, record)
        emit(status="EXACT_FIXED_DIRECTION_SEPARATOR", **evidence)
        completed.append(record["retained_direction"])
    emit(status="PASS_INDEPENDENT_OPPOSITE_OWNED_FIXED_DIRECTIONS", completed=completed, unresolved=[],
         case_count=2, runner_cap_seconds=CAP_SECONDS, lead_sha256=args.lead_sha256, input_pins=PINS,
         native_sha256=NATIVE, caller_head=CALLER, seconds=perf_counter()-started)
    alarm(0)


if __name__ == "__main__":
    main()

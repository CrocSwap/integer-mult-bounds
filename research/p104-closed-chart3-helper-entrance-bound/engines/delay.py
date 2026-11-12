"""Read the exact helper624/main130 fixed-route retiming window."""
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
import sys

PIN = "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
PRICE = "d360a9b6f336e35f168e7c41bc2c8f6330bb67bad711e44f9ade4a65a0b85bf7"
SRC, DST = 624, 130
CLOCK, FIRST_MOVE = 32943, 32945
TARGET = 117


def stop(*_):
    raise TimeoutError("10-second exact cap")


def commutes(e, source=SRC, dest=DST):
    op, r, *args = e
    if op == "ADD":
        # [E_dest,source,E_r,args[0]] vanishes iff neither cross-index matches.
        return r != source and args[0] != dest
    if op == "COPY":
        return {r, args[0]}.isdisjoint({source, dest})
    if op in ("SCALE", "INIT", "CLEAR"):
        return r not in (source, dest)
    assert op == "MOVE"
    return True


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(10)
    raw = Path(sys.argv[1]).read_bytes()
    assert sha256(raw).hexdigest() == PIN
    payload = decompress(raw)
    assert sha256(payload).hexdigest() == PAYLOAD
    price = Path(__file__).with_name("PRICE-BOUND.json").read_bytes()
    assert sha256(price).hexdigest() == PRICE
    quote = loads(price)["cases"]["9/5"]
    assert quote["paid_delta"] == {"5": -17}
    assert quote["target_delta"] == {"4": 17, "9": -17}
    w = loads(payload)
    tape = w["program"]
    assert len(tape) == 76466
    assert w["initial"][SRC] == 3 and w["final"][SRC] == 127
    assert len(w["frames"][TARGET]) == 5 and len(w["frames"][w["final"][SRC]]) == 9
    e = tape[CLOCK]
    assert e[0:3] == ["ADD", DST, SRC] and e[-1] == 3
    assert tape[FIRST_MOVE] == ["MOVE", SRC, 3, TARGET, False]
    main = set(w["live"]) | {r + 112 for r in w["live"]}
    main.update(w["hosted"]["X2"])
    main.update(w["hosted"]["Y2"])
    assert DST in main and SRC not in main

    # Read both complete transport paths, then find the first permissible cut.
    paths = {r: [(t, e[2], e[3]) for t, e in enumerate(tape) if e[:2] == ["MOVE", r]] for r in (SRC, DST)}
    chart = {r: w["initial"][r] for r in paths}
    for r, moves in paths.items():
        for t, low, high in moves:
            if t >= CLOCK:
                break
            assert chart[r] == low
            chart[r] = high
    assert chart == {SRC: 3, DST: 3}
    chart[SRC] = TARGET
    cuts = []
    first_blocker = None
    for t in range(CLOCK + 1, len(tape) + 1):
        if chart[SRC] == chart[DST] == TARGET:
            cuts.append(t)
            break
        if t == len(tape):
            break
        op = tape[t]
        if t == FIRST_MOVE:
            continue
        if op[0] == "MOVE" and op[1] in chart:
            _, r, low, high, _ = op
            assert chart[r] == low
            chart[r] = high
        if not commutes(op):
            first_blocker = [t, op]
            break

    assert commutes(["ADD", DST, 12, "1", 3])
    assert not commutes(["ADD", 12, DST, "1", 3])
    assert not commutes(["ADD", SRC, 12, "1", 3])
    alarm(0)
    print(dumps({
        "head": "aaeec8c0acf01e99a5f331ef363a698d9c084ace", "helper": SRC, "main": DST,
        "word_sha256": PIN, "payload_sha256": PAYLOAD, "price_sha256": PRICE,
        "old_add": [CLOCK, e], "first_move": [FIRST_MOVE, tape[FIRST_MOVE]],
        "literal_paths": paths, "reachable_cut": cuts, "first_blocker": first_blocker,
        "stop_charts": chart, "caps": {"word": 1, "events": len(tape), "seconds": 10},
        "status": "candidate gate only" if cuts else "no fixed-chronology candidate",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

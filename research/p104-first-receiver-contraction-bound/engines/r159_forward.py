"""Forward exact e930 impulse at the frozen chart-652 receiver."""
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
WORD = "inputs/CURRENT.json.gz"
PIN = "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
CUT, CHART, CARRIER, RECEIVER = 42651, 652, 930, 793


def timeout(*_):
    raise TimeoutError("20-second hard cap")


def main():
    assert __debug__
    signal(SIGALRM, timeout)
    alarm(20)
    raw = (ROOT / WORD).read_bytes()
    assert sha256(raw).hexdigest() == PIN
    payload = decompress(raw)
    assert sha256(payload).hexdigest() == "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
    w = loads(payload)
    tape, n = w["program"], w["public"]
    assert tape[CUT] == ["ADD", 793, 930, "1/2", 652]
    assert tape[42653] == ["MOVE", 793, 652, 653, False]
    chart = w["initial"][:] + [None] * w["owned_fields"]
    vals = [Q(r == CARRIER) for r in range(len(chart))]
    for op, r, *a in tape[:CUT]:
        if op == "MOVE":
            assert chart[r] == a[0] and a[2] == (r >= n)
            chart[r] = a[1]
        elif op in ("INIT", "CLEAR"):
            assert r >= n and chart[r] == (None if op == "INIT" else a[0])
            chart[r] = a[0] if op == "INIT" else None
            vals[r] = Q(0)
        elif op == "SCALE":
            assert chart[r] == a[-1]
            vals[r] *= Q(a[0])
        else:
            s, q, f = a
            assert op in ("ADD", "COPY") and chart[r] == chart[s] == f
            vals[r] = (vals[r] if op == "ADD" else Q(0)) + Q(q) * vals[s]
    assert chart[CARRIER] == chart[RECEIVER] == CHART
    bank = {i: str(vals[i]) for i,c in enumerate(chart) if c == CHART and i not in (CARRIER, RECEIVER)}
    target = vals[CARRIER] / 2
    assert vals[CARRIER] == -1 and vals[RECEIVER] == Q(1, 2) and target == -Q(1, 2)
    assert bank == {165:"0", 586:"0"} and vals[RECEIVER] + target == 0
    alarm(0)
    print(dumps(dict(pins={WORD:PIN},cut=CUT,chart=CHART,carrier=str(vals[CARRIER]),receiver=str(vals[RECEIVER]),
                     required=str(target),post_receiver="0",donors=bank,runner_seconds=20,scope=1),
                indent=2,sort_keys=True))


if __name__ == "__main__":
    main()

"""Bound a fixed two-MOVE fusion by relocating one outward ADD on exact #7481."""

from argparse import ArgumentParser
from bisect import bisect_left, bisect_right
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

HERE = Path(__file__).resolve().parent
CAP = 30
PINS = {
    "7003-slide_stops.py": "64a69bcd5689e17a081187a17ef2913adece970da653afa606b47cf130f1aa04",
    "7481-WORD.json.gz": "acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9",
    "7481-APPLICATION.json": "1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799",
    "pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}


def emit(record):
    print(dumps(record, sort_keys=True, default=str), flush=True)


def expired(_signal, _frame):
    emit({"status": "UNRESOLVED_TIMEOUT"})
    raise SystemExit(124)


def authenticate(path):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != PINS[path.name]:
        raise ValueError(f"Hash mismatch for {path.name}")
    return raw


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", required=True, type=Path)
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    signal(SIGALRM, expired)
    alarm(CAP)
    script = HERE / "7003-slide_stops.py"
    authenticate(script)
    inputs = args.input_root.resolve()
    packed_word = authenticate(inputs / "7481-WORD.json.gz")
    application = authenticate(inputs / "7481-APPLICATION.json")
    price_script = inputs / "pricing.py"
    authenticate(price_script)
    old = run_path(str(script))
    controls = old["controls"]()
    if args.preflight:
        emit({"status": "PREFLIGHT_PASSED", "inputs": sorted(PINS), "controls": controls})
        return

    word = loads(decompress(packed_word))
    tape = word["program"]
    frames = word["frames"]
    spaces = [old["span"](frame) for frame in frames]
    history, routes, charts = old["inventory"](word, spaces)
    lo, hi = map(Fraction, loads(application)["directed_crossing_bracket"])
    bound = run_path(str(price_script))["power_bounds"]
    tested = 0

    for role, route in enumerate(routes[:word["public"]]):
        for index, (first, second) in enumerate(zip(route, route[1:])):
            if first < 0 or tape[first][0] != "MOVE" or tape[second][0] != "MOVE":
                continue
            clocks = history[role]
            contacts = clocks[bisect_right(clocks, first):bisect_left(clocks, second)]
            if len(contacts) != 1:
                continue
            contact, = contacts
            event = tape[contact]
            if event[0] != "ADD" or event[2] != role:
                continue
            a, b, c = tape[first][2], tape[first][3], tape[second][3]
            r1, r2 = len(frames[b]) - len(frames[a]), len(frames[c]) - len(frames[b])
            assert r1 > 0 and r2 > 0 and spaces[a] < spaces[b] < spaces[c]
            lower = 17 * (bound(r1, hi)[0] + bound(r2, hi)[0] - bound(r1+r2, lo)[1])
            upper = 17 * (bound(r1, lo)[1] + bound(r2, lo)[1] - bound(r1+r2, hi)[0])
            left, right = old["scalar_interval"](contact, tape, history, {contact})
            next_move = route[index + 2] if index + 2 < len(route) else len(tape)
            row = [(contact, left, right)]
            earlier = old["placement"](role, row, (route[index - 1]+1, first), a, tape, routes, charts)
            later = old["placement"](role, row, (second+1, next_move), c, tape, routes, charts)
            tested += 1
            emit({"role": role, "moves": [first, second], "contact": contact,
                  "ranks": [r1, r2], "optimistic_raw": [lower, upper],
                  "earlier": earlier, "later": later})
            if lower > 0 and (earlier or later):
                emit({"status": "NEEDS_LITERAL_SPLICE_AND_INVOICE", "tested": tested})
                return
    emit({"status": "SCOPED_EXHAUSTION", "tested": tested})


if __name__ == "__main__":
    main()

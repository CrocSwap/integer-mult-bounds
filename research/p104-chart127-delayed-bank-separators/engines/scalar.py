"""Literal independent scalar replay of the two frozen chart-127 banks."""
from fractions import Fraction as F
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from sys import argv, implementation, version_info

HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
COMPRESSED = "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
PAYLOAD = "9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
CAP, CHART = 20, 127
CASES = {
    (40430, 40432, 46222): {
        "cut": 46224, "target": 1187, "source": 975, "source_coefficient": "-1",
        "first": 668, "middle": 650, "frame_ranks": [3, 7, 9],
        "entrant": 43, "entrant_first": 498, "observer_coefficient": "1/2",
        "bank_count": 298, "mutant_drop": 16,
    },
    (43091, 43093, 46566): {
        "cut": 46568, "target": 1043, "source": 935, "source_coefficient": "2",
        "first": 981, "middle": 181, "frame_ranks": [7, 8, 9],
        "entrant": 1031, "entrant_first": 129, "observer_coefficient": "-2",
        "bank_count": 417, "mutant_drop": 1,
    },
}


def unique(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs), "duplicate JSON key"
    return result


def span(vectors):
    result = {0}
    for value in vectors:
        assert value not in result
        result |= {value ^ x for x in result}
    return result


@cache
def scalar(value):
    return F(value)


def tape_check(word, certificate):
    key = certificate["key"]
    case = CASES[tuple(key)]
    cut = case["cut"]
    target, source = case["target"], case["source"]
    first, middle = case["first"], case["middle"]
    entrant = case["entrant"]
    drop = case["mutant_drop"]
    assert certificate["cut"] == cut and certificate["kind"] == "separator"
    public, owned = word["public"], word["owned_fields"]
    tape = word["program"]
    assert (public, owned, len(tape)) == (1501, 68, 76466)
    assert [tape[k] for k in key] == [
        ["MOVE", target, first, middle, False],
        ["ADD", target, source, case["source_coefficient"], middle],
        ["MOVE", target, middle, CHART, False],
    ]
    assert tape[cut-1] == ["MOVE", entrant, case["entrant_first"], CHART, False]
    assert tape[cut] == ["ADD", target, entrant, case["observer_coefficient"], CHART]
    touches = [i for i in range(key[0], cut) if target in
               tape[i][1:3 if tape[i][0] in ("ADD", "COPY") else 2]]
    assert touches == key
    frames = [word["frames"][i] for i in (first, middle, CHART)]
    assert list(map(len, frames)) == case["frame_ranks"]
    assert span(frames[0]) < span(frames[1]) < span(frames[2])

    raw_probe = certificate["input"]
    assert all(str(int(i)) == i and 0 <= int(i) < public for i in raw_probe)
    probe = {int(i): F(v) for i,v in raw_probe.items()}
    assert drop in probe and all(probe.values())
    zero = (F(0), F(0))
    charts = [*word["initial"], *([None] * owned)]
    values = [zero for _ in charts]
    for i, value in probe.items():
        values[i] = (value, F(0) if i == drop else value)
    for clock, (op, dest, *args) in enumerate(tape[:cut]):
        if clock == key[1]:
            assert charts[source] == charts[target] == middle
            at_source = values[source]
        if op == "MOVE":
            before, after, is_owned = args
            assert charts[dest] == before and is_owned == (dest >= public)
            charts[dest] = after
        elif op == "INIT":
            chart, = args
            assert dest >= public and charts[dest] is None and values[dest] == zero
            charts[dest] = chart
        elif op == "CLEAR":
            chart, = args
            assert dest >= public and charts[dest] == chart
            charts[dest], values[dest] = None, zero
        elif op == "SCALE":
            coefficient, chart = args
            assert charts[dest] == chart
            values[dest] = tuple(scalar(coefficient)*x for x in values[dest])
        else:
            src, coefficient, chart = args
            assert op in ("ADD", "COPY") and dest != src and charts[dest] == charts[src] == chart
            assert op != "COPY" or values[dest] == zero
            values[dest] = tuple(x+scalar(coefficient)*y for x,y in zip(values[dest],values[src],strict=True))
    bank = [i for i, chart in enumerate(charts) if chart == CHART and i != target]
    assert charts[target] == CHART and entrant in bank and len(bank) == case["bank_count"]
    assert at_source[0] == F(certificate["source_value"]) != 0
    assert all(values[i][0] == 0 for i in bank)
    assert at_source[1] == 0 or any(values[i][1] for i in bank)
    return {"key":key, "cut":cut, "chart":CHART, "chart_bank":bank, "kind":"separator",
            "source_value":str(at_source[0]),
            "donor_values":{str(i):str(values[i][0]) for i in bank},
            "mutant_drop_coordinate":drop, "mutant_source_value":str(at_source[1]),
            "mutant_donor_values":{str(i):str(values[i][1]) for i in bank}}


def stop(*_):
    raise TimeoutError("20-second single-cut independent replay cap")


def main(word_path, certificate_path):
    assert __debug__ and implementation.name == "cpython" and version_info[:2] == (3, 12)
    signal(SIGALRM, stop)
    alarm(CAP)
    blob = word_path.read_bytes()
    assert sha256(blob).hexdigest() == COMPRESSED
    payload = decompress(blob)
    assert sha256(payload).hexdigest() == PAYLOAD
    word = loads(payload, object_pairs_hook=unique)
    certificate_raw = certificate_path.read_bytes()
    result = tape_check(word, loads(certificate_raw, object_pairs_hook=unique))
    alarm(0)
    print(dumps({"head":HEAD, "caller":CALLER, "compressed_sha256":COMPRESSED,
                 "uncompressed_sha256":PAYLOAD, "certificate_sha256":sha256(certificate_raw).hexdigest(),
                 "case_cap":1, "runner_cap_seconds":CAP, **result}, indent=2, sort_keys=True))


if __name__ == "__main__":
    assert len(argv) == 3
    main(Path(argv[1]), Path(argv[2]))

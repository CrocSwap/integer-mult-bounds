"""Independently check one chart-922 delayed correction against the literal word."""
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
KEY = [41944, 41946, 43419]
CUT = 43421
TARGET, SOURCE, CHART = 185, 82, 922
CAP = 20


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


def input_map(data, size):
    assert all(str(int(k)) == k and 0 <= int(k) < size for k in data)
    result = {int(k): F(v) for k, v in data.items()}
    assert result and all(result.values())
    return result


def tape_check(word, probes):
    public, owned = word["public"], word["owned_fields"]
    tape = word["program"]
    assert (public, owned, len(tape)) == (1501, 68, 76466)
    assert [tape[k] for k in KEY] == [
        ["MOVE", TARGET, 401, 1062, False],
        ["ADD", TARGET, SOURCE, "-1/2", 1062],
        ["MOVE", TARGET, 1062, CHART, False],
    ]
    assert tape[CUT-1] == ["MOVE", 7, 743, CHART, False]
    assert tape[CUT] == ["ADD", TARGET, 7, "1", CHART]
    touches = [i for i in range(KEY[0], CUT) if TARGET in
               tape[i][1:3 if tape[i][0] in ("ADD", "COPY") else 2]]
    assert touches == KEY
    frames = [word["frames"][i] for i in (401, 1062, CHART)]
    assert list(map(len, frames)) == [2, 5, 7]
    assert span(frames[0]) < span(frames[1]) < span(frames[2])
    charts = [*word["initial"], *([None] * owned)]
    zero = (F(0),) * len(probes)
    values = [tuple(probe.get(i, F(0)) for probe in probes) for i in range(public+owned)]
    for clock, (op, dest, *args) in enumerate(tape[:CUT]):
        if clock == KEY[1]:
            assert charts[SOURCE] == charts[TARGET] == 1062
            at_source = values[SOURCE]
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
            values[dest] = tuple(x+scalar(coefficient)*y for x,y in zip(values[dest], values[src], strict=True))
    bank = [i for i, c in enumerate(charts) if c == CHART and i != TARGET]
    assert charts[TARGET] == CHART and len(bank) == 5 and 7 in bank
    return bank, at_source, [values[i] for i in bank]


def check(word, certificate):
    assert certificate["key"] == KEY and certificate["cut"] == CUT
    assert certificate["kind"] == "separator"
    probe = input_map(certificate["input"], word["public"])
    mutant = {i:v for i,v in probe.items() if i != 1}
    assert len(mutant) + 1 == len(probe)
    bank, source, values = tape_check(word, [probe, mutant])
    assert source[0] == F(certificate["source_value"]) != 0
    assert all(row[0] == 0 for row in values)
    assert source[1] == 0 or any(row[1] for row in values)
    return {"chart_bank": bank, "kind": "separator", "source_value": str(source[0]),
            "donor_values": {str(i):str(row[0]) for i,row in zip(bank,values,strict=True)},
            "mutant_drop_coordinate": 1, "mutant_source_value": str(source[1]),
            "mutant_donor_values": {str(i):str(row[1]) for i,row in zip(bank,values,strict=True)}}


def stop(*_):
    raise TimeoutError("20-second single-cut independent replay cap")


def main(word_path, certificate_path):
    assert __debug__ and implementation.name == "cpython" and version_info[:2] == (3,12)
    signal(SIGALRM, stop)
    alarm(CAP)
    blob = word_path.read_bytes()
    assert sha256(blob).hexdigest() == COMPRESSED
    raw = decompress(blob)
    assert sha256(raw).hexdigest() == PAYLOAD
    word = loads(raw, object_pairs_hook=unique)
    certificate_raw = certificate_path.read_bytes()
    result = check(word, loads(certificate_raw, object_pairs_hook=unique))
    alarm(0)
    print(dumps({"head":HEAD, "caller":CALLER, "key":KEY, "cut":CUT, "chart":CHART,
                 "compressed_sha256":COMPRESSED, "uncompressed_sha256":PAYLOAD,
                 "certificate_sha256":sha256(certificate_raw).hexdigest(), "case_cap":1,
                 "runner_cap_seconds":CAP, **result}, indent=2, sort_keys=True))


if __name__ == "__main__":
    assert len(argv) == 3, "pass the exact compressed native word and one certificate"
    main(Path(argv[1]), Path(argv[2]))

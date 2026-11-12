"""Verify one frozen stage-907 delayed bank using two scalar inputs."""
from fractions import Fraction as Q
from functools import cache
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from sys import argv, implementation, version_info

HEAD = 'aaeec8c0acf01e99a5f331ef363a698d9c084ace'
CALLER = '07a76c5e2738882c0cb322278e56f6cae3c9885d'
COMPRESSED = '4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a'
PAYLOAD = '9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac'
KEY = [41805, 41807, 43313]
CUT = 43315
CHART = 907
TARGET = 166
SOURCE = 100
DONORS = [226, 931, 978, 990]
CAP = 20
PROBE = {2: -4, 12: 4, 550: 1}
MUTANT = {2: -4, 12: 4}


def unique(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs), 'duplicate JSON key'
    return result


def digest(data):
    return sha256(data).hexdigest()


@cache
def scalar(value):
    return Q(value)


def literal(word):
    public, owned = word['public'], word['owned_fields']
    tape = word['program']
    assert (public, owned, len(tape)) == (1501, 68, 76466)
    assert tape[41805] == ['MOVE', TARGET, 327, 783, False]
    assert tape[41807] == ['ADD', TARGET, SOURCE, '-1/2', 783]
    assert tape[43313] == ['MOVE', TARGET, 783, CHART, False]
    assert tape[43314] == ['MOVE', 226, 719, CHART, False]
    assert tape[CUT] == ['ADD', TARGET, 226, '-1/2', CHART]
    for op, dest, *args in tape[41808:43313]:
        assert dest != TARGET and (op not in ('ADD', 'COPY') or args[0] != TARGET)
    assert [len(word['frames'][chart]) for chart in (327, 783, CHART)] == [2, 5, 7]

    charts = [*word['initial'], *([None] * owned)]
    values = [[Q(0), Q(0)] for _ in charts]
    for index, probe in enumerate((PROBE, MUTANT)):
        for role, value in probe.items():
            values[role][index] = Q(value)
    for clock, (op, dest, *args) in enumerate(tape[:CUT]):
        if clock == KEY[1]:
            assert charts[SOURCE] == charts[TARGET] == 783
            source_values = values[SOURCE].copy()
        if op == 'MOVE':
            before, after, is_owned = args
            assert charts[dest] == before and is_owned == (dest >= public)
            charts[dest] = after
        elif op == 'INIT':
            chart, = args
            assert dest >= public and charts[dest] is None and not any(values[dest])
            charts[dest] = chart
        elif op == 'CLEAR':
            chart, = args
            assert dest >= public and charts[dest] == chart
            charts[dest] = None
            values[dest] = [Q(0), Q(0)]
        elif op == 'SCALE':
            coefficient, chart = args
            assert charts[dest] == chart
            values[dest] = [scalar(coefficient) * value for value in values[dest]]
        else:
            src, coefficient, chart = args
            assert op in ('ADD', 'COPY') and dest != src and charts[dest] == charts[src] == chart
            if op == 'COPY':
                assert not any(values[dest])
            values[dest] = [x + scalar(coefficient) * y for x, y in zip(values[dest], values[src], strict=True)]
    bank = [role for role, chart in enumerate(charts) if chart == CHART]
    assert bank == [TARGET, *DONORS] and all(role < public for role in bank)
    assert source_values == [4, 4]
    assert [values[role][0] for role in DONORS] == [0, 0, 0, 0]
    assert [values[role][1] for role in DONORS] == [0, 0, 0, -4]
    return {
        'source_values': list(map(str, source_values)),
        'chart_bank': [[role, charts[role]] for role in bank],
        'donor_values': {str(role): list(map(str, values[role])) for role in DONORS},
        'entrant': tape[43314], 'observer': tape[CUT],
    }


def stop(*_):
    raise TimeoutError('20-second single-cut scalar replay cap')


def main(path):
    assert __debug__ and implementation.name == 'cpython' and version_info[:2] == (3, 12)
    signal(SIGALRM, stop)
    alarm(CAP)
    raw = path.read_bytes()
    assert digest(raw) == COMPRESSED
    data = decompress(raw)
    assert digest(data) == PAYLOAD
    word = loads(data, object_pairs_hook=unique)
    result = literal(word)
    alarm(0)
    print(dumps({'head': HEAD, 'caller': CALLER, 'input_path': 'inputs/7334-WORD.json.gz',
                 'compressed_sha256': COMPRESSED, 'uncompressed_sha256': PAYLOAD,
                 'key': KEY, 'cut': CUT, 'chart': CHART, 'target': TARGET, 'source': SOURCE,
                 'probe': PROBE, 'mutant': MUTANT, 'case_cap': 1, 'runner_cap_seconds': CAP,
                 **result}, indent=2, sort_keys=True))


if __name__ == '__main__':
    assert len(argv) == 2, 'pass the exact compressed native word'
    main(Path(argv[1]))

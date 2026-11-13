"""Forward check of the two old-return probes at the exact #7481 chart-836 cut."""
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from sys import exit

ROOT = Path(__file__).resolve().parent
WORD_PIN = 'acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9'
PAYLOAD_PIN = '64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8'
EARLY, CUT, CHART = 32947, 43805, 836
BYPASS, DONOR = 627, 360
FIXED = (406, 1168, 1289, 1430)


def timeout(signum, frame):
    print(dumps({'status': 'unresolved_timeout', 'cases_completed': 0, 'runner_cap_seconds': 30}))
    exit(124)


def unique(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs), 'duplicate JSON key'
    return result


def evaluate(word, assignment):
    public = word['public']
    values = [assignment.get(j, Q(0)) for j in range(public)] + [None] * word['owned_fields']
    charts = word['initial'] + [None] * word['owned_fields']
    early = None
    for clock, (op, dst, *args) in enumerate(word['program'][:CUT]):
        if clock == EARLY:
            assert charts[BYPASS] == 3
            early = values[BYPASS]
        if op == 'INIT':
            assert values[dst] is None and charts[dst] is None
            charts[dst], values[dst] = args[0], Q(0)
        elif op == 'CLEAR':
            assert charts[dst] == args[0]
            charts[dst], values[dst] = None, None
        elif op == 'MOVE':
            assert charts[dst] == args[0] and args[2] == (dst >= public)
            charts[dst] = args[1]
        elif op == 'SCALE':
            assert charts[dst] == args[1]
            values[dst] *= Q(args[0])
        else:
            src, coefficient, chart = args
            assert op in ('ADD', 'COPY') and charts[dst] == charts[src] == chart
            if op == 'COPY':
                assert values[dst] == 0
            values[dst] += Q(coefficient) * values[src]
    assert charts[BYPASS] == charts[DONOR] == CHART
    assert tuple(j for j, c in enumerate(charts) if c == CHART and j not in (DONOR, BYPASS)) == FIXED
    assert early is not None
    return {j: values[j] for j in FIXED}, early, [values[DONOR], values[BYPASS]]


def main():
    assert __debug__
    signal(SIGALRM, timeout)
    alarm(30)
    compressed = (ROOT / '7481-WORD.json.gz').read_bytes()
    assert sha256(compressed).hexdigest() == WORD_PIN
    payload = decompress(compressed)
    assert sha256(payload).hexdigest() == PAYLOAD_PIN
    word = loads(payload)
    tape = word['program']
    assert tape[EARLY] == ['MOVE', BYPASS, 3, 117, False]
    assert tape[42212] == ['MOVE', DONOR, 417, CHART, False]
    assert tape[42213] == ['MOVE', 406, 471, CHART, False]
    assert tape[CUT - 1:CUT + 1] == [['MOVE', BYPASS, 117, CHART, False],
                                   ['ADD', BYPASS, DONOR, '1', CHART]]
    source = loads((ROOT / 'PROBES.json').read_bytes(), object_pairs_hook=unique)
    assert len(source) == 2
    controls = []
    for item in source:
        probe = {int(j): Q(value) for j, value in item['probe'].items()}
        assert probe and len(probe) == len(item['probe'])
        assert all(0 <= j < word['public'] for j in probe)
        bank, early, targets = evaluate(word, probe)
        assert not any(bank.values()) and early == 0
        assert targets == list(map(Q, item['required_values']))
        controls.append({'probe': probe, 'fixed_bank': bank, 'bypassed_early_627': early,
                         'required_old_outputs': targets})
    (a, b), (c, d) = (item['required_old_outputs'] for item in controls)
    determinant = a * d - b * c
    assert determinant
    zero_bank, zero_early, zero = evaluate(word, {})
    assert not any(zero_bank.values()) and not zero_early and not any(zero)
    alarm(0)
    print(dumps({'status': 'PASS_INDEPENDENT_CHART836_QUOTIENT', 'cases_completed': 1,
                 'case_cap': 1, 'runner_cap_seconds': 30, 'cut': CUT, 'chart': CHART,
                 'fixed_bank': FIXED, 'early_bypass_clock': EARLY, 'target_roles': [DONOR, BYPASS],
                 'compressed_sha256': WORD_PIN, 'payload_sha256': PAYLOAD_PIN,
                 'witnesses': controls, 'target_determinant': determinant, 'zero_control': zero},
                indent=2, sort_keys=True, default=str))


if __name__ == '__main__':
    main()

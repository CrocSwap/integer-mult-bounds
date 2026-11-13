"""Forward signed replay of two exact probes for one #7481 retimed transfer."""
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
CUT, CHART, RETIMED, OWNED = 39884, 529, 992, 1532
BANK = (146, 162, 228, 440, 744, 913, 927, 1197, 1358, 1444, 1451, 1494)
PROBES = ({3: Q(-2), 22: Q(-1), 32: Q(-1)}, {0: Q(1, 2), 146: Q(-1, 2)})


def timeout(signum, frame):
    print(dumps({'status': 'unresolved_timeout', 'cases_completed': 0, 'runner_cap_seconds': 30}))
    exit(124)


def evaluate(word, assignment):
    public = word['public']
    values = [assignment.get(index, Q(0)) for index in range(public)] + [None] * word['owned_fields']
    charts = word['initial'] + [None] * word['owned_fields']
    snapshot, old_owned = None, None
    for clock, (op, role, *args) in enumerate(word['program'][:CUT + 3]):
        if clock == CUT:
            assert charts[RETIMED] == CHART and charts[OWNED] == 520
            snapshot = {index: values[index] for index, frame in enumerate(charts)
                        if frame == CHART and index != RETIMED}
            old_owned = values[OWNED]
        if op == 'INIT':
            assert values[role] is None and charts[role] is None
            values[role] = Q(0)
            charts[role] = args[0]
        elif op == 'CLEAR':
            assert charts[role] == args[0]
            values[role] = None
            charts[role] = None
        elif op == 'MOVE':
            assert charts[role] == args[0] and args[2] == (role >= public)
            charts[role] = args[1]
        elif op == 'SCALE':
            assert charts[role] == args[1]
            values[role] *= Q(args[0])
        else:
            source, scale, frame = args
            assert op in ('ADD', 'COPY') and charts[role] == charts[source] == frame
            if op == 'COPY':
                assert values[role] == 0
            values[role] += Q(scale) * values[source]
    assert snapshot is not None and tuple(snapshot) == BANK
    assert values[913] == snapshot[913] - old_owned / 2
    return snapshot, (values[RETIMED], values[913]), old_owned


def main():
    assert __debug__
    signal(SIGALRM, timeout)
    alarm(30)
    raw = (ROOT / '7481-WORD.json.gz').read_bytes()
    assert sha256(raw).hexdigest() == WORD_PIN
    payload = decompress(raw)
    assert sha256(payload).hexdigest() == PAYLOAD_PIN
    word = loads(payload)
    tape = word['program']
    assert tape[CUT:CUT + 4] == [['MOVE', OWNED, 520, CHART, True],
                                  ['SCALE', OWNED, '-1/2', CHART],
                                  ['ADD', 913, OWNED, '1', CHART], ['CLEAR', OWNED, CHART]]
    assert tape[39818] == ['MOVE', RETIMED, 520, CHART, False]
    assert tape[39876] == ['ADD', OWNED, 497, '4', 520]
    assert tape[39877] == ['MOVE', 1451, 737, CHART, False]
    arrivals = [clock for clock, event in enumerate(tape[CUT + 4:], CUT + 4)
                if event[0] == 'MOVE' and event[3] == CHART]
    assert not arrivals
    target_matrix = []
    controls = []
    for probe in PROBES:
        bank, target, transfer = evaluate(word, probe)
        assert not any(bank.values())
        target_matrix.append(target)
        controls.append({'input': probe, 'bank': bank, 'old_transfer': transfer, 'targets': target})
    assert target_matrix == [(Q(1), Q(2)), (Q(0), Q(1))]
    determinant = target_matrix[0][0] * target_matrix[1][1] - target_matrix[0][1] * target_matrix[1][0]
    assert determinant == 1
    zero_bank, zero_targets, zero_transfer = evaluate(word, {})
    assert not any(zero_bank.values()) and not any(zero_targets) and zero_transfer == 0
    alarm(0)
    print(dumps({'status': 'PASS_INDEPENDENT_RETIMED_992_TWO_PROBES', 'case_cap': 1,
                 'cases_completed': 1, 'runner_cap_seconds': 30, 'chart': CHART, 'cut': CUT,
                 'target_roles': [RETIMED, 913], 'receiver_roles': list(BANK),
                 'source_word_sha256': WORD_PIN, 'source_payload_sha256': PAYLOAD_PIN,
                 'target_determinant': determinant, 'witnesses': controls,
                 'zero_control': zero_targets, 'later_old_arrivals': arrivals},
                indent=2, sort_keys=True, default=str))


if __name__ == '__main__':
    main()

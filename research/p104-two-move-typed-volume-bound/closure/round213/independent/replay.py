"""Independent one-pair width-four monomial-erasure displacement bound."""
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from sys import argv, implementation, version_info

CAP = 30
WIDTH = 4
PRIOR_RUNNER = 'bdf2519d81b02f9c627906850f7c509dafbb25cfa5149b5a52b8baeffdc1c87b'


def counts(bits):
    residue = [1, 0, 0, 0]
    for _ in range(bits):
        residue = [residue[i] + residue[(i-1) % 4] for i in range(4)]
    assert sum(residue) == 1 << bits
    return residue


def stop(*_):
    raise TimeoutError('R213 independent 30-second cap')


def main():
    assert __debug__ and implementation.name == 'cpython' and version_info[:2] == (3, 12)
    assert len(argv) == 3, 'pass R212 independent replay.py and exact source input root'
    prior, root = [Path(s).resolve() for s in argv[1:]]
    signal(SIGALRM, stop)
    alarm(CAP)
    assert sha256(prior.read_bytes()).hexdigest() == PRIOR_RUNNER
    old = run_path(str(prior))
    raw = {}
    for name, digest in old['PINS'].items():
        raw[name] = (root / name).read_bytes()
        assert sha256(raw[name]).hexdigest() == digest, name
    body = decompress(raw['WORD.json.gz'])
    assert sha256(body).hexdigest() == old['WORD']
    word = loads(body, object_pairs_hook=old['no_duplicates'])
    clocks, roles = [32944, 32945], [625, 624]
    start, end = 3, 117
    for clock, role in zip(clocks, roles, strict=True):
        assert word['program'][clock] == ['MOVE', role, start, end, False]
    src, dest = [tuple(word['frames'][chart]) for chart in (start, end)]
    assert src == () and dest == (8, 17, 34, 68, 391)
    verifier = run_path(str(root / 'native_verify.py'))
    frame = verifier['adjoint'](verifier['frame'](src, 9)) + verifier['frame'](dest, 9)
    assert frame[2:7] == verifier['fourier'](5) and frame[:2] == verifier['adjoint'](frame[7:])
    nonzero = 0
    max_square = Q(0)
    column = old['column']
    for j in range(512):
        state, denominator_power = column(frame, j)
        assert len(state) == 32
        magnitudes = {Q(a*a+b*b, 4**denominator_power) for a, b in state.values()}
        assert magnitudes == {Q(1, 32)}
        max_square = max(max_square, max(magnitudes))
        nonzero += len(state)
    assert nonzero == 512*32
    target_entry_cap = max_square ** (WIDTH//2)
    assert target_entry_cap == Q(1, 1024)
    N = 1 << (9*WIDTH)
    # On a 2N-dimensional unitary, m fixed eigenvectors give Re(trace) >=
    # 2m-2N. The monomial matching can select at most 2N target entries.
    trace_upper = 2 * N * target_entry_cap
    fixed_upper = N + trace_upper/2
    target_rank_lower = 2*N - fixed_upper
    assert target_rank_lower == Q(1023, 1024)*N
    core_rows = []
    core_max = Q(0)
    for rank in range(1, 7):
        bits = rank * WIDTH
        residue = counts(bits)
        fixed_fraction = Q(residue[0], 1 << bits)
        assert fixed_fraction == Q(1, 4) + Q((-1)**rank, 1 << (2*rank+1))
        assert fixed_fraction >= Q(1, 8)
        movement = (1-fixed_fraction) * N
        core_rows.append({'rank': rank, 'phase_counts': residue, 'fixed_fraction': str(fixed_fraction), 'displacement': str(movement)})
        core_max = max(core_max, movement)
    assert core_max == Q(7, 8)*N
    assert target_rank_lower - core_max == Q(127, 1024)*N > 0
    alarm(0)
    print(dumps({'head': old['HEAD'], 'caller': old['CALLER'], 'pins': old['PINS'], 'word_sha256': old['WORD'],
                 'r212_runner_sha256': PRIOR_RUNNER, 'clocks': clocks, 'roles': roles, 'source': start, 'target': end,
                 'f': WIDTH, 'ambient_dimension': N, 'columns': 512, 'nonzero_one_slice_entries': nonzero,
                 'one_slice_max_squared_magnitude': str(max_square), 'target_entry_cap': str(target_entry_cap),
                 'relative_trace_upper': str(trace_upper), 'relative_fixed_dimension_upper': str(fixed_upper),
                 'target_displacement_lower': str(target_rank_lower), 'core_cases': core_rows,
                 'core_displacement_upper': str(core_max), 'strict_dimension_gap': str(target_rank_lower-core_max),
                 'runner_cap_seconds': CAP}, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()

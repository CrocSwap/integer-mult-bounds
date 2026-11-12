"""Independently replay exact Gaussian columns for the single R212 pair."""
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from sys import argv, implementation, version_info

PINS = {
    'WORD.json.gz': '4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a',
    'clifford_exact.py': '2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962',
    'native_verify.py': '3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38',
}
WORD = '9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac'
HEAD = 'aaeec8c0acf01e99a5f331ef363a698d9c084ace'
CALLER = '07a76c5e2738882c0cb322278e56f6cae3c9885d'
CAP = 30


def no_duplicates(items):
    out = dict(items)
    assert len(out) == len(items)
    return out


def parity(x):
    return x.bit_count() % 2


def gaussian_multiply(u, v):
    a, b = u
    c, d = v
    return a*c-b*d, a*d+b*c


def add(out, address, value):
    a, b = out.get(address, (0, 0))
    c, d = value
    if a+c or b+d:
        out[address] = a+c, b+d
    else:
        out.pop(address, None)


def column(circuit, basis):
    state, den = {basis: (1, 0)}, 0
    phases = ((1, 0), (0, 1), (-1, 0), (0, -1))
    for gate in circuit:
        tag, *args = gate
        out = {}
        for label, value in state.items():
            if tag == 'C':
                direction, sign = args
                add(out, label, gaussian_multiply(value, (1, sign)))
                add(out, label ^ direction, gaussian_multiply(value, (1, -sign)))
            elif tag == 'P':
                matrix, = args
                addr = sum(parity(label & row) << i for i, row in enumerate(matrix))
                assert addr not in out
                out[addr] = value
            elif tag == 'X':
                mask, = args
                out[label ^ mask] = value
            elif tag == 'D':
                matrix, linear = args
                hits = [i for i in range(9) if label >> i & 1]
                exponent = sum(linear[i] for i in hits)
                exponent += 2 * sum(1 for i in hits for j in hits if j > i and matrix[i] >> j & 1)
                out[label] = gaussian_multiply(value, phases[exponent % 4])
            else:
                assert tag == 'phase'
                out[label] = gaussian_multiply(value, phases[args[0] % 4])
        state = out
        den += tag == 'C'
    while den and all(not ((a | b) & 1) for a, b in state.values()):
        state = {i: (a//2, b//2) for i, (a, b) in state.items()}
        den -= 1
    return state, den


def stop(*_):
    raise TimeoutError('R212 independent 30-second cap')


def main():
    assert __debug__ and implementation.name == 'cpython' and version_info[:2] == (3, 12)
    assert len(argv) == 2, 'pass the pinned exact input directory'
    root = Path(argv[1]).resolve()
    signal(SIGALRM, stop)
    alarm(CAP)
    raw = {}
    for name, digest in PINS.items():
        raw[name] = (root / name).read_bytes()
        assert sha256(raw[name]).hexdigest() == digest, name
    body = decompress(raw['WORD.json.gz'])
    assert sha256(body).hexdigest() == WORD
    word = loads(body, object_pairs_hook=no_duplicates)
    clocks = [32944, 32945]
    roles = [625, 624]
    old, new = 3, 117
    assert len(word['program']) == 76466 and word['public'] == 1501
    for t, r in zip(clocks, roles, strict=True):
        assert word['program'][t] == ['MOVE', r, old, new, False]
    source, target = [tuple(word['frames'][i]) for i in (old, new)]
    assert source == () and target == (8, 17, 34, 68, 391)
    compiler = run_path(str(root / 'clifford_exact.py'))
    verifier = run_path(str(root / 'native_verify.py'))
    op = compiler['canonical_frame'](9, source).adjoint().then(compiler['canonical_frame'](9, target))
    recipe, compiled = compiler['lower_child'](op)
    literal = verifier['adjoint'](verifier['frame'](source, 9)) + verifier['frame'](target, 9)
    assert recipe['rank'] == 5
    assert tuple(compiled.circuit) == verifier['recipe'](recipe)
    assert literal[2:7] == verifier['fourier'](5)
    assert literal[:2] == verifier['adjoint'](literal[7:]) and len(literal) == 9
    for j in range(512):
        assert column(compiled.circuit, j) == column(literal, j)
    # An off-diagonal coordinate of V² is an exact non-scalar witness.
    squares = column(literal + literal, 0)
    off = next((i, value) for i, value in sorted(squares[0].items()) if i != 0)
    assert column(literal + verifier['adjoint'](literal), 0) == ({0: (1, 0)}, 0)
    broken = literal[:2] + literal[3:]
    assert column(broken, 0) != column(literal, 0)
    # One C axis contributes independent phases 1 and i. For five axes
    # the residue distribution is exact, and each further convolution
    # with the next bit's (1/2,1/2) cannot raise its largest entry.
    counts = [1, 0, 0, 0]
    for _ in range(5):
        counts = [counts[i] + counts[(i-1) % 4] for i in range(4)]
    assert counts == [6, 6, 10, 10]
    assert 2*(sum(counts)-max(counts)) > sum(counts)
    alarm(0)
    print(dumps({'head': HEAD, 'caller': CALLER, 'pins': PINS, 'word_sha256': WORD,
                 'clocks': clocks, 'roles': roles, 'source': old, 'target': new,
                 'ambient_axes': 9, 'paid_rank': recipe['rank'], 'target_frame': target,
                 'signed_one_slice_columns_verified': 512, 'square_column_zero': squares,
                 'square_offdiagonal_witness': [off[0], 0, *off[1], squares[1]],
                 'projective_order': 4, 'initial_residue_counts': counts,
                 'maximum_eigenspace_fraction_all_f_ge_1': '5/16',
                 'required_two_lane_ambient_fraction_all_f_ge_1': '11/8',
                 'dropped_C_gate_rejected': True, 'runner_cap_seconds': CAP}, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()

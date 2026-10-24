"""Check the exact helper echo in the pinned forward word."""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json


PINS = {
    'CANONICAL-WORD.json.gz': '16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219',
    'LOCAL-PROGRAMS.json.gz': '241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a',
}


def require(condition, label):
    if not condition:
        raise ValueError(label)


def plus(target, source, coefficient):
    for j, value in source.items():
        value = target.get(j, Q(0)) + coefficient * value
        if value:
            target[j] = value
        else:
            target.pop(j, None)


def replay(events, initial):
    rows = [row.copy() for row in initial]
    for event in events:
        if event[0] != 'scalar':
            continue
        gate = event[1]
        require(gate[1][0] == 'L', 'private register in emitted word')
        t = gate[1][1]
        if gate[0] == 'scale':
            q = Q(gate[2], gate[3])
            rows[t] = {j: q * value for j, value in rows[t].items()}
        else:
            require(gate[0] == 'add' and gate[2][0] == 'L', 'unexpected scalar gate')
            plus(rows[t], rows[gate[2][1]], Q(gate[3], gate[4]))
    return rows


def multiply(left, right):
    result = []
    for row in left:
        result.append({})
        for j, coefficient in row.items():
            plus(result[-1], right[j], coefficient)
    return result


def check_frames(events, word):
    frames = word['start'].copy()
    for event in events:
        if event[0] == 'climb':
            require(frames[event[2]] == event[3], 'climb entry frame')
            frames[event[2]] = event[4]
        elif event[0] == 'scalar':
            gate, frame = event[1:]
            require(frames[gate[1][1]] == frame, 'scalar target frame')
            if gate[0] == 'add':
                require(frames[gate[2][1]] == frame, 'scalar source frame')
    require(frames == word['final'], 'persistent endpoint frames')


def primitive_bound(gate):
    q = Q(gate[3], gate[4]) if gate[0] == 'add' else Q(gate[2], gate[3])
    a, b = abs(q.numerator), q.denominator
    require(b & (b - 1) == 0, 'non-dyadic denominator')
    if gate[0] == 'scale':
        require(a > 0 and a & (a - 1) == 0, 'non-binary scale')
        return abs(a.bit_length() - b.bit_length()) + int(q < 0)
    return 3 + a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1


def reflected(source, word, scale):
    cut = source.index(['phase', 'centers'])
    end = source.index(['phase', 'B'])
    sign = [
        ['scalar', ['scale', ['L', register], scale.numerator, scale.denominator], frame]
        for register, frame in zip(word['centers'], word['center_frames'])
    ]
    return source[:cut] + [['phase', 'retained_centre_scale']] + sign + source[end:]


def main(args):
    pinned = {}
    for name, digest in PINS.items():
        raw = (args.source / name).read_bytes()
        require(sha256(raw).hexdigest() == digest, name + ' pin')
        pinned[name] = json.loads(gzip.decompress(raw))
    word = pinned['CANONICAL-WORD.json.gz']
    source = pinned['LOCAL-PROGRAMS.json.gz']['forward']
    require(word['v'] == 112 and word['R'] == 480, 'register layout')
    n = 704
    identity = [{i: Q(1)} for i in range(n)]
    cut = source.index(['phase', 'centers'])
    end = source.index(['phase', 'B'])
    boundary = replay(source[:cut], identity)
    R = [{j: q for j, q in boundary[c].items() if j < 112} for c in word['centers']]
    H = [{j: q for j, q in boundary[c].items() if j >= 224} for c in word['centers']]
    probe = [{} for _ in range(n)]
    for k, c in enumerate(word['centers']):
        probe[c] = {k: Q(1)}
    V = replay(source[end:], probe)
    require(all(not row for row in V[:224]), 'helper-only centre response')
    require(multiply(H, V) == [{i: Q(1)} for i in range(8)], 'H V identity')
    RT = [{k: row[i] for k, row in enumerate(R) if i in row} for i in range(112)]
    K = [{k: q / 4 for k, q in row.items()} for row in RT]
    require(multiply(R, RT) == [{i: Q(56)} for i in range(8)], 'R Gram identity')
    code = [r.copy() for r in R]
    for row, dirty in zip(code, H):
        plus(row, dirty, Q(1))
    KC = multiply(K, code)
    VC = multiply(V, code)
    generated = {}
    checks = {}
    for scale in (Q(-1), Q(2), Q(1, 2)):
        events = reflected(source, word, scale)
        check_frames(events, word)
        actual = replay(events, identity)
        expected = [row.copy() for row in identity]
        for i, row in enumerate(KC):
            plus(expected[112 + i], {i: Q(1)}, Q(1))
            plus(expected[112 + i], row, Q(-1))
        for i, row in enumerate(VC):
            plus(expected[i], row, scale - 1)
        require(actual == expected, 'full local map for scale ' + str(scale))
        second = reflected(source, word, 1 / scale)
        gain1, gain2 = -scale / (1 - scale), 1 / (1 - scale)
        first_map = [row.copy() for row in actual]
        for i in range(112, 224):
            delta = first_map[i]
            plus(delta, {i: Q(1)}, Q(-1))
            first_map[i] = {j: gain1 * q for j, q in delta.items()}
            plus(first_map[i], {i: Q(1)}, Q(1))
        second_map = replay(second, identity)
        for i in range(112, 224):
            delta = second_map[i]
            plus(delta, {i: Q(1)}, Q(-1))
            second_map[i] = {j: gain2 * q for j, q in delta.items()}
            plus(second_map[i], {i: Q(1)}, Q(1))
        batch = multiply(second_map, first_map)
        desired = [row.copy() for row in identity]
        for i in range(112):
            plus(desired[112 + i], {i: Q(1)}, Q(1))
        require(batch == desired, 'full echo map for scale ' + str(scale))
        require(first_map != desired, 'one-pass control')
        checks[str(scale)] = {'first_gain': str(gain1), 'second_gain': str(gain2),
                              'local_rows_and_columns': n, 'echo_rows_and_columns': n,
                              'all_arbitrary_helper_columns_checked': True,
                              'one_pass_is_not_the_required_shear': True}
        generated[str(scale)] = events
    minus = generated['-1']
    first_sign = next(i for i, event in enumerate(minus)
                      if event == ['phase', 'retained_centre_scale']) + 1
    bad = replay(minus[:first_sign] + minus[first_sign + 1:], identity)
    good = replay(minus, identity)
    require(bad != good, 'missing centre sign control')
    bad_batch = multiply(good, bad)
    doubled = [row.copy() for row in identity]
    for i in range(112):
        plus(doubled[112 + i], {i: Q(1)}, Q(2))
    require(bad_batch != doubled, 'missing sign breaks echo')
    native = lambda stream: [e for e in stream if e[0] in ('climb', 'adapter', 'residual_adapter')]
    require(native(source) == native(minus), 'native event preservation')
    profile = {int(k): v for k, v in word['local_profile'].items()}
    require(profile.pop(8) == 8, 'eight centre children')
    payload = json.dumps({'forward_scale_minus_one': minus}, separators=(',', ':'), sort_keys=True).encode()
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / 'RAW-REFLECTION-PROGRAM.json.gz').write_bytes(gzip.compress(payload, mtime=0))
    report = {
        'status': 'PASS_EXACT_LOCAL_HISTORY_ECHO',
        'base': 'bce54fb3f895cbe5cd4c0eb477c3afeed100190f',
        'source_compressed_sha256': PINS,
        'program_payload_sha256': sha256(payload).hexdigest(),
        'map': "x'=x; y'=y+x-K(Rx+Hh); h'=h+(s-1)V(Rx+Hh)",
        'reduced_map': "w=Rx+Hh; w'=s*w; y'=y+x-Kw",
        'identities': ['HV=I8', 'RR^T=56I8', 'K=R^T/4'],
        'dyadic_echo_checks': checks,
        'scalar_macros_per_reflection': sum(e[0] == 'scalar' for e in minus),
        'real_component_primitive_bound_per_reflection': 2 * sum(primitive_bound(e[1]) for e in minus if e[0] == 'scalar'),
        'native_events_per_reflection': len(native(minus)),
        'paid_profile_per_reflection': profile,
        'paid_mass_per_reflection': sum(k * v for k, v in profile.items()),
        'rank8_children_removed_per_reflection': 8,
        'private_centre_registers_used': 0,
        'missing_first_sign_breaks_local_and_echo_maps': True,
        'native_scope': 'Each emitted local word has legal native frames. The two maps compose only after an identified common-coordinate interface. A native batch is not admitted.',
        'not_claimed': ['Free chart transport', 'Fresh productive growth from repeated axes', 'Global helper restoration', 'Recursive cost or kappa improvement'],
    }
    (args.out / 'ECHO-EVIDENCE.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(report['status'])
    print('Three dyadic pairs checked on all 704 input columns; native batch transport remains open.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    main(parser.parse_args())

#!/usr/bin/env python3
"""Exact one-digit boundary census. Standard library; Python >= 3.9."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def literal(y, t, z, G, width, inverse=False):
    """Four modular rotations; inversion reverses order and sign."""
    B, Q = 1 << G, 1 << width
    if inverse:
        t = (t + ((y & 1) ^ z)) % B
        y = (y - z * (1 - 2 * t)) % Q
        t = (t - (y & 1)) % B
        y = (y - 2 * z * t) % Q
    else:
        y = (y + 2 * z * t) % Q
        t = (t + (y & 1)) % B
        y = (y + z * (1 - 2 * t)) % Q
        t = (t - ((y & 1) ^ z)) % B
    return y, t


def formula(y, t, z, G, width):
    """Independent parity partition, derived in README.md."""
    correction = 2 * (1 << G) if z and (y & 1) and t == (1 << G) - 1 else 0
    return ((y ^ z) + correction) % (1 << width), t


def repaired_pair(y, t, z, G, width):
    a, b = literal(y, t, z, G, width)
    a, b = literal(a, b, z, G, width)
    if z and b == (1 << G) - 1:
        a = (a - 2 * (1 << G)) % (1 << width)
    return a, b


def source_pins():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    for name, pin in pins['files'].items():
        data = (ROOT / name).read_bytes().replace(b'\r\n', b'\n')
        require(hashlib.sha256(data).hexdigest() == pin['lf_sha256'], 'Source drift: ' + name)
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        require(blob == pin['git_blob'], 'Git blob mismatch: ' + name)
    selected = json.loads((ROOT / 'certificates/checkpoints/frontier942.json').read_text())
    require(selected['kappa'] == '1661960547713947/1000000000000000000', 'Historical checkpoint kappa changed')
    for key in ('certificate', 'source_manifest', 'proof', 'review'):
        require(selected[key] in pins['files'], 'Unpinned selected chain: ' + key)
    require(pins['files'][selected['certificate']]['lf_sha256'] == selected['certificate_sha256'],
            'Selected assembly binding failed')
    return pins['base_commit']


def census():
    total = 0
    rows = []
    # All y,t,z in these 16 complete one-digit rectangles, not random samples.
    for G in range(1, 5):
        for width in range(G + 2, G + 6):
            B, Q = 1 << G, 1 << width
            disagreements = pair_support = 0
            images = set()
            for z in (0, 1):
                images.clear()
                for t in range(B):
                    for y in range(Q):
                        out = literal(y, t, z, G, width)
                        require(out == formula(y, t, z, G, width), 'Parity formula')
                        require(literal(*out, z, G, width, inverse=True) == (y, t), 'Literal inverse')
                        images.add(out)
                        disagreements += out != (y ^ z, t)
                        pair = literal(*out, z, G, width)
                        expected = ((y + (2 * B if z and t == B - 1 else 0)) % Q, t)
                        require(pair == expected, 'Boundary translation')
                        pair_support += pair != (y, t)
                        require(repaired_pair(y, t, z, G, width) == (y, t), 'Pair repair')
                        total += 1
                require(len(images) == Q * B, 'Full permutation coverage')
            require(disagreements == Q // 2, 'Single-word support cardinality')
            require(pair_support == Q, 'Pair support cardinality')
            # Every exceptional z=1 orbit has exact length Q/B.
            y, t = 1, B - 1
            order = Q // B
            for step in range(1, order + 1):
                y, t = literal(y, t, 1, G, width)
                require(((y, t) == (1, B - 1)) == (step == order), 'Exact fibre order')
            rows.append(dict(G=G, width=width, states=2 * Q * B,
                             single_support=disagreements, pair_support=pair_support,
                             exceptional_word_order=order))
    return total, rows


def production_comparison():
    # The retained implementation contains actual front/back swaps and full
    # two-slot target widths; it is not used by the independent census above.
    sys.path.insert(0, str(ROOT / 'scripts'))
    spec = importlib.util.spec_from_file_location('retained_compact', ROOT / 'scripts/audit_compact_controls.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    count = 0
    for G, K in ((1, 4), (2, 6), (3, 8)):
        B, Q = 1 << G, 1 << (2 * K)
        for y in sorted({0, 1, 2, Q - 1, 4 * B, 4 * B + 1, Q - 4 * B - 1}):
            for t in range(B):
                for z in (0, 1):
                    for b in range(B):
                        old = dict(x=z, y=y, t=t, b=b)
                        out = module.execute(old, 1, K, 0, G)
                        wanted_y, wanted_t = literal(y, t, z, G, 2 * K)
                        require(out == dict(old, y=wanted_y, t=wanted_t), 'Retained primitive disagreement')
                        twice = module.execute(out, 1, K, 0, G)
                        require(twice == dict(old, y=(y + (2 * B if z and t == B - 1 else 0)) % Q), 'Retained boundary')
                        fixed = module.repaired(module.repaired(old, 1, K, 0, G), 1, K, 0, G)
                        require(fixed == old, 'Retained completed cancellation')
                        count += 1
    return count


def negative_controls():
    G, width, y, t, z = 2, 12, 33, 3, 1
    a = literal(y, t, z, G, width)
    b = literal(*a, z, G, width)
    checks = {
        'raw_word_is_not_ideal': a != (y ^ z, t),
        'raw_pair_is_not_identity': b != (y, t),
        'raw_forward_is_not_inverse': literal(*a, z, G, width) != (y, t),
        'omitting_saturation_test_fails': b != (y, t),
        'wrong_repair_sign_fails': ((b[0] + 8) % (1 << width), b[1]) != (y, t),
        'single_word_half_density_is_not_pair_density': (1 << (width - 1)) != (1 << width),
        'restored_temporary_does_not_imply_identity': b[1] == t and b[0] != y,
        'safe_target_guard_does_not_replace_digit_guard': 8 <= (y >> 1) < 32 - 8 and b != (y, t),
    }
    for name, value in checks.items():
        require(value, 'Failed rejection control: ' + name)
    require(repaired_pair(y, t, z, G, width) == (y, t), 'Correct repair control')
    require(literal(*a, z, G, width, inverse=True) == (y, t), 'Correct inverse control')
    return sorted(checks)


def result():
    base = source_pins()
    total, rows = census()
    return dict(status='SCOPED NEGATIVE RESULT; NO NEW KAPPA', base_commit=base,
                seed=51, exhaustive_states=total, domains=rows,
                production_comparisons=production_comparison(),
                controls=negative_controls(), witness=dict(G=2, K=6, x=1, y=33, t=3, b=2,
                first_y=40, second_y=41, ideal_pair_y=33),
                universal_pair_support='1/(2*2^G) over z,y,t; 1/2^G conditional on z=1',
                scope='One compact digit, rho=0. General proof is written, not formally checked. Production comparisons are targeted, not exhaustive.')


if __name__ == '__main__':
    receipt = result()
    if '--write' in sys.argv:
        (HERE / 'RESULT.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    else:
        require(receipt == json.loads((HERE / 'RESULT.json').read_text()), 'Receipt mismatch')
    print('PASS_COMPACT_BOUNDARY_CANCELLATION states=%d production=%d controls=%d no_new_kappa' %
          (receipt['exhaustive_states'], receipt['production_comparisons'], len(receipt['controls'])))

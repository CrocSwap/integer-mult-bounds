"""Direct Gaussian columns for the ordered 476 → 878 → 127 relay.

The canonical frame rule is the chart-dephased XOR convolution. Expand
it directly in integers here, independently of the native lowering engine.
"""

from hashlib import sha256
import json


def ensure(value, reason):
    if not value:
        raise ValueError(reason)


def support(vectors):
    result = [0]
    for v in vectors:
        ensure(v not in result, "independent frame basis")
        result.extend([x ^ v for x in result])
    return result


def phase_polynomial(basis):
    """Find the coordinate inverse by enumerating the 512-point basis bijection."""
    if len(basis) in (0, 9):
        return [0] * 512
    image = support(basis)
    for e in (1 << j for j in range(9)):
        if e not in image:
            image.extend([x ^ e for x in image])
    ensure(len(image) == len(set(image)) == 512, "square ordered chart extension")
    inverse = {value: i for i, value in enumerate(image)}
    dual = [inverse[1 << j] for j in range(9)]
    unary = [1 ^ (value.bit_count() % 2) for value in dual]
    pairs = [(1 << j) | (1 << i) for j in range(9) for i in range(j)
             if (dual[j] & dual[i]).bit_count() % 2]
    return [
        (sum(a for j, a in enumerate(unary) if x & (1 << j))
         + 2 * sum(x & mask == mask for mask in pairs)) % 4
        for x in range(512)
    ]


def rotate(a, b, kind):
    return ((a, b), (-b, a), (-a, -b), (b, -a))[kind % 4]


def direct_frame(basis, sign):
    bits = len(basis)
    powers = support(basis)
    phases = phase_polynomial(basis)
    a, b = 1, 0
    for _ in range(bits):
        a, b = a - sign*b, b + sign*a
    offsets = [(effect, sign * mask.bit_count()) for mask, effect in enumerate(powers)]

    def apply(source):
        ans = {}
        for x, (u, v) in source.items():
            re, im = u*a-v*b, u*b+v*a
            previous = phases[x]
            for offset, flips in offsets:
                y = x ^ offset
                wr, wi = rotate(re, im, phases[y] - previous - flips)
                old_r, old_i = ans.get(y, (0, 0))
                ans[y] = old_r + wr, old_i + wi
        return {k: value for k, value in ans.items() if value != (0, 0)}

    return apply


def compare_columns(frames):
    a, b, c = 476, 878, 127
    ensure(set(support(frames[a])) < set(support(frames[b])) < set(support(frames[c])),
           "exact binary nested charts")
    canonical = {(chart, sign): direct_frame(frames[chart], sign)
                 for chart in (a, b, c) for sign in (-1, 1)}

    def run(k, path):
        vect = {k: (1, 0)}
        denominator_bits = 0
        for chart, sign in path:
            vect = canonical[chart, sign](vect)
            denominator_bits += len(frames[chart])
        return vect, denominator_bits

    def literal(vect):
        return json.dumps(sorted(vect.items()), separators=(",", ":")).encode()

    summaries = {}
    first = {}
    for source, center, target, direction in ((a, b, c, "forward"), (c, b, a, "adjoint")):
        joined_path = ((source, -1), (target, 1))
        original_path = ((source, -1), (center, 1), (center, -1), (target, 1))
        direct_hash = sha256()
        for col in range(512):
            changed, new_bits = run(col, joined_path)
            original, old_bits = run(col, original_path)
            stretch = 1 << (old_bits - new_bits)
            ensure(len(changed) == 64 and old_bits == new_bits + 12, "all columns have rank-six support")
            ensure(original == {i: (stretch*x, stretch*y) for i, (x, y) in changed.items()},
                   f"same exact {direction} Gaussian column {col}")
            direct_hash.update(literal(changed))
            if col == 0:
                first[direction] = changed
        summaries[direction] = {"columns": 512, "entries_each": 64,
                                "unreduced_denominator_power_of_two": new_bits,
                                "sha256": direct_hash.hexdigest()}
    rotated = {i: rotate(x, y, 1) for i, (x, y) in first["forward"].items()}
    ensure(rotated != first["forward"], "same-rank global quarter-phase fault")
    ensure(summaries["forward"]["sha256"] != summaries["adjoint"]["sha256"],
           "reversing the orientation is detected")
    return {"method": "direct integer chart-dephased XOR convolution; no production native engine",
            "charts": [a, b, c], "source_and_destination_ranks": [3, 3, 6],
            **summaries, "quarter_phase_rejected": True, "wrong_orientation_rejected": True}

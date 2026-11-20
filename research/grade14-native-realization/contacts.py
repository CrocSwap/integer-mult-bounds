"""Construct all complete complex contact permutations and their translations."""

from functools import cache, reduce
from hashlib import sha256
from operator import xor
import json

from charts import linear_records, require

AXES = tuple(1 << i for i in range(17))
COUNT = 1 << 17
# Position k of each Python integer represents Walsh character k.
ONES = (1 << COUNT) - 1
BITS = tuple((ONES // ((1 << (1 << i)) + 1)) << (1 << i) for i in range(17))


@cache
def walsh(v):
    return reduce(xor, (x for j, x in enumerate(BITS) if v >> j & 1), 0)


def correction(before, after, transport):
    low = high = 0
    for sign, terms, change in ((-1, before, transport), (1, after, lambda v: v)):
        for v, coefficient in terms:
            bit = walsh(change(v))
            c = (sign * coefficient) % 4
            if c & 1:
                high ^= low & bit
                low ^= bit
            if c & 2:
                high ^= bit
    mask = sum(1 << i for i in range(17) if high >> (1 << i) & 1)
    require(
        low == 0 and high == walsh(mask), "all Walsh characters require one translation"
    )
    return mask


def image(columns, v):
    return reduce(xor, (a for j, a in enumerate(columns) if v >> j & 1), 0)


def binary_rows(columns):
    return [
        sum(((c >> i) & 1) << j for j, c in enumerate(columns))
        for i in range(len(columns))
    ]


def port_data(q, basis):
    frame = [q, *basis]
    require(
        len(frame) == 9
        and all(
            (x & y).bit_count() % 2 == int(i == j)
            for i, x in enumerate(frame)
            for j, y in enumerate(frame)
        ),
        "orthonormal port frame",
    )

    def push(v):
        return (v & ~511) ^ image(frame, v & 511)

    def pull(v):
        return (v & ~511) ^ sum(
            ((v & x).bit_count() % 2) << j for j, x in enumerate(frame)
        )

    def swap(v):
        h = v & 511
        out = q if (h & q).bit_count() % 2 else 0
        for j, b in enumerate(basis):
            if v >> (9 + j) & 1:
                out ^= b
            if (h & b).bit_count() % 2:
                out ^= 1 << (9 + j)
        return out

    require(all(swap(swap(v)) == v for v in AXES), "port exchange involution")
    central = [(v, 1) for v in AXES[:9]]
    fresh = [(v, 1) for v in AXES[9:]]
    all_axes = central + fresh
    y = central + [(q, -1)]
    signed = all_axes + [(q, -1)]
    forward = correction(central, central, push)
    reverse = correction(central, central, pull)
    require(
        reverse == pull(forward)
        and forward == correction(central + [(1, -1)], y, push),
        "one center route for both inputs",
    )
    shifts = [
        correction(central, fresh + [(q, 1)], swap),
        correction(y, fresh, swap),
        correction(all_axes, all_axes, swap),
        correction(signed, signed, swap),
    ]
    return frame, forward, reverse, shifts, [swap(v) for v in AXES]


def ordinary_map(columns, translation, slots):
    records = linear_records(binary_rows(columns))
    yield from (("ROW", slots[t], slots[s]) for _, t, s in records)
    yield from (("NOT", k) for i, k in enumerate(slots) if translation >> i & 1)


def contact_receipt(layout, bases):
    atlas = []
    upper = count = 0
    for q in layout["ports"]:
        frame, forward, reverse, shifts, columns = port_data(q, bases[str(q)])
        by_color = []
        for color in range(16):
            slots = [*range(9), *range(9 + 8 * color, 17 + 8 * color)]
            by_color.append([(v & 511) | ((v & ~511) << (8 * color)) for v in shifts])
            for v in shifts:
                plan = list(ordinary_map(columns, v, slots))
                require(
                    all(i in slots for rec in plan for i in rec[1:]), "port spectator"
                )
                upper = max(upper, len(plan))
                count += 1
        atlas.append([q, frame, forward, reverse, by_color])
    digest = sha256(json.dumps(atlas, separators=(",", ":")).encode()).hexdigest()
    require(
        digest == "bc28417912a4dcc1a949990776163791f772d9dace2254af8090dac32c9f6930",
        "source 137-axis port atlas",
    )
    return dict(
        contacts=count,
        walsh_phase_values=104 * 7 * COUNT,
        maximum_contact_records=upper,
        atlas_sha256=digest,
    )

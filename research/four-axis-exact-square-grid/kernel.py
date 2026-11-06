"""Exact four-axis lattice map; integer arithmetic and a finite certificate.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The native factorization and sharp radius originate in Nick Petalas's #6574;
the phase-period interface is developed in #6758 and the square-period
obstruction in #6761. This module does not implement a physical tape tariff.
"""

import json
from functools import lru_cache
from pathlib import Path

N = 16
ROWS = (0x21, 0x906, 0x6FDE, 0x103, 0xA8EC, 0x29E)
HI = tuple(j for j in range(N) if j.bit_count() >= 2)
SIGN = tuple((-1) ** j.bit_count() for j in range(N))
RE = tuple((1, 0, -1, 0)[j.bit_count() % 4] for j in range(N))
IM = tuple((0, -1, 0, 1)[j.bit_count() % 4] for j in range(N))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def vector(values):
    values = tuple(values)
    require(len(values) == N and all(type(x) is int for x in values),
            "expected sixteen exact integers")
    return values


def neg(v):
    return tuple(-x for x in v)


def walsh(v):
    """Unnormalized Walsh transform: 64 additions/subtractions."""
    out = list(v)
    width = 1
    while width < N:
        for block in range(0, N, 2 * width):
            for j in range(block, block + width):
                a, b = out[j], out[j + width]
                out[j], out[j + width] = a + b, a - b
        width *= 2
    return tuple(out)


def quarter(v):
    require(all(x % 4 == 0 for x in v), "nonintegral exact quarter")
    return tuple(x // 4 for x in v)


def b_map(v):
    return quarter(tuple(s * x for s, x in zip(SIGN, walsh(v))))


def k_map(v):
    return tuple(SIGN[j] * v[j ^ 15] for j in range(N))


def l_basis():
    out = []
    v = [0] * N
    v[0] = 4
    out.append(tuple(v))
    for bit in range(4):
        v = [0] * N
        v[0], v[1 << bit] = -2, 2
        out.append(tuple(v))
    for j in HI:
        v = [0] * N
        v[j], v[0] = 1, j.bit_count() - 1
        for bit in range(4):
            if j >> bit & 1:
                v[1 << bit] = -1
        out.append(tuple(v))
    return tuple(out)


BASIS = l_basis()


def l_coords(v):
    total = sum(v)
    bits = [sum(v[j] for j in range(N) if j >> bit & 1)
            for bit in range(4)]
    require(total % 4 == 0 and all(x % 2 == 0 for x in bits),
            "vector is not in the Walsh integrality lattice")
    return (total // 4, *(x // 2 for x in bits), *(v[j] for j in HI))


def syndrome(coords):
    mask = sum((x & 1) << j for j, x in enumerate(coords))
    return sum(((r & mask).bit_count() % 2) << j
               for j, r in enumerate(ROWS))


def coarse_rep(q):
    a, bits = q & 3, q >> 2
    v = [0] * N
    v[0] = a - bits.bit_count()
    for bit in range(4):
        v[1 << bit] = bits >> bit & 1
    return tuple(v)


BASE = tuple(coarse_rep(q) for q in range(64))


def class_id(z):
    """The 12-bit class depends only on each input's three low bits."""
    v = tuple(x % 8 for x in z)  # 8 Z^16 is contained in Gamma.
    bit_mask = sum((sum(v[j] for j in range(N) if j >> bit & 1) % 2)
                   << bit for bit in range(4))
    q = sum(v) % 4 + 4 * bit_mask
    return 64 * q + syndrome(l_coords(tuple(x - y for x, y in zip(v, BASE[q]))))


def representatives():
    # Deterministic section: first independent syndrome columns in ascending
    # basis order. The resulting representative ordering is certificate data.
    sections = {0: 0}
    for j in range(N):
        col = sum(((r >> j) & 1) << bit for bit, r in enumerate(ROWS))
        if col not in sections:
            sections.update({q ^ col: mask ^ (1 << j)
                             for q, mask in list(sections.items())})
    require(len(sections) == 64, "period syndrome rank is not six")
    lifts = [tuple(sum(BASIS[j][i] for j in range(N) if sections[q] >> j & 1)
                   for i in range(N)) for q in range(64)]
    return tuple(tuple(x + y for x, y in zip(BASE[q], lifts[v]))
                 for q in range(64) for v in range(64))


REPS = representatives()


def expand_certificate(data):
    """Expand cycle generators without a matching search or external inputs."""
    require(data.get("schema_version") == 1, "unsupported certificate schema")
    require(data.get("period_rows") == list(ROWS), "wrong period rows")
    cycles = data.get("cycles")
    require(type(cycles) is list and 1 <= len(cycles) <= 4096,
            "invalid cycle inventory")
    table = {}
    for row in cycles:
        require(type(row) is list and len(row) == 2, "invalid cycle encoding")
        source, raw_c = row
        require(type(source) is int and 0 <= source < 4096, "invalid source class")
        c0 = vector(raw_c)
        require(sum(x * x for x in c0) <= 64, "correction exceeds sharp radius")
        require(sum(a * x for a, x in zip(RE, c0)) == 0 and
                sum(a * x for a, x in zip(IM, c0)) == 0, "nonzero weighted sum")
        z0, c = REPS[source], c0
        z = z0
        for _ in range(4):
            for u, correction in ((class_id(z), c), (class_id(neg(z)), neg(c))):
                require(u not in table or table[u] == correction,
                        "incompatible correction cycle")
                table[u] = correction
            z = quarter(tuple(s * w + e for s, w, e in zip(SIGN, walsh(z), c)))
            c = neg(b_map(c))
        require(z == z0 and c == c0, "cycle does not close")
    require(len(table) == 4096, "incomplete correction table")
    return tuple(table[j] for j in range(4096))


@lru_cache(maxsize=1)
def load_table():
    path = Path(__file__).with_name("CERTIFICATE.json")
    require(path.stat().st_size <= 1_000_000, "oversized certificate")
    return expand_certificate(json.loads(path.read_text(encoding="utf-8")))


def t_map(z, table=None):
    z = vector(z)
    if table is None:
        table = load_table()
    c = table[class_id(z)]
    return quarter(tuple(s * w + e for s, w, e in zip(SIGN, walsh(z), c)))


def r_map(z, table=None):
    return tuple(s * x for s, x in zip(SIGN, t_map(z, table)))


def diagonal(real, imag):
    """Multiply coordinate j by (-i)^wt(j), using exact integer pairs."""
    a, b = [], []
    for j, (x, y) in enumerate(zip(real, imag)):
        pair = ((x, y), (y, -x), (-x, -y), (-y, x))[j.bit_count() % 4]
        a.append(pair[0])
        b.append(pair[1])
    return tuple(a), tuple(b)


def forward(real, imag, table=None):
    """F = -D R_C D. Arguments and return value are two integer vectors."""
    real, imag = diagonal(vector(real), vector(imag))
    real, imag = diagonal(r_map(real, table), r_map(imag, table))
    return neg(real), neg(imag)


def inverse(real, imag, table=None):
    """The literal inverse J F, not an approximate reverse transform."""
    real, imag = forward(real, imag, table)
    return tuple(real[j ^ 15] for j in range(N)), tuple(imag[j ^ 15] for j in range(N))

#!/usr/bin/env python3
"""Independent check of PR #4541's packed IO codec (Section 4 and PACKED-IO.md), written from the vendored text only.

Builds the codec as PACKED-IO.md describes it: tables E[x], Er[x] for x < 2^r and the decoder (length, value, valid)
for every y < 2^(cr); LSB-first and MSB-first input expansion through a reservoir of fewer than r cells with at most
one r-cell flush per append; output decoding of an MSB-first coded prefix (stop at the first blank or the m-cell cap,
reject invalid cells before the blank), reverse traversal of the chunk descriptors and exactly ceil(m/r) LSB digit
words with zero high padding. It is compared with direct binary encoding on random and edge-case operands for
r in {1,2,4,8}, c in {2,4} (2^(cr) <= 2^16), and on a tape shared by two operands with a delimiter. Controls: every
single-entry decoder mutation of a sample is detected by a round trip; concatenating separately padded chunks on a
shared tape inserts blanks and is caught.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import hashlib
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
SPEC = HERE / "PR4541-PACKED-IO.md"  # #4541 head 46ca24a8, research/packed-ram-speedup/PACKED-IO.md, blob 675e520c
SPEC_SHA256 = "3197b3763d6c8ac7733ed128b4191b19ae0fd22a9d94d90cf80ca2a3b9459120"


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def ceil_div(a, b):
    return -(-a // b)


class Codec:
    def __init__(self, r, c):
        self.r, self.c = r, c
        cm = (1 << c) - 1
        self.E = [0] * (1 << r)
        self.Er = [0] * (1 << r)
        for x in range(1 << r):
            for j in range(r):
                self.E[x] |= (1 + ((x >> j) & 1)) << (c * j)
                self.Er[x] |= (1 + ((x >> (r - 1 - j)) & 1)) << (c * j)
        self.D = []
        for y in range(1 << (c * r)):
            length, value, valid = 0, 0, True
            for j in range(r):
                cell = (y >> (c * j)) & cm
                if cell == 0:
                    break
                if cell not in (1, 2):
                    valid = False
                    break
                value = (value << 1) | (cell - 1)
                length += 1
            self.D.append((length, value, valid))
        self.max_reservoir = 0
        self.max_flushes = 0

    def _append(self, res, rlen, chunk, clen, out, width):
        """Append clen fields of `width` bits; flush r fields if at least r are present."""
        res |= chunk << (width * rlen)
        need(res < 1 << (2 * width * self.r), "reservoir below 2r fields of width bits")
        rlen += clen
        flushes = 0
        if rlen >= self.r:
            out.append(res & ((1 << (width * self.r)) - 1))
            res >>= width * self.r
            rlen -= self.r
            flushes += 1
        need(rlen < self.r, "reservoir below r after one flush")
        self.max_reservoir = max(self.max_reservoir, rlen + clen)
        self.max_flushes = max(self.max_flushes, flushes)
        return res, rlen

    def expand(self, digits, n, msb, res=0, rlen=0, out=None):
        """Input digits (little-endian base 2^r, exactly ceil(n/r)) -> packed r-cell chunks of c-bit codes."""
        r, c = self.r, self.c
        out = [] if out is None else out
        nd = ceil_div(n, r)
        need(len(digits) == nd, "digit count")
        top = n - r * (nd - 1) if nd else 0
        order = range(nd - 1, -1, -1) if msb else range(nd)
        for u in order:
            x = digits[u]
            ell = top if u == nd - 1 else r
            if msb:
                chunk = self.Er[x] >> (c * (r - ell))
            else:
                chunk = self.E[x] & ((1 << (c * ell)) - 1)
            res, rlen = self._append(res, rlen, chunk, ell, out, c)
        return res, rlen, out

    def finish(self, res, rlen, out):
        if rlen:
            out.append(res)
        return out

    def decode(self, chunks, m):
        """Packed tape chunks (MSB-first coded prefix) -> exactly ceil(m/r) LSB digit words, or None if rejected."""
        r, c = self.r, self.c
        descriptors, seen, terminated = [], 0, False
        for u in range(ceil_div(m, r)):
            y = chunks[u] if u < len(chunks) else 0
            cap = min(r, m - seen)
            y &= (1 << (c * cap)) - 1
            length, value, valid = self.D[y]
            if not valid:
                return None
            descriptors.append((value, length))
            seen += length
            if length < cap:
                terminated = True
                break
            if seen == m:
                break
        need(terminated or seen == m or m == 0, "protocol: payload or terminator")
        out, res, rlen = [], 0, 0
        for value, length in reversed(descriptors):
            res, rlen = self._append(res, rlen, value, length, out, 1)
        out = self.finish(res, rlen, out)
        while len(out) < ceil_div(m, r):
            out.append(0)
        return out


def to_digits(v, n, r):
    return [(v >> (r * u)) & ((1 << r) - 1) for u in range(ceil_div(n, r))]


def from_digits(ds, r):
    return sum(d << (r * u) for u, d in enumerate(ds))


def cells_of(chunks, r, c, count):
    return [(chunks[i // r] >> (c * (i % r))) & ((1 << c) - 1) if i // r < len(chunks) else 0 for i in range(count)]


def check_config(r, c, rng):
    cd = Codec(r, c)
    need(max(cd.E + cd.Er) < 1 << (c * r) and len(cd.D) == 1 << (c * r), "table keys and entries within cr bits")
    cases = 0
    lengths = sorted(set([0, 1, r - 1, r, r + 1, 2 * r, 2 * r + 1, 3 * r - 1] + [rng.randrange(1, 12 * r) for _ in range(8)]))
    for n in [x for x in lengths if x >= 0]:
        values = {0, (1 << n) - 1 if n else 0, 1 if n else 0} | {rng.getrandbits(n) if n else 0 for _ in range(6)}
        for v in values:
            ds = to_digits(v, n, r)
            need(all(d < (1 << r) for d in ds), "digits fit")
            bits_lsb = [(v >> i) & 1 for i in range(n)]
            for msb in (False, True):
                res, rlen, out = cd.expand(ds, n, msb)
                chunks = cd.finish(res, rlen, out)
                expect = [1 + b for b in (bits_lsb[::-1] if msb else bits_lsb)]
                need(cells_of(chunks, r, c, n + 2 * r) == expect + [0] * (2 * r), "expanded cells, blanks after n")
                cases += 1
            # Output: MSB-first coded prefix with dirty cells after the terminator; caps above and at n.
            stream = [1 + b for b in bits_lsb[::-1]]
            for m in sorted({n, n + 1, n + r, n + 3}):
                tape = stream + ([0] if m > n else []) + [rng.choice((1, 2, 3)) for _ in range(2 * r)]
                chunks = [sum(tape[i + j] << (c * j) for j in range(r) if i + j < len(tape)) for i in range(0, len(tape), r)]
                got = cd.decode(chunks, m)
                need(got is not None and len(got) == ceil_div(m, r), "output word count")
                need(all(d < (1 << r) for d in got) and from_digits(got, r) == v, "output value")
                cases += 1
    # Leading logical zeros in the output prefix, and an invalid cell before the terminator.
    for m in (r, 2 * r + 1):
        stream = [1] * (m // 2) + [2] + [1] * (m - m // 2 - 1)
        chunks = [sum(stream[i + j] << (c * j) for j in range(r) if i + j < m) for i in range(0, m, r)]
        need(from_digits(cd.decode(chunks, m), r) == 1 << (m - m // 2 - 1), "leading zeros")
        bad = list(stream)
        bad[m // 2] = 3
        chunks = [sum(bad[i + j] << (c * j) for j in range(r) if i + j < m) for i in range(0, m, r)]
        need(cd.decode(chunks, m) is None, "invalid pre-terminator cell rejects")
        cases += 2
    need(cd.decode([], 0) == [], "zero cap emits nothing")
    need(cd.max_reservoir < 2 * r and cd.max_flushes <= 1, "reservoir < 2r cells, one flush per append")
    return cd, cases


def shared_tape(rng):
    r, c = 4, 2
    cd = Codec(r, c)
    caught = 0
    for _ in range(50):
        n1, n2 = rng.randrange(1, 20), rng.randrange(1, 20)
        v1, v2 = rng.getrandbits(n1), rng.getrandbits(n2)
        res, rlen, out = cd.expand(to_digits(v1, n1, r), n1, True)
        res, rlen = cd._append(res, rlen, 3, 1, out, c)  # delimiter cell 3
        res, rlen, out = cd.expand(to_digits(v2, n2, r), n2, True, res, rlen, out)
        chunks = cd.finish(res, rlen, out)
        expect = [1 + ((v1 >> i) & 1) for i in reversed(range(n1))] + [3] + [1 + ((v2 >> i) & 1) for i in reversed(range(n2))]
        need(cells_of(chunks, r, c, n1 + n2 + 1) == expect, "continuous reservoir across operands")
        # Control: separately padded chunk streams leave blanks between the operands unless n1 is a multiple of r.
        a = cd.finish(*cd.expand(to_digits(v1, n1, r), n1, True))
        b = cd.finish(*cd.expand(to_digits(v2, n2, r), n2, True))
        naive = cells_of(a, r, c, len(a) * r) + [3] + cells_of(b, r, c, n2)
        if n1 % r:
            need(naive != expect, "padded concatenation differs")
            caught += 1
    return caught


def mutations(rng):
    r, c = 4, 2
    cd = Codec(r, c)
    caught = tried = 0
    for y in rng.sample(range(1 << (c * r)), 1 << (c * r)):
        if tried == 25:
            break
        length, value, valid = cd.D[y]
        if not valid or length == 0:
            continue
        cells = cells_of([y], r, c, length)
        v = sum((cells[i] - 1) << (length - 1 - i) for i in range(length))
        good = cd.decode([y], r)  # cap r: the decoder reads key y itself
        need(from_digits(good, r) == v, "unmutated entry")
        saved = cd.D[y]
        cd.D[y] = (length, value ^ 1, valid)
        tried += 1
        caught += int(from_digits(cd.decode([y], r), r) != v)
        cd.D[y] = saved
    need(tried == 25 and caught == tried, "every decoder mutation detected")
    return caught


def binding():
    raw = SPEC.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == SPEC_SHA256, "vendored PACKED-IO.md bytes")
    text = raw.decode("utf-8")
    for s in ("E[x]  = sum_j (1 + bit_j(x)) << (cj),", "Er[x] = sum_j (1 + bit_(r-1-j)(x)) << (cj).",
              "value <- (value<<1) OR (cell-1)", "shift Er[x] right by c(r-ell)", "fewer than 2r cells",
              "Traverse the retained chunk descriptors in reverse order.", "exactly ceil(m/r) little-endian beta digits"):
        need(s in text, f"PACKED-IO.md states: {s}")
    return 7


def main():
    rng = random.Random(45412)
    total, configs = 0, []
    for r, c in ((1, 2), (2, 2), (4, 2), (8, 2), (1, 4), (2, 4), (4, 4)):
        cd, cases = check_config(r, c, rng)
        total += cases
        configs.append(f"r={r},c={c}")
    report = {"status": "PASS_PR4541_PACKED_IO_CHECK", "configs": configs, "codec_cases": total,
              "decoder_rows_built": sum(1 << (c * r) for r, c in ((1, 2), (2, 2), (4, 2), (8, 2), (1, 4), (2, 4), (4, 4))),
              "shared_tape_padding_controls": shared_tape(rng), "decoder_mutations_detected": mutations(rng),
              "spec_statements_bound": binding(), "new_kappa_claimed": False}
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    sys.exit(main())

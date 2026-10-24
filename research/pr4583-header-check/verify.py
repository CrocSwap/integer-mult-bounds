#!/usr/bin/env python3
"""Independent check of PR #4583 (mihir-s-05): a serialized header for the PR4100 sparse-union schedule.

Written from #4583's README field table; nothing is imported from #4583's header.py or verify.py.
  1. A separate big-endian codec: marker 01 (2 bits), local coordinates x_0..x_(g-1) (h bits each), membership flags
     (g bits), boundary ordinals (h bits each; rank in E_i when flagged, 0 otherwise), flag count and current tag
     (b = ceil(log2(g+1)) bits each, tag = g as the untagged sentinel). Round trips over random contexts and every
     boundary subset in a small domain; the encoded width equals H = 2gh + g + 2b + 2; in round r the (r+1)st set
     flag gives the active axis, a record is kept iff count > r + 1, and the active ordinal is read back; a bad marker
     and an inconsistent flag count are rejected.
  2. The width bound H < 810 g log2 p with h = ceil(400 log2 p) computed exactly as (p^400 - 1).bit_length(), for
     integer p (powers of two and others) and g <= 2000, via the chain H <= 2gh + 5g <= 800 g t + 7g <= 807 g t.
  3. The cutoff: delta = 1 - beta = 3/10^30 bound to the pinned #4100 ledger (beta and the group_headers slack), the
     core side L = 2^ceil(400 log2 p) bound to GAUSSIAN.md, delta*t0 = 120 at t0 = 40*10^30, 810 t0 < 2^115 and
     1620 t0 < 2^116 (so H/p < 1/32 and < 1/16 at t0), and the derivative sign 1 - delta t ln 2 < 0 for t >= t0.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as Fr
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LEDGER = ROOT / "research/unconditional-batched-crt/evidence/composition-controls.json"
GAUSSIAN = ROOT / "research/unconditional-batched-crt/GAUSSIAN.md"


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def bits_for(g):
    return g.bit_length()  # ceil(log2(g+1))


def encode(x, sets, tag, h):
    g = len(x)
    b = bits_for(g)
    flags = [1 if x[i] in sets[i] else 0 for i in range(g)]
    ords = [sorted(sets[i]).index(x[i]) if flags[i] else 0 for i in range(g)]
    bits = "01" + "".join(format(v, f"0{h}b") for v in x) + "".join(map(str, flags))
    bits += "".join(format(v, f"0{h}b") for v in ords) + format(sum(flags), f"0{b}b") + format(tag, f"0{b}b")
    return bits


def decode(bits, g, h):
    b = bits_for(g)
    need(bits[:2] == "01", "record marker")
    pos = 2
    x = [int(bits[pos + i * h: pos + (i + 1) * h], 2) for i in range(g)]
    pos += g * h
    flags = [int(c) for c in bits[pos: pos + g]]
    pos += g
    ords = [int(bits[pos + i * h: pos + (i + 1) * h], 2) for i in range(g)]
    pos += g * h
    count = int(bits[pos: pos + b], 2)
    tag = int(bits[pos + b: pos + 2 * b], 2)
    need(pos + 2 * b == len(bits), "exact length")
    need(count == sum(flags) and tag <= g, "consistent count and tag")
    return x, flags, ords, count, tag


def check_codec(rng):
    trips = active = rejects = 0
    for g in range(1, 6):
        for L in (2, 3, 4, 7, 8, 16):
            h = (L - 1).bit_length()
            for _ in range(60):
                sets = [set(v for v in range(L) if rng.random() < 0.4) for _ in range(g)]
                x = [rng.randrange(L) for _ in range(g)]
                bits = encode(x, sets, g, h)
                need(len(bits) == 2 * g * h + g + 2 * bits_for(g) + 2, "width formula")
                xd, flags, ords, count, tag = decode(bits, g, h)
                need(xd == x and tag == g, "round trip")
                for i in range(g):
                    if flags[i]:
                        need(sorted(sets[i])[ords[i]] == x[i], "ordinal recovers the boundary point")
                trips += 1
                set_axes = [i for i in range(g) if flags[i]]
                for r in range(g):
                    need((count > r + 1) == (len(set_axes) > r + 1), "keep decision")
                    if r < len(set_axes):
                        f = set_axes[r]
                        _, _, o2, _, t2 = decode(encode(x, sets, f, h), g, h)
                        need(t2 == f and o2[f] == sorted(sets[f]).index(x[f]), "active axis and ordinal")
                        active += 1
                try:
                    decode("10" + bits[2:], g, h)
                except AssertionError:
                    rejects += 1
                b = bits_for(g)
                cpos = 2 + 2 * g * h + g
                wrong = (sum(flags) + 1) % (1 << b)
                if wrong != sum(flags):
                    try:
                        decode(bits[:cpos] + format(wrong, f"0{b}b") + bits[cpos + b:], g, h)
                    except AssertionError:
                        rejects += 1
    for g in (1, 2):
        L, h = 4, 2
        for mask in range(1 << (L * g)):
            sets = [set(v for v in range(L) if mask >> (i * L + v) & 1) for i in range(g)]
            for x0 in range(L):
                x = [x0] * g
                xd, flags, _, _, _ = decode(encode(x, sets, g, h), g, h)
                need(xd == x and flags == [1 if x0 in s else 0 for s in sets], "exhaustive subsets")
                trips += 1
    return trips, active, rejects


def check_width():
    cases = 0
    for p in list(range(2, 70)) + [2 ** k for k in range(7, 41)] + [10 ** 6 + 3, 3 ** 20]:
        h = (p ** 400 - 1).bit_length()
        need(1 << (h - 1) < p ** 400 <= 1 << h, "h = ceil(400 log2 p)")
        # t = log2 p satisfies 400 t > h - 1, i.e. t > (h - 1)/400 =: t_lo, and t >= 1 since p >= 2.
        t_lo = max(Fr(h - 1, 400), Fr(1))
        for g in list(range(1, 60)) + [100, 500, 2000]:
            b = bits_for(g)
            H = 2 * g * h + g + 2 * b + 2
            need(b <= g and H <= 2 * g * h + 5 * g, "first link: b <= g")
            # 2gh = 2g((h - 1) + 1) < 2g(400 t) + 2g, so H < 800 g t + 7 g <= 807 g t (t >= 1) < 810 g t.
            need(H <= 800 * g * Fr(h, 400) + 5 * g, "second link: 2gh = 800 g (h/400)")
            need(H <= 810 * g * t_lo, "H < 810 g t, since t > t_lo")
            cases += 1
    return cases


def check_cutoff():
    ledger = json.loads(LEDGER.read_bytes())
    beta = Fr(ledger["parameters"]["beta"])
    delta = 1 - beta
    need(delta == Fr(3, 10 ** 30) and Fr(ledger["side_slacks"]["group_headers"]) == delta, "beta and header slack")
    need("L=2^ceil(400log2 p)" in GAUSSIAN.read_text(encoding="utf-8"), "core side L = 2^ceil(400 log2 p)")
    t0 = 40 * 10 ** 30
    need(delta * t0 == 120, "delta t0 = 120")
    need(810 * t0 < 2 ** 115 and 1620 * t0 < 2 ** 116, "cutoff integers")
    need(Fr(810 * t0, 2 ** 120) < Fr(1, 32) and Fr(1620 * t0, 2 ** 120) < Fr(1, 16), "ratios at t0")
    need(delta * t0 * Fr(1, 2) > 1, "monotone tail (ln 2 > 1/2)")
    return str(delta)


def main():
    rng = random.Random(4583)
    trips, active, rejects = check_codec(rng)
    report = {"status": "PASS_PR4583_HEADER_CHECK", "codec_round_trips": trips, "active_header_checks": active,
              "rejected_corruptions": rejects, "width_cases": check_width(), "delta": check_cutoff(),
              "new_kappa_claimed": False}
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    sys.exit(main())

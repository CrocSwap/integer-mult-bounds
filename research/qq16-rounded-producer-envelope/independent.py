#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Separate forward-load / reverse-adjoint check; no primary-code imports.

Prepared for commdata2338, with substantial OpenAI Codex assistance.
This independently checks every P/J cut with integers and six reported
category rows with reverse adjoints. Native semantics remain inherited.
"""
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
SOURCE = ROOT / "research/joint-query/certificate.json.gz"
SOURCE_HASH = "a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7"
PAYLOAD_HASH = "2efe83c59978aa9c0db2c3e4eccc14cbfdcd3c9ce499432601b5dd34083472ef"


def check(ok, message):
    if not ok:
        raise ValueError(message)


def register(token):
    check(token[0] in ("L", "C"), "register namespace")
    return token[1] + (704 if token[0] == "C" else 0)


def events_for(packet, name):
    events = []
    for entry in packet["programs"][name]:
        if entry[0] == "retained_core":
            events += packet["core_words"][entry[1]]
        elif entry[0] in ("cover_sweep", "private_sweep"):
            events += entry[2]
        else:
            events.append(entry)
    return events


def instructions(events):
    """Independent event decoder, preserving the unfiltered indices."""
    rows = []
    for e in events:
        kind = e[0]
        if kind == "phase":
            rows.append(("none", -1, -1, Fraction(0), None))
        elif kind == "scalar":
            g = e[1]
            d = register(g[1])
            if g[0] == "clear":
                rows.append(("zero", d, -1, Fraction(0), None))
            elif g[0] == "scale":
                rows.append(("mul", d, -1, abs(Fraction(g[2], g[3])), "scale"))
            else:
                check(g[0] == "add", "scalar kind")
                rows.append(("sum", d, register(g[2]), abs(Fraction(g[3], g[4])), "add"))
        elif kind in ("climb", "adapter", "residual_adapter"):
            rows.append(("one", e[2], -1, Fraction(1), "child" if kind == "climb" else "adapter"))
        else:
            check(kind in ("native_line", "cover_map"), "native kind")
            rows.append(("one", register(e[1]), -1, Fraction(1),
                         "child" if kind == "native_line" else "map"))
    return rows


def load_trace(rows):
    values = [Fraction(1)] * 704 + [Fraction(0)] * 8
    initialized = set(range(704))
    loads = []
    for kind, d, s, c, _ in rows:
        if kind == "none":
            loads.append(Fraction(0))
            continue
        if kind == "zero":
            check(d >= 704, "clear ownership")
            values[d] = Fraction(0)
            initialized.add(d)
        else:
            check(d in initialized and (s < 0 or s in initialized), "uninitialized field")
            if kind == "mul":
                values[d] *= c
            elif kind == "sum":
                values[d] += c * values[s]
        loads.append(values[d])
    return loads


def dual_row(rows, loads, end, wire):
    covector = [Fraction(0) for _ in range(712)]
    covector[wire] = Fraction(1)
    gains = {key: Fraction(0) for key in ("add", "scale", "child", "adapter", "map")}
    for t in range(end, -1, -1):
        kind, d, s, c, category = rows[t]
        if category is not None:
            gains[category] += covector[d] * loads[t]
        if kind == "zero":
            covector[d] = Fraction(0)
        elif kind == "mul":
            covector[d] *= c
        elif kind == "sum":
            covector[s] += c * covector[d]
    return sum(covector[:704]), gains


def integer_all_cuts(rows, case):
    """Use one deliberately oversized exact dyadic integer grid, not Fractions.

    Paying every scalar denominator in series is sufficient for this verifier;
    it is not a proposed arithmetic format for the physical producer.
    """
    powers = [c.denominator.bit_length() - 1 for _, _, _, c, _ in rows if c]
    check(all(c.denominator & (c.denominator - 1) == 0 for _, _, _, c, _ in rows),
          "dyadic scalar coefficients")
    quantum = 1 << sum(powers)
    p, j = [quantum] * 704 + [0] * 8, [0] * 712
    digest, cut_count, sites = hashlib.sha256(), 0, 0
    maxima = {"P": (quantum, -1, 0), "J": (0, -1, 0)}
    for t, (kind, d, s, c, category) in enumerate(rows):
        if kind == "none":
            continue
        cut_count += 1
        if kind == "zero":
            p[d], j[d] = 0, 0
        elif kind in ("mul", "sum"):
            source = d if kind == "mul" else s
            pn, pr = divmod(p[source] * c.numerator, c.denominator)
            jn, jr = divmod(j[source] * c.numerator, c.denominator)
            check(pr == jr == 0, "independent integer grid exhausted")
            if kind == "mul":
                p[d], j[d] = pn, jn
            else:
                p[d], j[d] = p[d] + pn, j[d] + jn
        if category is not None:
            j[d] += p[d]
            sites += 1
        record = [t, d, str(Fraction(p[d], quantum)), str(Fraction(j[d], quantum))]
        digest.update(json.dumps(record, sort_keys=True, separators=(",", ":")).encode() + b"\n")
        for key, value in (("P", p[d]), ("J", j[d])):
            if value > maxima[key][0]:
                maxima[key] = (value, t, d)
    check(cut_count == case["changed_cuts"] and sites == case["defect_sites"], "cut coverage")
    check(digest.hexdigest() == case["P_J_cut_table_sha256"], "all-cut P/J digest")
    for key, (value, t, d) in maxima.items():
        target = case["all_cut"][key]
        check(Fraction(value, quantum) == Fraction(target[key]), "independent maximum")
        check((t, d) == (target["event"], target["wire"]), "maximum cut")
    for name, indices in (("data", range(224)), ("helpers", range(224, 704))):
        d = max(indices, key=lambda index: j[index])
        check(d == case["terminal"][name]["wire"], "terminal argmax")
        check(Fraction(j[d], quantum) == Fraction(case["terminal"][name]["J"]), "terminal maximum")
    check(p[704:] == j[704:] == [0] * 8, "private final zeros")
    return cut_count


def main():
    compressed = SOURCE.read_bytes()
    check(hashlib.sha256(compressed).hexdigest() == SOURCE_HASH, "source hash")
    payload = gzip.decompress(compressed)
    check(hashlib.sha256(payload).hexdigest() == PAYLOAD_HASH, "payload hash")
    packet = json.loads(payload)
    report = json.loads((BASE / "RESULT.json").read_bytes())
    count, cuts = 0, 0
    for name, case in report["cases"].items():
        rows = instructions(events_for(packet, name))
        cuts += integer_all_cuts(rows, case)
        loads = load_trace(rows)
        targets = list(case["all_cut"].values()) + list(case["terminal"].values())
        unique = {(r["event"], r["wire"]): r for r in targets}
        for (end, wire), target in unique.items():
            p, gains = dual_row(rows, loads, end, wire)
            check(p == Fraction(target["P"]), "reverse input gain")
            check(sum(gains.values()) == Fraction(target["J"]), "reverse derivative")
            for category, value in gains.items():
                check(value == Fraction(target["J_by_category"][category]),
                      "reverse category: " + category)
            count += 1
    c = report["composition"]
    check(Fraction(49, 256) + Fraction(1923, 8192) + Fraction(1, 2) == Fraction(7587, 8192),
          "completed decoder budget")
    check(Fraction(c["F_persistent_J"]) < 2**62, "F sufficient bound")
    check(Fraction(c["B_persistent_J"]) < 2**82, "B sufficient bound")
    check(c["common_relative_offset"] == 102 and c["count_guard"] == 16, "tolerance offsets")
    print(f"PASS_QQ16_PRODUCER_ENVELOPE_INDEPENDENT integer_cuts={cuts} reverse_rows={count} categories=5")


if __name__ == "__main__":
    main()

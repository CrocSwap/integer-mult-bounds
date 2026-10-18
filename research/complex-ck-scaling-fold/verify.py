#!/usr/bin/env python3
"""Exact finite CK cleanup scale relocation. Apache-2.0.

Prepared for @thakrarsagar with substantial OpenAI Codex assistance.
Horner accounting follows icekylinx's emitter/invoice lineage retained in #626.
This does not certify an all-size multiplication theorem or a new kappa.
"""
import copy
import gzip
import hashlib
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROVIDER = "research/community-k492-audit/pr626/replay/mixed-global/base/providers/ck/"
PINS = {
    PROVIDER + "CANONICAL-WORD.json.gz": "9bbc75dede090cfd7a0a0252424ea9d9f6211e2350d2a801d4e4f2f0784167c7",
    PROVIDER + "LOCAL-PROGRAMS.json.gz": "854f17274092263dc25e60367f4cd0d29f60a8446becd17cc1883ebed7a97900",
    "research/complex-k492-owner-repair/code/hpe_emit_local.py": "7e4a6fbc38c8228157b6311457d1496bf460291393043932d2c365f004f77805",
    "research/complex-k492-owner-repair/data/SPEC.json": "2a2577ac526535826fed9d5f7f83f6e2e0ec058a146c64f7286720b995fa2323",
    "certificates/selected-result.json": "b3bf402f31a69bde0629936a9b569bed48281568d7b16d5fba120b5311ea1f53",
    "docs/research/community-k492-review.md": "3b731d30e80010b15408a289b0b32192700885474c8b36d48ee3320a7a8c5c47",
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load():
    sources = {}
    for name, expected in PINS.items():
        data = (ROOT / name).read_bytes()
        if name.endswith(".gz"):
            data = gzip.decompress(data)
        need(hashlib.sha256(data).hexdigest() == expected, "source pin: " + name)
        if name.endswith((".json", ".json.gz")):
            sources[name] = json.loads(data)
    return sources[PROVIDER + "CANONICAL-WORD.json.gz"], sources[PROVIDER + "LOCAL-PROGRAMS.json.gz"]


def add_cost(q):
    a, b = abs(q.numerator), q.denominator
    need(a > 0 and b & (b - 1) == 0, "nonzero dyadic addition required")
    return 3 + a.bit_length() - 1 + bin(a).count("1") + b.bit_length() - 1


def coefficient(e):
    return Q(e[-3], e[-2])


def relocated(ops, source, destination):
    """Move one scale to its final index, preserving the full register map."""
    out = copy.deepcopy(ops)
    scale = out[source]
    need(scale[0] == "scale", "relocation source must be a scale")
    r, q = scale[1], coefficient(scale)
    right = destination > source
    for k in range(min(source, destination), max(source, destination) + 1):
        e = out[k]
        if e[0] == "add" and r in e[1:3]:
            factor = q if (e[2] == r) == right else 1 / q
            a = coefficient(e) * factor
            e[3:5] = [a.numerator, a.denominator]
    out.insert(destination, out.pop(source))
    return out


def search(ops):
    """Exhaust all final positions for each single scale; no composition."""
    records = []
    coverage = hashlib.sha256()
    candidates = 0
    for i, scale in enumerate(ops):
        if scale[0] != "scale":
            continue
        r, q = scale[1], coefficient(scale)
        best = (0, 0, i)
        coverage.update(f"{i},{i},0\n".encode())
        candidates += 1
        for direction in (-1, 1):
            delta = 0
            stop = -1 if direction < 0 else len(ops)
            for j in range(i + direction, stop, direction):
                e = ops[j]
                if e[0] == "add" and r in e[1:3]:
                    a = coefficient(e)
                    factor = q if (e[2] == r) == (direction > 0) else 1 / q
                    delta += add_cost(a * factor) - add_cost(a)
                coverage.update(f"{i},{j},{delta}\n".encode())
                candidates += 1
                best = min(best, (delta, abs(j - i), j))
        records.append(dict(source=i, register=r, factor=str(q), delta=best[0], destination=best[2]))
    winner = min(records, key=lambda x: (x["delta"], abs(x["destination"] - x["source"]), x["source"], x["destination"]))
    return dict(candidates=candidates, coverage_sha256=coverage.hexdigest(), records=records, winner=winner)


def dual(e):
    e = list(e)
    if e[0] == "add":
        e[1], e[2], e[3] = e[2], e[1], -e[3]
    else:
        e[2], e[3] = e[3], e[2]
    return e


def matrix(ops, registers):
    rows = {r: {r: Q(1)} for r in registers}
    for e in ops:
        r, q = e[1], coefficient(e)
        if e[0] == "scale":
            rows[r] = {k: q * v for k, v in rows[r].items()}
        else:
            for k, v in list(rows[e[2]].items()):
                value = rows[r].get(k, 0) + q * v
                if value:
                    rows[r][k] = value
                else:
                    rows[r].pop(k, None)
    return rows


def scalar(e):
    if e[0] == "add":
        return ["add", ["L", e[1]], ["L", e[2]], e[3], e[4]]
    return ["scale", ["L", e[1]], e[2], e[3]]


def recount(events, n):
    """Independent digit-loop billing, including private-work peaks and clears."""
    env = {("L", r): Q(1) for r in range(n)}
    peak, real, macros = Q(1), 0, 0
    for event in events:
        if event[0] != "scalar":
            continue
        e = event[1]
        tag, t = e[0], tuple(e[1])
        macros += 1
        if tag == "clear":
            env[t], count = Q(0), 1
        elif tag == "copy":
            env[t], count = env[tuple(e[2])], 1
        elif tag == "scale":
            q = Q(e[2], e[3])
            a, b = abs(q.numerator), q.denominator
            need(a > 0 and a & (a - 1) == 0 and b & (b - 1) == 0, "power-of-two scale")
            count = abs(a.bit_length() - b.bit_length()) + int(q < 0)
            env[t] *= abs(q)
        elif tag == "add":
            s, q = tuple(e[2]), Q(e[3], e[4])
            need(s != t, "distinct addition registers")
            acc, count = Q(0), 1
            for i, bit in enumerate(bin(abs(q.numerator))[2:]):
                if i:
                    acc *= 2
                    count += 1
                    peak = max(peak, acc * env[s])
                if bit == "1":
                    acc += 1
                    count += 1
                    peak = max(peak, acc * env[s])
            for _ in range(q.denominator.bit_length() - 1):
                acc /= 2
                count += 1
                peak = max(peak, acc * env[s])
            count += 2  # signed accumulation and final private-work clear
            need(acc == abs(q) and count == add_cost(q), "Horner recipe mismatch")
            env[t] += acc * env[s]
        else:
            raise ValueError("unknown scalar " + tag)
        peak = max(peak, env[t])
        real += 2 * count
    need(all(v == 0 for r, v in env.items() if r[0] == "C"), "private centres not cleared")
    return dict(real_primitives=real, scalar_macros=macros, prefix_l1=str(peak), prefix_bits=peak.numerator.bit_length() - peak.denominator.bit_length() + 1)


def run():
    word, programs = load()
    ops = word["cleanup"]
    need(len(ops) == 8309, "cleanup length")
    for e in ops:
        need(e[0] in ("add", "scale") and e[-1] == 1, "cleanup gate/frame")
        regs = e[1:3] if e[0] == "add" else e[1:2]
        need(all(word["final"][r] == 1 for r in regs), "low-ended helper touched")
        if e[0] == "add":
            need(e[1] != e[2], "self-addition")
            add_cost(coefficient(e))
    scan = search(ops)
    win = scan["winner"]
    need((win["source"], win["destination"], win["delta"]) == (4832, 4869, -31), "unexpected optimum")
    changed = relocated(ops, win["source"], win["destination"])
    start, end = win["source"], win["destination"] + 1
    need(ops[:start] == changed[:start] and ops[end:] == changed[end:], "nonlocal edit")
    before, after = ops[start:end], changed[start:end]
    regs = sorted({r for e in before for r in (e[1:3] if e[0] == "add" else e[1:2])})
    results = {}
    controls = 0
    for orientation in ("forward", "backward"):
        convert = dual if orientation == "backward" else lambda e: e
        old, new = [convert(e) for e in before], [convert(e) for e in after]
        need(matrix(old, regs) == matrix(new, regs), "exact boundary mismatch")
        # Omit settlement, leave a crossed coefficient unchanged, or double settlement.
        mutations = [new[:-1], copy.deepcopy(new), copy.deepcopy(new)]
        mutations[1][0][3:5] = old[1][3:5]
        mutations[2][-1][2] *= 2
        for mutation in mutations:
            need(matrix(old, regs) != matrix(mutation, regs), "negative control accepted")
            controls += 1
        events = programs[orientation]
        cleanup = events.index(["phase", "full_frame_cleanup"]) + 1
        expected = [["scalar", scalar(convert(e)), 1] for e in ops]
        need(events[cleanup:cleanup + len(ops)] == expected, "native/event binding")
        replacement = [["scalar", scalar(convert(e)), 1] for e in changed]
        revised = events[:cleanup] + replacement + events[cleanup + len(ops):]
        old_bill, new_bill = recount(events, 716), recount(revised, 716)
        need(old_bill["real_primitives"] - new_bill["real_primitives"] == 62, "full cost saving")
        need(new_bill["prefix_bits"] <= 192, "local precision allowance")
        need(len(events) == len(revised), "event count changed")
        results[orientation] = dict(before=old_bill, after=new_bill, events=len(events), program_sha256=digest(revised))
    return dict(status="PASS_CK_SINGLE_SCALE_RELOCATION", base_commit="66849e1475c930fd7732b1a0067ffee7e1e95f60", seed=34, source_pins=PINS, search=scan, changed_cleanup_sha256=digest(changed), boundary_registers=regs, boundary_columns_per_orientation=len(regs), controls=controls, programs=results)


if __name__ == "__main__":
    result = run()
    if sys.argv[1:] == ["--emit-certificate"]:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        need(not sys.argv[1:], "usage: verify.py [--emit-certificate]")
        need(result == json.loads((HERE / "CERTIFICATE.json").read_text()), "certificate mismatch")
        print("PASS_CK_SINGLE_SCALE_RELOCATION candidates=1022007 saving=62/62 columns=38/38 controls=6")

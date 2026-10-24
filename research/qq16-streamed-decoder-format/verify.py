#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""All-depth exact format for the literal PR4015 decoder and its producer boundary.

Nicholas Stone, with substantial OpenAI Codex assistance. No predecessor
executable is imported. Native/decoder functional semantics remain inherited.
"""
import argparse
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
WORD = "research/qq16-streaming-recovery/WORD.json"
MEMBER = "t16/global/base/work/complex-nine-native/DATA-PHASES.json"
MEMBER_SHA = "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"
AXES = tuple(1 << j for j in range(73))
F17 = tuple((v, 1) for v in AXES[:17])
F16 = tuple((v, 1) for v in AXES[9:25])


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canon(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def load():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for item in pins["files"]:
        if item["usage"] == "input":
            raw = (ROOT / item["path"]).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == item["sha256"], "source mismatch")
    with tarfile.open(ROOT / ARCHIVE) as tf:
        raw = tf.extractfile(MEMBER).read()
    need(hashlib.sha256(raw).hexdigest() == MEMBER_SHA, "phase source mismatch")
    return json.loads((ROOT / WORD).read_text()), json.loads(raw)


def act(columns, vector):
    result = 0
    while vector:
        bit = vector & -vector
        result ^= columns[bit.bit_length() - 1]
        vector ^= bit
    return result


@lru_cache(None)
def phase(terms):
    linear, quadratic = [0]*73, [0]*73
    for v, c in terms:
        bits = [j for j in range(73) if v >> j & 1]
        for j in bits:
            linear[j] = (linear[j] + c) % 4
            if c % 2:
                for k in bits:
                    if k > j:
                        quadratic[j] ^= 1 << k
    return tuple(linear), tuple(quadratic)


def tidy(terms):
    counts = Counter()
    for v, c in terms:
        counts[v] += c
    return tuple((v, c % 4) for v, c in sorted(counts.items()) if c % 4 and v)


def geometry(data):
    need(data["m"] == 73 and len(data["recipes"]) == 112, "source geometry")
    labels, maps = [], {}
    for p, record in enumerate(data["recipes"]):
        q = record["q"]
        need(record["port"] == p and 0 < q < 512, "source label")
        labels.append(q)
        basis = (q, *record["idle_children"][0]["orthogonal_axes"][:8])
        need(all(((u & v).bit_count() % 2) == (i == j)
                 for i, u in enumerate(basis) for j, v in enumerate(basis)), "chart basis")
        for stage in (1, 2):
            swaps = [basis[j+1] ^ AXES[9+8*(stage-1)+j] for j in range(8)]
            columns = tuple(v ^ act(swaps, sum(((v & s).bit_count() % 2) << j
                                               for j, s in enumerate(swaps))) for v in AXES)
            need(tuple(act(columns, v) for v in columns) == AXES, "owner involution")
            target = F17 if stage == 1 else F16 + ((q, 1),)
            moved = phase(tuple((act(columns, v), c) for v, c in F17))
            desired = phase(target)
            need(moved[1] == desired[1], "bridge quadratic phase")
            delta = tuple((a-b) % 4 for a, b in zip(desired[0], moved[0]))
            need(all(x in (0, 2) for x in delta), "bridge shift phase")
            shift = sum((x//2) << j for j, x in enumerate(delta))
            maps[stage, p] = columns, shift
    # Every signed local native recipe, including the negative affine offset.
    columns_checked = 0
    for q in labels:
        pivot = (q & -q).bit_length()-1
        basis = (q,) + tuple(1 << j for j in range(9) if j != pivot)
        inverse = {act(basis, x): x for x in range(512)}
        need(len(inverse) == 512, "native basis inverse")
        for sign in (1, -1):
            offset = 0 if sign == 1 else q
            for x in range(512):
                y = inverse[x]
                actual = {act(basis, y) ^ offset: (1, 1),
                          act(basis, y ^ 1) ^ offset: (1, -1)}
                need(actual == {x: (1, sign), x ^ q: (1, -sign)}, "native kernel sign")
                columns_checked += 1
    return labels, maps, columns_checked


@dataclass(frozen=True)
class Bound:
    poly: tuple
    grid: int = 0
    slope: int = 0

    def plus(self, other):
        if not self.poly:
            return other
        if not other.poly:
            return self
        size = max(len(self.poly), len(other.poly))
        return Bound(tuple((self.poly[j] if j < len(self.poly) else 0) +
                           (other.poly[j] if j < len(other.poly) else 0)
                           for j in range(size)), max(self.grid, other.grid),
                     max(self.slope, other.slope))

    def scale(self, c):
        if not self.poly or not c:
            return ZERO
        n = abs(c.numerator)
        need(c.denominator & (c.denominator-1) == 0, "dyadic coefficient")
        valuation = (n & -n).bit_length()-1
        return Bound(tuple(abs(c)*x for x in self.poly),
                     self.grid+c.denominator.bit_length()-1-valuation, self.slope)

    def tensor_line(self, multiplier, halved):
        if not self.poly:
            return ZERO
        return Bound((Q(0),) + tuple(multiplier*x for x in self.poly),
                     self.grid+int(halved), self.slope+1)

    def record(self):
        return [list(map(str, self.poly)), self.grid, self.slope]


ZERO, ONE = Bound(()), Bound((Q(1),))


def analyze(word, labels, maps):
    borrowed = {s+str(p) for s in ("X", "Y") for p in range(112)}
    outputs = {s+str(p) for s in ("Z", "W") for p in range(112)}
    state = {n: ONE for n in borrowed}
    frames = {n: F17 + (((labels[int(n[1:])], -1),) if n[0] == "Y" else ()) for n in borrowed}
    active, initialized = set(), set()
    counts, peak, degree, grid, slope = Counter(), Q(1), 0, 0, 0
    peak_site, observations, checkpoints = [-1, "entry"], [], []
    max_private = 0

    def observe(value, i, label):
        nonlocal peak, degree, grid, slope, peak_site
        observations.append([i, label, value.record()])
        if value.poly:
            degree = max(degree, len(value.poly)-1)
            grid, slope = max(grid, value.grid), max(slope, value.slope)
            magnitude = sum(value.poly)
            if magnitude > peak:
                peak, peak_site = magnitude, [i, label]

    def read(n):
        need(n in state and n in borrowed | outputs | active, "uninitialized read: " + n)
        return state[n]

    for i, e in enumerate(word):
        op = e[0]
        counts[op] += 1
        if op == "begin":
            need(not active and e[2] in (8, 16), "private allocation")
            active = {s+str(k) for s in ("F", "G")[:e[2]//8] for k in range(8)}
            max_private = max(max_private, len(active))
        elif op == "end":
            need(len(active) == e[2] and all(state.get(n) == ZERO and frames.get(n) == ()
                                           for n in active), "private zero/identity return")
            for n in active:
                del state[n], frames[n]
            active = set()
        elif op == "clear":
            need(e[1] in outputs | active, "CLEAR ownership")
            f = e[2]
            if f in ("current", "wide"):
                frame = F17
            elif f == "query2":
                frame = F16
            elif f == "identity":
                frame = ()
            else:
                need(f.startswith("hole") and 0 <= int(f[4:]) < 112, "clear frame")
                frame = F17 + ((labels[int(f[4:])], -1),)
            state[e[1]], frames[e[1]] = ZERO, tidy(frame)
            initialized.add(e[1]); observe(ZERO, i, "clear")
        elif op == "add":
            dst, src, c = e[1], e[2], Q(e[3])
            need(dst in outputs | active and dst != src, "ADD ownership")
            need(c in (1, -1, Q(1, 4), Q(-1, 4)), "ADD coefficient")
            left, right = read(dst), read(src)
            need(phase(frames[dst]) == phase(frames[src]), "ADD frame mismatch at " + str(i) + " " + str(e))
            observe(right, i, "product-copy")
            term = right.scale(c)
            observe(term, i, "product-result")
            state[dst] = left.plus(term); observe(state[dst], i, "add")
            counts["negative_ADD"] += int(c < 0)
            counts["quarter_ADD"] += int(c.denominator == 4)
        elif op == "line":
            dst, p, sign = e[1:]
            need(not active and dst in outputs and type(p) is int and
                 0 <= p < 112 and sign in (-1, 1), "native ownership/schema")
            value = read(dst)
            observe(value, i, "right-monomial")
            observe(value.tensor_line(2, False), i, "native-pair")
            observe(value.tensor_line(4, False), i, "native-cross")
            state[dst] = value.tensor_line(2, True)
            observe(state[dst], i, "native-output")
            observe(state[dst], i, "left-monomial")
            frames[dst] = tidy(frames[dst] + ((labels[p], sign),))
        elif op == "map":
            dst, stage, p, inv = e[1:]
            need(not active and dst in outputs and (stage, p) in maps and type(inv) is bool,
                 "map ownership/schema")
            observe(read(dst), i, "cover-map")
            columns, shift = maps[stage, p]
            if inv:
                shift = act(columns, shift)
            frames[dst] = tidy(tuple((act(columns, v), c) for v, c in frames[dst]) +
                                tuple((v, 2) for v in AXES if shift & v))
        elif op == "checkpoint":
            need(not active and outputs <= state.keys(), "checkpoint state")
            checkpoints.append([i, max(sum(state[n].poly) for n in outputs)])
        else:
            raise ValueError("unknown instruction")
    need(not active and outputs <= initialized, "complete output allocation")
    need(all(state[n] == ONE for n in borrowed), "borrowed state changed")
    need(all(phase(frames[n]) == phase(F17) for n in outputs), "output frame")
    bits = 0
    while 2**bits < peak:
        bits += 1
    base_ops = (4*counts["add"] + 2*counts["negative_ADD"] + 2*counts["quarter_ADD"]
                + 2*counts["clear"] + 8*counts["line"] + 2)
    fused_with_covers = (2*counts["add"] + 2*counts["quarter_ADD"] + 2*counts["clear"]
                         + 12*counts["line"] + 4*counts["map"])
    result = {
        "events": len(word), "counts": dict(sorted(counts.items())),
        "observations": len(observations), "peak_polynomial_at_one": str(peak),
        "peak_site": peak_site, "polynomial_degree": degree,
        "grid_intercept": grid, "grid_slope": slope, "range_bits": bits,
        "standalone_width_offset": grid+bits+1, "standalone_width_slope": slope+degree,
        "composed_grid_intercept": 71+grid, "composed_grid_slope": 19+slope,
        "composed_width_offset": 215+grid+bits,
        "composed_width_slope": 38+slope+degree,
        "borrowed_unchanged": len(borrowed), "output_banks": len(outputs),
        "private_peak": max_private, "checkpoints": [[i, str(v)] for i, v in checkpoints],
        "decoder_wordops_per_N": [base_ops, 10*counts["line"]],
        "decoder_wordops_constant": 12, "decoder_cover_transfers_per_N": 4*counts["map"],
        "pr4109_fused_reference_fixed_with_covers_per_N": fused_with_covers,
        "unfused_reference_fixed_with_covers_per_N": base_ops+4*counts["map"],
        "protocol_difference_fixed_per_N": base_ops+4*counts["map"]-fused_with_covers,
        "decoder_numeric_storage_per_N": 2*(len(borrowed)+len(outputs)+max_private+1),
        "composed_wordops_per_N": [372322+base_ops, 110760+10*counts["line"]],
        "composed_wordops_constant": 24, "composed_cover_transfers_per_N": 2112+4*counts["map"],
        "composed_numeric_storage_per_N": 2*(704+len(outputs)+max_private+1),
        "scratch_scalar_words": 12,
        "trace_sha256": hashlib.sha256(canon(observations).encode()).hexdigest(),
        "one_layer_capacity_sha256": hashlib.sha256(canon([
            [i, label, str(sum(map(Q, value[0]))), value[1] if value[0] else 0]
            for i, label, value in observations]).encode()).hexdigest(),
    }
    return result, observations


def compute():
    word, data = load()
    producer = json.loads((ROOT / "research/qq16-all-depth-producer-grid/RESULT.json").read_text())
    expected = {"grid_intercept_at_one": 71, "grid_slope": 19,
                "range_bits_at_one": 143, "range_slope": 19,
                "signed_width_P_plus_at_one": 215, "signed_width_slope": 38,
                "tensor_constant_wordops_per_N": 372322, "tensor_linear_wordops_per_N": 110760,
                "cover_transfers_per_N": 2112, "scalar_scratch_words": 12}
    need(all(producer[k] == v for k, v in expected.items()), "producer boundary constants")
    labels, maps, columns = geometry(data)
    result, _ = analyze(word, labels, maps)
    prior = json.loads((ROOT / "research/qq16-paired-precision/RESULT.json").read_text())
    need(prior["exact_format"]["q"] == "h*2^(-9-3t)" and
         prior["exact_format"]["signed_component_bits"] == "P+28+6t" and
         prior["conditional_producer_composition"]["joint_q"] == "h*2^(-80-22t)" and
         prior["conditional_producer_composition"]["joint_width"] == "P+242+44t",
         "published common-format comparison")
    result.update(status="PASS_QQ16_STREAMED_DECODER_FORMAT", native_basis_columns=columns,
                  owner_maps_checked=len(maps), new_supplier_or_kappa=False)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    result = compute()
    if args.write:
        with args.write.open("x") as out:
            out.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        need(canon(result) == canon(json.loads((HERE / "RESULT.json").read_text())), "receipt mismatch")
    print(result["status"], "decoder_guard=9+3t", "composed_guard=80+22t", "width=P+242+44t")


if __name__ == "__main__":
    main()

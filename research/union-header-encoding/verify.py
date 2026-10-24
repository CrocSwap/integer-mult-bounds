#!/usr/bin/env python3
"""Source-bound header audit. Standard library, exact acceptance arithmetic.

Mihir Srivastava with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from header import Layout, bits, require

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE = ROOT / "research/unconditional-batched-crt"


def authenticate():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    checked = []
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        data = (ROOT / row["path"]).read_bytes()
        require(hashlib.sha256(data).hexdigest() == row["sha256"], "source hash: " + row["path"])
        checked.append(row["path"])
    return checked


def width_bound():
    ledger = json.loads((SOURCE / "evidence/composition-controls.json").read_text(encoding="utf-8"))
    beta = Fraction(ledger["parameters"]["beta"])
    delta, q = 1-beta, 10**30
    require(delta == Fraction(3, q), "actual beta binding")
    require(Fraction(ledger["side_slacks"]["group_headers"]) == delta, "header slack binding")
    gaussian = (SOURCE / "GAUSSIAN.md").read_text(encoding="utf-8")
    require("L=2^ceil(400log2 p)" in gaussian, "actual core-side binding")
    require("retain every coarse coordinate as a complete spectator" in gaussian, "coarse context binding")
    schedule = (SOURCE / "vendor/UNION-SCHEDULE.md").read_text(encoding="utf-8")
    require("ordinal k of its source row" in schedule and "prefix fields of consecutive records" in schedule,
            "caller field binding")
    # For t=log2(p), H/p <= 810*t*2^(-delta*t).
    # Its derivative is negative when delta*t*ln(2)>1; ln(2)>1/2.
    t0 = 40*q
    require(delta > 0 and delta*t0 == 120, "cutoff exponent")
    require(810*t0 < 2**115, "cutoff coefficient")
    require(1620*t0 < 2**116, "rounded-up group cutoff coefficient")
    require(delta*t0/2 > 1, "monotone tail")
    require(Fraction(810*t0, 2**120) < Fraction(1, 32), "header cutoff")
    cases = 0
    for p in range(2, 257):
        h = (p**400-1).bit_length()  # ceil(log2(p**400)), no floating point
        require(2**(h-1) < p**400 <= 2**h, "exact core bits")
        for g in (1, 2, 3, 7, 16, 31, 64, 127):
            b = g.bit_length()
            H = 2*g*h + g + 2*b + 2
            require(H <= 2*g*h + 5*g, "noncoordinate field bound")
            # t > (h-1)/400; verify 2h+5 <= 810*(h-1)/400.
            require(400*(2*h+5) <= 810*(h-1), "conservative exact comparison")
            cases += 1
    return {"beta": str(beta), "delta": str(delta), "core_log2_coefficient": 400,
            "header_formula": "2*g*h + g + 2*ceil(log2(g+1)) + 2",
            "upper_bound": "810*p^beta*log2(p)", "cutoff_log2_p": str(t0),
            "cutoff_upper_ratio": str(Fraction(810*t0, 2**120)),
            "ratio_below": "1/32", "rounded_up_group_ratio_below": "1/16",
            "exact_finite_width_cases": cases}


def codec_cases():
    checked = active = 0
    for g, L in ((1, 2), (1, 3), (1, 4), (2, 2), (2, 3)):
        subsets = [tuple(i for i in range(L) if mask >> i & 1) for mask in range(1 << L)]
        for E in itertools.product(subsets, repeat=g):
            layout, seen = Layout(L, E), set()
            for x in itertools.product(range(L), repeat=g):
                encoded = layout.encode(x)
                require(encoded not in seen, "coordinate collision")
                seen.add(encoded)
                record = layout.decode(encoded)
                require(record.coordinates == x, "coordinate round trip")
                expected_flags = tuple(i for i in range(g) if x[i] in E[i])
                require(record.count == len(expected_flags), "split count")
                for r, f in enumerate(expected_flags):
                    tagged = layout.retag(encoded, r)
                    decoded = layout.decode(tagged, r)
                    require(decoded.tag == f, "rth flag extraction")
                    require(layout.line_key(tagged, r) == (x[:f], E[f].index(x[f])), "prefix/ordinal key")
                    require((decoded.count > r+1) == (len(expected_flags) > r+1), "keep bit")
                    active += 1
                checked += 1
    for h in (63, 64, 65, 400, 1200):
        L = 1 << h
        layout = Layout(L, ((0, L-1), (1, L//2), ()))
        for x in ((L-1, L//2, L-2), (0, 1, 0)):
            require(layout.decode(layout.encode(x)).coordinates == x, "large header round trip")
            checked += 1
    return {"round_trips": checked, "active_round_headers": active, "maximum_coordinate_bits": 1200}


def rejection_controls():
    rejected = []
    def rejects(name, action):
        try:
            action()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("control accepted: " + name)
    layout = Layout(3, ((0, 2), (1, 2), (2,)))
    original = layout.encode((2, 1, 0))
    def change(field, value, width):
        i = layout.offsets[field]
        return original[:i] + bits(value, width) + original[i+width:]
    rejects("truncated", lambda: layout.decode(original[:-1]))
    rejects("extra_bit", lambda: layout.decode(original+"0"))
    rejects("record_marker", lambda: layout.decode("00"+original[2:]))
    rejects("nonbinary", lambda: layout.decode("x"+original[1:]))
    rejects("coordinate_overflow", lambda: layout.decode(change("coordinates", 3, layout.h)))
    rejects("wrong_flag", lambda: layout.decode(change("flags", 0, 1)))
    rejects("wrong_ordinal", lambda: layout.decode(change("ordinals", 0, layout.h)))
    rejects("wrong_count", lambda: layout.decode(change("count", 1, layout.b)))
    rejects("unflagged_tag", lambda: layout.decode(change("tag", 2, layout.b)))
    rejects("wrong_round_tag", lambda: layout.decode(layout.retag(original, 0), 1))
    rejects("inactive_round", lambda: layout.retag(original, 2))
    rejects("unsorted_boundary", lambda: Layout(3, ((2, 0),)))
    rejects("duplicate_boundary", lambda: Layout(3, ((0, 0),)))
    i = layout.offsets["ordinals"] + 2*layout.h
    rejects("inactive_ordinal", lambda: layout.decode(original[:i]+bits(1, layout.h)+original[i+layout.h:]))
    same = Layout(4, ((0, 1), (2, 3)))
    a, b = same.retag(same.encode((0, 2)), 1), same.retag(same.encode((1, 2)), 1)
    require(same.line_key(a, 1)[1] == same.line_key(b, 1)[1], "omitted prefix collision fixture")
    require(same.line_key(a, 1) != same.line_key(b, 1), "prefix separates distinct lines")
    # The same local coordinate in two coarse contexts is deliberately not
    # globally unique. Keeping per-context stream boundaries is necessary.
    context_records = [("core-A", same.encode((0, 2)), 7, 2),
                       ("core-B", same.encode((0, 2)), 7, 3)]
    local_keys = {row[1] for row in context_records}
    global_keys = {(row[0], row[1]) for row in context_records}
    require(len(local_keys) == 1 and len(global_keys) == 2, "context keys collapse without boundary")
    require([row[2]*row[3] for row in context_records] == [14, 21], "distinct coarse-page actions")
    nonpolynomial = []
    for k in range(1, 9):
        p, g, h = 2**(2*k), 2**k, 2**k
        H = 2*g*h + g + 2*g.bit_length() + 2
        require(H > 2*p, "nonpolynomial core defeats sublinear conclusion")
        nonpolynomial.append({"k": k, "p": p, "header_bits": H})
    return {"rejections": rejected, "prefix_collision_without_prefix": True,
            "distinct_contexts_can_share_header": True, "nonpolynomial_side_counterexamples": nonpolynomial}


def serialized_schedule():
    path = ROOT / "research/pr4100-union-head-travel/verify.py"
    spec = importlib.util.spec_from_file_location("pinned_union_schedule", path)
    source = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(source)
    original_tape, rows = source.Tape, []
    for g, L, sizes, seed in ((1, 4, [2], 11), (2, 5, [2, 3], 13),
                              (3, 4, [2, 3, 2], 21), (4, 3, [1, 2, 2, 1], 5),
                              (4, 3, [3, 3, 3, 3], 7), (5, 2, [1]*5, 3)):
        rng = random.Random(seed)
        layout = Layout(L, [sorted(rng.sample(range(L), n)) for n in sizes])
        source.RW = 128 + layout.width
        counters = {"writes": 0, "decodes": 0}
        class Serialized:
            def __init__(self, coordinates, value):
                self.header = layout.encode(coordinates)
                require(abs(value).bit_length()+1 <= 128, "finite payload width")
                self.value = value
            def __iter__(self):
                yield self[0]
                yield self[1]
            def __getitem__(self, index):
                if index == 0:
                    counters["decodes"] += 1
                    return layout.decode(self.header).coordinates
                if index == 1:
                    return self.value
                raise IndexError(index)
        class SerializedTape(original_tape):
            def write(self, value):
                if self.w == source.RW:
                    x, payload = value
                    value = Serialized(x, payload)
                    counters["writes"] += 1
                return super().write(value)
        source.Tape = SerializedTape
        st = source.run(g, L, sizes, seed)
        require(st["ok"], "serialized run differs from exact Kronecker reference")
        require(st["streamed"] == st["sumF"] == sum(sizes)*L**(g-1), "visit identity")
        require(st["union"] <= source.union_bound(st), "rescaled predecessor movement bound")
        require(st["dense"] <= 6*st["V"]*source.RW + 4*st["V"], "rescaled dense bound")
        rows.append({"g": g, "L": L, "sizes": sizes, "seed": seed,
                     "header_bits": layout.width, "payload_bits": 128, "record_bits": source.RW,
                     "records": st["V"], "visits": st["sumF"], "lines": st["lines"],
                     "record_writes": counters["writes"], "header_decodes": counters["decodes"],
                     "union_moves": st["union"], "union_bound": source.union_bound(st)})
    source.Tape = original_tape
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    checked = authenticate()  # before importing predecessor code
    result = {"source_inputs": checked, "width": width_bound(), "codec": codec_cases(),
              "controls": rejection_controls(), "schedule": serialized_schedule(),
              "new_kappa": False, "full_tape_compiler": False}
    path = PACKAGE / "RESULT.json"
    if args.write_result:
        path.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n", encoding="utf-8", newline="\n")
    else:
        require(result == json.loads(path.read_text(encoding="utf-8")), "committed result mismatch")
    print("PASS_UNION_HEADER_ENCODING " + json.dumps({
        "round_trips": result["codec"]["round_trips"],
        "active_headers": result["codec"]["active_round_headers"],
        "rejections": len(result["controls"]["rejections"]),
        "source_schedule_cases": len(result["schedule"]),
        "source_schedule_header_decodes": sum(r["header_decodes"] for r in result["schedule"]),
        "cutoff_log2_p": result["width"]["cutoff_log2_p"], "no_new_kappa": True}, sort_keys=True))


if __name__ == "__main__":
    main()

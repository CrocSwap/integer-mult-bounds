#!/usr/bin/env python3
"""Exact minimum-macro scale-placement census. No solver or network.

Ross Richardson with substantial OpenAI Codex assistance, Apache-2.0.
PR681/PR696/PR922/PR924 sources and authors are credited in README.md.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SEED = 27


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text())


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def source_check():
    pins = read(HERE / "SOURCES.json")
    for path, expected in pins["files"].items():
        p = Path(path)
        need(not p.is_absolute() and ".." not in p.parts, "unsafe source path")
        need(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == expected, "source pin: " + path)
    return pins


def exponent(q):
    n, d = abs(q.numerator), q.denominator
    need(n > 0 and n & (n - 1) == 0 and d & (d - 1) == 0,
         "not a signed power of two")
    return n.bit_length() - d.bit_length()


def validate_word(word):
    need(isinstance(word, list) and word, "empty word")
    frame = [390, 74, 44, 30]
    for op in word:
        need(isinstance(op, list) and op[0] in ("add", "scale"), "unknown gate")
        need(len(op) == (6 if op[0] == "add" else 5), "gate shape")
        need(op[-1] == frame and all(type(x) is int for x in op[-1]), "wrong frame")
        need(all(type(x) is int for x in op[1:-1]), "integer gate fields required")
        need(0 <= op[1] < 8, "target range")
        if op[0] == "add":
            need(0 <= op[2] < 8 and op[1] != op[2], "source alias/range")
        need(op[-2] != 0, "zero denominator")
        exponent(Q(op[-3], op[-2]))


def model(word):
    validate_word(word)
    uses, old = [0] * 8, [0] * 8
    totals, records, old_positions = [Q(1)] * 8, [], {}
    for op in word:
        if op[0] == "scale":
            r, q = op[1], Q(op[2], op[3])
            old[r] += exponent(q)
            totals[r] *= q
            old_positions[r] = uses[r]
        else:
            t, s = op[1:3]
            records.append((t, s, uses[t], uses[s], exponent(Q(op[3], op[4])) - old[t] + old[s]))
            uses[t] += 1
            uses[s] += 1
    active = [r for r in range(8) if exponent(totals[r])]
    return uses, totals, records, old_positions, active


def census(word):
    uses, totals, records, old_positions, active = model(word)
    need(len(records) == 26 and len(word) == 32, "wrong topology")
    need(totals == list(map(Q, [2, 2, 2, 1, 1, -1, 2, -2])), "wrong wire totals")
    base = sum(abs(exponent(q)) + (q < 0) for q in totals)
    tables = []
    for t, s, ti, si, e0 in records:
        table = []
        for pt in range(uses[t] + 1):
            row = []
            for ps in range(uses[s] + 1):
                e = e0 + exponent(totals[t]) * (pt <= ti) - exponent(totals[s]) * (ps <= si)
                row.append(2 if e == 0 else 3 + abs(e))
            table.append(row)
        tables.append((t, s, table))
    # Seed changes enumeration/tie order, not the domain or proof.
    cut = SEED % len(active)
    order = active[cut:] + active[:cut]
    histogram, best, winners = Counter(), None, []
    for values in itertools.product(*(range(uses[r] + 1) for r in order)):
        positions = [0] * 8
        for r, value in zip(order, values):
            positions[r] = value
        price = base + sum(table[positions[t]][positions[s]] for t, s, table in tables)
        histogram[price] += 1
        if best is None or price < best:
            best, winners = price, []
        if price == best:
            winners.append({str(r): positions[r] for r in active})
    sign_wire = 5
    multiplicity = uses[sign_wire] + 1
    return {
        "fixed_additions": len(records), "minimum_macros": len(records) + sum(q != 1 for q in totals),
        "wire_uses": uses, "wire_net_scales": list(map(str, totals)), "enumeration_order": order,
        "magnitude_placements": sum(histogram.values()), "sign_only_wire": sign_wire,
        "sign_placements_per_magnitude": multiplicity,
        "complete_placements": sum(histogram.values()) * multiplicity,
        "minimum_primitives": best, "optimal_magnitude_positions": winners,
        "optimal_complete_placements": len(winners) * multiplicity,
        "histogram_magnitude": {str(k): v for k, v in sorted(histogram.items())},
        "histogram_complete": {str(k): v * multiplicity for k, v in sorted(histogram.items())},
        "stopping_rule": "complete Cartesian product, no timeout or heuristic pruning",
        "old_positions": {str(k): v for k, v in sorted(old_positions.items())},
    }


def construct(word, positions):
    uses, totals, _, _, _ = model(word)
    needed = {r for r, q in enumerate(totals) if q != 1}
    need(set(positions) == needed, "placement inventory")
    need(all(type(p) is int and 0 <= p <= uses[r] for r, p in positions.items()), "placement range")
    seen, old, new, done, out = [0] * 8, [Q(1)] * 8, [Q(1)] * 8, set(), []
    frame = word[0][-1]

    def place(r):
        if r in needed and r not in done and positions[r] == seen[r]:
            q = totals[r]
            out.append(["scale", r, q.numerator, q.denominator, frame])
            new[r] = q
            done.add(r)

    for op in word:
        if op[0] == "scale":
            old[op[1]] *= Q(op[2], op[3])
        else:
            t, s = op[1:3]
            place(t)
            place(s)
            q = Q(op[3], op[4]) * (new[t] / old[t]) / (new[s] / old[s])
            out.append(["add", t, s, q.numerator, q.denominator, frame])
            seen[t] += 1
            seen[s] += 1
    for r in range(8):
        place(r)
    need(done == needed and new == old, "unrestored boundary gauge")
    validate_word(out)
    return out


def variants(word):
    def inverse(w):
        out = []
        for op in reversed(w):
            e = op.copy()
            if e[0] == "add":
                e[3] = -e[3]
            else:
                e[2], e[3] = e[3], e[2]
            out.append(e)
        return out

    def dual(w):
        out = []
        for op in w:
            e = op.copy()
            if e[0] == "add":
                e[1], e[2], e[3] = e[2], e[1], -e[3]
            else:
                e[2], e[3] = e[3], e[2]
            out.append(e)
        return out
    return {"forward": word, "inverse": inverse(word),
            "inverse_transpose": dual(word), "transpose": dual(inverse(word))}


def lowerer():
    spec = importlib.util.spec_from_file_location("pinned_pr696", ROOT / "research/complex-dyadic-lowering/lower.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.lower


def primitives(word, lower):
    validate_word(word)
    out = []
    for op in word:
        e = (["add", ["L", op[1]], ["L", op[2]], op[3], op[4]] if op[0] == "add"
             else ["scale", ["L", op[1]], op[2], op[3]])
        out.extend(lower(e))
    return out


def replay(ops):
    regs = [("L", r) for r in range(8)] + [("W", 0)]
    rows = {r: [Q(i == j) for j in range(9)] for i, r in enumerate(regs)}
    peak, depth = Q(1), 0
    for op in ops:
        tag, t = op[:2]
        if tag == "clear":
            rows[t] = [Q(0)] * 9
        elif tag == "copy":
            rows[t] = rows[op[2]].copy()
        elif tag in ("double", "halve", "negate"):
            q = {"double": Q(2), "halve": Q(1, 2), "negate": Q(-1)}[tag]
            rows[t] = [q * x for x in rows[t]]
        elif tag in ("add", "subtract"):
            sign = 1 if tag == "add" else -1
            rows[t] = [x + sign * y for x, y in zip(rows[t], rows[op[2]])]
        else:
            raise ValueError("unknown primitive")
        peak = max(peak, sum(map(abs, rows[t])))
        depth = max(depth, *(x.denominator.bit_length() - 1 for x in rows[t]))
    need(rows[("W", 0)] == [0] * 9, "coefficient work not cleared")
    return [rows[r] for r in regs], {"primitives": len(ops), "row_l1_peak": str(peak), "fractional_bits": depth}


def verify_winners(word, result):
    lower = lowerer()
    predecessor = read(ROOT / "research/complex-factory5-resynthesis/CIRCUIT.json")["replacement"]
    reference = {}
    for name, variant in variants(word).items():
        reference[name], _ = replay(primitives(variant, lower))
        old_rows, _ = replay(primitives(variants(predecessor)[name], lower))
        need(reference[name] == old_rows, "PR924 map differs from PR681: " + name)
    receipt = []
    for winner in result["optimal_magnitude_positions"]:
        for sign_position in range(result["sign_placements_per_magnitude"]):
            positions = {int(r): p for r, p in winner.items()}
            positions[5] = sign_position
            candidate = construct(word, positions)
            evidence = {}
            for name, variant in variants(candidate).items():
                rows, stats = replay(primitives(variant, lower))
                need(rows == reference[name], "changed exact operator: " + name)
                need(stats["primitives"] == result["minimum_primitives"], "cost mismatch")
                evidence[name] = stats
            receipt.append({"positions": {str(r): p for r, p in sorted(positions.items())},
                            "word_sha256": digest(candidate), "orientations": evidence})
    return receipt


def complete_cost_floor(result):
    # The inherited invoice fixes C and charges 16*C per extra emitted macro.
    # Even eliminating every primitive in all 28 windows cannot pay for ONE
    # extra macro anywhere. Thus this also covers nonuniform window choices.
    compiler = 64 * 74 ** 3
    blocks = read(ROOT / "research/complex-factory5-resynthesis/BLOCKS.json")
    need([b["index"] for b in blocks] == list(range(14)), "factory block inventory")
    need(all(len(set(b["registers_before_112_port_restriction"])) == 8
             and b["exit_frames"] == [b["frame"]] * 8 for b in blocks), "factory block interface")
    all_window_primitives = len(blocks) * 2 * 2 * result["minimum_primitives"]
    penalty = 16 * compiler
    need(penalty > all_window_primitives, "extra macros may help complete bill")
    return {"compiler_constant": compiler, "adapter_units_per_extra_macro": 16,
            "extra_macro_penalty": penalty, "all_28_window_real_primitives": all_window_primitives,
            "strict_penalty_margin": penalty - all_window_primitives,
            "scope": "fixed inherited invoice, 26 ordered additions, signed dyadic diagonal gauges; no new kappa"}


def run():
    source_check()
    word = read(HERE / "sources/PR924-COMPOSITION.json")["replacement"]
    result = census(word)
    need(result["minimum_macros"] == 32 and result["minimum_primitives"] == 73, "frontier changed")
    result["winner_checks"] = verify_winners(word, result)
    result["complete_cost_floor"] = complete_cost_floor(result)
    result["status"] = "PASS_FACTORY_SCALE_FRONTIER"
    result["new_kappa"] = False
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a new receipt, refusing overwrite")
    args = parser.parse_args()
    result = run()
    if args.write:
        with args.write.open("x") as f:
            json.dump(result, f, indent=2, sort_keys=True)
            f.write("\n")
    else:
        need(result == read(HERE / "EXPECTED.json"), "deterministic receipt differs")
    print("PASS_FACTORY_SCALE_FRONTIER magnitude=39424 complete=315392 macros=32 minimum=73 winners=8 no_new_kappa")


if __name__ == "__main__":
    main()

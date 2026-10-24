"""Check the one-pair data stock and a paid terminal construction."""

from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]


def need(condition, label):
    if not condition:
        raise ValueError(label)


def add(row, other, coefficient=Q(1)):
    for key, value in other.items():
        row[key] = row.get(key, 0) + coefficient * value
        if not row[key]:
            del row[key]


def rank(rows):
    pivots = {}
    for value in rows:
        while value:
            p = value.bit_length() - 1
            if p in pivots:
                value ^= pivots[p]
            else:
                pivots[p] = value
                break
    return len(pivots)


def price(kind, value):
    a, b = abs(value.numerator), value.denominator
    need(a > 0 and b & (b - 1) == 0, "Nonzero dyadic coefficient")
    if kind == "scale":
        need(a & (a - 1) == 0, "Unit scale")
        return 2 * (abs(a.bit_length() - b.bit_length()) + (value < 0))
    return 2 * (3 + a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1)


def local_audit(word, response, direction):
    need(len(word["start"]) == len(word["final"]) == 632, "Frozen role count")
    need(word["start"][224:] == word["final"][224:],
         "Omitted helper slots have unchanged physical frame")
    frames = word["frames"]
    current = word["start"][:224]
    rows = [{i: Q(1)} for i in range(224)]
    widths, profile = [0] * 224, Counter()
    scalar = 0
    peak = Q(1)
    for event in word["events"]:
        if event[0] == "native":
            _, target, old, new, width, key = event
            need(0 <= target < 224 and current[target] == old, "Data-only native target")
            need(rank(frames[old] + frames[new]) == len(frames[new]), "Nested productive path")
            need(width == len(frames[new]) - len(frames[old]) > 0, "Exact positive rank")
            need(word["native_recipes"][key]["rank"] == width, "Literal native recipe")
            current[target] = new
            widths[target] += width
            profile[width] += 1
        else:
            need(event[0] == "scalar", "No private or allocation event")
            op, frame = event[1:]
            kind, target = op[:2]
            need(0 <= target < 224 and current[target] == frame, "Data-only scalar target")
            if kind == "scale":
                value = Q(*op[2:])
                rows[target] = {i: value * c for i, c in rows[target].items()}
            else:
                need(kind == "add", "Only reversible ADD and SCALE")
                origin = op[2]
                need(0 <= origin < 224 and origin != target and current[origin] == frame,
                     "Data-only scalar source in the same exact frame")
                value = Q(*op[3:])
                add(rows[target], rows[origin], value)
            scalar += price(kind, value)
            peak = max(peak, sum(map(abs, rows[target].values())))
    expected = [{i: Q(1)} for i in range(224)]
    for t, row in enumerate(response):
        if direction == "forward":
            add(expected[112 + t], row)
        else:
            for s, value in row.items():
                add(expected[s], {112 + t: -value})
    need(rows == expected and current == word["final"][:224], "All 224 independent input columns")
    need(widths == [8] * 224, "Every retained data path has rank eight")
    need(len(word["endpoint_adapters"]) == 224, "Only the 224 data endpoint maps")
    need(all(r["role"] in ("source", "target") and 0 <= r["port"] < 112
             for r in word["endpoint_adapters"]), "No endpoint helper operand")
    need(profile == {1: 160, 2: 48, 5: 48, 7: 112, 8: 64}, "Complete native profile")
    need(scalar == 3032 and peak == 6, "Literal scalar invoice and prefix bound")
    return {"profile": dict(sorted(profile.items())), "scalar": scalar,
            "children": sum(profile.values()), "rank_mass": sum(widths),
            "maximum_array_norm_bound": str(peak), "checked_input_columns": 224,
            "helper_operands": 0, "owned_fields": 0,
            "omitted_helper_start_ranks": dict(sorted(Counter(
                len(frames[f]) for f in word["start"][224:]).items()))}


def reduce_word(word):
    out = []
    for letter in word:
        if out and out[-1] == -letter:
            out.pop()
        else:
            out.append(letter)
    return tuple(out)


def code(row, word):
    result = {}
    for (origin, old), value in row.items():
        add(result, {(origin, reduce_word(tuple(word) + old)): value})
    return result


def controller_audit():
    # The symbols 1,2,3 denote E0,E1,E2; 4 denotes Q.
    x, y = {(0, ()): 1}, {(1, ()): 1}
    add(y, code(x, [1]))
    x = code(x, [1])
    y = code(y, [2])
    add(x, code(y, [-2]), -1)
    x = code(x, [2])
    y = code(y, [3])
    add(y, code(x, [3]))
    x = code(x, [-2])
    need(x == {(1, ()): -1} and y == {(0, (3, 2, 1)): 1}, "Ordered current-cut triple")
    raw_x, raw_y = code(y, [4]), {key: -value for key, value in x.items()}
    need(raw_y == {(1, ()): 1}, "Raw Y endpoint")
    first = code(raw_x, [-4])
    decoded = code(first, [-1, -2, -3])
    final = code(decoded, [4])
    need(final == {(0, (4,)): 1}, "Literal two-line terminal returns the raw X input")
    need(code(first, [-3, -2, -1]) != decoded, "Reject reversed inverse order")
    need(decoded != final, "Reject omission of the final original-input line")
    return {"preterminal": ["-y", "E2 E1 E0 x"],
            "post_old_terminal": ["Q E2 E1 E0 x", "y"],
            "paid_terminal_order": ["Q^-1", "E2^-1", "E1^-1", "E0^-1", "Q"],
            "extra_H1": 224, "H2_fusion_claimed": False,
            "wrong_inverse_order_rejected": True, "missing_final_Q_rejected": True}


def gauge_audit(gauge, response):
    out = []
    for key in ("scalar_word", "inverse_scalar_word"):
        rows = [{i: Q(1)} for i in range(112)]
        cost, peak = 0, Q(1)
        for kind, target, source, coefficient in gauge[key]:
            value = Q(coefficient)
            need(0 <= target < 112 and 0 <= source < 112, "Gauge data stock")
            if kind == "add":
                need(target != source, "Gauge ADD has distinct operands")
                add(rows[target], rows[source], value)
            else:
                need(kind == "scale", "Gauge scalar grammar")
                rows[target] = {i: value * c for i, c in rows[target].items()}
            cost += price(kind, value)
            peak = max(peak, sum(map(abs, rows[target].values())))
        need(rows == response and cost == 2668 and peak <= 4, "Actual E and E inverse scalar words")
        out.append({"word": key, "scalar": cost, "peak": str(peak)})
    return out


def main(out_path):
    pins_path = HERE / "SOURCE-PINS.json"
    pins = json.loads(pins_path.read_bytes())
    sources = {}
    for key, item in pins.items():
        raw = (ROOT / item["path"]).read_bytes()
        if item["kind"] == "gzip":
            raw = gzip.decompress(raw)
        need(sha256(raw).hexdigest() == item["sha256"], "Source pin: " + key)
        sources[key] = raw.decode() if item["kind"] == "text" else json.loads(raw)
    payload = sources["local_payload"]
    response = [{int(i): Q(v) for i, v in row.items()} for row in payload["response"]]
    for i, row in enumerate(response):
        square = {}
        for j, value in row.items():
            need(value == response[j].get(i, 0), "Symmetric local response")
            add(square, response[j], value)
        need(square == {i: Q(1)}, "Exact reciprocal involution")
    local = {provider: {direction: local_audit(word, response, direction)
                       for direction, word in words.items()}
             for provider, words in payload["providers"].items()}
    gauge = gauge_audit(sources["gauge"], response)
    schedule = [e for e in sources["retained_schedule"]["schedule"]
                if e["kind"] == "local" and e["pair"] == 0]
    need(schedule == [{"kind": "local", "stage": s, "pair": 0, "reverse": s == 1}
                      for s in range(3)], "Retained first-pair local order")
    need(sources["current_controller"]["program"] == [
        ["forward", 0], ["code_X", 0, 1], ["code_Y", 1, 1],
        ["backward", 1], ["code_X", 1, 1], ["code_Y", 2, 1],
        ["forward", 2], ["code_X", 1, -1]], "Literal five-code placement")
    views = sources["dimension_views"]["entries"]
    need(len(views) == 336 and {(v["stage"], v["port"]) for v in views}
         == {(s, p) for s in range(3) for p in range(112)}, "Complete D25 records")
    lines = {}
    for v in views:
        route = v["route_columns"]
        need(len(route) == 25 and all(0 < a < 1 << 25 for a in route), "D25 route bounds")
        need(all((a & b).bit_count() % 2 == (i == j)
                 for i, a in enumerate(route) for j, b in enumerate(route)), "Regular cover route")
        need(all(0 <= a < 1 << 25 for a in v["literal_stage_alignment"].values()), "D25 translation bounds")
        if v["stage"] == 0:
            lines[v["port"]] = v["q"]
    need(len(lines) == 112 and all(q and q.bit_count() % 2 for q in lines.values()), "All intrinsic lines")
    for words in payload["providers"].values():
        for word in words.values():
            need(all(word["frames"][word["start"][p]] == [q] for p, q in lines.items()),
                 "The terminal lines are the physical input lines in both providers")
    terminal_lines = []
    for p, q in sorted(lines.items()):
        pivot = (q & -q).bit_length() - 1
        basis = [q] + [1 << i for i in range(25) if i != pivot]
        need(rank(basis) == 25, "Explicit rank-one child address chart")
        terminal_lines.append({"port": p, "q": q, "chart_columns": basis,
                               "positive": "P_chart C_first P_chart^-1",
                               "inverse": "X_q P_chart C_first P_chart^-1"})
    group = 1 << 144
    for i in range(1, 13):
        group *= (1 << (2 * i)) - 1
    local_profile = Counter({1: 160, 2: 48, 5: 48, 7: 112, 8: 64})
    full_profile = Counter({r: 3 * n for r, n in local_profile.items()})
    full_profile[1] += 224
    need(sum(r * n for r, n in full_profile.items()) == 224 * 25, "Safe terminal exhausts rank deficit")
    receipt = {
        "status": "PASS_ONE_PAIR_STOCK_AND_PAID_TERMINAL",
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "source_pins_sha256": sha256(pins_path.read_bytes()).hexdigest(), "sources": pins,
        "local_words": local, "gauge_words": gauge, "controller": controller_audit(),
        "projected_role_count": 224, "omitted_unused_helper_slots": 408,
        "dimension": 25, "stage_calls": schedule, "nonzero_idle_jobs": 0,
        "bridge_jobs": 0, "identity_tail_idle": {"from": 2, "to": 2},
        "cover_order": str(group), "cover_order_bits": group.bit_length(),
        "independent_productive_role_count": str(224 * group),
        "productive_role_count_bits": (224 * group).bit_length(),
        "complete_native_profile_per_cover": dict(sorted(full_profile.items())),
        "preterminal_native_rank": 5376, "complete_native_rank": 5600,
        "complete_native_children": sum(full_profile.values()),
        "scalar_subtotal_local_and_eight_codes": 3 * 3032 + 8 * 2668,
        "native_halving_margin": 25 * 25 - 2 * 8 * 8,
        "prefix_bound_local_and_codes": str(6 ** 3 * 4 ** 8),
        "terminal_line_charts": terminal_lines,
        "phase_scope": "The source packets supply complete native and D25 phase checks. This checker binds their pins and checks scalar, frame, stock and route data; it does not rerun their phase compilers.",
        "scope": "Structural one-pair hosting and a paid exact terminal. Complete finite supplier pricing and a cheaper terminal are not proved. The specified complete profile fails every positive native improvement exponent."
    }
    out_path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=HERE / "CHECKS.json")
    main(parser.parse_args().out)

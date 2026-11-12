"""Exact fixed-port restoration witnesses and source-bound controls. Apache-2.0."""

from argparse import ArgumentParser
from collections import Counter
from hashlib import sha256
from heapq import heappop, heappush
from itertools import product
import json
from pathlib import Path
from runpy import run_path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FIXTURE = "research/clean-connector-per-mask-seede54e/verify.py"
BASELINE = "research/connector-all-tariff-optimum/RESULT.json"
RETARGET = "research/clean-connector-gray-optimum/RESULT.json"
KINDS = "BAFGZ"
MODES = ("closed", "entry_reset", "exit_reset")


def require(ok, detail):
    if not ok:
        raise ValueError(detail)


def json_at(path):
    return json.loads(path.read_text(encoding="utf-8"))


def input_paths():
    pins = {row["path"]: row["sha256"] for row in json_at(HERE / "SOURCES.json")["files"]
            if row["usage"] == "input"}
    require(set(pins) == {FIXTURE, BASELINE, RETARGET}, "unexpected source closure")
    for name, digest in pins.items():
        require(sha256((ROOT / name).read_bytes()).hexdigest() == digest, f"changed input: {name}")


def gray_word(n, mode):
    require(n >= 1 and mode in MODES, "invalid wrapper")
    vertices = [0]
    for i in range(n):
        vertices += [x | (1 << i) for x in reversed(vertices)]
    word = [("F", 0), ("Z" if mode == "entry_reset" else "G", 0)]
    for u, v in zip(vertices, vertices[1:]):
        bit = u ^ v
        require(bit.bit_count() == 1, "nonedge in Gray path")
        word.extend((("B", bit.bit_length() - 1), ("A", v)))
    terminal = vertices[-1]
    require(terminal.bit_count() == 1, "closed Gray path needs one closing toggle")
    word.append(("Z", 0) if mode == "exit_reset" else ("B", terminal.bit_length() - 1))
    return word + [("G", 0), ("F", 0)]


def execute(word, sources, old_z, outputs, backing_w, b_map, a_map, *, zero_owned=True):
    """All child calls use z, never w. Allocation clears arbitrary backing contents."""
    z, w = old_z, (0 if zero_owned else backing_w)
    y = list(outputs)
    resets = 0
    for op, arg in word:
        if op == "B" and 0 <= arg < len(sources):
            z ^= b_map(arg, sources[arg])
        elif op == "A" and 1 <= arg <= len(y):
            y[arg - 1] ^= a_map(arg, z)
        elif op == "F":
            w ^= z
        elif op == "G":
            z ^= w
        elif op == "Z":
            resets += 1
            require(resets <= 1, "second reset")
            z = 0
        else:
            raise ValueError(f"unknown fixed-port operation: {(op, arg)}")
    return z, w, tuple(y)


def counts(word):
    c = Counter(op for op, _ in word)
    return dict(zip(KINDS, (c[op] for op in KINDS)))


def best_singleton(n, prices):
    b, a, f, g, r = prices
    return ((1 << n) - 1) * (a + b) + 2 * f + g + min(b + g, b + r, g + r)


def symbolic_replay():
    total = 0
    for n in range(1, 9):
        targets = tuple(range(1, 1 << n))
        source = tuple(1 << j for j in range(n))
        old = 1 << n
        for mode in MODES:
            word = gray_word(n, mode)
            result = execute(word, source, old, (0,) * len(targets), 0, lambda j, x: x, lambda m, z: z)
            expected = dict(zip(KINDS, (len(targets) + (mode != "exit_reset"), len(targets),
                                       2, 1 + (mode != "entry_reset"), int(mode != "closed"))))
            require(result == (old, 0, targets) and counts(word) == expected, "symbolic wrapper")
            require(Counter(i for op, i in word if op == "A") == Counter(targets), "literal singleton calls")
            total += 1
    return total


def exact_small(n, singleton, prices):
    """Dijkstra over exact coefficients with one distinguished once-read target.

    Other targets may be read any number of times. In the chosen target's row,
    zero means unread: its only legal read produces the required nonzero mask.
    """
    b, a, f, g, r = prices
    masks = tuple(range(1, 1 << n))
    old = 1 << n
    start = (old, 0, (0,) * len(masks), False)
    dist, heap = {start: 0}, [(0, start)]
    while heap:
        cost, state = heappop(heap)
        if cost != dist[state]:
            continue
        z, w, ys, reset = state
        if (z, w, ys) == (old, 0, masks):
            return cost
        edges = [(b, (z ^ (1 << j), w, ys, reset)) for j in range(n)]
        edges.extend(((f, (z, w ^ z, ys, reset)), (g, (z ^ w, w, ys, reset))))
        if not reset and w & old:
            edges.append((r, (0, w, ys, True)))
        for i, m in enumerate(masks):
            if m != singleton or (ys[i] == 0 and z == m):
                dest = ys[:i] + (ys[i] ^ z,) + ys[i + 1:]
                edges.append((a, (z, w, dest, reset)))
        for weight, dest in edges:
            new = cost + weight
            if dest not in dist or new < dist[dest]:
                dist[dest] = new
                heappush(heap, (new, dest))
    raise ValueError("no endpoint in finite state graph")


def exact_controls():
    reports = []
    # The three strict minimizers and a unit tie. Uniform source/readout
    # prices make masks 1 and 3 representatives of both weights at n=2.
    price_vectors = ((2, 5, 3, 7, 20), (2, 5, 3, 7, 1), (7, 9, 2, 3, 1), (1, 1, 1, 1, 1))
    for n, m in ((1, 1), (2, 1), (2, 3)):
        for p in price_vectors:
            found = exact_small(n, m, p)
            require(found == best_singleton(n, p), "small exact optimum mismatch")
            reports.append({"n": n, "required_singleton": m, "prices_B_A_F_G_Z": p, "minimum": found})
    return reports


def fixed_map_control():
    # On these particular singular maps the three A calls can share one
    # connector value. This rebuts an unrestricted fixed-instance lower bound.
    word = [("F", 0), ("G", 0), ("B", 0), ("B", 1), ("A", 1), ("A", 2),
            ("A", 3), ("Z", 0), ("G", 0), ("F", 0)]
    for x, y, old, a, b, c in product(range(4), repeat=6):
        p, q = x & 1, y & 2
        got = execute(word, (x, y), old, (a, b, c), 0,
                      lambda j, v: v & (1 << j), lambda m, v: v & m)
        require(got == (old, 0, (a ^ p, b ^ q, c ^ p ^ q)), "fixed singular-map control")
    require(len(word) == 10 < best_singleton(2, (1,) * 5), "control must be cheaper")
    return 4**6


def dense(rows, value):
    return sum(((r & value).bit_count() & 1) << i for i, r in enumerate(rows))


def fixture_replay():
    source = run_path(str(ROOT / FIXTURE))
    length, masks = source["L"], source["MASKS"]
    require(length == 16 and masks == tuple(range(1, 32)), "fixture identity")
    b_map = lambda j, x: source["permute"](x, source["B_MAPS"][j])
    a_map = lambda m, z: source["apply_output_map"](z, m - 1)
    ones = (1 << length) - 1
    require(all(b_map(j, ones) == ones for j in range(5)) and
            all(a_map(m, ones) == ones for m in masks), "the fixture lost the common identity line")

    b_rows = [tuple(1 << col for col in p) for p in source["B_MAPS"]]
    kernel = source["a_rows"]()
    a_rows = {m: tuple(sum(1 << p[i] for i in range(length) if r & (1 << i)) for r in kernel)
              for m, p in zip(masks, source["Q_MAPS"], strict=True)}

    def expected(xs, old, out):
        images = [dense(r, x) for r, x in zip(b_rows, xs, strict=True)]
        result = list(out)
        for m in masks:
            total = 0
            for j, v in enumerate(images):
                if m & (1 << j):
                    total ^= v
            result[m - 1] ^= dense(a_rows[m], total)
        return old, 0, tuple(result)

    words = {mode: gray_word(5, mode) for mode in MODES}
    rows = 5 + 1 + len(masks) + 1
    for column in range(rows * length):
        inputs = [0] * rows
        inputs[column // length] = 1 << (column % length)
        xs, old, out, backing = inputs[:5], inputs[5], inputs[6:-1], inputs[-1]
        want = expected(xs, old, out)
        for word in words.values():
            got = execute(word, xs, old, out, backing, b_map, a_map)
            require(got == want, f"literal fixture basis column {column}")

    old, out, backing = ones, (0,) * len(masks), ones
    xs = (1, 2, 4, 8, 16)
    want = expected(xs, old, out)
    entry, closed = words["entry_reset"], words["closed"]
    mutants = (("missing save", entry[1:], True),
               ("missing entry reset", entry[:1] + entry[2:], True),
               ("missing close", closed[:-3] + closed[-2:], True),
               ("missing restore", entry[:-2] + entry[-1:], True),
               ("dirty release", entry[:-1], True),
               ("missing allocation zeroing", entry, False))
    for label, word, zero in mutants:
        require(execute(word, xs, old, out, backing, b_map, a_map, zero_owned=zero) != want, label)
    try:
        execute([("Z", 0)] + entry, xs, old, out, backing, b_map, a_map)
    except ValueError as exc:
        require(str(exc) == "second reset", "wrong reset rejection")
    else:
        raise ValueError("second reset accepted")

    ref = json_at(ROOT / RETARGET)
    retained = ref["invoice"]
    n = counts(entry)
    actions = sum(n.values())
    invoice = {k: retained[k] for k in ("shared_map_table_bits", "shared_row_cells",
                                        "mask_control_descriptors", "allocation_release_descriptors",
                                        "fresh_row_cells", "zero_writes")}
    invoice.update(source_updates=n["B"] * length, output_updates=n["A"] * length * 13,
                   wrapper_row_xors=(n["F"] + n["G"]) * length,
                   wrapper_reset_writes=n["Z"] * length, action_descriptors=actions * 13)
    a, b = length * 13 + 13, length + 13
    call_bill = sum(n[op] * (a if op == "A" else b) for op in KINDS)
    profiles = json_at(ROOT / BASELINE)["pareto_profiles"]
    require(len(profiles) == 16 and all(len(v) == 36 for v in profiles), "retained tariff frontier")
    dirty = invoice["shared_map_table_bits"] + invoice["shared_row_cells"]
    dirty += min(sum(v[i] * (b if i < 5 else a) for i in range(36)) for v in profiles)
    price = sum(invoice.values())
    require((call_bill, price, dirty, ref["new_clean_cost"]) == (7895, 35060, 40754, 34944),
            "complete fixed-port tariff comparison")
    require(call_bill == best_singleton(5, (b, a, b, b, b)) < 62 * a + 5 * b,
            "fixture requires a global call-price comparison")
    return {"basis_columns_per_word": rows * length, "fixed_map_identity_line_count": 36,
            "mutations_rejected": len(mutants) + 1, "all_witness_counts": {k: counts(v) for k, v in words.items()},
            "charged_entry_reset_invoice": invoice, "call_bill": call_bill, "total": price,
            "dirty_comparator": dirty, "retargeted_comparator": ref["new_clean_cost"],
            "saving_vs_dirty": dirty - price, "premium_vs_retargeting": price - ref["new_clean_cost"]}


def replay():
    input_paths()
    unit = best_singleton(5, (1,) * 5)
    require(unit == 62 + 5 == 67, "global unit cost with an owned zero row")
    return {"scope": "exact declared fixed-port connector model; no new kappa",
            "symbolic_witnesses": symbolic_replay(), "small_exact_costs": exact_controls(),
            "fixed_singular_counterexample_inputs": fixed_map_control(),
            "unit_with_owned_zero": unit, "unit_original": 74,
            "unit_provision_break_even": 74 - unit, "fixture": fixture_replay()}


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", type=Path, help="write a new exact receipt")
    args = parser.parse_args()
    result = json.dumps(replay(), indent=2, sort_keys=True) + "\n"
    if args.write_result:
        with args.write_result.open("x", encoding="utf-8") as f:
            f.write(result)
    else:
        require((HERE / "RESULT.json").read_text(encoding="utf-8") == result, "changed exact receipt")
    print("PASS_FIXED_PORT_CONNECTOR_RESET unit=67 baseline=74 break_even=7 fixture=35060 saving=5694 no_new_kappa")

#!/usr/bin/env python3
"""Independent exact raw, banked and signed checks for the single 1256 relay."""

import argparse
from collections import Counter
from fractions import Fraction as Q
from functools import cache
import gzip
from hashlib import sha256
import json
from math import lcm
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from orientation import compare_columns, support

HERE = Path(__file__).resolve().parent.parent
SOURCE_HEAD = "7d84799a447867d36137d12ef7ca5646154d763c"
SOURCE = "ae62d5d8bef6f7146454b4b3643e487a58380c606a16c5baef7bf0dcf9df1472"
PARENT = "72705b094d83d2ba24006661bbb031786a691b776bedb94515b1321e1535105f"
CHILD = "8e7b755bd2d2d387bc3d3adfe48100985adf74775ca5acbb143170a3d16b5ccf"
CALLER = "62d94fb992acab0a71c3d12f22be4ce63f4f65e5cbe3f420b93aa1393ffa8dcf"
CERTS = "39ef28b708cd8bf1166b111d656809407b370dd11cd81a8e43820779f995aca3"
SOURCE_INVOICE = "a6b9a9529db9476e4b39ef4d4fad0a075f5675cbbedde99b7a08b2c007ff006d"
COMPARE_7697 = "c5ca88568459eb5aa7769ca7f9f430bcb117f39c2e2c16764517afb5daec4b7e"
REMOVE, KEEP, ROLE = 95828, 104442, 1256
GRID = 225 * 2**18


def require(ok, detail):
    if not ok:
        raise ValueError(detail)


def hash_bytes(raw):
    return sha256(raw).hexdigest()


def current(path, digest):
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    require(hash_bytes(raw) == digest, f"byte pin {path.name}")
    return json.loads(raw)


def blocked(fn, reason):
    try:
        fn()
    except ValueError as exc:
        require(str(exc) == reason, f"unexpected fault control {exc}")
    else:
        raise ValueError(f"fault control accepted {reason}")
    return reason


def integer_smooth(n):
    for p in (2, 3, 5):
        while n % p == 0:
            n //= p
    return n == 1


def ordered_ranks(frames):
    spans = tuple(set(support(vectors)) for vectors in frames)

    @cache
    def rank(a, b):
        require(spans[a] < spans[b] or spans[b] < spans[a], "positive nested MOVE")
        return abs(len(frames[a]) - len(frames[b]))

    return rank


@cache
def coeff(amount, is_scale):
    q = Q(amount)
    require(q != 0 and abs(q.numerator).bit_length() <= 24 and q.denominator.bit_length() <= 24
            and integer_smooth(q.denominator)
            and (not is_scale or integer_smooth(abs(q.numerator))), "raw nonzero/smooth 24-bit coefficient")
    return q


def row_add(dst, src, factor):
    for i, x in src.items():
        y = dst.get(i, 0) + factor*x
        if y:
            dst[i] = y
        else:
            dst.pop(i, None)


def row_grid_add(dst, src, q):
    a, b = q.numerator, q.denominator
    for i, x in src.items():
        y, r = divmod(a*x, b)
        require(r == 0, "raw scalar term grid")
        total = dst.get(i, 0) + y
        if total:
            dst[i] = total
        else:
            dst.pop(i, None)


def prove_clear(owner, n, rows, terms):
    require(owner >= n and owner in rows, "CLEAR must retire the actual owned lifetime")
    require(owner not in terms, "CLEAR uses the erased role as its proof donor")
    require(terms.keys() <= rows.keys(), "CLEAR donor not live")
    common = lcm(*(q.denominator for q in terms.values()))
    total = {}
    for role, q in terms.items():
        row_add(total, rows[role], q.numerator * (common // q.denominator))
    require(total == {col: x*common for col, x in rows[owner].items()}, "exact CLEAR equation")


def moves_and_forms(g):
    moves = {k: (a, b) for k, a, b in g["moves"]}
    forms = {k: {j: Q(c) for j, c in row} for k, row in g["forms"]}
    require(len(moves) == len(g["moves"]) and len(forms) == len(g["forms"])
            and all(len(forms[k]) == len(row) and all(forms[k].values()) for k, row in g["forms"]),
            "unique literal normalized rows and donors")
    return moves, forms


def raw_replay(word, certs, parent, raw_moves, raw_forms, rank):
    n = word["public"]
    require(certs["candidate_canonical_sha256"] == SOURCE and n == 1501
            and len(word["program"]) == parent["first_output"] == 154768
            and word["initial"] == parent["initial"] and word["final"] == parent["final"]
            and word["frames"] == parent["frames"], "raw to folded source boundary")
    certificates = {int(i): {int(r): Q(q) for r, q in row.items()}
                    for i, row in certs["clear_event_index"].items()}
    state = {i: {i: GRID} for i in range(n)}
    forms = {i: {~i: Q(1)} for i in range(n)}
    charts = dict(enumerate(word["initial"]))
    half = 0
    owned_max = 0
    nonzero = 0
    clear_controls = None
    moves = set()
    clears = set()
    ops = Counter()

    for k, (op, r, *args) in enumerate(word["program"]):
        ops[op] += 1
        touched = {r}
        if op == "ADD":
            s, amount, chart = args
            q = coeff(amount, False)
            require(r != s and charts.get(r) == charts.get(s) == chart, "active cocharted ADD")
            row_grid_add(state[r], state[s], q)
            row_add(forms[r], forms[s], q)
            touched.add(s)
            half += len(state[s])
        elif op == "SCALE":
            amount, chart = args
            q = coeff(amount, True)
            require(charts.get(r) == chart, "active cocharted SCALE")
            out = {}
            row_grid_add(out, state[r], q)
            half += len(state[r])
            state[r] = out
            forms[r] = {i: q*v for i, v in forms[r].items()}
        elif op == "MOVE":
            a, b, owned = args
            require(charts.get(r) == a and owned is (r >= n), "physical MOVE ownership and chart")
            rank(a, b)
            charts[r] = b
            require(raw_moves[k] == (a, b) and raw_forms[k] == forms[r], "raw paid form equals frozen parent")
            forms[r] = {k: Q(1)}
            moves.add(k)
        elif op == "INIT":
            chart, = args
            require(n <= r < n + word["owned_fields"] and r not in charts, "strict fresh private INIT")
            charts[r] = chart
            state[r], forms[r] = {}, {}
            owned_max = max(owned_max, len(charts) - n)
        elif op == "CLEAR":
            chart, = args
            require(charts.get(r) == chart and k in certificates, "ordered CLEAR chart and certificate")
            proof = certificates[k]
            prove_clear(r, n, state, proof)
            touched.update(proof)
            clears.add(k)
            nonzero += bool(state[r])
            if state[r] and clear_controls is None:
                clear_controls = {
                    "first_nonzero_clock": k,
                    "erased_owner": r,
                    "self_certificate": blocked(lambda: prove_clear(r, n, state, {r: Q(1)}),
                                                "CLEAR uses the erased role as its proof donor"),
                    "public_erase": blocked(lambda: prove_clear(0, n, state, {}),
                                            "CLEAR must retire the actual owned lifetime"),
                    "omit_nonzero_operand": blocked(lambda: prove_clear(r, n, state, {}),
                                                    "exact CLEAR equation"),
                }
            for registry in (charts, state, forms):
                del registry[r]
        else:
            raise ValueError(f"unexpected raw literal {op}")
        if REMOVE < k < KEEP:
            require(ROLE not in touched, "role 1256 accessed inside the intermediate stays")

    require(set(charts) == set(state) == set(range(n)) and list(charts.values()) == word["final"]
            and moves == raw_moves.keys() and clears == certificates.keys()
            and len(clears) == 235 and nonzero == 193 and owned_max == 51,
            "all raw MOVE, lifetime, CLEAR and boundary inventories")
    end = parent["first_output"]
    require(all(forms[i] == raw_forms[end+i] for i in range(n)), "all literal folded terminal forms")
    expected = {i: {i: GRID} for i in range(n)}
    for port, x in enumerate(word["live"]):
        y = x + 112
        if port in word["hosted"]["Dports"]:
            expected[y][x] = GRID
        else:
            expected[x][y] = -GRID
            expected[y] = {x: GRID//2, y: GRID//2}
    for x, y in zip(word["hosted"]["X2"], word["hosted"]["Y2"], strict=True):
        expected[x][y] = -GRID
    require(state == expected, "all 1501 independent external normalized rows")
    return {"raw_input_grid": GRID, "exact_literal_products": half,
            "raw_events": dict(ops), "ordered_clear_relations": len(clears), "nonzero_clear_operands": nonzero,
            "peak_live_private": owned_max, "public_rows": len(expected),
            "all_paid_and_terminal_folded_forms_matched": True, "controls": clear_controls}


def coframe_execution(graph, moves, rows):
    order = graph["schedule"]
    first = graph["first_output"]
    public = range(len(graph["final"]))
    require(len(order) == len(set(order)) == len(rows)
            and set(order) == set(rows) == moves.keys() | {first + r for r in public},
            "each bank and terminal exactly once")
    ready = {~r: chart for r, chart in enumerate(graph["initial"])}
    for key in order:
        if key in moves:
            source, target = moves[key]
        else:
            source, target = graph["final"][key-first], None
        require(all(ready.get(donor) == source for donor in rows[key]), "causal cochart donor")
        if target is not None:
            ready[key] = target


def exclusive(rows):
    require([key for key, row in rows.items() if REMOVE in row] == [KEEP],
            "removed bank has an additional reader")
    require(rows[KEEP] == {REMOVE: Q(1)}, "surviving read is exactly identity")


def relay_check(word, parent, child, om, of, nm, nf, rank):
    k = word["program"]
    require(k[REMOVE] == ["MOVE", ROLE, 476, 878, False]
            and k[KEEP] == ["MOVE", ROLE, 878, 127, False], "two exact public relay clocks")
    require((om[REMOVE], om[KEEP], nm[KEEP]) == ((476, 878), (878, 127), (476, 127)),
            "two old ordered pairs and the new one")
    require(nm.keys() == om.keys() - {REMOVE} and nf.keys() == of.keys() - {REMOVE}
            and all(nm[i] == om[i] for i in nm if i != KEEP)
            and all(nf[i] == of[i] for i in nf if i != KEEP)
            and REMOVE not in {donor for row in nf.values() for donor in row}
            and nf[KEEP] == of[REMOVE], "only the exact silent relay contraction")
    require(all(parent[field] == child[field] for field in ("initial", "final", "frames", "first_output")),
            "unchanged public and geometry declarations")
    require(all(g["metadata"]["source_pr_head"] == SOURCE_HEAD
                and g["metadata"]["source_word_sha256"] == SOURCE
                and g["metadata"]["caller_sha256"] == CALLER
                for g in (parent, child)), "exact graph source metadata")
    exclusive(of)
    coframe_execution(parent, om, of)
    coframe_execution(child, nm, nf)
    parent_order = parent["schedule"]
    child_order = child["schedule"]
    require([i for i in parent_order if i not in (REMOVE, KEEP)] ==
            [i for i in child_order if i != KEEP], "all remaining row orders are preserved")
    old_position = parent_order.index(KEEP)
    new_position = child_order.index(KEEP)
    require(new_position < old_position, "the surviving stable key actually moves earlier")
    candidate_positions = {k: i for i, k in enumerate(child_order)}
    donor_position = max(candidate_positions[i] for i in nf[KEEP] if i >= 0)
    next_read = min(candidate_positions[k] for k, row in nf.items() if KEEP in row)
    require(donor_position < new_position < next_read, "actual source-ready window for the moved row")
    bad_order = [k for k in child_order if k != KEEP]
    bad_order.insert(donor_position, KEEP)
    premature = blocked(lambda: coframe_execution({**child, "schedule": bad_order}, nm, nf),
                        "causal cochart donor")
    require(tuple(rank(*pair) for pair in (om[REMOVE], om[KEEP], nm[KEEP])) == (3, 3, 6),
            "the complete grouped positive-rank change")
    other = next(k for k, (src, _) in om.items() if src == 878 and k != KEEP
                 and parent["schedule"].index(k) > parent["schedule"].index(REMOVE))
    fault = {**of, other: {**of[other], REMOVE: Q(1)}}
    coframe_execution(parent, om, fault)
    additional_reader = blocked(lambda: exclusive(fault), "removed bank has an additional reader")
    nonunit = {**of, KEEP: {REMOVE: Q(-1)}}
    wrong_coefficient = blocked(lambda: exclusive(nonunit), "surviving read is exactly identity")
    return {"role": ROLE, "old_slots": [REMOVE, KEEP], "paid_ranks": [3, 3, 6],
            "sender_row": {k: str(v) for k, v in nf[KEEP].items()},
            "parent_removed_position": parent_order.index(REMOVE), "survivor_positions": [old_position, new_position],
            "last_donor_and_first_reader_positions": [donor_position, next_read],
            "control_premature_survivor": premature,
            "global_equivalence": "all downstream rows use the same normalized return at the same chart",
            "between_clock_public_and_clear_touches": 0,
            "control_additional_cocharted_read_at": other,
            "control_additional_cocharted_read": additional_reader,
            "control_wrong_identity_weight": wrong_coefficient}


def owner_ranks(word, graph, caller, rank):
    boundaries = word["hosted"]
    mains = set(word["live"]) | {r+112 for r in word["live"]} | set(boundaries["X2"]) | set(boundaries["Y2"])
    require(len(mains) == 400 and len(graph["initial"]) == 1501, "actual native owner inventory")
    types = caller["types"]
    sides = {k: set(v["ports"]) for k, v in types.items()}
    require(len(sides["A"]) == 96 and len(sides["B"]) == 8
            and sides["A"].isdisjoint(sides["B"]) and sides["A"] | sides["B"] == set(range(104)),
            "exact disjoint A/B port inventory")
    require(sides["A"] == set(boundaries["Dports"]), "literal slots use the raw main type split")
    require(caller["stages"] == 16 and caller["ambient_rank"] == 137, "actual caller dimensions")
    paid = Counter()
    target = Counter()
    roots = set()
    stage_tags = set()
    stage_order = []
    targets_once = Counter(rank(a, b) for i, (a, b) in enumerate(zip(graph["initial"], graph["final"], strict=True))
                           if i not in mains)
    native_paid_once = Counter(rank(a, b) for _, a, b in graph["moves"])
    for event in caller["events"]:
        if event[0] == "J":
            _, stage, a, b = event
            require(len(a) == 4 and len(b) == 4 and b[2:] == ["-1","1/2"]
                    and len(set(a + b[:2])) == 6
                    and all(0 <= role < types["A"]["roles"] for role in a)
                    and all(types["B"]["offset"] <= role < caller["roles"] for role in b[:2]),
                    "actual J signs and owners")
            stage_order.append(stage)
            paid.update(native_paid_once)
            target.update(targets_once)
            stage_tags.update((stage, r) for r in range(1501) if r not in mains)
        else:
            role_type, op, r, *tail = event
            count = len(sides[role_type])
            if op == "QUERY":
                paid[1] += count
            elif op in ("IDLE_ONE", "IDLE_ODD"):
                stage_bits = tail[0]
                require(len(stage_bits) == len(set(stage_bits)) and all(1 <= i <= 16 for i in stage_bits),
                        "actual idle has distinct blocks")
                paid[8 * len(stage_bits) + (op == "IDLE_ODD")] += count
    require(stage_order == list(range(1, 17)), "sixteen actual calls in literal order")
    for name, spec in types.items():
        for i, (phase, alpha, *selection) in enumerate(spec["diagonal"]):
            require(alpha == 0 and len(selection) == 16 and set(selection) <= {0, 1}
                    and sum(selection) > 0, "actual productive signed call root")
            target[8 * sum(selection) + (phase % 2)] += len(sides[name])
            roots.update((port, spec["offset"]+i) for port in sides[name])
    require(len(roots) == 3536 and len(stage_tags) == 17616
            and len(roots) + len(stage_tags) == sum(target.values()) == 21152,
            "whole external target census")
    return paid, target


def invoice_counts(obj):
    return tuple(Counter({int(r): n for r, n in obj[side].items()}) for side in ("paid", "targets"))


def positive_log(z):
    n = 24
    partial = 2 * sum((z**(2*j+1) / (2*j+1) for j in range(n)), Q())
    return partial, partial + 2 * z**(2*n+1) / ((2*n+1)*(1-z*z))


@cache
def log_rank(r):
    bits = r.bit_length() - 1
    m = Q(r, 1 << bits)
    a, b = positive_log((m-1)/(m+1))
    c, d = positive_log(Q(1, 3))
    return a+bits*c, b+bits*d


def negative_exp(x):
    require(0 <= x < 1, "alternating exponential range")
    y = part = Q(1)
    for i in range(1, 18):
        y *= -x/i
        part += y
    return part, part-y


@cache
def root_weight(rank, k):
    a, b = log_rank(rank)
    low = rank * negative_exp(k*b)[0]
    high = rank * negative_exp(k*a)[1]
    d = 1 << 150
    return Q((low.numerator*d)//low.denominator, d), Q(-((-high.numerator*d)//high.denominator), d)


def signed_interval(invoice, l, r=None, derivative=False):
    paid, target = invoice
    r = l if r is None else r
    low = high = Q()
    for rank in set(paid) | set(target):
        subtraction = target[rank]-paid[rank]
        a, b = root_weight(rank, r)[0], root_weight(rank, l)[1]
        if derivative:
            la, lb = log_rank(rank)
            a, b = -b*lb, -a*la
        lq, rq = sorted((subtraction*a, subtraction*b))
        low += lq
        high += rq
    return low, high


def directed_result(invoice, point, required_sign):
    val = signed_interval(invoice, point)
    require(val[0] > 0 if required_sign > 0 else val[1] < 0, f"directed price sign at {point}")
    return {"point": str(point), "rational": list(map(str, val)), "approx": list(map(float, val))}


def price_proof(word, parent, child, caller, rank):
    start = owner_ranks(word, parent, caller, rank)
    end = owner_ranks(word, child, caller, rank)
    expected_start = invoice_counts(current(HERE/"data/SOURCE-INVOICE.json", SOURCE_INVOICE))
    prior = current(HERE/"review/COMPARATOR-7697.json", COMPARE_7697)
    require(prior["caller"] == CALLER
            and prior["head"] == "f55fc1434436ffa1c6d064a29fc56812044b3157",
            "exact previous compatible caller")
    accepted_invoice = invoice_counts(prior["invoice"])
    require(start == expected_start, "literal replay matches #7700's full supplied invoice")
    delta = end[0].copy()
    delta.subtract(start[0])
    require({r: n for r, n in delta.items() if n} == {3: -32, 6: 16} and start[1] == end[1],
            "all signed paid and target changes")
    require((sum(start[0].values()), sum(end[0].values()), sum(end[1].values())) == (101856, 101840, 21152),
            "full signed denominators")

    p7697_lo, p7697_hi = Q("0.0037266288769"), Q("0.0037266288770")
    p7700_lo, p7700_hi = Q("0.00372934317806"), Q("0.00372934317807")
    threshold = Q("0.00372935")
    cap = Q("0.00376669")
    checks = {
        "prior_7697_bracket": [directed_result(accepted_invoice, p7697_lo, 1),
                               directed_result(accepted_invoice, p7697_hi, -1)],
        "raw_7700_bracket": [directed_result(start, p7700_lo, 1),
                              directed_result(start, p7700_hi, -1)],
        "candidate_at_round_probe": directed_result(end, threshold, 1),
    }
    for invoice in (start, end, accepted_invoice):
        require(signed_interval(invoice, p7697_lo, cap, derivative=True)[1] < 0,
                "complete moment strictly decreases through the compatible interval")
    one_fee = end[0].copy()
    one_fee[1] += 1
    missing_group = end[0].copy()
    missing_group[3] += 16
    checks["one_new_rank_one_fee"] = directed_result((one_fee, end[1]), threshold, -1)
    checks["restore_one_simultaneously_replaced_rank_three_family"] = directed_result(
        (missing_group, end[1]), threshold, -1)

    precision = 10**14
    lo, hi = int(threshold*precision), int(cap*precision)
    while lo+1 < hi:
        mid = (lo+hi)//2
        bounds = signed_interval(end, Q(mid, precision))
        require(bounds[0] > 0 or bounds[1] < 0, "directed bisection rejects uncertain sign")
        if bounds[0] > 0:
            lo = mid
        else:
            hi = mid
    checks["candidate_crossing"] = [directed_result(end, Q(lo, precision), 1),
                                    directed_result(end, Q(hi, precision), -1)]
    ordinary_guarded_lower = Q(lo-10, precision)
    require(ordinary_guarded_lower > max(p7697_hi, p7700_hi), "strictly beats both directed upper points")
    checks["guarded_candidate_lower_point"] = directed_result(end, ordinary_guarded_lower, 1)
    return {"input_paid_counts": start[0], "output_paid_counts": end[0], "whole_targets": end[1],
            "checks": checks, "comparison_scope": "actual literal 16-call signed invoice",
            "exponent_convention": "each positive rank r costs r^(1-kappa)"}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--out", type=Path, required=True)
    args = cli.parse_args()
    require(not args.out.exists(), "exclusive review output")
    word = current(HERE/"data/WORD.json.gz", SOURCE)
    certs = current(HERE/"data/CERTS.json", CERTS)
    parent = current(HERE/"data/PARENT-GRAPH.json.gz", PARENT)
    child = current(HERE/"data/CANDIDATE-GRAPH.json.gz", CHILD)
    caller = current(HERE/"data/CALLER.json.gz", CALLER)
    om, of = moves_and_forms(parent)
    nm, nf = moves_and_forms(child)
    rank = ordered_ranks(word["frames"])
    relay = relay_check(word, parent, child, om, of, nm, nf, rank)
    replay = raw_replay(word, certs, parent, om, of, rank)
    gaussian = compare_columns(word["frames"])
    price = price_proof(word, parent, child, caller, rank)
    result = {
        "status": "PASS_INDEPENDENT_ROLE1256_RAW_CLEAR_READY_PHASE_AND_DIRECTED_PRICE",
        "source": SOURCE, "source_head": SOURCE_HEAD, "parent_graph": PARENT, "changed_graph": CHILD,
        "signed_caller": CALLER, "raw_clear_certificates": CERTS,
        "literal_source_and_owned_guard": replay,
        "banked_relay": relay,
        "native_direct_columns": gaussian,
        "price": price,
        "scope": "Independent implementation checks under the retained five P104 assumptions, not independent human theorem approval",
    }
    with args.out.open("x") as out:
        json.dump(result, out, indent=2, sort_keys=True)
        out.write("\n")
    print(result["status"])


if __name__ == "__main__":
    main()

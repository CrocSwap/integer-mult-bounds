"""Verify the exact 16-call role-230 transfer on both fixed #7674 graphs."""

from argparse import ArgumentParser
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
CALLER = "62d94fb992acab0a71c3d12f22be4ce63f4f65e5cbe3f420b93aa1393ffa8dcf"
SOURCE = "ee251f6005d2a92b887c5b804bd7aac05989d278b2c9ccb3c3091b50d533b08d"
DIRECT = "ab5653d6b6007f8a7987e7ffc6ebab24c662ba852a0d0b446c3a1be19b88db8a"
HEAD = "28b2af322a1fab01b3734365988930920f9dda48"
SCIENCE = "26b6c469aa6c4aa04322ce25a22150f90e5fb14e"
PIVOTS = "fb22afc8aaf543e62709fa682f222577e6bdf4e1f1994d307784468314c3da85"
PR_RESULT = "00340c699fd7e2895d31a41d1eb60aebf91d7ba2c1c193dc002f69315298cd38"
WIRE_RESULT = "cde8b602d182ece20f55616decab1bf5c2b64e877770c20106afca44ff08752d"
GRAPH_PINS = {
    "peer": ("d81ec9f47740852a4bf7bd83100feff5cb66b70e1973466e1609bbac8af75098",
             "d293b505f9c572ea56a5ee378d194e5a5b34796ae3fde97467d6f7aace97f84d"),
    "candidate": ("1f082936ada08b5138b7d13e33368bd21c6f46632c5319a348e2f2a8e0021150",
                  "8e28c1d403145ca5d72521f4acd7e068603598334c87f18f2fefb738844a1970"),
}
BL = "0.00372604555572"
PARENT = ("0.0037260455556", "0.00372604555571", BL)
TARGET = "0.0037261023899"
BIT = "0.00376669"
GAP = Fraction(1, 10**14)


def require(condition, error):
    if not condition:
        raise ValueError(error)


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode()


def digest(data):
    return sha256(data).hexdigest()


def load(path, byte_sha=None):
    raw = path.read_bytes()
    if byte_sha is not None:
        require(digest(raw) == byte_sha, "input bytes: " + path.name)
    decoded = gzip.decompress(raw) if raw.startswith(b"\x1f\x8b") else raw
    return json.loads(decoded), digest(decoded)


def emit(out, filename, value):
    with (out / filename).open("x", encoding="utf-8") as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.write("\n")


def pinned_inputs(package, engine_dir):
    spec = load(HERE / "SOURCE-PINS.json")[0]
    roots = {"peer": package, "engine": engine_dir, "local": HERE}
    for row in spec["pins"]:
        target = roots[row["root"]] / row["path"]
        require(digest(target.read_bytes()) == row["sha256"], "exact pinned file: " + row["path"])
    claim = load(engine_dir / "selected-claim.json")[0]
    repair = load(engine_dir / "selected-bit-ambient.json")[0]
    validation = load(engine_dir / "selected-validation.json")[0]
    bit = next(item for item in claim["uniform_templates"] if item["family"] == "BIT before cover")
    require(bit["ambient"] == 134 and bit["rank_encoding"] == "2^296630000000000"
            and repair["exit_code"] == 0 and validation["status"] == "admitted_conditional",
            "corrected 134-axis BIT")
    require(Fraction("0.00385248") > Fraction(BIT), "completed selected BIT supplies outer floor")
    return {"working_ambient": bit["ambient"], "completed_ordinary": "0.00385248",
            "outer_floor": BIT, "retained_assumptions": claim["assumptions"]}


def graph_input(path, kind, word, receipt):
    from network import Network

    can_sha, byte_sha = GRAPH_PINS[kind]
    data, decoded = load(path, byte_sha)
    require(decoded == can_sha and digest(canonical(data)) == can_sha, "exact canonical graph")
    fixed = receipt["graphs"][kind]
    require((fixed["canonical_sha256"], fixed["gzip_sha256"]) == (can_sha, byte_sha),
            "exact wire gate binds graph")
    metadata = data["metadata"]
    require(metadata == {"schema": "p104-exact-banked-dag/v1", "kind": kind,
                         "peer_head": HEAD, "scientific_commit": SCIENCE,
                         "source_word_sha256": SOURCE, "caller_sha256": CALLER,
                         "role230_direct_word_sha256": DIRECT if kind == "candidate" else None,
                         "fixed_pivot_sha256": PIVOTS, "published_result_sha256": PR_RESULT},
            "fixed exact comparison scope")
    require(data["frames"] == word["frames"] and data["initial"] == word["initial"]
            and data["final"] == word["final"] and data["first_output"] == len(word["program"]),
            "public boundary and frames")
    moves = {key: (a, b) for key, a, b in data["moves"]}
    forms = {key: {donor: Fraction(coef) for donor, coef in entries}
             for key, entries in data["forms"]}
    require(len(moves) == len(data["moves"]) == 6142 and len(forms) == len(data["forms"]) == 7643
            and all(len(forms[key]) == len(entries) for key, entries in data["forms"]),
            "duplicate or lost graph slot")
    require(all(coef for row in forms.values() for coef in row.values()), "nonzero literal reads")
    graph = Network(data["first_output"], data["initial"], data["final"], moves, forms)
    schedule = graph.schedule()
    require(schedule == data["schedule"], "deterministic coframe and causal schedule")
    return graph, schedule


def owner_and_phase(word, caller, signed):
    from binding16 import contact_phase
    from caller16 import literal_layout

    stages, types, role_sets = literal_layout(caller, word)
    h = word["hosted"]
    hosted = dict(zip(h["Dports"], zip(h["X2"], h["Y2"], strict=True), strict=True))
    main = set(word["live"]) | {r + 112 for r in word["live"]} | set(h["X2"]) | set(h["Y2"])
    helpers = sorted(set(range(1501)) - main)
    owner_tags = {("main", port, role) for kind, spec in types.items()
                  for port in spec["ports"] for role in role_sets[kind]}
    require(len(owner_tags) == 3536 == signed["root_owners"] and len(helpers) == 1101
            and len(main) == 400, "distinct whole root and helper owners")
    phase_bases = load(HERE / "data/PHASE-BASES.json")[0]["by_q"]
    phase_rows, mapped, exact_helpers = [], [], []
    for clock, event in enumerate(caller["events"]):
        if event[0] != "J":
            continue
        _, stage, a, b = event
        rows = {}
        for j, (r, q) in enumerate(zip(word["live"], word["ports"], strict=True)):
            y = r + 112
            require(word["frames"][word["initial"][r]] == [q]
                    and not word["frames"][word["initial"][y]], "actual main ingress")
            if j in hosted:
                u, v = hosted[j]
                require(all(word[boundary][u] == word[boundary][r]
                            and word[boundary][v] == word[boundary][y]
                            for boundary in ("initial", "final")), "second-plane exact charts")
                pairs = zip((r, y, u, v), a, strict=True)
            else:
                pairs = zip((r, y), b[:2], strict=True)
            for slot, role in pairs:
                tag = ("main", j, role)
                require(tag in owner_tags and slot not in rows, "valid stage alias guard")
                rows[slot] = tag
            shifts, _ = contact_phase(q, phase_bases[str(q)], stage, caller["ambient_rank"])
            phase_rows.append([clock, j, shifts, 2 if j in hosted else 1])
        require(set(rows) == main and len(set(rows.values())) == 400, "injective main bindings")
        for role in helpers:
            rows[role] = ("helper", stage, role)
        require(len(rows) == len(set(rows.values())) == 1501, "actual 1,501-input stage")
        for role in (325, 1087):
            require(rows[role] == ("helper", stage, role)
                    and (word["initial"][role], word["final"][role]) == (3, 237)
                    and not word["frames"][3] and word["frames"][237] == [30, 75, 138, 266],
                    "distinct arbitrary helper rank-four boundary")
            exact_helpers.append([stage, role, 3, 237])
        mapped.append([stage, sorted(rows.items())])
    require(len(mapped) == stages and len(exact_helpers) == 32, "complete stage lineage")
    contacts = sum(4 * row[3] for row in phase_rows)
    require(contacts == 12800 and all(all(row[2]) for row in phase_rows)
            and digest(canonical(phase_rows)) == "29196a9aa29ecf4b3705a6346c40642eef9b14600ccc832210df91c3e4f84f50",
            "complete pre-existing same-caller phase context")
    root_negative = sum(len(spec["ports"]) for spec in types.values()
                        for phase, _, *_ in spec["diagonal"] if phase == -1)
    require(root_negative == 3536, "charge actual negative root ordinary head corrections")
    return {"owners": sorted(owner_tags), "root_negative_corrections": root_negative,
            "phase_contacts": contacts, "phase_digest": digest(canonical(phase_rows)),
            "all_public_tag_digest": digest(canonical(mapped)),
            "fresh_helpers": stages * len(helpers), "special_live_helpers": exact_helpers,
            "main_roles": sorted(main)}


def independent_rank(word, graph, caller, signed):
    dims, masks = [], []
    for basis in word["frames"]:
        span = {0}
        for row in basis:
            require(type(row) is int and 0 < row < 512 and row not in span,
                    "independent actual chart basis")
            span |= {row ^ v for v in span}
        masks.append(span)
        dims.append(len(basis))

    def positive(pair, directed=False):
        a, b = pair
        require(0 <= a < len(masks) and 0 <= b < len(masks)
                and (masks[a] < masks[b] or (not directed and masks[b] < masks[a])),
                "actual positive nested chart pair")
        return abs(dims[a] - dims[b])

    main_roles = set(caller["main_roles"])
    native = Counter(positive(pair) for pair in graph.moves.values())
    helper = Counter(positive((graph.initial[r], graph.final[r]), True)
                     for r in range(word["public"]) if r not in main_roles)
    p = Counter({rank: signed["calls"] * count for rank, count in native.items()})
    t = Counter({rank: signed["calls"] * count for rank, count in helper.items()})
    p.update(signed["fixed_caller_paid"])
    t.update(signed["fixed_root_targets"])
    require(sum(p.values()) == 101824 and sum(t.values()) == 21152
            and sum(rank * (t[rank] - p[rank]) for rank in p.keys() | t.keys()) == 1328,
            "actual complete paid and productive counts")
    return native, helper, p, t


def make_invoice(reference, p, t):
    return {**reference, "paid": {str(k): v for k, v in p.items()},
            "targets": {str(k): v for k, v in t.items()}}


def price(empty, invoice, point):
    from evaluate_recursive_power import evaluate

    at = 1 - Fraction(point)
    check = evaluate(empty, invoice, at, 256)
    require(check["classification"] in ("new_cost_lower", "new_cost_higher"),
            "directed price undetermined")
    return check


def decimal_integer(k, places):
    base = 10**places
    return f"{k // base}.{k % base:0{places}d}"


def find_crossing(empty, invoice):
    places = 13
    lo = int(Fraction(TARGET) * 10**places)
    hi = int(Fraction("0.00372611") * 10**places)
    require(price(empty, invoice, decimal_integer(lo, places))["classification"] == "new_cost_lower"
            and price(empty, invoice, decimal_integer(hi, places))["classification"] == "new_cost_higher",
            "candidate bracket right of fixed target")
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if price(empty, invoice, decimal_integer(mid, places))["classification"] == "new_cost_lower":
            lo = mid
        else:
            hi = mid
    return decimal_integer(lo - 1, places), decimal_integer(lo, places), decimal_integer(hi, places)


def numerical(empty, invoice, p, t, triple, baseline_sign):
    from interval_gate import gate

    claim, lower, upper = triple
    probe = Fraction(claim) + 7 * GAP
    rows = {}
    for point, direction in ((claim, "lower"), (str(probe), "lower"), (lower, "lower"),
                             (upper, "higher"), (BL, baseline_sign)):
        check = price(empty, invoice, point)
        require(check["classification"] == "new_cost_" + direction, "strict endpoint " + point)
        rows[point] = check
    outer = gate({"P": p, "T": t}, claim, probe, lower, upper, BIT)
    o = outer["outer"]
    require(o["strict_count"] == 54 and o["functional_count"] == 4
            and Fraction(o["minimum_margin"]) > 0, "all exact numerical outer predicates")
    return {"decimal_claim": claim, "bracket": [lower, upper],
            "directed_checks": rows, "compiler": outer}


def main():
    parser = ArgumentParser(description=__doc__)
    for field in ("package", "engine-dir", "parent-graph", "candidate-graph", "graph-receipt", "out"):
        parser.add_argument("--" + field, required=True, type=Path)
    args = parser.parse_args()
    args.out.mkdir()
    bit = pinned_inputs(args.package, args.engine_dir)
    sys.path[:0] = [str(HERE), str(HERE / "vendor"), str(args.package.resolve()),
                    str(args.package.resolve() / "source"), str(args.engine_dir.resolve())]
    from bank_cost import dispatch_fixture, ordinary_cost
    from caller import caller_replay
    from caller16 import signed_caller
    from native import check_endpoints
    from network import networks, source_word
    from physical import budget

    ref = load(args.package / "RESULT.json", PR_RESULT)[0]
    wire = load(args.graph_receipt, WIRE_RESULT)[0]
    require(wire["status"] == "PASS_BANK24_WIRE_COMMUTATION", "exact positive wire receipt")
    word = source_word()
    caller, caller_sha = load(args.package / "source/caller.json.gz")
    require(caller_sha == CALLER and digest(canonical(word)) == SOURCE, "actual 16-call source")
    peer, peer_order = graph_input(args.parent_graph, "peer", word, wire)
    child, child_order = graph_input(args.candidate_graph, "candidate", word, wire)
    _, expected_peer, pivot_rows = networks(word)
    require(expected_peer == peer and pivot_rows == ref["application"]["pivots"]
            and len(pivot_rows) == 15, "actual published parent fixed pivots")
    require(peer.moves.keys() == child.moves.keys()
            and set(i for i in peer.moves if peer.moves[i] != child.moves[i]) == {97471, 102393},
            "no extra paid child in exact graph")
    emit(args.out, "INPUTS.json", {"graph_pins": GRAPH_PINS, "wire_sha256": WIRE_RESULT,
                                  "caller_sha256": CALLER, "public_parent_head": HEAD, "bit": bit})

    old_signed = caller_replay(caller, word)
    require(json.loads(json.dumps(old_signed, sort_keys=True)) == ref["application"]["caller"],
            "exact #7674 signed caller receipt")
    signed = signed_caller(caller, word, 2025, 9)
    for a, b in (("fixed_caller_paid", "paid"), ("fixed_root_targets", "targets"),
                 ("uses", "uses"), ("root_owners", "root_owners"), ("exact_preproduct_divisions", "exact_preproduct_divisions"),
                 ("peak_scaled_mass", "peak_scaled_mass"), ("dyadic_height", "dyadic_height")):
        require(signed[a] == old_signed[b], "second exact caller replay: " + a)
    owners = owner_and_phase(word, caller, signed)
    require(owners["fresh_helpers"] == 17616, "distinct arbitrary helper roots")
    emit(args.out, "CALLER.json", {"signed": signed, "owners": owners})

    p_native, p_helper, p, t = independent_rank(word, peer, owners, signed)
    c_native, c_helper, cp, ct = independent_rank(word, child, owners, signed)
    expected = ref["application"]["invoice"]
    original = make_invoice(expected, p, t)
    candidate = make_invoice(expected, cp, ct)
    require(original == expected and p_helper == c_helper and t == ct, "exact original P/T and target preservation")
    require((cp - p, p - cp) == (Counter({2: 16, 4: 16}), Counter({3: 32})),
            "only the two paid ranks changed on the full tape")
    emit(args.out, "INVOICES.json", {"peer": original, "candidate": candidate,
                                   "native_paid": {"peer": p_native, "candidate": c_native},
                                   "native_helper_targets": p_helper})
    empty = make_invoice(expected, {}, {})
    old_number = numerical(empty, original, p, t, PARENT, "higher")
    triple = find_crossing(empty, candidate)
    new_number = numerical(empty, candidate, cp, ct, triple, "lower")
    require(Fraction(triple[0]) > Fraction(BL), "strict directed increase at safety claim")
    paid_tax = deepcopy(candidate)
    paid_tax["paid"]["1"] += 1
    erases_gain = price(empty, paid_tax, BL)
    require(erases_gain["classification"] == "new_cost_higher", "extra paid charge control")
    emit(args.out, "PRICE-OUTER.json", {"peer": old_number, "candidate": new_number,
                                      "added_rank_one_charge": erases_gain})
    print("PASS signed paired caller, actual complete P/T, split compiler and 54+4", flush=True)

    grid = {"peer": check_endpoints(peer, word), "candidate": check_endpoints(child, word)}
    require(grid["peer"] == ref["native"], "exact published fixed bank endpoint/grid replay")
    emit(args.out, "GRAPH-GRID.json", grid)
    merged = {**signed, **owners}
    costs = {}
    for kind, graph, schedule, paid, target, numeric in (
        ("peer", peer, peer_order, p, t, old_number),
        ("candidate", child, child_order, cp, ct, new_number),
    ):
        c = numeric["compiler"]
        original_budget = budget(graph, caller, grid[kind], old_signed, paid, target, c)
        if kind == "peer":
            require(original_budget == ref["application"]["physical"],
                    "published finite budget reproduces before adding common explicit charges")
        fixture = dispatch_fixture(word, graph, schedule, int(grid[kind]["grid"]))
        costs[kind] = {"original_budget": original_budget, "dispatcher": fixture,
                       "explicit_complete_cost": ordinary_cost(word, graph, grid[kind], merged,
                                                               c, original_budget, fixture)}
    emit(args.out, "PHYSICAL.json", costs)
    result = {
        "status": "PASS_BANK24_ACTUAL16_APPLICATION_COMPONENT",
        "candidate_directed_conditional_lower": triple[0],
        "candidate_raw_bracket": list(triple[1:]),
        "published_peer_upper": BL,
        "strict_gap": str(Fraction(triple[0]) - Fraction(BL)),
        "graphs": GRAPH_PINS,
        "caller_sha256": CALLER,
        "signed_paid_delta": {"2": 16, "3": -32, "4": 16}, "signed_target_delta": {},
        "paid_count": sum(cp.values()), "productive_count": sum(ct.values()),
        "scope": "Paired exact normalized banked graph and caller, physical snapshot scheduler in normalized coordinates, all-width ordinary accounting under the selected five assumptions, and complete rank funding and outer numerical probes. Separate held-field native map receipts bind all shaped paid operators; the compiled multiplier is an inherited conditional construction.",
    }
    emit(args.out, "RESULT.json", result)
    print(result["status"], triple[0], flush=True)


if __name__ == "__main__":
    main()

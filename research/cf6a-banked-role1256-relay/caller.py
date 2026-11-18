#!/usr/bin/env python3
"""Replay the literal signed caller on the supplied word and frozen relay."""

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
DATA = HERE / "data"
ENGINE = HERE / "engines/caller"
SOURCE_HEAD = "7d84799a447867d36137d12ef7ca5646154d763c"
SOURCE_WORD = "ae62d5d8bef6f7146454b4b3643e487a58380c606a16c5baef7bf0dcf9df1472"
SOURCE_CERTS = "39ef28b708cd8bf1166b111d656809407b370dd11cd81a8e43820779f995aca3"
PARENT = "72705b094d83d2ba24006661bbb031786a691b776bedb94515b1321e1535105f"
CANDIDATE = "8e7b755bd2d2d387bc3d3adfe48100985adf74775ca5acbb143170a3d16b5ccf"
CALLER = "62d94fb992acab0a71c3d12f22be4ce63f4f65e5cbe3f420b93aa1393ffa8dcf"
PHASE_BASES = "325a1eb4aa7fe5f918b1d8344b88ad132ef4606268bccec20f223ace5feda18b"
PHASE_DIGEST = "29196a9aa29ecf4b3705a6346c40642eef9b14600ccc832210df91c3e4f84f50"
INVOICE = "a6b9a9529db9476e4b39ef4d4fad0a075f5675cbbedde99b7a08b2c007ff006d"
DATA_PINS = {
    "WORD.json.gz": ("50c1facfc5626c060560e2f354b71bd92d0bb1c1e853b2aad72abcbaaa5328a5", SOURCE_WORD),
    "PARENT-GRAPH.json.gz": ("c86288cddb4b80af3c8128c9a0d2f7a1e82bae64c5152a0d96a19d166afaab1d", PARENT),
    "CANDIDATE-GRAPH.json.gz": ("0177c25371181e3b1f2c13325eb8434fbf6384a9ab99a612849efd5d0f6ab2cc", CANDIDATE),
    "CALLER.json.gz": ("d889996a337f648087208ab51c98eaf052705d4fca88b5d01b6e9257a829897a", CALLER),
}
ENGINE_PINS = {
    "binding16.py": "589058311e44f2d8909495c005bee6d54828ebe561d4673b599193d269006170",
    "caller16.py": "ced48867f07ca0143604aa98cfd74fa7453696b9d3221f7c230d73e9ab9ba81f",
    "network.py": "a9169fd6ad0a13c69cf39bd32649d53256f6d6fa2ed2ceda854f848b64f4c546",
    "native.py": "788465324eb8693a698c75cb3dfdf1b82297324d5583910107ecad4600645e43",
    "reference_caller.py": "9bfb77250ca4826c1098b896769dc504b587c8c0dac634dd07012150fc8dde37",
    "upstream_application.py": "d98987db98553dc55bfc80e3ca47abfcd51c57af6f8cda61101391d8eae94184",
}
STAGES = 16
PUBLIC = 1501
RETIRED = 95828
MERGED = 104442
RELAY_OWNER = 1256
PAID_DELTA = {3: -32, 6: 16}
STATUS = "PASS_CF6A_RELAY_ACTUAL16_CALLER"


def need(condition, explanation):
    if not condition:
        raise ValueError(explanation)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return sha256(value).hexdigest()


def load(path, byte_pin=None, decoded_pin=None, canonical=False):
    raw = path.read_bytes()
    if byte_pin is not None:
        need(digest(raw) == byte_pin, f"frozen bytes {path.name}")
    decoded = gzip.decompress(raw) if raw.startswith(b"\x1f\x8b") else raw
    value = json.loads(decoded)
    if decoded_pin is not None:
        need(digest(decoded) == decoded_pin, f"literal source identity {path.name}")
    if canonical:
        need(encoded(value) == decoded, f"canonical data {path.name}")
    return value


def write(path, record):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(record, stream, sort_keys=True, indent=2)
        stream.write("\n")


def check_sources():
    for name, expected in ENGINE_PINS.items():
        need(digest((ENGINE / name).read_bytes()) == expected, f"vendored engine source {name}")
    if str(ENGINE) not in sys.path:
        sys.path.insert(0, str(ENGINE))


def read_data(name):
    return load(DATA / name, *DATA_PINS[name], canonical=name != "CALLER.json.gz")


def signed_delta(old, new):
    return {rank: new.get(rank, 0) - old.get(rank, 0) for rank in sorted(old.keys() | new.keys())
            if new.get(rank, 0) != old.get(rank, 0)}


def decode_graph(raw, word, paid):
    from network import Network, coefficients

    moves = {key: (a, b) for key, a, b in raw["moves"]}
    forms = {key: coefficients(row) for key, row in raw["forms"]}
    schedule = {key: pos for pos, key in enumerate(raw["schedule"])}
    need(raw["first_output"] == len(word["program"]) == 154768
         and all(word[key] == raw[key] for key in ("frames", "initial", "final"))
         and len(word["initial"]) == len(word["final"]) == PUBLIC
         and len(moves) == len(raw["moves"]) == paid
         and len(forms) == len(raw["forms"]) == paid + PUBLIC
         and len(schedule) == len(raw["schedule"]) and schedule.keys() == forms.keys()
         and all(donor < 0 or schedule[donor] < schedule[key]
                 for key, terms in forms.items() for donor in terms),
         "literal source fields, paid homes, terminal rows and declared chronology")
    graph = Network(raw["first_output"], raw["initial"], raw["final"], moves, forms)
    graph.schedule()
    meta = raw["metadata"]
    need(meta["source_pr"] == 7700 and meta["source_pr_head"] == SOURCE_HEAD
         and meta["source_word_sha256"] == SOURCE_WORD and meta["caller_sha256"] == CALLER
         and meta["source_clear_certificates_sha256"] == SOURCE_CERTS, "exact supplied source custody")
    return graph


def relay_contract(parent, child, parent_schedule, child_schedule, word):
    from network import fold

    need(parent == fold(word), "literal folded parent agrees with every supplied WORD row")
    need(word["program"][RETIRED] == ["MOVE", RELAY_OWNER, 476, 878, False]
         and word["program"][MERGED] == ["MOVE", RELAY_OWNER, 878, 127, False]
         and parent.moves[RETIRED] == (476, 878) and parent.moves[MERGED] == (878, 127)
         and parent.forms[MERGED] == {RETIRED: Fraction(1)}
         and [key for key, row in parent.forms.items() if RETIRED in row] == [MERGED],
         "exclusive unit-coefficient paid relay at the actual public role")
    moves, rows = parent.moves.copy(), parent.forms.copy()
    del moves[RETIRED]
    moves[MERGED] = (476, 127)
    rows[MERGED] = rows.pop(RETIRED)
    need(child.moves == moves and child.forms == rows
         and [key for key in child_schedule if key != MERGED]
         == [key for key in parent_schedule if key not in (RETIRED, MERGED)],
         "exact relay substitution and conserved order of the other paid and ordinary rows")
    ordinals = {"parent_retired": parent_schedule.index(RETIRED),
                "parent_survivor": parent_schedule.index(MERGED),
                "candidate_survivor": child_schedule.index(MERGED)}
    need(ordinals == {"parent_retired": 3308, "parent_survivor": 4114, "candidate_survivor": 3310},
         "literal ordered schedule positions of the paid relay")
    return ordinals


def rank_lookup(frames):
    spans = []
    for frame in frames:
        span = {0}
        for direction in frame:
            need(type(direction) is int and 0 < direction < 512 and direction not in span,
                 "independent literal binary chart")
            span |= {old ^ direction for old in span}
        spans.append(span)

    def rank(a, b, productive=False):
        need(0 <= a < len(spans) and 0 <= b < len(spans)
             and (spans[a] < spans[b] or (not productive and spans[b] < spans[a])),
             "strict nested paid or productive boundary")
        return abs(len(frames[a]) - len(frames[b]))

    return rank


def reject(action, reason):
    try:
        action()
    except ValueError as error:
        need(str(error) == reason, f"control reached its expected rejection: {reason}")
        return
    raise ValueError(f"invalid mutant accepted: {reason}")


def caller_replays(word, tape):
    from caller16 import signed_caller
    from reference_caller import caller_replay

    signed = signed_caller(tape, word, 2025, 9)
    reference = caller_replay(tape, word)
    signatures = (("fixed_caller_paid", "paid"), ("fixed_root_targets", "targets"), ("uses", "uses"),
                  ("root_owners", "root_owners"), ("exact_preproduct_divisions", "exact_preproduct_divisions"),
                  ("peak_scaled_mass", "peak_scaled_mass"), ("dyadic_height", "dyadic_height"))
    for name, old_name in signatures:
        need(signed[name] == reference[old_name], f"two exact signed caller replays agree: {name}")
    need(signed["calls"] == reference["calls"] == STAGES and reference["fresh_helpers"] == 17616
         and signed["exact_preproduct_divisions"] == 153295
         and sum(signed["fixed_caller_paid"].values()) == 3552
         and sum(signed["fixed_root_targets"].values()) == signed["root_owners"] == 3536,
         "all signed stages and fixed tariffs")
    fault = deepcopy(tape)
    joint = next(event for event in fault["events"] if event[0] == "J")
    joint[2][1] = joint[2][0]
    reject(lambda: signed_caller(fault, word, 2025, 9), "joint owner alias")
    return signed


def stage_invoice(word, tape, graphs, paid_orders, signed, source_binding):
    from caller16 import literal_layout
    from network import main_roles

    stages, types, role_sets = literal_layout(tape, word)
    main = set(main_roles(word))
    helpers = sorted(set(range(PUBLIC)) - main)
    roots = {("main", port, role) for kind, spec in types.items()
             for port in spec["ports"] for role in role_sets[kind]}
    hosted = word["hosted"]
    extra = dict(zip(hosted["Dports"], zip(hosted["X2"], hosted["Y2"], strict=True), strict=True))
    need((len(main), len(helpers), len(roots)) == (400, 1101, 3536), "complete stage partitions")
    rank = rank_lookup(word["frames"])
    target_ranks = {r: rank(word["initial"][r], word["final"][r], productive=True) for r in helpers}
    need(all(target_ranks[r] == 4 and (word["initial"][r], word["final"][r]) == (3, 237)
             for r in (325, 1087)) and target_ranks[RELAY_OWNER] == 9,
         "same arbitrary helper boundaries, including relay public owner")
    targets = Counter()
    paid = {kind: Counter() for kind in graphs}
    paid_digest = {kind: sha256() for kind in graphs}
    target_digest = sha256()
    owner_rows, stage_rows = [], []
    helper_owners = set()
    for clock, event in enumerate(tape["events"]):
        if event[0] != "J":
            continue
        _, stage, a, b = event
        owners = {}
        for port, x in enumerate(word["live"]):
            slots = (x, x + 112, *extra[port]) if port in extra else (x, x + 112)
            roles = a if port in extra else b[:2]
            for slot, role in zip(slots, roles, strict=True):
                tag = ("main", port, role)
                need(slot not in owners and tag in roots, "injective actual stage main role")
                owners[slot] = tag
        need(owners.keys() == main and len(set(owners.values())) == 400, "all main slots bound")
        for role, target_rank in target_ranks.items():
            tag = ("helper", stage, role)
            need(tag not in roots and tag not in helper_owners, "independent fresh helper input and return")
            owners[role] = tag
            helper_owners.add(tag)
            targets[target_rank] += 1
            target_digest.update(encoded([clock, tag, word["initial"][role], word["final"][role], target_rank, tag]) + b"\n")
        need(owners.keys() == set(range(PUBLIC)) and len(set(owners.values())) == PUBLIC,
             "complete distinct raw public owner assignments")
        owner_map = sorted(owners.items())
        owner_rows.append([stage, owner_map])
        for kind, graph in graphs.items():
            for key in paid_orders[kind]:
                a, b = graph.moves[key]
                weight = rank(a, b)
                paid[kind][weight] += 1
                tag = ("bank_sender_invocation", stage, key)
                paid_digest[kind].update(encoded([clock, tag, a, b, weight]) + b"\n")
        stage_rows.append({"stage": stage, "clock": clock,
                           "owner_map_sha256": digest(encoded(owner_map)),
                           "ordered_positive_paid": {kind: len(keys) for kind, keys in paid_orders.items()},
                           "independent_native_helpers": len(target_ranks),
                           "retained_relay_owner_tag": owners[RELAY_OWNER]})
    from upstream_application import digest as phase_digest

    need(digest(encoded(owner_rows)) == source_binding["owner_map_digest"] == phase_digest(owner_rows)
         and [r["stage"] for r in stage_rows] == list(range(1, stages + 1))
         and len(helper_owners) == 17616, "same actual stage owners across the supplied word and both banks")
    need(paid["parent"] == {rank: STAGES * count for rank, count in source_binding["native_paid"].items()}
         and targets == {rank: STAGES * count for rank, count in source_binding["native_targets"].items()}
         and signed_delta(paid["parent"], paid["candidate"]) == PAID_DELTA,
         "exact native paid edit and unchanged positive helpers")
    fixed_paid, fixed_targets = Counter(signed["fixed_caller_paid"]), Counter(signed["fixed_root_targets"])
    reference = load(DATA / "SOURCE-INVOICE.json", INVOICE)
    bills = {}
    for kind, tally in paid.items():
        p, t = fixed_paid + tally, fixed_targets + targets
        expected_paid = 101856 if kind == "parent" else 101840
        need(all(1 <= r <= 137 and v > 0 for h in (p, t) for r, v in h.items())
             and sum(p.values()) == expected_paid and sum(t.values()) == 21152
             and sum(r * (t[r] - p[r]) for r in p.keys() | t.keys()) == 1328,
             "complete actual positive invoice and rank mass surplus")
        bills[kind] = dict(reference, paid={str(r): p[r] for r in sorted(p)},
                           targets={str(r): t[r] for r in sorted(t)})
    need(bills["parent"] == reference
         and {str(r): v for r, v in source_binding["paid"].items()} == reference["paid"]
         and {str(r): v for r, v in source_binding["targets"].items()} == reference["targets"],
         "independent raw owner-census and folded registered caller match the supplied #7700 invoice")
    return bills, {
        "stages": stage_rows, "all_stage_owner_digest": source_binding["owner_map_digest"],
        "main_slots_per_stage": len(main), "root_owners": len(roots), "fresh_helpers": len(helper_owners),
        "native_paid_occurrences": {kind: dict(hist) for kind, hist in paid.items()},
        "native_paid_occurrence_sha256": {kind: h.hexdigest() for kind, h in paid_digest.items()},
        "native_helper_target_occurrences": dict(targets), "native_helper_target_sha256": target_digest.hexdigest(),
        "independent_helper_325_and_1087_examples": source_binding["role_325_and_1087_helper_owners"],
    }


def verify():
    check_sources()
    from binding16 import complete_binding
    from native import check_endpoints

    word, tape = read_data("WORD.json.gz"), read_data("CALLER.json.gz")
    need(word["public"] == PUBLIC and word["owned_fields"] == 68 and len(word["ports"]) == len(set(word["ports"])) == 104,
         "fixed supplied ordered port layout and public count")
    need(digest((DATA / "CERTS.json").read_bytes()) == SOURCE_CERTS, "supplied source certificate custody")
    raw = {kind: read_data(f"{kind.upper()}-GRAPH.json.gz") for kind in ("parent", "candidate")}
    graphs = {kind: decode_graph(raw[kind], word, paid) for kind, paid in (("parent", 6144), ("candidate", 6143))}
    need(raw["parent"]["metadata"]["kind"] == "parent" and raw["candidate"]["metadata"]["kind"] == "candidate"
         and raw["candidate"]["metadata"]["source_banked_graph_sha256"] == PARENT,
         "exact parent and child graph roles")
    orders = {kind: [key for key in raw[kind]["schedule"] if key in graph.moves]
              for kind, graph in graphs.items()}
    relay_ordinals = relay_contract(graphs["parent"], graphs["candidate"],
                                    raw["parent"]["schedule"], raw["candidate"]["schedule"], word)
    signed = caller_replays(word, tape)
    by_q = load(DATA / "CALLER-PHASE-BASES.json", PHASE_BASES)["by_q"]
    need({str(q) for q in word["ports"]} <= by_q.keys(), "every actual head has its retained phase basis")
    phases = {"recipes": [{"q": q, "idle_children": [{"orthogonal_axes": by_q[str(q)]}]}
                          for q in word["ports"]]}
    source = complete_binding(word, tape, phases, signed)
    need(source["phase_digest"] == PHASE_DIGEST and source["contacts"] == source["nonzero_contact_translations"] == 12800
         and source["negative_root_ordinary_corrections"] == 3536 and source["phase_omission_rejected"],
         "actual 137-axis phase contacts and root translations")
    invoices, owners = stage_invoice(word, tape, graphs, orders, signed, source)
    print("PASS_CF6A_RELAY_SIGNED_ROOTS", signed["root_owners"], flush=True)
    native = {kind: check_endpoints(graph, word) for kind, graph in graphs.items()}
    need(all(r["public"] == PUBLIC and r["mains"] == 400 and r["odd"] == 2025 and r["dyadic_height"] == 20
             for r in native.values()), "both full native endpoint maps and hereditary grids")
    ordinary = {
        kind: {"root_owners": signed["root_owners"], "fresh_helper_owners": owners["fresh_helpers"],
               "root_head_translations": source["negative_root_ordinary_corrections"],
               "main_phase_contacts": source["contacts"],
               "odd_boundary_conversions": 2 * (signed["root_owners"] + STAGES * n["public"]),
               "native_helper_boundary_maps": 2 * owners["fresh_helpers"]}
        for kind, n in native.items()
    }
    return {"status": STATUS, "source_head": SOURCE_HEAD, "source_word_sha256": SOURCE_WORD,
            "graphs": {"parent": PARENT, "candidate": CANDIDATE}, "caller_sha256": CALLER,
            "published_parent_invoice_sha256": INVOICE, "phase_bases_sha256": PHASE_BASES,
            "signed": signed, "owners": owners, "native": native, "invoices": invoices,
            "relay_zero_based_schedule_ordinals": relay_ordinals,
            "signed_paid_delta": PAID_DELTA, "signed_target_delta": {},
            "ordinary_occurrences": ordinary,
            "source_phase": {k: source[k] for k in ("phase_digest", "contacts", "nonzero_contact_translations",
                                                    "negative_root_ordinary_corrections", "phase_omission_rejected")},
            "supplied_raw_paid_owner_occurrence_sha256": source["ordered_paid_digest"],
            "controls": {"aliased_joint_stage": "rejected", "omitted_phase_translation": "rejected"}}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", "--output", type=Path, required=True)
    args = parser.parse_args()
    result = verify()
    write(args.out, result)
    candidate = result["invoices"]["candidate"]
    print(result["status"], sum(candidate["paid"].values()), sum(candidate["targets"].values()), flush=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Verify the literal 16-stage chart-595 caller, owner maps and signed tariff."""

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
PARENT_HEAD = "1b4a4d6f9370b8c93b3f769a6229a9111ef3940e"
PARENT = "1f082936ada08b5138b7d13e33368bd21c6f46632c5319a348e2f2a8e0021150"
PARENT_GZIP = "8e28c1d403145ca5d72521f4acd7e068603598334c87f18f2fefb738844a1970"
CANDIDATE = "d5dab11bb773bf5beb8ae2998be1282b243e2d1606c5257896a037c9b52c5c3b"
EDIT = "c8a914049eb36f5f307dfabef080169bbee06c024eab77b75249566028ca3fcf"
NATIVE_SOURCE = "ee251f6005d2a92b887c5b804bd7aac05989d278b2c9ccb3c3091b50d533b08d"
CALLER = "62d94fb992acab0a71c3d12f22be4ce63f4f65e5cbe3f420b93aa1393ffa8dcf"
CALLER_GZIP = "d889996a337f648087208ab51c98eaf052705d4fca88b5d01b6e9257a829897a"
LAYOUT = "622c6f458eba2dab0fdfd6050303cbc16ad684ab8b834c7df568264e4cf01db6"
PHASE_BASES = "325a1eb4aa7fe5f918b1d8344b88ad132ef4606268bccec20f223ace5feda18b"
INVOICE = "a9aecf52d99d5370506b9dc6d03799241bebd2c03bbdcfa2dd5f45ec03c9d70d"
PHASE_DIGEST = "29196a9aa29ecf4b3705a6346c40642eef9b14600ccc832210df91c3e4f84f50"
ENGINE = HERE / "engines/caller"
ENGINE_PINS = {
    "binding16.py": "589058311e44f2d8909495c005bee6d54828ebe561d4673b599193d269006170",
    "caller16.py": "ced48867f07ca0143604aa98cfd74fa7453696b9d3221f7c230d73e9ab9ba81f",
    "network.py": "a9169fd6ad0a13c69cf39bd32649d53256f6d6fa2ed2ceda854f848b64f4c546",
    "native.py": "788465324eb8693a698c75cb3dfdf1b82297324d5583910107ecad4600645e43",
    "reference_caller.py": "9bfb77250ca4826c1098b896769dc504b587c8c0dac634dd07012150fc8dde37",
    "upstream_application.py": "d98987db98553dc55bfc80e3ca47abfcd51c57af6f8cda61101391d8eae94184",
}


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


def check_sources():
    for name, expected in ENGINE_PINS.items():
        need(digest((ENGINE / name).read_bytes()) == expected, f"vendored engine source {name}")
    if str(ENGINE) not in sys.path:
        sys.path.insert(0, str(ENGINE))


def decode_graph(raw, role_count):
    from network import Network

    moves = {key: (a, b) for key, a, b in raw["moves"]}
    forms = {key: {donor: Fraction(value) for donor, value in row} for key, row in raw["forms"]}
    need(raw["first_output"] == 150522 and len(raw["initial"]) == len(raw["final"]) == role_count
         and len(moves) == len(raw["moves"]) == 6142
         and len(forms) == len(raw["forms"]) == 6142 + role_count
         and all(len(forms[key]) == len(row) and all(forms[key].values())
                 for key, row in raw["forms"]), "complete literal native input, slots and terminal rows")
    graph = Network(raw["first_output"], raw["initial"], raw["final"], moves, forms)
    graph.schedule()
    observed = {key: ordinal for ordinal, key in enumerate(raw["schedule"])}
    need(len(observed) == len(raw["schedule"]) and observed.keys() == forms.keys()
         and all(donor < 0 or observed[donor] < observed[row]
                 for row, terms in forms.items() for donor in terms),
         "exact cochart and acyclic declared bank execution order")
    return graph


def same_paid_contract(parent_raw, child_raw):
    peer, child = decode_graph(parent_raw, 1501), decode_graph(child_raw, 1502)
    metadata = child_raw["metadata"]
    need(parent_raw["metadata"]["source_word_sha256"] == NATIVE_SOURCE
         and parent_raw["metadata"]["caller_sha256"] == CALLER
         and metadata["source_pr_head"] == PARENT_HEAD
         and metadata["source_bank_graph_sha256"] == PARENT
         and metadata["edit_sha256"] == EDIT
         and metadata["caller_sha256"] == CALLER
         and child_raw["frames"] == parent_raw["frames"], "frozen native precursor, caller and phase bases")
    need(peer.moves == child.moves, "all ordered paid keys and endpoint frames retained")
    old_order = [k for k in parent_raw["schedule"] if k in peer.moves]
    new_order = [k for k in child_raw["schedule"] if k in child.moves]
    need(old_order == new_order, "same physical paid invocation order")
    need(child.initial[:-1] == peer.initial and
         [r for r in range(1501) if child.final[r] != peer.final[r]] == [281] and
         (peer.initial[281], peer.final[281], child.final[281]) == (3, 127, 595) and
         (child.initial[1501], child.final[1501]) == (595, 127),
         "one exact old-owner terminal and one fresh helper owner")
    return peer, child, old_order


def rank_map(frames):
    spans = []
    for basis in frames:
        span = {0}
        for direction in basis:
            need(type(direction) is int and 0 < direction < 512 and direction not in span,
                 "independent literal binary frame")
            span |= {v ^ direction for v in span}
        spans.append(span)

    def rank(a, b, productive=False):
        need(0 <= a < len(spans) and 0 <= b < len(spans)
             and (spans[a] < spans[b] or (not productive and spans[b] < spans[a])),
             "positive nested endpoint")
        return abs(len(frames[a]) - len(frames[b]))

    return rank


def reject(action, explanation):
    try:
        action()
    except ValueError as error:
        need(explanation in str(error), "control ran to its known rejection")
        return
    raise ValueError(f"invalid mutation accepted: {explanation}")


def stage_bindings(layout, tape, graphs, paid_order, signed, phase_bases, rank):
    from binding16 import contact_phase
    from caller16 import literal_layout
    from upstream_application import boundary

    n_stages, types, role_sets = literal_layout(tape, layout)
    hosted = layout["hosted"]
    extra = dict(zip(hosted["Dports"], zip(hosted["X2"], hosted["Y2"], strict=True), strict=True))
    main = set(layout["live"]) | {r + 112 for r in layout["live"]} | set(hosted["X2"]) | set(hosted["Y2"])
    roots = {("main", port, role) for block, spec in types.items()
             for port in spec["ports"] for role in role_sets[block]}
    need(len(main) == 400 and len(roots) == signed["root_owners"] == 3536,
         "distinct main fields and same-owner root returns")
    phase_rows, reports = [], []
    inventories = {kind: {r: rank(graph.initial[r], graph.final[r], productive=True)
                          for r in range(len(graph.initial)) if r not in main}
                   for kind, graph in graphs.items()}
    target_hash = {kind: sha256() for kind in graphs}
    paid_hash = sha256()
    actual_native_paid = Counter()
    actual_native_targets = {kind: Counter() for kind in graphs}
    seen_helpers = {kind: set() for kind in graphs}
    negative_control = False
    frames = layout["frames"]
    for clock, event in enumerate(tape["events"]):
        if event[0] != "J":
            continue
        _, stage, a, b = event
        main_for_stage = {}
        for port, (x, q) in enumerate(zip(layout["live"], layout["ports"], strict=True)):
            y = x + 112
            final_axes = frames[layout["final"][y]]
            need(frames[layout["initial"][x]] == [q]
                 and frames[layout["initial"][y]] == []
                 and frames[layout["final"][x]] == [1 << j for j in range(9)]
                 and len(final_axes) == 8 and all((axis & q).bit_count() % 2 == 0 for axis in final_axes),
                 "main input head, helper-basis companion and full output")
            if port in extra:
                u, v = extra[port]
                need(all(layout[key][u] == layout[key][x] and layout[key][v] == layout[key][y]
                         for key in ("initial", "final")), "second-plane exact chart interfaces")
                assignments = zip((x, y, u, v), a, strict=True)
            else:
                assignments = zip((x, y), b[:2], strict=True)
            for slot, root in assignments:
                tag = ("main", port, root)
                need(tag in roots and slot not in main_for_stage, "stage owner assignment")
                main_for_stage[slot] = tag
            phases, witness = contact_phase(q, phase_bases[str(q)], stage, tape["ambient_rank"])
            phase_rows.append([clock, port, phases, 2 if port in extra else 1])
            if witness is not None and not negative_control:
                transform, (before, after) = witness
                reject(lambda: boundary(before, after, transform, omit_translation=True),
                       "forward contact includes its phase")
                negative_control = True
        need(set(main_for_stage) == main and len(set(main_for_stage.values())) == 400,
             "all 400 phase-specialized main bindings are injective")
        for key in paid_order:
            pair = graphs["peer"].moves[key]
            legs = rank(*pair)
            actual_native_paid[legs] += 1
            paid_hash.update(encoded([stage, clock, key, *pair, legs]) + b"\n")
        record = {"stage": stage, "caller_clock": clock,
                  "main_binding_sha256": digest(encoded(sorted(main_for_stage.items()))),
                  "main_owner_count": len(main_for_stage), "helpers": {}, "split": []}
        for kind, graph in graphs.items():
            helpers = inventories[kind]
            owners = dict(main_for_stage)
            for role, h_rank in sorted(helpers.items()):
                tag = ("helper", stage, role)
                need(tag not in seen_helpers[kind] and tag not in roots, "independently supplied helper job")
                seen_helpers[kind].add(tag)
                owners[role] = tag
                ingress, egress = graph.initial[role], graph.final[role]
                actual_native_targets[kind][h_rank] += 1
                target_hash[kind].update(encoded([clock, tag, ingress, egress, h_rank, tag]) + b"\n")
                if role in {281, 325, 1087, 1501}:
                    record["split"].append([kind, tag, ingress, egress, h_rank, tag])
            need(len(owners) == len(set(owners.values())) == len(graph.initial)
                 and set(owners) == set(range(len(graph.initial))), "complete stage input and final owner matching")
            record["helpers"][kind] = len(helpers)
        reports.append(record)
    need([r["stage"] for r in reports] == list(range(1, n_stages + 1))
         and all((len(seen_helpers[k]), len(inventories[k])) == expected
                 for k, expected in (("peer", (17616, 1101)), ("candidate", (17632, 1102)))),
         "all 16 fresh helper groups")
    need(all(graph.initial[r] == 3 and graph.final[r] == 237
             and inventories[kind][r] == 4 for kind, graph in graphs.items() for r in (325, 1087)),
         "explicit original arbitrary-input rank-four helpers")
    need(inventories["peer"][281] == 9 and inventories["candidate"][281] == 1
         and inventories["candidate"][1501] == 8, "literal 9 to 1+8 target split")
    contacts = sum(4 * row[3] for row in phase_rows)
    need(contacts == 12800 and negative_control and digest(encoded(phase_rows)) == PHASE_DIGEST,
         "retained exact contact phases and rejected missing translation")
    root_translations = sum(len(spec["ports"]) for spec in types.values()
                            for phase, _, *_ in spec["diagonal"] if phase == -1)
    need(root_translations == len(roots), "complete ordinary head translations")
    return {"stages": reports, "root_owners": len(roots),
            "ordinary_root_translations": root_translations, "main_contacts": contacts,
            "main_contact_digest": PHASE_DIGEST, "omitted_translation_rejected": negative_control,
            "fresh_helpers": {k: len(v) for k, v in seen_helpers.items()},
            "native_paid_occurrences": dict(actual_native_paid),
            "native_target_occurrences": {kind: dict(hist) for kind, hist in actual_native_targets.items()},
            "paid_occurrence_sha256": paid_hash.hexdigest(),
            "target_occurrence_sha256": {kind: h.hexdigest() for kind, h in target_hash.items()}}


def whole_invoices(owners, signed, reference):
    invoices = {}
    for kind in ("peer", "candidate"):
        paid = Counter(signed["fixed_caller_paid"])
        paid.update(owners["native_paid_occurrences"])
        target = Counter(signed["fixed_root_targets"])
        target.update(owners["native_target_occurrences"][kind])
        invoice = dict(reference, paid={str(r): paid[r] for r in sorted(paid)},
                       targets={str(r): target[r] for r in sorted(target)})
        count = 21152 if kind == "peer" else 21168
        need(sum(paid.values()) == 101824 and sum(target.values()) == count
             and sum(r * (target[r] - paid[r]) for r in target.keys() | paid.keys()) == 1328,
             "complete literal 16-stage paid and target totals")
        invoices[kind] = invoice
    need(invoices["peer"] == reference, "literal peer reproduces committed #7682 invoice")
    need(invoices["peer"]["paid"] == invoices["candidate"]["paid"], "paid delta zero")
    p, c = (Counter(row["targets"]) for row in invoices.values())
    need(c - p == Counter({"1": 16, "8": 16}) and p - c == Counter({"9": 16}),
         "fresh target fully charged against surrendered rank-nine helper")
    return invoices


def main():
    parser = ArgumentParser(description=__doc__)
    for flag in ("parent", "candidate", "caller", "out"):
        parser.add_argument(f"--{flag}", type=Path, required=True)
    parser.add_argument("--candidate-sha256", required=True)
    args = parser.parse_args()
    check_sources()
    from caller16 import signed_caller
    from native import check_endpoints
    from reference_caller import caller_replay

    need(args.candidate_sha256 == CANDIDATE, "declared qualification identity")
    parent_raw = load(args.parent, PARENT_GZIP, PARENT, canonical=True)
    child_raw = load(args.candidate, decoded_pin=CANDIDATE, canonical=True)
    peer, child, paid_order = same_paid_contract(parent_raw, child_raw)
    tape = load(args.caller, CALLER_GZIP, CALLER)
    source = load(HERE / "data/CALLER-LAYOUT.json", LAYOUT)
    need(source["source_word_sha256"] == NATIVE_SOURCE and source["public"] == 1501,
         "bound layout from native precursor")
    layout = dict(source, **{key: parent_raw[key] for key in ("initial", "final", "frames")})
    child_layout = dict(layout, public=1502, initial=child.initial, final=child.final)
    phases = load(HERE / "data/CALLER-PHASE-BASES.json", PHASE_BASES)["by_q"]
    reference = load(HERE / "data/PARENT-INVOICES.json", INVOICE)["candidate"]
    need(reference["contract"]["ambient_rank"] == 137, "actual signed 137-axis contract")
    signed = signed_caller(tape, layout, 2025, 9)
    older = caller_replay(tape, child_layout)
    for a, b in (("fixed_caller_paid", "paid"), ("fixed_root_targets", "targets"), ("uses", "uses"),
                 ("root_owners", "root_owners"), ("exact_preproduct_divisions", "exact_preproduct_divisions"),
                 ("peak_scaled_mass", "peak_scaled_mass"), ("dyadic_height", "dyadic_height")):
        need(signed[a] == older[b], f"two exact signed caller replays agree: {a}")
    need(signed["calls"] == older["calls"] == 16 and older["fresh_helpers"] == 17632,
         "all exact native occurrences over the literal tape")
    fault = deepcopy(tape)
    first_joint = next(e for e in fault["events"] if e[0] == "J")
    first_joint[2][1] = first_joint[2][0]
    reject(lambda: signed_caller(fault, layout, 2025, 9), "joint owner alias")
    print("PASS_CHART595_SIGNED_ROOTS 3536", flush=True)
    graphs = {"peer": peer, "candidate": child}
    owners = stage_bindings(layout, tape, graphs, paid_order, signed, phases, rank_map(layout["frames"]))
    invoices = whole_invoices(owners, signed, reference)
    native = {"peer": check_endpoints(peer, layout), "candidate": check_endpoints(child, child_layout)}
    need(native["peer"]["public"] == 1501 and native["candidate"]["public"] == 1502
         and all(row["slots"] == 6142 and row["mains"] == 400 for row in native.values()),
         "complete normalized operator applied at every stage")
    result = {"status": "PASS_CHART595_ACTUAL16_CALLER", "parent_head": PARENT_HEAD,
              "graphs": {"peer": PARENT, "candidate": args.candidate_sha256}, "caller_sha256": CALLER,
              "source_layout_sha256": LAYOUT, "published_parent_invoice_sha256": INVOICE,
              "signed": signed, "owners": owners, "native": native,
              "invoices": invoices, "signed_paid_delta": {}, "signed_target_delta": {"1": 16, "8": 16, "9": -16},
              "ordinary_occurrences": {
                  kind: {"root_owners": 3536, "fresh_helper_owners": owners["fresh_helpers"][kind],
                         "root_head_translations": 3536,
                         "odd_boundary_conversions": 2 * (3536 + 16 * native[kind]["public"]),
                         "native_helper_boundary_maps": 2 * owners["fresh_helpers"][kind]}
                  for kind in graphs},
              "controls": {"aliased_joint_stage": "rejected", "omitted_phase_translation": "rejected"},
              "scope": "Exact normalized native outputs, same-owner stage bindings, matching main phase contexts and complete literal recursive tariff"}
    with args.out.open("x") as handle:
        json.dump(result, handle, sort_keys=True, indent=2)
        handle.write("\n")
    print(result["status"], sum(invoices["candidate"]["paid"].values()),
          sum(invoices["candidate"]["targets"].values()), flush=True)


if __name__ == "__main__":
    main()

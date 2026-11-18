#!/usr/bin/env python3
"""Independent row and signed-price comparison on the #7636 180-CLEAR words."""

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from fractions import Fraction
import gzip
from hashlib import sha1, sha256
from io import BytesIO
import json
from pathlib import Path
import sys
import tarfile
from types import ModuleType


SOURCE_HEAD = "7e68d8dd62d9a38c0f3c942262a7a85ca7125b75"
RELEASE_HEAD = "d12b854d4825e9edfa3a3466909e1abf3525e929"
CALLER_HEAD = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
CALLER_MEMBER = "caller/expected/ODD-TYPE-AB-CALLER.json"
CALLER_BLOB = "9451ceaf6e8e037894680b549f3ef41c21b260d7"
CALLER_BYTES = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
PEER_HEAD = "1e6fd08a7c4fb616ea802c5f432f58594d14a107"
BASE_SHA = "98b8c12ece2f323a6ff5cac8c7ed2f78ba3835438ea56b16bd7d4698ec5ad5b2"
RAW_B_SHA = "9b5b66e93f91c9538525d8d7b1278e0f203058d5cd4e1351fa06f8315fdaa555"
RAW_C_SHA = "375f924e1588893680d39a194d29e5400bec4ab7e0b5db24b05f4cfe6fd05e15"
LOW_BASE_SHA = "9ea1dab98cbd532af75ab780f284c513534d5df13fa366c3241a08a36c3610f8"
LOW_B_SHA = "2ea3a954f053b4cec96f1b03830353b79c32bb74160a023b96e40872759ad560"
LOW_C_SHA = "5f555d6bb6736eb0c98826d9822f077ce1cbc6875c46b0c10731737665dbda6e"
ENGINE_SHA = "8391dcaee8e81715c496f6215ef2541715e718daa13b16ae18a06f88e7094d91"
BASE_CLEAR_SHA = "94809b766d041f6bb400df151de5702c5e8ec0a8a47c80ddfe5b2b3a5e0f09d2"
RAW_C_CLEAR_SHA = "11caf0ddb32cbd94c4d5842a3324e6236b551090080dea5598c71f9dee72c7ff"
LOW_B_CLEAR_SHA = "1cf6339c3c4851393ddfb082a3fe4b9bf2db88920d6836e182292cf710de131f"
ANCHOR = 150836
WIDE = ("ADD", 841, 284, "23184221/921600", 127)
SPLIT = (("ADD", 841, 284, "25", 127), ("ADD", 841, 284, "144221/921600", 127))
CONTACT = {
    127153: (("MOVE", 902, 3, 618, False), (("MOVE", 902, 3, 373, False),)),
    127445: (("MOVE", 1091, 373, 618, False), ()),
    127446: (("ADD", 1091, 902, "1/2", 618), (("ADD", 1091, 902, "1/2", 373),)),
    127469: (("MOVE", 1091, 618, 733, False), (("MOVE", 1091, 373, 733, False),)),
    130068: (("MOVE", 902, 618, 913, False), (("MOVE", 902, 373, 913, False),)),
}
BYPASS = {
    131142: (("MOVE", 379, 748, 1065, False), ()),
    131294: (("MOVE", 379, 1065, 1072, False), (("MOVE", 379, 748, 1072, False),)),
}
LOWERING = {ANCHOR: (WIDE, SPLIT)}
BRACKETS = {
    "base": ("0.0036807241001", "0.0036807241002"),
    "B": ("0.0036810345257", "0.0036810345258"),
    "C": ("0.0036813560187", "0.0036813560188"),
}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def digest(raw):
    return sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def read(root, record, expected=None):
    body = (root / record["path"]).read_bytes()
    require(digest(body) == record["sha256"], f"transport custody {record['path']}")
    require(expected is None or record["sha256"] == expected, f"reference pin {record['path']}")
    return body


def exact_replay(root, entry):
    raw = read(root, entry, ENGINE_SHA)
    module = ModuleType("pinned_independent_role379")
    module.__file__ = str(root / entry["path"])
    sys.modules[module.__name__] = module
    exec(compile(raw, module.__file__, "exec"), module.__dict__)
    return module


def word(root, record, expected, exact_json):
    raw = gzip.decompress(read(root, record))
    require(digest(raw) == record["raw_sha256"] and (expected is None or expected == digest(raw)),
            f"decoded custody {record['path']}")
    parsed = exact_json(raw)
    return parsed, {"literal_sha256": digest(raw), "gzip_sha256": record["sha256"],
                    "canonical_sha256": digest(canonical(parsed))}


def verify_edit(base, changed, changes):
    require({k: v for k, v in base.items() if k != "program"} ==
            {k: v for k, v in changed.items() if k != "program"}, "unchanged ordered headers")
    clock_map = {}
    candidate = changed["program"]
    offset = 0
    records = []
    for old_clock, old_event in enumerate(base["program"]):
        expected, replacement = changes.get(old_clock, (tuple(old_event), (tuple(old_event),)))
        require(tuple(old_event) == expected and
                tuple(map(tuple, candidate[offset:offset + len(replacement)])) == replacement,
                f"literal tape mismatch {old_clock}/{offset}")
        if old_clock in changes:
            records.append({"source_clock": old_clock, "candidate_clock": offset if replacement else None,
                            "old": old_event, "new": replacement})
        if replacement:
            clock_map[old_clock] = offset
        offset += len(replacement)
    require(offset == len(candidate) and len(records) == len(changes), "literal exact suffix and edit count")
    return clock_map, records


def normalized(word_data):
    return [tuple(event[:-1]) for event in word_data["program"] if event[0] != "MOVE"]


def certificates(root, record, expected, engine, word_data):
    raw = read(root, record, expected)
    indexed = engine.exact_json(raw)["clear_event_index"]
    ordered = engine.source_certificates(raw, word_data["program"], 180)
    return indexed, ordered


def preserve_witnesses(source, candidate, by_source_clock):
    require({str(by_source_clock[int(clock)]): terms for clock, terms in source.items()} == candidate,
            "independent original-clock map for all 180 witness lists")


def width_failures(word_data):
    return [(clock, event, Fraction(event[-2]).numerator.bit_length())
            for clock, event in enumerate(word_data["program"])
            if event[0] in {"ADD", "COPY", "SCALE"} and Fraction(event[-2]).numerator.bit_length() > 24]


def lower_charge():
    original = Fraction(WIDE[3])
    terms = [Fraction(e[3]) for e in SPLIT]
    require(sum(terms) == original and all(t > 0 for t in terms), "exact positive adjacent same-role shear")
    require(all(e[:3] == WIDE[:3] and e[4] == WIDE[4] for e in SPLIT) and WIDE[1] != WIDE[2],
            "distinct and immutable donor in the split")

    def ordinary(value):
        n, d = abs(value.numerator), value.denominator
        return 4 * (n.bit_length() + n.bit_count() + d.bit_length() + 1)

    costs = [ordinary(t) for t in terms]
    require(sum(costs) == ordinary(original) == 236, "local split ordinary tariff")
    return {"ordinary_original": 236, "ordinary_inserted": costs, "scheduled_extra_services": 17 * 32,
            "old": WIDE, "new": SPLIT, "normalized_exact_shear": True}


def load_caller(root, record, engine):
    closure = read(root, record, "6f6f67b5b1ef44d6a5085dfd518c0b488ae91dbeee49d0bdbec4cf63a2f41735")
    with tarfile.open(fileobj=BytesIO(closure), mode="r:gz") as archive:
        member = archive.getmember(CALLER_MEMBER)
        require(member.isfile() and member.size == 117156, "exact caller member")
        body = archive.extractfile(member).read()
    require(digest(body) == CALLER_BYTES and sha1(f"blob {len(body)}\0".encode() + body).hexdigest() == CALLER_BLOB,
            "signed caller literal and Git identities")
    return engine.exact_json(body)


def recount_fixed_caller(caller):
    require(caller["schema"] == "mixed-root-caller/1" and (caller["stages"], caller["ambient_rank"]) == (17, 145),
            "exact signed-caller schema and ambient")
    types = caller["types"]
    ports = {name: info["ports"] for name, info in types.items()}
    all_ports = [port for group in ports.values() for port in group]
    require(set(types) == {"A", "B"} and list(map(len, (ports["A"], ports["B"]))) == [96, 8] and
            sorted(all_ports) == list(range(104)), "104 nonaliased caller ports with the exact partition")
    by_op = defaultdict(Counter)
    stages = []
    for event in caller["events"]:
        name = event[0]
        if name == "J":
            require(len(event) == 4 and len(set(event[2])) == 4 and event[3][0] != event[3][1],
                    "native occurrence shape")
            stages.append(event[1])
            continue
        op = event[1]
        require(name in ports, "outer operation type")
        if op == "QUERY":
            require(name == "A" and len(event) == 5 and event[4] in (-1, 1), "rank-one query shape")
            rank = 1
        elif op in {"IDLE_ONE", "IDLE_ODD"}:
            blocks = event[3]
            require(blocks and len(blocks) == len(set(blocks)) and
                    all(type(block) is int and 1 <= block <= 17 for block in blocks), "distinct idle blocks")
            if op == "IDLE_ODD":
                require(name == "B" and len(blocks) == 1 and event[4:] == [-1], "signed-idle query channel")
            rank = 8 * len(blocks) + (op == "IDLE_ODD")
        else:
            require(op in {"ADD", "SCALE", "SWAP", "LAMBDA"}, "unknown outer operation")
            continue
        for _ in ports[name]:
            by_op[f"{name}:{op}"][rank] += 1
    require(stages == list(range(1, 18)) and len(caller["events"]) == 4783, "all 17 ordered native occurrences")
    roots = {}
    for info in types.values():
        require(info["roles"] == len(info["diagonal"]) == 36, "declared productive owner count")
        for field, (q, central, *blocks) in enumerate(info["diagonal"], start=info["offset"]):
            require((q, central) == (-1, 0) and len(blocks) == 17 and set(blocks) <= {0, 1},
                    "declared output frame block pattern")
            rank = 1 + 8 * sum(blocks)
            for port in info["ports"]:
                require((port, field) not in roots, "duplicate productive owner")
                roots[port, field] = rank
    fixed_paid = sum(by_op.values(), Counter())
    fixed_targets = Counter(roots.values())
    require((sum(fixed_paid.values()), len(roots)) == (3776, 3744), "full fixed caller counts")
    return stages, fixed_paid, fixed_targets, by_op


def invoice(replay, stages, fixed_paid, fixed_targets):
    paid, targets = fixed_paid.copy(), fixed_targets.copy()
    for _ in stages:
        paid.update(replay["paid"])
        targets.update(replay["targets"])
    return {
        "schema": "integer-mult-recursive-invoice/v1",
        "contract": {"ambient_rank": 145, "boundary": "complete signed #7113 caller application with 17 native calls",
                     "model": "mixed-target-unnormalized-power-v1",
                     "rank_semantics": "H_r costs r^(1-C); debit surrendered productive fields"},
        "paid": {str(rank): count for rank, count in sorted(paid.items())},
        "targets": {str(rank): count for rank, count in sorted(targets.items())},
    }


def price(engine, locator, signed, claim, probe):
    weights = engine.signed_weights(signed)
    proposed = engine.approximate_grid(weights)
    require(tuple(proposed) == BRACKETS[locator], f"separate price bracket differs {locator}")
    summary = engine.price_bracket(weights, proposed)
    derivative = engine.signed_price(weights, Fraction(0), Fraction("0.00376669"), derivative=True)
    require(derivative[1] < 0 and sum(weights.values()) == 1424, "exact slope and rank surplus")
    at_claim = engine.signed_price(weights, claim, claim)
    at_probe = engine.signed_price(weights, probe, probe)
    require((at_claim[0] > 0 and at_probe[0] > 0) if locator == "C" else (at_claim[1] < 0 and at_probe[1] < 0),
            f"directed comparison at C claim and interior probe on {locator}")
    return summary | {"claim": str(claim), "probe": str(probe),
                      "at_claim": engine.outward_decimal(at_claim), "at_probe": engine.outward_decimal(at_probe),
                      "derivative_on_BIT_interval": engine.outward_decimal(derivative)}


def controls(engine, candidate, candidate_replay, masks, dims, cert, contact_clock, invoice_fn):
    first, series = cert[0]
    bad_clear = [(first, {**series, first[1]: Fraction(1)}), *cert[1:]]
    clear = engine.rejected({"clear_self"}, lambda: engine.interpret(candidate, masks, dims, bad_clear))
    contact = candidate["program"][contact_clock]
    require(contact == ["ADD", 1091, 902, "1/2", 373], "changed chart-373 contact")
    stale = engine.with_event(candidate, contact_clock, [*contact[:4], 618])
    chart = engine.rejected({"scalar_chart"}, lambda: engine.interpret(stale, masks, dims, cert))
    require(chart["clock"] == contact_clock, "stale chart rejected at changed contact")
    bad_contact = engine.with_event(candidate, contact_clock, [*contact[:3], "-1/2", 373])
    # A sign mutation touches no rank-carrying operation or target owner.
    require([e for e in candidate["program"] if e[0] == "MOVE"] ==
            [e for e in bad_contact["program"] if e[0] == "MOVE"], "same recursive invoice inputs")
    try:
        bad_replay = engine.interpret(bad_contact, masks, dims, cert)
    except engine.Refusal as failure:
        require(failure.record["code"] == "clear_reconstruction" and failure.record["clock"] > contact_clock,
                f"contact control reached unrelated failure {failure.record}")
        sign = failure.record
    else:
        require(invoice_fn(bad_replay) == invoice_fn(candidate_replay), "same exact signed invoice after sign flip")
        sign = engine.rejected({"final_row", "protected_value"}, lambda: engine.exact_compare(candidate_replay, bad_replay))
    require(len(width_failures(bad_contact)) == 0, "sign control remains literal-width legal")
    return {"wrong_contact_sign": sign, "stale_contact_chart": chart, "self_CLEAR": clear,
            "original_25_bit_words": "rejected_by_exact_literal_census"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    start = datetime.now(timezone.utc).isoformat()
    spec = json.loads(args.spec.read_bytes())
    require((spec["source_head"], spec["publication_head"], spec["caller_head"]) ==
            (SOURCE_HEAD, RELEASE_HEAD, CALLER_HEAD), "exact source lineage")
    root = args.spec.resolve().parent
    pins = spec["files"]
    engine = exact_replay(root, pins["interpreter"])
    inputs = {}
    bindings = {}
    for name, sha in (("base", BASE_SHA), ("raw_b", RAW_B_SHA), ("raw_c", RAW_C_SHA),
                      ("low_base", LOW_BASE_SHA), ("low_b", LOW_B_SHA), ("low_c", LOW_C_SHA)):
        inputs[name], bindings[name] = word(root, pins[name], sha, engine.exact_json)
    base = inputs["base"]
    require(base["schema"] == "p104-accumulated-block-composition/2" and
            (base["public"], base["owned_fields"], len(base["frames"]), len(base["program"])) ==
            (1501, 68, 1096, 202668), "180-word exact domain")
    require((base["initial"][457], base["initial"][461]) == (281, 285), "two fresh helper entrance charts")
    witness_sources = {
        "base": ("base_clear", BASE_CLEAR_SHA), "raw_c": ("raw_c_clear", RAW_C_CLEAR_SHA),
        "low_b": ("low_b_clear", LOW_B_CLEAR_SHA), "low_c": ("low_c_clear", RAW_C_CLEAR_SHA),
    }
    witness = {name: certificates(root, pins[key], expected, engine, inputs[name])
               for name, (key, expected) in witness_sources.items()}
    changes = {"raw_b": BYPASS, "raw_c": CONTACT | BYPASS, "low_base": LOWERING,
               "low_b": BYPASS | LOWERING, "low_c": CONTACT | BYPASS | LOWERING}
    receipt_edits = {}
    for name, edits in changes.items():
        order, receipt_edits[name] = verify_edit(base, inputs[name], edits)
        if name in witness:
            preserve_witnesses(witness["base"][0], witness[name][0], order)
    require(witness["raw_c"][0] == witness["low_c"][0], "no CLEAR moved by the late lowering")
    require(normalized(base) == normalized(inputs["raw_b"]) == normalized(inputs["raw_c"]) and
            normalized(inputs["low_base"]) == normalized(inputs["low_b"]) == normalized(inputs["low_c"]),
            "ordered normalized scalar and lifetime sequence")
    for name, clock in (("base", 150836), ("raw_b", 150835), ("raw_c", 150834)):
        require(width_failures(inputs[name]) == [(clock, list(WIDE), 25)], f"sole 25-bit guard on {name}")
    for name in ("low_base", "low_b", "low_c"):
        require(not width_failures(inputs[name]), f"lowered width gate on {name}")
    charges = lower_charge()
    caller = load_caller(root, pins["caller_archive"], engine)
    stages, fixed_paid, fixed_targets, paid_by_op = recount_fixed_caller(caller)
    peer = engine.exact_json(read(root, pins["peer_result"]))
    require(peer["K_paid"] == {str(k): v for k, v in fixed_paid.items()} and
            peer["K_T_declared_roots"] == {str(k): v for k, v in fixed_targets.items()},
            "literal residual agrees with exact #7661 independent accounting")

    def complete_invoice(result):
        return invoice(result, stages, fixed_paid, fixed_targets)

    masks, dims = engine.chart_catalogue(base["frames"])
    base_replay = engine.interpret(inputs["low_base"], masks, dims, witness["base"][1])
    old_replay = engine.interpret(inputs["low_b"], masks, dims, witness["low_b"][1])
    new_replay = engine.interpret(inputs["low_c"], masks, dims, witness["low_c"][1])
    for replay in (base_replay, old_replay, new_replay):
        require(len(replay["rows"]) == 1501 + 68 and len(replay["erasures"]) == 180 and
                len(replay["labels"]) == 68 and replay["peak"] == 50 and
                len(replay["observations"]) == 1049 and not replay["altered_helpers"], "protected full row domain")
    engine.exact_compare(base_replay, old_replay)
    engine.exact_compare(old_replay, new_replay)
    require(base_replay["scalar_units"] == old_replay["scalar_units"] == new_replay["scalar_units"],
            "same charged normalized scalar macro bill on the three lowered words")
    claim, probe = map(Fraction, (spec["claim"], spec["probe"]))
    require(Fraction(BRACKETS["B"][1]) < claim < probe < Fraction(BRACKETS["C"][0]) and
            ((probe - claim) / 7).numerator == 1, "strict funded low comparison and compiler probe spacing")
    results = {}
    for name, locator, replay, numerator in (
        ("low_base", "base", base_replay, 109652), ("low_b", "B", old_replay, 109635), ("low_c", "C", new_replay, 109618)
    ):
        signed = complete_invoice(replay)
        require(sum(signed["paid"].values()) == numerator and sum(signed["targets"].values()) == 22461,
                f"full signed paid/productive multiplicities on {locator}")
        results[name] = bindings[name] | {
            "head": SOURCE_HEAD, "full_signed_invoice": signed, "price": price(engine, locator, signed, claim, probe),
            "trace": engine.ordered_proof_trace(replay),
        }
    old, new = results["low_b"]["full_signed_invoice"], results["low_c"]["full_signed_invoice"]
    delta = {rank: new["paid"][rank] - count for rank, count in old["paid"].items()
             if new["paid"][rank] != count}
    require(delta == {"1": -34, "2": 34, "3": -17, "4": -17, "5": 17} and old["targets"] == new["targets"],
            "separate contact gain over pure low B at unchanged productive targets")
    contact_clock = next(e["candidate_clock"] for e in receipt_edits["low_c"] if e["source_clock"] == 127446)
    adverse = controls(engine, inputs["low_c"], new_replay, masks, dims, witness["low_c"][1],
                       contact_clock, complete_invoice)
    summary = {
        "result": "PASS_PAIRED_EXACT_REPLAY_AND_CONDITIONAL_PRICE",
        "started_at": start, "completed_at": datetime.now(timezone.utc).isoformat(),
        "source": results["low_b"], "candidate": results["low_c"], "matched_lowered_7636": results["low_base"],
        "publication_head": RELEASE_HEAD, "literal_edits_by_original_clock": receipt_edits, "raw_pins": bindings,
        "source_to_candidate_signed_paid_delta": delta, "signed_targets_equal": True,
        "caller": {"head": CALLER_HEAD, "sha256": CALLER_BYTES, "stages": stages, "events": 4783,
                   "fixed_paid": fixed_paid, "fixed_targets": fixed_targets, "fixed_paid_by_operation": paid_by_op,
                   "peer_7661_head": PEER_HEAD, "peer_7661_result_sha256": pins["peer_result"]["sha256"]},
        "lowering_tariff": charges, "controls": adverse, "changed_half_clock": contact_clock,
        "boundary": "180 ideal CLEAR lifetimes, chart-281 and chart-285 entrances, fixed-port signed invoice model."
                    " Exact rounding/divisibility at the contact, physical phase, resource and actual caller are separate gates.",
    }
    with args.out.open("x", encoding="utf-8") as handle:
        json.dump(summary, handle, sort_keys=True, indent=2)
        handle.write("\n")
    print(summary["result"], bindings["low_c"]["literal_sha256"], "180", "109618", "22461", flush=True)


if __name__ == "__main__":
    main()

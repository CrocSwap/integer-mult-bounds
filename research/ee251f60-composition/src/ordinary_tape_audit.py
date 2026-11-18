"""Parameterized ordinary and finite-count substitutions, not admission.

Uses pinned #7113 owning ordinary/signed calculation blocks only. No author
main, native endpoint, caller polynomial, bundle or historical replay runs.
Rohan Arun/OpenAI predecessor attribution is retained in vendor7113_ordinary.
New adapter: Apache-2.0, prepared with OpenAI Codex assistance.
"""

import argparse
import ast
import collections
import copy
import gzip
import hashlib
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

SOURCE_COMMIT = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
DEFAULT_SOURCE = Path(__file__).resolve().parent / "vendor7113_ordinary"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def read_json(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw), raw


def rational(value):
    need(type(value) in (str, int), "coefficient must be exact integer/rational text")
    return Q(value)


def load_sources(folder):
    pins, pin_bytes = read_json(folder / "SOURCE-PINS.json")
    need(pins["source_commit"] == SOURCE_COMMIT, "unexpected owning source version")
    sources = {}
    for item in pins["files"]:
        name = item["name"]
        need(Path(name).name == name, "source pin must be a direct member")
        raw = (folder / name).read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        need(len(raw) == item["bytes"] and digest(raw) == item["sha256"] and blob == item["git_blob"],
             "owning source bytes differ: " + name)
        sources[name] = raw.decode("utf-8")
    return sources, {"commit": SOURCE_COMMIT, "pins_sha256": digest(pin_bytes), "files": pins["files"],
                     "scope": "Source identification only; no candidate hash or census acceptance gate."}


def ordinary_function(sources, signed=False):
    original = sources["independent.py"]
    tree = ast.parse(original)
    definitions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "ordinary"]
    need(len(definitions) == 1, "one owning ordinary definition required")
    text = ast.get_source_segment(original, definitions[0])
    owner = ast.parse(sources["check_odd_partial_admission.py"])
    edits = []
    for node in ast.walk(owner):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "replace" and len(node.args) >= 2
                and all(isinstance(a, ast.Constant) and isinstance(a.value, str) for a in node.args[:2])):
            continue
        before, after = (a.value for a in node.args[:2])
        if before not in text or (not signed and before != "calls=18;"):
            continue
        need(text.count(before) == 1, "ambiguous owning ordinary adaptation")
        text = text.replace(before, after)
        edits.append({"before": before, "after": after})
    need(len(edits) == (3 if signed else 1), "owning stage/fused-route adaptation changed")
    # Only this calculation function is compiled, never the source main or
    # its heavyweight native()/caller()/invoices() entry points.
    namespace = {"F": Q, "Counter": collections.Counter}
    exec(compile(text, "pinned7113:ordinary", "exec"), namespace)  # noqa: S102 -- pinned ordinary function only
    return namespace["ordinary"], {"calculation_sha256": digest(text.encode()), "edits": edits}


def signed_surcharges(sources, caller, ordinary, caller_odd_scale=None):
    tree = ast.parse(sources["check_odd_partial_admission.py"])

    def target(node, variable, key=None):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            return False
        value = node.targets[0]
        if key is None:
            return isinstance(value, ast.Name) and value.id == variable
        return (isinstance(value, ast.Subscript) and isinstance(value.value, ast.Name)
                and value.value.id == variable and isinstance(value.slice, ast.Constant) and value.slice.value == key)

    start = next(i for i, node in enumerate(tree.body) if target(node, "surcharge"))
    key = "margin_to_billion" if caller_odd_scale is not None else "all_caller_scalar_surcharge"
    stop = next(i for i, node in enumerate(tree.body[start:], start) if target(node, "ordinary", key)) + 1
    nodes = ast.Module(body=tree.body[start:stop], type_ignores=[])
    namespace = {"Q": Q, "C": caller, "ordinary": copy.deepcopy(ordinary),
                 "odd_grid": {"caller_odd_scale": caller_odd_scale}}
    try:
        exec(compile(nodes, "pinned7113:signed-surcharges", "exec"), namespace)  # noqa: S102 -- pinned calculation AST only
    except AssertionError as error:
        raise ValueError("caller scalar is outside the owning signed-surcharge recipe") from error
    result = namespace["ordinary"]
    if caller_odd_scale is None:
        known = result.pop("conservative_total") + result["all_caller_scalar_surcharge"]
        result.pop("margin_to_billion")
        result["known_total_excluding_pending_odd_conversions"] = known
        result["charged_caller_odd_conversions"] = None
    return result, {"calculation_sha256": digest(ast.unparse(nodes).encode()),
                    "caller_odd_conversions_complete": caller_odd_scale is not None}


def validate_caller(caller):
    need(type(caller["stages"]) is int and caller["stages"] > 0, "positive caller stages required")
    need(type(caller["roles"]) is int and caller["roles"] > 0 and {"A", "B"} <= caller["types"].keys(),
         "caller roles and A/B types required")
    for kind in caller["types"].values():
        need(type(kind["roles"]) is int and kind["roles"] > 0 and len(kind["diagonal"]) == kind["roles"],
             "caller role/diagonal count mismatch")
        need(type(kind["offset"]) is int and 0 <= kind["offset"] <= caller["roles"] - kind["roles"],
             "caller type offset outside roles")
        need(len(kind["ports"]) == len(set(kind["ports"])) and all(type(p) is int and p >= 0 for p in kind["ports"]),
             "invalid caller ports")
        need(all(len(d) >= 2 and all(type(v) is int for v in d) for d in kind["diagonal"]), "invalid caller diagonal")
    stages = []
    lengths = {"ADD": 5, "SCALE": 4, "SWAP": 4, "QUERY": 5, "LAMBDA": 4, "IDLE_ONE": 4, "IDLE_ODD": 5}
    for event in caller["events"]:
        if event[0] == "J":
            need(len(event) == 4 and type(event[1]) is int, "malformed J event")
            stages.append(event[1])
            continue
        need(event[0] in caller["types"] and event[1] in lengths and len(event) == lengths[event[1]],
             "unsupported caller event")
        need(type(event[2]) is int and 0 <= event[2] < caller["roles"], "caller target outside roles")
        if event[1] in ("ADD", "SCALE"):
            need(rational(event[-1]) != 0, "zero caller scalar")
        if event[1] in ("IDLE_ONE", "IDLE_ODD"):
            need(event[3] and len(event[3]) == len(set(event[3])) and
                 all(type(s) is int and 1 <= s <= caller["stages"] for s in event[3]), "invalid idle stages")
    need(sorted(stages) == list(range(1, caller["stages"] + 1)), "one chronological native occurrence per caller stage required")


def native_inventory(word):
    n, banks = word["public"], word["owned_fields"]
    need(type(n) is int and n > 0 and type(banks) is int and banks >= 0 and
         len(word["initial"]) == len(word["final"]) == n, "invalid native field metadata")
    spans = []
    for frame in word["frames"]:
        span = {0}
        for vector in frame:
            need(type(vector) is int and 0 < vector < 512 and vector not in span, "invalid F2^9 frame basis")
            span |= {a ^ vector for a in span}
        spans.append(span)
    dimensions = [len(frame) for frame in word["frames"]]
    need(all(type(c) is int and 0 <= c < len(spans) for c in word["initial"] + word["final"]), "invalid native chart")
    live, charts = set(range(n)), list(word["initial"]) + [None] * banks
    paid, rises, opcodes = collections.Counter(), collections.Counter(), collections.Counter()
    peak = lifetimes = 0
    for event in word["program"]:
        op, r = event[:2]
        need(type(r) is int and 0 <= r < n + banks, "native field outside reserved stock")
        opcodes[op] += 1
        if op == "INIT":
            need(r >= n and r not in live and len(event) == 3 and 0 <= event[2] < len(spans), "invalid INIT")
            live.add(r)
            charts[r] = event[2]
            lifetimes += 1
            peak = max(peak, len(live) - n)
        elif op == "CLEAR":
            need(r >= n and r in live and charts[r] == event[2], "invalid CLEAR")
            live.remove(r)
            charts[r] = None
        elif op == "MOVE":
            _, _, a, b, owner = event
            need(type(a) is int and type(b) is int and 0 <= a < len(spans) and 0 <= b < len(spans), "invalid MOVE chart")
            need(r in live and charts[r] == a and owner == (r >= n), "invalid MOVE owner/source")
            need((spans[a] < spans[b]) or (owner and spans[b] < spans[a]), "non-nested native MOVE")
            rank = abs(dimensions[b] - dimensions[a])
            paid[rank] += 1
            if owner and dimensions[b] > dimensions[a]:
                rises[rank] += 1
            charts[r] = b
        elif op in ("ADD", "COPY", "SCALE"):
            need(r in live and charts[r] == event[-1], "invalid native arithmetic target")
            need(rational(event[2] if op == "SCALE" else event[3]) != 0, "zero native scalar")
            if op != "SCALE":
                need(event[2] in live and r != event[2] and charts[event[2]] == event[-1], "invalid native arithmetic source")
        else:
            raise ValueError("unsupported native opcode: " + str(op))
    need(live == set(range(n)) and charts[:n] == word["final"], "native final live/charts mismatch")
    mains = set(word["live"]) | {x + 112 for x in word["live"]} | set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"])
    need(all(type(r) is int and 0 <= r < n for r in mains), "native main label outside public fields")
    helpers = collections.Counter()
    for r in set(range(n)) - mains:
        need(spans[word["initial"][r]] < spans[word["final"][r]], "nonproductive declared helper")
        helpers[dimensions[word["final"][r]] - dimensions[word["initial"][r]]] += 1
    return {"public": n, "events": len(word["program"]), "paid": dict(paid), "helpers": dict(helpers),
            "rises": dict(rises), "lifetimes": lifetimes, "owned_peak": peak, "owned_fields": banks,
            "opcodes": dict(opcodes), "endpoint_checked": False, "CLEAR_relations_checked": False}


def histogram(value):
    result = {}
    for key, count in value.items():
        need(str(int(key)) == str(key) and int(key) > 0 and type(count) is int and count >= 0, "invalid invoice histogram")
        if count:
            result[int(key)] = count
    return result


def invoice_counts(caller, native):
    paid, targets = collections.Counter(), collections.Counter()
    for event in caller["events"]:
        if event[0] == "J":
            paid.update(native["paid"])
            targets.update(native["helpers"])
        else:
            ports = len(caller["types"][event[0]]["ports"])
            if event[1] == "QUERY":
                paid[1] += ports
            elif event[1] in ("IDLE_ONE", "IDLE_ODD"):
                paid[8 * len(event[3]) + (event[1] == "IDLE_ODD")] += ports
    for kind in caller["types"].values():
        for diagonal in kind["diagonal"]:
            targets[diagonal[0] % 2 + 8 * sum(diagonal[2:])] += len(kind["ports"])
    empty = targets.pop(0, 0)
    return {r: count for r, count in paid.items() if count}, {r: count for r, count in targets.items() if count}, empty


def receipt_member(packet, name):
    return packet["checks"][name] if "checks" in packet else packet


def caller_grid_scale(packet, caller_sha):
    if packet is None:
        return None
    record = receipt_member(packet, "ODD-CALLER-EXACT-GRID.json")
    need(record["caller_sha256"] == caller_sha, "caller-grid receipt does not bind this caller's bytes")
    scale = int(record["caller_odd_scale"])
    need(scale > 0 and scale % 2 == 1, "positive odd caller scale required")
    return scale


def native_grid_scale(packet, word_sha):
    if packet is None:
        return None
    recorded = packet.get("candidate_canonical_sha256", packet.get("word_canonical_sha256"))
    need(recorded == word_sha, "native-grid receipt does not bind this WORD")
    if "grid" in packet:
        scale = int(packet["grid"]["odd_den"])
    else:
        scale = int(packet["native_grid"]["odd_scale_lcm"])
    need(scale > 0 and scale % 2 == 1, "positive odd native scale required")
    return scale


def finite_counts(word, caller, invoice, native_odd=None, caller_odd=None, binding=None, word_sha=None, caller_sha=None):
    calls = caller["stages"]
    nonmove = sum(e[0] != "MOVE" for e in word["program"])
    macros = sum(len(caller["types"][e[0]]["ports"]) for e in caller["events"] if e[0] != "J")
    conversions = 2 * calls * word["public"] + 2 * sum(t["roles"] * len(t["ports"]) for t in caller["types"].values())
    coefficients = [rational(e[2] if e[0] == "SCALE" else e[3]) for e in word["program"] if e[0] in ("ADD", "COPY", "SCALE")]
    coefficients += [rational(e[-1]) for e in caller["events"] if e[0] != "J" and e[1] in ("ADD", "SCALE")]
    def smooth(value):
        for prime_factor in (2, 3, 5):
            while value % prime_factor == 0:
                value //= prime_factor
        return value == 1

    native_literals = [(e[0], rational(e[2] if e[0] == "SCALE" else e[3]))
                       for e in word["program"] if e[0] in ("ADD", "COPY", "SCALE")]
    for value in (native_odd, caller_odd):
        if value is not None:
            coefficients.extend([Q(value), Q(1, value)])
    literal_bits = max((abs(q.numerator).bit_length() for q in coefficients), default=0)
    result = {"native_nonMOVE_per_call": nonmove, "native_instances": calls * nonmove,
              "caller_macros": macros, "conversions": conversions,
              "scalar_services_arithmetic_at_constant32": 32 * (calls * nonmove + macros + conversions),
              "constant32_applicability": "PENDING", "precision_context": "PENDING",
              "max_literal_scalar_numerator_bits": literal_bits,
              "literal_bit_bound24_complete": native_odd is not None and caller_odd is not None,
              "literal_bit_bound24_holds_if_complete": literal_bits <= 24 if native_odd is not None and caller_odd is not None else None,
              "native_odd_scale": native_odd, "caller_odd_scale": caller_odd,
              "observed_original_native_scalar_conditions": {
                  "abs_coefficient_plus1_lt_2pow16": all(abs(q) + 1 < 2**16 for _, q in native_literals),
                  "denominators_235_smooth": all(smooth(q.denominator) for _, q in native_literals),
                  "SCALE_numerators_235_smooth": all(smooth(abs(q.numerator)) for op, q in native_literals if op == "SCALE"),
                  "scope": "Observed owning-source scalar conditions, not complete model admission or a new acceptance gate."},
              "map_count": None,
              "scope": "Exact substitutions in declared finite-count formulas. Constant32, context c/H/Kstar, rounded bounds, physical binding, and all proof applicability remain pending. Literal bits are not row-numerator bits."}
    if binding is not None:
        record = receipt_member(binding, "ODD-PHYSICAL-BINDING.json")
        need(record["native_sha256"] == word_sha and record["caller_sha256"] == caller_sha, "binding receipt input mismatch")
        b = record["occurrence_and_geometry"]
        need(b["native_calls"] == calls and b["paid_positions"] == sum(histogram(invoice["paid"]).values()) and
             b["productive_fields"] == sum(histogram(invoice["targets"]).values()), "binding/invoice count mismatch")
        idle = sum(len(caller["types"][e[0]]["ports"]) for e in caller["events"] if e[:2] == ["B", "IDLE_ODD"])
        slots = 2 * b["paid_positions"] + 2 * b["productive_fields"] + b["native_contact_boundaries"]
        slots += 2 * b["idle_uses"] + 3 * b["query_uses"] + b["lambda_uses"] + idle
        records = 4 * (b["ambient"] + 1) ** 2
        result["map_count"] = {"map_slots": slots, "records_per_map": records, "elementary_records": slots * records,
                               "scope": "Bound-receipt arithmetic only; receipt validity and compiler applicability not independently proved."}
    return result


def audit(word, invoice, caller, sources, caller_sha, caller_grid=None, native_grid=None, binding=None):
    validate_caller(caller)
    need(invoice["schema"] == "integer-mult-recursive-invoice/v1", "wrong invoice schema")
    declared_paid, declared_targets = histogram(invoice["paid"]), histogram(invoice["targets"])
    native = native_inventory(word)
    reconstructed_paid, reconstructed_targets, empty = invoice_counts(caller, native)
    matched = reconstructed_paid == declared_paid and reconstructed_targets == declared_targets
    raw_fn, raw_code = ordinary_function(sources, signed=False)
    signed_fn, signed_code = ordinary_function(sources, signed=True)
    raw = raw_fn(word, caller, native)
    signed_base = signed_fn(word, caller, native)
    caller_odd = caller_grid_scale(caller_grid, caller_sha)
    word_sha = digest(canonical(word))
    native_odd = native_grid_scale(native_grid, word_sha)
    signed, surcharge_code = signed_surcharges(sources, caller, signed_base, caller_odd)
    return {"status": "ACCOUNTING_SUBSTITUTION_ONLY" if matched else "ACCOUNTING_SUBSTITUTION_INVOICE_MISMATCH",
            "candidate_canonical_sha256": word_sha, "native_inventory_counts_only": native,
            "invoice_match": matched, "reconstructed_paid": reconstructed_paid, "reconstructed_targets": reconstructed_targets,
            "empty_root_target_count": empty, "caller_stages": caller["stages"],
            "raw_ordinary_at_caller_stages": raw, "signed_source_unit_ordinary": signed,
            "calculation_blocks": {"raw": raw_code, "signed": signed_code, "surcharges": surcharge_code},
            "finite_counts": finite_counts(word, caller, invoice, native_odd, caller_odd, binding, word_sha, caller_sha),
            "source_author_reference": {"source_pr": 7641, "reported_ordinary": 878834276,
                                        "applies_to": "Original source #7641 only, not this arbitrary input candidate.",
                                        "unitemized_512000_definition": "UNRESOLVED; not labeled an error or added to this bill."},
            "scope": "Parameterized source-formula accounting/counts only. No endpoint/CLEAR row replay, caller identity, new grid proof, constant32/precision/context, compiler/outer, physical or provider admission. Inherited conditions remain."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("word", "invoice", "caller", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--caller-grid-receipt", type=Path)
    parser.add_argument("--native-grid-receipt", type=Path)
    parser.add_argument("--binding-receipt", type=Path)
    args = parser.parse_args()
    need(not args.output.exists(), "refuse accounting output overwrite")
    sources, pins = load_sources(args.source_dir)
    word, word_bytes = read_json(args.word)
    invoice, invoice_bytes = read_json(args.invoice)
    caller, caller_bytes = read_json(args.caller)
    receipts, receipt_pins = {}, {}
    for key in ("caller_grid_receipt", "native_grid_receipt", "binding_receipt"):
        path = getattr(args, key)
        if path is not None:
            receipts[key], payload = read_json(path)
            receipt_pins[key] = digest(payload)
    result = audit(word, invoice, caller, sources, digest(caller_bytes), receipts.get("caller_grid_receipt"),
                   receipts.get("native_grid_receipt"), receipts.get("binding_receipt"))
    result.update(source_identification=pins, word_file_sha256=digest(word_bytes), invoice_file_sha256=digest(invoice_bytes),
                  caller_file_sha256=digest(caller_bytes), receipt_file_sha256=receipt_pins)
    with args.output.open("x", encoding="utf-8") as output:
        json.dump(result, output, indent=2)
        output.write("\n")
    signed = result["signed_source_unit_ordinary"]
    print(json.dumps({"status": result["status"], "invoice_match": result["invoice_match"],
                      "raw_ordinary": result["raw_ordinary_at_caller_stages"]["conservative_total"],
                      "signed_ordinary": signed.get("conservative_total"), "finite_context": "PENDING"}, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
        print(json.dumps({"status": "ACCOUNTING_INPUT_INVALID", "error": str(error)}), file=sys.stderr)
        raise SystemExit(2) from error

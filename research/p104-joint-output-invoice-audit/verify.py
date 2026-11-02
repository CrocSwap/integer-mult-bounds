"""Independently count frozen P104 frame-rank and scalar-work invoices.

Native maps and phases, physical erasure, the Laurent caller endpoint and the
outer multiplication theorem are not inferred from these formal invoices.
No author constructor, replay, invoice assembler or interval engine is loaded.
"""
from collections import Counter
from fractions import Fraction
from hashlib import sha1, sha256
from pathlib import Path
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent
PUBLIC, OWNED, PORTS = 770, 29, 104
PINS = {
    "INPUT-WORD.json.gz": ("1415a62059ed62d0b4657db91f7ec01b23c117f5f2744746d93c880bd777be92", "f21f7ac451c3f2e1ae8d5ca1dcad839a0b0d844f"),
    "OUTPUT-WORD.json.gz": ("0c83c1f1dee8c9442558719510a61b89f38c2dbfc8fb565ba035660d2a68d928", "03ea7690285d4cda72815f962d5710ab96e08490"),
    "CONTROLLER.json": ("6fd67eaabe659956d6694471d3fd7d2824c0a4a79cf3b8f22922f7189b11b91f", "1f2e375b24aba5fb25580dfea7fab7a2049f3eb8"),
    "AUTHOR-RESULT.json": ("4c9b2d2b4f0df1ed852250b6815fce62a174ce297fed04801298183afd55c7b7", "f5fc1f595607837531d0aee8c6835f55a2e2ab98"),
    "tariff-source.py": ("7201df8e32f5c99f7403150e8664042322037906088bc754c67293a241368597", "b7be846b10c4c54a4e1558d7b563bc8c3a170223"),
    "controller-source.py": ("8067ade84815b54d539cbaef9885db9fa4d7a23fdde2e683451d317038a8477c", "3b4bf82eba05d57ef4bb1fd934e8ca65780425c1"),
    "NOTICE": ("6c5f4a452f7d65ef8ca0980992dce279938b0a1139f6c067f91de78bf8ecb7bd", "e6cae17f778e8e31b7c294ff2890c545978931c0"),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, lower, upper, label):
    require(type(value) is int and lower <= value < upper, label)
    return value


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def read_sources():
    data = {}
    for name, (expected_sha, expected_blob) in PINS.items():
        raw = (HERE / "sources" / name).read_bytes()
        require(sha256(raw).hexdigest() == expected_sha, "Exact source SHA256: " + name)
        require(sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
                == expected_blob, "Exact source Git blob: " + name)
        if name.endswith(".json.gz"):
            data[name] = json.loads(gzip.decompress(raw))
        elif name.endswith(".json"):
            data[name] = json.loads(raw)
    return data


def profile(counter):
    return {str(rank): count for rank, count in sorted(counter.items()) if count}


def decode_profile(value):
    require(type(value) is dict, "A tariff profile is an object")
    out = Counter()
    for rank, count in value.items():
        require(type(rank) is str and str(int(rank)) == rank, "Canonical rank string")
        integer(count, 1, 10**9, "Positive profile multiplicity")
        integer(int(rank), 1, 1000, "Positive tariff rank")
        out[int(rank)] = count
    return out


def difference(actual, expected):
    return {rank: actual.get(rank, 0) - expected.get(rank, 0)
            for rank in sorted(actual.keys() | expected.keys())
            if actual.get(rank, 0) != expected.get(rank, 0)}


def equal_profile(actual, expected, label):
    delta = difference(actual, expected)
    require(not delta, label + ": differing rank coefficients " + canonical(profile(delta)))


def mass(counter):
    return sum(rank * count for rank, count in counter.items())


def frame_space(vectors):
    require(type(vectors) is list, "A native frame is a list")
    space = {0}
    for vector in vectors:
        integer(vector, 1, 512, "GF(2)^9 frame vector")
        require(vector not in space, "Independent frame basis")
        space |= {x ^ vector for x in tuple(space)}
    return frozenset(space)


def scalar_coefficient(value):
    require(type(value) is str, "Rational scalar string")
    result = Fraction(value)
    require(str(result) == value and result != 0, "Canonical nonzero rational scalar")
    denominator = result.denominator
    require(denominator & (denominator - 1) == 0, "Dyadic scalar coefficient")
    require(abs(result) + 1 < 2**16, "Fixed scalar growth bound")
    return result


def local_invoice(word):
    require(type(word) is dict and type(word["public"]) is int
            and word["public"] == PUBLIC and type(word["owned_fields"]) is int
            and word["owned_fields"] == OWNED, "Exact public and owned inventories")
    require(type(word["frames"]) is list, "Frame inventory")
    spaces = [frame_space(vectors) for vectors in word["frames"]]
    dimensions = [len(vectors) for vectors in word["frames"]]
    for boundary in ("initial", "final"):
        require(type(word[boundary]) is list and len(word[boundary]) == PUBLIC, "Public boundary length")
        for frame in word[boundary]:
            integer(frame, 0, len(spaces), "Public boundary frame")
    require(type(word["live"]) is list and len(word["live"]) == PORTS,
            "104 main pairs")
    for role in word["live"]:
        integer(role, 0, PUBLIC - 112, "Main pair role")
    main = set(word["live"]) | {r + 112 for r in word["live"]}
    require(len(main) == 2 * PORTS, "Distinct main pair roles")
    require(type(word["ports"]) is list and len(word["ports"]) == PORTS,
            "104 central ports")
    for port in word["ports"]:
        integer(port, 1, 512, "Central port")
    current = list(word["initial"]) + [None] * OWNED
    active, peak, lifetimes = set(), 0, 0
    paid, public_paid, owned_paid, operations = Counter(), Counter(), Counter(), Counter()
    charges, ordinary = [], 0
    require(type(word["program"]) is list, "Literal local program")
    for index, event in enumerate(word["program"]):
        require(type(event) is list and event, "Literal event")
        op = event[0]
        require(op in ("MOVE", "INIT", "CLEAR", "ADD", "COPY", "SCALE"), "Known local opcode")
        require(len(event) == {"MOVE": 5, "INIT": 3, "CLEAR": 3,
                               "ADD": 5, "COPY": 5, "SCALE": 4}[op], "Local event arity")
        r = integer(event[1], 0, PUBLIC + OWNED, "Local role")
        operations[op] += 1
        if op == "MOVE":
            a = integer(event[2], 0, len(spaces), "MOVE source frame")
            b = integer(event[3], 0, len(spaces), "MOVE target frame")
            require(type(event[4]) is bool and event[4] == (r in active),
                    "Literal ownership flag")
            require(current[r] == a, "Chronological MOVE source")
            require(spaces[b] < spaces[a] if event[4] else spaces[a] < spaces[b],
                    "Strict nested descent for owned data or ascent for public data")
            rank = abs(dimensions[b] - dimensions[a])
            require(rank > 0, "Positive paid transport rank")
            paid[rank] += 1
            (owned_paid if event[4] else public_paid)[rank] += 1
            charges.append({"index": index, "role": r, "from": a, "to": b,
                            "owned": event[4], "rank": rank})
            current[r] = b
        elif op in ("INIT", "CLEAR"):
            f = integer(event[2], 0, len(spaces), "Lifetime frame")
            require(r >= PUBLIC, "Only owned labels have lifetime events")
            if op == "INIT":
                require(r not in active and current[r] is None, "INIT inactive owned label")
                active.add(r)
                current[r] = f
                lifetimes += 1
                peak = max(peak, len(active))
            else:
                require(r in active and current[r] == f, "CLEAR active owned label and frame")
                active.remove(r)
                current[r] = None
            ordinary += 2
        else:
            f = integer(event[-1], 0, len(spaces), "Scalar frame")
            require(current[r] == f, "Scalar destination frame and lifetime")
            coefficient = scalar_coefficient(event[-2])
            numerator, denominator = abs(coefficient.numerator), coefficient.denominator
            if op == "SCALE":
                require(numerator & (numerator - 1) == 0, "Dyadic unit SCALE")
                ordinary += 2 * (abs(numerator.bit_length() - denominator.bit_length())
                                  + int(coefficient < 0))
            else:
                s = integer(event[2], 0, PUBLIC + OWNED, "Scalar source role")
                require(s != r and current[s] == f, "Common scalar chart and active lifetime")
                if op == "COPY":
                    require(r in active, "COPY has an owned destination")
                ordinary += 2 * (3 + numerator.bit_length() - 1 + bin(numerator).count("1")
                                  + denominator.bit_length() - 1)
    require(not active and current[:PUBLIC] == word["final"]
            and all(frame is None for frame in current[PUBLIC:]), "All public and owned exits")
    helpers = Counter()
    boundaries = {}
    for r in range(PUBLIC):
        a, b = word["initial"][r], word["final"][r]
        increment = dimensions[b] - dimensions[a]
        require(spaces[a] < spaces[b], "Positive nested public boundary increment")
        if r not in main:
            require(increment > 0, "Positive helper target rank")
            helpers[increment] += 1
            boundaries[r] = increment
    require(sum(helpers.values()) == PUBLIC - 2 * PORTS == 562,
            "Every non-main public role supplies one target; no owned target")
    main_increments = {dimensions[word["final"][r]] - dimensions[word["initial"][r]] for r in main}
    require(main_increments == {8}, "Every main stage has declared rank increment eight")
    return {"paid": profile(paid), "helpers": profile(helpers), "public_inputs": PUBLIC,
            "owned_fields": OWNED, "owned_lifetimes": lifetimes, "peak_owned_fields": peak,
            "real_scalar_allowance": ordinary, "events": len(word["program"]),
            "opcodes": dict(sorted(operations.items())), "paid_calls": sum(paid.values()),
            "paid_rank_mass": mass(paid), "productive_rank_mass": mass(helpers),
            "public_paid": profile(public_paid), "owned_paid": profile(owned_paid),
            "helper_fields": sum(helpers.values()), "main_rank_increment": 8}, charges, boundaries


def caller_invoice(caller, local):
    require(type(caller) is dict and caller["schema"] == "binary-query-tree/1", "Frozen caller schema")
    require(type(caller["roles"]) is int and caller["roles"] == 34
            and type(caller["stages"]) is int and caller["stages"] == 19, "Caller inventory")
    require(type(caller["events"]) is list, "Caller literal events")
    local_paid, local_helpers = decode_profile(local["paid"]), decode_profile(local["helpers"])
    paid, targets, fixed_paid = Counter(), Counter(), Counter()
    counts, seen = Counter(), []
    idle_groups, query_indices = [], []
    for index, event in enumerate(caller["events"]):
        require(type(event) is list and event, "Caller event")
        op = event[0]
        require(op in ("ADD", "SCALE", "SWAP", "LOCAL", "QUERY", "Q_POWER", "IDLE"), "Known caller event")
        require(len(event) == {"ADD": 4, "SCALE": 3, "SWAP": 3, "LOCAL": 4,
                               "QUERY": 4, "Q_POWER": 3, "IDLE": 4}[op], "Caller arity")
        counts[op] += 1
        if op == "LOCAL":
            stage = integer(event[1], 1, 20, "Local stage")
            for role in event[2:]:
                integer(role, 0, 34, "Local caller role")
            require(event[2] != event[3], "Distinct local caller roles")
            seen.append(stage)
            paid.update(local_paid)
            targets.update(local_helpers)
        elif op == "QUERY":
            for role in event[1:3]:
                integer(role, 0, 34, "Thin query caller role")
            require(event[1] != event[2] and type(event[3]) is int and event[3] in (-1, 1),
                    "Thin query orientation")
            paid[1] += PORTS
            fixed_paid[1] += PORTS
            query_indices.append(index)
        elif op == "IDLE":
            for role in event[1:3]:
                integer(role, 0, 34, "Paired idle caller role")
            require(event[1] != event[2] and type(event[3]) is list and event[3], "Paired idle stage list")
            for stage in event[3]:
                integer(stage, 1, 20, "Idle stage")
            require(len(set(event[3])) == len(event[3]), "No repeated idle stage")
            rank = local["main_rank_increment"] * len(event[3])
            paid[rank] += 2 * PORTS
            fixed_paid[rank] += 2 * PORTS
            idle_groups.append({"index": index, "rank": rank, "jobs": 2 * PORTS})
        else:
            integer(event[1], 0, 34, "Ordinary caller role")
            if op in ("SWAP", "ADD"):
                integer(event[2], 0, 34, "Ordinary caller second role")
                require(event[1] != event[2], "Distinct ordinary caller roles")
            if op in ("ADD", "SCALE", "Q_POWER"):
                require(type(event[-1]) is int and event[-1] != 0, "Ordinary integer caller coefficient")
                if op == "Q_POWER":
                    require(event[-1] in (-2, 2), "Ordinary central translation")
    require(sorted(seen) == list(range(1, 20)), "Exactly one complete bill for each of nineteen stages")
    require(counts["LOCAL"] == 19 and counts["QUERY"] == 16 and counts["IDLE"] == 16,
            "Complete caller call census")
    require(type(caller["diagonal"]) is list and len(caller["diagonal"]) == 34,
            "34 declared main output targets")
    main = Counter()
    for term in caller["diagonal"]:
        require(type(term) is list and len(term) == 21 and type(term[0]) is int
                and abs(term[0]) == 1, "Declared central target exponent")
        for bit in term[1:]:
            require(type(bit) is int and bit in (0, 1), "Declared stage incidence")
        require(term[1] == 0, "No fictitious stage zero")
        rank = abs(term[0]) + local["main_rank_increment"] * sum(term[1:])
        main[rank] += PORTS
    targets.update(main)
    # A separate fixed-tree formula, not a call to the author assembler.
    formula_paid = Counter({rank: 19 * count for rank, count in local_paid.items()})
    formula_targets = Counter({rank: 19 * count for rank, count in local_helpers.items()})
    formula_paid[1] += 16 * PORTS
    formula_targets[153] += 2 * PORTS
    for size, count in ((2, 9), (3, 1), (4, 4), (7, 1), (8, 1)):
        formula_paid[8 * size] += 2 * PORTS * count
        formula_targets[1 + 8 * size] += 2 * PORTS * count
    equal_profile(paid, formula_paid, "Literal caller and independent paid formula")
    equal_profile(targets, formula_targets, "Declared caller targets and independent formula")
    return {"paid": profile(paid), "targets": profile(targets),
            "paid_calls": sum(paid.values()), "productive_fields": sum(targets.values()),
            "paid_rank_mass": mass(paid), "productive_rank_mass": mass(targets),
            "rank_mass_surplus": mass(targets) - mass(paid)}, {
                "events": len(caller["events"]), "opcode_counts": dict(sorted(counts.items())),
                "local_stages": sorted(seen), "fixed_paid": profile(fixed_paid),
                "declared_main_targets": profile(main), "thin_query_indices": query_indices,
                "paired_idle_groups": idle_groups,
            }


def author_checks(author, old, new, complete):
    for label, local in (("source_local", old), ("local", new)):
        supplied = author[label]
        for field in ("paid", "helpers"):
            equal_profile(decode_profile(local[field]), decode_profile(supplied[field]),
                          "Independently derived versus author " + label + "/" + field)
        for field in ("public_inputs", "owned_fields", "owned_lifetimes", "peak_owned_fields",
                      "real_scalar_allowance", "paid_rank_mass"):
            require(type(supplied[field]) is int and local[field] == supplied[field],
                    "Independently derived versus author " + label + "/" + field)
    supplied = author["complete_cost"]
    for field in ("paid", "targets"):
        equal_profile(decode_profile(complete[field]), decode_profile(supplied[field]),
                      "Independent complete " + field + " versus author")
    for field in ("paid_calls", "productive_fields", "rank_mass_surplus"):
        require(type(supplied[field]) is int and complete[field] == supplied[field],
                "Independent complete " + field + " versus author")


def control_profile(label, expected, corrupted, detail):
    delta = difference(corrupted, expected)
    require(delta, "Control must change a concrete rank coefficient: " + label)
    rank = min(delta)
    try:
        equal_profile(corrupted, expected, label)
    except ValueError:
        return {"control": label, "rejected": True, "rank": rank,
                "expected": expected.get(rank, 0), "corrupted": corrupted.get(rank, 0),
                "detail": detail}
    raise ValueError("Control accepted: " + label)


def controls(new, complete, charges, caller_details):
    paid, targets = decode_profile(complete["paid"]), decode_profile(complete["targets"])
    out = []
    owned = next(charge for charge in charges if charge["owned"])
    wrong = Counter(paid)
    wrong[owned["rank"]] -= 19
    out.append(control_profile("unpaid_owned_transport_in_all_nineteen_calls", paid, wrong, owned))
    wrong = Counter(paid)
    wrong.subtract(decode_profile(new["paid"]))
    out.append(control_profile("one_complete_local_bill_missing", paid, wrong, {"omitted_stage": 1}))
    wrong = Counter(targets)
    wrong[8] -= 19
    wrong[9] += 19
    out.append(control_profile("one_9_to_8_target_debit_missing_in_nineteen_calls", targets, wrong,
                               {"helper_role": 393, "copies": 19}))
    wrong = Counter(targets)
    wrong[1] += 19
    out.append(control_profile("invented_owned_productive_credit", targets, wrong,
                               {"owned_role": PUBLIC, "copies": 19}))
    wrong = Counter(paid)
    wrong[1] -= PORTS
    out.append(control_profile("one_thin_query_unpaid", paid, wrong,
                               {"caller_index": caller_details["thin_query_indices"][0], "jobs": PORTS}))
    idle = caller_details["paired_idle_groups"][0]
    wrong = Counter(paid)
    wrong[idle["rank"]] -= PORTS
    out.append(control_profile("one_paired_idle_member_unpaid", paid, wrong,
                               {"caller_index": idle["index"], "jobs": PORTS, "rank": idle["rank"]}))
    return out


def run():
    data = read_sources()
    source, output = data["INPUT-WORD.json.gz"], data["OUTPUT-WORD.json.gz"]
    old, _, old_boundaries = local_invoice(source)
    new, charges, new_boundaries = local_invoice(output)
    require(source["initial"] == output["initial"] and source["live"] == output["live"]
            and source["ports"] == output["ports"], "Unchanged source input and main interfaces")
    changed = [{"role": r, "source_rank": old_boundaries[r], "output_rank": new_boundaries[r], "copies": 19}
               for r in sorted(old_boundaries) if old_boundaries[r] != new_boundaries[r]]
    require(changed == [{"role": r, "source_rank": 9, "output_rank": 5 if r == 703 else 8, "copies": 19}
                        for r in (226, 297, 361, 393, 451, 484, 485, 703, 707)],
            "Exactly nine productive boundary contractions at all nineteen copies")
    local_paid_delta = difference(decode_profile(new["paid"]), decode_profile(old["paid"]))
    local_target_delta = difference(decode_profile(new["helpers"]), decode_profile(old["helpers"]))
    equal_profile(local_paid_delta, {1: 14, 2: -4, 3: -3, 4: 4, 5: -5}, "Exact literal local paid delta")
    equal_profile(local_target_delta, {5: 1, 8: 8, 9: -9}, "All nine local productive target debits")
    old_complete, caller_details = caller_invoice(data["CONTROLLER.json"], old)
    new_complete, second_details = caller_invoice(data["CONTROLLER.json"], new)
    require(canonical(caller_details) == canonical(second_details), "Unchanged complete fixed caller")
    full_paid_delta = difference(decode_profile(new_complete["paid"]), decode_profile(old_complete["paid"]))
    full_target_delta = difference(decode_profile(new_complete["targets"]), decode_profile(old_complete["targets"]))
    equal_profile(full_paid_delta, {r: 19 * n for r, n in local_paid_delta.items()}, "All nineteen paid changes")
    equal_profile(full_target_delta, {r: 19 * n for r, n in local_target_delta.items()}, "All nineteen target debits")
    author_checks(data["AUTHOR-RESULT.json"], old, new, new_complete)
    return {"schema_version": 1, "status": "PASS",
            "scope": "finite formal frame-rank invoices and contained local scalar-work tally",
            "source_local": old, "output_local": new, "caller": caller_details,
            "source_complete": old_complete, "output_complete": new_complete,
            "changed_helper_targets": changed,
            "local_paid_delta": profile(local_paid_delta), "local_target_delta": profile(local_target_delta),
            "complete_paid_delta": profile(full_paid_delta), "complete_target_delta": profile(full_target_delta),
            "author_receipt_profiles_agree": True,
            "counterfactual_invoice_controls": controls(new, new_complete, charges, caller_details),
            "limits": ["Native maps, absolute phases and their all-column realization are not checked.",
                       "COPY zero destinations and physical owned erasure are separate obligations.",
                       "Main target billing is conditional on the frozen caller diagonal and rank-eight stage interface.",
                       "The Laurent caller endpoint and physical contacts are not proved by this invoice.",
                       "Local scalar-work tally does not establish native routing or complete ordinary-work funding.",
                       "No new kappa, uniform compiler, rounded multiplier or outer admission is claimed."]}


if __name__ == "__main__":
    require(sys.argv[1:] in ([], ["--emit"]), "Usage: verify.py [--emit]")
    result = run()
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    else:
        retained = json.loads((HERE / "RESULT.json").read_bytes())
        require(canonical(result) == canonical(retained), "Exact typed retained RESULT.json receipt")
        print("PASS independently derived finite invoices and retained receipt")
